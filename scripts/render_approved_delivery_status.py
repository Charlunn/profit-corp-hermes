#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


APPROVED_RECORD_NAME = "APPROVED_PROJECT.json"
EVENTS_FILE_NAME = "approved-delivery-events.jsonl"
STATUS_FILE_NAME = "DELIVERY_PIPELINE_STATUS.md"


class ApprovedDeliveryStatusError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render DELIVERY_PIPELINE_STATUS.md from the Phase 10 authority event stream.")
    parser.add_argument("--project-dir", required=True, help="Approved-project directory containing the authority bundle.")
    parser.add_argument("--dry-run", action="store_true", help="Print markdown instead of writing the status file.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ApprovedDeliveryStatusError(f"invalid JSON in authority record: {path}") from exc
    if not isinstance(payload, dict):
        raise ApprovedDeliveryStatusError(f"authority record must be an object: {path}")
    return payload


def load_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ApprovedDeliveryStatusError(f"invalid JSONL at line {line_number}: {path}") from exc
        if not isinstance(payload, dict):
            raise ApprovedDeliveryStatusError(f"approved delivery event at line {line_number} must be an object")
        events.append(payload)
    return events


def first_nonempty(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def get_nested(payload: dict[str, Any], *keys: str) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def normalize_flag(value: Any) -> str:
    if isinstance(value, bool):
        return "yes" if value else "no"
    text = str(value).strip()
    return text or "not available"


def summarize_action_required(latest: dict[str, Any], record: dict[str, Any], github: dict[str, Any], vercel: dict[str, Any], protected_change: dict[str, Any], justification: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    latest_status = str(latest.get("status", "")).strip().lower()
    latest_outcome = str(latest.get("outcome", "")).strip().lower()
    block_reason = first_nonempty(latest.get("block_reason"), get_nested(record, "pipeline", "block_reason"))
    evidence_path = first_nonempty(latest.get("evidence_path"), get_nested(record, "pipeline", "evidence_path"))
    if latest_status == "blocked" or latest_outcome in {"blocked", "failed"}:
        lines.append(f"- Investigate latest blocked/failed stage before retrying: `{block_reason or 'reason not available'}`")
    if evidence_path:
        lines.append(f"- Review evidence first: `{evidence_path}`")
    if str(github.get("last_sync_status", "")).strip().lower() in {"blocked", "failed"}:
        lines.append("- Resolve GitHub sync failure before any Vercel retry.")
    if str(vercel.get("deploy_status", vercel.get("deployment_status", "")).strip()).lower() in {"blocked", "failed"}:
        lines.append("- Resolve Vercel deployment failure and rerun only the governed deploy stage.")
    if str(protected_change.get("status", "")).strip().lower() in {"blocked", "pending", "rejected"}:
        lines.append("- Protected platform changes need justification/governance resolution before shipping can continue.")
    if str(justification.get("status", "")).strip().lower() in {"pending", "rejected", "blocked"}:
        lines.append("- Inspect platform justification artifact and governance decision before resume.")
    if not lines:
        lines.append("- No immediate operator action required; governed delivery surface is coherent.")
    return lines


def build_status_markdown(events: list[dict[str, Any]], record: dict[str, Any], project_dir: Path) -> str:
    latest = events[-1] if events else {}
    artifacts = record.get("artifacts", {}) if isinstance(record.get("artifacts"), dict) else {}
    pipeline = record.get("pipeline", {}) if isinstance(record.get("pipeline"), dict) else {}
    identity = record.get("project_identity", {}) if isinstance(record.get("project_identity"), dict) else {}
    approval = record.get("approval", {}) if isinstance(record.get("approval"), dict) else {}
    shipping = latest.get("shipping", {}) if isinstance(latest.get("shipping"), dict) else {}
    if not shipping and isinstance(record.get("shipping"), dict):
        shipping = record.get("shipping", {})
    github = shipping.get("github", {}) if isinstance(shipping.get("github"), dict) else {}
    vercel = shipping.get("vercel", {}) if isinstance(shipping.get("vercel"), dict) else {}
    latest_blocked = record.get("latest_blocked_prerequisite", {}) if isinstance(record.get("latest_blocked_prerequisite"), dict) else {}
    protected_change = record.get("protected_change", {}) if isinstance(record.get("protected_change"), dict) else {}
    justification = record.get("platform_justification", {}) if isinstance(record.get("platform_justification"), dict) else {}
    final_handoff = record.get("final_handoff", {}) if isinstance(record.get("final_handoff"), dict) else {}

    workspace_path = first_nonempty(latest.get("workspace_path"), get_nested(pipeline, "workspace_path"), artifacts.get("workspace_path"), record.get("workspace_path"))
    final_handoff_path = first_nonempty(latest.get("final_handoff_path"), get_nested(pipeline, "final_handoff_path"), final_handoff.get("path"), final_handoff.get("link"))
    final_review_path = first_nonempty(artifacts.get("final_review_path"), (project_dir / "FINAL_OPERATOR_REVIEW.md").as_posix())
    blocked_reason = first_nonempty(latest.get("block_reason"), latest_blocked.get("reason"), pipeline.get("block_reason"))
    blocked_evidence = first_nonempty(latest.get("evidence_path"), latest_blocked.get("path"), pipeline.get("evidence_path"))

    history_lines = []
    for event in events:
        history_lines.append(
            "- "
            f"stage=`{event.get('stage', 'not available')}` "
            f"status=`{event.get('status', 'not available')}` "
            f"outcome=`{event.get('outcome', 'not available')}` "
            f"block_reason=`{event.get('block_reason', 'not available')}` "
            f"artifact=`{event.get('artifact', 'not available')}` "
            f"evidence=`{event.get('evidence_path', 'not available')}` "
            f"handoff=`{event.get('final_handoff_path', 'not available')}`"
        )

    action_required_lines = summarize_action_required(latest, record, github, vercel, protected_change, justification)

    return "\n".join(
        [
            "# Delivery Pipeline Status",
            f"- **Authority Source**: `{EVENTS_FILE_NAME}`",
            f"- **Authority Record**: `{(project_dir / APPROVED_RECORD_NAME).as_posix()}`",
            f"- **Final Operator Review**: `{final_review_path}`",
            f"- **Project Slug**: `{first_nonempty(latest.get('project_slug'), identity.get('project_slug')) or 'not available'}`",
            f"- **Current Stage**: `{first_nonempty(latest.get('stage'), pipeline.get('stage')) or 'not available'}`",
            f"- **Pipeline Status**: `{first_nonempty(latest.get('status'), pipeline.get('status')) or 'not available'}`",
            f"- **Latest Outcome**: `{first_nonempty(latest.get('outcome')) or 'not available'}`",
            f"- **Delivery Brief**: `{first_nonempty(latest.get('brief_path'), artifacts.get('delivery_brief_path')) or 'not available'}`",
            f"- **Workspace Path**: `{workspace_path or 'not available'}`",
            f"- **Delivery Run ID**: `{first_nonempty(latest.get('delivery_run_id'), pipeline.get('delivery_run_id')) or 'not available'}`",
            "",
            "## Final Operator Review",
            "This authority-layer review is the single operator-facing artifact for governed delivery inspection and resume.",
            "",
            "## Action Required",
            *action_required_lines,
            "",
            "## Approval Summary",
            f"- Approval ID: `{approval.get('approval_id', 'not available')}`",
            f"- Approved At: `{approval.get('approved_at', 'not available')}`",
            f"- Approver: `{approval.get('approver', 'not available')}`",
            f"- Approval Evidence: `{get_nested(approval, 'evidence', 'decision_record') or 'not available'}`",
            f"- Approval Summary: `{get_nested(approval, 'evidence', 'summary') or 'not available'}`",
            "",
            "## Blocked Prerequisites",
            f"- Block Reason: `{blocked_reason or 'not available'}`",
            f"- Blocked Prerequisite Evidence: `{blocked_evidence or 'not available'}`",
            f"- Resume From Stage: `{first_nonempty(latest.get('resume_from_stage'), pipeline.get('resume_from_stage')) or 'not available'}`",
            f"- Blocked State Visible: `{normalize_flag(bool(blocked_reason or blocked_evidence))}`",
            "",
            "## Credentialed Delivery Actions",
            f"- GitHub Repository Mode: `{github.get('repository_mode', 'not available')}`",
            f"- GitHub Repository Owner: `{github.get('repository_owner', 'not available')}`",
            f"- GitHub Repository Name: `{github.get('repository_name', 'not available')}`",
            f"- GitHub Repository URL: `{github.get('repository_url', 'not available')}`",
            f"- GitHub Default Branch: `{github.get('default_branch', 'not available')}`",
            f"- GitHub Synced Commit: `{github.get('synced_commit', 'not available')}`",
            f"- GitHub Sync Evidence Path: `{github.get('sync_evidence_path', 'not available')}`",
            f"- GitHub Sync Audit Path: `{first_nonempty(github.get('sync_audit_path'), github.get('prepare_audit_path')) or 'not available'}`",
            f"- GitHub Sync Status: `{github.get('last_sync_status', 'not available')}`",
            f"- Vercel Team Scope: `{vercel.get('team_scope', 'not available')}`",
            f"- Vercel Project ID: `{vercel.get('project_id', 'not available')}`",
            f"- Vercel Project Name: `{vercel.get('project_name', 'not available')}`",
            f"- Vercel Project URL: `{vercel.get('project_url', 'not available')}`",
            f"- Vercel Link Status: `{normalize_flag(vercel.get('linked', 'not available'))}`",
            f"- Vercel Env Contract Path: `{first_nonempty(vercel.get('env_contract_path'), get_nested(vercel, 'env_contract', 'evidence_path')) or 'not available'}`",
            f"- Vercel Env Audit Path: `{vercel.get('env_audit_path', 'not available')}`",
            f"- Vercel Deploy URL: `{first_nonempty(vercel.get('deploy_url'), vercel.get('deployment_url')) or 'not available'}`",
            f"- Vercel Deploy Status: `{first_nonempty(vercel.get('deploy_status'), vercel.get('deployment_status')) or 'not available'}`",
            f"- Vercel Deploy Evidence Path: `{first_nonempty(vercel.get('deploy_evidence_path'), vercel.get('deployment_evidence_path')) or 'not available'}`",
            f"- Vercel Deploy Audit Path: `{vercel.get('deploy_audit_path', 'not available')}`",
            "",
            "## Protected Change Review",
            f"- Protected Change Classification: `{protected_change.get('classification', 'not available')}`",
            f"- Protected Change Status: `{protected_change.get('status', 'not available')}`",
            f"- Protected Change Evidence: `{protected_change.get('evidence_path', 'not available')}`",
            f"- Platform Justification Status: `{justification.get('status', 'not available')}`",
            f"- Platform Justification Artifact: `{justification.get('artifact_path', 'not available')}`",
            f"- Governance Action: `{justification.get('governance_action_id', 'not available')}`",
            "",
            "## Deployment Outcome",
            f"- Latest Stage Outcome: `{first_nonempty(latest.get('outcome')) or 'not available'}`",
            f"- Latest Artifact: `{latest.get('artifact', 'not available')}`",
            f"- Deployment Failure Visibility: `{normalize_flag(first_nonempty(vercel.get('deploy_status'), vercel.get('deployment_status')).lower() in {'blocked', 'failed'})}`",
            "",
            "## Final Handoff",
            f"- Final Handoff Path: `{final_handoff_path or 'not available'}`",
            f"- Handoff Status: `{'completed' if final_handoff_path else 'not available'}`",
            "",
            "## Event History",
            *(history_lines or ["- stage=`not available` status=`not available` outcome=`not available` block_reason=`not available` artifact=`not available` evidence=`not available` handoff=`not available`"]),
            "",
            "This latest view is derived from the append-only approved delivery event stream.",
        ]
    ).rstrip() + "\n"


def render_approved_delivery_status(project_dir: Path) -> str:
    project_dir = Path(project_dir)
    record = load_json(project_dir / APPROVED_RECORD_NAME)
    events = load_events(project_dir / EVENTS_FILE_NAME)
    markdown = build_status_markdown(events, record, project_dir)
    status_path = project_dir / STATUS_FILE_NAME
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(markdown, encoding="utf-8")
    final_review_path = Path(first_nonempty(get_nested(record, "artifacts", "final_review_path"), (project_dir / "FINAL_OPERATOR_REVIEW.md").as_posix()))
    final_review_path.parent.mkdir(parents=True, exist_ok=True)
    final_review_path.write_text(markdown, encoding="utf-8")
    return markdown


def main() -> int:
    args = parse_args()
    try:
        project_dir = Path(args.project_dir)
        record = load_json(project_dir / APPROVED_RECORD_NAME)
        events = load_events(project_dir / EVENTS_FILE_NAME)
        if args.dry_run:
            print(build_status_markdown(events, record, project_dir), end="")
            return 0
        render_approved_delivery_status(project_dir)
    except ApprovedDeliveryStatusError as exc:
        print(f"approved delivery status render error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {(Path(args.project_dir) / STATUS_FILE_NAME).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
