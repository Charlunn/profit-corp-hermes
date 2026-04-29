# Phase 17: Authority and Status Convergence - Pattern Map

**Mapped:** 2026-04-29
**Files analyzed:** 7
**Analogs found:** 7 / 7

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/start_approved_project_delivery.py` | service | event-driven | `scripts/start_approved_project_delivery.py` | exact |
| `scripts/render_approved_delivery_status.py` | utility | transform | `scripts/render_approved_delivery_status.py` | exact |
| `scripts/validate_approved_delivery_pipeline.py` | utility | batch | `scripts/validate_approved_delivery_pipeline.py` | exact |
| `scripts/append_approved_delivery_event.py` | utility | event-driven | `scripts/append_approved_delivery_event.py` | exact |
| `tests/test_project_delivery_pipeline_bootstrap.py` | test | batch | `tests/test_project_delivery_pipeline_bootstrap.py` | exact |
| `tests/test_project_delivery_pipeline_resume.py` | test | batch | `tests/test_project_delivery_pipeline_resume.py` | exact |
| `tests/test_approved_delivery_pipeline_cli.py` | test | batch | `tests/test_approved_delivery_pipeline_cli.py` | exact |

## Pattern Assignments

### `scripts/start_approved_project_delivery.py` (service, event-driven)

**Analog:** `scripts/start_approved_project_delivery.py`

**Imports and governed dependency pattern** (`scripts/start_approved_project_delivery.py:17-33`):
```python
from scripts.approved_delivery_governance import (
    inspect_workspace_changes,
    run_governed_github_repository_action,
    run_governed_github_sync_action,
    run_governed_vercel_deploy_action,
    run_governed_vercel_env_action,
    run_governed_vercel_link_action,
)
from scripts.github_delivery_common import prepare_github_repository as github_prepare_repository
from scripts.github_delivery_common import sync_workspace_to_github
from scripts.instantiate_template_project import build_metadata, instantiate_workspace, resolve_template_source
from scripts.request_platform_justification import validate_platform_justification
from scripts.start_delivery_run import initialize_delivery_run
from scripts.template_contract_common import build_identity_payload, load_registry, require_asset
from scripts.vercel_delivery_common import apply_env_contract as vercel_apply_env_contract
from scripts.vercel_delivery_common import deploy_to_vercel
from scripts.vercel_delivery_common import link_vercel_project as vercel_link_project
```
Copy this import shape and dependency style for any new authority-layer orchestration logic. It keeps the CLI/orchestrator thin and pushes external side effects into helpers.

**Authority-first current-state mutation pattern** (`scripts/start_approved_project_delivery.py:543-582`):
```python
def update_pipeline_state(
    record: dict[str, Any],
    *,
    stage: str,
    status: str,
    block_reason: str | None = None,
    workspace_path: str | None = None,
    evidence_path: str | None = None,
    resume_from_stage: str | None = None,
    delivery_run_id: str | None = None,
    final_handoff_path: str | None = None,
) -> None:
    pipeline = record.setdefault("pipeline", {})
    artifacts = record.setdefault("artifacts", {})
    shipping = record.setdefault("shipping", {})
    github = shipping.setdefault("github", {})
    vercel = shipping.setdefault("vercel", {})
    record.setdefault("final_handoff", {})
    pipeline["stage"] = stage
    pipeline["status"] = status
    pipeline["block_reason"] = block_reason
    if workspace_path is not None:
        pipeline["workspace_path"] = workspace_path
        artifacts["workspace_path"] = workspace_path
        record["workspace_path"] = workspace_path
    if evidence_path is not None:
        pipeline["evidence_path"] = evidence_path
    if resume_from_stage is not None:
        pipeline["resume_from_stage"] = resume_from_stage
    if delivery_run_id is not None:
        pipeline["delivery_run_id"] = delivery_run_id
        github.setdefault("delivery_run_id", delivery_run_id)
    if final_handoff_path is not None:
        pipeline["final_handoff_path"] = final_handoff_path
        artifacts["final_handoff_path"] = final_handoff_path
        record["final_handoff"] = {
            "path": final_handoff_path,
            "link": final_handoff_path,
        }
