#!/usr/bin/env python3
import json
import os
import re
import shutil
import subprocess
from pathlib import Path
from typing import Any, Callable, Mapping


Runner = Callable[..., Any]
Which = Callable[[str], str | None]

PROJECT_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
TEAM_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,99}$")
ENV_NAME_RE = re.compile(r"^[A-Z][A-Z0-9_]{1,127}$")
URL_RE = re.compile(r"^https://[^\s]+$")

PLATFORM_MANAGED_ENV_NAMES = [
    "NEXT_PUBLIC_SUPABASE_URL",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "NEXT_PUBLIC_PAYPAL_CLIENT_ID",
    "PAYPAL_CLIENT_SECRET",
    "PAYPAL_ENVIRONMENT",
]
IDENTITY_ENV_NAMES = ["APP_KEY", "APP_NAME", "APP_URL", "PAYPAL_BRAND_NAME"]
AUTH_ERROR_PATTERNS = (
    "invalid token",
    "token invalid",
    "not authenticated",
    "unauthorized",
    "forbidden",
    "please login",
    "please log in",
    "login required",
    "authentication required",
    "run vercel login",
    "log in to vercel",
)
SCOPE_ERROR_PATTERNS = (
    "do not have access to the requested scope",
    "scope not found",
    "team not found",
    "project not found",
    "not authorized for this project",
    "no access to project",
    "permission denied for scope",
)


class VercelDeliveryError(Exception):
    pass



def _safe_summary(text: str) -> str:
    cleaned = " ".join(str(text or "").split())
    for key in ("VERCEL_TOKEN",):
        cleaned = cleaned.replace(key, f"{key}=[redacted]")
    return cleaned[:400]



def _ensure_workspace(workspace_path: Path | str) -> Path:
    workspace = Path(workspace_path)
    workspace.mkdir(parents=True, exist_ok=True)
    (workspace / ".hermes").mkdir(parents=True, exist_ok=True)
    return workspace



def _evidence_path(workspace: Path, stem: str) -> Path:
    return workspace / ".hermes" / stem



def _write_json(path: Path, payload: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path.as_posix()



def _blocked(workspace: Path, evidence_name: str, block_reason: str, message: str, **extra: Any) -> dict[str, Any]:
    payload = {
        "ok": False,
        "block_reason": block_reason,
        "message": message,
        **extra,
    }
    evidence_path = _write_json(_evidence_path(workspace, evidence_name), payload)
    return {
        "ok": False,
        "block_reason": block_reason,
        "error": message,
        "evidence_path": evidence_path,
        **extra,
    }



def _classify_vercel_failure(stderr: str, stdout: str = "") -> str | None:
    summary = _safe_summary(f"{stderr}\n{stdout}").lower()
    if any(pattern in summary for pattern in AUTH_ERROR_PATTERNS):
        return "invalid_vercel_auth"
    if any(pattern in summary for pattern in SCOPE_ERROR_PATTERNS):
        return "inaccessible_vercel_scope"
    return None



def _validate_project_name(value: str) -> str:
    text = value.strip()
    if not PROJECT_RE.fullmatch(text):
        raise VercelDeliveryError("invalid Vercel project name")
    return text



def _validate_team_scope(value: str) -> str:
    text = value.strip()
    if not TEAM_RE.fullmatch(text):
        raise VercelDeliveryError("invalid Vercel team scope")
    return text



def _validate_project_id(value: str) -> str:
    text = value.strip()
    if not text:
        return ""
    if not re.fullmatch(r"^[A-Za-z0-9_-]{3,120}$", text):
        raise VercelDeliveryError("invalid Vercel project id")
    return text



def _extract_vercel_deploy_url(stdout: str, stderr: str, project_name: str) -> str:
    candidates = [str(stdout or ""), str(stderr or "")]
    patterns = [
        r'"url"\s*:\s*"(https://[^"\s]+)"',
        r'\b(?:Production|Preview):\s*(https://[^\s]+)',
        r'\b(?:Inspect|Deployment)[:]?\s*(https://[^\s]+)',
        r'\b(https://[^\s]+\.vercel\.app)\b',
    ]
    for text in candidates:
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1).strip()
    return f"https://{project_name}.vercel.app"



def _validate_env_name(value: str) -> str:
    text = value.strip()
    if not ENV_NAME_RE.fullmatch(text):
        raise VercelDeliveryError(f"invalid environment variable name: {value}")
    return text



def _validate_identity_derived(identity_derived_env: Mapping[str, str]) -> dict[str, str]:
    payload = {key: str(identity_derived_env.get(key, "")).strip() for key in IDENTITY_ENV_NAMES}
    missing = [key for key, value in payload.items() if not value]
    if missing:
        raise VercelDeliveryError(f"missing identity-derived values: {', '.join(missing)}")
    if not URL_RE.fullmatch(payload["APP_URL"]):
        raise VercelDeliveryError("APP_URL must be a valid https URL")
    return payload



