"""Governed credential wrapper helpers for approved project delivery."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from scripts.append_approved_delivery_event import append_approved_delivery_event
from scripts.github_delivery_common import prepare_github_repository, sync_workspace_to_github
from scripts.vercel_delivery_common import apply_env_contract, deploy_to_vercel, link_vercel_project


class ApprovedDeliveryGovernanceError(RuntimeError):
    """Raised when a governed credential action is invalid."""


ALLOWED_CREDENTIAL_ACTIONS = (
    "github_repository_prepare",
    "github_sync",
    "vercel_project_link",
    "vercel_env_apply",
    "vercel_deploy",
)

_GITHUB_ACTIONS = {"github_repository_prepare", "github_sync"}
_VERCEL_ACTIONS = {"vercel_project_link", "vercel_env_apply", "vercel_deploy"}


Helper = Callable[..., dict[str, Any]]


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_record(authority_record_path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(authority_record_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ApprovedDeliveryGovernanceError(f"invalid authority record JSON: {authority_record_path}") from exc
    if not isinstance(payload, dict):
        raise ApprovedDeliveryGovernanceError(f"authority record root must be an object: {authority_record_path}")
    return payload


def _normalize_action(action: str) -> str:
    value = str(action).strip()
    if value not in ALLOWED_CREDENTIAL_ACTIONS:
        raise ApprovedDeliveryGovernanceError(f"unsupported governed credential action: {value}")
    return value


def _project_dir_for(authority_record_path: Path) -> Path:
    return authority_record_path.parent


def _delivery_run_id(record: dict[str, Any]) -> str:
    return str(record.get("pipeline", {}).get("delivery_run_id", "")).strip()


def _workspace_path(record: dict[str, Any]) -> str:
    pipeline = record.get("pipeline", {})
    artifacts = record.get("artifacts", {})
    return str(pipeline.get("workspace_path") or artifacts.get("workspace_path") or "").strip()


def _project_slug(record: dict[str, Any], authority_record_path: Path) -> str:
    identity = record.get("project_identity", {})
    return str(record.get("project_slug") or identity.get("project_slug") or authority_record_path.parent.name).strip()


def _brief_path(record: dict[str, Any], authority_record_path: Path) -> str:
    artifacts = record.get("artifacts", {})
    return str(record.get("brief_path") or artifacts.get("delivery_brief_path") or (authority_record_path.parent / "PROJECT_BRIEF.md").as_posix()).strip()


def _status_and_outcome(result: dict[str, Any]) -> tuple[str, str]:
    if result.get("ok"):
        return "completed", "success"
    reason = str(result.get("block_reason", "")).strip()
    if reason.startswith("missing_") or reason.endswith("_incomplete"):
        return "blocked", "blocked"
    return "failed", "failed"


def _target_for(action: str, record: dict[str, Any], result: dict[str, Any]) -> dict[str, str]:
    shipping = record.get("shipping", {})
    github = shipping.get("github", {}) if isinstance(shipping.get("github", {}), dict) else {}
    vercel = shipping.get("vercel", {}) if isinstance(shipping.get("vercel", {}), dict) else {}

    if action in _GITHUB_ACTIONS:
        repository_name = str(result.get("repository_name") or github.get("repository_name") or "").strip()
        repository_url = str(result.get("repository_url") or github.get("repository_url") or "").strip()
        return {
            "repository_name": repository_name,
            "repository_url": repository_url,
        }

    if action in _VERCEL_ACTIONS:
        project_name = str(result.get("project_name") or vercel.get("project_name") or "").strip()
        project_id = str(result.get("project_id") or vercel.get("project_id") or "").strip()
        project_url = str(result.get("project_url") or vercel.get("project_url") or "").strip()
        return {
            "project_name": project_name,
            "project_id": project_id,
            "project_url": project_url,
        }

    return {}


def _audit_path(project_dir: Path, action: str) -> Path:
    slug = action.replace("_", "-")
    return project_dir / f"credential-audit-{slug}.json"


def _write_json(path: Path, payload: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path.as_posix()


def _build_audit_payload(
    *,
    action: str,
    stage: str,
    result: dict[str, Any],
    record: dict[str, Any],
    authority_record_path: Path,
    timestamp: str,
) -> dict[str, Any]:
    _, outcome = _status_and_outcome(result)
    return {
        "action": action,
        "stage": stage,
        "outcome": outcome,
        "target": _target_for(action, record, result),
        "evidence_path": str(result.get("evidence_path", "")).strip(),
        "delivery_run_id": _delivery_run_id(record),
        "timestamp": timestamp,
        "reason": str(result.get("block_reason", "")).strip(),
        "error": str(result.get("error", "")).strip(),
        "authority_record_path": authority_record_path.as_posix(),
        "project_slug": _project_slug(record, authority_record_path),
    }


def _append_event(
    *,
    project_dir: Path,
    record: dict[str, Any],
    authority_record_path: Path,
    stage: str,
    result: dict[str, Any],
    audit_path: str,
    timestamp: str,
) -> None:
    status, outcome = _status_and_outcome(result)
    event = {
        "project_slug": _project_slug(record, authority_record_path),
        "stage": stage,
        "status": status,
        "action": f"credential_governance.{stage}.{outcome}",
        "timestamp": timestamp,
        "outcome": outcome,
        "authority_record_path": authority_record_path.as_posix(),
        "brief_path": _brief_path(record, authority_record_path),
        "workspace_path": _workspace_path(record),
        "delivery_run_id": _delivery_run_id(record),
        "artifact": audit_path,
        "block_reason": str(result.get("block_reason", "")).strip(),
        "evidence_path": str(result.get("evidence_path", "")).strip(),
        "resume_from_stage": stage if status in {"blocked", "failed"} else "",
        "final_handoff_path": "",
        "shipping": dict(record.get("shipping", {})),
    }
    append_approved_delivery_event(project_dir, event)


def run_governed_action(*, action, authority_record_path, stage, helper: Helper, **kwargs):
    normalized_action = _normalize_action(action)
    authority_path = Path(authority_record_path)
    record = _load_record(authority_path)
    timestamp = _utc_timestamp()
    project_dir = _project_dir_for(authority_path)

    result = dict(helper(action=normalized_action, authority_record_path=authority_path, stage=stage, **kwargs) or {})
    if "ok" not in result:
        raise ApprovedDeliveryGovernanceError(f"governed helper must return an ok field for action: {normalized_action}")

    audit_payload = _build_audit_payload(
        action=normalized_action,
        stage=stage,
        result=result,
        record=record,
        authority_record_path=authority_path,
        timestamp=timestamp,
    )
    audit_path = _write_json(_audit_path(project_dir, normalized_action), audit_payload)
    _append_event(
        project_dir=project_dir,
        record=record,
        authority_record_path=authority_path,
        stage=stage,
        result=result,
        audit_path=audit_path,
        timestamp=timestamp,
    )

    return {
        **result,
        "audit_path": audit_path,
        "timestamp": timestamp,
        "governed_action": normalized_action,
    }


def run_governed_github_repository_action(
    *,
    authority_record_path: Path | str,
    stage: str,
    workspace_path: Path | str,
    repository_mode: str,
    repository_owner: str,
    repository_name: str,
    repository_url: str | None = None,
    remote_name: str = "origin",
    **kwargs: Any,
) -> dict[str, Any]:
    return run_governed_action(
        action="github_repository_prepare",
        authority_record_path=authority_record_path,
        stage=stage,
        helper=lambda **_: prepare_github_repository(
            workspace_path=workspace_path,
            repository_mode=repository_mode,
            repository_owner=repository_owner,
            repository_name=repository_name,
            repository_url=repository_url,
            remote_name=remote_name,
            **kwargs,
        ),
    )


def run_governed_github_sync_action(
    *,
    authority_record_path: Path | str,
    stage: str,
    workspace_path: Path | str,
    repository_url: str,
    default_branch: str,
    remote_name: str = "origin",
    **kwargs: Any,
) -> dict[str, Any]:
    return run_governed_action(
        action="github_sync",
        authority_record_path=authority_record_path,
        stage=stage,
        helper=lambda **_: sync_workspace_to_github(
            workspace_path=workspace_path,
            repository_url=repository_url,
            default_branch=default_branch,
            remote_name=remote_name,
            **kwargs,
        ),
    )


def run_governed_vercel_link_action(
    *,
    authority_record_path: Path | str,
    stage: str,
    workspace_path: Path | str,
    project_name: str,
    team_scope: str,
    project_id: str = "",
    **kwargs: Any,
) -> dict[str, Any]:
    return run_governed_action(
        action="vercel_project_link",
        authority_record_path=authority_record_path,
        stage=stage,
        helper=lambda **_: link_vercel_project(
            workspace_path=workspace_path,
            project_name=project_name,
            team_scope=team_scope,
            project_id=project_id,
            **kwargs,
        ),
    )


def run_governed_vercel_env_action(
    *,
    authority_record_path: Path | str,
    stage: str,
    workspace_path: Path | str,
    project_name: str,
    team_scope: str,
    platform_managed_env: dict[str, str],
    identity_derived_env: dict[str, str],
    **kwargs: Any,
) -> dict[str, Any]:
    return run_governed_action(
        action="vercel_env_apply",
        authority_record_path=authority_record_path,
        stage=stage,
        helper=lambda **_: apply_env_contract(
            workspace_path=workspace_path,
            project_name=project_name,
            team_scope=team_scope,
            platform_managed_env=platform_managed_env,
            identity_derived_env=identity_derived_env,
            **kwargs,
        ),
    )


def run_governed_vercel_deploy_action(
    *,
    authority_record_path: Path | str,
    stage: str,
    workspace_path: Path | str,
    project_name: str,
    team_scope: str,
    github_sync_ok: bool,
    vercel_link_ok: bool,
    env_contract_ok: bool,
    **kwargs: Any,
) -> dict[str, Any]:
    return run_governed_action(
        action="vercel_deploy",
        authority_record_path=authority_record_path,
        stage=stage,
        helper=lambda **_: deploy_to_vercel(
            workspace_path=workspace_path,
            project_name=project_name,
            team_scope=team_scope,
            github_sync_ok=github_sync_ok,
            vercel_link_ok=vercel_link_ok,
            env_contract_ok=env_contract_ok,
            **kwargs,
        ),
    )
