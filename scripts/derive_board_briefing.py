#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SHARED_DIR = ROOT_DIR / "assets" / "shared"
DECISION_PACKAGES_DIR = SHARED_DIR / "decision_packages"
BOARD_BRIEFINGS_DIR = SHARED_DIR / "board_briefings"
BOARD_HISTORY_DIR = BOARD_BRIEFINGS_DIR / "history"
OPERATING_DECISION_PACKAGE_PATH = DECISION_PACKAGES_DIR / "OPERATING_DECISION_PACKAGE.md"
BOARD_BRIEFING_PATH = BOARD_BRIEFINGS_DIR / "BOARD_BRIEFING.md"
BOARD_BRIEFING_HISTORY_TEMPLATE = "{date}-board-briefing.md"
TRACE_DIR = SHARED_DIR / "trace"
ALLOWED_WRITE_DIRS = (
    BOARD_BRIEFINGS_DIR,
    BOARD_HISTORY_DIR,
    TRACE_DIR,
)


class BoardBriefingError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive the board briefing from the operating decision package.")
    parser.add_argument("--date", default="", help="Override the report date (YYYY-MM-DD).")
    parser.add_argument("--dry-run", action="store_true", help="Render output contract details without writing files.")
    return parser.parse_args()


def today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def ensure_dirs() -> None:
    BOARD_BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)
    BOARD_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)


def write_output(path: Path, content: str) -> None:
    resolved = path.resolve()
    if not any(parent.resolve() == resolved.parent for parent in ALLOWED_WRITE_DIRS):
        raise BoardBriefingError(f"refusing to write outside allowed directories: {path}")
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def load_operating_package(path: Path) -> str:
    if not path.exists():
        raise BoardBriefingError(f"operating decision package not found: {path}")
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise BoardBriefingError(f"operating decision package is empty: {path}")
    return content


def history_output_path(date_value: str) -> Path:
    return BOARD_HISTORY_DIR / BOARD_BRIEFING_HISTORY_TEMPLATE.format(date=date_value)


def render_board_briefing(date_value: str) -> str:
    return (
        f"# Board Briefing - {date_value}\n"
        f"- **Derived From**: `{OPERATING_DECISION_PACKAGE_PATH.relative_to(ROOT_DIR).as_posix()}`\n"
        "- **Conclusion**: {{one_line_conclusion}}\n\n"
        "## Top 3\n"
        "1. {{idea_id_1}} — {{short_reason_1}}\n"
        "2. {{idea_id_2}} — {{short_reason_2}}\n"
        "3. {{idea_id_3}} — {{short_reason_3}}\n\n"
        "## Key Numbers / Signals\n"
        "- {{number_or_signal_1}}\n"
        "- {{number_or_signal_2}}\n\n"
        "## Major Risk\n"
        "- {{major_risk}}\n\n"
        "## Required Attention\n"
        "- {{required_attention_item}}\n"
    )


def main() -> int:
    args = parse_args()
    try:
        date_value = args.date or today_iso()
        load_operating_package(OPERATING_DECISION_PACKAGE_PATH)
        latest_output = render_board_briefing(date_value)
        history_path = history_output_path(date_value)
        if args.dry_run:
            print("=== BOARD_BRIEFING.md ===")
            print(latest_output)
            print(f"=== history/{history_path.name} ===")
            print(latest_output)
            return 0
        ensure_dirs()
        write_output(BOARD_BRIEFING_PATH, latest_output)
        write_output(history_path, latest_output)
        print(f"Wrote {BOARD_BRIEFING_PATH.relative_to(ROOT_DIR)}")
        print(f"Wrote {history_path.relative_to(ROOT_DIR)}")
        return 0
    except BoardBriefingError as exc:
        print(f"board briefing error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
