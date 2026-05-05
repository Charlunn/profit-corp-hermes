#!/usr/bin/env python3
import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


class ChatDeliveryNotifyError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render and persist the final delivery chat reply from authority truth.")
    parser.add_argument("--authority-record-path", required=True, help="APPROVED_PROJECT.json authority record path.")
    parser.add_argument("--platform", required=True, choices=["discord", "telegram"], help="Chat platform to render.")
    return parser.parse_args()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_text(path_value: str) -> str:
    path = Path(path_value)
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def build_notification_key(platform: str, record: dict[str, Any]) -> str:
    pipeline = dict(record.get("pipeline", {}) or {})
    shipping = dict(record.get("shipping", {}) or {})
    vercel = dict(shipping.get("vercel", {}) or {})
    raw = "::".join(
        [
            platform,
            str(record.get("artifacts", {}).get("authority_record_path", "")).strip(),
            str(pipeline.get("stage", "")).strip(),
            str(pipeline.get("status", "")).strip(),
            str(pipeline.get("block_reason", "")).strip(),
            str(pipeline.get("final_handoff_path", record.get("artifacts", {}).get("final_handoff_path", ""))).strip(),
            str(vercel.get("deploy_url", vercel.get("deployment_url", ""))).strip(),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def render_final_chat_message(record: dict[str, Any], *, platform: str) -> tuple[str, str]:
    pipeline = dict(record.get("pipeline", {}) or {})
    artifacts = dict(record.get("artifacts", {}) or {})
    identity = dict(record.get("project_identity", {}) or {})
    shipping = dict(record.get("shipping", {}) or {})
    vercel = dict(shipping.get("vercel", {}) or {})
    app_name = str(identity.get("app_name", identity.get("project_slug", "Approved Project"))).strip() or "Approved Project"
    deploy_url = str(vercel.get("deploy_url", vercel.get("deployment_url", ""))).strip()
    status_path = str(artifacts.get("status_path", "")).strip()
    final_review_path = str(artifacts.get("final_review_path", "")).strip()
    final_handoff_path = str(pipeline.get("final_handoff_path", artifacts.get("final_handoff_path", ""))).strip()
    stage = str(pipeline.get("stage", "not available")).strip() or "not available"
    status = str(pipeline.get("status", "not available")).strip() or "not available"
    block_reason = str(pipeline.get("block_reason", "")).strip()
    approval_summary = str(record.get("approval", {}).get("evidence", {}).get("summary", "")).strip()

    status_text = read_text(status_path)
    final_review_text = read_text(final_review_path)
    if status == "completed":
        if not (deploy_url and final_handoff_path and status_text and final_review_text):
            raise ChatDeliveryNotifyError("completed delivery truth is incomplete; refusing success notification")
        message = "\n".join(
            [
                f"[{platform}] {app_name} shipped successfully.",
                f"Deployment: {deploy_url}",
                f"Summary: {approval_summary or 'Delivery completed from persisted authority truth.'}",
                f"Final handoff: {final_handoff_path}",
                f"Final operator review: {final_review_path}",
                f"Pipeline status: {status_path}",
            ]
        )
        return "completed", message

    message = "\n".join(
        [
            f"[{platform}] {app_name} is blocked.",
            f"Failed stage: {stage}",
            f"Blocked reason: {block_reason or 'not available'}",
            f"Recovery context: review {status_path or 'the authority status artifact'} before resuming.",
            f"Final operator review: {final_review_path or 'not available'}",
        ]
    )
    return "blocked", message


def deliver_final_chat_notification(authority_record_path: Path | str, *, platform: str) -> dict[str, Any]:
    authority_path = Path(authority_record_path)
    record = load_json(authority_path)
    key = build_notification_key(platform, record)
    notifications = record.setdefault("chat_notifications", {}).setdefault("final", {})
    if key in notifications:
        stored = dict(notifications[key])
        return {
            "ok": True,
            "platform": platform,
            "delivery_status": stored.get("delivery_status", "not_available"),
            "message": stored.get("message", ""),
            "notification_key": key,
            "idempotent_replay": True,
        }

    delivery_status, message = render_final_chat_message(record, platform=platform)
    notifications[key] = {
        "platform": platform,
        "delivery_status": delivery_status,
        "message": message,
    }
    write_json(authority_path, record)
    return {
        "ok": True,
        "platform": platform,
        "delivery_status": delivery_status,
        "message": message,
        "notification_key": key,
        "idempotent_replay": False,
    }


def main() -> int:
    args = parse_args()
    try:
        result = deliver_final_chat_notification(Path(args.authority_record_path), platform=args.platform)
    except (OSError, json.JSONDecodeError, ChatDeliveryNotifyError) as exc:
        print(f"chat delivery notify error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
