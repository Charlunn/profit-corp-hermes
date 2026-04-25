#!/usr/bin/env python3
import argparse
import json
import re
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SHARED_DIR = ROOT_DIR / "assets" / "shared"
DECISION_PACKAGES_DIR = SHARED_DIR / "decision_packages"
TRACE_DIR = SHARED_DIR / "trace"
GOVERNANCE_DIR = SHARED_DIR / "governance"
EXTERNAL_INTELLIGENCE_DIR = SHARED_DIR / "external_intelligence"
EXECUTION_PACKAGES_DIR = SHARED_DIR / "execution_packages"
BOARD_BRIEFINGS_DIR = SHARED_DIR / "board_briefings"
VISIBILITY_DIR = SHARED_DIR / "visibility"
VISIBILITY_HISTORY_DIR = VISIBILITY_DIR / "history"
OPERATING_DECISION_PACKAGE_PATH = DECISION_PACKAGES_DIR / "OPERATING_DECISION_PACKAGE.md"
DECISION_TRACE_PATH = TRACE_DIR / "decision_package_trace.json"
GOVERNANCE_STATUS_PATH = GOVERNANCE_DIR / "GOVERNANCE_STATUS.md"
LATEST_SUMMARY_PATH = EXTERNAL_INTELLIGENCE_DIR / "LATEST_SUMMARY.md"
EXECUTION_PACKAGE_PATH = EXECUTION_PACKAGES_DIR / "EXECUTION_PACKAGE.md"
BOARD_BRIEFING_PATH = BOARD_BRIEFINGS_DIR / "BOARD_BRIEFING.md"
OPERATING_VISIBILITY_PATH = VISIBILITY_DIR / "OPERATING_VISIBILITY.md"
VISIBILITY_HISTORY_TEMPLATE = "{date}-operating-visibility.md"
ALLOWED_WRITE_DIRS = (
    VISIBILITY_DIR,
    VISIBILITY_HISTORY_DIR,
)
EXPECTED_DAILY_CYCLE = timedelta(hours=24)


class OperatingVisibilityError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the operating visibility surface from trusted artifacts.")
    parser.add_argument("--date", default="", help="Override report date (YYYY-MM-DD).")
    parser.add_argument("--dry-run", action="store_true", help="Render output without writing files.")
    parser.add_argument("--now", default="", help="Override current UTC timestamp (ISO8601).")
    parser.add_argument("--operating-package-path", default=str(OPERATING_DECISION_PACKAGE_PATH))
    parser.add_argument("--trace-path", default=str(DECISION_TRACE_PATH))
    parser.add_argument("--governance-status-path", default=str(GOVERNANCE_STATUS_PATH))
    parser.add_argument("--latest-summary-path", default=str(LATEST_SUMMARY_PATH))
    parser.add_argument("--execution-package-path", default=str(EXECUTION_PACKAGE_PATH))
    parser.add_argument("--board-briefing-path", default=str(BOARD_BRIEFING_PATH))
    parser.add_argument("--output-path", default=str(OPERATING_VISIBILITY_PATH))
    parser.add_argument("--history-path", default="")
    return parser.parse_args()


def utc_now(now_override: str) -> datetime:
    if not now_override:
        return datetime.now(timezone.utc)
    return parse_iso_datetime(now_override)


def parse_iso_datetime(value: str) -> datetime:
    normalized = value.strip().replace("Z", "+00:00")
    parsed = datetime.fromisoformat(normalized)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def today_iso(now_override: str) -> str:
    return utc_now(now_override).date().isoformat()


def ensure_dirs() -> None:
    VISIBILITY_DIR.mkdir(parents=True, exist_ok=True)
    VISIBILITY_HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def ensure_allowed_write_path(path: Path) -> None:
    resolved = path.resolve()
    for directory in ALLOWED_WRITE_DIRS:
        try:
            resolved.relative_to(directory.resolve())
            return
        except ValueError:
            continue
    raise OperatingVisibilityError(f"refusing to write outside allowed directories: {path}")