def _run_command(
    command: list[str],
    *,
    cwd: Path,
    runner: Runner | None = None,
    env: Mapping[str, str] | None = None,
    input_text: str | None = None,
) -> Any:
    executor = runner or subprocess.run
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    kwargs = {"cwd": str(cwd), "capture_output": True, "text": True, "check": False, "env": run_env}
    if input_text is not None:
        kwargs["input"] = input_text
    if runner is None:
        kwargs["encoding"] = "utf-8"
        kwargs["errors"] = "replace"
    return executor(command, **kwargs)



def _upsert_env_value(
    *,
    command_prefix: list[str],
    workspace: Path,
    env_name: str,
    env_value: str,
    team_scope: str,
    runner: Runner | None = None,
    env: Mapping[str, str] | None = None,
) -> tuple[bool, str, str]:
    add_command = [
        *command_prefix,
        "env",
        "add",
        env_name,
        "production",
        "--scope",
        team_scope,
        "--yes",
    ]
    add_result = _run_command(
        add_command,
        cwd=workspace,
        runner=runner,
        env=env,
        input_text=env_value + "\n",
    )
    if int(getattr(add_result, "returncode", 1)) == 0:
        return True, _safe_summary(getattr(add_result, "stdout", "")), _safe_summary(getattr(add_result, "stderr", ""))

    stderr_summary = _safe_summary(getattr(add_result, "stderr", ""))
    stdout_summary = _safe_summary(getattr(add_result, "stdout", ""))
    summary_text = f"{stderr_summary}\n{stdout_summary}".lower()
    if "already exists" not in summary_text:
        return False, stdout_summary, stderr_summary

    remove_command = [
        *command_prefix,
        "env",
        "rm",
        env_name,
        "production",
        "--scope",
        team_scope,
        "--yes",
    ]
    remove_result = _run_command(remove_command, cwd=workspace, runner=runner, env=env)
    if int(getattr(remove_result, "returncode", 1)) != 0:
        return (
            False,
            _safe_summary(getattr(remove_result, "stdout", "")),
            _safe_summary(getattr(remove_result, "stderr", "")),
        )

    retry_result = _run_command(
        add_command,
        cwd=workspace,
        runner=runner,
        env=env,
        input_text=env_value + "\n",
    )
    return (
        int(getattr(retry_result, "returncode", 1)) == 0,
        _safe_summary(getattr(retry_result, "stdout", "")),
        _safe_summary(getattr(retry_result, "stderr", "")),
    )



def _resolve_vercel_command(which: Which | None = None) -> list[str] | None:
    locator = which or shutil.which
    vercel = locator("vercel")
    if vercel:
        return [vercel]
    vercel_cmd = locator("vercel.cmd")
    if vercel_cmd:
        return [vercel_cmd]
    npx = locator("npx")
    if npx:
        return [npx, "vercel@latest"]
    npx_cmd = locator("npx.cmd")
    if npx_cmd:
        return [npx_cmd, "vercel@latest"]
    return None



def _resolve_vercel_auth(
    workspace: Path,
    command_prefix: list[str],
    *,
    env: Mapping[str, str] | None = None,
    runner: Runner | None = None,
    evidence_name: str,
) -> tuple[dict[str, Any] | None, dict[str, Any] | None]:
    source = dict(env or {})
    token = str(source.get("VERCEL_TOKEN", "")).strip()
    if token:
        return {
            "auth_source": "vercel_token",
            "auth_source_details": {
                "token_supplied": True,
            },
        }, None

    probe = _run_command([*command_prefix, "whoami"], cwd=workspace, runner=runner, env=env)
    if int(getattr(probe, "returncode", 1)) == 0:
        username = str(getattr(probe, "stdout", "")).strip().splitlines()
        return {
            "auth_source": "vercel_cli_session",
            "auth_source_details": {
                "username": username[-1].strip() if username else "",
            },
        }, None

    stderr_summary = _safe_summary(getattr(probe, "stderr", ""))
    stdout_summary = _safe_summary(getattr(probe, "stdout", ""))
    failure_reason = _classify_vercel_failure(stderr_summary, stdout_summary) or "invalid_vercel_auth"
    return None, _blocked(
        workspace,
        evidence_name,
        failure_reason,
        "Vercel authentication is required before project linkage or deploy automation can run.",
        stderr_summary=stderr_summary,
        stdout_summary=stdout_summary,
    )



