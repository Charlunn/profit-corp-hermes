---
phase: 10-approved-project-delivery-pipeline
created: 2026-04-27
source: phase research
---

# Phase 10: Approved Project Delivery Pipeline - Validation Strategy

## Validation Architecture

### Goal-Backward Validation
The phase passes only if Hermes can convert a single explicit owner approval into a deterministic approved-project bootstrap flow that generates the canonical delivery brief, instantiates a governed workspace, validates it, starts the Phase 9 delivery runtime, tracks bootstrap state durably, and blocks with explicit persisted reasons when prerequisites fail.

### Required Evidence
- Approved-project authority artifact exists and captures approval, normalized project identity, scope, constraints, and pipeline stage/status.
- Delivery-ready brief is generated deterministically from the approved-project authority, not hand-authored independently.
- Bootstrap wrapper creates or reuses the governed workspace, attaches the canonical brief into `.hermes`, and runs template conformance before delivery-run start.
- Phase 10 state latest view is derived from machine-readable authority state and surfaces stage, status, block reason, and output links.
- Missing approval, missing brief inputs, instantiation failure, conformance failure, or bootstrap failure produce persisted blocked state with enough evidence to resume.
- Successful bootstrap hands off cleanly to Phase 9 by creating/recording the delivery run id and workspace linkage.

### Validation Layers
1. **Contract tests**
   - Lock approved-project schema, brief content contract, stage/status/block enums, and latest-view required fields.
2. **Bootstrap workflow tests**
   - Validate approval capture, brief generation, identity normalization, workspace instantiation attachment, and handoff to `start_delivery_run.py`.
3. **Failure-path tests**
   - Validate block behavior for missing approval, missing required inputs, duplicate active bootstrap, conformance failure, and delivery-run bootstrap failure.
4. **Resume/retry tests**
   - Validate blocked runs can resume from the last incomplete Phase 10 stage without losing authority state or creating duplicate workspaces.

### Critical Failure Modes
- Approval exists only in chat history and not in a durable artifact.
- Project identity fields diverge between approval record, brief, and workspace bootstrap.
- Conformance failure occurs after instantiation but the pipeline loses track of the workspace or block reason.
- `PROJECT_BRIEF_ENTRYPOINT.md` remains only a locator stub and not a trustworthy delivery-ready brief input.
- Phase 10 latest view drifts from the underlying machine state.
- Phase 10 and Phase 9 stage/state models are mixed together, making resume/retry ambiguous.

### Suggested Verification Commands
- `python -m unittest tests.test_approved_project_record tests.test_delivery_ready_brief`
- `python -m unittest tests.test_project_delivery_pipeline_bootstrap tests.test_project_delivery_pipeline_resume`
- `python scripts/<phase10-bootstrap-script>.py --help`
- `python scripts/instantiate_template_project.py --help`
- `python scripts/check_template_conformance.py --help`
- `python scripts/start_delivery_run.py --help`

### Exit Criteria
The phase is verification-ready only when an approved opportunity can be materialized into a durable approved-project record, a canonical delivery brief, a governed instantiated workspace, a passed conformance check, a started delivery run, and a persisted latest-view status, with blocked states remaining resumable instead of forcing a full restart.