```
This is the primary Phase 17 pattern: write the canonical snapshot into `record` first, across all mirrored fields that operator surfaces and validators depend on.

**Persist-then-render pattern** (`scripts/start_approved_project_delivery.py:584-588`):
```python
def persist_and_render(authority_path: Path, record: dict[str, Any]) -> None:
    project_dir, _, _ = record_paths(authority_path, record)
    write_json(authority_path, record)
    render_pipeline_status(project_dir)
```
Any new convergence logic should preserve this order: authoritative JSON first, derived markdown second.

**Append-only event emission pattern** (`scripts/start_approved_project_delivery.py:503-540`, `590-602`):
```python
def make_event(
    *,
    record: dict[str, Any],
    authority_path: Path,
    stage: str,
    status: str,
    action: str,
    outcome: str,
    artifact: str,
    timestamp: str,
    workspace_path: str = "",
    delivery_run_id: str = "",
    block_reason: str = "",
    evidence_path: str = "",
    resume_from_stage: str = "",
    final_handoff_path: str = "",
) -> dict[str, Any]:
    identity = dict(record.get("project_identity", {}))
    artifacts = dict(record.get("artifacts", {}))
    shipping = dict(record.get("shipping", {}))
    return {
        "project_slug": str(identity.get("project_slug", "")).strip(),
        "stage": stage,
        "status": status,
        "action": action,
        "timestamp": timestamp,
        "outcome": outcome,
        "authority_record_path": authority_path.as_posix(),
        "brief_path": str(artifacts.get("delivery_brief_path", "")).strip(),
        "workspace_path": workspace_path,
        "delivery_run_id": delivery_run_id,
        "artifact": artifact,
        "block_reason": block_reason,
        "evidence_path": evidence_path,
        "resume_from_stage": resume_from_stage,
        "final_handoff_path": final_handoff_path,
        "shipping": shipping,
    }


def append_next_pipeline_event(project_dir: Path, event: dict[str, Any]) -> None:
    path = project_dir / "approved-delivery-events.jsonl"
    if path.exists():
        last_line = ""
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                last_line = line
        if last_line:
            last_event = json.loads(last_line)
            latest_timestamp = str(last_event.get("timestamp", "")).strip()
            if latest_timestamp and event["timestamp"] <= latest_timestamp:
                event["timestamp"] = latest_timestamp
    append_pipeline_event(project_dir, event)
```
For Phase 17, new historical visibility should be added as new event fields or events, not by mutating old events.

**Blocked-state persistence pattern** (`scripts/start_approved_project_delivery.py:884-933`):
```python
def block_pipeline(
    authority_path: Path,
    record: dict[str, Any],
    *,
    stage: str,
    block_reason: str,
    evidence_path: str,
    message: str,
    workspace_path: str = "",
    delivery_run_id: str = "",
    timestamp: str = "2026-04-27T08:35:00Z",
) -> dict[str, Any]:
    project_dir, _, _ = record_paths(authority_path, record)
    update_pipeline_state(
        record,
        stage=stage,
        status="blocked",
        block_reason=block_reason,
        workspace_path=workspace_path or record.get("pipeline", {}).get("workspace_path", ""),
        evidence_path=evidence_path,
        resume_from_stage=stage,
        delivery_run_id=delivery_run_id or record.get("pipeline", {}).get("delivery_run_id", ""),
    )
    append_next_pipeline_event(
        project_dir,
        make_event(
            record=record,
            authority_path=authority_path,
            stage=stage,
            status="blocked",
            action="stage_blocked",
            outcome="blocked",
            artifact=evidence_path,
            timestamp=timestamp,
            workspace_path=record.get("pipeline", {}).get("workspace_path", ""),
            delivery_run_id=record.get("pipeline", {}).get("delivery_run_id", ""),
            block_reason=block_reason,
            evidence_path=evidence_path,
            resume_from_stage=stage,
        ),
    )
    persist_and_render(authority_path, record)