def write_output(path: Path, content: str) -> None:
    ensure_allowed_write_path(path)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def load_text(path: Path, label: str) -> str:
    if not path.exists():
        raise OperatingVisibilityError(f"{label} not found: {path}")
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise OperatingVisibilityError(f"{label} is empty: {path}")
    return content


def load_json(path: Path, label: str) -> dict:
    raw = load_text(path, label)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise OperatingVisibilityError(f"invalid JSON in {label}: {path}") from exc
    if not isinstance(payload, dict):
        raise OperatingVisibilityError(f"{label} must be a JSON object: {path}")
    return payload


def relative(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT_DIR.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


def require_section(content: str, heading: str) -> None:
    if heading not in content:
        raise OperatingVisibilityError(f"operating package missing required section: {heading}")


def require_heading(content: str, heading: str, label: str) -> None:
    if heading not in content:
        raise OperatingVisibilityError(f"{label} missing required section: {heading}")


def extract_line_after_heading(content: str, heading: str) -> str:
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == heading:
            for candidate in lines[index + 1 :]:
                stripped = candidate.strip()
                if stripped:
                    return stripped
            break
    raise OperatingVisibilityError(f"content missing value after heading: {heading}")


def extract_table_rows(content: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in content.splitlines():
        if line.startswith("| ") and not line.startswith("| Rank ") and not line.startswith("|---"):
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) >= 6:
                rows.append(
                    {
                        "rank": parts[0],
                        "idea_id": parts[1],
                        "title": parts[2],
                        "why_now": parts[3],
                        "signal": parts[4],
                        "motion": parts[5],
                    }
                )
    if not rows:
        raise OperatingVisibilityError("Top 3 rows not found in operating package")
    return rows


def extract_bullets(content: str, heading: str) -> list[str]:
    start = content.find(heading)
    if start == -1:
        raise OperatingVisibilityError(f"heading not found: {heading}")
    section = content[start:].split("\n## ", 1)[0]
    bullets = [line.strip()[2:] for line in section.splitlines() if line.strip().startswith("- ")]
    if not bullets:
        raise OperatingVisibilityError(f"no bullets found under heading: {heading}")
    return bullets


def extract_labeled_value(content: str, label: str) -> str:
    pattern = re.compile(rf"^- \*\*{re.escape(label)}\*\*: (.+)$", re.MULTILINE)
    match = pattern.search(content)
    if not match:
        raise OperatingVisibilityError(f"missing required labeled bullet: {label}")
    return match.group(1).strip()


def extract_risk_items(content: str) -> list[str]:
    require_section(content, "## 主要风险")
    section = content.split("## 主要风险", 1)[1]
    section = section.split("\n## ", 1)[0]
    chunks = [chunk.strip() for chunk in section.split("### ") if chunk.strip()]
    risks: list[str] = []
    for chunk in chunks:
        lines = chunk.splitlines()
        title = lines[0].strip()
        summary = ""
        for line in lines[1:]:
            if line.startswith("- **Summary**:"):
                summary = line.split(":", 1)[1].strip()
                break
        if title and summary:
            risks.append(f"{title} — {summary}")
    if not risks:
        raise OperatingVisibilityError("risk summaries not found in operating package")
    return risks


def parse_governance_section(content: str, heading: str) -> list[str]:
    require_heading(content, heading, "governance status")
    section = content.split(heading, 1)[1].split("\n## ", 1)[0]
    items = [line.strip()[2:] for line in section.splitlines() if line.strip().startswith("- ")]
    return [item for item in items if item != "None"]


def parse_latest_summary_metadata(content: str) -> dict[str, str]:
    require_heading(content, "## Run Metadata", "latest summary")
    section = content.split("## Run Metadata", 1)[1].split("\n## ", 1)[0]
    metadata: dict[str, str] = {}
    for line in section.splitlines():
        line = line.strip()
        if not line.startswith("- **"):
            continue
        match = re.match(r"- \*\*(.+?)\*\*: (.+)", line)
        if match:
            metadata[match.group(1)] = match.group(2).strip()
    required = ["completed_at", "failed_source_count", "failed_sources"]
    missing = [key for key in required if key not in metadata]
    if missing:
        raise OperatingVisibilityError(f"latest summary missing metadata: {', '.join(missing)}")
    return metadata


def normalize_status(value: str) -> str:
    return value.upper().replace("-", " ")


def history_output_path(date_value: str, override: str) -> Path:
    if override:
        return Path(override)
    return VISIBILITY_HISTORY_DIR / VISIBILITY_HISTORY_TEMPLATE.format(date=date_value)


def build_status_and_alerts(governance_content: str, latest_metadata: dict[str, str], now: datetime) -> tuple[str, list[str], list[str]]:
    pending_items = parse_governance_section(governance_content, "## Pending Approvals")
    blocked_items = parse_governance_section(governance_content, "## Active Blocks")
    override_items = parse_governance_section(governance_content, "## Recent Overrides")

    completed_at = parse_iso_datetime(latest_metadata["completed_at"])
    stale = now - completed_at > EXPECTED_DAILY_CYCLE
    failed_source_count = int(latest_metadata["failed_source_count"])
    failed_sources = latest_metadata["failed_sources"]

    alerts: list[str] = []
    action_items: list[str] = []

    for item in blocked_items:
        alerts.append(f"Blocked governance action: {item} — source: `{relative(GOVERNANCE_STATUS_PATH)}`")
        action_items.append(f"- Resolve blocked governance action before protected writes proceed — source: `{relative(GOVERNANCE_STATUS_PATH)}`")

    for item in pending_items:
        alerts.append(f"Pending governance approval: {item} — source: `{relative(GOVERNANCE_STATUS_PATH)}`")
        if blocked_items:
            action_items.append(f"- Review pending governance approval tied to current block — source: `{relative(GOVERNANCE_STATUS_PATH)}`")

    if failed_source_count > 0 or failed_sources.lower() != "none":
        alerts.append(
            f"Failed source collection detected: failed_source_count={failed_source_count}, failed_sources={failed_sources} — source: `{relative(LATEST_SUMMARY_PATH)}`"
        )
        action_items.append(f"- Repair failed source collection before trusting the next run — source: `{relative(LATEST_SUMMARY_PATH)}`")

    if stale:
        alerts.append(
            f"Stale external intelligence: completed_at={latest_metadata['completed_at']} is older than one expected daily cycle — source: `{relative(LATEST_SUMMARY_PATH)}`"
        )
        action_items.append(f"- Refresh the daily pipeline because the latest intelligence run is stale — source: `{relative(LATEST_SUMMARY_PATH)}`")

    if blocked_items or failed_source_count > 0 or stale:
        status = "ACTION REQUIRED"
    elif pending_items or override_items:
        status = "WATCH"
    else:
        status = "HEALTHY"

    return status, alerts, action_items


def build_action_list(operating_actions: list[str], governance_actions: list[str]) -> list[str]:
    merged: list[str] = []
    seen: set[str] = set()
    for item in governance_actions + [f"- {action}" if not action.startswith("- ") else action for action in operating_actions]:
        if item in seen:
            continue
        seen.add(item)
        merged.append(item)
        if len(merged) == 3:
            break
    return merged


def render_operating_visibility(
    date_value: str,
    operating_content: str,
    trace_payload: dict,
    governance_content: str,
    latest_summary_content: str,
    execution_path: Path,
    board_path: Path,
    now: datetime,
) -> str:
    require_section(operating_content, "## Overall Conclusion / 一句话总判断")
    require_section(operating_content, "## Top 3 Ranked Opportunities")
    require_section(operating_content, "## 主要风险")
    require_section(operating_content, "## 推荐下一步")
    if "judgment_links" not in trace_payload:
        raise OperatingVisibilityError("decision trace missing judgment_links")

    conclusion = extract_line_after_heading(operating_content, "## Overall Conclusion / 一句话总判断")
    opportunities = extract_table_rows(operating_content)
    risks = extract_risk_items(operating_content)
    operating_actions = extract_bullets(operating_content, "## 推荐下一步")
    latest_metadata = parse_latest_summary_metadata(latest_summary_content)
    status, alerts, governance_actions = build_status_and_alerts(governance_content, latest_metadata, now)
    surfaced_actions = build_action_list(operating_actions, governance_actions)

    if not surfaced_actions:
        raise OperatingVisibilityError("no visibility actions could be derived from trusted artifacts")

    status_line = {
        "HEALTHY": "- HEALTHY — current operating package, governance view, and external-intelligence run are aligned and free of blocking exceptions.",
        "WATCH": "- WATCH — the visibility surface is readable, but pending governance or recent override conditions need attention.",
        "ACTION REQUIRED": "- ACTION REQUIRED — blocked, failed, or stale conditions are preventing a calm healthy operating state.",
    }[status]

    alerts_block = "None." if not alerts else "\n".join(f"- {item}" for item in alerts)
    opportunities_block = "\n".join(
        f"- {row['idea_id']} — {row['why_now']} — evidence: {row['signal']}" for row in opportunities[:3]
    )
    risks_block = "\n".join(f"- {risk}" for risk in risks[:3])
    actions_block = "\n".join(surfaced_actions)

    evidence_backlinks = [
        f"- primary anchor: `{relative(OPERATING_DECISION_PACKAGE_PATH)}`",
        f"- governance overlay: `{relative(GOVERNANCE_STATUS_PATH)}`",
        f"- freshness overlay: `{relative(LATEST_SUMMARY_PATH)}`",
        f"- supporting execution view: `{relative(execution_path)}`",
        f"- supporting board view: `{relative(board_path)}`",
        f"- source trace: `{relative(DECISION_TRACE_PATH)}`",
    ]

    evidence_block = "\n".join(evidence_backlinks)

    return (
        f"# Operating Visibility - {date_value}\n"
        f"- **Primary Anchor**: `{relative(OPERATING_DECISION_PACKAGE_PATH)}`\n"
        f"- **Governance Overlay**: `{relative(GOVERNANCE_STATUS_PATH)}`\n"
        f"- **Freshness Overlay**: `{relative(LATEST_SUMMARY_PATH)}`\n"
        f"- **Supporting Views**: `{relative(execution_path)}`, `{relative(board_path)}`\n"
        f"- **Source Trace**: `{relative(DECISION_TRACE_PATH)}`\n\n"
        f"## Status\n"
        f"{status_line}\n\n"
        f"## Top Alerts\n"
        f"{alerts_block}\n\n"
        f"## Current Situation\n"
        f"- {conclusion}\n\n"
        f"## Top Opportunities\n"
        f"{opportunities_block}\n\n"
        f"## Top Risks\n"
        f"{risks_block}\n\n"
        f"## Top 3 Next Actions\n"
        f"{actions_block}\n\n"
        f"## Evidence Backlinks\n"
        f"{evidence_block}\n"
    )


def main() -> int:
    args = parse_args()
    try:
        operating_path = Path(args.operating_package_path)
        trace_path = Path(args.trace_path)
        governance_path = Path(args.governance_status_path)
        latest_summary_path = Path(args.latest_summary_path)
        execution_path = Path(args.execution_package_path)
        board_path = Path(args.board_briefing_path)
        output_path = Path(args.output_path)
        now = utc_now(args.now)
        date_value = args.date or today_iso(args.now)
        history_path = history_output_path(date_value, args.history_path)

        operating_content = load_text(operating_path, "operating decision package")
        trace_payload = load_json(trace_path, "decision trace")
        governance_content = load_text(governance_path, "governance status")
        latest_summary_content = load_text(latest_summary_path, "latest summary")
        load_text(execution_path, "execution package")
        load_text(board_path, "board briefing")

        output = render_operating_visibility(
            date_value,
            operating_content,
            trace_payload,
            governance_content,
            latest_summary_content,
            execution_path,
            board_path,
            now,
        )

        if args.dry_run:
            print(output, end="")
            return 0

        ensure_dirs()
        write_output(output_path, output)
        write_output(history_path, output)
        print(f"Wrote {relative(output_path)}")
        print(f"Wrote {relative(history_path)}")
        return 0
    except OperatingVisibilityError as exc:
        print(f"operating visibility error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
