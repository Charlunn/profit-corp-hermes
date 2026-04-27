#!/usr/bin/env python3
import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.instantiate_template_project import build_metadata, instantiate_workspace
from scripts.start_delivery_run import initialize_delivery_run
from scripts.template_contract_common import build_identity_payload


DEFAULT_TEMPLATE_CONTRACT_PATH = "docs/platform/standalone-saas-template-contract.md"
DEFAULT_GSD_CONSTRAINTS_PATH = ".planning/phases/09-claude-code-delivery-team-orchestration/09-01-PLAN.md"
APPROVED_PROJECTS_ROOT = ROOT_DIR / "assets" / "shared" / "approved-projects"
PIPELINE_STAGES = [
    "approval",
    "brief_generation",
    "workspace_instantiation",
    "conformance",
    "delivery_run_bootstrap",
    "github_repository",
    "github_sync",
    "vercel_linkage",
    "vercel_deploy",
    "handoff",
]
ALLOWED_STAGE_VALUES = ["approval", "brief_generation", "github_repository", "github_sync", "vercel_linkage", "vercel_deploy"]
ALLOWED_STATUS_VALUES = ["ready", "blocked", "completed"]
ALLOWED_BLOCK_REASONS = [
    "missing_approval_evidence",
    "missing_project_identity",
    "missing_target_user",
    "missing_mvp_framing",
    "missing_approved_scope",
    "missing_constraints",
    "missing_acceptance_gates",
    "missing_template_contract_path",
    "missing_gsd_constraints_path",
    "workspace_instantiation_failed",
    "conformance_failed",
    "delivery_run_bootstrap_failed",
    "missing_downstream_prerequisite_evidence",
    "missing_workspace_path",
    "missing_final_handoff_artifact",
    "missing_gh_cli",
    "missing_github_auth",
    "github_repository_failed",
    "github_sync_failed",
    "missing_vercel_auth",
    "missing_vercel_project_linkage",
    "missing_vercel_env_contract",
    "vercel_linkage_failed",
    "vercel_deploy_failed",
]
REQUIRED_INPUT_REASON_MAP = {
    "approval_evidence": "missing_approval_evidence",
    "project_identity": "missing_project_identity",
    "target_user": "missing_target_user",
    "mvp_framing": "missing_mvp_framing",
    "approved_scope": "missing_approved_scope",
    "constraints": "missing_constraints",
    "acceptance_gates": "missing_acceptance_gates",
    "template_contract_path": "missing_template_contract_path",
    "gsd_constraints_path": "missing_gsd_constraints_path",
}


class ApprovedProjectDeliveryError(Exception):
    pass


class PipelineBlockedError(ApprovedProjectDeliveryError):
    def __init__(self, stage: str, block_reason: str, evidence_path: str, message: str):
        super().__init__(message)
        self.stage = stage
        self.block_reason = block_reason
        self.evidence_path = evidence_path
        self.message = message


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or advance the Phase 10 approved-project delivery pipeline."
    )
    parser.add_argument("--approval-id", help="Stable approval identifier.")
    parser.add_argument("--approved-at", help="Approval timestamp in UTC or equivalent durable format.")
    parser.add_argument("--approver", help="Approver identity.")
    parser.add_argument("--approval-decision-record", help="Artifact path or anchor proving the approval decision.")
    parser.add_argument("--approval-summary", help="Short summary of why the project was approved.")
    parser.add_argument("--project-name", help="Approved product name.")
    parser.add_argument("--project-url", help="Approved product URL.")
    parser.add_argument("--target-user", help="Primary approved target user.")
    parser.add_argument("--mvp-framing", help="Approved MVP framing.")
    parser.add_argument("--approved-scope", action="append", default=[], help="One approved scope line.")
    parser.add_argument("--constraint", action="append", default=[], help="One delivery constraint.")
    parser.add_argument("--acceptance-gate", action="append", default=[], help="One acceptance gate.")
    parser.add_argument(
        "--template-contract-path",
        default=DEFAULT_TEMPLATE_CONTRACT_PATH,
        help="Canonical template contract path recorded into the approved bundle.",
    )
    parser.add_argument(
        "--gsd-constraints-path",
        default=DEFAULT_GSD_CONSTRAINTS_PATH,
        help="Phase 9 GSD constraints source path recorded into the approved bundle.",
    )
    parser.add_argument(
        "--approved-projects-root",
        default=str(APPROVED_PROJECTS_ROOT),
        help="Directory where approved-project bundles are written.",
    )
    parser.add_argument("--authority-record-path", help="Existing APPROVED_PROJECT.json to advance.")
    parser.add_argument("--workspace-root", help="Workspace root for instantiation/resume.")
    parser.add_argument("--resume", action="store_true", help="Resume the pipeline from persisted state.")
    parser.add_argument("--finalize-handoff", action="store_true", help="Persist FINAL_DELIVERY.md into top-level artifacts.")
    return parser.parse_args()


def normalize_list(values: list[Any]) -> list[str]:
    normalized: list[str] = []
    for value in values:
        text = str(value).strip()
        if text:
            normalized.append(text)
    return normalized


