#!/usr/bin/env python3
import json
import os
import re
import shutil
import subprocess
import tempfile
from os import PathLike
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib.parse import urlparse


Runner = Callable[..., Any]
Which = Callable[[str], str | None]

OWNER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
REPO_RE = re.compile(r"^[A-Za-z0-9._-]+$")
BRANCH_RE = re.compile(r"^[A-Za-z0-9._/-]+$")
REMOTE_RE = re.compile(r"^[A-Za-z0-9._-]+$")
SNAPSHOT_EXCLUDED_DIR_NAMES = {
    ".git",
    ".hermes",
    ".next",
    ".pnpm-store",
    ".turbo",
    ".vercel",
    "coverage",
    "dist",
    "build",
    "node_modules",
    "out",
}


class GithubDeliveryError(Exception):
    pass


def _safe_summary(text: str) -> str:
    cleaned = " ".join(str(text or "").split())
    for key in ("GH_TOKEN", "GITHUB_TOKEN"):
        cleaned = cleaned.replace(key, f"{key}=[redacted]")
    return cleaned[:400]


def _ensure_workspace(workspace_path: Path | str) -> Path:
    workspace = Path(workspace_path)
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / ".hermes").mkdir(parents=True, exist_ok=True)
    return workspace


def _evidence_path(workspace: Path, stem: str) -> Path:
    return workspace / ".hermes" / stem


def _ensure_git_repository(workspace: Path, *, runner: Runner | None = None) -> dict[str, Any] | None:
    git_dir = workspace / ".git"
    if git_dir.exists():
        return None
    init_result = _run_command(["git", "init", "-b", "main"], cwd=workspace, runner=runner)
    if int(getattr(init_result, "returncode", 1)) != 0:
        return _blocked(
            workspace,
            "github-repository-prepare.json",
            "github_repository_failed",
            "Failed to initialize workspace git repository.",
            command="git init",
            stderr_summary=_safe_summary(getattr(init_result, "stderr", "")),
        )
    return None


