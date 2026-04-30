#!/usr/bin/env python3
import argparse
import json
import re
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
DECISION_TRACE_PATH = TRACE_DIR / "decision_package_trace.json"
ALLOWED_WRITE_DIRS = (
    DECISION_PACKAGES_DIR,
    DECISION_HISTORY_DIR,
    TRACE_DIR,
)
ROLE_ARTIFACTS = (
    PAIN_POINTS_PATH,
    MARKET_PLAN_PATH,
    TECH_SPEC_PATH,
    CEO_RANKING_PATH,
)


class DecisionPackageError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate the operating decision package.")
    parser.add_argument("--date", default="", help="Override the report date (YYYY-MM-DD).")
    parser.add_argument("--dry-run", action="store_true", help="Render outputs to stdout without writing files.")
    return parser.parse_args()


def today_iso() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def timestamp_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def build_run_id(date_value: str) -> str:
    return f"decision-package-{date_value.replace('-', '')}"


def ensure_dirs() -> None:
    DECISION_PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    DECISION_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    TRACE_DIR.mkdir(parents=True, exist_ok=True)


def ensure_allowed_write_path(path: Path) -> None:
    resolved = path.resolve()
    for directory in ALLOWED_WRITE_DIRS:
        try:
            resolved.relative_to(directory.resolve())
            return
        except ValueError:
            continue
    raise DecisionPackageError(f"refusing to write outside allowed directories: {path}")


def write_output(path: Path, content: str) -> None:
    ensure_allowed_write_path(path)
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

    validated: list[dict[str, Any]] = []
    required_keys = (
        "idea_id",
        "title",
        "problem_summary",
        "target_user",
        "evidence_links",
        "score_components",
        "estimated_mvp_hours",
        "total_score",
        "rank",
        "generated_from",
    )
    for index, record in enumerate(prioritized, start=1):
        if not isinstance(record, dict):
            raise DecisionPackageError(f"prioritized_signals[{index}] must be an object")
        missing = [key for key in required_keys if key not in record]
        if missing:
            raise DecisionPackageError(f"prioritized_signals[{index}] missing fields: {', '.join(missing)}")
        if not isinstance(record["evidence_links"], list) or not record["evidence_links"]:
            raise DecisionPackageError(f"prioritized_signals[{index}] must include non-empty evidence_links")
        if not isinstance(record["generated_from"], dict):
            raise DecisionPackageError(f"prioritized_signals[{index}] missing generated_from object")
        validated.append(record)

    validated.sort(key=lambda item: (item.get("rank", 999), -float(item.get("total_score", 0))), reverse=False)
    return validated


def load_markdown(path: Path, label: str) -> str:
    if not path.exists():
        raise DecisionPackageError(f"{label} file not found: {path}")
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise DecisionPackageError(f"{label} file is empty: {path}")
    return content


def relative(path: Path) -> str:
    return path.relative_to(ROOT_DIR).as_posix()


def fmt_score(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:.2f}".rstrip("0").rstrip(".")
    return str(value)


def extract_markdown_value(content: str, label: str) -> str:
    pattern = re.compile(rf"^- \*\*{re.escape(label)}\*\*: (.+)$", re.MULTILINE)
    match = pattern.search(content)
    if not match:
        raise DecisionPackageError(f"missing markdown value for {label}")
    return match.group(1).strip()


def extract_recommended_idea_id(ceo_ranking: str) -> str:
    match = re.search(r"\*\*Recommended\*\*:\s*([A-Z0-9-]+)", ceo_ranking)
    if not match:
        raise DecisionPackageError("CEO_RANKING.md missing recommended idea_id")
    return match.group(1)


def summarize_evidence(lead: dict[str, Any]) -> str:
    evidence_count = lead.get("evidence_count", len(lead["evidence_links"]))
    source_ids = lead.get("source_ids") or []
    source_summary = ", ".join(source_ids) if source_ids else "shared discovery sources"
    age_hours = fmt_score(lead.get("latest_evidence_age_hours", 0))
    return f"{evidence_count} 条证据，最近证据距今 {age_hours} 小时，来源集中在 {source_summary}。"


