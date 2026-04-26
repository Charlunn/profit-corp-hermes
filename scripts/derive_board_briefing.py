#!/usr/bin/env python3
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SHARED_DIR = ROOT_DIR / "assets" / "shared"
DECISION_PACKAGES_DIR = SHARED_DIR / "decision_packages"
BOARD_BRIEFINGS_DIR = SHARED_DIR / "board_briefings"
BOARD_HISTORY_DIR = BOARD_BRIEFINGS_DIR / "history"
TRACE_DIR = SHARED_DIR / "trace"
GOVERNANCE_DIR = SHARED_DIR / "governance"
OPERATING_DECISION_PACKAGE_PATH = DECISION_PACKAGES_DIR / "OPERATING_DECISION_PACKAGE.md"
DECISION_TRACE_PATH = TRACE_DIR / "decision_package_trace.json"
GOVERNANCE_STATUS_PATH = GOVERNANCE_DIR / "GOVERNANCE_STATUS.md"
LEDGER_PATH = SHARED_DIR / "LEDGER.json"
BOARD_BRIEFING_PATH = BOARD_BRIEFINGS_DIR / "BOARD_BRIEFING.md"
BOARD_BRIEFING_HISTORY_TEMPLATE = "{date}-board-briefing.md"
ALLOWED_WRITE_DIRS = (
    BOARD_BRIEFINGS_DIR,
    BOARD_HISTORY_DIR,
)


class BoardBriefingError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Derive the board briefing from the operating decision package.")
    parser.add_argument("--date", default="", help="Override the report date (YYYY-MM-DD).")
    parser.add_argument("--dry-run", action="store_true", help="Render output without writing files.")
    return parser.parse_args()


def today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def ensure_dirs() -> None:
    BOARD_BRIEFINGS_DIR.mkdir(parents=True, exist_ok=True)
    BOARD_HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def ensure_allowed_write_path(path: Path) -> None:
    resolved = path.resolve()
    for directory in ALLOWED_WRITE_DIRS:
        try:
            resolved.relative_to(directory.resolve())
            return
        except ValueError:
            continue
    raise BoardBriefingError(f"refusing to write outside allowed directories: {path}")


def write_output(path: Path, content: str) -> None:
    ensure_allowed_write_path(path)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def load_text(path: Path, label: str) -> str:
    if not path.exists():
        raise BoardBriefingError(f"{label} not found: {path}")
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise BoardBriefingError(f"{label} is empty: {path}")
    return content


def load_json(path: Path, label: str) -> dict:
    raw = load_text(path, label)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BoardBriefingError(f"invalid JSON in {label}: {path}") from exc
    if not isinstance(payload, dict):
        raise BoardBriefingError(f"{label} must be a JSON object: {path}")
    return payload


def relative(path: Path) -> str:
    return path.relative_to(ROOT_DIR).as_posix()


def require_section(content: str, heading: str) -> None:
    if heading not in content:
        raise BoardBriefingError(f"operating package missing required section: {heading}")


def assert_derived_only_inputs() -> None:
    if OPERATING_DECISION_PACKAGE_PATH.name != "OPERATING_DECISION_PACKAGE.md":
        raise BoardBriefingError("unexpected operating decision package path")
    if DECISION_TRACE_PATH.name != "decision_package_trace.json":
        raise BoardBriefingError("unexpected decision trace path")


def extract_line_after_heading(content: str, heading: str) -> str:
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == heading:
            for candidate in lines[index + 1 :]:
                stripped = candidate.strip()
                if stripped:
                    return stripped
            break
    raise BoardBriefingError(f"content missing value after heading: {heading}")


def extract_bullets(content: str, heading: str) -> list[str]:
    section_start = content.find(heading)
    if section_start == -1:
        raise BoardBriefingError(f"heading not found: {heading}")
    section = content[section_start:].split("\n## ", 1)[0]
    bullets = [line.strip()[2:] for line in section.splitlines() if line.strip().startswith("- ")]
    if not bullets:
        raise BoardBriefingError(f"no bullets found under heading: {heading}")
    return bullets