```
Reuse this exact three-surface update sequence for any new blocked or recovery state: authority snapshot, event stream, derived status.

**Resume-with-persisted-state pattern** (`scripts/start_approved_project_delivery.py:1531-1547`):
```python
def resume_approved_project_delivery(authority_record_path: Path | str, *, workspace_root: Path | None = None) -> dict[str, Any]:
    authority_path = Path(authority_record_path)
    record = load_json(authority_path)
    pipeline = dict(record.get("pipeline", {}))
    stage = str(pipeline.get("resume_from_stage", pipeline.get("stage", "approval"))).strip() or "approval"
    status = str(pipeline.get("status", "")).strip()
    if str(pipeline.get("stage", "")).strip() == "handoff" and status == "completed":
        final_path = str(pipeline.get("final_handoff_path", record.get("artifacts", {}).get("final_handoff_path", ""))).strip()
        if final_path and Path(final_path).exists():
            return {
                "ok": True,
                "stage": "handoff",
                "status": "completed",
                "final_handoff_path": final_path,
            }
    return run_pipeline_from_stage(authority_path, record, start_stage=stage, workspace_root=workspace_root)
```
Phase 17 should keep resume logic rooted in persisted authority metadata, never in markdown parsing.

**Historical-vs-current truth cleanup pattern** (`scripts/start_approved_project_delivery.py:860-881`, `1324-1366`):
```python
def _remove_authoritative_vercel_success_fields(vercel: dict[str, Any]) -> None:
    for key in [
        "project_id",
        "project_name",
        "project_url",
        "team_scope",
        "linked",
        "auth_source",
        "auth_source_details",
        "env_contract",
        "env_contract_path",
        "env_audit_path",
        "required_env",
        "deploy_url",
        "deploy_status",
        "deploy_evidence_path",
        "deploy_audit_path",
        "deployment_url",
        "deployment_status",
        "deployment_evidence_path",
    ]:
        vercel.pop(key, None)

...
vercel_record = record.setdefault("shipping", {}).setdefault("vercel", {})
_remove_authoritative_vercel_success_fields(vercel_record)
append_next_pipeline_event(... stage="vercel_linkage", action="vercel_linkage_pending" ...)
update_pipeline_state(record, stage="vercel_linkage", status="ready", ...)
persist_and_render(authority_path, record)
```
This is the clearest convergence pattern for Phase 17: preserve old history in events, but actively clear stale current-state success metadata before a later stage re-establishes authoritative truth.

### `scripts/render_approved_delivery_status.py` (utility, transform)

**Analog:** `scripts/render_approved_delivery_status.py`

**Current-state fallback pattern** (`scripts/render_approved_delivery_status.py:105-125`):
```python
def build_status_markdown(events: list[dict[str, Any]], record: dict[str, Any], project_dir: Path) -> str:
    latest = events[-1] if events else {}
    artifacts = record.get("artifacts", {}) if isinstance(record.get("artifacts"), dict) else {}
    pipeline = record.get("pipeline", {}) if isinstance(record.get("pipeline"), dict) else {}
    identity = record.get("project_identity", {}) if isinstance(record.get("project_identity"), dict) else {}
    approval = record.get("approval", {}) if isinstance(record.get("approval"), dict) else {}
    shipping = latest.get("shipping", {}) if isinstance(latest.get("shipping"), dict) else {}
    if not shipping and isinstance(record.get("shipping"), dict):
        shipping = record.get("shipping", {})
    github = shipping.get("github", {}) if isinstance(shipping.get("github"), dict) else {}
    vercel = shipping.get("vercel", {}) if isinstance(shipping.get("vercel"), dict) else {}
    ...
    workspace_path = first_nonempty(latest.get("workspace_path"), get_nested(pipeline, "workspace_path"), artifacts.get("workspace_path"), record.get("workspace_path"))
    final_handoff_path = first_nonempty(latest.get("final_handoff_path"), get_nested(pipeline, "final_handoff_path"), final_handoff.get("path"), final_handoff.get("link"))
