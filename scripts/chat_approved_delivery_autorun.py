#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.start_approved_project_delivery import (
    finalize_delivery_handoff,
    resume_approved_project_delivery,
    start_approved_project_delivery,
)


class ChatAutorunError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Continue an approved delivery pipeline automatically from authority truth.")
    parser.add_argument("--authority-record-path", required=True, help="APPROVED_PROJECT.json authority record path.")
    parser.add_argument("--workspace-root", default="", help="Optional workspace root override.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def authority_is_completed(record: dict[str, Any]) -> bool:
    pipeline = dict(record.get("pipeline", {}) or {})
    final_handoff_path = str(
        pipeline.get("final_handoff_path", record.get("artifacts", {}).get("final_handoff_path", ""))
    ).strip()
    return (
        str(pipeline.get("stage", "")).strip() == "handoff"
        and str(pipeline.get("status", "")).strip() == "completed"
        and final_handoff_path
        and Path(final_handoff_path).exists()
    )


def should_finalize(record: dict[str, Any], result: dict[str, Any]) -> bool:
    if not result.get("ok"):
        return False
    pipeline = dict(record.get("pipeline", {}) or {})
    if str(result.get("stage", "")).strip() == "handoff" and str(result.get("status", "")).strip() == "completed":
        return False
    if str(pipeline.get("resume_from_stage", "")).strip() == "handoff":
        return True
    final_handoff_path = str(
        result.get("final_handoff_path", pipeline.get("final_handoff_path", record.get("artifacts", {}).get("final_handoff_path", "")))
    ).strip()
    return bool(final_handoff_path and Path(final_handoff_path).exists())


def autorun_approved_delivery(authority_record_path: Path | str, *, workspace_root: Path | None = None) -> dict[str, Any]:
    authority_path = Path(authority_record_path)
    record = load_json(authority_path)
    pipeline = dict(record.get("pipeline", {}) or {})
    if authority_is_completed(record):
        return {
            "ok": True,
            "stage": "handoff",
            "status": "completed",
            "final_handoff_path": str(pipeline.get("final_handoff_path", record.get("artifacts", {}).get("final_handoff_path", ""))).strip(),
            "idempotent_replay": True,
        }

    current_status = str(pipeline.get("status", "")).strip().lower()
    current_stage = str(pipeline.get("stage", "approval")).strip() or "approval"
    if current_status == "blocked" or current_stage not in {"approval", ""}:
        result = resume_approved_project_delivery(authority_path, workspace_root=workspace_root)
    else:
        result = start_approved_project_delivery(authority_path, workspace_root=workspace_root)

    refreshed = load_json(authority_path)
    if should_finalize(refreshed, result):
        finalized = finalize_delivery_handoff(authority_path)
        finalized["idempotent_replay"] = False
        return finalized
    result["idempotent_replay"] = False
    return result


def main() -> int:
    args = parse_args()
    try:
        workspace_root = Path(args.workspace_root) if args.workspace_root else None
        result = autorun_approved_delivery(Path(args.authority_record_path), workspace_root=workspace_root)
    except (OSError, json.JSONDecodeError, ChatAutorunError) as exc:
        print(f"chat autorun error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 1


if __name__ == "__main__":
    raise SystemExit(main())
