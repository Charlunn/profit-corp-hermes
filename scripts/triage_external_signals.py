#!/usr/bin/env python3
import argparse
import json
import math
import re
import sys
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
EXTERNAL_DIR = ROOT_DIR / "assets" / "shared" / "external_intelligence"
HISTORY_PATH = EXTERNAL_DIR / "history" / "signals.jsonl"
TRIAGE_DIR = EXTERNAL_DIR / "triage"
PRIORITIZED_PATH = TRIAGE_DIR / "prioritized_signals.json"
CLUSTERS_PATH = TRIAGE_DIR / "clusters.json"

WORD_RE = re.compile(r"[a-z0-9]+")
URL_WORD_RE = re.compile(r"^[a-z]+://")
STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "built",
    "by",
    "did",
    "do",
    "does",
    "even",
    "for",
    "from",
    "hard",
    "how",
    "i",
    "in",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "the",
    "this",
    "to",
    "we",
    "what",
    "who",
    "why",
}
URGENT_TERMS = {
    "broken",
    "difficult",
    "fail",
    "friction",
    "hate",
    "issue",
    "issues",
    "lose",
    "lost",
    "pain",
    "problem",
    "problems",
    "slow",
    "struggle",
    "stuck",
    "wish",
}


@dataclass
class Signal:
    payload: dict[str, Any]
    collected_at: datetime
    effective_at: datetime
    title_norm: str
    host: str
    keywords: set[str]