```
Copy this precedence rule when adding new status fields: latest event first for freshest emitted state, then authority record fallbacks.

**History-preserving render pattern** (`scripts/render_approved_delivery_status.py:127-140`, `214-217`):
```python
history_lines = []
for event in events:
    history_lines.append(
        "- "
        f"stage=`{event.get('stage', 'not available')}` "
        f"status=`{event.get('status', 'not available')}` "
        f"outcome=`{event.get('outcome', 'not available')}` "
        f"block_reason=`{event.get('block_reason', 'not available')}` "
        f"artifact=`{event.get('artifact', 'not available')}` "
        f"evidence=`{event.get('evidence_path', 'not available')}` "
        f"handoff=`{event.get('final_handoff_path', 'not available')}`"
    )
...
"## Event History",
*(history_lines or ["- stage=`not available` status=`not available` outcome=`not available` block_reason=`not available` artifact=`not available` evidence=`not available` handoff=`not available`"]),
"",
"This latest view is derived from the append-only approved delivery event stream.",
```
Any Phase 17 status additions should preserve this distinction: one latest-view summary plus an explicit event-history section.

**Operator action synthesis pattern** (`scripts/render_approved_delivery_status.py:82-102`):
```python
def summarize_action_required(latest: dict[str, Any], record: dict[str, Any], github: dict[str, Any], vercel: dict[str, Any], protected_change: dict[str, Any], justification: dict[str, Any]) -> list[str]:
    lines: list[str] = []
    latest_status = str(latest.get("status", "")).strip().lower()
    latest_outcome = str(latest.get("outcome", "")).strip().lower()
    block_reason = first_nonempty(latest.get("block_reason"), get_nested(record, "pipeline", "block_reason"))
    evidence_path = first_nonempty(latest.get("evidence_path"), get_nested(record, "pipeline", "evidence_path"))
    if latest_status == "blocked" or latest_outcome in {"blocked", "failed"}:
        lines.append(f"- Investigate latest blocked/failed stage before retrying: `{block_reason or 'reason not available'}`")
    if evidence_path:
        lines.append(f"- Review evidence first: `{evidence_path}`")
    ...
    if not lines:
        lines.append("- No immediate operator action required; governed delivery surface is coherent.")
    return lines
```
Use this style when exposing convergence mismatches: derive operator guidance from canonical machine-readable fields.

**Write-both-surfaces pattern** (`scripts/render_approved_delivery_status.py:222-233`):
```python
def render_approved_delivery_status(project_dir: Path) -> str:
    project_dir = Path(project_dir)
    record = load_json(project_dir / APPROVED_RECORD_NAME)
    events = load_events(project_dir / EVENTS_FILE_NAME)
    markdown = build_status_markdown(events, record, project_dir)
    status_path = project_dir / STATUS_FILE_NAME
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(markdown, encoding="utf-8")
    final_review_path = project_dir / "FINAL_OPERATOR_REVIEW.md"
    final_review_path.parent.mkdir(parents=True, exist_ok=True)
    final_review_path.write_text(markdown, encoding="utf-8")
    return markdown
```
Phase 17 changes that affect operator-facing truth must keep `DELIVERY_PIPELINE_STATUS.md` and `FINAL_OPERATOR_REVIEW.md` synchronized from the same render pass.

### `scripts/validate_approved_delivery_pipeline.py` (utility, batch)

**Analog:** `scripts/validate_approved_delivery_pipeline.py`

**Resolver helper pattern** (`scripts/validate_approved_delivery_pipeline.py:111-178`):
```python
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
        raise ApprovedDeliveryPipelineValidationError(f"workspace path not found: {workspace.as_posix()}")
    return workspace

...

def resolve_final_handoff_path(record: dict[str, Any], workspace: Path, *, blocked_context: bool = False) -> Path:
    final_handoff_path = first_nonempty(
        get_nested(record, "pipeline", "final_handoff_path"),
        get_nested(record, "artifacts", "final_handoff_path"),
        get_nested(record, "final_handoff", "path"),
        get_nested(record, "final_handoff", "link"),
    )
```
Any new field added in Phase 17 should get a dedicated resolver like this, with explicit precedence and failure messages.

**Cross-surface blocked visibility pattern** (`scripts/validate_approved_delivery_pipeline.py:198-222`):
```python
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
    ...
    if Path(evidence_path).name.lower() not in lowered and evidence_path.lower() not in lowered:
        raise ApprovedDeliveryPipelineValidationError("status view missing blocked prerequisite evidence link")
