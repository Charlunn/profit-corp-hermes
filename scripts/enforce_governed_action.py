#!/usr/bin/env python3
import argparse
import subprocess
import sys
from typing import Any

from governance_common import (
    GovernanceError,
    append_event,
    find_latest_event,
    refresh_status_view,
    timestamp_now,
    validate_actor_target,
)


class GovernanceBlocked(Exception):
    pass


class GovernedActionError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Enforce gate-before-mutate execution for a governed action.")
    parser.add_argument("--action-id", required=True, help="Existing governance action_id to enforce.")
    parser.add_argument("--command", nargs="+", required=True, help="Authoritative command to run when governance allows it.")
    parser.add_argument("--dry-run", action="store_true", help="Validate governance status without executing the command.")
    return parser.parse_args()


def build_terminal_event(latest: dict[str, Any], event_type: str, status_after: str, reason: str, result_code: str) -> dict[str, Any]:
    return {
        "action_id": latest["action_id"],
        "event_type": event_type,
        "action_type": latest.get("action_type", "unclassified"),
        "actor": latest.get("actor", "unknown"),
        "target_artifact": latest.get("target_artifact", ""),
        "related_decision_package": latest["related_decision_package"],
        "status_before": latest.get("status_after", "pending"),
        "status_after": status_after,
        "approved_by": latest.get("approved_by", ""),
        "timestamp": timestamp_now(),
        "reason": reason,
        "result_code": result_code,
        "primary_writer": latest.get("primary_writer", ""),
        "override_reason": latest.get("override_reason", ""),
        "related_trace": latest.get("related_trace", {}),
    }


def require_allowed_status(action_id: str) -> dict[str, Any]:
    latest = find_latest_event(action_id)
    if latest is None:
        raise GovernedActionError(f"action_id not found: {action_id}")
    validation = validate_actor_target(
        str(latest.get("actor", "")),
        str(latest.get("target_artifact", "")),
        str(latest.get("action_type", "unclassified")),
    )
    if validation["finance_only"]:
        command_text = " ".join(sys.argv)
        if "manage_finance.py" not in command_text:
            raise GovernedActionError("finance-governed actions must execute through manage_finance.py")
    status = str(latest.get("status_after", "")).lower()
    if validation["is_fallback"] and not str(latest.get("action_type", "")).startswith("fallback.takeover"):
        raise GovernedActionError("fallback execution requires fallback.takeover.* action type")
    if status in {"approved", "override"}:
        return latest
    if status in {"pending", "rejected", "blocked", "failed"}:
        event = build_terminal_event(
            latest,
            event_type="blocked",
            status_after="blocked",
            reason=f"Governed action blocked because current approval status is {status}.",
            result_code="governance_blocked",
        )
        append_event(event)
        refresh_status_view()
        raise GovernanceBlocked(f"governed action blocked: {status}")
    raise GovernedActionError(f"unsupported governance status: {status}")


def main() -> int:
    args = parse_args()
    try:
        latest = require_allowed_status(args.action_id)
        if args.dry_run:
            print(f"allowed:{latest.get('status_after', 'unknown')}")
            return 0
        completed = subprocess.run(args.command, check=False)
        if completed.returncode != 0:
            failed_event = build_terminal_event(
                latest,
                event_type="failed",
                status_after="blocked",
                reason=f"Governed action failed while executing authoritative command: {' '.join(args.command)}",
                result_code="authoritative_command_failed",
            )
            append_event(failed_event)
            refresh_status_view()
            return completed.returncode
        print(f"executed:{latest.get('status_after', 'approved')}")
        return 0
    except GovernanceBlocked as exc:
        print(str(exc), file=sys.stderr)
        return 1
    except (GovernanceError, GovernedActionError) as exc:
        print(f"governed action error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