def summarize_competition_window(lead: dict[str, Any]) -> str:
    score_components = lead["score_components"]
    monetization = fmt_score(score_components.get("monetization_signal", 0))
    urgency = fmt_score(score_components.get("urgency_pain", 0))
    return f"Monetization {monetization}/10、Urgency {urgency}/10，适合先做轻量验证再决定是否深入。"


def top3_note(leads: list[dict[str, Any]]) -> str:
    if len(leads) >= 3:
        return "Top 3 ranking is fully populated from the shared shortlist."
    return f"Only {len(leads)} validated opportunities were available in the current shortlist, so this run keeps the Top 3 frame while rendering all validated rows."


def build_overall_conclusion(top: dict[str, Any], recommended_id: str, risk_level: str) -> str:
    build_time = top.get("estimated_mvp_hours", "unknown")
    return (
        f"优先围绕 {recommended_id} 开启下一轮 founder/operator 验证：它仍是今天最强的机会信号，"
        f"但由于当前风险等级为 {risk_level} 且预计 MVP 需要 {build_time} 小时，执行上应先做窄范围验证而不是直接全面投入。"
    )


def build_goal(top: dict[str, Any]) -> str:
    return f"验证 {top['idea_id']} 是否值得作为下一阶段 mini-SaaS 切入点，并确认用户是否愿意为该痛点付费。"


def build_mvp_framing(top: dict[str, Any], tech_spec: str) -> str:
    build_time = extract_markdown_value(tech_spec, "Build Time")
    return f"以 {top['idea_id']} 为核心做一个 {build_time} 小时量级的 markdown-first operator workflow 原型，先验证最痛的检索/反馈闭环。"


def build_opportunities(leads: list[dict[str, Any]]) -> list[dict[str, str]]:
    opportunities: list[dict[str, str]] = []
    for lead in leads[:3]:
        score_components = lead["score_components"]
        opportunities.append(
            {
                "judgment_id": f"opp-{lead['idea_id'].lower()}",
                "idea_id": lead["idea_id"],
                "heading": f"{lead['idea_id']} — {lead['title']}",
                "summary": (
                    f"{lead['problem_summary']} {summarize_evidence(lead)} "
                    f"EvidenceStrength {fmt_score(score_components.get('evidence_strength', 0))}/10。"
                ),
                "why_now": (
                    f"{fmt_score(score_components.get('recency', 0))}/10 recency 与 "
                    f"{fmt_score(score_components.get('evidence_strength', 0))}/10 evidence strength 支撑今天优先评估。"
                ),
                "signal": summarize_evidence(lead),
                "motion": f"先与 {lead.get('target_user', 'operators')} 做 3-5 个高密度访谈，再决定是否进入构建。",
            }
        )
    return opportunities


def build_risks(top: dict[str, Any], market_plan: str, leads: list[dict[str, Any]]) -> list[dict[str, str]]:
    risk_level = extract_markdown_value(market_plan, "Risk Level")
    competition = fmt_score(top["score_components"].get("competition_signal", 0))
    risks = [
        {
            "judgment_id": f"risk-{top['idea_id'].lower()}-scope",
            "idea_id": top["idea_id"],
            "heading": f"{top['idea_id']} 需要先控制验证范围",
            "summary": (
                f"MARKET_PLAN.md 标记风险等级为 {risk_level}，同时该机会预计 MVP 需 {top['estimated_mvp_hours']} 小时，"
                f"说明直接进入完整构建的执行风险偏高。"
            ),
        },
        {
            "judgment_id": f"risk-{top['idea_id'].lower()}-breadth",
            "idea_id": top["idea_id"],
            "heading": "当前 shortlist 覆盖面仍偏窄",
            "summary": (
                f"本次 validated shortlist 仅有 {len(leads)} 个机会，且 Top 1 competition signal 为 {competition}/10，"
                "说明仍需要更多对比验证来确认机会窗口不是短期噪声。"
            ),
        },
    ]
    return risks