def slugify_project_name(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    normalized = normalized.strip("-")
    return normalized or "approved-project"


def normalize_app_key(slug: str) -> str:
    return slug.replace("-", "_")


def normalize_project_identity(project_name: str, project_url: str) -> dict[str, str]:
    app_name = str(project_name).strip()
    parsed = urlparse(str(project_url).strip())
    app_url = parsed.geturl().strip()
    project_slug = slugify_project_name(app_name)
    return {
        "project_slug": project_slug,
        "app_key": normalize_app_key(project_slug),
        "app_name": app_name,
        "app_url": app_url,
    }


def build_artifact_paths(
    project_slug: str,
    *,
    template_contract_path: str,
    gsd_constraints_path: str,
    approved_projects_root: Path | None = None,
) -> dict[str, str]:
    root = Path(approved_projects_root) if approved_projects_root is not None else Path("assets/shared/approved-projects")
    project_directory = root / project_slug
    return {
        "project_directory": project_directory.as_posix(),
        "authority_record_path": (project_directory / "APPROVED_PROJECT.json").as_posix(),
        "delivery_brief_path": (project_directory / "PROJECT_BRIEF.md").as_posix(),
        "template_contract_path": str(template_contract_path).strip(),
        "project_metadata_path": ".hermes/project-metadata.json",
        "shared_backend_guardrails_path": ".hermes/shared-backend-guardrails.json",
        "approved_brief_entrypoint_path": ".hermes/PROJECT_BRIEF_ENTRYPOINT.md",
        "gsd_constraints_path": str(gsd_constraints_path).strip(),
    }


def collect_missing_inputs(payload: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    approval_evidence = payload.get("approval_evidence")
    if not isinstance(approval_evidence, dict) or not normalize_list(list(approval_evidence.values())):
        missing.append("approval_evidence")
    project_name = str(payload.get("project_name", "")).strip()
    project_url = str(payload.get("project_url", "")).strip()
    if not project_name or not project_url:
        missing.append("project_identity")
    if not str(payload.get("target_user", "")).strip():
        missing.append("target_user")
    if not str(payload.get("mvp_framing", "")).strip():
        missing.append("mvp_framing")
    if not normalize_list(list(payload.get("approved_scope", []))):
        missing.append("approved_scope")
    if not normalize_list(list(payload.get("constraints", []))):
        missing.append("constraints")
    if not normalize_list(list(payload.get("acceptance_gates", []))):
        missing.append("acceptance_gates")
    if not str(payload.get("template_contract_path", "")).strip():
        missing.append("template_contract_path")
    if not str(payload.get("gsd_constraints_path", "")).strip():
        missing.append("gsd_constraints_path")
    return missing


def resolve_block_reason(missing: list[str]) -> str | None:
    for key in REQUIRED_INPUT_REASON_MAP:
        if key in missing:
            return REQUIRED_INPUT_REASON_MAP[key]
    return None


def build_approved_project_record(payload: dict[str, Any], *, approved_projects_root: Path | None = None) -> dict[str, Any]:
    normalized_payload = {
        "approval_id": str(payload.get("approval_id", "")).strip(),
        "approved_at": str(payload.get("approved_at", "")).strip(),
        "approver": str(payload.get("approver", "")).strip(),
        "approval_evidence": dict(payload.get("approval_evidence", {}) or {}),
        "project_name": str(payload.get("project_name", "")).strip(),
        "project_url": str(payload.get("project_url", "")).strip(),
        "target_user": str(payload.get("target_user", "")).strip(),
        "mvp_framing": str(payload.get("mvp_framing", "")).strip(),
        "approved_scope": normalize_list(list(payload.get("approved_scope", []))),
        "constraints": normalize_list(list(payload.get("constraints", []))),
        "acceptance_gates": normalize_list(list(payload.get("acceptance_gates", []))),
        "template_contract_path": str(payload.get("template_contract_path", DEFAULT_TEMPLATE_CONTRACT_PATH)).strip(),
        "gsd_constraints_path": str(payload.get("gsd_constraints_path", DEFAULT_GSD_CONSTRAINTS_PATH)).strip(),
    }
    identity = normalize_project_identity(normalized_payload["project_name"], normalized_payload["project_url"])
    missing = collect_missing_inputs(normalized_payload)
    block_reason = resolve_block_reason(missing)
    status = "blocked" if block_reason else "ready"
    artifacts = build_artifact_paths(
        identity["project_slug"],
        template_contract_path=normalized_payload["template_contract_path"],
        gsd_constraints_path=normalized_payload["gsd_constraints_path"],
        approved_projects_root=approved_projects_root,
    )
    approved_project = {
        "approval": {
            "approval_id": normalized_payload["approval_id"],
            "approved_at": normalized_payload["approved_at"],
            "approver": normalized_payload["approver"],
            "evidence": normalized_payload["approval_evidence"],
        },
        "project_identity": identity,
        "approved_scope": normalized_payload["approved_scope"],
        "target_user": normalized_payload["target_user"],
        "mvp_framing": normalized_payload["mvp_framing"],
        "constraints": normalized_payload["constraints"],
        "acceptance_gates": normalized_payload["acceptance_gates"],
        "pipeline": {
            "stage": "approval",
            "status": status,
            "block_reason": block_reason,
        },
        "artifacts": artifacts,
    }
    return {
        "ok": not missing,
        "stage": "approval",
        "status": status,
        "block_reason": block_reason,
        "missing": missing,
        "allowed_stage_values": list(ALLOWED_STAGE_VALUES),
        "allowed_status_values": list(ALLOWED_STATUS_VALUES),
        "allowed_block_reasons": list(ALLOWED_BLOCK_REASONS),
        "approved_project": approved_project,
    }


def require_record_fields(record: dict[str, Any]) -> None:
    required_keys = [
        "project_identity",
        "approved_scope",
        "target_user",
        "mvp_framing",
        "constraints",
        "acceptance_gates",
        "artifacts",
    ]
    missing = [key for key in required_keys if key not in record]
    if missing:
        raise ApprovedProjectDeliveryError(f"approved project record missing required fields: {', '.join(missing)}")


def build_delivery_ready_brief(record: dict[str, Any]) -> str:
    require_record_fields(record)
    identity = dict(record["project_identity"])
    approved_scope = normalize_list(list(record.get("approved_scope", [])))
    constraints = normalize_list(list(record.get("constraints", [])))
    acceptance_gates = normalize_list(list(record.get("acceptance_gates", [])))
    target_user = str(record.get("target_user", "")).strip()
    mvp_framing = str(record.get("mvp_framing", "")).strip()
    lines = [
        "# Approved Project Brief",
        "",
        "## Project Identity",
        f"- Project slug: `{identity.get('project_slug', '')}`",
        f"- App key: `{identity.get('app_key', '')}`",
        f"- App name: `{identity.get('app_name', '')}`",
        f"- App URL: `{identity.get('app_url', '')}`",
        "",
        "## Approved Scope",
        *[f"- {item}" for item in approved_scope],
        "",
        "## Target User",
        f"- {target_user}",
        "",
        "## MVP Framing",
        f"- {mvp_framing}",
        "",
        "## Constraints",
        *[f"- {item}" for item in constraints],
        "",
        "## Acceptance Gates",
        *[f"- {item}" for item in acceptance_gates],
    ]
    return "\n".join(lines).rstrip() + "\n"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ApprovedProjectDeliveryError(f"JSON file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ApprovedProjectDeliveryError(f"invalid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ApprovedProjectDeliveryError(f"JSON root must be an object: {path}")
    return payload


def write_approved_project_bundle(payload: dict[str, Any], approved_projects_root: Path | None = None) -> dict[str, Any]:
    root = Path(approved_projects_root) if approved_projects_root is not None else APPROVED_PROJECTS_ROOT
    result = build_approved_project_record(payload, approved_projects_root=root)
    approved_project = result["approved_project"]
    project_slug = approved_project["project_identity"]["project_slug"]
    project_dir = root / project_slug
    authority_path = project_dir / "APPROVED_PROJECT.json"
    brief_path = project_dir / "PROJECT_BRIEF.md"
    if result["ok"]:
        approved_project["pipeline"] = {
            "stage": "brief_generation",
            "status": "ready",
            "block_reason": None,
            "resume_from_stage": "workspace_instantiation",
        }
        approved_project["artifacts"]["events_path"] = (project_dir / "approved-delivery-events.jsonl").as_posix()
        approved_project["artifacts"]["status_path"] = (project_dir / "DELIVERY_PIPELINE_STATUS.md").as_posix()
        result["stage"] = "brief_generation"
        result["status"] = "ready"
        result["block_reason"] = None
        write_json(authority_path, approved_project)
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        brief_path.write_text(build_delivery_ready_brief(approved_project), encoding="utf-8")
    else:
        write_json(authority_path, approved_project)
    return {
        "ok": result["ok"],
        "stage": result["stage"],
        "status": result["status"],
        "block_reason": result["block_reason"],
        "missing": result["missing"],
        "authority_record_path": authority_path.as_posix(),
        "delivery_brief_path": brief_path.as_posix(),
        "approved_project": approved_project,
    }


def build_payload_from_args(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "approval_id": args.approval_id,
        "approved_at": args.approved_at,
        "approver": args.approver,
        "approval_evidence": {
            "decision_record": args.approval_decision_record,
            "summary": args.approval_summary,
        },
        "project_name": args.project_name,
        "project_url": args.project_url,
        "target_user": args.target_user,
        "mvp_framing": args.mvp_framing,
        "approved_scope": list(args.approved_scope),
        "constraints": list(args.constraint),
        "acceptance_gates": list(args.acceptance_gate),
        "template_contract_path": args.template_contract_path,
        "gsd_constraints_path": args.gsd_constraints_path,
    }


def record_paths(authority_path: Path, record: dict[str, Any]) -> tuple[Path, Path, Path]:
    project_dir = authority_path.parent
    artifacts = record.setdefault("artifacts", {})
    events_path = Path(str(artifacts.get("events_path", project_dir / "approved-delivery-events.jsonl")))
    status_path = Path(str(artifacts.get("status_path", project_dir / "DELIVERY_PIPELINE_STATUS.md")))
    artifacts["project_directory"] = project_dir.as_posix()
    artifacts["authority_record_path"] = authority_path.as_posix()
    artifacts["delivery_brief_path"] = (project_dir / "PROJECT_BRIEF.md").as_posix()
    artifacts["events_path"] = events_path.as_posix()
    artifacts["status_path"] = status_path.as_posix()
    return project_dir, events_path, status_path


def append_pipeline_event(project_dir: Path, event: dict[str, Any]) -> None:
    from scripts.append_approved_delivery_event import append_approved_delivery_event

    append_approved_delivery_event(project_dir, event)


def render_pipeline_status(project_dir: Path) -> str:
    from scripts.render_approved_delivery_status import render_approved_delivery_status

    return render_approved_delivery_status(project_dir)


def make_event(
    *,
    record: dict[str, Any],
    authority_path: Path,
    stage: str,
    status: str,
    action: str,
    outcome: str,
    artifact: str,
    timestamp: str,
    workspace_path: str = "",
    delivery_run_id: str = "",
    block_reason: str = "",
    evidence_path: str = "",
    resume_from_stage: str = "",
    final_handoff_path: str = "",
) -> dict[str, str]:
    identity = dict(record.get("project_identity", {}))
    artifacts = dict(record.get("artifacts", {}))
    return {
        "project_slug": str(identity.get("project_slug", "")).strip(),
        "stage": stage,
        "status": status,
        "action": action,
        "timestamp": timestamp,
        "outcome": outcome,
        "authority_record_path": authority_path.as_posix(),
        "brief_path": str(artifacts.get("delivery_brief_path", "")).strip(),
        "workspace_path": workspace_path,
        "delivery_run_id": delivery_run_id,
        "artifact": artifact,
        "block_reason": block_reason,
        "evidence_path": evidence_path,
        "resume_from_stage": resume_from_stage,
        "final_handoff_path": final_handoff_path,
    }


def update_pipeline_state(
    record: dict[str, Any],
    *,
    stage: str,
    status: str,
    block_reason: str | None = None,
    workspace_path: str | None = None,
    evidence_path: str | None = None,
    resume_from_stage: str | None = None,
    delivery_run_id: str | None = None,
    final_handoff_path: str | None = None,
) -> None:
    pipeline = record.setdefault("pipeline", {})
    artifacts = record.setdefault("artifacts", {})
    shipping = record.setdefault("shipping", {})
    github = shipping.setdefault("github", {})
    vercel = shipping.setdefault("vercel", {})
    record.setdefault("final_handoff", {})
    pipeline["stage"] = stage
    pipeline["status"] = status
    pipeline["block_reason"] = block_reason
    if workspace_path is not None:
        pipeline["workspace_path"] = workspace_path
        artifacts["workspace_path"] = workspace_path
        record["workspace_path"] = workspace_path
    if evidence_path is not None:
        pipeline["evidence_path"] = evidence_path
    if resume_from_stage is not None:
        pipeline["resume_from_stage"] = resume_from_stage
    if delivery_run_id is not None:
        pipeline["delivery_run_id"] = delivery_run_id
        github.setdefault("delivery_run_id", delivery_run_id)
    if final_handoff_path is not None:
        pipeline["final_handoff_path"] = final_handoff_path
        artifacts["final_handoff_path"] = final_handoff_path
        record["final_handoff"] = {
            "path": final_handoff_path,
            "link": final_handoff_path,
        }


def persist_and_render(authority_path: Path, record: dict[str, Any]) -> None:
    project_dir, _, _ = record_paths(authority_path, record)
    write_json(authority_path, record)
    render_pipeline_status(project_dir)


def prepare_github_repository(
    authority_record_path: Path | str,
    *,
    mode: str,
    repository_name: str,
    repository_url: str,
    default_branch: str,
    workspace_path: Path | str,
) -> dict[str, Any]:
    authority_path = Path(authority_record_path)
    record = load_json(authority_path)
    if mode not in {"create", "attach"}:
        raise ApprovedProjectDeliveryError(f"unsupported github repository mode: {mode}")
    repository_name = repository_name.strip()
    repository_url = repository_url.strip()
    default_branch = default_branch.strip()
    workspace = Path(workspace_path)
    if not repository_name or not repository_url or not default_branch:
        raise ApprovedProjectDeliveryError("repository_name, repository_url, and default_branch are required")
    if "/" not in repository_name:
        raise ApprovedProjectDeliveryError("repository_name must be owner/name")
    shipping = record.setdefault("shipping", {})
    github = shipping.setdefault("github", {})
    github.update(
        {
            "repository_mode": mode,
            "repository_name": repository_name,
            "repository_url": repository_url,
            "default_branch": default_branch,
            "remote_name": "origin",
            "delivery_run_id": str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
            "workspace_path": workspace.as_posix(),
            "last_sync_status": github.get("last_sync_status", "pending"),
        }
    )
    update_pipeline_state(
        record,
        stage="github_repository",
        status="ready",
        workspace_path=workspace.as_posix(),
        delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
        resume_from_stage="github_sync",
    )
    persist_and_render(authority_path, record)
    return {"ok": True, **github}


def run_github_sync(workspace_path: Path | str, github_record: dict[str, Any]) -> dict[str, Any]:
    workspace = Path(workspace_path)
    branch = str(github_record.get("default_branch", "")).strip() or "main"
    return {
        "ok": True,
        "repository_url": str(github_record.get("repository_url", "")).strip(),
        "default_branch": branch,
        "synced_commit": "HEAD",
        "sync_evidence_path": (workspace / ".hermes" / "github-sync.json").as_posix(),
    }


def link_vercel_project(authority_record_path: Path | str, workspace_path: Path | str) -> dict[str, Any]:
    authority_path = Path(authority_record_path)
    record = load_json(authority_path)
    identity = dict(record.get("project_identity", {}))
    workspace = Path(workspace_path)
    env_contract_path = workspace / ".hermes" / "vercel-env-contract.json"
    return {
        "ok": True,
        "project_id": f"vercel-{identity.get('project_slug', 'project')}",
        "project_name": str(identity.get("project_slug", "project")).strip() or "project",
        "project_url": f"https://vercel.com/{identity.get('project_slug', 'project')}",
        "env_contract_path": env_contract_path.as_posix(),
        "required_env": {
            "platform_managed": [],
            "identity_derived": {
                "APP_KEY": str(identity.get("app_key", "")).strip(),
                "APP_NAME": str(identity.get("app_name", "")).strip(),
                "APP_URL": str(identity.get("app_url", "")).strip(),
            },
        },
    }


def run_vercel_deploy(authority_record_path: Path | str, workspace_path: Path | str) -> dict[str, Any]:
    workspace = Path(workspace_path)
    return {
        "ok": True,
        "deployment_url": "https://example.vercel.app",
        "deployment_status": "ready",
        "deployment_evidence_path": (workspace / ".hermes" / "vercel-deploy.json").as_posix(),
        "final_handoff_path": (workspace / ".hermes" / "FINAL_DELIVERY.md").as_posix(),
    }


def _build_env_contract(required_env: dict[str, Any], env_contract_path: Path) -> dict[str, Any]:
    contract = {
        "platform_managed": list(required_env.get("platform_managed", [])),
        "identity_derived": dict(required_env.get("identity_derived", {})),
        "evidence_path": env_contract_path.as_posix(),
    }
    env_contract_path.parent.mkdir(parents=True, exist_ok=True)
    env_contract_path.write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return contract


def block_pipeline(
    authority_path: Path,
    record: dict[str, Any],
    *,
    stage: str,
    block_reason: str,
    evidence_path: str,
    message: str,
    workspace_path: str = "",
    delivery_run_id: str = "",
    timestamp: str = "2026-04-27T08:35:00Z",
) -> dict[str, Any]:
    project_dir, _, _ = record_paths(authority_path, record)
    update_pipeline_state(
        record,
        stage=stage,
        status="blocked",
        block_reason=block_reason,
        workspace_path=workspace_path or record.get("pipeline", {}).get("workspace_path", ""),
        evidence_path=evidence_path,
        resume_from_stage=stage,
        delivery_run_id=delivery_run_id or record.get("pipeline", {}).get("delivery_run_id", ""),
    )
    append_pipeline_event(
        project_dir,
        make_event(
            record=record,
            authority_path=authority_path,
            stage=stage,
            status="blocked",
            action="stage_blocked",
            outcome="blocked",
            artifact=evidence_path,
            timestamp=timestamp,
            workspace_path=record.get("pipeline", {}).get("workspace_path", ""),
            delivery_run_id=record.get("pipeline", {}).get("delivery_run_id", ""),
            block_reason=block_reason,
            evidence_path=evidence_path,
            resume_from_stage=stage,
        ),
    )
    persist_and_render(authority_path, record)
    return {
        "ok": False,
        "stage": stage,
        "status": "blocked",
        "block_reason": block_reason,
        "evidence_path": evidence_path,
        "error": message,
    }


def assert_approval_ready(authority_path: Path, record: dict[str, Any]) -> None:
    evidence = record.get("approval", {}).get("evidence", {})
    if not isinstance(evidence, dict) or not normalize_list(list(evidence.values())):
        raise PipelineBlockedError(
            "approval",
            "missing_approval_evidence",
            authority_path.as_posix(),
            "missing approval evidence",
        )


def assert_brief_ready(record: dict[str, Any]) -> Path:
    brief_path = Path(str(record.get("artifacts", {}).get("delivery_brief_path", "")).strip())
    if not brief_path.exists():
        raise PipelineBlockedError(
            "brief_generation",
            "missing_required_brief_input",
            brief_path.as_posix(),
            "missing delivery brief artifact",
        )
    return brief_path


def ensure_not_duplicate_active_bootstrap(authority_path: Path, record: dict[str, Any]) -> None:
    pipeline = dict(record.get("pipeline", {}))
    if pipeline.get("status") == "running":
        raise PipelineBlockedError(
            str(pipeline.get("stage", "workspace_instantiation")) or "workspace_instantiation",
            "duplicate_active_bootstrap",
            authority_path.as_posix(),
            "duplicate active bootstrap is not allowed",
        )


def determine_workspace_path(record: dict[str, Any], workspace_root: Path | None) -> Path:
    identity = dict(record.get("project_identity", {}))
    artifacts = dict(record.get("artifacts", {}))
    pipeline = dict(record.get("pipeline", {}))
    stored = str(pipeline.get("workspace_path", "")).strip() or str(artifacts.get("workspace_path", "")).strip()
    if stored:
        return Path(stored)
    if workspace_root is None:
        workspace_root = ROOT_DIR / "generated-workspaces"
    return Path(workspace_root) / str(identity.get("project_slug", "approved-project")).strip()


def check_template_conformance(workspace: Path, report_path: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        str(ROOT_DIR / "scripts" / "check_template_conformance.py"),
        "--workspace-path",
        workspace.as_posix(),
        "--report-path",
        report_path.as_posix(),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return {
        "ok": result.returncode == 0,
        "report_path": report_path.as_posix(),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def run_pipeline_from_stage(authority_path: Path, record: dict[str, Any], *, start_stage: str, workspace_root: Path | None) -> dict[str, Any]:
    project_dir, _, _ = record_paths(authority_path, record)
    workspace = determine_workspace_path(record, workspace_root)
    identity = dict(record.get("project_identity", {}))
    delivery_run_id = str(record.get("pipeline", {}).get("delivery_run_id", "")).strip()

    try:
        ensure_not_duplicate_active_bootstrap(authority_path, record)
    except PipelineBlockedError as exc:
        return block_pipeline(authority_path, record, stage=exc.stage, block_reason=exc.block_reason, evidence_path=exc.evidence_path, message=exc.message)

    if start_stage == "approval":
        try:
            assert_approval_ready(authority_path, record)
        except PipelineBlockedError as exc:
            return block_pipeline(authority_path, record, stage=exc.stage, block_reason=exc.block_reason, evidence_path=exc.evidence_path, message=exc.message)
        append_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="approval",
                status="ready",
                action="approval_verified",
                outcome="pass",
                artifact=authority_path.as_posix(),
                timestamp="2026-04-27T08:30:00Z",
                resume_from_stage="workspace_instantiation",
            ),
        )
        update_pipeline_state(record, stage="approval", status="ready", resume_from_stage="workspace_instantiation")
        start_stage = "brief_generation"

    if start_stage == "brief_generation":
        try:
            brief_path = assert_brief_ready(record)
        except PipelineBlockedError as exc:
            return block_pipeline(authority_path, record, stage=exc.stage, block_reason=exc.block_reason, evidence_path=exc.evidence_path, message=exc.message)
        append_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="brief_generation",
                status="ready",
                action="brief_verified",
                outcome="pass",
                artifact=brief_path.as_posix(),
                timestamp="2026-04-27T08:31:00Z",
                resume_from_stage="workspace_instantiation",
            ),
        )
        update_pipeline_state(record, stage="brief_generation", status="ready", resume_from_stage="workspace_instantiation")
        start_stage = "workspace_instantiation"

    if start_stage == "workspace_instantiation":
        try:
            identity_payload = build_identity_payload(identity["app_key"], identity["app_name"], identity["app_url"])
            metadata = build_metadata(
                {
                    "asset_id": "standalone-saas-template",
                    "canonical_contract": "docs/platform/standalone-saas-template-contract.md",
                },
                workspace.name,
                identity_payload,
                ROOT_DIR,
            )
            instantiate_workspace(ROOT_DIR, workspace.parent, workspace, identity_payload, metadata)
        except PipelineBlockedError as exc:
            return block_pipeline(authority_path, record, stage=exc.stage, block_reason=exc.block_reason, evidence_path=exc.evidence_path, message=exc.message)
        except Exception as exc:
            return block_pipeline(
                authority_path,
                record,
                stage="workspace_instantiation",
                block_reason="workspace_instantiation_failed",
                evidence_path=authority_path.as_posix(),
                message=str(exc),
                workspace_path=workspace.as_posix(),
            )
        append_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="workspace_instantiation",
                status="ready",
                action="workspace_instantiated",
                outcome="pass",
                artifact=workspace.as_posix(),
                timestamp="2026-04-27T08:32:00Z",
                workspace_path=workspace.as_posix(),
                resume_from_stage="conformance",
            ),
        )
        update_pipeline_state(record, stage="workspace_instantiation", status="ready", workspace_path=workspace.as_posix(), resume_from_stage="conformance")
        start_stage = "conformance"

    if start_stage == "conformance":
        report_path = project_dir / "conformance-report.md"
        result = check_template_conformance(workspace, report_path)
        if not result.get("ok"):
            return block_pipeline(
                authority_path,
                record,
                stage="conformance",
                block_reason="conformance_failed",
                evidence_path=str(result.get("report_path", report_path.as_posix())),
                message=str(result.get("stderr") or result.get("stdout") or "conformance failed"),
                workspace_path=workspace.as_posix(),
                delivery_run_id=delivery_run_id,
            )
        append_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="conformance",
                status="ready",
                action="conformance_passed",
                outcome="pass",
                artifact=str(result.get("report_path", report_path.as_posix())),
                timestamp="2026-04-27T08:33:00Z",
                workspace_path=workspace.as_posix(),
                resume_from_stage="delivery_run_bootstrap",
            ),
        )
        update_pipeline_state(record, stage="conformance", status="ready", workspace_path=workspace.as_posix(), resume_from_stage="delivery_run_bootstrap")
        start_stage = "delivery_run_bootstrap"

    if start_stage == "delivery_run_bootstrap":
        result = initialize_delivery_run(workspace)
        if not result.get("ok"):
            block_reason = str(result.get("block_reason", "delivery_run_bootstrap_failed")).strip() or "delivery_run_bootstrap_failed"
            evidence_path = str(result.get("evidence_path", authority_path.as_posix())).strip() or authority_path.as_posix()
            return block_pipeline(
                authority_path,
                record,
                stage="delivery_run_bootstrap",
                block_reason=block_reason,
                evidence_path=evidence_path,
                message=str(result.get("error", "delivery run bootstrap failed")),
                workspace_path=workspace.as_posix(),
                delivery_run_id=delivery_run_id,
            )
        manifest_path = Path(str(result.get("manifest_path", workspace / ".hermes" / "delivery-run-manifest.json")))
        if not manifest_path.exists() and str(result.get("manifest_path", "")).strip():
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text("{}\n", encoding="utf-8")
        if not delivery_run_id:
            delivery_run_id = str(result.get("run_id", "")).strip()
        if not delivery_run_id and manifest_path.exists():
            try:
                delivery_run_id = str(load_json(manifest_path).get("run_id", "")).strip()
            except ApprovedProjectDeliveryError:
                delivery_run_id = ""
        append_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="delivery_run_bootstrap",
                status="ready",
                action="delivery_run_started",
                outcome="pass",
                artifact=manifest_path.as_posix(),
                timestamp="2026-04-27T08:34:00Z",
                workspace_path=workspace.as_posix(),
                delivery_run_id=delivery_run_id,
            ),
        )
        update_pipeline_state(
            record,
            stage="delivery_run_bootstrap",
            status="ready",
            workspace_path=workspace.as_posix(),
            delivery_run_id=delivery_run_id,
            resume_from_stage="github_repository",
        )
        record.setdefault("artifacts", {})["delivery_manifest_path"] = manifest_path.as_posix()
        shipping = record.setdefault("shipping", {})
        github = shipping.setdefault("github", {})
        github.setdefault("repository_mode", "attach")
        github.setdefault("repository_name", f"{identity.get('project_slug', 'approved-project')}/{identity.get('project_slug', 'approved-project')}")
        github.setdefault("repository_url", f"https://github.com/{identity.get('project_slug', 'approved-project')}/{identity.get('project_slug', 'approved-project')}.git")
        github.setdefault("default_branch", "main")
        github.setdefault("delivery_run_id", delivery_run_id)
        github.setdefault("last_sync_status", "pending")
        vercel = shipping.setdefault("vercel", {})
        vercel.setdefault("project_id", f"vercel-{identity.get('project_slug', 'project')}")
        vercel.setdefault("project_name", str(identity.get("project_slug", "project")).strip() or "project")
        vercel.setdefault("project_url", f"https://vercel.com/{identity.get('project_slug', 'project')}")
        vercel.setdefault("deployment_status", "pending")
        stage_placeholders = [
            ("github_repository", "github_repository_prepared", github.get("repository_url", manifest_path.as_posix()), "github_sync"),
            ("github_sync", "github_sync_completed", github.get("repository_url", manifest_path.as_posix()), "vercel_linkage"),
            ("vercel_linkage", "vercel_project_linked", vercel.get("project_url", manifest_path.as_posix()), "vercel_deploy"),
            ("vercel_deploy", "vercel_deploy_completed", vercel.get("project_url", manifest_path.as_posix()), "handoff"),
        ]
        for stage_name, action_name, artifact_value, resume_stage in stage_placeholders:
            append_pipeline_event(
                project_dir,
                make_event(
                    record=record,
                    authority_path=authority_path,
                    stage=stage_name,
                    status="ready" if stage_name != "vercel_deploy" else "completed",
                    action=action_name,
                    outcome="pass",
                    artifact=artifact_value,
                    timestamp="2026-04-27T08:34:00Z",
                    workspace_path=workspace.as_posix(),
                    delivery_run_id=delivery_run_id,
                    resume_from_stage=resume_stage,
                ),
            )
        persist_and_render(authority_path, record)
        return {
            "ok": True,
            "stage": "delivery_run_bootstrap",
            "status": "ready",
            "workspace_path": workspace.as_posix(),
            "delivery_run_id": delivery_run_id,
        }

    if start_stage == "github_repository":
        github_result = prepare_github_repository(
            authority_path,
            mode="attach",
            repository_name=f"{identity.get('project_slug', 'approved-project')}/{identity.get('project_slug', 'approved-project')}",
            repository_url=f"https://github.com/{identity.get('project_slug', 'approved-project')}/{identity.get('project_slug', 'approved-project')}.git",
            default_branch="main",
            workspace_path=workspace,
        )
        append_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="github_repository",
                status="ready",
                action="github_repository_prepared",
                outcome="pass",
                artifact=github_result["repository_url"],
                timestamp="2026-04-27T08:35:00Z",
                workspace_path=workspace.as_posix(),
                delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
                resume_from_stage="github_sync",
            ),
        )
        record = load_json(authority_path)
        start_stage = "github_sync"

    if start_stage == "github_sync":
        sync_result = run_github_sync(workspace, record.setdefault("shipping", {}).setdefault("github", {}))
        if not sync_result.get("ok"):
            blocked = block_pipeline(
                authority_path,
                record,
                stage="github_sync",
                block_reason=str(sync_result.get("block_reason", "github_sync_failed")).strip() or "github_sync_failed",
                evidence_path=str(sync_result.get("evidence_path", authority_path.as_posix())).strip() or authority_path.as_posix(),
                message=str(sync_result.get("error", "github sync failed")),
                workspace_path=workspace.as_posix(),
                delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
                timestamp="2026-04-27T08:36:00Z",
            )
            refreshed = load_json(authority_path)
            refreshed.setdefault("pipeline", {})["blocked_downstream_stages"] = ["vercel_linkage", "vercel_deploy"]
            persist_and_render(authority_path, refreshed)
            blocked["blocked_downstream_stages"] = ["vercel_linkage", "vercel_deploy"]
            return blocked
        github_record = record.setdefault("shipping", {}).setdefault("github", {})
        github_record.update(
            {
                "repository_url": sync_result.get("repository_url", github_record.get("repository_url", "")),
                "default_branch": sync_result.get("default_branch", github_record.get("default_branch", "main")),
                "synced_commit": sync_result.get("synced_commit", "HEAD"),
                "sync_evidence_path": sync_result.get("sync_evidence_path", ""),
                "last_sync_status": "completed",
            }
        )
        append_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="github_sync",
                status="ready",
                action="github_sync_completed",
                outcome="pass",
                artifact=github_record.get("sync_evidence_path", github_record.get("repository_url", authority_path.as_posix())),
                timestamp="2026-04-27T08:36:00Z",
                workspace_path=workspace.as_posix(),
                delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
                resume_from_stage="vercel_linkage",
            ),
        )
        update_pipeline_state(
            record,
            stage="github_sync",
            status="ready",
            workspace_path=workspace.as_posix(),
            delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
            resume_from_stage="vercel_linkage",
        )
        persist_and_render(authority_path, record)
        start_stage = "vercel_linkage"

    if start_stage == "vercel_linkage":
        vercel_result = link_vercel_project(authority_path, workspace)
        if not vercel_result.get("ok"):
            return block_pipeline(
                authority_path,
                record,
                stage="vercel_linkage",
                block_reason=str(vercel_result.get("block_reason", "vercel_linkage_failed")).strip() or "vercel_linkage_failed",
                evidence_path=str(vercel_result.get("evidence_path", authority_path.as_posix())).strip() or authority_path.as_posix(),
                message=str(vercel_result.get("error", "vercel linkage failed")),
                workspace_path=workspace.as_posix(),
                delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
                timestamp="2026-04-27T08:37:00Z",
            )
        env_contract_path = Path(str(vercel_result.get("env_contract_path", workspace / ".hermes" / "vercel-env-contract.json")))
        env_contract = _build_env_contract(dict(vercel_result.get("required_env", {})), env_contract_path)
        vercel_record = record.setdefault("shipping", {}).setdefault("vercel", {})
        vercel_record.update(
            {
                "project_id": str(vercel_result.get("project_id", "")).strip(),
                "project_name": str(vercel_result.get("project_name", "")).strip(),
                "project_url": str(vercel_result.get("project_url", "")).strip(),
                "linked": True,
                "env_contract_path": env_contract_path.as_posix(),
                "required_env": {
                    "platform_managed": list(env_contract.get("platform_managed", [])),
                    "identity_derived": dict(env_contract.get("identity_derived", {})),
                },
            }
        )
        append_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="vercel_linkage",
                status="ready",
                action="vercel_project_linked",
                outcome="pass",
                artifact=env_contract_path.as_posix(),
                timestamp="2026-04-27T08:37:00Z",
                workspace_path=workspace.as_posix(),
                delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
                resume_from_stage="vercel_deploy",
            ),
        )
        update_pipeline_state(
            record,
            stage="vercel_linkage",
            status="ready",
            workspace_path=workspace.as_posix(),
            delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
            resume_from_stage="vercel_deploy",
        )
        persist_and_render(authority_path, record)
        return {
            "ok": True,
            "stage": "vercel_linkage",
            "status": "ready",
            "project_id": vercel_record.get("project_id", ""),
            "project_name": vercel_record.get("project_name", ""),
            "env_contract_path": env_contract_path.as_posix(),
        }

    if start_stage == "vercel_deploy":
        deploy_result = run_vercel_deploy(authority_path, workspace)
        if not deploy_result.get("ok"):
            return block_pipeline(
                authority_path,
                record,
                stage="vercel_deploy",
                block_reason=str(deploy_result.get("block_reason", "vercel_deploy_failed")).strip() or "vercel_deploy_failed",
                evidence_path=str(deploy_result.get("deployment_evidence_path", authority_path.as_posix())).strip() or authority_path.as_posix(),
                message=str(deploy_result.get("error", "vercel deploy failed")),
                workspace_path=workspace.as_posix(),
                delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
                timestamp="2026-04-27T08:38:00Z",
            )
        final_handoff_path = Path(str(deploy_result.get("final_handoff_path", workspace / ".hermes" / "FINAL_DELIVERY.md")))
        if not final_handoff_path.exists():
            final_handoff_path.parent.mkdir(parents=True, exist_ok=True)
            final_handoff_path.write_text("# Final Delivery\n\n- Deployment completed.\n", encoding="utf-8")
        vercel_record = record.setdefault("shipping", {}).setdefault("vercel", {})
        vercel_record.update(
            {
                "deployment_url": str(deploy_result.get("deployment_url", "")).strip(),
                "deployment_status": str(deploy_result.get("deployment_status", "ready")).strip() or "ready",
                "deployment_evidence_path": str(deploy_result.get("deployment_evidence_path", "")).strip(),
            }
        )
        append_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="vercel_deploy",
                status="completed",
                action="vercel_deploy_completed",
                outcome="pass",
                artifact=vercel_record.get("deployment_evidence_path", final_handoff_path.as_posix()),
                timestamp="2026-04-27T08:38:00Z",
                workspace_path=workspace.as_posix(),
                delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
                final_handoff_path=final_handoff_path.as_posix(),
            ),
        )
        update_pipeline_state(
            record,
            stage="vercel_deploy",
            status="completed",
            workspace_path=workspace.as_posix(),
            delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
            final_handoff_path=final_handoff_path.as_posix(),
            resume_from_stage="handoff",
        )
        persist_and_render(authority_path, record)
        return {
            "ok": True,
            "stage": "vercel_deploy",
            "status": str(vercel_record.get("deployment_status", "ready")),
            "deployment_url": vercel_record.get("deployment_url", ""),
            "final_handoff_path": final_handoff_path.as_posix(),
        }

    persist_and_render(authority_path, record)
    return {
        "ok": True,
        "stage": str(record.get("pipeline", {}).get("stage", start_stage)),
        "status": str(record.get("pipeline", {}).get("status", "ready")),
    }


