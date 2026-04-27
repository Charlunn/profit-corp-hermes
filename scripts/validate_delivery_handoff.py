#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


STAGE_HANDOFF_TEMPLATE = ROOT_DIR / "docs" / "skill-governance" / "templates" / "stage-handoff-template-v0.2.md"
FINAL_DELIVERY_TEMPLATE = ROOT_DIR / "docs" / "skill-governance" / "templates" / "final-delivery-template-v0.2.md"
MANIFEST_RELATIVE_PATH = ".hermes/delivery-run-manifest.json"
EVENTS_RELATIVE_PATH = ".hermes/delivery-events.jsonl"
FINAL_DELIVERY_RELATIVE_PATH = ".hermes/FINAL_DELIVERY.md"
REQUIRED_STAGE_HEADINGS = [
    "## 1) Stage Summary",
    "## 2) Outputs Produced",
    "## 3) Evidence Links",
    "## 4) Gate Decision",
    "## 5) Open Risks",
    "## 6) Next Stage Input",
]
REQUIRED_STAGE_METADATA = ["`run_id`", "`role`", "`stage`", "`scope_status`", "`next_stage`"]
REQUIRED_FINAL_HEADINGS = [
    "## 1) End-to-end Summary",
    "## 2) Impact Surface",
    "## 3) Test & Verification Evidence",
    "## 4) Gate Status Snapshot",
    "## 5) Rollback Plan",
    "## 6) Release Recommendation",
]
REQUIRED_FINAL_METADATA = ["`run_id`", "`role`", "`stage`", "`scope_status`"]
REQUIRED_FINAL_EVIDENCE_LABELS = [
    "- UI：",
    "- API：",
    "- DB：",
    "- 权限：",
    "- 日志与观测：",
    "- 主路径验证：",
    "- 失败路径验证：",
    "- 回归验证：",
    "- 证据链接：",
    "- 回滚触发条件：",
    "- 回滚步骤：",
    "- 回滚验证：",
    "- 建议：",
]


class DeliveryHandoffValidationError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Validate delivery handoff artifacts and replay a run from workspace-local artifacts plus events.")
    parser.add_argument("--workspace-path", required=True, help="Path to the generated workspace.")
    return parser.parse_args()