def build_next_actions(top: dict[str, Any], opportunities: list[dict[str, str]], risks: list[dict[str, str]]) -> list[dict[str, str]]:
    return [
        {
            "judgment_id": f"action-{top['idea_id'].lower()}-interviews",
            "idea_id": top["idea_id"],
            "action": f"围绕 {top['idea_id']} 组织 3-5 个目标用户验证访谈",
            "reason": opportunities[0]["summary"],
        },
        {
            "judgment_id": f"action-{top['idea_id'].lower()}-prototype",
            "idea_id": top["idea_id"],
            "action": f"定义一个只覆盖核心痛点的 MVP framing，并压缩到单一 workflow 原型",
            "reason": risks[0]["summary"],
        },
    ]


def build_top_rows(leads: list[dict[str, Any]]) -> list[str]:
    rows: list[str] = []
    for lead in leads[:3]:
        rows.append(
            "| {rank} | {idea_id} | {title} | {why_now} | {signal} | {motion} |".format(
                rank=lead["rank"],
                idea_id=lead["idea_id"],
                title=lead["title"],
                why_now=summarize_competition_window(lead),
                signal=summarize_evidence(lead),
                motion=f"Validate {lead['idea_id']} before expanding scope.",
            )
        )
    return rows


def build_operating_package(
    date_value: str,
    generated_at: str,
    run_id: str,
    leads: list[dict[str, Any]],
    target_user: str,
    goal: str,
    mvp_framing: str,
    overall_conclusion: str,
    opportunities: list[dict[str, str]],
    risks: list[dict[str, str]],
    next_actions: list[dict[str, str]],
) -> str:
    top = leads[0]
    top_rows = build_top_rows(leads)
    lines = [
        f"# Operating Decision Package - {date_value}",
        f"- **Generated At**: {generated_at}",
        f"- **Run ID**: {run_id}",
        f"- **Shared Shortlist Source**: `{relative(TRIAGE_PATH)}`",
        f"- **CEO Synthesis Source**: `{relative(CEO_RANKING_PATH)}`",
        "",
        "## Overall Conclusion / 一句话总判断",
        overall_conclusion,
        "",
        "## Top 3 Ranked Opportunities",
        f"- {top3_note(leads)}",
        "| Rank | idea_id | Opportunity | Why now | Evidence signal | Recommended motion |",
        "|---|---|---|---|---|---|",
        *top_rows,
        "",
        "## Operating Framing",
        f"- **Goal**: {goal}",
        f"- **Target User**: {target_user}",
        f"- **MVP Framing**: {mvp_framing}",
        f"- **Primary Focus**: {top['idea_id']} remains the current operating bet.",
        "",
        "## 关键机会",
    ]
    for opportunity in opportunities:
        lines.extend(
            [
                f"### {opportunity['heading']}",
                f"- **Judgment ID**: {opportunity['judgment_id']}",
                f"- **Summary**: {opportunity['summary']}",
                "- **Backlinks**:",
                f"  - `{relative(TRIAGE_PATH)}#{opportunity['idea_id']}`",
                f"  - `{relative(PAIN_POINTS_PATH)}`",
                f"  - `{relative(CEO_RANKING_PATH)}`",
                "",
            ]
        )
    lines.append("## 主要风险")
    for risk in risks:
        lines.extend(
            [
                f"### {risk['heading']}",
                f"- **Judgment ID**: {risk['judgment_id']}",
                f"- **Summary**: {risk['summary']}",
                "- **Backlinks**:",
                f"  - `{relative(TRIAGE_PATH)}#{risk['idea_id']}`",
                f"  - `{relative(MARKET_PLAN_PATH)}`",
                f"  - `{relative(TECH_SPEC_PATH)}`",
                f"  - `{relative(CEO_RANKING_PATH)}`",
                "",
            ]
        )
    lines.append("## 推荐下一步")
    for item in next_actions:
        lines.extend(
            [
                f"- {item['action']} — evidence: {item['reason']} — trace: `judgment_id={item['judgment_id']}`",
            ]
        )
    lines.extend(
        [
            "",
            "## 证据回链",
            f"- prioritized shortlist: `{relative(TRIAGE_PATH)}`",
            f"- role outputs: `{relative(PAIN_POINTS_PATH)}`, `{relative(MARKET_PLAN_PATH)}`, `{relative(TECH_SPEC_PATH)}`",
            f"- CEO synthesis: `{relative(CEO_RANKING_PATH)}`",
            f"- trace sidecar: `{relative(DECISION_TRACE_PATH)}`",
        ]
    )
    return "\n".join(lines).rstrip() + "\n"


