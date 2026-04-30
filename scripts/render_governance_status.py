#!/usr/bin/env python3
import argparse
import sys

from governance_common import (
    GOVERNANCE_EVENTS_PATH,
    GOVERNANCE_STATUS_PATH,
    GovernanceError,
    ensure_governance_dir,
    load_jsonl,
    render_status_markdown,
    write_text,
)


class GovernanceStatusRenderError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the governance latest status view from governance_events.jsonl.")
    parser.add_argument("--dry-run", action="store_true", help="Render markdown to stdout without writing files.")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        ensure_governance_dir()
        events = load_jsonl(GOVERNANCE_EVENTS_PATH)
        markdown = render_status_markdown(events)
        if args.dry_run:
            print(markdown, end="")
            return 0
        write_text(GOVERNANCE_STATUS_PATH, markdown)
        print(f"Wrote {GOVERNANCE_STATUS_PATH}")
        return 0
    except (GovernanceError, GovernanceStatusRenderError) as exc:
        print(f"governance status render error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
