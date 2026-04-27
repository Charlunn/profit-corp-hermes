#!/usr/bin/env python3
import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


DEFAULT_TEMPLATE_CONTRACT_PATH = "docs/platform/standalone-saas-template-contract.md"
DEFAULT_GSD_CONSTRAINTS_PATH = ".planning/phases/09-claude-code-delivery-team-orchestration/09-01-PLAN.md"
APPROVED_PROJECTS_ROOT = ROOT_DIR / "assets" / "shared" / "approved-projects"
ALLOWED_STAGE_VALUES = ["approval", "brief_generation"]
ALLOWED_STATUS_VALUES = ["ready", "blocked"]
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


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create the approved-project authority bundle for Phase 10 delivery kickoff."
    )
    parser.add_argument("--approval-id", required=True, help="Stable approval identifier.")
    parser.add_argument("--approved-at", required=True, help="Approval timestamp in UTC or equivalent durable format.")
    parser.add_argument("--approver", required=True, help="Approver identity.")
    parser.add_argument(
        "--approval-decision-record",
        required=True,
        help="Artifact path or anchor proving the approval decision.",
    )
    parser.add_argument(
        "--approval-summary",
        required=True,
        help="Short summary of why the project was approved.",
    )
    parser.add_argument("--project-name", required=True, help="Approved product name.")
    parser.add_argument("--project-url", required=True, help="Approved product URL.")
    parser.add_argument("--target-user", required=True, help="Primary approved target user.")
    parser.add_argument("--mvp-framing", required=True, help="Approved MVP framing.")
    parser.add_argument(
        "--approved-scope",
        action="append",
        default=[],
        help="One approved scope line. Repeat for multiple entries.",
    )
    parser.add_argument(
        "--constraint",
        action="append",
        default=[],
        help="One delivery constraint. Repeat for multiple entries.",
    )
    parser.add_argument(
        "--acceptance-gate",
        action="append",
        default=[],
        help="One acceptance gate. Repeat for multiple entries.",
    )
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


def build_artifact_paths(project_slug: str, *, template_contract_path: str, gsd_constraints_path: str) -> dict[str, str]:
    project_directory = Path("assets/shared/approved-projects") / project_slug
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


def build_approved_project_record(payload: dict[str, Any]) -> dict[str, Any]:
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


def write_approved_project_bundle(payload: dict[str, Any], approved_projects_root: Path | None = None) -> dict[str, Any]:
    result = build_approved_project_record(payload)
    approved_project = result["approved_project"]
    project_slug = approved_project["project_identity"]["project_slug"]
    root = Path(approved_projects_root) if approved_projects_root is not None else APPROVED_PROJECTS_ROOT
    project_dir = root / project_slug
    authority_path = project_dir / "APPROVED_PROJECT.json"
    brief_path = project_dir / "PROJECT_BRIEF.md"

    if result["ok"]:
        approved_project["pipeline"] = {
            "stage": "brief_generation",
            "status": "ready",
            "block_reason": None,
        }
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


def main() -> int:
    args = parse_args()
    try:
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
