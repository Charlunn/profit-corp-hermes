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


class RoleHandoffError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate Scout, CMO, Architect, and CEO handoff artifacts.")
    parser.add_argument("--limit", type=int, default=3, help="Maximum number of prioritized leads to include.")
    parser.add_argument("--date", default="", help="Override the report date (YYYY-MM-DD).")
    parser.add_argument("--dry-run", action="store_true", help="Render outputs to stdout without writing files.")
    return parser.parse_args()


def today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def load_prioritized(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise RoleHandoffError(f"prioritized signal file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RoleHandoffError(f"invalid prioritized signal JSON: {path}") from exc
    prioritized = payload.get("prioritized_signals")
    if not isinstance(prioritized, list) or not prioritized:
        raise RoleHandoffError("prioritized_signals must be a non-empty list")
    for index, record in enumerate(prioritized, start=1):
        if not isinstance(record, dict):
            raise RoleHandoffError(f"prioritized_signals[{index}] must be an object")
        missing = [key for key in ("idea_id", "title", "problem_summary", "evidence_links", "score_components", "estimated_mvp_hours", "total_score") if key not in record]
        if missing:
            raise RoleHandoffError(f"prioritized_signals[{index}] missing fields: {', '.join(missing)}")
    return prioritized


def fmt_score(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def render_pain_points(date_value: str, leads: list[dict[str, Any]], source_path: Path) -> str:
    lines = [f"# Daily Intelligence Report - {date_value}", "## Leads (Scoring-Ready)"]
    for lead in leads:
        components = lead["score_components"]
        lines.extend(
            [
                f"### Lead: {lead['title']}",
                f"- **Idea ID**: {lead['idea_id']}",
                f"- **Problem**: {lead['problem_summary']}",
                f"- **Target User**: {lead.get('target_user', 'Developers and technical operators')}",
                f"- **Evidence Links**: {', '.join(lead['evidence_links'])}",
                f"- **Latest Evidence Age (hours)**: {fmt_score(lead.get('latest_evidence_age_hours', 0))}",
                f"- **Urgency Pain (0-10)**: {fmt_score(components.get('urgency_pain', 0))}",
                f"- **Estimated MVP Hours**: {lead['estimated_mvp_hours']}",
                f"- **Monetization Signal (0-10)**: {fmt_score(components.get('monetization_signal', 0))}",
                f"- **Competition Signal (0-10)**: {fmt_score(components.get('competition_signal', 0))}",
                f"- **Confidence (0-10)**: {fmt_score(components.get('confidence', 0))}",
                f"- **Notes**: {lead.get('notes', '')} Shared shortlist source: `{source_path.as_posix()}`.",
                "",
            ]
        )
    return "\n".join(lines).rstrip() + "\n"


def render_market_plan(top: dict[str, Any], source_path: Path) -> str:
    components = top["score_components"]
    return (
        f"# Market Strategy: {top['title']}\n"
        f"- **Core USP**: Turn the pain cluster behind {top['idea_id']} into a focused operator workflow before competitors generalize it.\n"
        f"- **Pricing**: Start with a solo-operator plan around the urgency and MVP scope signaled by the shortlist; validate willingness to pay before adding team features.\n"
        f"- **Distribution**: Revisit the same communities and source URLs already represented in the prioritized shortlist, then expand into adjacent operator/developer channels.\n"
        f"- **Risk Level**: medium\n"
        f"- **Shared Shortlist Source**: `{source_path.as_posix()}`\n"
        f"- **Chosen Idea ID**: {top['idea_id']}\n"
        f"- **Evidence Strength (0-10)**: {fmt_score(components.get('evidence_strength', 0))}\n"
        f"- **Recency (0-10)**: {fmt_score(components.get('recency', 0))}\n"
    )


def render_tech_spec(top: dict[str, Any], source_path: Path) -> str:
    return (
        f"# Technical Specification: {top['title']}\n"
        f"- **Stack**: Hermes prompts + Python triage/read-model pipeline + markdown shared-state artifacts\n"
        f"- **File Tree**:\n"
        f"  ```\n"
        f"  scripts/triage_external_signals.py\n"
        f"  scripts/generate_role_handoffs.py\n"
        f"  scripts/run_signal_analysis_loop.sh\n"
        f"  assets/shared/external_intelligence/triage/prioritized_signals.json\n"
        f"  assets/shared/PAIN_POINTS.md\n"
        f"  assets/shared/MARKET_PLAN.md\n"
        f"  assets/shared/TECH_SPEC.md\n"
        f"  assets/shared/CEO_RANKING.md\n"
        f"  ```\n"
        f"- **MVP Features**: deterministic triage, shared shortlist generation, role-specific markdown handoffs, CEO ranking over the same shortlist\n"
        f"- **Build Time**: {top['estimated_mvp_hours']}\n"
        f"- **Shared Shortlist Source**: `{source_path.as_posix()}`\n"
        f"- **Chosen Idea ID**: {top['idea_id']}\n"
    )


def render_ceo_ranking(leads: list[dict[str, Any]], source_path: Path) -> str:
    header = [
        "## Top 3 Ranked Micro-SaaS Ideas (last 48h)",
        "| Rank | idea_id | Idea | TotalScore/100 | Urgency | Feasibility | Monetization | Evidence | Recency | Competition | MVP Hours |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    rows = []
    for lead in leads[:3]:
        c = lead["score_components"]
        feasibility = max(1.0, min(10.0, 10 - (lead["estimated_mvp_hours"] / 8)))
        rows.append(
            f"| {lead['rank']} | {lead['idea_id']} | {lead['title']} | {fmt_score(lead['total_score'])} | {fmt_score(c.get('urgency_pain', 0))} | {fmt_score(feasibility)} | {fmt_score(c.get('monetization_signal', 0))} | {fmt_score(c.get('evidence_strength', 0))} | {fmt_score(c.get('recency', 0))} | {fmt_score(c.get('competition_signal', 0))} | {lead['estimated_mvp_hours']} |"
        )
    top = leads[0]
    recommendation = (
        f"**Recommended**: {top['idea_id']} — highest shared-shortlist score with fresh evidence and the clearest bridge from pain signal to MVP.\n\n"
        f"Shared shortlist source: `{source_path.as_posix()}`\n"
    )
    return "\n".join(header + rows + ["", recommendation])


def write_output(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        date_value = args.date or today_iso()
        prioritized = load_prioritized(TRIAGE_PATH)
        leads = prioritized[: max(1, args.limit)]
        pain_points = render_pain_points(date_value, leads, TRIAGE_PATH.relative_to(ROOT_DIR))
        market_plan = render_market_plan(leads[0], TRIAGE_PATH.relative_to(ROOT_DIR))
        tech_spec = render_tech_spec(leads[0], TRIAGE_PATH.relative_to(ROOT_DIR))
        ceo_ranking = render_ceo_ranking(leads, TRIAGE_PATH.relative_to(ROOT_DIR))
        if args.dry_run:
            print("=== PAIN_POINTS.md ===")
            print(pain_points)
            print("=== MARKET_PLAN.md ===")
            print(market_plan)
            print("=== TECH_SPEC.md ===")
            print(tech_spec)
            print("=== CEO_RANKING.md ===")
            print(ceo_ranking)
            return 0
        write_output(PAIN_POINTS_PATH, pain_points)
        write_output(MARKET_PLAN_PATH, market_plan)
        write_output(TECH_SPEC_PATH, tech_spec)
        write_output(CEO_RANKING_PATH, ceo_ranking)
        print(f"Wrote {PAIN_POINTS_PATH.relative_to(ROOT_DIR)}")
        print(f"Wrote {MARKET_PLAN_PATH.relative_to(ROOT_DIR)}")
        print(f"Wrote {TECH_SPEC_PATH.relative_to(ROOT_DIR)}")
        print(f"Wrote {CEO_RANKING_PATH.relative_to(ROOT_DIR)}")
        return 0
    except RoleHandoffError as exc:
        print(f"role handoff error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
