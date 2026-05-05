# Phase 21: Bootstrap/Resume Governance Regressions - Research

**Researched:** 2026-05-04  
**Domain:** approved-project bootstrap/resume governance hardening  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Bootstrap and resume must execute the same governance contract rather than branching into a lighter resume-only path.
- **D-02:** Persisted artifacts cannot be trusted just because they exist; resumed stages must still validate run match, stage match, artifact linkage, freshness, and required coverage.
- **D-03:** Resume should restore parity by refreshing governed managed surfaces when necessary, while preserving legitimate existing workspace state like Git history and previously proven artifacts.
- **D-04:** Governance failures must persist precise machine-readable stage, reason, evidence path, and resolution status.
- **D-05:** Recovered runs must preserve recent blocked history as resolved context without leaving blocked fields acting like current truth.
- **D-06:** Authority/event/render drift is itself a blocking failure and must persist as `authority_state_drift`.
- **D-07:** Expand the existing approved-delivery fixture suites instead of inventing a separate regression harness.
- **D-08:** The regression matrix must cover fresh start, blocked bootstrap, resumed recovery, and recovered-final-state success.
- **D-09:** All four governance surfaces must converge: `APPROVED_PROJECT.json`, `approved-delivery-events.jsonl`, `DELIVERY_PIPELINE_STATUS.md`, and `FINAL_OPERATOR_REVIEW.md`.
- **D-10:** Post-handoff resume should no-op when authoritative completion artifacts already exist.
- **D-11:** Workspace recovery should prefer in-place refresh of managed files over destructive recreation.
- **D-12:** Every new governance block added by Phases 19 and 20 must remain repairable and resumable without hand-editing authority artifacts.

### the agent's Discretion
- Exact helper extraction for shared bootstrap/resume gate execution.
- Final field naming for resolved-block metadata so long as all surfaces consume one canonical truth.
- How shared fixture builders are factored across bootstrap, resume, and validator tests.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| RESUME-01 | Bootstrap and resume enforce the same evidence, UI-artifact, and product-proof gates | Unify gate entry paths around existing controller/validator helpers and add regressions that prove resume cannot bypass them |
| RESUME-02 | Governance failures persist precise block reasons and recoverable evidence paths | Keep authority-first block metadata plus append-only event detail; extend drift and resolved-block assertions |
| RESUME-03 | Regression coverage proves fresh, blocked, resumed, and recovered-final-state behavior | Grow the current bootstrap/resume/CLI suites into a four-state governance matrix rather than building a new harness |
</phase_requirements>

## Summary

Phase 21 is not a new subsystem. The repo already has most of the runtime seams needed for bootstrap/resume hardening:

- `scripts/start_approved_project_delivery.py` owns both `start_approved_project_delivery(...)` and `resume_approved_project_delivery(...)`, with both paths funneled through `run_pipeline_from_stage(...)`.
- `scripts/validate_approved_delivery_pipeline.py` already validates blocked-prerequisite visibility, current-state precedence, specialist stage visibility, product proof, and cross-links between authority, events, status, and final review.
- `tests/test_project_delivery_pipeline_bootstrap.py` and `tests/test_project_delivery_pipeline_resume.py` already model blocked, resumed, recovered, and finalized runs with rich fixtures.

That means the core research conclusion is: **Phase 21 should harden parity, not add parallel machinery.** The safest brownfield path is to keep bootstrap and resume as thin entry points into the same gate helpers, then expand the existing regression suites until they prove that new Phase 19 and Phase 20 gates behave identically in both paths.

## Current Seams That Already Support Phase 21

### 1) Shared orchestration path already exists
- `resume_approved_project_delivery(...)` resolves persisted stage/status, validates drift, and then re-enters `run_pipeline_from_stage(...)`.
- `start_approved_project_delivery(...)` also funnels into `run_pipeline_from_stage(...)`.
- This is the best place to enforce parity: one set of stage handlers should gate both fresh and resumed runs.

### 2) Drift detection already exists but needs to scale with new gates
- `validate_resume_governance_truth(...)` in `start_approved_project_delivery.py` already blocks resume when authority and event truth diverge.
- Existing tests already assert `authority_state_drift` behavior for stale blocked-state mismatches.
- Phase 21 should extend that same pattern to the newer evidence/UI/product-proof rules rather than layering a second resume-specific audit.

### 3) Reusable regression fixtures are already strong
- Bootstrap tests already seed approved-project bundles, workspace outputs, UI artifact summaries, workspace-change inventories, blocked prereq evidence, and final handoff snapshots.
- Resume tests already cover workspace restoration, stale shipping metadata replacement, authority drift reblocking, and no-op post-handoff resume.
- CLI validator tests already enforce cross-link integrity and operator-surface truth.

### 4) Renderer/validator are already part of resumable truth
- A governance block is not complete until `APPROVED_PROJECT.json`, `approved-delivery-events.jsonl`, `DELIVERY_PIPELINE_STATUS.md`, and `FINAL_OPERATOR_REVIEW.md` all agree.
- Phase 21 therefore needs both runtime and rendered-surface assertions in every important recovery scenario.

