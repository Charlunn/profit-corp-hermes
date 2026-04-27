#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


EVENTS_RELATIVE_PATH = ".hermes/delivery-events.jsonl"
REQUIRED_EVENT_FIELDS = (
    "run_id",
    "workspace_name",
    "role",
    "stage",
    "action",
    "artifact",
    "timestamp",
    "outcome",
)
ALLOWED_ROLE_STAGE = {
    "delivery-orchestrator": {"design"},
    "design-specialist": {"design"},
    "development-specialist": {"development"},
    "testing-specialist": {"testing"},
    "git-versioning-specialist": {"git versioning"},
    "release-readiness-specialist": {"release readiness"},
}


class DeliveryEventError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Append a validated delivery event to the workspace-local authority stream.")
    parser.add_argument("--workspace-path", required=True, help="Path to the generated workspace.")
    parser.add_argument("--event-json", required=True, help="JSON object containing the event payload.")
    return parser.parse_args()


def events_path_for(workspace: Path) -> Path:
    return Path(workspace) / EVENTS_RELATIVE_PATH


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
            raise DeliveryEventError(f"invalid JSONL at line {line_number}: {path}") from exc
        if not isinstance(payload, dict):
            raise DeliveryEventError(f"delivery event at line {line_number} must be an object")
        events.append(payload)
    return events


def validate_event(event: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_EVENT_FIELDS if field not in event]
    if missing:
        raise DeliveryEventError(f"delivery event missing required fields: {', '.join(missing)}")
    for field in REQUIRED_EVENT_FIELDS:
        value = event.get(field)
        if not isinstance(value, str) or not value.strip():
            raise DeliveryEventError(f"delivery event field must be a non-empty string: {field}")
    role = event["role"]
    stage = event["stage"]
    allowed_stages = ALLOWED_ROLE_STAGE.get(role)
    if allowed_stages is None:
        raise DeliveryEventError(f"unsupported delivery role: {role}")
    if stage not in allowed_stages:
        raise DeliveryEventError(f"role '{role}' is not allowed to emit stage '{stage}'")


def append_delivery_event(workspace: Path, event: dict[str, Any]) -> None:
    workspace = Path(workspace)
    validate_event(event)
    path = events_path_for(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_events(path)
    if existing:
        latest_timestamp = str(existing[-1].get("timestamp", ""))
        if event["timestamp"] < latest_timestamp:
            raise DeliveryEventError("delivery events must append in nondecreasing timestamp order")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def main() -> int:
    args = parse_args()
    try:
        payload = json.loads(args.event_json)
        if not isinstance(payload, dict):
            raise DeliveryEventError("event JSON must decode to an object")
        append_delivery_event(Path(args.workspace_path), payload)
    except (json.JSONDecodeError, DeliveryEventError) as exc:
        print(f"delivery event error: {exc}", file=sys.stderr)
        return 1
    print(f"appended event to {(Path(args.workspace_path) / EVENTS_RELATIVE_PATH).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
