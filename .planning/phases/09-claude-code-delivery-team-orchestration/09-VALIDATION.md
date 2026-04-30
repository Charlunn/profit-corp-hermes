---
phase: 09-claude-code-delivery-team-orchestration
created: 2026-04-27
source: phase research
---

# Phase 9: Claude Code Delivery Team Orchestration - Validation Strategy

## Validation Architecture

### Goal-Backward Validation
The phase passes only if Hermes can define a repeatable, role-attributed approved-project delivery workflow that starts from the fixed approved bundle, constrains work to approved scope and protected platform boundaries, emits per-stage handoff artifacts, and leaves an operator-readable plus machine-readable replay trail.

### Required Evidence
- Delivery-run initialization artifact exists and lists the fixed required input bundle.
- Stage handoff artifacts exist for each normalized stage with gate decision, outputs, evidence links, risks, and next-stage input.
- Machine-readable delivery event stream records role, stage, action, artifact, timestamp, and outcome.
- Human-readable latest-status artifact is derived from the delivery event stream and surfaces current run state.
- Scope-reopen path exists and blocks protected-platform or out-of-scope work unless explicitly approved.
- Final delivery artifact summarizes end-to-end outcome, impact surface, verification evidence, rollback plan, and release recommendation.

### Validation Layers
1. **Contract tests**
   - Lock delivery templates, required fields, event schema invariants, and stage ordering.
2. **CLI / script tests**
   - Validate run initialization, event append helpers, status rendering, scope reopen request flow, and delivery handoff validation commands.
3. **Integration workflow tests**
   - Simulate an approved workspace and verify a full delivery run can progress through all stages while producing the expected artifacts.
4. **Negative-path tests**
   - Verify missing approved inputs, protected-path edits, missing handoff fields, or missing scope approval cause a block.

### Critical Failure Modes
- Delivery run starts without one of the mandatory approved inputs.
- Specialist stages skip artifact handoff and rely on freeform state.
- Protected platform change proceeds without scope reopen.
- Event stream lacks enough metadata to replay who did what.
- Latest-status view drifts from the underlying event stream.
- Final delivery artifact exists but omits verification or rollback evidence.

### Suggested Verification Commands
- `python -m unittest tests.test_delivery_orchestration_templates`
- `python -m unittest tests.test_delivery_run_workflow`
- `python scripts/start_delivery_run.py --help`
- `python scripts/append_delivery_event.py --help`
- `python scripts/render_delivery_status.py --help`
- `python scripts/request_scope_reopen.py --help`
- `python scripts/validate_delivery_handoff.py --help`

### Exit Criteria
The phase is verification-ready only when a seeded approved workspace can produce a complete run manifest, stage handoff chain, delivery event log, latest-status markdown, governed scope-reopen path, and final delivery artifact with all locked fields present.
