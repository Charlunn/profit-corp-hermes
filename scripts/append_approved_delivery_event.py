#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


EVENTS_FILE_NAME = "approved-delivery-events.jsonl"
REQUIRED_EVENT_FIELDS = (
    "project_slug",
    "stage",
    "status",
    "action",
    "timestamp",
    "outcome",
    "authority_record_path",
    "brief_path",
    "workspace_path",
    "delivery_run_id",
    "artifact",
    "block_reason",
    "evidence_path",
    "resume_from_stage",
    "final_handoff_path",
)
OPTIONAL_OBJECT_FIELDS = (
    "shipping",
)
ALLOWED_STAGES = {
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
}
ALLOWED_STATUSES = {"ready", "blocked", "completed", "running"}
ALLOWED_OUTCOMES = {"pass", "blocked", "running"}


class ApprovedDeliveryEventError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append a validated Phase 10 approved-project delivery event.")
    parser.add_argument("--project-dir", required=True, help="Approved-project directory containing the authority bundle.")
    parser.add_argument("--event-json", required=True, help="JSON object containing the event payload.")
    return parser.parse_args()


def events_path_for(project_dir: Path) -> Path:
    return Path(project_dir) / EVENTS_FILE_NAME


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
            raise ApprovedDeliveryEventError(f"invalid JSONL at line {line_number}: {path}") from exc
        if not isinstance(payload, dict):
            raise ApprovedDeliveryEventError(f"approved delivery event at line {line_number} must be an object")
        events.append(payload)
    return events


def validate_event(event: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_EVENT_FIELDS if field not in event]
    if missing:
        raise ApprovedDeliveryEventError(f"approved delivery event missing required fields: {', '.join(missing)}")

    for field in REQUIRED_EVENT_FIELDS:
        value = event.get(field)
        if not isinstance(value, str):
            raise ApprovedDeliveryEventError(f"approved delivery event field must be a string: {field}")

    for field in OPTIONAL_OBJECT_FIELDS:
        if field in event and not isinstance(event.get(field), dict):
            raise ApprovedDeliveryEventError(f"approved delivery event field must be an object when present: {field}")

    if event["stage"] not in ALLOWED_STAGES:
        raise ApprovedDeliveryEventError(f"unsupported approved delivery stage: {event['stage']}")
    if event["status"] not in ALLOWED_STATUSES:
        raise ApprovedDeliveryEventError(f"unsupported approved delivery status: {event['status']}")
    if event["outcome"] not in ALLOWED_OUTCOMES:
        raise ApprovedDeliveryEventError(f"unsupported approved delivery outcome: {event['outcome']}")
    if not event["project_slug"].strip():
        raise ApprovedDeliveryEventError("project_slug must not be blank")
    if not event["timestamp"].strip():
        raise ApprovedDeliveryEventError("timestamp must not be blank")


def append_approved_delivery_event(project_dir: Path, event: dict[str, Any]) -> None:
    project_dir = Path(project_dir)
    validate_event(event)
    path = events_path_for(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_events(path)
    if existing:
        latest_timestamp = str(existing[-1].get("timestamp", ""))
        if event["timestamp"] < latest_timestamp:
            raise ApprovedDeliveryEventError("approved delivery events must append in nondecreasing timestamp order")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def main() -> int:
    args = parse_args()
    try:
        payload = json.loads(args.event_json)
        if not isinstance(payload, dict):
            raise ApprovedDeliveryEventError("event JSON must decode to an object")
        append_approved_delivery_event(Path(args.project_dir), payload)
    except (json.JSONDecodeError, ApprovedDeliveryEventError) as exc:
        print(f"approved delivery event error: {exc}", file=sys.stderr)
        return 1
    print(f"appended event to {(Path(args.project_dir) / EVENTS_FILE_NAME).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