## Recommended Brownfield Changes

### 1) Centralize stage-gate parity around shared helpers
Research direction:
- Keep bootstrap and resume as entrypoint wrappers only.
- Move any remaining stage-specific validation branching into shared helpers called from `run_pipeline_from_stage(...)`.
- Avoid any `if resume:` fast-paths that skip evidence, UI-artifact, or product-proof checks.

Recommended focal points:
- `run_pipeline_from_stage(...)`
- `ensure_ui_ux_preflight(...)`
- structured stage-evidence validation
- workspace-change/product-proof validation helpers
- resume drift validation before stage execution begins

### 2) Treat block metadata as a first-class resumable contract
Persisted block context should continue to include:
- stage
- reason
- evidence path
- status (`blocked` vs `resolved`)
- enough linkage for rendered surfaces and resume diagnostics

Research implication:
- New Phase 19/20 failures should be written through the same block/update/render path as older deployment failures.
- Resolved block history must remain queryable without overriding current completed truth.

### 3) Expand tests by scenario matrix, not by isolated helper
Best-fit matrix:
- fresh start success through bootstrap path
- fresh start blocked by missing governed evidence
- resumed run after repairing the exact blocking evidence
- recovered success with final authority truth cleaned up and recent block context retained as resolved history
- post-handoff resume no-op
- authority/event drift reblock

This aligns with the repo’s existing testing style more naturally than unitizing every helper in isolation.

## Affected Files and Functions

### Highest-priority runtime surfaces
1. `scripts/start_approved_project_delivery.py`
   - `run_pipeline_from_stage(...)`
   - `start_approved_project_delivery(...)`
   - `resume_approved_project_delivery(...)`
   - `validate_resume_governance_truth(...)`
   - `block_pipeline(...)`
   - `update_pipeline_state(...)`
2. `scripts/validate_approved_delivery_pipeline.py`
   - `validate_current_state_precedence(...)`
   - `validate_blocked_prerequisite_visibility(...)`
   - `validate_specialist_stage_visibility(...)`
   - `validate_product_proof_visibility(...)`
3. `scripts/render_approved_delivery_status.py`
   - derived status/final-review alignment for resumed and recovered runs

### Highest-priority test surfaces
1. `tests/test_project_delivery_pipeline_bootstrap.py`
2. `tests/test_project_delivery_pipeline_resume.py`
3. `tests/test_approved_delivery_pipeline_cli.py`
4. `tests/test_approved_project_record.py`

## Recommended Implementation Order

### Wave 1: Gate parity foundation
- Identify any bootstrap-only or resume-only gate branches in `run_pipeline_from_stage(...)`.
- Route evidence/UI/product-proof validation through shared helpers.
- Add or extend tests proving resume cannot bypass freshly-added gates.

### Wave 2: Blocked-truth and recovery metadata hardening
- Ensure all new blocks use the same authority/event/render persistence path.
- Confirm resolved-block context survives recovery while current truth clears blocked fields.
- Expand drift tests to cover newer governance categories, not only deployment linkage failures.

### Wave 3: Regression matrix completion and milestone-close proof
- Add coverage for the four required states across runtime plus rendered artifacts.
- Ensure post-handoff resume stays idempotent.
- Ensure milestone-close validation can point to targeted regression evidence proving strictness and recoverability together.

## Test Recommendations

| Scenario | Why it matters | Primary Test Surface |
|----------|----------------|----------------------|
| bootstrap and resume both fail on the same missing governed evidence | proves RESUME-01 parity | bootstrap + resume tests |
| resumed run must revalidate persisted UI artifact summary against current contract | prevents stale-artifact bypass | resume tests |
| resumed run must revalidate product-proof paths rather than trusting prior workspace existence | prevents proof shortcut drift | resume + CLI tests |
| recovered success clears blocked current-state fields but preserves resolved block history | proves RESUME-02 truth layering | resume + CLI tests |
| authority/event disagreement reblocks before stage execution | prevents truth drift from silently resuming | resume tests |
| post-handoff resume returns success without duplicate events | preserves resumable idempotence | resume tests |
| status/final-review surfaces show the same recovered truth after resume | closes the operator-facing convergence loop | CLI tests |

## Key Research Conclusions

1. **Do not invent a new regression harness.** The existing approved-delivery test suites are already the authoritative seam for this phase.
2. **Do not split bootstrap and resume governance logic further.** Both paths should share the same stage handlers and validation helpers.
3. **Truth convergence remains the core risk.** Runtime behavior alone is not enough; every important recovery scenario must assert rendered artifact correctness too.
4. **Recoverability is part of the requirement, not a side effect.** Every fail-closed rule added in earlier phases must produce actionable persisted evidence that a resumed run can consume.

## RESEARCH COMPLETE
