#!/usr/bin/env python3
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable, Mapping
from urllib.parse import urlparse


Runner = Callable[..., Any]
Which = Callable[[str], str | None]

OWNER_RE = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})$")
REPO_RE = re.compile(r"^[A-Za-z0-9._-]+$")
BRANCH_RE = re.compile(r"^[A-Za-z0-9._/-]+$")
REMOTE_RE = re.compile(r"^[A-Za-z0-9._-]+$")


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


def _has_github_auth(env: Mapping[str, str] | None = None) -> bool:
    source = dict(os.environ)
    if env is not None:
        source.update(dict(env))
    return bool(source.get("GH_TOKEN") or source.get("GITHUB_TOKEN"))


def _run_command(command: list[str], *, cwd: Path, runner: Runner | None = None) -> Any:
    executor = runner or subprocess.run
    return executor(command, cwd=str(cwd), capture_output=True, text=True, check=False)


def _require_gh(workspace: Path, *, which: Which | None = None, env: Mapping[str, str] | None = None) -> dict[str, Any] | None:
    locator = which or shutil.which
    if not locator("gh"):
        return _blocked(
            workspace,
            "github-repository-prepare.json",
            "missing_gh_cli",
            "GitHub CLI is required for repository preparation.",
        )
    if not _has_github_auth(env):
        return _blocked(
            workspace,
            "github-repository-prepare.json",
            "missing_github_auth",
            "GitHub credentials are required for repository preparation.",
        )
    return None


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
    blocked = _require_gh(workspace, which=which, env=env)
    if blocked:
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
            if int(getattr(create_result, "returncode", 1)) != 0:
                return _blocked(
                    workspace,
                    "github-repository-prepare.json",
                    "github_repository_failed",
                    "GitHub repository creation failed.",
                    command="gh repo create",
                    stderr_summary=_safe_summary(getattr(create_result, "stderr", "")),
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

    def run_git(*parts: str) -> Any:
        return _run_command(list(parts), cwd=workspace, runner=runner)

    try:
        inside = run_git("git", "rev-parse", "--is-inside-work-tree")
        if int(getattr(inside, "returncode", 1)) != 0:
            return _blocked(
                workspace,
                "github-sync.json",
                "github_sync_failed",
                "Workspace is not a git repository.",
                stderr_summary=_safe_summary(getattr(inside, "stderr", "")),
            )

        existing_remote = run_git("git", "remote", "get-url", remote)
        if int(getattr(existing_remote, "returncode", 1)) != 0:
            add_remote = run_git("git", "remote", "add", remote, repo_url)
            if int(getattr(add_remote, "returncode", 1)) != 0:
                return _blocked(
                    workspace,
                    "github-sync.json",
                    "github_sync_failed",
                    "Failed to add git remote.",
                    stderr_summary=_safe_summary(getattr(add_remote, "stderr", "")),
                )
        elif str(getattr(existing_remote, "stdout", "")).strip() != repo_url:
            set_remote = run_git("git", "remote", "set-url", remote, repo_url)
            if int(getattr(set_remote, "returncode", 1)) != 0:
                return _blocked(
                    workspace,
                    "github-sync.json",
                    "github_sync_failed",
                    "Failed to update git remote URL.",
                    stderr_summary=_safe_summary(getattr(set_remote, "stderr", "")),
                )

        fetch_result = run_git("git", "fetch", remote, branch)
        checkout_result = run_git("git", "checkout", "-B", branch)
        if int(getattr(checkout_result, "returncode", 1)) != 0:
            return _blocked(
                workspace,
                "github-sync.json",
                "github_sync_failed",
                "Failed to checkout canonical branch.",
                stderr_summary=_safe_summary(getattr(checkout_result, "stderr", "")),
                fetch_stderr_summary=_safe_summary(getattr(fetch_result, "stderr", "")),
            )

        add_result = run_git("git", "add", "-A")
        if int(getattr(add_result, "returncode", 1)) != 0:
            return _blocked(
                workspace,
                "github-sync.json",
                "github_sync_failed",
                "Failed to stage workspace snapshot.",
                stderr_summary=_safe_summary(getattr(add_result, "stderr", "")),
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
                stderr_summary=_safe_summary(getattr(status_result, "stderr", "")),
            )

        if str(getattr(status_result, "stdout", "")).strip() or not has_existing_commit:
            commit_result = run_git("git", "commit", "-m", "Bootstrap approved project delivery snapshot")
            if int(getattr(commit_result, "returncode", 1)) != 0:
                return _blocked(
                    workspace,
                    "github-sync.json",
                    "github_sync_failed",
                    "Failed to create bootstrap commit.",
                    stderr_summary=_safe_summary(getattr(commit_result, "stderr", "")),
                )

        push_result = run_git("git", "push", "-u", remote, branch)
        if int(getattr(push_result, "returncode", 1)) != 0:
            return _blocked(
                workspace,
                "github-sync.json",
                "github_sync_failed",
                "Failed to push workspace snapshot to GitHub.",
                stderr_summary=_safe_summary(getattr(push_result, "stderr", "")),
            )

        head_result = run_git("git", "rev-parse", "--short", "HEAD")
        if int(getattr(head_result, "returncode", 1)) != 0:
            return _blocked(
                workspace,
                "github-sync.json",
                "github_sync_failed",
                "Failed to resolve synced commit hash.",
                stderr_summary=_safe_summary(getattr(head_result, "stderr", "")),
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
        }
    except GithubDeliveryError:
        raise
