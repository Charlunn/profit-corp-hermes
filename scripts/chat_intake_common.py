#!/usr/bin/env python3
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
CHAT_RUNS_ROOT = ROOT_DIR / "assets" / "shared" / "chat-runs"
CHAT_EVENTS_NAME = "chat-run-events.jsonl"
CHAT_STATUS_NAME = "CHAT_RUN_STATUS.md"
AUTHORITY_FILE_NAME = "CHAT_RUN.json"

REQUIRED_CANONICAL_FIELDS = (
    "platform",
    "channel_or_chat_id",
    "thread_or_reply_context",
    "requester",
    "message_id",
    "message_text",
    "received_at",
    "intent",
)


class ChatIntakeError(Exception):
    pass


def utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ChatIntakeError(f"invalid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ChatIntakeError(f"JSON object required: {path}")
    return payload


def dump_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def normalize_requester(requester: Any) -> dict[str, str]:
    if not isinstance(requester, dict):
        raise ChatIntakeError("missing requester provenance")
    requester_id = str(requester.get("id", "")).strip()
    display_name = str(requester.get("display_name", "")).strip()
    username = str(requester.get("username", "")).strip()
    if not requester_id or not (display_name or username):
        raise ChatIntakeError("missing requester provenance")
    return {
        "id": requester_id,
        "display_name": display_name or username,
        "username": username or display_name,
    }


def normalize_thread_context(platform: str, payload: dict[str, Any]) -> dict[str, str]:
    if platform == "discord":
        channel_id = str(payload.get("channel_id", "")).strip()
        message_id = str(payload.get("message_id", "")).strip()
        thread_id = str(payload.get("thread_id", "")).strip()
        if not channel_id or not message_id:
            raise ChatIntakeError("missing chat provenance for discord payload")
        return {
            "channel_or_chat_id": channel_id,
            "thread_or_reply_context": thread_id or f"message:{message_id}",
        }
    if platform == "telegram":
        chat = payload.get("chat")
        message = payload.get("message")
        reply_to_message = payload.get("reply_to_message")
        if not isinstance(chat, dict) or not isinstance(message, dict):
            raise ChatIntakeError("missing chat provenance for telegram payload")
        chat_id = str(chat.get("id", "")).strip()
        message_id = str(message.get("message_id", "")).strip()
        reply_id = ""
        if isinstance(reply_to_message, dict):
            reply_id = str(reply_to_message.get("message_id", "")).strip()
        if not chat_id or not message_id:
            raise ChatIntakeError("missing chat provenance for telegram payload")
        return {
            "channel_or_chat_id": chat_id,
            "thread_or_reply_context": reply_id or f"message:{message_id}",
        }
    if platform == "hermes":
        conversation = payload.get("conversation")
        request = payload.get("request")
        provenance = payload.get("provenance")
        if not isinstance(conversation, dict) or not isinstance(request, dict) or not isinstance(provenance, dict):
            raise ChatIntakeError("missing Hermes start provenance")
        conversation_id = str(conversation.get("id", "")).strip()
        request_id = str(request.get("id", "")).strip()
        session_id = str(provenance.get("session_id", "")).strip()
        if not conversation_id or not request_id:
            raise ChatIntakeError("missing Hermes start provenance")
        return {
            "channel_or_chat_id": conversation_id,
            "thread_or_reply_context": session_id or f"request:{request_id}",
        }
    raise ChatIntakeError(f"unsupported platform: {platform}")


def extract_message_bits(platform: str, payload: dict[str, Any]) -> dict[str, str]:
    if platform == "discord":
        content = str(payload.get("content", "")).strip()
        message_id = str(payload.get("message_id", "")).strip()
        received_at = str(payload.get("timestamp", "")).strip()
        requester = normalize_requester(payload.get("author"))
    elif platform == "telegram":
        message = payload.get("message")
        from_user = payload.get("from") or (message.get("from") if isinstance(message, dict) else None)
        if not isinstance(message, dict):
            raise ChatIntakeError("missing telegram message payload")
        content = str(message.get("text", "")).strip()
        message_id = str(message.get("message_id", "")).strip()
        received_at = str(message.get("date", "")).strip()
        requester = normalize_requester(from_user)
    elif platform == "hermes":
        request = payload.get("request")
        provenance = payload.get("provenance")
        if not isinstance(request, dict):
            raise ChatIntakeError("missing Hermes request payload")
        if not isinstance(provenance, dict) or not str(provenance.get("surface", "")).strip():
            raise ChatIntakeError("missing Hermes start provenance")
        content = str(request.get("text", "")).strip()
        message_id = str(request.get("id", "")).strip()
        received_at = str(request.get("received_at", "")).strip()
        requester = normalize_requester(payload.get("owner"))
    else:
        raise ChatIntakeError(f"unsupported platform: {platform}")
    if not content or not message_id or not received_at:
        raise ChatIntakeError("missing message provenance")
    return {
        "message_text": content,
        "message_id": message_id,
        "received_at": received_at,
        "requester": requester,
    }


def derive_intent(message_text: str) -> str:
    compact = " ".join(message_text.split())
    return compact[:240]


def canonical_origin_key(envelope: dict[str, Any]) -> str:
    raw = "::".join(
        [
            str(envelope["platform"]),
            str(envelope["channel_or_chat_id"]),
            str(envelope["thread_or_reply_context"]),
            str(envelope["message_id"]),
            str(envelope["requester"]["id"]),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def governed_run_id(envelope: dict[str, Any]) -> str:
    digest = canonical_origin_key(envelope)[:12]
    date_prefix = str(envelope["received_at"]).replace(":", "").replace("-", "")[:8] or "chatrun"
    return f"chat-run-{date_prefix}-{digest}"


def normalize_chat_payload(raw_payload: dict[str, Any]) -> dict[str, Any]:
    platform = str(raw_payload.get("platform", "")).strip().lower()
    if platform not in {"discord", "telegram", "hermes"}:
        raise ChatIntakeError("platform must be discord, telegram, or hermes")
    thread_bits = normalize_thread_context(platform, raw_payload)
    message_bits = extract_message_bits(platform, raw_payload)
    envelope = {
        "platform": platform,
        **thread_bits,
        "requester": message_bits["requester"],
        "message_id": message_bits["message_id"],
        "message_text": message_bits["message_text"],
        "received_at": message_bits["received_at"],
        "intent": derive_intent(message_bits["message_text"]),
    }
    for field in REQUIRED_CANONICAL_FIELDS:
        if field == "requester":
            if not isinstance(envelope[field], dict):
                raise ChatIntakeError(f"missing canonical field: {field}")
        elif not str(envelope[field]).strip():
            raise ChatIntakeError(f"missing canonical field: {field}")
    if platform == "hermes":
        provenance = raw_payload.get("provenance")
        if not isinstance(provenance, dict):
            raise ChatIntakeError("missing Hermes start provenance")
        envelope["provenance"] = {
            "surface": str(provenance.get("surface", "")).strip(),
            "session_id": str(provenance.get("session_id", "")).strip(),
        }
        if not envelope["provenance"]["surface"]:
            raise ChatIntakeError("missing Hermes start provenance")
    envelope["origin_key"] = canonical_origin_key(envelope)
    envelope["run_id"] = governed_run_id(envelope)
    return envelope


def run_dir_for(run_id: str) -> Path:
    return CHAT_RUNS_ROOT / run_id


def authority_path_for(run_id: str) -> Path:
    return run_dir_for(run_id) / AUTHORITY_FILE_NAME


def events_path_for() -> Path:
    return CHAT_RUNS_ROOT / CHAT_EVENTS_NAME


def status_path_for(run_id: str) -> Path:
    return run_dir_for(run_id) / CHAT_STATUS_NAME


def append_chat_event(event: dict[str, Any]) -> None:
    path = events_path_for()
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def load_existing_run_by_origin(origin_key: str) -> dict[str, Any] | None:
    if not CHAT_RUNS_ROOT.exists():
        return None
    for candidate in CHAT_RUNS_ROOT.glob("*/CHAT_RUN.json"):
        try:
            record = load_json(candidate)
        except ChatIntakeError:
            continue
        if str(record.get("chat_origin", {}).get("origin_key", "")).strip() == origin_key:
            return record
    return None