```
This is the Phase 17 validation shape for historical/current convergence: if a blocked condition ever existed, operator surfaces must still link to it.

**External shipping linkage validation pattern** (`scripts/validate_approved_delivery_pipeline.py:224-301`):
```python
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
    ...

def validate_vercel_linkage(record: dict[str, Any], status_text: str) -> None:
    vercel = get_nested(record, "shipping", "vercel")
    if not isinstance(vercel, dict) or not vercel:
        return
    ...
    if has_link_metadata and not has_link_success:
        raise ApprovedDeliveryPipelineValidationError(
            "approved-project authority record has Vercel linkage metadata without authoritative env contract evidence"
        )
```
Use this exact pattern for any new authoritative state: if current snapshot claims success metadata, validator must require corresponding evidence and status visibility.

**Top-level convergence check pattern** (`scripts/validate_approved_delivery_pipeline.py:348-401`):
```python
def validate_approved_delivery_pipeline(approved_project_path: Path) -> dict[str, Any]:
    project_dir = Path(approved_project_path)
    record = load_json(project_dir / APPROVED_RECORD_NAME, "approved-project authority record")
    load_text(project_dir / BRIEF_NAME, "approved-project brief")
    events = load_jsonl(project_dir / EVENTS_NAME, "approved delivery events")
    status_text = load_text(project_dir / STATUS_NAME, "delivery pipeline status")
    ...
    final_handoff_path = resolve_final_handoff_path(record, workspace, blocked_context=has_blocked_state)
    ...
    if event_final_handoff_path.resolve() != final_handoff_path.resolve():
        raise ApprovedDeliveryPipelineValidationError("final handoff path mismatch between authority record and handoff event")
    ...
    validate_status_markdown(status_text, workspace, final_handoff_path)
    validate_final_review(record, final_review_path, final_review_text)
    validate_github_linkage(record, status_text + "\n" + final_review_text)
    validate_vercel_linkage(record, status_text + "\n" + final_review_text)
    validate_blocked_prerequisite_visibility(record, events, status_text + "\n" + final_review_text)
```
Phase 17 work should extend this validator rather than inventing a second checker.

### `scripts/append_approved_delivery_event.py` (utility, event-driven)

**Analog:** `scripts/append_approved_delivery_event.py`

**Strict event schema pattern** (`scripts/append_approved_delivery_event.py:13-47`):
```python
REQUIRED_EVENT_FIELDS = (
    "project_slug",
    "stage",
    "status",
    "action",
    "timestamp",
    "outcome",
    "authority_record_path",
    "brief_path",
    "workspace_path",
    "delivery_run_id",
    "artifact",
    "block_reason",
    "evidence_path",
    "resume_from_stage",
    "final_handoff_path",
)
OPTIONAL_OBJECT_FIELDS = (
    "shipping",
)
ALLOWED_STAGES = {
    "approval",
    "brief_generation",
    "workspace_instantiation",
    "conformance",
    "delivery_run_bootstrap",
    "github_repository",
    "github_sync",
    "vercel_linkage",
    "vercel_deploy",
    "handoff",
}
ALLOWED_STATUSES = {"ready", "blocked", "completed", "running", "failed"}
ALLOWED_OUTCOMES = {"pass", "blocked", "running", "success", "failed"}
```
If Phase 17 needs extra event detail, extend this schema centrally and keep it explicit.

**Validation and monotonic append pattern** (`scripts/append_approved_delivery_event.py:83-120`):
```python
def validate_event(event: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_EVENT_FIELDS if field not in event]
    if missing:
        raise ApprovedDeliveryEventError(f"approved delivery event missing required fields: {', '.join(missing)}")
    ...
    if event["stage"] not in ALLOWED_STAGES:
        raise ApprovedDeliveryEventError(f"unsupported approved delivery stage: {event['stage']}")
    ...

def append_approved_delivery_event(project_dir: Path, event: dict[str, Any]) -> None:
    project_dir = Path(project_dir)
    validate_event(event)
    path = events_path_for(project_dir)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_events(path)
    if existing:
        latest_timestamp = str(existing[-1].get("timestamp", ""))
        if event["timestamp"] < latest_timestamp:
            raise ApprovedDeliveryEventError("approved delivery events must append in nondecreasing timestamp order")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