def _require_vercel(
    workspace: Path,
    *,
    env: Mapping[str, str] | None = None,
    runner: Runner | None = None,
    which: Which | None = None,
    evidence_name: str = "vercel-linkage.json",
) -> tuple[list[str] | None, dict[str, Any] | None, dict[str, Any] | None]:
    command = _resolve_vercel_command(which=which)
    if not command:
        return None, None, _blocked(
            workspace,
            evidence_name,
            "missing_vercel_cli",
            "Vercel CLI is required for project linkage and deploy automation.",
        )
    auth_result, blocked = _resolve_vercel_auth(
        workspace,
        command,
        env=env,
        runner=runner,
        evidence_name=evidence_name,
    )
    if blocked:
        return None, None, blocked
    return command, auth_result, None



def build_env_contract(
    *,
    workspace_path: Path | str,
    platform_managed_env: Mapping[str, str],
    identity_derived_env: Mapping[str, str],
) -> dict[str, Any]:
    workspace = _ensure_workspace(workspace_path)
    identity_values = _validate_identity_derived(identity_derived_env)
    platform_names = [_validate_env_name(name) for name in platform_managed_env.keys()]
    missing_platform = [
        name for name in PLATFORM_MANAGED_ENV_NAMES if name in platform_names and not str(platform_managed_env.get(name, "")).strip()
    ]
    if missing_platform:
        raise VercelDeliveryError(f"missing platform-managed env values: {', '.join(missing_platform)}")
    contract = {
        "platform_managed": platform_names,
        "platform_values": {
            name: str(platform_managed_env.get(name, "")).strip()
            for name in platform_names
        },
        "identity_derived": identity_values,
        "evidence_path": (workspace / ".hermes" / "vercel-env-contract.json").as_posix(),
    }
    _write_json(workspace / ".hermes" / "vercel-env-contract.json", contract)
    return contract



