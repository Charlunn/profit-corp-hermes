# Phase 28: Hermes Proposal and Approval Surface - Context

**Gathered:** 2026-05-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Present one evidence-backed proposal and one clear approve/reject interaction as a Hermes-native conversation surface while preserving the same locked delivery contract and fail-closed governance backbone shipped in earlier phases.

This phase owns proposal composition, Hermes-native approval and rejection semantics, contract persistence under the conversation surface, and hard blocking when proposal evidence or approval linkage is missing. It does not redesign the earlier qualification gates, and it does not own final delivery completion/recovery messaging after approval.

</domain>

<decisions>
## Implementation Decisions

### Proposal surface shape
- **D-01:** Hermes should present one concise, evidence-backed proposal as the only approval object instead of asking the owner to reconcile multiple discovery, qualification, or contract artifacts.
- **D-02:** The proposal must summarize pain point, target user, feasibility, market/pricing proof, launch framing, and why the candidate passed required gates while keeping deep evidence available through backlinks.
- **D-03:** Proposal language should feel like a normal Hermes recommendation, not a bundle of subsystem-generated documents stitched together for the operator.

### Approval and rejection semantics
- **D-04:** The owner should approve or reject the proposal by replying to Hermes in the same surface where the proposal appears, without switching to a separate command or tool.
- **D-05:** Approval/rejection must map into the existing governed approval/event model so the visible Hermes conversation remains backed by durable, idempotent truth.
- **D-06:** If the reply is ambiguous, unlinked, or missing required evidence context, Hermes should block rather than guessing approval intent.

### Locked delivery contract persistence
- **D-07:** Approval must persist the same authoritative locked delivery contract already expected by the approved-project backbone instead of creating a conversation-only agreement.
- **D-08:** Proposal identity, qualification proof, approval evidence, and required delivery fields should all trace back to the same canonical run and approved-project artifacts.
- **D-09:** Downstream delivery and status surfaces must be able to prove exactly which approved proposal and contract the run is following.

### Hard-block governance at the Hermes surface
- **D-10:** Missing freshness proof, weak feasibility, thin pricing evidence, or broken approval linkage must still block hard even if Hermes presents the proposal in a cleaner conversation format.
- **D-11:** Hermes should surface these blocks in owner-facing language, but it may not smooth over missing evidence just to keep the interaction feeling polished.
- **D-12:** Any post-approval drift in scope, pricing, or core requirements should continue to escalate through the existing governed reopen/block model rather than becoming an informal chat exception.

### the agent's Discretion
- Exact proposal formatting and section ordering, as long as one concise Hermes-facing approval object remains present and evidence-backed.
- Exact approve/reject phrase matching and idempotency strategy, as long as approval intent maps durably into the governed model.
- Exact backlink set exposed to the owner, as long as proposal claims remain auditable from authoritative artifacts.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and milestone contract
- `.planning/ROADMAP.md` - Phase 28 goal and success criteria for proposal presentation and approval as one Hermes conversation.
- `.planning/REQUIREMENTS.md` - `PROP-01`, `PROP-02`, and `PROP-03`.
- `.planning/PROJECT.md` - v1.3 requirement to keep one human approval gate while hiding subsystem choreography.
- `.planning/STATE.md` - current planning context and concern that Hermes must stay honest about blockers.

### Prior decisions that constrain this phase
- `.planning/phases/23-real-pain-qualification-and-market-proof-gates/23-CONTEXT.md` - freshness, pain reality, feasibility, and pricing proof requirements that the proposal must summarize, not weaken.
- `.planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md` - prior approved-project bundle and locked-contract decisions that remain the persistence backbone.
- `.planning/phases/25-autonomous-delivery-to-deploy-and-return-link/25-CONTEXT.md` - downstream autonomous delivery expectations that depend on a stable approved contract.
- `.planning/phases/18-handoff-contract-and-authority-alignment/18-CONTEXT.md` - authority-first contract alignment rules relevant to proposal-to-delivery continuity.
- `.planning/phases/21-bootstrap-resume-governance-regressions/21-CONTEXT.md` - fail-closed truth and recovery expectations that approval linkage must preserve.

### Existing artifacts and governance surfaces
- `docs/STATE_CONTRACT.md` - write-governance rules for proposal, approval, and contract artifacts.
- `docs/skill-governance/templates/orchestrator-input-template-v0.2.md` - downstream approved-brief field expectations that the Hermes proposal must still satisfy.
- `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` - current evidence-backed synthesis style that the Hermes proposal can compress and reframe.

### Existing code and tests
- `scripts/request_governance_approval.py` - durable approval/rejection event contract and idempotent action model.
- `scripts/approved_delivery_governance.py` - approved-project governance helpers relevant to locking and validating contract state.
- `scripts/start_approved_project_delivery.py` - authoritative approved-project bundle and downstream contract fields.
- `tests/test_chat_approval_flow.py` - existing conversational approval linkage behavior relevant to Hermes-surface approval semantics.
- `tests/test_approved_project_record.py` - approved-project record requirements and blocking expectations for missing approval inputs.
- `tests/test_delivery_ready_brief.py` - proposal/brief content ordering and required field coverage that should remain true under Hermes packaging.
- `tests/test_scope_reopen_flow.py` - governance-backed reopen behavior for post-approval drift.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/request_governance_approval.py`: already models explicit approval/rejection transitions and append-only governance truth.
- `scripts/start_approved_project_delivery.py`: already persists the approved-project bundle and fields later delivery depends on.
- `scripts/approved_delivery_governance.py`: already provides helpers around approved delivery authority and policy enforcement.
- `tests/test_chat_approval_flow.py`: already captures the existing conversational approval pattern that can be repackaged as Hermes-native.

### Established Patterns
- Hermes approval truth is expected to live in durable artifacts and append-only events, not inferred from a conversation transcript alone.
- Missing required evidence is supposed to block progress rather than degrade into softer UI wording.
- Downstream delivery depends on stable approved-contract fields rather than human interpretation of proposal prose.

### Integration Points
- The Hermes proposal surface should likely render from qualified artifacts and approved-project bundle seams already used in the current pipeline.
- Approve/reject replies should likely terminate at `request_governance_approval.py` or closely related governance helpers instead of implementing a separate approval store.
- Post-approval drift handling should reuse existing reopen/governance machinery so Hermes remains consistent with current validators and status rendering.

</code_context>

<specifics>
## Specific Ideas

- Auto-selected the "one concise proposal object" default so approval feels like a single Hermes recommendation rather than artifact archaeology.
- Defaulted to governed approve/reject persistence under the hood so the improved UX does not weaken locked-contract truth.
- Chose hard blocking on missing evidence or ambiguous replies because a smoother-looking interface should not dilute shipped governance guarantees.

</specifics>

<deferred>
## Deferred Ideas

- Final success reply and blocked recovery experience after delivery belong to Phase 29.
- Richer multi-party approval or delegation workflows remain out of scope for this milestone.
- Additional channel-specific approval UX beyond the primary Hermes operator surface remains future work.

</deferred>

---

*Phase: 28-hermes-proposal-and-approval-surface*
*Context gathered: 2026-05-05*
