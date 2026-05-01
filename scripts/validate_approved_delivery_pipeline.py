#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.validate_delivery_handoff import require_in_order


APPROVED_RECORD_NAME = "APPROVED_PROJECT.json"
BRIEF_NAME = "PROJECT_BRIEF.md"
EVENTS_NAME = "approved-delivery-events.jsonl"
STATUS_NAME = "DELIVERY_PIPELINE_STATUS.md"
FINAL_REVIEW_NAME = "FINAL_OPERATOR_REVIEW.md"
FINAL_DELIVERY_RELATIVE = ".hermes/FINAL_DELIVERY.md"
MANIFEST_RELATIVE = ".hermes/delivery-run-manifest.json"
CONFORMANCE_CANDIDATES = (
    ".hermes/template-conformance.json",
    ".hermes/conformance-report.md",
)
STATUS_REQUIRED_LINES = [
    "Authority",
    "Workspace",
    "Final handoff",
    "Final operator review",
    "Blocked prerequisite",
    "Protected change",
    "Platform justification",
]
SPECIALIST_STAGE_ORDER = [
    "design",
    "development",
    "testing",
    "git_versioning",
    "release_readiness",
]


class ApprovedDeliveryPipelineValidationError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Validate the approved-project authority bundle through final delivery handoff cross-links."
    )
    parser.add_argument(
        "--approved-project-path",
        required=True,
        help="Path to assets/shared/approved-projects/<project>.",
    )
    return parser.parse_args()


def load_text(path: Path, label: str) -> str:
    if not path.exists():
        raise ApprovedDeliveryPipelineValidationError(f"{label} not found: {path.as_posix()}")
    content = path.read_text(encoding="utf-8")
    if not content.strip():
        raise ApprovedDeliveryPipelineValidationError(f"{label} is empty: {path.as_posix()}")
    return content


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(load_text(path, label))
    except json.JSONDecodeError as exc:
        raise ApprovedDeliveryPipelineValidationError(f"invalid JSON in {label}: {path.as_posix()}") from exc
    if not isinstance(payload, dict):
        raise ApprovedDeliveryPipelineValidationError(f"{label} must be a JSON object: {path.as_posix()}")
    return payload


