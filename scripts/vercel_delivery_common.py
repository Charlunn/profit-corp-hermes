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
    "SUPABASE_URL",
    "SUPABASE_ANON_KEY",
    "SUPABASE_SERVICE_ROLE_KEY",
    "PAYPAL_CLIENT_ID",
    "PAYPAL_CLIENT_SECRET",
]
IDENTITY_ENV_NAMES = ["APP_KEY", "APP_NAME", "APP_URL", "PAYPAL_BRAND_NAME"]


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



def _run_command(command: list[str], *, cwd: Path, runner: Runner | None = None, env: Mapping[str, str] | None = None) -> Any:
    executor = runner or subprocess.run
    run_env = os.environ.copy()
    if env:
        run_env.update(env)
    return executor(command, cwd=str(cwd), capture_output=True, text=True, check=False, env=run_env)



def _resolve_vercel_command(which: Which | None = None) -> list[str] | None:
    locator = which or shutil.which
    if locator("vercel"):
        return ["vercel"]
    if locator("npx"):
        return ["npx", "vercel@latest"]
    return None



def _require_vercel(
    workspace: Path,
    *,
    env: Mapping[str, str] | None = None,
    which: Which | None = None,
    evidence_name: str = "vercel-linkage.json",
) -> tuple[list[str] | None, dict[str, Any] | None]:
    command = _resolve_vercel_command(which=which)
    if not command:
        return None, _blocked(
            workspace,
            evidence_name,
            "missing_vercel_cli",
            "Vercel CLI is required for project linkage and deploy automation.",
        )
    source = dict(env or {})
    if not source.get("VERCEL_TOKEN"):
        return None, _blocked(
            workspace,
            evidence_name,
            "missing_vercel_auth",
            "VERCEL_TOKEN is required for non-interactive Vercel automation.",
        )
    return command, None



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
    command_prefix, blocked = _require_vercel(workspace, env=env, which=which, evidence_name="vercel-linkage.json")
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
        return _blocked(
            workspace,
            "vercel-linkage.json",
            "vercel_linkage_failed",
            "Vercel project linkage failed.",
            stderr_summary=_safe_summary(getattr(result, "stderr", "")),
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
    command_prefix, blocked = _require_vercel(workspace, env=env, which=which, evidence_name="vercel-env-contract.json")
    if blocked:
        return blocked

    validated_project_name = _validate_project_name(project_name)
    validated_team_scope = _validate_team_scope(team_scope)
    contract = build_env_contract(
        workspace_path=workspace,
        platform_managed_env=platform_managed_env,
        identity_derived_env=identity_derived_env,
    )

    for env_name in contract["identity_derived"].keys():
        command = [
            *command_prefix,
            "env",
            "add",
            env_name,
            "production",
            "--scope",
            validated_team_scope,
            "--yes",
        ]
        result = _run_command(command, cwd=workspace, runner=runner, env={**dict(env or {}), env_name: contract["identity_derived"][env_name]})
        if int(getattr(result, "returncode", 1)) != 0:
            return _blocked(
                workspace,
                "vercel-env-contract.json",
                "missing_vercel_env_contract",
                f"Failed to apply Vercel env contract for {env_name}.",
                stderr_summary=_safe_summary(getattr(result, "stderr", "")),
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
    command_prefix, blocked = _require_vercel(workspace, env=env, which=which, evidence_name="vercel-deploy.json")
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
        "--prod",
        "--yes",
        "--scope",
        validated_team_scope,
    ]
    result = _run_command(deploy_command, cwd=workspace, runner=runner, env=env)
    if int(getattr(result, "returncode", 1)) != 0:
        return _blocked(
            workspace,
            "vercel-deploy.json",
            "vercel_deploy_failed",
            "Vercel deployment failed.",
            stderr_summary=_safe_summary(getattr(result, "stderr", "")),
            project_name=validated_project_name,
        )

    stdout = str(getattr(result, "stdout", "")).strip()
    deploy_url = stdout.splitlines()[-1].strip() if stdout else f"https://{validated_project_name}.vercel.app"
    if not deploy_url.startswith("https://"):
        deploy_url = f"https://{validated_project_name}.vercel.app"

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
    }
    evidence_path = _write_json(_evidence_path(workspace, "vercel-deploy.json"), payload)
    payload["deploy_evidence_path"] = evidence_path
    payload["deployment_evidence_path"] = evidence_path
    return payload
