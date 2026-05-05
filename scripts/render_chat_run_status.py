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


def build_status_markdown(record: dict) -> str:
    origin = dict(record.get("chat_origin", {}))
    pipeline = dict(record.get("pipeline", {}))
    dispatch = dict(record.get("dispatch", {}))
    blocked = dict(record.get("blocked", {}))
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