def build_judgment_links(
    leads: list[dict[str, Any]],
    opportunities: list[dict[str, str]],
    risks: list[dict[str, str]],
    next_actions: list[dict[str, str]],
) -> list[dict[str, Any]]:
    lead_map = {lead["idea_id"]: lead for lead in leads}
    links: list[dict[str, Any]] = []
    for item in [*opportunities, *risks, *next_actions]:
        idea_id = item["idea_id"]
        lead = lead_map.get(idea_id)
        if lead is None:
            raise DecisionPackageError(f"missing shortlist record for judgment idea_id: {idea_id}")
        generated_from = lead.get("generated_from")
        if not isinstance(generated_from, dict):
            raise DecisionPackageError(f"missing generated_from for idea_id: {idea_id}")
        history_path = generated_from.get("history_path")
        cluster_path = generated_from.get("cluster_path")
        if not history_path or not cluster_path:
            raise DecisionPackageError(f"missing backlink fields for idea_id: {idea_id}")
        links.append(
            {
                "judgment_id": item["judgment_id"],
                "idea_id": idea_id,
                "upstream_paths": [
                    f"{relative(TRIAGE_PATH)}#{idea_id}",
                    history_path,
                    cluster_path,
                ],
                "role_artifacts": [relative(path) for path in ROLE_ARTIFACTS],
            }
        )
    return links


def render_trace(generated_at: str, run_id: str, judgment_links: list[dict[str, Any]]) -> str:
    payload = {
        "generated_at": generated_at,
        "run_id": run_id,
        "operating_package_path": relative(OPERATING_DECISION_PACKAGE_PATH),
        "derived_from": {
            "prioritized_shortlist_path": relative(TRIAGE_PATH),
            "role_outputs": [relative(path) for path in ROLE_ARTIFACTS],
        },
        "judgment_links": judgment_links,
    }
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def history_output_path(date_value: str) -> Path:
    return DECISION_HISTORY_DIR / OPERATING_DECISION_HISTORY_TEMPLATE.format(date=date_value)


def main() -> int:
    args = parse_args()
    try:
        date_value = args.date or today_iso()
        generated_at = timestamp_now()
        run_id = build_run_id(date_value)

        prioritized = load_prioritized(TRIAGE_PATH)
        pain_points = load_markdown(PAIN_POINTS_PATH, "pain points")
        market_plan = load_markdown(MARKET_PLAN_PATH, "market plan")
        tech_spec = load_markdown(TECH_SPEC_PATH, "tech spec")
        ceo_ranking = load_markdown(CEO_RANKING_PATH, "ceo ranking")

        top = prioritized[0]
        recommended_id = extract_recommended_idea_id(ceo_ranking)
        risk_level = extract_markdown_value(market_plan, "Risk Level")
        target_user = extract_markdown_value(pain_points, "Target User")
        goal = build_goal(top)
        mvp_framing = build_mvp_framing(top, tech_spec)
        overall_conclusion = build_overall_conclusion(top, recommended_id, risk_level)
        opportunities = build_opportunities(prioritized)
        risks = build_risks(top, market_plan, prioritized)
        next_actions = build_next_actions(top, opportunities, risks)

        latest_output = build_operating_package(
            date_value=date_value,
            generated_at=generated_at,
            run_id=run_id,
            leads=prioritized,
            target_user=target_user,
            goal=goal,
            mvp_framing=mvp_framing,
            overall_conclusion=overall_conclusion,
            opportunities=opportunities,
            risks=risks,
            next_actions=next_actions,
        )
        history_path = history_output_path(date_value)
        trace_output = render_trace(
            generated_at=generated_at,
            run_id=run_id,
            judgment_links=build_judgment_links(prioritized, opportunities, risks, next_actions),
        )

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
        write_output(DECISION_TRACE_PATH, trace_output)
        print(f"Wrote {relative(OPERATING_DECISION_PACKAGE_PATH)}")
        print(f"Wrote {relative(history_path)}")
        print(f"Wrote {relative(DECISION_TRACE_PATH)}")
        return 0
    except DecisionPackageError as exc:
        print(f"decision package error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