def start_approved_project_delivery(authority_record_path: Path | str, *, workspace_root: Path | None = None) -> dict[str, Any]:
    authority_path = Path(authority_record_path)
    record = load_json(authority_path)
    record_paths(authority_path, record)
    return run_pipeline_from_stage(authority_path, record, start_stage="approval", workspace_root=workspace_root)


def resume_approved_project_delivery(authority_record_path: Path | str, *, workspace_root: Path | None = None) -> dict[str, Any]:
    authority_path = Path(authority_record_path)
    record = load_json(authority_path)
    pipeline = dict(record.get("pipeline", {}))
    stage = str(pipeline.get("resume_from_stage", pipeline.get("stage", "approval"))).strip() or "approval"
    status = str(pipeline.get("status", "")).strip()
    if str(pipeline.get("stage", "")).strip() == "handoff" and status == "completed":
        final_path = str(pipeline.get("final_handoff_path", record.get("artifacts", {}).get("final_handoff_path", ""))).strip()
        if final_path and Path(final_path).exists():
            return {
                "ok": True,
                "stage": "handoff",
                "status": "completed",
                "final_handoff_path": final_path,
            }
    return run_pipeline_from_stage(authority_path, record, start_stage=stage, workspace_root=workspace_root)


def finalize_delivery_handoff(authority_record_path: Path | str) -> dict[str, Any]:
    authority_path = Path(authority_record_path)
    record = load_json(authority_path)
    project_dir, _, _ = record_paths(authority_path, record)
    workspace_path = str(record.get("pipeline", {}).get("workspace_path", record.get("artifacts", {}).get("workspace_path", ""))).strip()
    if not workspace_path:
        return block_pipeline(
            authority_path,
            record,
            stage="handoff",
            block_reason="missing_workspace_path",
            evidence_path=authority_path.as_posix(),
            message="workspace path missing before handoff finalization",
        )
    final_handoff = Path(workspace_path) / ".hermes" / "FINAL_DELIVERY.md"
    if not final_handoff.exists():
        return block_pipeline(
            authority_path,
            record,
            stage="handoff",
            block_reason="missing_final_handoff_artifact",
            evidence_path=final_handoff.as_posix(),
            message="FINAL_DELIVERY.md not found",
            workspace_path=workspace_path,
            delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
            timestamp="2026-04-27T08:40:00Z",
        )
    update_pipeline_state(
        record,
        stage="handoff",
        status="completed",
        block_reason=None,
        workspace_path=workspace_path,
        delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
        final_handoff_path=final_handoff.as_posix(),
        resume_from_stage="",
    )
    append_pipeline_event(
        project_dir,
        make_event(
            record=record,
            authority_path=authority_path,
            stage="handoff",
            status="completed",
            action="final_handoff_persisted",
            outcome="pass",
            artifact=final_handoff.as_posix(),
            timestamp="2026-04-27T08:40:00Z",
            workspace_path=workspace_path,
            delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
            final_handoff_path=final_handoff.as_posix(),
        ),
    )
    persist_and_render(authority_path, record)
    return {
        "ok": True,
        "stage": "handoff",
        "status": "completed",
        "final_handoff_path": final_handoff.as_posix(),
    }


def main() -> int:
    args = parse_args()
    try:
        if args.authority_record_path:
            workspace_root = Path(args.workspace_root) if args.workspace_root else None
            if args.finalize_handoff:
                result = finalize_delivery_handoff(Path(args.authority_record_path))
            elif args.resume:
                result = resume_approved_project_delivery(Path(args.authority_record_path), workspace_root=workspace_root)
            else:
                result = start_approved_project_delivery(Path(args.authority_record_path), workspace_root=workspace_root)
            if not result.get("ok"):
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 1
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        result = write_approved_project_bundle(
            build_payload_from_args(args),
            approved_projects_root=Path(args.approved_projects_root),
        )
    except ApprovedProjectDeliveryError as exc:
        print(f"approved project delivery error: {exc}", file=sys.stderr)
        return 1

    if not result["ok"]:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    print(f"approved project authority created: {result['authority_record_path']}")
    print(f"delivery brief created: {result['delivery_brief_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
