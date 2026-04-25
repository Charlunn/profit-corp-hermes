#!/usr/bin/env python3
import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SHARED_DIR = ROOT_DIR / "assets" / "shared"
DECISION_PACKAGES_DIR = SHARED_DIR / "decision_packages"
EXECUTION_PACKAGES_DIR = SHARED_DIR / "execution_packages"
EXECUTION_HISTORY_DIR = EXECUTION_PACKAGES_DIR / "history"
OPERATING_DECISION_PACKAGE_PATH = DECISION_PACKAGES_DIR / "OPERATING_DECISION_PACKAGE.md"
EXECUTION_PACKAGE_PATH = EXECUTION_PACKAGES_DIR / "EXECUTION_PACKAGE.md"
EXECUTION_HISTORY_TEMPLATE = "{date}-execution-package.md"
TRACE_DIR = SHARED_DIR / "trace"
ALLOWED_WRITE_DIRS = (
    EXECUTION_PACKAGES_DIR,
    EXECUTION_HISTORY_DIR,
    TRACE_DIR,
)


class ExecutionPackageError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive the execution package from the operating decision package.")
    parser.add_argument("--date", default="", help="Override the report date (YYYY-MM-DD).")
    parser.add_argument("--dry-run", action="store_true", help="Render output contract details without writing files.")
    return parser.parse_args()


def today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def ensure_dirs() -> None:
    EXECUTION_PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    EXECUTION_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)


def write_output(path: Path, content: str) -> None:
    resolved = path.resolve()
    if not any(parent.resolve() == resolved.parent for parent in ALLOWED_WRITE_DIRS):
        raise ExecutionPackageError(f"refusing to write outside allowed directories: {path}")
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def load_operating_package(path: Path) -> str:
    if not path.exists():
        raise ExecutionPackageError(f"operating decision package not found: {path}")
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise ExecutionPackageError(f"operating decision package is empty: {path}")
    return content


def history_output_path(date_value: str) -> Path:
    return EXECUTION_HISTORY_DIR / EXECUTION_HISTORY_TEMPLATE.format(date=date_value)


def render_execution_package(date_value: str) -> str:
    return (
        f"# Execution Package - {date_value}\n"
        f"- **Derived From**: `{OPERATING_DECISION_PACKAGE_PATH.relative_to(ROOT_DIR).as_posix()}`\n"
        "- **Goal**: {{goal_from_operating_package}}\n"
        "- **Target User**: {{target_user_from_operating_package}}\n"
        "- **MVP Framing**: {{mvp_framing_from_operating_package}}\n"
        "- **Key Risks**: {{risk_summary_from_operating_package}}\n"
        "- **Recommended Near-Term Actions**:\n"
        "  - {{action_1}}\n"
        "  - {{action_2}}\n"
    )


def main() -> int:
    args = parse_args()
    try:
        date_value = args.date or today_iso()
        load_operating_package(OPERATING_DECISION_PACKAGE_PATH)
        latest_output = render_execution_package(date_value)
        history_path = history_output_path(date_value)
        if args.dry_run:
            print("=== EXECUTION_PACKAGE.md ===")
            print(latest_output)
            print(f"=== history/{history_path.name} ===")
            print(latest_output)
            return 0
        ensure_dirs()
        write_output(EXECUTION_PACKAGE_PATH, latest_output)
        write_output(history_path, latest_output)
        print(f"Wrote {EXECUTION_PACKAGE_PATH.relative_to(ROOT_DIR)}")
        print(f"Wrote {history_path.relative_to(ROOT_DIR)}")
        return 0
    except ExecutionPackageError as exc:
        print(f"execution package error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