def load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(load_text(path, label).splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ApprovedDeliveryPipelineValidationError(
                f"invalid JSONL in {label} at line {line_number}: {path.as_posix()}"
            ) from exc
        if not isinstance(payload, dict):
            raise ApprovedDeliveryPipelineValidationError(
                f"{label} line {line_number} must be a JSON object: {path.as_posix()}"
            )
        events.append(payload)
    if not events:
        raise ApprovedDeliveryPipelineValidationError(f"{label} has no events: {path.as_posix()}")
    return events


def first_nonempty(*values: Any) -> str:
    for value in values:
        if isinstance(value, str) and value.strip():
            return value.strip()
    return ""


def get_nested(payload: dict[str, Any], *keys: str) -> Any:
    current: Any = payload
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def resolve_workspace_path(record: dict[str, Any]) -> Path:
    workspace_path = first_nonempty(
        get_nested(record, "pipeline", "workspace_path"),
        get_nested(record, "artifacts", "workspace_path"),
        record.get("workspace_path"),
    )
    if not workspace_path:
        raise ApprovedDeliveryPipelineValidationError("approved-project authority record missing workspace path")
    workspace = Path(workspace_path)
    if not workspace.exists():
        status = first_nonempty(get_nested(record, "pipeline", "status"))
        final_handoff_path = first_nonempty(
            get_nested(record, "pipeline", "final_handoff_path"),
            get_nested(record, "artifacts", "final_handoff_path"),
            get_nested(record, "final_handoff", "path"),
            get_nested(record, "final_handoff", "link"),
        )
        if status == "completed" and final_handoff_path and Path(final_handoff_path).exists():
            return workspace
        raise ApprovedDeliveryPipelineValidationError(f"workspace path not found: {workspace.as_posix()}")
    return workspace


def resolve_manifest_path(record: dict[str, Any], workspace: Path) -> Path:
    raw = first_nonempty(
        get_nested(record, "artifacts", "delivery_manifest_path"),
        record.get("phase9_delivery_run_manifest_path"),
        record.get("phase9_delivery_run_manifest"),
        MANIFEST_RELATIVE,
    )
    manifest_path = Path(raw)
    if not manifest_path.is_absolute():
        manifest_path = workspace / raw
    if not manifest_path.exists():
        pipeline_status = first_nonempty(get_nested(record, "pipeline", "status"))
        if pipeline_status == "completed":
            return manifest_path
        raise ApprovedDeliveryPipelineValidationError(
            f"Phase 9 delivery run manifest missing: {manifest_path.as_posix()}"
        )
    return manifest_path


def resolve_conformance_path(record: dict[str, Any], workspace: Path, project_dir: Path) -> Path:
    raw = first_nonempty(
        get_nested(record, "artifacts", "conformance_evidence_path"),
        record.get("conformance_evidence_path"),
    )
    candidates = [raw] if raw else []
    candidates.extend(CONFORMANCE_CANDIDATES)
    for candidate in candidates:
        candidate_path = Path(candidate)
        if not candidate_path.is_absolute():
            candidate_path = resolve_project_artifact_path(candidate, project_dir) if "approved-projects" in candidate_path.parts else workspace / candidate_path
        if candidate_path.exists():
            return candidate_path
    if first_nonempty(get_nested(record, "pipeline", "status")) == "completed":
        return Path(raw) if raw else workspace / CONFORMANCE_CANDIDATES[0]
    raise ApprovedDeliveryPipelineValidationError("conformance evidence missing from authority record/workspace")


def resolve_final_handoff_path(record: dict[str, Any], workspace: Path, *, blocked_context: bool = False) -> Path:
    final_handoff_path = first_nonempty(
        get_nested(record, "pipeline", "final_handoff_path"),
        get_nested(record, "artifacts", "final_handoff_path"),
        get_nested(record, "final_handoff", "path"),
        get_nested(record, "final_handoff", "link"),
    )
    if not final_handoff_path:
        if blocked_context:
            raise ApprovedDeliveryPipelineValidationError(
                "approved-project authority record missing final handoff path/link while blocked prerequisite evidence is still being tracked"
            )
        raise ApprovedDeliveryPipelineValidationError(
            "approved-project authority record missing final handoff path/link"
        )
    path = Path(final_handoff_path)
    if not path.is_absolute():
        path = workspace / final_handoff_path
    if not path.exists():
        raise ApprovedDeliveryPipelineValidationError(f"final handoff artifact not found: {path.as_posix()}")
    return path


def resolve_project_artifact_path(raw_path: str, project_dir: Path) -> Path:
    path = Path(raw_path)
    if path.is_absolute():
        return path
    parts = list(path.parts)
    if "approved-projects" in parts:
        anchor = parts.index("approved-projects")
        if anchor + 1 < len(parts) and parts[anchor + 1] == project_dir.name:
            suffix = parts[anchor + 2 :]
            return project_dir.joinpath(*suffix) if suffix else project_dir
    return project_dir / path


def resolve_final_review_path(record: dict[str, Any], project_dir: Path, *, blocked_context: bool = False) -> Path:
    raw = first_nonempty(
        get_nested(record, "artifacts", "final_review_path"),
        (project_dir / FINAL_REVIEW_NAME).as_posix(),
    )
    path = resolve_project_artifact_path(raw, project_dir)
    if not path.exists():
        if blocked_context:
            raise ApprovedDeliveryPipelineValidationError(
                f"final operator review artifact missing while block evidence is still active: {path.as_posix()}"
            )
        raise ApprovedDeliveryPipelineValidationError(f"final operator review artifact not found: {path.as_posix()}")
    return path


def validate_specialist_stage_visibility(record: dict[str, Any], events: list[dict[str, Any]], status_text: str, workspace: Path) -> None:
    lowered = status_text.lower()
    manifest_path = resolve_manifest_path(record, workspace)
    if manifest_path.exists():
        manifest = load_json(manifest_path, "delivery run manifest")
        stages = manifest.get("stages", [])
        if not isinstance(stages, list) or len(stages) < len(SPECIALIST_STAGE_ORDER):
            declared_order = []
        else:
            declared_order = [str(stage.get("stage", "")).strip() for stage in stages if isinstance(stage, dict)]
        expected_delivery_order = ["design", "development", "testing", "git versioning", "release readiness"]
        if declared_order and declared_order[: len(expected_delivery_order)] != expected_delivery_order:
            raise ApprovedDeliveryPipelineValidationError("delivery run manifest specialist stage order drifted")

    pipeline = get_nested(record, "pipeline") if isinstance(get_nested(record, "pipeline"), dict) else {}
    current_stage = first_nonempty(get_nested(pipeline, "stage"))
    specialist_events = {str(event.get("stage", "")).strip(): event for event in events if str(event.get("stage", "")).strip() in SPECIALIST_STAGE_ORDER}
    github_seen = any(str(event.get("stage", "")).strip() == "github_repository" for event in events)
    should_enforce = bool(specialist_events)

    for stage in SPECIALIST_STAGE_ORDER:
        if not should_enforce:
            break
        if stage not in specialist_events and (github_seen or current_stage in {stage, "github_repository", "github_sync", "vercel_linkage", "vercel_deploy", "handoff"}):
            raise ApprovedDeliveryPipelineValidationError(f"missing specialist stage event before shipping: {stage}")
        if stage in specialist_events:
            event = specialist_events[stage]
            artifact = first_nonempty(event.get("artifact"))
            if not artifact:
                raise ApprovedDeliveryPipelineValidationError(f"specialist stage missing artifact: {stage}")
            artifact_path = Path(artifact)
            if not artifact_path.is_absolute():
                artifact_path = workspace / artifact
            if artifact_path.exists():
                if artifact_path.name.lower() not in lowered and artifact_path.as_posix().lower() not in lowered:
                    raise ApprovedDeliveryPipelineValidationError(f"status view missing specialist stage artifact linkage: {artifact_path.name}")
            elif first_nonempty(get_nested(record, "pipeline", "status")) != "completed":
                raise ApprovedDeliveryPipelineValidationError(f"specialist stage artifact not found: {artifact_path.as_posix()}")


def validate_blocked_prerequisite_visibility(record: dict[str, Any], events: list[dict[str, Any]], status_text: str) -> None:
    blocked_events = [event for event in events if str(event.get("status", "")).strip() == "blocked"]
    if not blocked_events:
        return
    latest_blocked = blocked_events[-1]
    block_reason = first_nonempty(
        latest_blocked.get("block_reason"),
        get_nested(record, "pipeline", "block_reason"),
        get_nested(record, "latest_blocked_prerequisite", "reason"),
    )
    evidence_path = first_nonempty(
        latest_blocked.get("evidence_path"),
        get_nested(record, "pipeline", "evidence_path"),
        get_nested(record, "latest_blocked_prerequisite", "path"),
    )
    lowered = status_text.lower()
    if not block_reason:
        raise ApprovedDeliveryPipelineValidationError("blocked pipeline state missing persisted block reason")
    if not evidence_path:
        raise ApprovedDeliveryPipelineValidationError("blocked pipeline state missing persisted evidence path")
    if "block" not in lowered:
        raise ApprovedDeliveryPipelineValidationError("status view missing blocked-state summary")
    if Path(evidence_path).name.lower() not in lowered and evidence_path.lower() not in lowered:
        raise ApprovedDeliveryPipelineValidationError("status view missing blocked prerequisite evidence link")


def validate_github_linkage(record: dict[str, Any], status_text: str) -> None:
    github = get_nested(record, "shipping", "github")
    if not isinstance(github, dict):
        return
    required_fields = {
        "repository_mode": "GitHub repository mode",
        "repository_name": "GitHub repository name",
        "repository_url": "GitHub repository URL",
        "default_branch": "GitHub default branch",
        "synced_commit": "GitHub synced commit",
        "sync_evidence_path": "GitHub sync evidence path",
    }
    lowered = status_text.lower()
    for key, label in required_fields.items():
        value = first_nonempty(github.get(key))
        if not value:
            raise ApprovedDeliveryPipelineValidationError(f"approved-project authority record missing {label}")
        if value.lower() not in lowered and Path(value).name.lower() not in lowered:
            raise ApprovedDeliveryPipelineValidationError(f"status view missing {label} linkage")



def validate_vercel_linkage(record: dict[str, Any], status_text: str) -> None:
    vercel = get_nested(record, "shipping", "vercel")
    if not isinstance(vercel, dict) or not vercel:
        return

    lowered = status_text.lower()
    link_evidence = first_nonempty(
        vercel.get("link_evidence_path"),
        vercel.get("env_contract_path"),
        get_nested(vercel, "env_contract", "evidence_path"),
    )
    has_link_metadata = bool(
        first_nonempty(
            vercel.get("project_id"),
            vercel.get("project_name"),
            vercel.get("project_url"),
            vercel.get("team_scope"),
        )
    )
    has_link_success = bool(link_evidence)
    deploy_evidence = first_nonempty(vercel.get("deploy_evidence_path"), vercel.get("deployment_evidence_path"))
    deploy_status = first_nonempty(vercel.get("deploy_status"), vercel.get("deployment_status"))
    has_deploy_success = bool(deploy_evidence)

    if has_link_metadata and not has_link_success:
        raise ApprovedDeliveryPipelineValidationError(
            "approved-project authority record has Vercel linkage metadata without authoritative env contract evidence"
        )

    if has_link_success:
        required_link_fields = {
            "project_name": "Vercel project name",
            "project_url": "Vercel project URL",
            "team_scope": "Vercel team scope",
        }
        for key, label in required_link_fields.items():
            value = first_nonempty(vercel.get(key))
            if not value:
                raise ApprovedDeliveryPipelineValidationError(f"approved-project authority record missing {label}")
            if value.lower() not in lowered and Path(value).name.lower() not in lowered:
                raise ApprovedDeliveryPipelineValidationError(f"status view missing {label} linkage")
        if link_evidence.lower() not in lowered and Path(link_evidence).name.lower() not in lowered:
            raise ApprovedDeliveryPipelineValidationError("status view missing Vercel env contract linkage")

    if has_deploy_success:
        if not deploy_status:
            raise ApprovedDeliveryPipelineValidationError("approved-project authority record missing Vercel deploy status")
        if deploy_status.lower() not in lowered and Path(deploy_status).name.lower() not in lowered:
            raise ApprovedDeliveryPipelineValidationError("status view missing Vercel deploy status linkage")
        deploy_url = first_nonempty(vercel.get("deploy_url"), vercel.get("deployment_url"))
        if not deploy_url:
            raise ApprovedDeliveryPipelineValidationError("approved-project authority record missing Vercel deploy URL")
        if deploy_url.lower() not in lowered and Path(deploy_url).name.lower() not in lowered:
            raise ApprovedDeliveryPipelineValidationError("status view missing Vercel deploy URL linkage")
        if deploy_evidence.lower() not in lowered and Path(deploy_evidence).name.lower() not in lowered:
            raise ApprovedDeliveryPipelineValidationError("status view missing Vercel deploy evidence linkage")


def validate_current_state_precedence(record: dict[str, Any], events: list[dict[str, Any]], status_text: str, final_review_text: str) -> None:
    pipeline = get_nested(record, "pipeline") if isinstance(get_nested(record, "pipeline"), dict) else {}
    status = first_nonempty(get_nested(pipeline, "status"))
    stage = first_nonempty(get_nested(pipeline, "stage"))
    combined = (status_text + "\n" + final_review_text).lower()

    if status == "completed":
        if "pipeline status" in combined and "blocked" in combined.split("pipeline status", 1)[1][:40]:
            raise ApprovedDeliveryPipelineValidationError("status view still presents blocked current state after recovered completion")
        if "handoff status" in combined and "completed" not in combined.split("handoff status", 1)[1][:40]:
            raise ApprovedDeliveryPipelineValidationError("status view missing completed handoff current state")

    if stage and stage.lower() not in combined:
        raise ApprovedDeliveryPipelineValidationError("status view missing current pipeline stage")


def validate_status_markdown(status_text: str, workspace: Path, final_handoff: Path) -> None:
    require_in_order(status_text, ["#", "Final"], STATUS_NAME)
    lowered = status_text.lower()
    for token in STATUS_REQUIRED_LINES:
        if token.lower() not in lowered:
            raise ApprovedDeliveryPipelineValidationError(
                f"{STATUS_NAME} missing required operator linkage token: {token}"
            )
    if workspace.as_posix().lower() not in lowered:
        raise ApprovedDeliveryPipelineValidationError("status view missing workspace path linkage")
    if final_handoff.as_posix().lower() not in lowered:
        raise ApprovedDeliveryPipelineValidationError("status view missing final handoff link")


def latest_successful_handoff_reference(events: list[dict[str, Any]]) -> str:
    for event in reversed(events):
        handoff = first_nonempty(
            event.get("final_handoff_path"),
            get_nested(event, "final_handoff", "path"),
            get_nested(event, "final_handoff", "link"),
        )
        if handoff:
            return handoff
        if str(event.get("stage", "")).strip() == "handoff" and first_nonempty(event.get("artifact")):
            return first_nonempty(event.get("artifact"))
    return ""


def validate_final_review(record: dict[str, Any], final_review_path: Path, review_text: str) -> None:
    lowered = review_text.lower()
    required_tokens = [
        "final operator review",
        "credentialed delivery actions",
    ]
    for token in required_tokens:
        if token not in lowered:
            raise ApprovedDeliveryPipelineValidationError(f"final operator review missing required section: {token}")

    protected_change = get_nested(record, "protected_change") if isinstance(get_nested(record, "protected_change"), dict) else {}
    platform_justification = get_nested(record, "platform_justification") if isinstance(get_nested(record, "platform_justification"), dict) else {}
    latest_blocked = get_nested(record, "latest_blocked_prerequisite") if isinstance(get_nested(record, "latest_blocked_prerequisite"), dict) else {}
    final_handoff = get_nested(record, "final_handoff") if isinstance(get_nested(record, "final_handoff"), dict) else {}

    if get_nested(record, "shipping", "github") and "github" not in lowered:
        raise ApprovedDeliveryPipelineValidationError("final operator review missing GitHub delivery summary")
    if get_nested(record, "shipping", "vercel") and "vercel" not in lowered:
        raise ApprovedDeliveryPipelineValidationError("final operator review missing Vercel delivery summary")


def validate_approved_delivery_pipeline(approved_project_path: Path) -> dict[str, Any]:
    project_dir = Path(approved_project_path)
    record = load_json(project_dir / APPROVED_RECORD_NAME, "approved-project authority record")
    load_text(project_dir / BRIEF_NAME, "approved-project brief")
    events = load_jsonl(project_dir / EVENTS_NAME, "approved delivery events")
    status_text = load_text(project_dir / STATUS_NAME, "delivery pipeline status")

    blocked_events = [event for event in events if str(event.get("status", "")).strip() == "blocked"]
    has_blocked_state = bool(blocked_events)
    final_review_path = resolve_final_review_path(record, project_dir, blocked_context=has_blocked_state)
    final_review_text = load_text(final_review_path, "final operator review")

    workspace = resolve_workspace_path(record)
    conformance_path = resolve_conformance_path(record, workspace, project_dir)
    manifest_path = resolve_manifest_path(record, workspace)
    validate_blocked_prerequisite_visibility(record, events, status_text)
    final_handoff_path = resolve_final_handoff_path(record, workspace, blocked_context=False)

    event_final_handoff = latest_successful_handoff_reference(events)
    if not event_final_handoff:
        pipeline_status = first_nonempty(get_nested(record, "pipeline", "status"))
        if pipeline_status == "completed":
            raise ApprovedDeliveryPipelineValidationError("completed pipeline missing successful final handoff event reference")
    else:
        event_final_handoff_path = Path(event_final_handoff)
        if not event_final_handoff_path.is_absolute():
            event_final_handoff_path = workspace / event_final_handoff
        if event_final_handoff_path.resolve() != final_handoff_path.resolve():
            raise ApprovedDeliveryPipelineValidationError("final handoff path mismatch between authority record and successful event history")

    event_workspace = first_nonempty(
        next(
            (
                event.get("workspace_path")
                for event in reversed(events)
                if first_nonempty(
                    event.get("final_handoff_path"),
                    get_nested(event, "final_handoff", "path"),
                    get_nested(event, "final_handoff", "link"),
                )
            ),
            "",
        ),
        workspace.as_posix(),
    )
    if Path(event_workspace).resolve() != workspace.resolve():
        raise ApprovedDeliveryPipelineValidationError("workspace path mismatch between authority record and handoff event")

    validate_status_markdown(status_text, workspace, final_handoff_path)
    validate_specialist_stage_visibility(record, events, status_text + "\n" + final_review_text, workspace)
    validate_final_review(record, final_review_path, final_review_text)
    validate_current_state_precedence(record, events, status_text, final_review_text)
    validate_github_linkage(record, status_text + "\n" + final_review_text)
    validate_vercel_linkage(record, status_text + "\n" + final_review_text)
    validate_blocked_prerequisite_visibility(record, events, status_text + "\n" + final_review_text)

    terminal_stage = "handoff" if event_final_handoff else first_nonempty(get_nested(record, "pipeline", "stage")) or "handoff"
    return {
        "ok": True,
        "approved_project_path": project_dir.as_posix(),
        "workspace_path": workspace.as_posix(),
        "conformance_evidence_path": conformance_path.as_posix(),
        "delivery_run_manifest_path": manifest_path.as_posix(),
        "final_handoff_path": final_handoff_path.as_posix(),
        "final_review_path": final_review_path.as_posix(),
        "event_count": len(events),
        "terminal_stage": terminal_stage,
    }


def main() -> int:
    args = parse_args()
    try:
        result = validate_approved_delivery_pipeline(Path(args.approved_project_path))
    except ApprovedDeliveryPipelineValidationError as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(
        "validated approved delivery pipeline: "
        f"workspace={result['workspace_path']} handoff={result['final_handoff_path']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
