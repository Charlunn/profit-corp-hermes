# Phase 21: Bootstrap/Resume Governance Regressions - Context

**Gathered:** 2026-05-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Lock the hardened approved-project governance rules into bootstrap and resume flows so fresh starts, blocked runs, resumed runs, and recovered-success runs all obey the same fail-closed evidence policy and converge to one authoritative truth.

This phase covers governance parity and regression proof for `RESUME-01` through `RESUME-03`. It does not introduce new delivery stages, replace the authority/event architecture, or reopen the underlying GitHub/Vercel transport work that shipped in v1.1.1.

</domain>

<decisions>
## Implementation Decisions

### Bootstrap and resume gate parity
- **D-01:** Bootstrap and resume must execute the same governance contract, not separate "best effort" branches. Fresh-start and resume paths should reuse the same gate primitives for evidence validation, UI artifact validation, stage substance checks, product-proof checks, and authority/event rendering.
- **D-02:** Resume is not allowed to bypass gates just because prior artifacts exist. Persisted artifacts must still be checked for run match, stage match, artifact linkage, freshness, and required content coverage before the resumed stage can pass.
- **D-03:** When required workspace/bootstrap metadata is missing or stale, resume should rebuild or refresh only the governed managed surfaces needed to restore parity, while preserving legitimate existing workspace state such as Git history and already-proven delivery artifacts.

### Block reasons and resumable truth
- **D-04:** Canonical blocked-state truth must persist precise machine-readable reason, stage, evidence path, and resolution status in authority fields that both bootstrap and resume update consistently.
- **D-05:** The latest authoritative block context must remain visible after recovery as resolved history, while current-state fields must clear blocked status once the pipeline legitimately advances to ready/completed.
- **D-06:** Authority/event drift is itself a blocking governance failure. Resume should fail closed and persist `authority_state_drift` when the latest blocked event, authority record, or rendered surfaces disagree about why the run is blocked or what evidence path proves it.

### Regression coverage strategy
- **D-07:** Phase 21 should expand the existing Python fixture-based approved-delivery regression suite instead of creating a new ad hoc harness. The test seam should stay centered on `start_approved_project_delivery.py`, `validate_approved_delivery_pipeline.py`, and rendered authority artifacts.
- **D-08:** The regression matrix must explicitly cover four states: fresh-start success path, blocked bootstrap path, resumed path after repairing evidence, and recovered-final-state success with cleaned current-state truth but preserved resolved block history.
- **D-09:** Regression assertions must verify convergence across all four governance surfaces: `APPROVED_PROJECT.json`, `approved-delivery-events.jsonl`, `DELIVERY_PIPELINE_STATUS.md`, and `FINAL_OPERATOR_REVIEW.md`.

### Resume recovery behavior
- **D-10:** Resume should continue from persisted truth, not restart from assumptions. If the handoff is already finalized and authoritative artifacts exist, post-handoff resume should no-op rather than append duplicate events or replay completed stages.
- **D-11:** Workspace-instantiation recovery should prefer refreshing managed files in place over destructive recreation, as long as the workspace can be brought back to contract compliance without losing legitimate repo state.
- **D-12:** Recoverability is a hard requirement alongside strictness: every new governance block added in Phases 19 and 20 must carry enough persisted evidence and repair guidance that an operator can fix the issue and resume without manual record surgery.

### the agent's Discretion
- Exact helper/function extraction used to unify bootstrap and resume gate execution.
- Final field naming for resolved block context, as long as authority JSON, event history, renderer, and validator all read the same canonical truth.
- How to factor shared regression-fixture builders between bootstrap, resume, and validator tests to keep the test suite readable.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirement contract
- `.planning/ROADMAP.md` - Phase 21 goal, milestone context, and required outcomes for bootstrap/resume governance regressions.
- `.planning/REQUIREMENTS.md` - Formal definitions of `RESUME-01`, `RESUME-02`, and `RESUME-03`.
- `.planning/PROJECT.md` - Milestone-level governance-hardening intent, including fail-closed evidence rules and real-SaaS proof expectations.
- `.planning/STATE.md` - Current planning state and the milestone concern that recovered truth must remain authoritative across resumed runs.

### Prior phase decisions that must carry forward
- `.planning/phases/18-handoff-contract-and-authority-alignment/18-CONTEXT.md` - Canonical handoff contract, authority/event truth precedence, and operator-surface convergence rules that Phase 21 must preserve during bootstrap and resume.
- `.planning/phases/17-authority-and-status-convergence/17-authority-and-status-convergence-01-SUMMARY.md` - Recovered current truth supersedes stale blocked state.
- `.planning/phases/17-authority-and-status-convergence/17-authority-and-status-convergence-02-SUMMARY.md` - Authority/event/status/final-review convergence work that Phase 21 regression coverage must continue to protect.
- `.planning/phases/17-authority-and-status-convergence/17-authority-and-status-convergence-03-SUMMARY.md` - Final recovered-state rendering expectations for operator-facing artifacts.

