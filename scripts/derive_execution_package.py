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
GOVERNANCE_DIR = SHARED_DIR / "governance"
OPERATING_DECISION_PACKAGE_PATH = DECISION_PACKAGES_DIR / "OPERATING_DECISION_PACKAGE.md"
DECISION_TRACE_PATH = TRACE_DIR / "decision_package_trace.json"
GOVERNANCE_STATUS_PATH = GOVERNANCE_DIR / "GOVERNANCE_STATUS.md"
EXECUTION_PACKAGE_PATH = EXECUTION_PACKAGES_DIR / "EXECUTION_PACKAGE.md"
EXECUTION_HISTORY_TEMPLATE = "{date}-execution-package.md"
ALLOWED_WRITE_DIRS = (
    EXECUTION_PACKAGES_DIR,
    EXECUTION_HISTORY_DIR,
)
BANNED_SCOPE_BOUNDARY_LINES = (
    "No task board behavior or work queue expansion.",
    "No approval workflow detail or routing state machine.",
    "No backlog dump or open-ended brainstorm capture.",
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


def extract_risk_items(content: str) -> list[dict[str, str]]:
    section_start = content.find("## 主要风险")
    if section_start == -1:
        raise ExecutionPackageError("heading not found: ## 主要风险")
    section = content[section_start:].split("\n## ", 1)[0]
    chunks = [chunk.strip() for chunk in section.split("### ") if chunk.strip()]
    risk_items: list[dict[str, str]] = []
    for chunk in chunks:
        lines = chunk.splitlines()
        title = lines[0].strip()
        summary = ""
        judgment_id = ""
        for line in lines[1:]:
            if line.startswith("- **Judgment ID**:"):
                judgment_id = line.split(":", 1)[1].strip()
            if line.startswith("- **Summary**:"):
                summary = line.split(":", 1)[1].strip()
        if title and summary:
            risk_items.append({"title": title, "summary": summary, "judgment_id": judgment_id})
    if not risk_items:
        raise ExecutionPackageError("risk summaries not found in operating package")
    return risk_items[:3]


def extract_bullets(content: str, heading: str) -> list[str]:
    section_start = content.find(heading)
    if section_start == -1:
        raise ExecutionPackageError(f"heading not found: {heading}")
    section = content[section_start:].split("\n## ", 1)[0]
    bullets = [line.strip()[2:] for line in section.splitlines() if line.strip().startswith("- ")]
    if not bullets:
        raise ExecutionPackageError(f"no bullet found under heading: {heading}")
    return bullets


def parse_governance_section(content: str, heading: str) -> list[str]:
    if heading not in content:
        raise ExecutionPackageError(f"governance status missing required section: {heading}")
    section = content.split(heading, 1)[1].split("\n## ", 1)[0]
    return [line.strip()[2:] for line in section.splitlines() if line.strip().startswith("- ") and line.strip() != "- None"]


def derive_readiness_status(governance_content: str) -> str:
    blocked_items = parse_governance_section(governance_content, "## Active Blocks")
    if blocked_items:
        return "blocked"
    pending_items = parse_governance_section(governance_content, "## Pending Approvals")
    if pending_items:
        return "needs-input"
    return "ready"


def history_output_path(date_value: str) -> Path:
    return EXECUTION_HISTORY_DIR / EXECUTION_HISTORY_TEMPLATE.format(date=date_value)


def render_execution_package(date_value: str, operating_package: str, trace_content: str, governance_content: str) -> str:
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
    risks = extract_risk_items(operating_package)
    actions = extract_bullets(operating_package, "## 推荐下一步")[:3]
    readiness_status = derive_readiness_status(governance_content)
    dependency_lines = [
        f"- Operating decision anchor: `{relative(OPERATING_DECISION_PACKAGE_PATH)}`",
        f"- Source trace: `{relative(DECISION_TRACE_PATH)}`",
        f"- Governance readiness overlay: `{relative(GOVERNANCE_STATUS_PATH)}`",
    ]
    key_risk_lines = [
        f"- Risk {index}: {risk['summary']}"
        for index, risk in enumerate(risks, start=1)
    ]
    acceptance_lines = [
        f"- Risk {index} gate: Confirm the handoff stays narrow enough to address '{risk['title']}' before moving beyond founder/operator validation."
        for index, risk in enumerate(risks, start=1)
    ]
    first_action_lines = [f"- {action}" for action in actions]

    return (
        f"# Execution Package - {date_value}\n"
        f"- **Derived From**: `{relative(OPERATING_DECISION_PACKAGE_PATH)}`\n"
        f"- **Source Trace**: `{relative(DECISION_TRACE_PATH)}`\n"
        f"- **Owner**: ceo\n"
        f"- **Primary Role**: ceo\n"
        f"- **Handoff Target**: founder/operator\n"
        f"- **Readiness Status**: {readiness_status}\n\n"
        f"## Goal\n"
        f"- {goal}\n\n"
        f"## Scope Boundary\n"
        f"- {BANNED_SCOPE_BOUNDARY_LINES[0]}\n"
        f"- {BANNED_SCOPE_BOUNDARY_LINES[1]}\n"
        f"- {BANNED_SCOPE_BOUNDARY_LINES[2]}\n\n"
        f"## Target User\n"
        f"- {target_user}\n\n"
        f"## MVP Framing\n"
        f"- {mvp_framing}\n"
        f"- Primary focus remains {top_row['idea_id']} until founder/operator validation clears expansion.\n\n"
        f"## Dependencies\n"
        + "\n".join(dependency_lines)
        + "\n\n## Key Risks\n"
        + "\n".join(key_risk_lines)
        + "\n\n## Acceptance Gate\n"
        + "\n".join(acceptance_lines)
        + "\n\n## Recommended First Actions\n"
        + "\n".join(first_action_lines)
        + "\n\n## Handoff Target\n"
        + "- Current handoff is for the founder/operator to pick up immediately.\n"
        + "- Stable ownership metadata keeps the structure reusable for later team intake without adding workflow machinery.\n"
    )


def main() -> int:
    args = parse_args()
    try:
        assert_derived_only_inputs()
        date_value = args.date or today_iso()
        operating_package = load_text(OPERATING_DECISION_PACKAGE_PATH, "operating decision package")
        trace_content = load_text(DECISION_TRACE_PATH, "decision trace")
        governance_content = load_text(GOVERNANCE_STATUS_PATH, "governance status")
        latest_output = render_execution_package(date_value, operating_package, trace_content, governance_content)
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