def _write_evidence(path: Path, payload: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path.as_posix()


def _blocked(workspace: Path, evidence_name: str, block_reason: str, message: str, **extra: Any) -> dict[str, Any]:
    evidence_path = _evidence_path(workspace, evidence_name)
    payload = {
        "ok": False,
        "block_reason": block_reason,
        "message": message,
        **extra,
    }
    written = _write_evidence(evidence_path, payload)
    return {
        "ok": False,
        "block_reason": block_reason,
        "error": message,
        "evidence_path": written,
        **extra,
    }


def _validate_owner(owner: str) -> str:
    value = owner.strip()
    if not OWNER_RE.fullmatch(value):
        raise GithubDeliveryError("invalid GitHub repository owner")
    return value


def _validate_repo(repo: str) -> str:
    value = repo.strip()
    if not REPO_RE.fullmatch(value):
        raise GithubDeliveryError("invalid GitHub repository name")
    return value


def _validate_branch(branch: str) -> str:
    value = branch.strip()
    if not BRANCH_RE.fullmatch(value) or value.startswith("/") or value.endswith("/"):
        raise GithubDeliveryError("invalid GitHub branch name")
    return value


def _validate_remote(remote_name: str) -> str:
    value = remote_name.strip()
    if not REMOTE_RE.fullmatch(value):
        raise GithubDeliveryError("invalid Git remote name")
    return value


def _validate_repository_url(repository_url: str) -> str:
    value = repository_url.strip()
    if not value:
        return value
    parsed = urlparse(value)
    if parsed.scheme != "https" or parsed.netloc != "github.com" or not parsed.path.strip("/"):
        raise GithubDeliveryError("invalid GitHub repository URL")
    return value


def _github_identity(repository_owner: str, repository_name: str) -> str:
    return f"{repository_owner}/{repository_name}"


def _looks_like_existing_repository_conflict(stderr: str, stdout: str = "") -> bool:
    summary = _safe_summary(f"{stderr}\n{stdout}").lower()
    return (
        "name already exists on this account" in summary
        or "repository already exists" in summary
        or "createrepository" in summary and "already exists" in summary
    )


def _resolve_github_auth(
    workspace: Path,
    *,
    runner: Runner | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    source = dict(os.environ)
    if env is not None:
        source.update(dict(env))
    if source.get("GH_TOKEN"):
        return {
            "ok": True,
            "auth_source": "env_token",
            "auth_source_details": {"source": "GH_TOKEN"},
        }
    if source.get("GITHUB_TOKEN"):
        return {
            "ok": True,
            "auth_source": "env_token",
            "auth_source_details": {"source": "GITHUB_TOKEN"},
        }
    try:
        auth_status = _run_command(["gh", "auth", "status"], cwd=workspace, runner=runner)
    except FileNotFoundError:
        return {"ok": False}
    if int(getattr(auth_status, "returncode", 1)) == 0:
        summary = str(getattr(auth_status, "stdout", "")).strip()
        login = ""
        match = re.search(r"Logged in to github\.com as\s+([^\s]+)", summary)
        if match:
            login = match.group(1).strip()
        return {
            "ok": True,
            "auth_source": "gh_cli",
            "auth_source_details": {
                "command": "gh auth status",
                "login": login,
            },
        }
    return {"ok": False}


def _has_github_auth(env: Mapping[str, str] | None = None) -> bool:
    source = dict(os.environ)
    if env is not None:
        source.update(dict(env))
    return bool(source.get("GH_TOKEN") or source.get("GITHUB_TOKEN"))


def _run_command(command: list[str], *, cwd: Path, runner: Runner | None = None, env: Mapping[str, str] | None = None) -> Any:
    executor = runner or subprocess.run
    return executor(command, cwd=str(cwd), capture_output=True, text=True, check=False, env=dict(env) if env is not None else None)


def _normalize_github_transport(repository_url: str, *, scheme: str) -> str:
    value = _validate_repository_url(repository_url)
    parsed = urlparse(value)
    path = parsed.path.strip("/")
    if scheme == "https":
        return f"https://github.com/{path}"
    if scheme == "ssh":
        return f"git@github.com:{path}"
    raise GithubDeliveryError("unsupported GitHub transport scheme")


def _safe_relative_path(path: str | PathLike[str], workspace: Path) -> str | None:
    try:
        candidate = Path(path)
        relative = candidate.relative_to(workspace)
    except (TypeError, ValueError):
        return None
    parts = relative.parts
    if any(part in SNAPSHOT_EXCLUDED_DIR_NAMES for part in parts[:-1]):
        return None
    return relative.as_posix()


def _canonical_snapshot_paths(workspace: Path) -> list[str]:
    included: list[str] = []
    for root, dirnames, filenames in os.walk(workspace, topdown=True):
        dirnames[:] = [name for name in dirnames if name not in SNAPSHOT_EXCLUDED_DIR_NAMES]
        root_path = Path(root)
        for filename in filenames:
            relative = _safe_relative_path(root_path / filename, workspace)
            if relative is None:
                continue
            included.append(relative)
    included.sort()
    return included


def _stage_workspace_snapshot(workspace: Path, run_git: Callable[..., Any], included_paths: list[str] | None = None) -> tuple[dict[str, Any], Any]:
    included_paths = list(included_paths) if included_paths is not None else _canonical_snapshot_paths(workspace)
    excluded_categories = sorted(name for name in SNAPSHOT_EXCLUDED_DIR_NAMES if (workspace / name).exists())
    evidence = {
        "snapshot_mode": "explicit_paths",
        "snapshot_excluded_categories": excluded_categories,
        "snapshot_included_paths": included_paths,
        "snapshot_policy": "exclude_generated_directories",
    }
    if not included_paths:
        return evidence, None
    add_result = run_git("git", "add", "--", *included_paths)
    return evidence, add_result


def _preserve_workspace_snapshot(workspace: Path, included_paths: list[str]) -> tuple[Path, list[str]]:
    backup_root = Path(tempfile.mkdtemp(prefix="github-sync-snapshot-"))
    restored_paths: list[str] = []
    for relative in included_paths:
        source = workspace / relative
        if not source.is_file():
            continue
        destination = backup_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        restored_paths.append(relative)
    return backup_root, restored_paths


def _preserve_workspace_sidecars(workspace: Path) -> tuple[Path, list[str]]:
    backup_root = Path(tempfile.mkdtemp(prefix="github-sync-sidecars-"))
    preserved: list[str] = []
    for name in sorted(SNAPSHOT_EXCLUDED_DIR_NAMES - {".git"}):
        source = workspace / name
        if not source.exists():
            continue
        destination = backup_root / name
        shutil.move(source.as_posix(), destination.as_posix())
        preserved.append(name)
    return backup_root, preserved


def _restore_workspace_sidecars(workspace: Path, backup_root: Path, preserved: list[str]) -> None:
    for name in preserved:
        source = backup_root / name
        if not source.exists():
            continue
        destination = workspace / name
        if destination.exists():
            if destination.is_dir():
                shutil.rmtree(destination)
            else:
                destination.unlink()
        shutil.move(source.as_posix(), destination.as_posix())
    if backup_root.exists():
        shutil.rmtree(backup_root)


def _restore_workspace_snapshot(workspace: Path, backup_root: Path, included_paths: list[str]) -> None:
    for relative in included_paths:
        source = backup_root / relative
        if not source.is_file():
            continue
        destination = workspace / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
    if backup_root.exists():
        shutil.rmtree(backup_root)


def _resolve_checkout_target(run_git: Callable[..., Any], remote: str, branch: str) -> tuple[str | None, Any]:
    remote_ref = f"refs/remotes/{remote}/{branch}"
    remote_head = run_git("git", "rev-parse", "--verify", remote_ref)
    if int(getattr(remote_head, "returncode", 1)) == 0:
        return remote_ref, remote_head
    return None, remote_head


def _commit_workspace_snapshot(workspace: Path, run_git: Callable[..., Any]) -> Any:
    env = dict(os.environ)
    author_name = str(env.get("APPROVED_DELIVERY_GIT_AUTHOR_NAME", env.get("GIT_AUTHOR_NAME", "Charlunn"))).strip() or "Charlunn"
    author_email = str(env.get("APPROVED_DELIVERY_GIT_AUTHOR_EMAIL", env.get("GIT_AUTHOR_EMAIL", "184456842+Charlunn@users.noreply.github.com"))).strip() or "184456842+Charlunn@users.noreply.github.com"
    env["GIT_AUTHOR_NAME"] = author_name
    env["GIT_COMMITTER_NAME"] = str(env.get("GIT_COMMITTER_NAME", author_name)).strip() or author_name
    env["GIT_AUTHOR_EMAIL"] = author_email
    env["GIT_COMMITTER_EMAIL"] = str(env.get("GIT_COMMITTER_EMAIL", author_email)).strip() or author_email
    return run_git(
        "git",
        "commit",
        "-m",
        "Bootstrap approved project delivery snapshot",
        env=env,
    )


def _converge_remote(workspace: Path, run_git: Callable[..., Any], remote: str, repo_url: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    existing_remote = run_git("git", "remote", "get-url", remote)
    current_remote_url = str(getattr(existing_remote, "stdout", "")).strip()
    remote_action = "unchanged"
    if int(getattr(existing_remote, "returncode", 1)) != 0:
        add_remote = run_git("git", "remote", "add", remote, repo_url)
        if int(getattr(add_remote, "returncode", 1)) != 0:
            return (
                _blocked(
                    workspace,
                    "github-sync.json",
                    "github_sync_failed",
                    "Failed to add git remote.",
                    failed_step="remote",
                    attempted_command="git remote add",
                    stderr_summary=_safe_summary(getattr(add_remote, "stderr", "")),
                ),
                {},
            )
        remote_action = "added"
        current_remote_url = repo_url
    elif current_remote_url != repo_url:
        set_remote = run_git("git", "remote", "set-url", remote, repo_url)
        if int(getattr(set_remote, "returncode", 1)) != 0:
            return (
                _blocked(
                    workspace,
                    "github-sync.json",
                    "github_sync_failed",
                    "Failed to update git remote URL.",
                    failed_step="remote",
                    attempted_command="git remote set-url",
                    stderr_summary=_safe_summary(getattr(set_remote, "stderr", "")),
                    current_remote_url=current_remote_url,
                ),
                {},
            )
        remote_action = "updated"
        current_remote_url = repo_url
    return None, {"remote_action": remote_action, "remote_url": current_remote_url}


def _push_with_transport_fallback(workspace: Path, run_git: Callable[..., Any], remote: str, branch: str, repo_url: str) -> tuple[dict[str, Any] | None, dict[str, Any]]:
    attempts: list[dict[str, str]] = []
    https_url = _normalize_github_transport(repo_url, scheme="https")
    ssh_url = _normalize_github_transport(repo_url, scheme="ssh")
    current_remote = run_git("git", "remote", "get-url", remote)
    current_remote_url = str(getattr(current_remote, "stdout", "")).strip() if int(getattr(current_remote, "returncode", 1)) == 0 else repo_url

    for transport, target_url in (("https", https_url), ("ssh", ssh_url)):
        if current_remote_url != target_url:
            set_remote = run_git("git", "remote", "set-url", remote, target_url)
            if int(getattr(set_remote, "returncode", 1)) != 0:
                attempts.append({
                    "transport": transport,
                    "remote_url": target_url,
                    "status": "remote_update_failed",
                    "stderr_summary": _safe_summary(getattr(set_remote, "stderr", "")),
                })
                continue
            current_remote_url = target_url
        push_result = run_git("git", "push", "-u", remote, branch)
        attempts.append({
            "transport": transport,
            "remote_url": target_url,
            "status": "ok" if int(getattr(push_result, "returncode", 1)) == 0 else "failed",
            "stderr_summary": _safe_summary(getattr(push_result, "stderr", "")),
        })
        if int(getattr(push_result, "returncode", 1)) == 0:
            if current_remote_url != repo_url:
                restore_remote = run_git("git", "remote", "set-url", remote, repo_url)
                if int(getattr(restore_remote, "returncode", 1)) == 0:
                    current_remote_url = repo_url
            return None, {
                "push_transport": transport,
                "push_remote_url": target_url,
                "push_attempts": attempts,
                "remote_url": current_remote_url,
            }

    return (
        _blocked(
            workspace,
            "github-sync.json",
            "github_sync_failed",
            "Failed to push workspace snapshot to GitHub.",
            failed_step="push",
            attempted_command="git push",
            push_attempts=attempts,
            stderr_summary=attempts[-1]["stderr_summary"] if attempts else "",
        ),
        {"push_attempts": attempts, "remote_url": current_remote_url},
    )


def _require_gh(
    workspace: Path,
    *,
    which: Which | None = None,
    env: Mapping[str, str] | None = None,
    runner: Runner | None = None,
) -> dict[str, Any] | None:
    locator = which or shutil.which
    if not locator("gh"):
        return _blocked(
            workspace,
            "github-repository-prepare.json",
            "missing_gh_cli",
            "GitHub CLI is required for repository preparation.",
        )
    auth_resolution = _resolve_github_auth(workspace, runner=runner, env=env)
    if not auth_resolution.get("ok"):
        return _blocked(
            workspace,
            "github-repository-prepare.json",
            "missing_github_auth",
            "GitHub credentials are required for repository preparation.",
        )
    return auth_resolution


def _parse_repo_view(stdout: str) -> dict[str, Any]:
    try:
        payload = json.loads(stdout)
    except json.JSONDecodeError as exc:
        raise GithubDeliveryError("failed to parse GitHub repository metadata") from exc
    if not isinstance(payload, dict):
        raise GithubDeliveryError("GitHub repository metadata must be an object")
    return payload


def prepare_github_repository(
    *,
    workspace_path: Path | str,
    repository_mode: str,
    repository_owner: str,
    repository_name: str,
    repository_url: str | None = None,
    remote_name: str = "origin",
    runner: Runner | None = None,
    which: Which | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    workspace = _ensure_workspace(workspace_path)
    blocked = _require_gh(workspace, which=which, env=env, runner=runner)
    if blocked and not blocked.get("ok", False):
        return blocked

    if repository_mode not in {"create", "attach"}:
        raise GithubDeliveryError("repository_mode must be create or attach")

    if repository_mode == "create":
        init_blocked = _ensure_git_repository(workspace, runner=runner)
        if init_blocked:
            return init_blocked

    owner = _validate_owner(repository_owner)
    repo = _validate_repo(repository_name)
    remote = _validate_remote(remote_name)
    identity = _github_identity(owner, repo)
    validated_url = _validate_repository_url(repository_url or "")

    try:
        if repository_mode == "create":
            create_command = [
                "gh",
                "repo",
                "create",
                identity,
                "--source",
                workspace.as_posix(),
                "--remote",
                remote,
                "--private",
            ]
            create_result = _run_command(create_command, cwd=workspace, runner=runner)
            create_stderr = _safe_summary(getattr(create_result, "stderr", ""))
            create_stdout = _safe_summary(getattr(create_result, "stdout", ""))
            reused_existing = False
            if int(getattr(create_result, "returncode", 1)) != 0:
                if _looks_like_existing_repository_conflict(create_stderr, create_stdout):
                    reused_existing = True
                else:
                    return _blocked(
                        workspace,
                        "github-repository-prepare.json",
                        "github_repository_failed",
                        "GitHub repository creation failed.",
                        command="gh repo create",
                        stderr_summary=create_stderr,
                        stdout_summary=create_stdout,
                    )
            view_command = ["gh", "repo", "view", identity, "--json", "nameWithOwner,url,defaultBranchRef"]
            view_result = _run_command(view_command, cwd=workspace, runner=runner)
            if int(getattr(view_result, "returncode", 1)) != 0:
                return _blocked(
                    workspace,
                    "github-repository-prepare.json",
                    "github_repository_failed",
                    "GitHub repository inspection failed after creation.",
                    command="gh repo view",
                    stderr_summary=_safe_summary(getattr(view_result, "stderr", "")),
                )
            repo_payload = _parse_repo_view(getattr(view_result, "stdout", ""))
        else:
            view_command = ["gh", "repo", "view", identity, "--json", "nameWithOwner,url,defaultBranchRef"]
            view_result = _run_command(view_command, cwd=workspace, runner=runner)
            if int(getattr(view_result, "returncode", 1)) != 0:
                return _blocked(
                    workspace,
                    "github-repository-prepare.json",
                    "github_repository_failed",
                    "GitHub repository attach failed.",
                    command="gh repo view",
                    stderr_summary=_safe_summary(getattr(view_result, "stderr", "")),
                )
            repo_payload = _parse_repo_view(getattr(view_result, "stdout", ""))


        canonical_url = validated_url or str(repo_payload.get("url", "")).strip()
        if canonical_url and not canonical_url.endswith(".git"):
            canonical_url = f"{canonical_url}.git"
        canonical_url = _validate_repository_url(canonical_url)
        default_branch = _validate_branch(
            str((repo_payload.get("defaultBranchRef") or {}).get("name", "")).strip() or "main"
        )
        evidence_path = _write_evidence(
            _evidence_path(workspace, "github-repository-prepare.json"),
            {
                "ok": True,
                "repository_mode": repository_mode,
                "repository_owner": owner,
                "repository_name": identity,
                "repository_url": canonical_url,
                "default_branch": default_branch,
                "remote_name": remote,
                "command": "gh repo create" if repository_mode == "create" else "gh repo view",
                "remote_action": "reused_existing" if repository_mode == "create" and reused_existing else "created" if repository_mode == "create" else "attached",
                "auth_source": blocked.get("auth_source", ""),
                "auth_source_details": dict(blocked.get("auth_source_details", {})),
            },
        )
        return {
            "ok": True,
            "block_reason": "",
            "evidence_path": evidence_path,
            "repository_mode": repository_mode,
            "repository_owner": owner,
            "repository_name": identity,
            "repository_url": canonical_url,
            "default_branch": default_branch,
            "remote_name": remote,
            "remote_action": "reused_existing" if repository_mode == "create" and reused_existing else "created" if repository_mode == "create" else "attached",
            "auth_source": blocked.get("auth_source", ""),
            "auth_source_details": dict(blocked.get("auth_source_details", {})),
        }
    except GithubDeliveryError:
        raise


def sync_workspace_to_github(
    *,
    workspace_path: Path | str,
    repository_url: str,
    default_branch: str,
    remote_name: str = "origin",
    runner: Runner | None = None,
) -> dict[str, Any]:
    workspace = _ensure_workspace(workspace_path)
    remote = _validate_remote(remote_name)
    branch = _validate_branch(default_branch)
    repo_url = _validate_repository_url(repository_url)

    def run_git(*parts: str, env: Mapping[str, str] | None = None) -> Any:
        return _run_command(list(parts), cwd=workspace, runner=runner, env=env)

    try:
        inside = run_git("git", "rev-parse", "--is-inside-work-tree")
        if int(getattr(inside, "returncode", 1)) != 0:
            return _blocked(
                workspace,
                "github-sync.json",
                "github_sync_failed",
                "Workspace is not a git repository.",
                failed_step="repository",
                attempted_command="git rev-parse --is-inside-work-tree",
                stderr_summary=_safe_summary(getattr(inside, "stderr", "")),
            )

        remote_blocked, remote_evidence = _converge_remote(workspace, run_git, remote, repo_url)
        if remote_blocked:
            return remote_blocked

        snapshot_paths = _canonical_snapshot_paths(workspace)
        snapshot_backup_root, preserved_paths = _preserve_workspace_snapshot(workspace, snapshot_paths)
        sidecar_backup_root, preserved_sidecars = _preserve_workspace_sidecars(workspace)
        snapshot_evidence = {
            "snapshot_mode": "explicit_paths",
            "snapshot_excluded_categories": sorted(name for name in SNAPSHOT_EXCLUDED_DIR_NAMES if (workspace / name).exists() or name in preserved_sidecars),
            "snapshot_included_paths": snapshot_paths,
            "snapshot_policy": "exclude_generated_directories",
        }
        try:
            fetch_result = run_git("git", "fetch", remote, branch)
            checkout_target, remote_head_result = _resolve_checkout_target(run_git, remote, branch)
            checkout_command = ["git", "checkout", "-B", branch]
            attempted_checkout_command = "git checkout -B"
            if checkout_target:
                checkout_command.append(checkout_target)
                attempted_checkout_command = f"git checkout -B {branch} {checkout_target}"
            checkout_result = run_git(*checkout_command)
            if int(getattr(checkout_result, "returncode", 1)) != 0:
                return _blocked(
                    workspace,
                    "github-sync.json",
                    "github_sync_failed",
                    "Failed to checkout canonical branch.",
                    failed_step="branch",
                    attempted_command=attempted_checkout_command,
                    stderr_summary=_safe_summary(getattr(checkout_result, "stderr", "")),
                    fetch_stderr_summary=_safe_summary(getattr(fetch_result, "stderr", "")),
                    remote_branch_found=checkout_target is not None,
                    remote_branch_lookup_stderr_summary=_safe_summary(getattr(remote_head_result, "stderr", "")),
                    **remote_evidence,
                    **snapshot_evidence,
                )

            _restore_workspace_snapshot(workspace, snapshot_backup_root, preserved_paths)
            _restore_workspace_sidecars(workspace, sidecar_backup_root, preserved_sidecars)

            snapshot_evidence, add_result = _stage_workspace_snapshot(workspace, run_git, snapshot_paths)
            if add_result is not None and int(getattr(add_result, "returncode", 1)) != 0:
                return _blocked(
                    workspace,
                    "github-sync.json",
                    "github_sync_failed",
                    "Failed to stage workspace snapshot.",
                    failed_step="stage",
                    attempted_command="git add -- <paths>",
                    stderr_summary=_safe_summary(getattr(add_result, "stderr", "")),
                    remote_branch_found=checkout_target is not None,
                    **remote_evidence,
                    **snapshot_evidence,
                )

            head_exists_result = run_git("git", "rev-parse", "--verify", "HEAD")
            has_existing_commit = int(getattr(head_exists_result, "returncode", 1)) == 0

            status_result = run_git("git", "status", "--short")
            if int(getattr(status_result, "returncode", 1)) != 0:
                return _blocked(
                    workspace,
                    "github-sync.json",
                    "github_sync_failed",
                    "Failed to inspect git status.",
                    failed_step="status",
                    attempted_command="git status --short",
                    stderr_summary=_safe_summary(getattr(status_result, "stderr", "")),
                    remote_branch_found=checkout_target is not None,
                    **remote_evidence,
                    **snapshot_evidence,
                )

            if str(getattr(status_result, "stdout", "")).strip() or not has_existing_commit:
                commit_result = _commit_workspace_snapshot(workspace, run_git)
                if int(getattr(commit_result, "returncode", 1)) != 0:
                    return _blocked(
                        workspace,
                        "github-sync.json",
                        "github_sync_failed",
                        "Failed to create bootstrap commit.",
                        failed_step="commit",
                        attempted_command="git commit -m",
                        stderr_summary=_safe_summary(getattr(commit_result, "stderr", "")),
                        remote_branch_found=checkout_target is not None,
                        **remote_evidence,
                        **snapshot_evidence,
                    )

            push_blocked, push_evidence = _push_with_transport_fallback(workspace, run_git, remote, branch, repo_url)
            if push_blocked:
                return {
                    **push_blocked,
                    **remote_evidence,
                    **snapshot_evidence,
                    **push_evidence,
                    "remote_branch_found": checkout_target is not None,
                }

            head_result = run_git("git", "rev-parse", "--short", "HEAD")
            if int(getattr(head_result, "returncode", 1)) != 0:
                return _blocked(
                    workspace,
                    "github-sync.json",
                    "github_sync_failed",
                    "Failed to resolve synced commit hash.",
                    failed_step="commit_hash",
                    attempted_command="git rev-parse --short HEAD",
                    stderr_summary=_safe_summary(getattr(head_result, "stderr", "")),
                    remote_branch_found=checkout_target is not None,
                    **remote_evidence,
                    **snapshot_evidence,
                    **push_evidence,
                )
            synced_commit = str(getattr(head_result, "stdout", "")).strip()
            evidence_path = _write_evidence(
                _evidence_path(workspace, "github-sync.json"),
                {
                    "ok": True,
                    "repository_url": repo_url,
                    "default_branch": branch,
                    "remote_name": remote,
                    "synced_commit": synced_commit,
                    "remote_branch_found": checkout_target is not None,
                    **remote_evidence,
                    **snapshot_evidence,
                    **push_evidence,
                },
            )
            return {
                "ok": True,
                "block_reason": "",
                "evidence_path": evidence_path,
                "repository_url": repo_url,
                "default_branch": branch,
                "remote_name": remote,
                "synced_commit": synced_commit,
                "remote_branch_found": checkout_target is not None,
                **remote_evidence,
                **snapshot_evidence,
                **push_evidence,
            }
        finally:
            if snapshot_backup_root.exists():
                shutil.rmtree(snapshot_backup_root)
            if sidecar_backup_root.exists():
                _restore_workspace_sidecars(workspace, sidecar_backup_root, preserved_sidecars)
    except GithubDeliveryError:
        raise