def extract_labeled_bullet_value(content: str, label: str) -> str:
    pattern = re.compile(rf"^- \*\*{re.escape(label)}\*\*: (.+)$", re.MULTILINE)
    match = pattern.search(content)
    if not match:
        raise BoardBriefingError(f"missing required labeled bullet in operating package: {label}")
    return match.group(1).strip()


def extract_first_risk_summary(content: str) -> str:
    section_start = content.find("## 主要风险")
    if section_start == -1:
        raise BoardBriefingError("heading not found: ## 主要风险")
    section = content[section_start:].split("\n## ", 1)[0]
    return extract_labeled_bullet_value(section, "Summary")


def parse_governance_section(content: str, heading: str) -> list[str]:
    if heading not in content:
        raise BoardBriefingError(f"governance status missing required section: {heading}")
    section = content.split(heading, 1)[1].split("\n## ", 1)[0]
    return [line.strip()[2:] for line in section.splitlines() if line.strip().startswith("- ") and line.strip() != "- None"]


def select_governance_signal(governance_content: str) -> str:
    blocked_items = parse_governance_section(governance_content, "## Active Blocks")
    if blocked_items:
        return blocked_items[0]
    pending_items = parse_governance_section(governance_content, "## Pending Approvals")
    if pending_items:
        return pending_items[0]
    overrides = parse_governance_section(governance_content, "## Recent Overrides")
    if overrides:
        return overrides[0]
    return "No current governance blockers or pending approvals."


def build_finance_signal(ledger_payload: dict) -> str:
    treasury = ledger_payload.get("treasury", "unknown")
    maturity = ledger_payload.get("maturity_level", "unknown")
    status = ledger_payload.get("status", "unknown")
    return f"Treasury={treasury}; maturity={maturity}; status={status}."


def history_output_path(date_value: str) -> Path:
    return BOARD_HISTORY_DIR / BOARD_BRIEFING_HISTORY_TEMPLATE.format(date=date_value)


def render_board_briefing(
    date_value: str,
    operating_package: str,
    trace_content: str,
    governance_content: str,
    ledger_payload: dict,
) -> str:
    require_section(operating_package, "## Overall Conclusion / 一句话总判断")
    require_section(operating_package, "## Top 3 Ranked Opportunities")
    require_section(operating_package, "## 主要风险")
    require_section(operating_package, "## 推荐下一步")
    if '"judgment_links"' not in trace_content:
        raise BoardBriefingError("decision trace missing judgment_links")

    conclusion = extract_line_after_heading(operating_package, "## Overall Conclusion / 一句话总判断")
    governance_signal = select_governance_signal(governance_content)
    risk_signal = extract_first_risk_summary(operating_package)
    finance_signal = build_finance_signal(ledger_payload)
    action_bullets = extract_bullets(operating_package, "## 推荐下一步")

    return (
        f"# Board Briefing - {date_value}\n"
        f"- **Derived From**: `{relative(OPERATING_DECISION_PACKAGE_PATH)}`\n"
        f"- **Source Trace**: `{relative(DECISION_TRACE_PATH)}`\n"
        f"- **Conclusion**: {conclusion}\n\n"
        f"## Governance Signal\n"
        f"- {governance_signal}\n\n"
        f"## Risk Signal\n"
        f"- {risk_signal}\n\n"
        f"## Finance Signal\n"
        f"- {finance_signal}\n\n"
        f"## Required Attention\n"
        f"- {action_bullets[0]}\n"
    )


def main() -> int:
    args = parse_args()
    try:
        assert_derived_only_inputs()
        date_value = args.date or today_iso()
        operating_package = load_text(OPERATING_DECISION_PACKAGE_PATH, "operating decision package")
        trace_content = load_text(DECISION_TRACE_PATH, "decision trace")
        governance_content = load_text(GOVERNANCE_STATUS_PATH, "governance status")
        ledger_payload = load_json(LEDGER_PATH, "ledger")
        latest_output = render_board_briefing(date_value, operating_package, trace_content, governance_content, ledger_payload)
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
        print(f"Wrote {relative(BOARD_BRIEFING_PATH)}")
        print(f"Wrote {relative(history_path)}")
        return 0
    except BoardBriefingError as exc:
        print(f"board briefing error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
