#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.governance_common import (
    DECISION_TRACE_PATH,
    GOVERNANCE_EVENTS_PATH,
    OPERATING_DECISION_PACKAGE_PATH,
    find_latest_event,
    load_jsonl,
    relative,
)


JUSTIFICATION_FILE_NAME = "platform-justification.json"
APPROVED_STATUSES = {"approved", "override"}
PENDING_STATUSES = {"pending", "blocked", "failed", ""}


class PlatformJustificationError(RuntimeError):
    """Raised when platform-justification artifacts cannot be created or validated."""


def _utc_timestamp() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _load_json(path: Path, *, label: str) -> dict[str, Any]:
    if not path.exists():
        raise PlatformJustificationError(f"{label} not found: {path.as_posix()}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise PlatformJustificationError(f"invalid JSON in {label}: {path.as_posix()}") from exc
    if not isinstance(payload, dict):
        raise PlatformJustificationError(f"{label} root must be an object: {path.as_posix()}")
    return payload


def _write_json(path: Path, payload: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path.as_posix()


def _project_dir(authority_record_path: Path) -> Path:
    return authority_record_path.parent


def _justification_path(authority_record_path: Path) -> Path:
    return _project_dir(authority_record_path) / JUSTIFICATION_FILE_NAME


def _load_authority_record(authority_record_path: Path | str) -> dict[str, Any]:
    return _load_json(Path(authority_record_path), label="approved-project authority record")


def _project_slug(record: dict[str, Any], authority_record_path: Path) -> str:
    identity = record.get("project_identity", {})
    return str(record.get("project_slug") or identity.get("project_slug") or authority_record_path.parent.name).strip()


def _workspace_path(record: dict[str, Any]) -> str:
    pipeline = record.get("pipeline", {})
    artifacts = record.get("artifacts", {})
    return str(pipeline.get("workspace_path") or artifacts.get("workspace_path") or record.get("workspace_path") or "").strip()


def _resolve_governance_link(governance_action_id: str) -> tuple[str, dict[str, Any] | None]:
    action_id = str(governance_action_id).strip()
    if not action_id:
        return "", None
    latest = find_latest_event(action_id, load_jsonl(GOVERNANCE_EVENTS_PATH))
    return action_id, latest


def _derive_governance_status(latest_event: dict[str, Any] | None) -> str:
    if not latest_event:
        return "pending"
    return str(latest_event.get("status_after", "pending")).strip().lower() or "pending"


def _derive_event_type(latest_event: dict[str, Any] | None) -> str:
    if not latest_event:
        return "requested"
    return str(latest_event.get("event_type", "requested")).strip().lower() or "requested"


def _derive_block_reason(governance_status: str) -> str:
    if governance_status in APPROVED_STATUSES:
        return ""
    if governance_status == "rejected":
        return "platform_justification_rejected"
    return "platform_justification_pending"


def _base_artifact_payload(
    *,
    authority_record_path: Path,
    record: dict[str, Any],
    stage: str,
    classification: dict[str, Any],
    classification_evidence_path: str,
    governance_action_id: str,
    latest_event: dict[str, Any] | None,
) -> dict[str, Any]:
    governance_status = _derive_governance_status(latest_event)
    return {
        "artifact_type": "platform_justification",
        "project_slug": _project_slug(record, authority_record_path),
        "authority_record_path": authority_record_path.as_posix(),
        "workspace_path": _workspace_path(record),
        "stage": stage,
        "classification": str(classification.get("classification", "")).strip(),
        "classification_evidence_path": str(classification_evidence_path).strip(),
        "protected_matches": list(classification.get("protected_matches", [])),
        "touched_paths": list(classification.get("touched_paths", [])),
        "reasons": list(classification.get("reasons", [])),
        "governance": {
            "action_id": governance_action_id,
            "status": governance_status,
            "event_type": _derive_event_type(latest_event),
            "approved_by": str((latest_event or {}).get("approved_by", "")).strip(),
            "reason": str((latest_event or {}).get("reason", "")).strip(),
            "timestamp": str((latest_event or {}).get("timestamp", "")).strip(),
            "events_path": GOVERNANCE_EVENTS_PATH.as_posix(),
            "decision_package_path": relative(OPERATING_DECISION_PACKAGE_PATH),
            "trace_path": relative(DECISION_TRACE_PATH),
        },
        "status": "approved" if governance_status in APPROVED_STATUSES else "pending",
        "approval_required": True,
        "generated_at": _utc_timestamp(),
    }


def request_platform_justification(
    *,
    authority_record_path: Path | str,
    stage: str,
    classification: dict[str, Any],
    classification_evidence_path: str,
    governance_action_id: str = "",
) -> dict[str, Any]:
    authority_path = Path(authority_record_path)
    record = _load_authority_record(authority_path)
    action_id, latest_event = _resolve_governance_link(governance_action_id)
    payload = _base_artifact_payload(
        authority_record_path=authority_path,
        record=record,
        stage=stage,
        classification=classification,
        classification_evidence_path=classification_evidence_path,
        governance_action_id=action_id,
        latest_event=latest_event,
    )
    artifact_path = _justification_path(authority_path)
    _write_json(artifact_path, payload)
    governance_status = str(payload["governance"]["status"]).strip().lower()
    block_reason = _derive_block_reason(governance_status)
    return {
        "ok": governance_status in APPROVED_STATUSES,
        "status": payload["status"],
        "block_reason": block_reason,
        "artifact_path": artifact_path.as_posix(),
        "governance_action_id": action_id,
        "governance_status": governance_status,
        "classification": payload["classification"],
    }


def validate_platform_justification(
    *,
    authority_record_path: Path | str,
    stage: str,
    classification: dict[str, Any] | None = None,
    classification_evidence_path: str = "",
    governance_action_id: str = "",
) -> dict[str, Any]:
    authority_path = Path(authority_record_path)
    artifact_path = _justification_path(authority_path)
    existing = _load_json(artifact_path, label="platform justification artifact") if artifact_path.exists() else {}
    linked_action_id = str(governance_action_id or existing.get("governance", {}).get("action_id", "")).strip()
    current_classification = dict(classification or {})
    if not current_classification:
        current_classification = {
            "classification": str(existing.get("classification", "")).strip(),
            "protected_matches": list(existing.get("protected_matches", [])),
            "touched_paths": list(existing.get("touched_paths", [])),
            "reasons": list(existing.get("reasons", [])),
        }
    current_evidence_path = str(classification_evidence_path or existing.get("classification_evidence_path", "")).strip()
    return request_platform_justification(
        authority_record_path=authority_path,
        stage=stage,
        classification=current_classification,
        classification_evidence_path=current_evidence_path,
        governance_action_id=linked_action_id,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Create or validate platform-justification artifacts for protected delivery changes.")
    parser.add_argument("command", choices=["request", "validate"])
    parser.add_argument("--authority-record-path", required=True)
    parser.add_argument("--stage", required=True)
    parser.add_argument("--classification-path", required=True)
    parser.add_argument("--governance-action-id", default="")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        classification_payload = _load_json(Path(args.classification_path), label="classification artifact")
        if args.command == "request":
            result = request_platform_justification(
                authority_record_path=args.authority_record_path,
                stage=args.stage,
                classification=classification_payload,
                classification_evidence_path=args.classification_path,
                governance_action_id=args.governance_action_id,
            )
        else:
            result = validate_platform_justification(
                authority_record_path=args.authority_record_path,
                stage=args.stage,
                classification=classification_payload,
                classification_evidence_path=args.classification_path,
                governance_action_id=args.governance_action_id,
            )
    except PlatformJustificationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