```
Do not add side-channel event writers. All history changes should go through this function.

### `tests/test_project_delivery_pipeline_bootstrap.py` (test, batch)

**Analog:** `tests/test_project_delivery_pipeline_bootstrap.py`

**Dynamic module load + temp fixture pattern** (`tests/test_project_delivery_pipeline_bootstrap.py:29-37`, `46-112`):
```python
def load_module(module_name: str, script_path: Path):
    if not script_path.exists():
        raise AssertionError(f"expected script to exist: {script_path}")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

...

def create_project_fixture(self, *, custom_approved_root: bool = False) -> tuple[Path, Path, Path, Path]:
    root = Path(tempfile.mkdtemp(prefix="approved-delivery-bootstrap-"))
    ...
    authority_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return root, project_dir, authority_path, workspace_root
```
Follow this pattern for new script-level unit tests instead of spinning up subprocesses unless CLI behavior itself is under test.

**Happy-path convergence assertions** (`tests/test_project_delivery_pipeline_bootstrap.py:296-381`):
```python
self.assertEqual(updated["pipeline"]["stage"], "vercel_linkage")
self.assertEqual(updated["pipeline"]["status"], "ready")
self.assertEqual(updated["pipeline"]["workspace_path"], workspace.as_posix())
self.assertEqual(updated["pipeline"]["delivery_run_id"], "delivery-lead-capture-copilot-001")
...
self.assert_event_stages(events, PIPELINE_STAGES[:-2])
...
vercel_shipping = updated.get("shipping", {}).get("vercel", {})
self.assertEqual(vercel_shipping, {}, "github sync must not prewrite authoritative Vercel metadata")
pending_event = events[-1]
self.assertEqual(pending_event["stage"], "vercel_linkage")
pending_shipping_vercel = pending_event.get("shipping", {}).get("vercel", {})
self.assertEqual(pending_shipping_vercel, {}, "pending Vercel event must not claim linked project metadata")
```
These are the most important reuse assertions for Phase 17: current truth must be coherent and must not claim downstream success early.

**Blocked-state multi-surface assertions** (`tests/test_project_delivery_pipeline_bootstrap.py:383-520`):
```python
self.assertFalse(result["ok"], msg=result)
self.assertEqual(result["status"], "blocked")
self.assertEqual(result["stage"], case["expected_stage"])
self.assertEqual(result["block_reason"], case["expected_reason"])
updated = self.read_json(authority_path)
self.assertEqual(updated["pipeline"]["status"], "blocked")
self.assertEqual(updated["pipeline"]["stage"], case["expected_stage"])
self.assertEqual(updated["pipeline"]["block_reason"], case["expected_reason"])
self.assertEqual(updated["pipeline"]["resume_from_stage"], case["expected_stage"])
self.assertEqual(updated["pipeline"]["evidence_path"], expected_evidence)

events = self.read_events(project_dir)
self.assertEqual(events[-1]["outcome"], "blocked")
self.assertEqual(events[-1]["stage"], case["expected_stage"])
self.assertEqual(events[-1]["block_reason"], case["expected_reason"])
self.assertEqual(events[-1]["evidence_path"], expected_evidence)

status_text = (project_dir / "DELIVERY_PIPELINE_STATUS.md").read_text(encoding="utf-8")
self.assertIn(case["expected_stage"], status_text)
self.assertIn(case["expected_reason"], status_text)
self.assertIn(expected_evidence, status_text)
```
New Phase 17 tests should keep this three-surface assertion style: authority record, event stream, derived markdown.

### `tests/test_project_delivery_pipeline_resume.py` (test, batch)

**Analog:** `tests/test_project_delivery_pipeline_resume.py`

**Resume fixture pattern** (`tests/test_project_delivery_pipeline_resume.py:30-123`):
```python
def create_resume_fixture(self, *, stage: str, status: str = "blocked") -> tuple[Path, Path, Path, Path]:
    root = Path(tempfile.mkdtemp(prefix="approved-delivery-resume-"))
    ...
    authority = {
        ...
        "pipeline": {
            "stage": stage,
            "status": status,
            "block_reason": "resume_required" if status == "blocked" else None,
            "resume_from_stage": stage,
            "workspace_path": workspace.as_posix(),
        },
        ...
    }
