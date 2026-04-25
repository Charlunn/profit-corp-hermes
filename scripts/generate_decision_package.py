#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
SHARED_DIR = ROOT_DIR / "assets" / "shared"
TRIAGE_PATH = SHARED_DIR / "external_intelligence" / "triage" / "prioritized_signals.json"
PAIN_POINTS_PATH = SHARED_DIR / "PAIN_POINTS.md"
MARKET_PLAN_PATH = SHARED_DIR / "MARKET_PLAN.md"
TECH_SPEC_PATH = SHARED_DIR / "TECH_SPEC.md"
CEO_RANKING_PATH = SHARED_DIR / "CEO_RANKING.md"
DECISION_PACKAGES_DIR = SHARED_DIR / "decision_packages"
DECISION_HISTORY_DIR = DECISION_PACKAGES_DIR / "history"
TRACE_DIR = SHARED_DIR / "trace"
OPERATING_DECISION_PACKAGE_PATH = DECISION_PACKAGES_DIR / "OPERATING_DECISION_PACKAGE.md"
OPERATING_DECISION_HISTORY_TEMPLATE = "{date}-operating-decision-package.md"
DECISION_TRACE_TEMPLATE_PATH = TRACE_DIR / "decision_package_trace.template.json"
ALLOWED_WRITE_DIRS = (
    DECISION_PACKAGES_DIR,
    DECISION_HISTORY_DIR,
    TRACE_DIR,
)


class DecisionPackageError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the operating decision package skeleton.")
    parser.add_argument("--date", default="", help="Override the report date (YYYY-MM-DD).")
    parser.add_argument("--dry-run", action="store_true", help="Render output contract details without writing files.")
    return parser.parse_args()


def today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def ensure_dirs() -> None:
    DECISION_PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    DECISION_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)


def write_output(path: Path, content: str) -> None:
    resolved = path.resolve()
    if not any(parent.resolve() == resolved.parent for parent in ALLOWED_WRITE_DIRS):
        raise DecisionPackageError(f"refusing to write outside allowed directories: {path}")
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def load_prioritized(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise DecisionPackageError(f"prioritized signal file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DecisionPackageError(f"invalid prioritized signal JSON: {path}") from exc
    prioritized = payload.get("prioritized_signals")
    if not isinstance(prioritized, list) or not prioritized:
        raise DecisionPackageError("prioritized_signals must be a non-empty list")
    for index, record in enumerate(prioritized, start=1):
        if not isinstance(record, dict):
            raise DecisionPackageError(f"prioritized_signals[{index}] must be an object")
        missing = [key for key in ("idea_id", "title", "problem_summary", "score_components", "evidence_links") if key not in record]
        if missing:
            raise DecisionPackageError(f"prioritized_signals[{index}] missing fields: {', '.join(missing)}")
    return prioritized


def load_markdown(path: Path, label: str) -> str:
    if not path.exists():
        raise DecisionPackageError(f"{label} file not found: {path}")
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise DecisionPackageError(f"{label} file is empty: {path}")
    return content


def history_output_path(date_value: str) -> Path:
    return DECISION_HISTORY_DIR / OPERATING_DECISION_HISTORY_TEMPLATE.format(date=date_value)


def render_operating_package(date_value: str) -> str:
    return (
        f"# Operating Decision Package - {date_value}\n\n"
        "## 一句话总判断\n"
        "{{one_line_operator_decision}}\n\n"
        "## Top 3 Opportunities\n"
        "| Rank | idea_id | Opportunity | Why now | Evidence signal | Recommended motion |\n"
        "|---|---|---|---|---|---|\n"
        "| 1 | {{idea_id_1}} | {{title_1}} | {{why_now_1}} | {{signal_1}} | {{motion_1}} |\n"
        "| 2 | {{idea_id_2}} | {{title_2}} | {{why_now_2}} | {{signal_2}} | {{motion_2}} |\n"
        "| 3 | {{idea_id_3}} | {{title_3}} | {{why_now_3}} | {{signal_3}} | {{motion_3}} |\n\n"
        "## Opportunities / Risks / Next Actions\n"
        "- Derived from prioritized shortlist plus role outputs with layered evidence summaries.\n"
    )


def render_trace(date_value: str) -> str:
    payload = {
        "generated_at": f"{date_value}T00:00:00Z",
        "run_id": "{{run_id}}",
        "operating_package_path": OPERATING_DECISION_PACKAGE_PATH.relative_to(ROOT_DIR).as_posix(),
        "derived_from": {
            "prioritized_shortlist_path": TRIAGE_PATH.relative_to(ROOT_DIR).as_posix(),
            "role_outputs": [
                PAIN_POINTS_PATH.relative_to(ROOT_DIR).as_posix(),
                MARKET_PLAN_PATH.relative_to(ROOT_DIR).as_posix(),
                TECH_SPEC_PATH.relative_to(ROOT_DIR).as_posix(),
                CEO_RANKING_PATH.relative_to(ROOT_DIR).as_posix(),
            ],
        },
        "judgment_links": [
            {
                "judgment_id": "{{judgment_id}}",
                "idea_id": "{{idea_id}}",
                "upstream_paths": [
                    f"{TRIAGE_PATH.relative_to(ROOT_DIR).as_posix()}#{{idea_id}}"
                ],
                "role_artifacts": [
                    PAIN_POINTS_PATH.relative_to(ROOT_DIR).as_posix(),
                    MARKET_PLAN_PATH.relative_to(ROOT_DIR).as_posix(),
                    TECH_SPEC_PATH.relative_to(ROOT_DIR).as_posix(),
                    CEO_RANKING_PATH.relative_to(ROOT_DIR).as_posix(),
                ],
            }
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


def main() -> int:
    args = parse_args()
    try:
        date_value = args.date or today_iso()
        load_prioritized(TRIAGE_PATH)
        load_markdown(PAIN_POINTS_PATH, "pain points")
        load_markdown(MARKET_PLAN_PATH, "market plan")
        load_markdown(TECH_SPEC_PATH, "tech spec")
        load_markdown(CEO_RANKING_PATH, "ceo ranking")
        latest_output = render_operating_package(date_value)
        history_path = history_output_path(date_value)
        trace_output = render_trace(date_value)
        if args.dry_run:
            print("=== OPERATING_DECISION_PACKAGE.md ===")
            print(latest_output)
            print(f"=== history/{history_path.name} ===")
            print(latest_output)
            print("=== decision_package_trace.json ===")
            print(trace_output)
            return 0
        ensure_dirs()
        write_output(OPERATING_DECISION_PACKAGE_PATH, latest_output)
        write_output(history_path, latest_output)
        write_output(DECISION_TRACE_TEMPLATE_PATH, trace_output)
        print(f"Wrote {OPERATING_DECISION_PACKAGE_PATH.relative_to(ROOT_DIR)}")
        print(f"Wrote {history_path.relative_to(ROOT_DIR)}")
        print(f"Wrote {DECISION_TRACE_TEMPLATE_PATH.relative_to(ROOT_DIR)}")
        return 0
    except DecisionPackageError as exc:
        print(f"decision package error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
