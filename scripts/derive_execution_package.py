#!/usr/bin/env python3
import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SHARED_DIR = ROOT_DIR / "assets" / "shared"
DECISION_PACKAGES_DIR = SHARED_DIR / "decision_packages"
EXECUTION_PACKAGES_DIR = SHARED_DIR / "execution_packages"
EXECUTION_HISTORY_DIR = EXECUTION_PACKAGES_DIR / "history"
TRACE_DIR = SHARED_DIR / "trace"
OPERATING_DECISION_PACKAGE_PATH = DECISION_PACKAGES_DIR / "OPERATING_DECISION_PACKAGE.md"
DECISION_TRACE_PATH = TRACE_DIR / "decision_package_trace.json"
EXECUTION_PACKAGE_PATH = EXECUTION_PACKAGES_DIR / "EXECUTION_PACKAGE.md"
EXECUTION_HISTORY_TEMPLATE = "{date}-execution-package.md"
ALLOWED_WRITE_DIRS = (
    EXECUTION_PACKAGES_DIR,
    EXECUTION_HISTORY_DIR,
)


class ExecutionPackageError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive the execution package from the operating decision package.")
    parser.add_argument("--date", default="", help="Override the report date (YYYY-MM-DD).")
    parser.add_argument("--dry-run", action="store_true", help="Render output without writing files.")
    return parser.parse_args()


def today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def ensure_dirs() -> None:
    EXECUTION_PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    EXECUTION_HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def ensure_allowed_write_path(path: Path) -> None:
    resolved = path.resolve()
    for directory in ALLOWED_WRITE_DIRS:
        try:
            resolved.relative_to(directory.resolve())
            return
        except ValueError:
            continue
    raise ExecutionPackageError(f"refusing to write outside allowed directories: {path}")


def write_output(path: Path, content: str) -> None:
    ensure_allowed_write_path(path)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def load_text(path: Path, label: str) -> str:
    if not path.exists():
        raise ExecutionPackageError(f"{label} not found: {path}")
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise ExecutionPackageError(f"{label} is empty: {path}")
    return content


def relative(path: Path) -> str:
    return path.relative_to(ROOT_DIR).as_posix()


def require_section(content: str, heading: str) -> None:
    if heading not in content:
        raise ExecutionPackageError(f"operating package missing required section: {heading}")


def require_source_reference(content: str) -> None:
    if relative(OPERATING_DECISION_PACKAGE_PATH) not in content and "CEO_RANKING.md" not in content:
        raise ExecutionPackageError("operating package missing source references")


def assert_derived_only_inputs() -> None:
    if OPERATING_DECISION_PACKAGE_PATH.name != "OPERATING_DECISION_PACKAGE.md":
        raise ExecutionPackageError("unexpected operating decision package path")
    if DECISION_TRACE_PATH.name != "decision_package_trace.json":
        raise ExecutionPackageError("unexpected decision trace path")


def extract_value(content: str, label: str) -> str:
    pattern = re.compile(rf"^- \*\*{re.escape(label)}\*\*: (.+)$", re.MULTILINE)
    match = pattern.search(content)
    if not match:
        raise ExecutionPackageError(f"missing required value in operating package: {label}")
    return match.group(1).strip()


def extract_first_table_row(content: str) -> dict[str, str]:
    lines = content.splitlines()
    for line in lines:
        if line.startswith("| 1 |"):
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) < 6:
                raise ExecutionPackageError("Top 3 first row is malformed")
            return {
                "rank": parts[0],
                "idea_id": parts[1],
                "title": parts[2],
                "why_now": parts[3],
                "signal": parts[4],
                "motion": parts[5],
            }
    raise ExecutionPackageError("Top 3 first row not found in operating package")


def extract_first_risk_summary(content: str) -> str:
    section_start = content.find("## 主要风险")
    if section_start == -1:
        raise ExecutionPackageError("heading not found: ## 主要风险")
    section = content[section_start:].split("\n## ", 1)[0]
    return extract_labeled_bullet_value(section, "Summary")


def extract_first_bullet_after_heading(content: str, heading: str) -> str:
    section_start = content.find(heading)
    if section_start == -1:
        raise ExecutionPackageError(f"heading not found: {heading}")
    section = content[section_start:].split("\n## ", 1)[0]
    for line in section.splitlines():
        stripped = line.strip()
        if stripped.startswith("- "):
            return stripped[2:]
    raise ExecutionPackageError(f"no bullet found under heading: {heading}")


def extract_labeled_bullet_value(content: str, label: str) -> str:
    pattern = re.compile(rf"^- \*\*{re.escape(label)}\*\*: (.+)$", re.MULTILINE)
    match = pattern.search(content)
    if not match:
        raise ExecutionPackageError(f"missing required labeled bullet in operating package: {label}")
    return match.group(1).strip()


def history_output_path(date_value: str) -> Path:
    return EXECUTION_HISTORY_DIR / EXECUTION_HISTORY_TEMPLATE.format(date=date_value)


def render_execution_package(date_value: str, operating_package: str, trace_content: str) -> str:
    require_section(operating_package, "## Overall Conclusion / 一句话总判断")
    require_section(operating_package, "## Top 3 Ranked Opportunities")
    require_section(operating_package, "## Operating Framing")
    require_section(operating_package, "## 主要风险")
    require_section(operating_package, "## 推荐下一步")
    require_source_reference(operating_package)
    if '"judgment_links"' not in trace_content:
        raise ExecutionPackageError("decision trace missing judgment_links")

    top_row = extract_first_table_row(operating_package)
    goal = extract_value(operating_package, "Goal")
    target_user = extract_value(operating_package, "Target User")
    mvp_framing = extract_value(operating_package, "MVP Framing")
    key_risk = extract_first_risk_summary(operating_package)
    first_action = extract_first_bullet_after_heading(operating_package, "## 推荐下一步")

    return (
        f"# Execution Package - {date_value}\n"
        f"- **Derived From**: `{relative(OPERATING_DECISION_PACKAGE_PATH)}`\n"
        f"- **Source Trace**: `{relative(DECISION_TRACE_PATH)}`\n"
        f"- **Goal**: {goal}\n"
        f"- **Target User**: {target_user}\n"
        f"- **MVP Framing**: {mvp_framing}\n"
        f"- **Key Risks**: {key_risk}\n"
        f"- **Recommended Near-Term Actions**:\n"
        f"  - {first_action}\n"
        f"  - Keep scope anchored on {top_row['idea_id']} until user validation confirms expansion.\n\n"
        f"## Kickoff Focus\n"
        f"- **Primary Idea**: {top_row['idea_id']}\n"
        f"- **Why This Opportunity**: {top_row['why_now']}\n"
        f"- **Signal Reference**: {top_row['signal']}\n"
        f"- **MVP Boundary**: Stay within the operator workflow implied by the operating package; do not add task-board governance fields.\n"
    )


def main() -> int:
    args = parse_args()
    try:
        assert_derived_only_inputs()
        date_value = args.date or today_iso()
        operating_package = load_text(OPERATING_DECISION_PACKAGE_PATH, "operating decision package")
        trace_content = load_text(DECISION_TRACE_PATH, "decision trace")
        latest_output = render_execution_package(date_value, operating_package, trace_content)
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
        print(f"Wrote {relative(EXECUTION_PACKAGE_PATH)}")
        print(f"Wrote {relative(history_path)}")
        return 0
    except ExecutionPackageError as exc:
        print(f"execution package error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
