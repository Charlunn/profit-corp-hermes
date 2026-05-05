# Phase 24: Approval Package and Locked Delivery Contract - Context

**Gathered:** 2026-05-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Turn a qualified opportunity into one concise operator-facing proposal bundle, let the operator approve or reject it from chat, and persist the approved result as a locked delivery contract that downstream specialists and automation must follow.

This phase owns proposal composition, chat approval/rejection semantics, authoritative contract persistence, and drift detection after approval. It does not own the pre-approval qualification rules from Phase 23, and it does not reopen the already-built delivery execution backbone beyond making it consume the locked contract.

</domain>

<decisions>
## Implementation Decisions

### Proposal bundle shape
- **D-01:** Hermes should produce one final proposal bundle derived from qualified artifacts, not a loose collection of discovery notes the operator must reconcile manually.
- **D-02:** The proposal must summarize pain point, target user, pricing path, market rationale, build scope, expected launch outcome, and the reasons the candidate passed qualification gates.
- **D-03:** The proposal should remain concise for chat consumption, but every claim must backlink to authoritative artifacts so approval is evidence-backed rather than trust-me orchestration.

### Chat approval protocol
- **D-04:** Approval and rejection from chat should map onto the existing governed approval/event model rather than bypassing it with an untracked bot-only state change.
- **D-05:** Hermes should treat one explicit reply in the originating conversation as the authoritative approval decision, and decision handling must be idempotent so duplicate chat messages do not fork authority.
- **D-06:** If the operator response is ambiguous, incomplete, or cannot be linked to the proposal/run id, the run should block instead of guessing a contract state.

### Locked contract persistence
- **D-07:** Approval must persist one authoritative contract record that downstream delivery reads as source of truth for scope, pricing, required languages, acceptance gates, and approved product framing.
- **D-08:** The locked contract should extend the existing approved-project authority bundle rather than inventing a second downstream delivery record type.
- **D-09:** Chat-origin metadata, qualification proof links, and proposal identity should be persisted into the authoritative contract so later delivery/handoff can trace back to the exact approved decision.

### Drift and reopen governance
- **D-10:** Downstream delivery may not silently change approved scope, pricing, or acceptance gates; any such change should open a blocked drift/reopen state with explicit reason codes.
- **D-11:** Scope expansion or protected-platform deviations after approval should continue to use governance-backed reopen mechanics rather than side-channel operator messages.
- **D-12:** Operator-facing status and final review surfaces must be able to explain whether the active delivery still matches the approved contract and what exact contract field drifted when it does not.

### the agent's Discretion
- Exact proposal markdown/chat formatting, as long as required evidence-backed sections remain present and concise.
- Exact contract field nesting inside the approved-project record, as long as downstream specialists can read stable canonical fields.
- Exact idempotency key for chat approval handling, as long as duplicate approval messages cannot produce divergent authority state.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and milestone contract
- `.planning/ROADMAP.md` - Phase 24 goal and success criteria for proposal approval and locked contract persistence.
- `.planning/REQUIREMENTS.md` - `PROP-01`, `PROP-02`, and `AUTO-01`.
- `.planning/PROJECT.md` - milestone requirement to keep one human approval gate but remove repeated healthy-path orchestration.
- `.planning/STATE.md` - current planning state and pending move to one-shot approval.

### Prior decisions that constrain this phase
- `.planning/phases/04-governance-and-control-layer/04-CONTEXT.md` - governed approval/event/status model to reuse for chat approval transitions.
- `.planning/phases/10-approved-project-delivery-pipeline/10-CONTEXT.md` - approved-project bundle as the authoritative bridge into delivery.
- `.planning/phases/18-handoff-contract-and-authority-alignment/18-CONTEXT.md` - shared machine-readable contract and authority-first rendering expectations.
- `.planning/phases/21-bootstrap-resume-governance-regressions/21-CONTEXT.md` - fail-closed drift/resume truth expectations that locked contract enforcement must preserve.
- `.planning/phases/23-real-pain-qualification-and-market-proof-gates/23-CONTEXT.md` - qualification outputs that the final proposal must summarize and freeze.

### Existing artifacts and contracts
- `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` - current operator-facing synthesis artifact whose evidence/backlink style the proposal should preserve.
- `docs/STATE_CONTRACT.md` - write boundaries for any new approval/package artifacts.
- `docs/skill-governance/templates/orchestrator-input-template-v0.2.md` - explicit approved-brief/bundle field expectations already consumed downstream.

### Existing code and tests
- `scripts/request_governance_approval.py` - governed action request/approve/reject/override contract and append-only event model.
- `scripts/start_approved_project_delivery.py` - approved-project bundle creation, authority record fields, and pipeline state contract.
- `scripts/request_scope_reopen.py` - post-approval scope drift/reopen path that should remain the escalation mechanism.
- `tests/test_approved_project_record.py` - approved-project authority shape and missing-input blocking expectations.
- `tests/test_delivery_ready_brief.py` - stable brief/proposal section ordering and derivation expectations.
- `tests/test_scope_reopen_flow.py` - governed reopen behavior for protected changes and out-of-brief work.
- `tests/test_delivery_orchestration_contract.py` - explicit downstream bundle-field expectations that the locked contract must continue to satisfy.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/start_approved_project_delivery.py`: already writes `APPROVED_PROJECT.json`, `PROJECT_BRIEF.md`, status artifacts, allowed block reasons, and shipping/delivery metadata.
- `scripts/request_governance_approval.py`: already models request/approve/reject/override transitions with action ids and append-only governance history.
- `scripts/request_scope_reopen.py`: already records pending scope-reopen state into both governance artifacts and workspace-local delivery events.
- `tests/test_delivery_ready_brief.py`: already codifies the expected order of project identity, scope, pain point, monetization, language, and acceptance sections.

### Established Patterns
- Approval truth in this repo is persisted as a durable authority record plus append-only history, not inferred from conversational context.
- Downstream delivery relies on explicit artifact paths and fixed field names rather than hidden prompt memory.
- Scope drift is expected to stop at a governed reopen gate instead of silently mutating approved intent.

### Integration Points
- Proposal finalization should likely extend the existing approved-project record/brief generation seam rather than creating a separate proposal engine.
- Chat approval messages should map into the governance approval script/event model and then update the authoritative approved-project bundle.
- Contract-drift checks should plug into existing scope-reopen and pipeline validation/rendering surfaces.

</code_context>

<specifics>
## Specific Ideas

- Auto-selected the stricter path that one concise proposal bundle should be the only operator approval object, with deep evidence preserved as backlinks rather than parallel documents.
- Defaulted to persisting the locked contract inside the existing approved-project authority record so Phase 25 can keep using the shipped delivery backbone.
- Defaulted to treating contract drift as a blocked governance state instead of a soft warning, because silent scope/pricing drift would break the milestone promise.

</specifics>

<deferred>
## Deferred Ideas

- Rich multi-operator approval workflows remain out of scope for this milestone.
- Full post-approval autonomous continuation and final chat handoff belong to Phase 25.
- Recovery commands from chat after approval failure remain later-scope work beyond the one-shot approve/reject contract.

</deferred>

---

*Phase: 24-approval-package-and-locked-delivery-contract*
*Context gathered: 2026-05-04*
