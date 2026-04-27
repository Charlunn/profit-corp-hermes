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
STATUS_RELATIVE_PATH = ".hermes/DELIVERY_STATUS.md"


class DeliveryStatusError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render DELIVERY_STATUS.md from the workspace-local delivery event stream.")
    parser.add_argument("--workspace-path", required=True, help="Path to the generated workspace.")
    parser.add_argument("--dry-run", action="store_true", help="Print markdown instead of writing the status file.")
    return parser.parse_args()


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
            raise DeliveryStatusError(f"invalid JSONL at line {line_number}: {path}") from exc
        if not isinstance(payload, dict):
            raise DeliveryStatusError(f"delivery event at line {line_number} must be an object")
        events.append(payload)
    return events


def build_status_markdown(events: list[dict[str, Any]]) -> str:
    latest = events[-1] if events else {}
    return "\n".join(
        [
            "# Delivery Status",
            f"- **Authority Source**: `{EVENTS_RELATIVE_PATH}`",
            f"- **Run ID**: `{latest.get('run_id', 'not available')}`",
            f"- **Workspace**: `{latest.get('workspace_name', 'not available')}`",
            f"- **Current Stage**: `{latest.get('stage', 'not available')}`",
            f"- **Last Role**: `{latest.get('role', 'not available')}`",
            f"- **Last Action**: `{latest.get('action', 'not available')}`",
            f"- **Latest Outcome**: `{latest.get('outcome', 'not available')}`",
            f"- **Gate Status**: `{latest.get('gate_status', 'not available')}`",
            f"- **Scope Status**: `{latest.get('scope_status', 'not available')}`",
            f"- **Latest Artifact**: `{latest.get('artifact', 'not available')}`",
            "",
            "This latest view is derived from the append-only delivery event stream.",
        ]
    ).rstrip() + "\n"


def render_delivery_status(workspace: Path) -> str:
    workspace = Path(workspace)
    events = load_events(workspace / EVENTS_RELATIVE_PATH)
    markdown = build_status_markdown(events)
    status_path = workspace / STATUS_RELATIVE_PATH
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(markdown, encoding="utf-8")
    return markdown


def main() -> int:
    args = parse_args()
    try:
        workspace = Path(args.workspace_path)
        if args.dry_run:
            print(build_status_markdown(load_events(workspace / EVENTS_RELATIVE_PATH)), end="")
            return 0
        render_delivery_status(workspace)
    except DeliveryStatusError as exc:
        print(f"delivery status render error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {(Path(args.workspace_path) / STATUS_RELATIVE_PATH).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
