#!/usr/bin/env python3
import argparse
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.chat_intake_common import AUTHORITY_FILE_NAME, CHAT_STATUS_NAME, load_json


class ChatRunStatusError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render a chat-run status view from the authoritative chat-run record.")
    parser.add_argument("--run-id", required=True, help="Canonical chat run identifier.")
    parser.add_argument("--project-dir", default="", help="Optional explicit chat-run directory.")
    parser.add_argument("--dry-run", action="store_true", help="Print markdown instead of writing the status file.")
    return parser.parse_args()


def resolve_project_dir(run_id: str, explicit_dir: str = "") -> Path:
    if explicit_dir.strip():
        return Path(explicit_dir)
    from scripts.chat_intake_common import run_dir_for

    return run_dir_for(run_id)


def _build_hermes_status_lines(record: dict, authority_path: str, status_path: str) -> list[str]:
    origin = dict(record.get("chat_origin", {}))
    pipeline = dict(record.get("pipeline", {}))
    blocked = dict(record.get("blocked", {}))
    role_routing = dict(record.get("role_routing", {}) or {})
    status = str(pipeline.get("status", "ready")).strip().lower()
    stage = str(pipeline.get("stage", "intake")).strip().lower()

    if status == "blocked":
        headline = "Start blocked"
        summary = "Hermes could not safely start this project yet."
        detail = str(blocked.get("detail", "Missing recovery detail.")).strip() or "Missing recovery detail."
        next_step = "Review the blocker detail and the authority artifacts below before retrying."
    elif status == "running" and stage == "qualification":
        headline = "Request accepted"
        summary = "Hermes is preparing the governed project run and moving into qualification."
        detail = f"Current step: {stage}."
        next_step = "Hermes will keep the request moving without asking you to choose scripts or backend entrypoints."
    else:
        headline = "Request received"
        summary = "Hermes recorded the project-start request and is preparing the governed run."
        detail = f"Current step: {stage or 'intake'}."
        next_step = "Hermes will confirm progress from the persisted run record."

    routing_lines: list[str] = []
    if role_routing:
        workstream = str(role_routing.get("workstream", "")).strip()
        current_role = str(role_routing.get("current_role", "")).strip()
        artifact_path = str(role_routing.get("artifact_path", "")).strip()
        next_handoff = str(role_routing.get("next_handoff", "")).strip()
        if workstream:
            detail = f"{detail} Hermes is currently handling {workstream}."
        if status == "blocked" and current_role:
            next_step = f"Review the blocker detail and the routing artifacts below. Current internal owner: {current_role}."
        routing_lines = [
            "",
            "## Internal Routing",
            f"- **Current Workstream**: `{workstream or stage or 'not available'}`",
            f"- **Responsible Role**: `{current_role or 'not available'}`",
            f"- **Routing Artifact**: `{artifact_path or 'not available'}`",
            f"- **Next Handoff**: `{next_handoff or 'not available'}`",
        ]

    return [
        "# Hermes Project Start",
        f"- **Status**: {headline}",
        f"- **Summary**: {summary}",
        f"- **Requester**: `{origin.get('requester', {}).get('display_name', 'not available')}`",
        f"- **Project Intent**: `{origin.get('intent', 'not available')}`",
        f"- **Run ID**: `{record.get('run_id', 'not available')}`",
        f"- **Detail**: {detail}",
        f"- **Next**: {next_step}",
        "",
        "## Governance Artifacts",
        f"- **Authority Record**: `{authority_path}`",
        f"- **Status View**: `{status_path}`",
        *routing_lines,
        "",
        "This owner-facing update is derived from the authoritative governed run record.",
    ]


def build_status_markdown(record: dict) -> str:
    origin = dict(record.get("chat_origin", {}))
    pipeline = dict(record.get("pipeline", {}))
    dispatch = dict(record.get("dispatch", {}))
    blocked = dict(record.get("blocked", {}))
    authority_path = str(record.get("artifacts", {}).get("authority_record_path", "not available"))
    status_path = str(record.get("artifacts", {}).get("status_path", "not available"))
    if str(origin.get("platform", "")).strip().lower() == "hermes":
        return "\n".join(_build_hermes_status_lines(record, authority_path, status_path)).rstrip() + "\n"
    return "\n".join(
        [
            "# Chat Run Status",
            f"- **Authority Source**: `{AUTHORITY_FILE_NAME}`",
            f"- **Run ID**: `{record.get('run_id', 'not available')}`",
            f"- **Platform**: `{origin.get('platform', 'not available')}`",
            f"- **Channel / Chat**: `{origin.get('channel_or_chat_id', 'not available')}`",
            f"- **Thread / Reply Context**: `{origin.get('thread_or_reply_context', 'not available')}`",
            f"- **Requester**: `{origin.get('requester', {}).get('display_name', 'not available')}`",
            f"- **Origin Message ID**: `{origin.get('message_id', 'not available')}`",
            f"- **Intent**: `{origin.get('intent', 'not available')}`",
            f"- **Current Stage**: `{pipeline.get('stage', 'intake')}`",
            f"- **Current Status**: `{pipeline.get('status', 'ready')}`",
            f"- **Dispatch Mode**: `{dispatch.get('mode', 'not available')}`",
            f"- **Dispatch Target**: `{dispatch.get('target', 'not available')}`",
            f"- **Dispatch Command**: `{dispatch.get('command', 'not available')}`",
            f"- **Blocked Reason**: `{blocked.get('reason', 'none')}`",
            "",
            "This latest view is derived from the authoritative chat-run record.",
        ]
    ).rstrip() + "\n"


def render_chat_run_status(run_id: str, project_dir: str = "") -> str:
    output_dir = resolve_project_dir(run_id, project_dir)
    authority_path = output_dir / AUTHORITY_FILE_NAME
    if not authority_path.exists():
        raise ChatRunStatusError(f"chat run authority not found: {authority_path}")
    record = load_json(authority_path)
    markdown = build_status_markdown(record)
    (output_dir / CHAT_STATUS_NAME).write_text(markdown, encoding="utf-8")
    return markdown


def main() -> int:
    args = parse_args()
    try:
        if args.dry_run:
            project_dir = resolve_project_dir(args.run_id, args.project_dir)
            record = load_json(project_dir / AUTHORITY_FILE_NAME)
            print(build_status_markdown(record), end="")
            return 0
        render_chat_run_status(args.run_id, args.project_dir)
    except (ChatRunStatusError, OSError) as exc:
        print(f"chat run status error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {(resolve_project_dir(args.run_id, args.project_dir) / CHAT_STATUS_NAME).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
