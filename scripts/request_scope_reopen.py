#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
if str(SCRIPTS_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_DIR))


from scripts.append_delivery_event import append_delivery_event, load_events
from scripts.check_template_conformance import PROTECTED_PATHS
from scripts.governance_common import append_event, refresh_status_view, timestamp_now
from scripts.render_delivery_status import render_delivery_status
from scripts.request_governance_approval import build_request_event


SCOPE_REOPEN_SCOPE_STATUS = "scope-reopen-requested"


class ScopeReopenError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Request a governance-backed delivery scope reopen and record the matching delivery event.")
    parser.add_argument("--workspace-path", required=True, help="Path to the generated workspace.")
    parser.add_argument("--run-id", required=True, help="Delivery run identifier.")
    parser.add_argument("--stage", required=True, help="Current delivery stage requesting reopen.")
    parser.add_argument("--role", required=True, help="Role requesting reopen, such as development-specialist.")
    parser.add_argument("--target-artifact", required=True, help="Repo-relative target that triggered the reopen request.")
    parser.add_argument("--reason", required=True, help="Human-readable reopen reason.")
    return parser.parse_args()


def workspace_name_for(workspace: Path) -> str:
    return Path(workspace).name


def action_type_for(target_artifact: str) -> str:
    normalized = target_artifact.strip().replace("\\", "/")
    if normalized.startswith("approved_contract:"):
        return "delivery.scope_reopen.contract_drift"
    if normalized in PROTECTED_PATHS:
        return "delivery.scope_reopen.protected_path"
    return "delivery.scope_reopen.scope_expansion"


def build_governance_args(*, role: str, target_artifact: str, reason: str):
    return argparse.Namespace(
        action_type=action_type_for(target_artifact),
        actor=role,
        target_artifact=target_artifact,
        related_decision_package="assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md",
        reason=reason,
        trace_path="assets/shared/trace/decision_package_trace.json",
        judgment_id=[],
        primary_writer="",
        approved_by="ceo",
        status_before="approved-brief-only",
    )


def build_delivery_event(*, workspace: Path, run_id: str, role: str, stage: str, target_artifact: str, reason: str, timestamp: str) -> dict[str, str]:
    return {
        "run_id": run_id,
        "workspace_name": workspace_name_for(workspace),
        "role": role,
        "stage": stage,
        "action": "scope_reopen_requested",
        "artifact": target_artifact,
        "timestamp": timestamp,
        "outcome": "pending",
        "gate_status": "pending",
        "scope_status": SCOPE_REOPEN_SCOPE_STATUS,
        "reason": reason,
    }


def encode_contract_value(value: Any) -> str:
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def next_delivery_timestamp(workspace: Path, fallback_timestamp: str) -> str:
    events_path = Path(workspace) / ".hermes" / "delivery-events.jsonl"
    existing = load_events(events_path)
    if not existing:
        return fallback_timestamp
    latest_timestamp = str(existing[-1].get("timestamp", "")).strip()
    if not latest_timestamp or fallback_timestamp >= latest_timestamp:
        return fallback_timestamp
    return latest_timestamp


def request_scope_reopen(
    workspace: Path,
    *,
    run_id: str,
    stage: str,
    role: str,
    target_artifact: str,
    reason: str,
) -> dict[str, Any]:
    workspace = Path(workspace)
    governance_event = build_request_event(
        build_governance_args(role=role, target_artifact=target_artifact, reason=reason)
    )
    append_event(governance_event)
    refresh_status_view()

    delivery_timestamp = next_delivery_timestamp(workspace, governance_event["timestamp"] or timestamp_now())
    delivery_event = build_delivery_event(
        workspace=workspace,
        run_id=run_id,
        role=role,
        stage=stage,
        target_artifact=target_artifact,
        reason=reason,
        timestamp=delivery_timestamp,
    )
    append_delivery_event(workspace, delivery_event)
    render_delivery_status(workspace)

    return {
        "ok": True,
        "action_id": governance_event["action_id"],
        "governance_event": governance_event,
        "delivery_event": delivery_event,
        "status_path": (workspace / ".hermes" / "DELIVERY_STATUS.md").as_posix(),
    }


def request_contract_drift_reopen(
    workspace: Path,
    *,
    run_id: str,
    stage: str,
    role: str,
    drift_field: str,
    approved_value: Any,
    proposed_value: Any,
    reason: str,
) -> dict[str, Any]:
    normalized_field = str(drift_field).strip()
    if not normalized_field:
        raise ScopeReopenError("drift_field is required")
    target_artifact = f"approved_contract:{normalized_field}"
    approved_text = encode_contract_value(approved_value)
    proposed_text = encode_contract_value(proposed_value)
    drift_reason = (
        f"Locked contract drift for {normalized_field}: approved={approved_text}; "
        f"proposed={proposed_text}. {reason.strip()}"
    ).strip()
    result = request_scope_reopen(
        workspace,
        run_id=run_id,
        stage=stage,
        role=role,
        target_artifact=target_artifact,
        reason=drift_reason,
    )
    delivery_events_path = Path(workspace) / ".hermes" / "delivery-events.jsonl"
    events = load_events(delivery_events_path)
    if not events:
        raise ScopeReopenError("delivery reopen event was not recorded")
    latest = dict(events[-1])
    latest["contract_drift_field"] = normalized_field
    latest["approved_value"] = approved_text
    latest["proposed_value"] = proposed_text
    events[-1] = latest
    delivery_events_path.write_text(
        "\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n",
        encoding="utf-8",
    )
    render_delivery_status(workspace)
    result["delivery_event"] = latest
    return result


def main() -> int:
    args = parse_args()
    try:
        result = request_scope_reopen(
            Path(args.workspace_path),
            run_id=args.run_id,
            stage=args.stage,
            role=args.role,
            target_artifact=args.target_artifact,
            reason=args.reason,
        )
    except Exception as exc:
        print(f"scope reopen error: {exc}", file=sys.stderr)
        return 1
    print(result["action_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
