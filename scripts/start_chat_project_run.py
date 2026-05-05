#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any, Callable


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.chat_intake_common import (
    AUTHORITY_FILE_NAME,
    ChatIntakeError,
    append_chat_event,
    authority_path_for,
    dump_json,
    load_existing_run_by_origin,
    normalize_chat_payload,
    run_dir_for,
    status_path_for,
    utc_now_iso,
)
from scripts.render_chat_run_status import render_chat_run_status


DEFAULT_DISPATCH_COMMAND = "bash orchestration/cron/commands.sh run-analysis-loop"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Normalize a Discord or Telegram intake and bootstrap one governed chat run.")
    parser.add_argument("--payload-json", default="", help="Raw chat payload as a JSON object.")
    parser.add_argument("--payload-file", default="", help="Path to a JSON payload file.")
    parser.add_argument("--dry-run", action="store_true", help="Normalize and print the result without writing files.")
    return parser.parse_args()


def read_payload(args: argparse.Namespace) -> dict[str, Any]:
    if args.payload_json.strip():
        payload = json.loads(args.payload_json)
    elif args.payload_file.strip():
        payload = json.loads(Path(args.payload_file).read_text(encoding="utf-8"))
    else:
        raise ChatIntakeError("either --payload-json or --payload-file is required")
    if not isinstance(payload, dict):
        raise ChatIntakeError("chat payload must decode to a JSON object")
    return payload


def build_dispatch(run_id: str) -> dict[str, Any]:
    return {
        "mode": "governed-existing-pipeline",
        "target": "existing-discovery-startup",
        "command": DEFAULT_DISPATCH_COMMAND,
        "status": "ready",
        "run_id": run_id,
    }


def dispatch_existing_pipeline(_record: dict[str, Any]) -> dict[str, Any]:
    return {
        "ok": True,
        "action": "dispatched_existing_governed_startup",
        "command": DEFAULT_DISPATCH_COMMAND,
        "target": "existing-discovery-startup",
    }


def _build_new_record(envelope: dict[str, Any]) -> dict[str, Any]:
    run_id = str(envelope["run_id"])
    return {
        "run_id": run_id,
        "chat_origin": envelope,
        "pipeline": {
            "stage": "intake",
            "status": "ready",
            "resume_from_stage": "qualification",
            "status_path": status_path_for(run_id).as_posix(),
        },
        "dispatch": build_dispatch(run_id),
        "blocked": {
            "reason": "",
            "detail": "",
        },
        "artifacts": {
            "project_directory": run_dir_for(run_id).as_posix(),
            "authority_record_path": authority_path_for(run_id).as_posix(),
            "status_path": status_path_for(run_id).as_posix(),
        },
    }


def bootstrap_chat_project_run(
    raw_payload: dict[str, Any],
    dispatch_fn: Callable[[dict[str, Any]], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    envelope = normalize_chat_payload(raw_payload)
    existing = load_existing_run_by_origin(str(envelope["origin_key"]))
    if existing is not None:
        render_chat_run_status(str(existing["run_id"]), str(run_dir_for(str(existing["run_id"]))))
        return {
            "ok": True,
            "run_id": existing["run_id"],
            "authority_record_path": authority_path_for(str(existing["run_id"])).as_posix(),
            "status_path": status_path_for(str(existing["run_id"])).as_posix(),
            "idempotent_replay": True,
            "record": existing,
        }

    record = _build_new_record(envelope)
    authority_path = authority_path_for(str(record["run_id"]))
    dump_json(authority_path, record)
    append_chat_event(
        {
            "run_id": record["run_id"],
            "timestamp": utc_now_iso(),
            "stage": "intake",
            "status": "ready",
            "action": "chat_run_initialized",
            "platform": envelope["platform"],
            "origin_key": envelope["origin_key"],
            "authority_record_path": authority_path.as_posix(),
        }
    )

    dispatcher = dispatch_fn or dispatch_existing_pipeline
    try:
        dispatch_result = dispatcher(record)
    except Exception as exc:  # pragma: no cover - defensive gate
        dispatch_result = {
            "ok": False,
            "action": "dispatch_failed",
            "error": str(exc),
            "command": DEFAULT_DISPATCH_COMMAND,
            "target": "existing-discovery-startup",
        }

    record["dispatch"].update(
        {
            "status": "completed" if dispatch_result.get("ok") else "blocked",
            "last_action": str(dispatch_result.get("action", "")).strip(),
            "command": str(dispatch_result.get("command", DEFAULT_DISPATCH_COMMAND)).strip(),
            "target": str(dispatch_result.get("target", "existing-discovery-startup")).strip(),
        }
    )
    if dispatch_result.get("ok"):
        record["pipeline"].update({"stage": "qualification", "status": "running"})
    else:
        record["pipeline"].update({"stage": "intake", "status": "blocked"})
        record["blocked"] = {
            "reason": "dispatch_failed",
            "detail": str(dispatch_result.get("error", "governed dispatch failed")).strip(),
        }
    dump_json(authority_path, record)
    append_chat_event(
        {
            "run_id": record["run_id"],
            "timestamp": utc_now_iso(),
            "stage": record["pipeline"]["stage"],
            "status": record["pipeline"]["status"],
            "action": record["dispatch"]["last_action"] or "dispatch_recorded",
            "platform": envelope["platform"],
            "origin_key": envelope["origin_key"],
            "authority_record_path": authority_path.as_posix(),
        }
    )
    render_chat_run_status(str(record["run_id"]), str(run_dir_for(str(record["run_id"]))))
    return {
        "ok": dispatch_result.get("ok", False),
        "run_id": record["run_id"],
        "authority_record_path": authority_path.as_posix(),
        "status_path": status_path_for(str(record["run_id"])).as_posix(),
        "record": record,
    }


def main() -> int:
    args = parse_args()
    try:
        payload = read_payload(args)
        result = bootstrap_chat_project_run(payload)
    except (ChatIntakeError, OSError, json.JSONDecodeError) as exc:
        print(f"chat run bootstrap error: {exc}", file=sys.stderr)
        return 1
    if args.dry_run:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    print(json.dumps({"run_id": result["run_id"], "authority_record_path": result["authority_record_path"]}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