def link_vercel_project(
    *,
    workspace_path: Path | str,
    project_name: str,
    team_scope: str,
    project_id: str = "",
    runner: Runner | None = None,
    which: Which | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    workspace = _ensure_workspace(workspace_path)
    command_prefix, auth_result, blocked = _require_vercel(
        workspace,
        env=env,
        runner=runner,
        which=which,
        evidence_name="vercel-linkage.json",
    )
    if blocked:
        return blocked

    validated_project_name = _validate_project_name(project_name)
    validated_team_scope = _validate_team_scope(team_scope)
    validated_project_id = _validate_project_id(project_id)
    if not validated_project_name and not validated_project_id:
        return _blocked(
            workspace,
            "vercel-linkage.json",
            "missing_vercel_project_linkage",
            "A target Vercel project identifier or name is required before linkage.",
        )

    link_command = [
        *command_prefix,
        "link",
        "--yes",
        "--scope",
        validated_team_scope,
        "--project",
        validated_project_name,
    ]
    result = _run_command(link_command, cwd=workspace, runner=runner, env=env)
    if int(getattr(result, "returncode", 1)) != 0:
        stderr_summary = _safe_summary(getattr(result, "stderr", ""))
        stdout_summary = _safe_summary(getattr(result, "stdout", ""))
        return _blocked(
            workspace,
            "vercel-linkage.json",
            _classify_vercel_failure(stderr_summary, stdout_summary) or "vercel_linkage_failed",
            "Vercel project linkage failed.",
            stderr_summary=stderr_summary,
            stdout_summary=stdout_summary,
            project_name=validated_project_name,
            team_scope=validated_team_scope,
        )

    payload = {
        "ok": True,
        "linked": True,
        "project_id": validated_project_id,
        "project_name": validated_project_name,
        "team_scope": validated_team_scope,
        "project_url": f"https://vercel.com/{validated_team_scope}/{validated_project_name}",
        **(auth_result or {}),
    }
    evidence_path = _write_json(_evidence_path(workspace, "vercel-linkage.json"), payload)
    payload["evidence_path"] = evidence_path
    return payload



def apply_env_contract(
    *,
    workspace_path: Path | str,
    project_name: str,
    team_scope: str,
    platform_managed_env: Mapping[str, str],
    identity_derived_env: Mapping[str, str],
    runner: Runner | None = None,
    which: Which | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    workspace = _ensure_workspace(workspace_path)
    command_prefix, auth_result, blocked = _require_vercel(
        workspace,
        env=env,
        runner=runner,
        which=which,
        evidence_name="vercel-env-contract.json",
    )
    if blocked:
        return blocked

    validated_project_name = _validate_project_name(project_name)
    validated_team_scope = _validate_team_scope(team_scope)
    contract = build_env_contract(
        workspace_path=workspace,
        platform_managed_env=platform_managed_env,
        identity_derived_env=identity_derived_env,
    )

    for env_name in contract["platform_managed"]:
        ok, stdout_summary, stderr_summary = _upsert_env_value(
            command_prefix=command_prefix,
            workspace=workspace,
            env_name=env_name,
            env_value=contract["platform_values"][env_name],
            team_scope=validated_team_scope,
            runner=runner,
            env=env,
        )
        if not ok:
            return _blocked(
                workspace,
                "vercel-env-contract.json",
                _classify_vercel_failure(stderr_summary, stdout_summary) or "missing_vercel_env_contract",
                f"Failed to apply Vercel env contract for {env_name}.",
                stderr_summary=stderr_summary,
                stdout_summary=stdout_summary,
                project_name=validated_project_name,
                team_scope=validated_team_scope,
            )

    for env_name in contract["identity_derived"].keys():
        ok, stdout_summary, stderr_summary = _upsert_env_value(
            command_prefix=command_prefix,
            workspace=workspace,
            env_name=env_name,
            env_value=contract["identity_derived"][env_name],
            team_scope=validated_team_scope,
            runner=runner,
            env=env,
        )
        if not ok:
            return _blocked(
                workspace,
                "vercel-env-contract.json",
                _classify_vercel_failure(stderr_summary, stdout_summary) or "missing_vercel_env_contract",
                f"Failed to apply Vercel env contract for {env_name}.",
                stderr_summary=stderr_summary,
                stdout_summary=stdout_summary,
                project_name=validated_project_name,
                team_scope=validated_team_scope,
            )

    payload = {
        "ok": True,
        "project_name": validated_project_name,
        "team_scope": validated_team_scope,
        "env_contract": contract,
        "env_contract_path": contract["evidence_path"],
        "required_env": {
            "platform_managed": contract["platform_managed"],
            "identity_derived": contract["identity_derived"],
        },
        **(auth_result or {}),
    }
    evidence_path = _write_json(_evidence_path(workspace, "vercel-env-apply.json"), payload)
    payload["evidence_path"] = evidence_path
    return payload



def deploy_to_vercel(
    *,
    workspace_path: Path | str,
    project_name: str,
    team_scope: str,
    github_sync_ok: bool,
    vercel_link_ok: bool,
    env_contract_ok: bool,
    runner: Runner | None = None,
    which: Which | None = None,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    workspace = _ensure_workspace(workspace_path)
    command_prefix, auth_result, blocked = _require_vercel(
        workspace,
        env=env,
        runner=runner,
        which=which,
        evidence_name="vercel-deploy.json",
    )
    if blocked:
        return blocked

    validated_project_name = _validate_project_name(project_name)
    validated_team_scope = _validate_team_scope(team_scope)

    if not github_sync_ok:
        return _blocked(
            workspace,
            "vercel-deploy.json",
            "github_sync_incomplete",
            "GitHub sync must complete before Vercel deploy can run.",
        )
    if not vercel_link_ok:
        return _blocked(
            workspace,
            "vercel-deploy.json",
            "missing_vercel_project_linkage",
            "Vercel project linkage must complete before deploy can run.",
        )
    if not env_contract_ok:
        return _blocked(
            workspace,
            "vercel-deploy.json",
            "missing_vercel_env_contract",
            "Vercel env contract must complete before deploy can run.",
        )

    deploy_command = [
        *command_prefix,
        "deploy",
        "--yes",
        "--scope",
        validated_team_scope,
    ]
    result = _run_command(deploy_command, cwd=workspace, runner=runner, env=env)
    if int(getattr(result, "returncode", 1)) != 0:
        stderr_summary = _safe_summary(getattr(result, "stderr", ""))
        stdout_summary = _safe_summary(getattr(result, "stdout", ""))
        return _blocked(
            workspace,
            "vercel-deploy.json",
            _classify_vercel_failure(stderr_summary, stdout_summary) or "vercel_deploy_failed",
            "Vercel deployment failed.",
            stderr_summary=stderr_summary,
            stdout_summary=stdout_summary,
            project_name=validated_project_name,
        )

    stdout = str(getattr(result, "stdout", "")).strip()
    stderr = str(getattr(result, "stderr", "")).strip()
    deploy_url = _extract_vercel_deploy_url(stdout, stderr, validated_project_name)

    payload = {
        "ok": True,
        "project_name": validated_project_name,
        "team_scope": validated_team_scope,
        "deploy_status": "ready",
        "deploy_url": deploy_url,
        "deploy_evidence_path": (workspace / ".hermes" / "vercel-deploy.json").as_posix(),
        "deployment_status": "ready",
        "deployment_url": deploy_url,
        "deployment_evidence_path": (workspace / ".hermes" / "vercel-deploy.json").as_posix(),
        **(auth_result or {}),
    }
    evidence_path = _write_json(_evidence_path(workspace, "vercel-deploy.json"), payload)
    payload["deploy_evidence_path"] = evidence_path
    payload["deployment_evidence_path"] = evidence_path
    return payload