```
Use this to set up deterministic persisted-state recovery tests.

**Resume without replaying completed work pattern** (`tests/test_project_delivery_pipeline_resume.py:435-459`):
```python
result = start_module.resume_approved_project_delivery(authority_path)
self.assertTrue(result["ok"], msg=result)
self.assertEqual(result["stage"], "handoff")
self.assertEqual(result["status"], "completed")
instantiate_mock.assert_not_called()
conformance_mock.assert_not_called()
start_run_mock.assert_not_called()
events = self.read_events(project_dir)
self.assertEqual(events, [], "post-handoff resume should not append duplicate events")
```
Phase 17 changes to convergence should preserve idempotent resume semantics.

**Overwrite stale current-state metadata pattern** (`tests/test_project_delivery_pipeline_resume.py:349-434`):
```python
authority["shipping"] = {
    ...
    "vercel": {
        "project_id": "stale_project",
        "project_name": "stale-project-prod",
        "project_url": "https://vercel.com/old-team/stale-project-prod",
        "team_scope": "old-team",
        ...
        "deploy_status": "failed",
        ...
    },
}
...
self.assertEqual(vercel["project_id"], "prj_current")
self.assertEqual(vercel["project_name"], "lead-capture-copilot-prod")
self.assertEqual(vercel["project_url"], "https://vercel.com/profit-corp/lead-capture-copilot-prod")
self.assertEqual(vercel["team_scope"], "profit-corp")
...
self.assertNotEqual(vercel["project_name"], "stale-project-prod")
self.assertNotEqual(vercel["team_scope"], "old-team")
```
This is the strongest test analog for Phase 17’s “current truth beats stale truth” rule.

### `tests/test_approved_delivery_pipeline_cli.py` (test, batch)

**Analog:** `tests/test_approved_delivery_pipeline_cli.py`

**CLI wrapper and validator subprocess pattern** (`tests/test_approved_delivery_pipeline_cli.py:317-330`):
```python
def run_shell(self, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [BASH_EXE, str(COMMANDS_SH), *args],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
    )


def run_validator(self, approved_project: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(VALIDATOR), "--approved-project-path", str(approved_project)],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
    )
```
Use subprocess tests only when validating entrypoints, help text, and end-to-end CLI behavior.

**Cross-link failure expectation pattern** (`tests/test_approved_delivery_pipeline_cli.py:41-94`):
```python
result = self.run_validator(approved_project)
self.assertNotEqual(result.returncode, 0)
output = result.stdout + result.stderr
self.assertIn("final operator review", output)
self.assertIn("block", output)
self.assertIn("evidence", output)
```
For new convergence rules, prefer asserting on the operator-facing failure language, not only on raw exception types.

**Authoritative-evidence gating pattern** (`tests/test_approved_delivery_pipeline_cli.py:95-165`):
```python
result = self.run_validator(approved_project)
self.assertNotEqual(result.returncode, 0)
self.assertIn("env contract", (result.stdout + result.stderr).lower())
```
Re-use this when Phase 17 adds new “metadata exists but authority evidence is missing” checks.

**End-to-end agreement pattern** (`tests/test_approved_delivery_pipeline_cli.py:166-303`):
```python
result = self.run_validator(approved_project)
self.assertEqual(result.returncode, 0, result.stderr)
self.assertIn("validated approved delivery pipeline", result.stdout)
self.assertIn("handoff", result.stdout)
```
New CLI coverage should keep full agreement among authority record, workspace artifacts, events, status markdown, and final review.

## Shared Patterns

### Authority-first writes
**Source:** `scripts/start_approved_project_delivery.py:543-588`
**Apply to:** `scripts/start_approved_project_delivery.py`, `scripts/render_approved_delivery_status.py`, `scripts/validate_approved_delivery_pipeline.py`
```python
update_pipeline_state(...)
write_json(authority_path, record)
render_pipeline_status(project_dir)
```
Rule: machine-readable authority state is primary; rendered status is derived.

### Append-only history with monotonic timestamps
**Source:** `scripts/append_approved_delivery_event.py:109-120`, `scripts/start_approved_project_delivery.py:590-602`
**Apply to:** event emission and any new recovery/history behavior
```python
if existing:
    latest_timestamp = str(existing[-1].get("timestamp", ""))
    if event["timestamp"] < latest_timestamp:
        raise ApprovedDeliveryEventError("approved delivery events must append in nondecreasing timestamp order")