### Existing governance implementation surfaces
- `scripts/start_approved_project_delivery.py` - Bootstrap, resume, block, render, and finalize orchestration for approved-project delivery.
- `scripts/validate_approved_delivery_pipeline.py` - Cross-surface validator for authority, events, status, final review, and product-proof rendering.
- `scripts/approved_delivery_governance.py` - Governed credential and workspace-change enforcement helpers that feed persisted evidence and event updates.
- `scripts/render_approved_delivery_status.py` - Operator-facing approved-delivery status renderer.
- `scripts/append_approved_delivery_event.py` - Append-only approved-delivery event contract and timestamp ordering rules.
- `scripts/validate_delivery_handoff.py` - Structured stage-handoff/evidence validation that resumed specialist stages must still satisfy.
- `scripts/product_proof_contract.py` - Product-proof summary and failure-reason contract that resume cannot bypass once Phase 20 lands.

### Existing regression seams and fixtures
- `tests/test_project_delivery_pipeline_bootstrap.py` - Bootstrap fixtures and blocked/resumed/finalized authority-path tests already covering approved-project delivery startup behavior.
- `tests/test_project_delivery_pipeline_resume.py` - Resume-path regression suite, including workspace recovery, drift detection, and post-handoff no-op behavior.
- `tests/test_approved_delivery_pipeline_cli.py` - Validator-oriented CLI and cross-link regression tests for approved-project authority bundles.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/start_approved_project_delivery.py`: already owns `start_approved_project_delivery(...)`, `resume_approved_project_delivery(...)`, `finalize_delivery_handoff(...)`, block persistence, and pipeline-state updates.
- `scripts/validate_approved_delivery_pipeline.py`: already validates blocked prerequisite visibility, specialist stage visibility, product-proof visibility, and current-state precedence across rendered artifacts.
- `tests/test_project_delivery_pipeline_bootstrap.py`: already has fixture builders for approved-project roots, workspace seeds, UI artifact summaries, and blocked/resumed/finalized pipeline scenarios.
- `tests/test_project_delivery_pipeline_resume.py`: already exercises resume-specific behaviors such as workspace refresh, authority drift reblocking, stale shipping metadata replacement, and post-handoff no-op resumes.

### Established Patterns
- Approved-project governance uses `APPROVED_PROJECT.json` for latest state, `approved-delivery-events.jsonl` for append-only history, and rendered markdown as operator-facing derived views.
- Resume logic is expected to fail closed when authoritative truth drifts, not silently reconcile conflicting state.
- Governance rules are enforced through Python scripts plus fixture-driven unit tests rather than through a separate service or database-backed workflow engine.
- UI and product-proof gates are already modeled as persisted artifacts and structured evidence paths, which means Phase 21 should reuse those contracts rather than invent phase-specific resume markers.

### Integration Points
- Planning should treat bootstrap and resume as two entry points into the same governance pipeline centered on `run_pipeline_from_stage(...)` and the supporting block/render helpers.
- Phase 19 and Phase 20 gates will likely add new block reasons and structured evidence fields, so Phase 21 needs to ensure those additions flow through resume, status rendering, validator checks, and tests without branching logic drift.
- Regression coverage needs to verify both runtime behavior and post-run rendered artifacts, because operator-visible drift is part of the failure mode this milestone is trying to prevent.

</code_context>

<specifics>
## Specific Ideas

- Auto mode selected the stricter path: bootstrap and resume should share one fail-closed gate contract rather than allowing resume-only shortcuts.
- Existing bootstrap/resume test files are the preferred place to grow the regression matrix; the repo already treats them as the authority seam for delivery recovery behavior.
- Recovered success should keep block history visible as resolved context, but current status must read as completed everywhere once the run has legitimately recovered.

</specifics>

<deferred>
## Deferred Ideas

- Adding brand-new delivery stages or specialist roles is out of scope for this phase.
- Reworking GitHub/Vercel credential transport or deploy mechanics is out of scope unless a new blocker appears while hardening governance parity.
- Replacing file-backed authority/event artifacts with a new state store or workflow engine remains out of scope for this milestone.

</deferred>

---

*Phase: 21-bootstrap-resume-governance-regressions*
*Context gathered: 2026-05-04*
