#!/usr/bin/env python3
import argparse
import sys
from typing import Any

from governance_common import (
    DECISION_TRACE_PATH,
    GOVERNANCE_EVENTS_PATH,
    OPERATING_DECISION_PACKAGE_PATH,
    GovernanceError,
    append_event,
    find_latest_event,
    generate_action_id,
    is_high_impact_action,
    load_jsonl,
    refresh_status_view,
    relative,
    timestamp_now,
    validate_actor_target,
)


class GovernanceApprovalError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Request or decide governance approval state transitions.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    def add_common_arguments(target: argparse.ArgumentParser, include_action_id: bool) -> None:
        if include_action_id:
            target.add_argument("--action-id", required=True, help="Existing governance action_id.")
        target.add_argument("--action-type", help="Governed action type, such as finance.revenue or fallback.takeover.tech_spec.")
        target.add_argument("--actor", required=True, help="Actor requesting or deciding the action.")
        target.add_argument("--target-artifact", help="Repo-relative artifact path governed by this action.")
        target.add_argument("--related-decision-package", default=relative(OPERATING_DECISION_PACKAGE_PATH))
        target.add_argument("--reason", required=True, help="Human-readable reason for the governance event.")
        target.add_argument("--trace-path", default=relative(DECISION_TRACE_PATH))
        target.add_argument("--judgment-id", action="append", default=[])
        target.add_argument("--primary-writer", default="")
        target.add_argument("--approved-by", default="")

    request_parser = subparsers.add_parser("request", help="Create a requested governance action.")
    add_common_arguments(request_parser, include_action_id=False)
    request_parser.add_argument("--status-before", default="none")

    approve_parser = subparsers.add_parser("approve", help="Approve an existing pending governance action.")
    add_common_arguments(approve_parser, include_action_id=True)

    reject_parser = subparsers.add_parser("reject", help="Reject an existing pending governance action.")
    add_common_arguments(reject_parser, include_action_id=True)

    override_parser = subparsers.add_parser("override", help="Override an existing pending governance action as CEO.")
    add_common_arguments(override_parser, include_action_id=True)

    return parser.parse_args()


def build_related_trace(args: argparse.Namespace) -> dict[str, Any]:
    judgment_ids = [item for item in args.judgment_id if item]
    return {
        "trace_path": args.trace_path,
        "judgment_ids": judgment_ids,
    }


def build_request_event(args: argparse.Namespace) -> dict[str, Any]:
    action_type = args.action_type or "unclassified"
    validation = validate_actor_target(args.actor, args.target_artifact or "", action_type)
    is_fallback = validation["is_fallback"]
    if is_fallback and not action_type.startswith("fallback.takeover"):
        raise GovernanceApprovalError("CEO fallback requests must use fallback.takeover.* action types")
    return {
        "action_id": generate_action_id(),
        "event_type": "requested",
        "action_type": action_type,
        "actor": args.actor,
        "target_artifact": args.target_artifact or "",
        "related_decision_package": args.related_decision_package,
        "status_before": args.status_before,
        "status_after": "pending",
        "approved_by": args.approved_by or args.actor,
        "timestamp": timestamp_now(),
        "reason": args.reason,
        "result_code": "approval_requested" if is_high_impact_action(action_type) else "non_high_impact_requested",
        "primary_writer": args.primary_writer or validation["primary_writer"],
        "override_reason": "",
        "related_trace": build_related_trace(args),
    }


def require_pending(action_id: str) -> dict[str, Any]:
    latest = find_latest_event(action_id, load_jsonl(GOVERNANCE_EVENTS_PATH))
    if latest is None:
        raise GovernanceApprovalError(f"action_id not found: {action_id}")
    if str(latest.get("status_after", "")).lower() != "pending":
        raise GovernanceApprovalError(f"action_id is not pending: {action_id}")
    return latest


def build_decision_event(args: argparse.Namespace, event_type: str, status_after: str) -> dict[str, Any]:
    latest = require_pending(args.action_id)
    action_type = args.action_type or latest.get("action_type", "unclassified")
    target_artifact = args.target_artifact or latest.get("target_artifact", "")
    validation = validate_actor_target(args.actor, target_artifact, action_type)
    approved_by = args.approved_by or args.actor
    if event_type == "override" and approved_by != "ceo":
        raise GovernanceApprovalError("override is only allowed when approved_by=ceo")
    if validation["is_fallback"] and event_type not in {"approved", "override"}:
        raise GovernanceApprovalError("fallback takeover requests can only transition through approved or override")
    return {
        "action_id": args.action_id,
        "event_type": event_type,
        "action_type": action_type,
        "actor": args.actor,
        "target_artifact": target_artifact,
        "related_decision_package": args.related_decision_package or latest["related_decision_package"],
        "status_before": latest.get("status_after", "pending"),
        "status_after": status_after,
        "approved_by": approved_by,
        "timestamp": timestamp_now(),
        "reason": args.reason,
        "result_code": f"approval_{status_after}",
        "primary_writer": args.primary_writer or validation["primary_writer"] or latest.get("primary_writer", ""),
        "override_reason": args.reason if event_type == "override" else "",
        "related_trace": build_related_trace(args) if args.judgment_id or args.trace_path else latest.get("related_trace", {}),
    }


def main() -> int:
    args = parse_args()
    try:
        if not args.related_decision_package:
            raise GovernanceApprovalError("related decision package is required")
        if args.command == "request":
            if not args.action_type:
                raise GovernanceApprovalError("request requires --action-type")
            if not args.target_artifact:
                raise GovernanceApprovalError("request requires --target-artifact")
            event = build_request_event(args)
        elif args.command == "approve":
            event = build_decision_event(args, "approved", "approved")
        elif args.command == "reject":
            event = build_decision_event(args, "rejected", "rejected")
        elif args.command == "override":
            event = build_decision_event(args, "override", "override")
        else:
            raise GovernanceApprovalError(f"unsupported command: {args.command}")
        append_event(event)
        refresh_status_view()
        print(event["action_id"])
        return 0
    except (GovernanceError, GovernanceApprovalError) as exc:
        print(f"governance approval error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