class TriageError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build prioritized triage artifacts from signal history.")
    parser.add_argument("--window-hours", type=int, default=48, help="Only include signals newer than this many hours.")
    parser.add_argument("--limit", type=int, default=25, help="Maximum number of prioritized signals to emit.")
    parser.add_argument("--dry-run", action="store_true", help="Compute outputs without writing files.")
    return parser.parse_args()


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def parse_iso8601(value: str, *, field: str) -> datetime:
    if not value:
        raise TriageError(f"missing required timestamp field: {field}")
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise TriageError(f"invalid timestamp for {field}: {value}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def tokenize(text: str) -> list[str]:
    return WORD_RE.findall(text.lower())


def normalize_title(title: str) -> str:
    tokens = [token for token in tokenize(title) if token not in STOPWORDS]
    return " ".join(tokens)


def keyword_set(payload: dict[str, Any]) -> set[str]:
    tokens: set[str] = set()
    for field in ("title", "summary", "evidence_text"):
        value = payload.get(field, "")
        if not isinstance(value, str):
            continue
        for token in tokenize(value):
            if len(token) >= 4 and token not in STOPWORDS and not token.isdigit():
                tokens.add(token)
    return tokens


def validate_payload(payload: Any, line_number: int) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise TriageError(f"line {line_number}: expected JSON object")
    required = ["signal_id", "source_id", "title", "url", "collected_at"]
    missing = [key for key in required if not payload.get(key)]
    if missing:
        raise TriageError(f"line {line_number}: missing required fields: {', '.join(missing)}")
    return payload


def load_signals(path: Path, window_hours: int) -> list[Signal]:
    if not path.exists():
        raise TriageError(f"signal history not found: {path}")

    cutoff = now_utc() - timedelta(hours=window_hours)
    signals: list[Signal] = []

    with path.open("r", encoding="utf-8") as handle:
        for line_number, raw_line in enumerate(handle, start=1):
            line = raw_line.strip()
            if not line:
                continue
            try:
                payload = json.loads(line)
            except json.JSONDecodeError as exc:
                raise TriageError(f"line {line_number}: invalid JSON") from exc
            payload = validate_payload(payload, line_number)
            collected_at = parse_iso8601(str(payload["collected_at"]), field="collected_at")
            published_raw = str(payload.get("published_at") or "").strip()
            effective_at = parse_iso8601(published_raw, field="published_at") if published_raw else collected_at
            if effective_at < cutoff:
                continue
            title = str(payload.get("title", "")).strip()
            url = str(payload.get("url", "")).strip()
            host = ""
            if URL_WORD_RE.match(url):
                host = url.split("//", 1)[1].split("/", 1)[0].lower()
            signals.append(
                Signal(
                    payload=payload,
                    collected_at=collected_at,
                    effective_at=effective_at,
                    title_norm=normalize_title(title),
                    host=host,
                    keywords=keyword_set(payload),
                )
            )
    return signals


def should_merge(anchor: Signal, candidate: Signal) -> bool:
    if anchor.payload["url"] == candidate.payload["url"]:
        return True
    if anchor.title_norm and anchor.title_norm == candidate.title_norm:
        return True
    shared_keywords = anchor.keywords & candidate.keywords
    if anchor.host and anchor.host == candidate.host and len(shared_keywords) >= 4:
        return True
    if len(shared_keywords) >= 5:
        return True
    return False


def cluster_signals(signals: list[Signal]) -> list[list[Signal]]:
    clusters: list[list[Signal]] = []
    for signal in sorted(signals, key=lambda item: item.effective_at, reverse=True):
        placed = False
        for cluster in clusters:
            anchor = cluster[0]
            if should_merge(anchor, signal):
                cluster.append(signal)
                placed = True
                break
        if not placed:
            clusters.append([signal])
    return clusters


def score_confidence(values: list[str]) -> float:
    weights = {"low": 3.0, "medium": 6.0, "high": 9.0}
    numeric = [weights.get(value.lower(), 5.0) for value in values if isinstance(value, str)]
    if not numeric:
        return 5.0
    return round(sum(numeric) / len(numeric), 2)


def recency_score(hours_old: float) -> float:
    if hours_old <= 6:
        return 10.0
    if hours_old <= 12:
        return 9.0
    if hours_old <= 24:
        return 8.0
    if hours_old <= 48:
        return 6.5
    return 4.0


def evidence_score(evidence_count: int) -> float:
    return round(min(10.0, 4.0 + math.log2(max(1, evidence_count)) * 2.0), 2)


def urgency_score(cluster: list[Signal]) -> float:
    text = " ".join(str(item.payload.get("title", "")) + " " + str(item.payload.get("summary", "")) for item in cluster).lower()
    matched = sum(1 for term in URGENT_TERMS if term in text)
    return round(min(10.0, 4.0 + matched * 1.5), 2)


def monetization_score(cluster: list[Signal]) -> float:
    keyword_hits = len({token for signal in cluster for token in signal.keywords if token in {"developer", "tools", "notifications", "security", "markdown", "memory", "performance"}})
    return round(min(10.0, 5.0 + keyword_hits * 1.2), 2)


def competition_score(cluster: list[Signal]) -> float:
    repeated_hosts = len({signal.host for signal in cluster if signal.host})
    return round(max(1.0, 8.0 - repeated_hosts), 2)


def estimate_mvp_hours(cluster: list[Signal]) -> int:
    base = 8 + len(cluster) * 2
    if any("security" in signal.keywords for signal in cluster):
        base += 4
    return base


def build_cluster_record(index: int, cluster: list[Signal], generated_at: datetime) -> dict[str, Any]:
    lead = max(cluster, key=lambda item: (len(item.keywords), item.effective_at.timestamp()))
    timestamps = [item.effective_at for item in cluster]
    newest_at = max(timestamps)
    oldest_at = min(timestamps)
    evidence_links = [item.payload["url"] for item in cluster]
    confidence = score_confidence([str(item.payload.get("confidence", "medium")) for item in cluster])
    cluster_record = {
        "cluster_id": f"cluster-{index:03d}",
        "lead_signal_id": lead.payload["signal_id"],
        "representative_title": lead.payload["title"],
        "problem_summary": str(lead.payload.get("summary") or lead.payload.get("evidence_text") or lead.payload["title"])[:280],
        "member_signal_ids": [item.payload["signal_id"] for item in cluster],
        "member_count": len(cluster),
        "evidence_count": len(cluster),
        "evidence_links": evidence_links,
        "source_ids": sorted({item.payload["source_id"] for item in cluster}),
        "latest_signal_at": newest_at.isoformat().replace("+00:00", "Z"),
        "oldest_signal_at": oldest_at.isoformat().replace("+00:00", "Z"),
        "keywords": sorted({keyword for item in cluster for keyword in item.keywords})[:12],
        "confidence": confidence,
        "generated_at": generated_at.isoformat().replace("+00:00", "Z"),
    }
    return cluster_record


def build_prioritized_records(cluster_records: list[dict[str, Any]], clusters: list[list[Signal]], generated_at: datetime, limit: int) -> list[dict[str, Any]]:
    prioritized: list[dict[str, Any]] = []
    current_time = now_utc()
    for cluster_record, cluster in zip(cluster_records, clusters):
        newest = max(signal.effective_at for signal in cluster)
        hours_old = max(0.0, (current_time - newest).total_seconds() / 3600)
        evidence = evidence_score(cluster_record["evidence_count"])
        recency = recency_score(hours_old)
        urgency = urgency_score(cluster)
        monetization = monetization_score(cluster)
        competition = competition_score(cluster)
        confidence = float(cluster_record["confidence"])
        total = round(
            10
            * (
                0.25 * urgency
                + 0.20 * evidence
                + 0.20 * recency
                + 0.15 * monetization
                + 0.10 * confidence
                + 0.10 * competition
            ),
            2,
        )
        representative = cluster[0]
        prioritized.append(
            {
                "cluster_id": cluster_record["cluster_id"],
                "lead_signal_id": cluster_record["lead_signal_id"],
                "title": cluster_record["representative_title"],
                "problem_summary": cluster_record["problem_summary"],
                "target_user": "Developers and technical operators",
                "evidence_links": cluster_record["evidence_links"],
                "evidence_count": cluster_record["evidence_count"],
                "latest_evidence_age_hours": round(hours_old, 2),
                "source_ids": cluster_record["source_ids"],
                "score_components": {
                    "urgency_pain": urgency,
                    "evidence_strength": evidence,
                    "recency": recency,
                    "monetization_signal": monetization,
                    "competition_signal": competition,
                    "confidence": confidence,
                },
                "estimated_mvp_hours": estimate_mvp_hours(cluster),
                "notes": f"Derived from {cluster_record['evidence_count']} clustered signals sharing title/url/keyword evidence.",
                "generated_from": {
                    "history_path": HISTORY_PATH.relative_to(ROOT_DIR).as_posix(),
                    "cluster_path": CLUSTERS_PATH.relative_to(ROOT_DIR).as_posix(),
                    "representative_url": representative.payload["url"],
                },
                "generated_at": generated_at.isoformat().replace("+00:00", "Z"),
                "total_score": total,
            }
        )
    prioritized.sort(key=lambda item: (-item["total_score"], item["latest_evidence_age_hours"], item["title"].lower()))
    for index, record in enumerate(prioritized[:limit], start=1):
        record["rank"] = index
        record["idea_id"] = f"IDEA-{index:03d}"
    return prioritized[:limit]


def ensure_output_dir() -> None:
    TRIAGE_DIR.mkdir(parents=True, exist_ok=True)


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        signals = load_signals(HISTORY_PATH, args.window_hours)
        if not signals:
            raise TriageError("no signals found in requested time window")
        generated_at = now_utc()
        clusters = cluster_signals(signals)
        cluster_records = [build_cluster_record(index, cluster, generated_at) for index, cluster in enumerate(clusters, start=1)]
        prioritized_records = build_prioritized_records(cluster_records, clusters, generated_at, args.limit)
        clusters_payload = {
            "generated_at": generated_at.isoformat().replace("+00:00", "Z"),
            "window_hours": args.window_hours,
            "source_history": HISTORY_PATH.relative_to(ROOT_DIR).as_posix(),
            "cluster_count": len(cluster_records),
            "clusters": cluster_records,
        }
        prioritized_payload = {
            "generated_at": generated_at.isoformat().replace("+00:00", "Z"),
            "window_hours": args.window_hours,
            "source_history": HISTORY_PATH.relative_to(ROOT_DIR).as_posix(),
            "prioritized_count": len(prioritized_records),
            "prioritized_signals": prioritized_records,
        }
        if args.dry_run:
            json.dump({"clusters": clusters_payload, "prioritized": prioritized_payload}, sys.stdout, ensure_ascii=False, indent=2)
            sys.stdout.write("\n")
            return 0
        ensure_output_dir()
        write_json(CLUSTERS_PATH, clusters_payload)
        write_json(PRIORITIZED_PATH, prioritized_payload)
        print(f"Wrote {CLUSTERS_PATH.relative_to(ROOT_DIR)}")
        print(f"Wrote {PRIORITIZED_PATH.relative_to(ROOT_DIR)}")
        return 0
    except TriageError as exc:
        print(f"triage error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