def load_text(path: Path, label: str) -> str:
    if not path.exists():
        raise DeliveryHandoffValidationError(f"{label} not found: {path.as_posix()}")
    content = path.read_text(encoding="utf-8")
    if not content.strip():
        raise DeliveryHandoffValidationError(f"{label} is empty: {path.as_posix()}")
    return content


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(load_text(path, label))
    except json.JSONDecodeError as exc:
        raise DeliveryHandoffValidationError(f"invalid JSON in {label}: {path.as_posix()}") from exc
    if not isinstance(payload, dict):
        raise DeliveryHandoffValidationError(f"{label} must be a JSON object: {path.as_posix()}")
    return payload


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(load_text(path, "delivery events").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DeliveryHandoffValidationError(f"invalid JSONL at line {line_number}: {path.as_posix()}") from exc
        if not isinstance(payload, dict):
            raise DeliveryHandoffValidationError(f"delivery event at line {line_number} must be an object")
        events.append(payload)
    return events


def require_in_order(text: str, headings: list[str], label: str) -> None:
    positions: list[int] = []
    for heading in headings:
        if heading not in text:
            raise DeliveryHandoffValidationError(f"{label} missing required section: {heading}")
        positions.append(text.index(heading))
    if positions != sorted(positions):
        raise DeliveryHandoffValidationError(f"{label} section order drifted")


def require_tokens(text: str, tokens: list[str], label: str) -> None:
    missing = [token for token in tokens if token not in text]
    if missing:
        raise DeliveryHandoffValidationError(f"{label} missing required metadata: {', '.join(missing)}")


def extract_tag_value(text: str, tag: str) -> str:
    marker = f"- `{tag}`:"
    for line in text.splitlines():
        if line.startswith(marker):
            return line.split(":", 1)[1].strip()
    return ""


def validate_stage_handoff(path: Path, *, expected_stage: str, expected_role: str, expected_next_stage: str, run_id: str) -> None:
    label = path.name
    text = load_text(path, label)
    require_in_order(text, REQUIRED_STAGE_HEADINGS, label)
    require_tokens(text, REQUIRED_STAGE_METADATA, label)
    if extract_tag_value(text, "run_id") != run_id:
        raise DeliveryHandoffValidationError(f"{label} run_id mismatch")
    if extract_tag_value(text, "stage") != expected_stage:
        raise DeliveryHandoffValidationError(f"{label} stage mismatch: expected {expected_stage}")
    if extract_tag_value(text, "role") != expected_role:
        raise DeliveryHandoffValidationError(f"{label} role mismatch: expected {expected_role}")
    if extract_tag_value(text, "scope_status") not in {"approved-brief-only", "in-scope", "scope-reopen-requested", "blocked"}:
        raise DeliveryHandoffValidationError(f"{label} scope_status missing approved delivery value")
    if extract_tag_value(text, "next_stage") != expected_next_stage:
        raise DeliveryHandoffValidationError(f"{label} next_stage mismatch: expected {expected_next_stage}")


def validate_final_delivery(path: Path, *, run_id: str) -> None:
    label = path.name
    text = load_text(path, label)
    require_in_order(text, REQUIRED_FINAL_HEADINGS, label)
    require_tokens(text, REQUIRED_FINAL_METADATA, label)
    if extract_tag_value(text, "run_id") != run_id:
        raise DeliveryHandoffValidationError(f"{label} run_id mismatch")
    if extract_tag_value(text, "role") != "release-readiness-specialist":
        raise DeliveryHandoffValidationError(f"{label} role mismatch: expected release-readiness-specialist")
    if extract_tag_value(text, "stage") != "release readiness":
        raise DeliveryHandoffValidationError(f"{label} stage mismatch: expected release readiness")
    missing_labels = [label_text for label_text in REQUIRED_FINAL_EVIDENCE_LABELS if label_text not in text]
    if missing_labels:
        raise DeliveryHandoffValidationError(f"{label} missing final release evidence: {', '.join(missing_labels)}")


def validate_delivery_run(workspace: Path) -> dict[str, Any]:
    workspace = Path(workspace)
    manifest = load_json(workspace / MANIFEST_RELATIVE_PATH, "delivery run manifest")
    events = load_jsonl(workspace / EVENTS_RELATIVE_PATH)
    run_id = str(manifest.get("run_id", "")).strip()
    if not run_id:
        return {"ok": False, "error": "delivery run manifest missing run_id"}

    stages = manifest.get("stages")
    if not isinstance(stages, list) or not stages:
        return {"ok": False, "error": "delivery run manifest missing stages"}

    validated_stage_order: list[str] = []
    try:
        for index, stage_entry in enumerate(stages):
            if not isinstance(stage_entry, dict):
                raise DeliveryHandoffValidationError("delivery run manifest stages must be objects")
            stage = str(stage_entry.get("stage", "")).strip()
            role = str(stage_entry.get("role", "")).strip()
            artifact = str(stage_entry.get("artifact", "")).strip()
            if not stage or not role or not artifact:
                raise DeliveryHandoffValidationError("delivery run manifest stage entry missing stage, role, or artifact")
            next_stage = str(stages[index + 1].get("stage", "none")).strip() if index + 1 < len(stages) else "none"
            validate_stage_handoff(workspace / artifact, expected_stage=stage, expected_role=role, expected_next_stage=next_stage, run_id=run_id)
            matching_events = [event for event in events if event.get("stage") == stage and event.get("role") == role and event.get("artifact") == artifact]
            if not matching_events:
                raise DeliveryHandoffValidationError(f"missing replay event for stage {stage} and artifact {artifact}")
            latest = matching_events[-1]
            if latest.get("action") != "stage_completed":
                raise DeliveryHandoffValidationError(f"stage {stage} missing stage_completed event")
            if latest.get("run_id") != run_id:
                raise DeliveryHandoffValidationError(f"stage {stage} event run_id mismatch")
            validated_stage_order.append(stage)

        validate_final_delivery(workspace / FINAL_DELIVERY_RELATIVE_PATH, run_id=run_id)
        final_events = [event for event in events if event.get("artifact") == FINAL_DELIVERY_RELATIVE_PATH]
        if not final_events:
            raise DeliveryHandoffValidationError("missing final delivery replay event for .hermes/FINAL_DELIVERY.md")
        latest_final = final_events[-1]
        if latest_final.get("action") != "final_delivery_validated":
            raise DeliveryHandoffValidationError("final delivery artifact missing final_delivery_validated event")
        if latest_final.get("run_id") != run_id:
            raise DeliveryHandoffValidationError("final delivery event run_id mismatch")
    except DeliveryHandoffValidationError as exc:
        return {"ok": False, "error": str(exc)}

    return {
        "ok": True,
        "run_id": run_id,
        "validated_stage_order": validated_stage_order,
        "authority_stream": str(manifest.get("authority_stream", EVENTS_RELATIVE_PATH)),
        "final_artifact": FINAL_DELIVERY_RELATIVE_PATH,
    }


def main() -> int:
    args = parse_args()
    result = validate_delivery_run(Path(args.workspace_path))
    if not result["ok"]:
        print(result["error"], file=sys.stderr)
        return 1
    print(f"validated delivery run: {result['run_id']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