```
Rule: never rewrite or delete old approved-delivery events.

### Historical-vs-current truth separation
**Source:** `scripts/render_approved_delivery_status.py:105-125`, `scripts/start_approved_project_delivery.py:860-881`
**Apply to:** status rendering, stale metadata cleanup, recovery
```python
latest = events[-1] if events else {}
...
if not shipping and isinstance(record.get("shipping"), dict):
    shipping = record.get("shipping", {})
...
_remove_authoritative_vercel_success_fields(vercel_record)
```
Rule: event history retains prior facts; current authority snapshot must reflect only presently authoritative state.

### Cross-surface blocked-state visibility
**Source:** `scripts/validate_approved_delivery_pipeline.py:198-222`; `tests/test_project_delivery_pipeline_bootstrap.py:500-520`
**Apply to:** blocked resume paths, status/review rendering, validator additions
```python
self.assertEqual(updated["pipeline"]["block_reason"], case["expected_reason"])
self.assertEqual(events[-1]["block_reason"], case["expected_reason"])
self.assertIn(case["expected_reason"], status_text)
```
Rule: if the pipeline blocks, the reason and evidence link must survive in authority, events, and operator markdown.

### Governed external action wrapper
**Source:** `scripts/approved_delivery_governance.py:454-489`
**Apply to:** GitHub/Vercel or other credentialed actions touched by Phase 17
```python
def run_governed_action(*, action, authority_record_path, stage, helper: Helper, **kwargs):
    normalized_action = _normalize_action(action)
    authority_path = Path(authority_record_path)
    record = _load_record(authority_path)
    timestamp = _utc_timestamp()
    project_dir = _project_dir_for(authority_path)

    result = dict(helper(action=normalized_action, authority_record_path=authority_path, stage=stage, **kwargs) or {})
    ...
    audit_path = _write_json(_audit_path(project_dir, normalized_action), audit_payload)
    _append_event(...)
```
Rule: credentialed side effects produce both audit artifacts and approved-delivery events.

### Test style for convergence work
**Source:** `tests/test_project_delivery_pipeline_bootstrap.py`, `tests/test_project_delivery_pipeline_resume.py`, `tests/test_approved_delivery_pipeline_cli.py`
**Apply to:** all Phase 17 tests
```python
self.assertEqual(updated["pipeline"][...], ...)
self.assertEqual(events[-1][...], ...)
self.assertIn(..., status_text)
```
Rule: verify all relevant surfaces, not just one helper’s return value.

## No Analog Found

None. Phase 17’s target files already have direct, high-quality analogs in the approved-delivery pipeline and its Phase 9 workspace-local precursor.

## Metadata

**Analog search scope:** `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts`, `C:\Users\42236\Desktop\dev\profit-corp-hermes\tests`, `C:\Users\42236\Desktop\dev\profit-corp-hermes\CLAUDE.md`, `C:\Users\42236\Desktop\dev\profit-corp-hermes\.claude\skills\ui-ux-pro-max\SKILL.md`

**Files scanned:** 11 relevant analog/source files read for pattern extraction
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\start_approved_project_delivery.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\render_approved_delivery_status.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\validate_approved_delivery_pipeline.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\append_approved_delivery_event.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\approved_delivery_governance.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\append_delivery_event.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\render_delivery_status.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\validate_delivery_handoff.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\start_delivery_run.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\tests\test_project_delivery_pipeline_bootstrap.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\tests\test_project_delivery_pipeline_resume.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\tests\test_approved_delivery_pipeline_cli.py`

**Pattern extraction date:** 2026-04-29
