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
STATUS_FILE_NAME = "DELIVERY_PIPELINE_STATUS.md"


class ApprovedDeliveryStatusError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render DELIVERY_PIPELINE_STATUS.md from the Phase 10 authority event stream.")
    parser.add_argument("--project-dir", required=True, help="Approved-project directory containing the authority bundle.")
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
            raise ApprovedDeliveryStatusError(f"invalid JSONL at line {line_number}: {path}") from exc
        if not isinstance(payload, dict):
            raise ApprovedDeliveryStatusError(f"approved delivery event at line {line_number} must be an object")
        events.append(payload)
    return events


def build_status_markdown(events: list[dict[str, Any]]) -> str:
    latest = events[-1] if events else {}
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
    shipping = latest.get("shipping", {}) if isinstance(latest.get("shipping"), dict) else {}
    github = shipping.get("github", {}) if isinstance(shipping.get("github"), dict) else {}
    vercel = shipping.get("vercel", {}) if isinstance(shipping.get("vercel"), dict) else {}
    return "\n".join(
        [
            "# Delivery Pipeline Status",
            f"- **Authority Source**: `{EVENTS_FILE_NAME}`",
            f"- **Project Slug**: `{latest.get('project_slug', 'not available')}`",
            f"- **Current Stage**: `{latest.get('stage', 'not available')}`",
            f"- **Pipeline Status**: `{latest.get('status', 'not available')}`",
            f"- **Last Action**: `{latest.get('action', 'not available')}`",
            f"- **Latest Outcome**: `{latest.get('outcome', 'not available')}`",
            f"- **Authority Record**: `{latest.get('authority_record_path', 'not available')}`",
            f"- **Delivery Brief**: `{latest.get('brief_path', 'not available')}`",
            f"- **Workspace Path**: `{latest.get('workspace_path', 'not available')}`",
            f"- **Delivery Run ID**: `{latest.get('delivery_run_id', 'not available')}`",
            f"- **GitHub Repository Mode**: `{github.get('repository_mode', 'not available')}`",
            f"- **GitHub Repository Owner**: `{github.get('repository_owner', 'not available')}`",
            f"- **GitHub Repository**: `{github.get('repository_name', 'not available')}`",
            f"- **GitHub Repository URL**: `{github.get('repository_url', 'not available')}`",
            f"- **GitHub Branch**: `{github.get('default_branch', 'not available')}`",
            f"- **GitHub Sync Commit**: `{github.get('synced_commit', 'not available')}`",
            f"- **GitHub Sync Evidence**: `{github.get('sync_evidence_path', 'not available')}`",
            f"- **Vercel Project**: `{vercel.get('project_name', 'not available')}`",
            f"- **Vercel Env Contract**: `{vercel.get('env_contract_path', 'not available')}`",
            f"- **Deploy URL**: `{vercel.get('deployment_url', 'not available')}`",
            f"- **Deploy Status**: `{vercel.get('deployment_status', 'not available')}`",
            f"- **Block Reason**: `{latest.get('block_reason', 'not available')}`",
            f"- **Evidence Path**: `{latest.get('evidence_path', 'not available')}`",
            f"- **Resume From Stage**: `{latest.get('resume_from_stage', 'not available')}`",
            f"- **Final Handoff Path**: `{latest.get('final_handoff_path', 'not available')}`",
            f"- **Latest Artifact**: `{latest.get('artifact', 'not available')}`",
            "",
            "## Event History",
            *(history_lines or ["- stage=`not available` status=`not available` outcome=`not available` block_reason=`not available` artifact=`not available` evidence=`not available` handoff=`not available`"]),
            "",
            "This latest view is derived from the append-only approved delivery event stream.",
        ]
    ).rstrip() + "\n"


def render_approved_delivery_status(project_dir: Path) -> str:
    project_dir = Path(project_dir)
    events = load_events(project_dir / EVENTS_FILE_NAME)
    markdown = build_status_markdown(events)
    status_path = project_dir / STATUS_FILE_NAME
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(markdown, encoding="utf-8")
    return markdown


def main() -> int:
    args = parse_args()
    try:
        project_dir = Path(args.project_dir)
        if args.dry_run:
            print(build_status_markdown(load_events(project_dir / EVENTS_FILE_NAME)), end="")
            return 0
        render_approved_delivery_status(project_dir)
    except ApprovedDeliveryStatusError as exc:
        print(f"approved delivery status render error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {(Path(args.project_dir) / STATUS_FILE_NAME).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
