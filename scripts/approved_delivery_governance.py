"""Governed credential wrapper helpers for approved project delivery."""

from __future__ import annotations

import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from scripts.append_approved_delivery_event import append_approved_delivery_event
from scripts.check_template_conformance import PROTECTED_PATHS as CONFORMANCE_PROTECTED_PATHS
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
_PROTECTED_EXTRA_PATHS = (
    "src/app/api/paypal/client-token/route.ts",
)
PROTECTED_SURFACE_PATHS = tuple(dict.fromkeys((*CONFORMANCE_PROTECTED_PATHS, *_PROTECTED_EXTRA_PATHS)))
CLASSIFICATION_ALLOWED_VALUES = (
    "product_only",
    "protected_platform",
    "blocked_for_missing_information",
)
WORKSPACE_CHANGES_EVIDENCE_NAME = "workspace-changes.json"


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
    if reason.startswith("missing_") or reason.endswith("_incomplete") or reason.endswith("_pending"):
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
        team_scope = str(result.get("team_scope") or vercel.get("team_scope") or "").strip()
        return {
            "project_name": project_name,
            "project_id": project_id,
            "project_url": project_url,
            "team_scope": team_scope,
        }

    return {}


def _audit_path(project_dir: Path, action: str) -> Path:
    slug = action.replace("_", "-")
    return project_dir / f"credential-audit-{slug}.json"


