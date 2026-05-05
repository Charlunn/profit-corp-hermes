#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.qualification_common import (
    LATEST_BUNDLE_PATH,
    LATEST_SUMMARY_PATH,
    QUALIFICATION_HISTORY_DIR,
    QUALIFICATION_LATEST_DIR,
    QUALIFICATION_DIR,
    QualificationError,
    evaluate_candidate,
    load_json,
    load_jsonl,
    now_utc,
    render_summary,
    write_json,
    write_text,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate prioritized candidates against qualification gates.")
    parser.add_argument("--triage-path", default="", help="Override prioritized_signals.json path.")
    parser.add_argument("--signals-path", default="", help="Override signals history path.")
    parser.add_argument("--dry-run", action="store_true", help="Print the bundle instead of writing files.")
    return parser.parse_args()


def qualification_history_path(timestamp: str) -> Path:
    safe_stamp = timestamp.replace(":", "").replace("-", "")
    return QUALIFICATION_HISTORY_DIR / f"{safe_stamp}-qualification-bundle.json"


def load_candidates(triage_path: Path) -> list[dict[str, Any]]:
    payload = load_json(triage_path)
    prioritized = payload.get("prioritized_signals")
    if not isinstance(prioritized, list) or not prioritized:
        raise QualificationError("prioritized_signals must be a non-empty list")
    candidates: list[dict[str, Any]] = []
    for item in prioritized:
        if not isinstance(item, dict):
            continue
        candidate = dict(item)
        candidate.setdefault("signal_ids", [str(candidate.get("lead_signal_id", "")).strip()])
        candidates.append(candidate)
    return candidates


def evaluate_candidates_bundle(triage_path: Path, signals_path: Path, current_time=None) -> dict[str, Any]:
    rows = load_jsonl(signals_path)
    from scripts.qualification_common import build_signals_index

    signals_index = build_signals_index(rows)
    generated_at = (current_time or now_utc()).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    candidates = [evaluate_candidate(item, signals_index, current_time=current_time) for item in load_candidates(triage_path)]
    return {
        "generated_at": generated_at,
        "qualification_source": triage_path.as_posix(),
        "signals_source": signals_path.as_posix(),
        "candidates": candidates,
    }


def main() -> int:
    args = parse_args()
    from scripts.qualification_common import SIGNALS_HISTORY_PATH, TRIAGE_PATH

    triage_path = Path(args.triage_path) if args.triage_path else TRIAGE_PATH
    signals_path = Path(args.signals_path) if args.signals_path else SIGNALS_HISTORY_PATH
    try:
        bundle = evaluate_candidates_bundle(triage_path, signals_path)
        if args.dry_run:
            print(json.dumps(bundle, ensure_ascii=False, indent=2))
            return 0
        QUALIFICATION_DIR.mkdir(parents=True, exist_ok=True)
        QUALIFICATION_LATEST_DIR.mkdir(parents=True, exist_ok=True)
        QUALIFICATION_HISTORY_DIR.mkdir(parents=True, exist_ok=True)
        write_json(LATEST_BUNDLE_PATH, bundle)
        write_json(qualification_history_path(bundle["generated_at"]), bundle)
        write_text(LATEST_SUMMARY_PATH, render_summary(bundle))
    except QualificationError as exc:
        print(f"qualification error: {exc}", file=sys.stderr)
        return 1
    print(f"wrote {LATEST_BUNDLE_PATH.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
