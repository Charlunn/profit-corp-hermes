# Phase 19: Specialist Evidence and UI Artifact Gates - Pattern Map

**Mapped:** 2026-05-04
**Files analyzed:** 6 primary + 1 adjacent renderer
**Analogs found:** 7 / 7

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/start_approved_project_delivery.py` | controller/orchestrator | event-driven | `scripts/start_approved_project_delivery.py` | exact |
| `scripts/validate_delivery_handoff.py` | validator | request-response | `scripts/validate_delivery_handoff.py` | exact |
| `scripts/validate_approved_delivery_pipeline.py` | validator | event-driven | `scripts/validate_approved_delivery_pipeline.py` | exact |
| `scripts/approved_delivery_governance.py` | service/governance | file-I/O | `scripts/approved_delivery_governance.py` | exact |
| `scripts/render_approved_delivery_status.py` | utility/renderer | transform | `scripts/render_approved_delivery_status.py` | exact |
| `tests/test_approved_delivery_pipeline_cli.py` | test | event-driven | `tests/test_approved_delivery_pipeline_cli.py` | exact |
| `.hermes/stage-evidence/*.json` and status/review artifacts | artifact contract | file-I/O | existing `.hermes` + approved-project artifacts | exact |

## Pattern Assignments

### `scripts/start_approved_project_delivery.py` (orchestrator, event-driven)

**Analog:** `scripts/start_approved_project_delivery.py`

**Stage + artifact constants** ([scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:96), [scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:155), [scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:201))
```python
ALLOWED_BLOCK_REASONS = [...]
SPECIALIST_STAGE_CONFIGS = [...]
UI_UX_ARTIFACT_NAME = "ui-ux-design-system.md"
STAGE_EVIDENCE_DIR = ".hermes/stage-evidence"
```
Copy this pattern for any new Phase 19 block reason or artifact contract: add it centrally, then thread it through gate validation and status rendering.

**Handoff markdown contract** ([scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:1781))
```python
headings = REQUIRED_STAGE_HEADINGS
lines = [
    headings[0], f"- `run_id`: {run_id}", f"- `role`: {role}",
    ...
    headings[6], f"- `gate_decision`: {gate_decision}", f"- `reason`: {gate_reason}",
    ...
    headings[8], f"- `next_stage`: {next_stage}",
]
```
Reuse this validator-owned generation approach. Do not invent a second stage handoff shape for new evidence/UI gate failures.

**Structured stage evidence bundle** ([scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:1910))
```python
payload = {
    "run_id": run_id,
    "stage": config["delivery_stage"],
    "pipeline_stage": config["pipeline_stage"],
    "role": config["role"],
    "handoff_path": handoff_path,
    "transcript_path": transcript_path,
    "workspace_change_inventory_path": workspace_change_inventory_path,
    "ui_artifact_path": ui_artifact_path,
    "ui_artifact_summary_path": ui_artifact_summary_path,
    "changed_files": normalize_list(changed_files),
    "evidence_links": normalize_list(evidence_links),
    "verification_evidence": normalize_list(list(verification_evidence or [])),
    "gate": {"decision": gate_decision, "reason": gate_reason},
}
```
Phase 19 should extend this JSON, not create a parallel evidence file.

**Fail-closed evidence bundle validation** ([scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:1945))
```python
if not stage_evidence_path.exists():
    return False, "missing_structured_stage_evidence", ...
if str(payload.get("run_id", "")).strip() != run_id:
    return False, "stage_evidence_run_mismatch", ...
if config["pipeline_stage"] in UI_SPECIALIST_STAGES:
    if not ui_artifact_path: return False, "missing_ui_ux_artifact", ...
    if not ui_summary_path: return False, "missing_ui_ux_summary", ...
if config["pipeline_stage"] == "testing" and not normalize_list(...):
    return False, "missing_testing_verification_evidence", ...
```
This is the exact Phase 19 gate shape: existence, non-empty content, run/stage/path alignment, then stage-specific required evidence.

**UI gate before stage completion + event persistence** ([scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:2291), [scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:2606), [scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:2620))
```python
ui_artifact_path = ensure_ui_ux_preflight(workspace, record, pipeline_stage)
if pipeline_stage in UI_SPECIALIST_STAGES and detect_delivery_surface(record) == "ui" and not ui_artifact_path:
    return block_pipeline(..., block_reason="missing_ui_ux_artifact", ...)

ui_valid, ui_reason, ui_evidence, ui_message = validate_ui_ux_artifact(...)
if not ui_valid:
    return block_pipeline(..., block_reason=ui_reason, evidence_path=ui_evidence, ...)

stage_evidence_path = write_stage_structured_evidence(...)
bundle_ok, bundle_reason, bundle_evidence_path, bundle_message = validate_stage_evidence_bundle(...)
```
Keep the order: preflight -> specialist dispatch -> workspace inventory/substance -> UI validation -> structured evidence write -> structured evidence validation -> event/state persistence.

**Append-only event + authority + derived status synchronization** ([scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:1072), [scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:1142), [scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:1248), [scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:2954))
```python
event = {
    "stage": stage,
    "status": status,
    "block_reason": block_reason,
    "evidence_path": evidence_path,
    "gate": {"name": gate_name, "decision": ...},
    "recovery": {"run_id": delivery_run_id, "resume_from_stage": resume_from_stage, "repair_action": repair_action},
    "substance": substance,
}

update_pipeline_state(..., gate_name=gate_name, repair_action=repair_action, detail=message)
append_next_pipeline_event(project_dir, make_event(...))
persist_and_render(authority_path, record)
```
Every new Phase 19 gate must write all three layers together: authority JSON, JSONL event, markdown status/final review.

### `scripts/validate_delivery_handoff.py` (validator, request-response)

**Analog:** `scripts/validate_delivery_handoff.py`

**Validator-owned section list and placeholder rejection** ([scripts/validate_delivery_handoff.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_delivery_handoff.py:20))
```python
REQUIRED_STAGE_HEADINGS = [...]
REQUIRED_SUBSTANTIVE_STAGE_SECTIONS = {
    "## 4) Changed Files",
    "## 5) User Visible Behavior",
    "## 6) Pain Point Mapping",
}
PLACEHOLDER_SECTION_VALUES = {...}
```
Copy this pattern for template-only rejection: real sections are enforced by validator constants, not by prompt wording.

**Structured evidence validation** ([scripts/validate_delivery_handoff.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_delivery_handoff.py:230))
```python
if not str(payload.get("workspace_change_inventory_path", "")).strip():
    raise ...
if not isinstance(payload.get("evidence_links"), list) or not payload.get("evidence_links"):
    raise ...
if expected_stage in {"design", "development"}:
    for field in ("ui_artifact_path", "ui_artifact_summary_path"): ...
    missing_coverage = [key for key in REQUIRED_UI_COVERAGE_KEYS if not isinstance(coverage.get(key), list) or not coverage.get(key)]
if expected_stage == "testing":
    if not isinstance(payload.get("verification_evidence"), list) or not payload.get("verification_evidence"):
        raise ...
```
Phase 19 UI coverage and testing evidence checks should be added here first, then mirrored in orchestrator logic.

**Manifest replay pattern** ([scripts/validate_delivery_handoff.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_delivery_handoff.py:285))
```python
validate_stage_handoff(...)
validate_stage_evidence(...)
matching_events = [event for event in events if event.get("stage") == stage and event.get("role") == role and event.get("artifact") == artifact]
if latest.get("action") != "stage_completed":
    raise ...
```
Use this replay model for Phase 19 evidence gates: artifact validity is not enough; there must be matching event history.

### `scripts/validate_approved_delivery_pipeline.py` (cross-link validator, event-driven)

**Analog:** `scripts/validate_approved_delivery_pipeline.py`

**Stage order and UI-stage enforcement** ([scripts/validate_approved_delivery_pipeline.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_approved_delivery_pipeline.py:28), [scripts/validate_approved_delivery_pipeline.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_approved_delivery_pipeline.py:232))
```python
SPECIALIST_STAGE_ORDER = ["design", "development", "testing", "git_versioning", "release_readiness"]
UI_STAGE_ORDER = {"design", "development"}
...
structured_evidence_path = first_nonempty(get_nested(event, "evidence", "primary_path"), event.get("evidence_path"))
payload = load_json(structured_evidence_file, f"{stage} structured evidence")
if stage in UI_STAGE_ORDER:
    for key in ("ui_artifact_path", "ui_artifact_summary_path"): ...
```
This is the exact pattern for validating that UI stages carry UI evidence in event-linked structured artifacts.

**Blocked-state visibility contract** ([scripts/validate_approved_delivery_pipeline.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_approved_delivery_pipeline.py:291))
```python
block_reason = first_nonempty(...event..., ...pipeline..., ...latest_blocked_prerequisite...)
evidence_path = first_nonempty(...)
failed_gate = first_nonempty(...)
repair_action = first_nonempty(...)
if Path(evidence_path).name.lower() not in lowered and evidence_path.lower() not in lowered:
    raise ...("status view missing blocked prerequisite evidence link")
```
Phase 19 blocked gates should preserve the same reason/evidence/gate/repair tuple across authority, event, and rendered markdown.

**Template-only rejection and current-truth precedence** ([scripts/validate_approved_delivery_pipeline.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_approved_delivery_pipeline.py:409), [scripts/validate_approved_delivery_pipeline.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_approved_delivery_pipeline.py:476))
```python
template_only = bool(substance.get("template_only", False))
if template_only:
    raise ApprovedDeliveryPipelineValidationError(...)

if status == "completed":
    if first_nonempty(get_nested(pipeline, "block_reason")):
        raise ...
    if first_nonempty(get_nested(latest_blocked, "status")) == "blocked":
        raise ...
```
Copy this when adding new fail-closed gates: blocked history may remain visible, but current authority truth must be resolved when the run completes.

**Status token enforcement** ([scripts/validate_approved_delivery_pipeline.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_approved_delivery_pipeline.py:501))
```python
STATUS_REQUIRED_LINES = [
    "Authority", "Workspace", "Final handoff",
    "Final operator review", "Blocked prerequisite",
    "Protected change", "Platform justification",
]
```
Any new Phase 19 surfaced field should follow this explicit token-based status validator pattern.

### `scripts/approved_delivery_governance.py` (governance service, file-I/O)

**Analog:** `scripts/approved_delivery_governance.py`

**Workspace inventory classification** ([scripts/approved_delivery_governance.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/approved_delivery_governance.py:34), [scripts/approved_delivery_governance.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/approved_delivery_governance.py:173))
```python
CLASSIFICATION_ALLOWED_VALUES = (
    "product_only",
    "protected_platform",
    "blocked_for_missing_information",
)
...
if not normalized_touched_paths and not unknown_paths:
    classification = "blocked_for_missing_information"
    block_reason = "missing_workspace_change_inventory"
elif unknown_paths:
    classification = "blocked_for_missing_information"
    block_reason = "workspace_change_inventory_incomplete"
elif protected_matches:
    classification = "protected_platform"
```
Phase 19 substance gating should reuse this deterministic classification style: explicit classes, explicit block reasons, no optimistic fallback.

**Inventory source preference + report artifact** ([scripts/approved_delivery_governance.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/approved_delivery_governance.py:237), [scripts/approved_delivery_governance.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/approved_delivery_governance.py:298))
```python
if inventory is not None:
    return {"ok": True, "source": "workspace_change_inventory", ...}
...
path = workspace / ".hermes" / f"protected-surface-classification-{stage.replace('_', '-')}.json"
payload = {
    "inventory_source": ...,
    "classification": classification["classification"],
    "protected_matches": ...,
    "unknown_paths": ...,
    "reasons": ...,
    "touched_paths": ...,
    "block_reason": ...,
}
```
Copy this report shape for Phase 19 evidence artifacts that need both machine gating and operator inspection.

**Governed audit wrapper** ([scripts/approved_delivery_governance.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/approved_delivery_governance.py:457))
```python
audit_path = _write_json(_audit_path(project_dir, normalized_action), audit_payload)
_append_event(... artifact=audit_path ...)
return {**result, "audit_path": audit_path, "timestamp": timestamp, "governed_action": normalized_action}
```
Reuse this for any new governed UI validation artifact if it needs separate audit evidence.

### `scripts/render_approved_delivery_status.py` (renderer, transform)

**Analog:** `scripts/render_approved_delivery_status.py`

**Single-source derived operator view** ([scripts/render_approved_delivery_status.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/render_approved_delivery_status.py:147), [scripts/render_approved_delivery_status.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/render_approved_delivery_status.py:261), [scripts/render_approved_delivery_status.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/render_approved_delivery_status.py:273), [scripts/render_approved_delivery_status.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/render_approved_delivery_status.py:308))
```python
"## Blocked Prerequisites",
f"- Block Reason: `{blocked_reason or 'not available'}`",
f"- Failed Gate: `{blocked_gate or 'not available'}`",
f"- Blocked Prerequisite Evidence: `{blocked_evidence or 'not available'}`",
f"- Repair Action: `{blocked_repair_action or 'not available'}`",
...
"## Specialist Delivery Stages",
f"- {item['stage']}: status=`{item['status']}` artifact=`{item['artifact']}` evidence=`{item['evidence']}` template_only=`{item['template_only']}` proof_verdict=`{item['proof_verdict']}`"
...
"## Protected Change Review",
f"- Protected Change Evidence: `{protected_change.get('evidence_path', 'not available')}`",
f"- Platform Justification Artifact: `{justification.get('artifact_path', 'not available')}`",
```
Phase 19 should surface new UI evidence gate failures here instead of inventing a separate status file.

**Status and final review written from same markdown** ([scripts/render_approved_delivery_status.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/render_approved_delivery_status.py:333))
```python
status_path.write_text(markdown, encoding="utf-8")
final_review_path.write_text(markdown, encoding="utf-8")
```
Preserve this convergence pattern. New gate visibility should appear identically in both artifacts.

### `tests/test_approved_delivery_pipeline_cli.py` (test, event-driven)

**Analog:** `tests/test_approved_delivery_pipeline_cli.py`

**Validator-owned handoff contract test** ([tests/test_approved_delivery_pipeline_cli.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_approved_delivery_pipeline_cli.py:65))
```python
markdown = starter_module.build_specialist_handoff_markdown(...)
for heading in validator_module.REQUIRED_STAGE_HEADINGS:
    self.assertIn(heading, markdown)
```
Add Phase 19 tests by asserting runtime generation follows validator constants.

**Missing artifact / cross-link failure fixture** ([tests/test_approved_delivery_pipeline_cli.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_approved_delivery_pipeline_cli.py:125))
Use temporary workspace + minimal authority/event/status files, then assert validator stderr mentions the missing artifact class. This is the preferred regression style for new fail-closed gate cases.

**Vercel authoritative-evidence rejection pattern** ([tests/test_approved_delivery_pipeline_cli.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_approved_delivery_pipeline_cli.py:179))
Use partial metadata without the evidence artifact and assert failure. Reuse this pattern for stale/missing UI summary or drifted UI contract cases.

**Template-only specialist rejection fixture** ([tests/test_approved_delivery_pipeline_cli.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_approved_delivery_pipeline_cli.py:250))
```python
"substance": {
    "template_only": True,
    "issues": ["workspace changes only touched src/lib/app-definition.ts"],
},
```
This is the exact test pattern for Phase 19 substance gates.

**Resolved block history accepted / stale current block rejected** ([tests/test_approved_delivery_pipeline_cli.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_approved_delivery_pipeline_cli.py:904), [tests/test_approved_delivery_pipeline_cli.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_approved_delivery_pipeline_cli.py:1064))
Use paired fixtures:
- one with historical blocked event plus `latest_blocked_prerequisite.status = "resolved"` and completed handoff
- one with completed pipeline but stale `pipeline.block_reason` / `latest_blocked_prerequisite.status = "blocked"`

That pair is the reusable Phase 19 pattern for blocked-state evidence visibility and recovered-truth precedence.

## Shared Patterns

### Fail-Closed Gate Results
**Sources:** [scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:2954), [scripts/validate_approved_delivery_pipeline.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_approved_delivery_pipeline.py:291)
Apply to all new Phase 19 gates.
```python
return block_pipeline(
    authority_path,
    record,
    stage=pipeline_stage,
    block_reason=...,
    evidence_path=...,
    message=...,
    workspace_path=workspace.as_posix(),
    delivery_run_id=delivery_run_id,
)
```

### Machine Evidence + Human Markdown Pairing
**Sources:** [scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:1910), [scripts/render_approved_delivery_status.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/render_approved_delivery_status.py:234)
Every gate should emit a JSON evidence artifact and make that path appear in derived markdown.

### UI Artifact Governance
**Sources:** [scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:2291), [scripts/validate_delivery_handoff.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_delivery_handoff.py:251)
Only UI stages (`design`, `development`) on UI delivery surfaces should require:
- `.hermes/ui-ux-design-system.md`
- `.hermes/ui-ux-design-system.summary.json`
- non-empty `coverage` lists for the required keys

### Workspace Inventory as Substance Truth
**Sources:** [scripts/approved_delivery_governance.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/approved_delivery_governance.py:173), [scripts/start_approved_project_delivery.py](/abs/path/C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:2380)
Use workspace inventory as the canonical source for `template_only`, touched paths, and product/proof evidence. Do not infer substance from handoff prose alone.

## No Analog Found

None. Phase 19 fits directly into the existing approved-delivery authority/event/status/handoff architecture.

## Metadata

**Analog search scope:** `scripts/`, `tests/`, `.planning/phases/19-specialist-evidence-and-ui-artifact-gates/`
**Files scanned:** 7
**Pattern extraction date:** 2026-05-04