def _write_json(path: Path, payload: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path.as_posix()


def _read_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ApprovedDeliveryGovernanceError(f"invalid JSON artifact: {path}") from exc
    if not isinstance(payload, dict):
        raise ApprovedDeliveryGovernanceError(f"JSON artifact root must be an object: {path}")
    return payload


def _normalize_workspace_relative_path(raw_path: str, workspace_root: Path) -> tuple[str, str]:
    text = str(raw_path or "").strip().replace("\\", "/")
    if not text:
        return "", "blank touched path entry"
    candidate = Path(text)
    if candidate.is_absolute():
        try:
            text = candidate.resolve().relative_to(workspace_root.resolve()).as_posix()
        except ValueError:
            return "", f"path outside workspace: {candidate.as_posix()}"
    return text.lstrip("./"), ""


def _classification_reason(classification: str, *, protected_matches: list[str], unknown_paths: list[str], touched_paths: list[str]) -> str:
    if classification == "blocked_for_missing_information":
        if not touched_paths:
            return "workspace change inventory missing or empty"
        if unknown_paths:
            return "workspace change inventory contains paths that cannot be normalized safely"
    if classification == "protected_platform":
        return f"protected platform surfaces touched: {', '.join(protected_matches)}"
    return "touched paths remain within the product extension layer"


def classify_workspace_changes(*, workspace_root: Path | str, touched_paths: list[str] | tuple[str, ...] | None) -> dict[str, Any]:
    workspace = Path(workspace_root)
    normalized_touched_paths: list[str] = []
    unknown_paths: list[str] = []
    reasons: list[str] = []

    for raw_path in list(touched_paths or []):
        normalized, reason = _normalize_workspace_relative_path(str(raw_path), workspace)
        if normalized:
            normalized_touched_paths.append(normalized)
        else:
            unknown_paths.append(str(raw_path))
            if reason:
                reasons.append(reason)

    normalized_touched_paths = sorted(dict.fromkeys(normalized_touched_paths))
    protected_matches = sorted(path for path in normalized_touched_paths if path in PROTECTED_SURFACE_PATHS)

    classification = "product_only"
    block_reason = ""
    if not normalized_touched_paths and not unknown_paths:
        classification = "blocked_for_missing_information"
        block_reason = "missing_workspace_change_inventory"
        reasons.append("no touched paths available for deterministic classification")
    elif unknown_paths:
        classification = "blocked_for_missing_information"
        block_reason = "workspace_change_inventory_incomplete"
    elif protected_matches:
        classification = "protected_platform"

    reason = _classification_reason(
        classification,
        protected_matches=protected_matches,
        unknown_paths=unknown_paths,
        touched_paths=normalized_touched_paths,
    )
    if reason and reason not in reasons:
        reasons.insert(0, reason)

    return {
        "classification": classification,
        "protected_matches": protected_matches,
        "unknown_paths": unknown_paths,
        "reasons": reasons,
        "touched_paths": normalized_touched_paths,
        "block_reason": block_reason,
    }


def _workspace_changes_evidence_path(workspace_root: Path) -> Path:
    return workspace_root / ".hermes" / WORKSPACE_CHANGES_EVIDENCE_NAME


def load_workspace_change_inventory(workspace_root: Path | str) -> dict[str, Any] | None:
    path = _workspace_changes_evidence_path(Path(workspace_root))
    if not path.exists():
        return None
    payload = _read_json(path)
    touched_paths = payload.get("touched_paths", [])
    if not isinstance(touched_paths, list):
        raise ApprovedDeliveryGovernanceError("workspace change inventory touched_paths must be a list")
    return payload


def collect_workspace_touched_paths(workspace_root: Path | str) -> dict[str, Any]:
    workspace = Path(workspace_root)
    inventory = load_workspace_change_inventory(workspace)
    if inventory is not None:
        touched_paths = [str(item) for item in inventory.get("touched_paths", [])]
        return {
            "ok": True,
            "source": "workspace_change_inventory",
            "touched_paths": touched_paths,
            "evidence_path": _workspace_changes_evidence_path(workspace).as_posix(),
        }

    git_dir = workspace / ".git"
    if not git_dir.exists():
        return {
            "ok": False,
            "source": "missing_inventory",
            "touched_paths": [],
            "evidence_path": "",
            "block_reason": "missing_workspace_change_inventory",
            "error": "workspace change inventory missing and workspace is not a git repository",
        }

    result = subprocess.run(
        ["git", "-C", workspace.as_posix(), "status", "--porcelain"],
        capture_output=True,
        text=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    if result.returncode != 0:
        return {
            "ok": False,
            "source": "git_status_failed",
            "touched_paths": [],
            "evidence_path": "",
            "block_reason": "workspace_change_inventory_incomplete",
            "error": result.stderr.strip() or result.stdout.strip() or "unable to inspect workspace changes",
        }

    touched_paths: list[str] = []
    for raw_line in result.stdout.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        payload = line[3:] if len(line) > 3 else ""
        if " -> " in payload:
            before, after = payload.split(" -> ", 1)
            touched_paths.extend([before.strip(), after.strip()])
        else:
            touched_paths.append(payload.strip())

    return {
        "ok": True,
        "source": "git_status_porcelain",
        "touched_paths": touched_paths,
        "evidence_path": "",
    }


def write_workspace_classification_report(
    *,
    workspace_root: Path | str,
    stage: str,
    collection: dict[str, Any],
    classification: dict[str, Any],
) -> str:
    workspace = Path(workspace_root)
    path = workspace / ".hermes" / f"protected-surface-classification-{stage.replace('_', '-')}.json"
    payload = {
        "stage": stage,
        "workspace_path": workspace.as_posix(),
        "inventory_source": str(collection.get("source", "")).strip(),
        "inventory_evidence_path": str(collection.get("evidence_path", "")).strip(),
        "classification": classification["classification"],
        "protected_matches": list(classification.get("protected_matches", [])),
        "unknown_paths": list(classification.get("unknown_paths", [])),
        "reasons": list(classification.get("reasons", [])),
        "touched_paths": list(classification.get("touched_paths", [])),
        "block_reason": str(classification.get("block_reason", "")).strip(),
        "protected_surface_paths": list(PROTECTED_SURFACE_PATHS),
        "generated_at": _utc_timestamp(),
    }
    return _write_json(path, payload)


def inspect_workspace_changes(*, workspace_root: Path | str, stage: str) -> dict[str, Any]:
    collection = collect_workspace_touched_paths(workspace_root)
    classification = classify_workspace_changes(
        workspace_root=workspace_root,
        touched_paths=collection.get("touched_paths", []),
    )
    if not collection.get("ok") and not classification.get("block_reason"):
        classification["classification"] = "blocked_for_missing_information"
        classification["block_reason"] = str(collection.get("block_reason", "missing_workspace_change_inventory")).strip() or "missing_workspace_change_inventory"
        if collection.get("error"):
            classification.setdefault("reasons", []).insert(0, str(collection["error"]).strip())
    evidence_path = write_workspace_classification_report(
        workspace_root=workspace_root,
        stage=stage,
        collection=collection,
        classification=classification,
    )
    return {
        **classification,
        "inventory_source": str(collection.get("source", "")).strip(),
        "inventory_evidence_path": str(collection.get("evidence_path", "")).strip(),
        "evidence_path": evidence_path,
    }


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
        "auth_source": str(result.get("auth_source", "")).strip(),
        "auth_source_details": dict(result.get("auth_source_details", {}) or {}),
    }


def _merged_shipping_snapshot(record: dict[str, Any], result: dict[str, Any], stage: str) -> dict[str, Any]:
    shipping = dict(record.get("shipping", {}))
    github = dict(shipping.get("github", {}) if isinstance(shipping.get("github", {}), dict) else {})
    vercel = dict(shipping.get("vercel", {}) if isinstance(shipping.get("vercel", {}), dict) else {})

    if stage == "github_repository":
        if result.get("repository_name"):
            github["repository_name"] = str(result.get("repository_name", "")).strip()
        if result.get("repository_url"):
            github["repository_url"] = str(result.get("repository_url", "")).strip()
    elif stage == "github_sync":
        if result.get("repository_url"):
            github["repository_url"] = str(result.get("repository_url", "")).strip()
        if result.get("default_branch"):
            github["default_branch"] = str(result.get("default_branch", "")).strip()
        if result.get("synced_commit"):
            github["synced_commit"] = str(result.get("synced_commit", "")).strip()
        if result.get("evidence_path"):
            github["sync_evidence_path"] = str(result.get("evidence_path", "")).strip()
    elif stage in {"vercel_linkage", "vercel_deploy"}:
        for key in ("project_name", "project_id", "project_url", "team_scope", "auth_source"):
            if result.get(key):
                vercel[key] = str(result.get(key, "")).strip()
        if result.get("auth_source_details"):
            vercel["auth_source_details"] = dict(result.get("auth_source_details", {}) or {})
        if result.get("env_contract_path"):
            vercel["env_contract_path"] = str(result.get("env_contract_path", "")).strip()
        if result.get("env_contract"):
            vercel["env_contract"] = dict(result.get("env_contract", {}) or {})
        if result.get("deploy_url"):
            vercel["deploy_url"] = str(result.get("deploy_url", "")).strip()
        if result.get("deploy_status"):
            vercel["deploy_status"] = str(result.get("deploy_status", "")).strip()
        if result.get("deploy_evidence_path"):
            vercel["deploy_evidence_path"] = str(result.get("deploy_evidence_path", "")).strip()
        if result.get("deployment_url"):
            vercel["deployment_url"] = str(result.get("deployment_url", "")).strip()
        if result.get("deployment_status"):
            vercel["deployment_status"] = str(result.get("deployment_status", "")).strip()
        if result.get("deployment_evidence_path"):
            vercel["deployment_evidence_path"] = str(result.get("deployment_evidence_path", "")).strip()

    if github:
        shipping["github"] = github
    if vercel:
        shipping["vercel"] = vercel
    return shipping


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
        "shipping": _merged_shipping_snapshot(record, result, stage),
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
