#!/usr/bin/env python3
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
SHARED_DIR = ROOT_DIR / "assets" / "shared"
TRIAGE_PATH = SHARED_DIR / "external_intelligence" / "triage" / "prioritized_signals.json"
SIGNALS_HISTORY_PATH = SHARED_DIR / "external_intelligence" / "history" / "signals.jsonl"
QUALIFICATION_DIR = SHARED_DIR / "qualification"
QUALIFICATION_LATEST_DIR = QUALIFICATION_DIR / "latest"
QUALIFICATION_HISTORY_DIR = QUALIFICATION_DIR / "history"
LATEST_BUNDLE_PATH = QUALIFICATION_LATEST_DIR / "qualification_bundle.json"
LATEST_SUMMARY_PATH = QUALIFICATION_LATEST_DIR / "QUALIFICATION_SUMMARY.md"
ALLOWED_WRITE_DIRS = (QUALIFICATION_DIR, QUALIFICATION_LATEST_DIR, QUALIFICATION_HISTORY_DIR)
FRESHNESS_WINDOW_HOURS = 72

ALLOWED_BLOCK_REASONS = {
    "missing_required_evidence",
    "stale_required_evidence",
    "pain_not_user_facing",
    "pain_too_vague",
    "pain_not_narrow_enough",
    "template_fit_failed",
    "missing_market_pricing_proof",
}


class QualificationError(Exception):
    pass


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso8601(value: str) -> datetime:
    text = str(value).strip()
    if not text:
        raise QualificationError("blank timestamp")
    return datetime.fromisoformat(text.replace("Z", "+00:00")).astimezone(timezone.utc)


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise QualificationError(f"JSON file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise QualificationError(f"invalid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise QualificationError(f"JSON object required: {path}")
    return payload


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise QualificationError(f"JSONL file not found: {path}")
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            rows.append(payload)
    return rows


def ensure_allowed_write_path(path: Path) -> None:
    resolved = path.resolve()
    for directory in ALLOWED_WRITE_DIRS:
        try:
            resolved.relative_to(directory.resolve())
            return
        except ValueError:
            continue
    raise QualificationError(f"refusing to write outside qualification directories: {path}")


def write_text(path: Path, content: str) -> None:
    ensure_allowed_write_path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def write_json(path: Path, payload: dict[str, Any]) -> None:
    write_text(path, json.dumps(payload, ensure_ascii=False, indent=2))


def validate_reason(reason: str) -> str:
    normalized = str(reason).strip()
    if normalized not in ALLOWED_BLOCK_REASONS:
        raise QualificationError(f"unsupported qualification block reason: {normalized}")
    return normalized


def build_signals_index(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {str(item.get("signal_id", "")).strip(): item for item in rows if str(item.get("signal_id", "")).strip()}


def evidence_rows_for_candidate(candidate: dict[str, Any], signals_index: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    signal_ids = [str(value).strip() for value in list(candidate.get("signal_ids", [])) if str(value).strip()]
    if not signal_ids:
        lead_signal_id = str(candidate.get("lead_signal_id", "")).strip()
        if lead_signal_id:
            signal_ids = [lead_signal_id]
    rows = [signals_index[item] for item in signal_ids if item in signals_index]
    if not rows:
        raise QualificationError(f"candidate {candidate.get('idea_id', 'unknown')} missing required evidence rows")
    return rows


def evaluate_candidate(candidate: dict[str, Any], signals_index: dict[str, dict[str, Any]], current_time: datetime | None = None) -> dict[str, Any]:
    current = current_time or now_utc()
    evidence_rows = evidence_rows_for_candidate(candidate, signals_index)
    freshness_cutoff = current - timedelta(hours=FRESHNESS_WINDOW_HOURS)
    evidence_checks: list[dict[str, Any]] = []
    stale_found = False
    for row in evidence_rows:
        observed_at_raw = str(row.get("published_at", "")).strip() or str(row.get("collected_at", "")).strip()
        observed_at = parse_iso8601(observed_at_raw)
        passes = observed_at >= freshness_cutoff
        stale_found = stale_found or not passes
        evidence_checks.append(
            {
                "signal_id": str(row.get("signal_id", "")).strip(),
                "observed_at": observed_at.replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "passes_72h": passes,
                "url": str(row.get("url", "")).strip(),
            }
        )

    target_user = str(candidate.get("target_user", "")).strip()
    problem_summary = str(candidate.get("problem_summary", "")).strip()
    market_pricing_proof = candidate.get("market_pricing_proof", {})
    feasibility = candidate.get("feasibility", {})
    reason_codes: list[str] = []

    if stale_found:
        reason_codes.append("stale_required_evidence")
    if not target_user or target_user.lower() in {"developers and technical operators", "everyone", "general users"}:
        reason_codes.append("pain_not_user_facing")
    if len(problem_summary.split()) < 8:
        reason_codes.append("pain_too_vague")
    if not any(keyword in problem_summary.lower() for keyword in ("pain", "slow", "manual", "lose", "workflow", "qualify", "follow-up", "operators")):
        reason_codes.append("pain_not_narrow_enough")

    requires_protected_layer_change = bool(feasibility.get("requires_protected_layer_change", False))
    requires_custom_backend = bool(feasibility.get("requires_custom_backend", False))
    if requires_protected_layer_change or requires_custom_backend:
        reason_codes.append("template_fit_failed")

    competitors = list(market_pricing_proof.get("competitor_links", [])) if isinstance(market_pricing_proof, dict) else []
    pricing = list(market_pricing_proof.get("pricing_links", [])) if isinstance(market_pricing_proof, dict) else []
    if not competitors or not pricing:
        reason_codes.append("missing_market_pricing_proof")

    verdict = "passed" if not reason_codes else "blocked"
    return {
        "idea_id": str(candidate.get("idea_id", "")).strip(),
        "title": str(candidate.get("title", "")).strip(),
        "verdict": verdict,
        "reason_codes": [validate_reason(reason) for reason in reason_codes],
        "evidence_checks": evidence_checks,
        "target_user": target_user,
        "problem_summary": problem_summary,
        "market_pricing_proof": market_pricing_proof if isinstance(market_pricing_proof, dict) else {},
        "feasibility": feasibility if isinstance(feasibility, dict) else {},
        "generated_from": dict(candidate.get("generated_from", {})),
    }


def render_summary(bundle: dict[str, Any]) -> str:
    lines = [
        "# Qualification Summary",
        f"- **Generated At**: `{bundle.get('generated_at', 'not available')}`",
        f"- **Candidate Count**: `{len(bundle.get('candidates', []))}`",
        "",
        "## Verdicts",
    ]
    for candidate in bundle.get("candidates", []):
        reasons = ", ".join(candidate.get("reason_codes", [])) or "passed"
        lines.append(f"- `{candidate.get('idea_id', 'unknown')}` -> `{candidate.get('verdict', 'unknown')}` ({reasons})")
    return "\n".join(lines) + "\n"
