# Phase 29: Hermes Final Delivery Experience and Blocked Recovery - Context

**Gathered:** 2026-05-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Make the natural end of the Hermes project workflow either one final shipped-result reply with the live deployment URL or one clear blocked-recovery reply that explains what failed and what context exists for recovery, all without forcing the owner to inspect pipeline internals first.

This phase owns the owner-facing final success response, owner-facing blocked recovery response, and the requirement that both derive from authoritative persisted truth rather than transient process memory. It does not redesign the technical delivery backbone itself, and it does not expand into richer conversational recovery commands beyond surfacing actionable blocked context.

</domain>

<decisions>
## Implementation Decisions

### Final success surface
- **D-01:** Successful completion should return one Hermes-native final reply that includes the live deployment URL, concise ship summary, and quick access to authoritative delivery artifacts.
- **D-02:** The final success reply should feel like the natural completion of the same project request that started the run, not like a separate operator workflow or report-hunting step.
- **D-03:** Final success content should be rendered from persisted status/final-review truth rather than composed from in-memory assumptions about what probably shipped.

### Blocked recovery surface
- **D-04:** When delivery blocks, Hermes should return one owner-facing blocked reply that states the failed stage, concrete reason, and the recovery context needed to continue.
- **D-05:** The blocked reply should explain the issue in Hermes language first, while still preserving direct links or references to the authoritative status and evidence artifacts underneath.
- **D-06:** Hermes may not pretend a run succeeded or is still healthy when the persisted authority state says it is blocked, incomplete, or inconsistent.

### Healthy-path autonomy and surfaced truth
- **D-07:** The owner should not need manual resume commands on healthy runs; the normal expectation after approval is that Hermes continues until either final success or a real blocker emerges.
- **D-08:** Success and blocked replies must stay synchronized with the same approved-project, delivery-event, and rendered-status truth already enforced in the shipped backbone.
- **D-09:** If the authoritative artifacts do not converge on one final truth, Hermes should block and report the inconsistency rather than improvising a clean-looking final answer.

### Recovery boundary
- **D-10:** Phase 29 should surface recovery context clearly, but it does not need to implement a brand-new recovery state model or freeform chat remediation engine.
- **D-11:** Existing reason-coded resume/recovery mechanics should remain the canonical path behind the Hermes reply so operators can recover runs without hidden state.
- **D-12:** The Hermes final surface should distinguish healthy completion from blocked recovery explicitly, ensuring the owner never has to infer whether intervention is required.

### the agent's Discretion
- Exact wording and layout of the final success and blocked replies, as long as URL/summary or stage/reason/recovery context remain explicit.
- Exact backlink bundle included in the final messages, as long as operators can quickly inspect authoritative artifacts.
- Exact rendering seam used to produce the final Hermes reply, as long as it remains driven by persisted truth.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and milestone contract
- `.planning/ROADMAP.md` - Phase 29 goal and success criteria for final success and blocked recovery as one Hermes workflow outcome.
- `.planning/REQUIREMENTS.md` - `AUTO-01`, `AUTO-02`, and `AUTO-03`.
- `.planning/PROJECT.md` - v1.3 requirement that healthy-path interaction collapses to start plus approve plus final result.
- `.planning/STATE.md` - current milestone concern about keeping blocked truth honest while hiding pipeline internals.

### Prior decisions that constrain this phase
- `.planning/phases/17-authority-and-status-convergence/17-PATTERNS.md` - authoritative current-truth convergence expectations for final status reporting.
- `.planning/phases/21-bootstrap-resume-governance-regressions/21-CONTEXT.md` - recovered/blocked truth and resume parity expectations.
- `.planning/phases/25-autonomous-delivery-to-deploy-and-return-link/25-CONTEXT.md` - healthy-path autonomy and final notification decisions that this phase now repackages as Hermes-first operator experience.
- `.planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md` - approved-contract continuity that final success or failure must still trace back to.
- `.planning/phases/19-specialist-evidence-and-ui-artifact-gates/19-CONTEXT.md` - proof and artifact requirements that final success cannot bypass.

### Existing artifacts and rendering surfaces
- `docs/STATE_CONTRACT.md` - state-governance expectations for final status and recovery artifacts.
- `docs/skill-governance/templates/final-delivery-template-v0.2.md` - final delivery artifact structure already consumed downstream.
- `README.md` - current render/validate/recover commands that should become implementation details under the Hermes final surface.

### Existing code and tests
- `scripts/render_approved_delivery_status.py` - authoritative final/current status rendering seam for shipped and blocked outcomes.
- `scripts/chat_final_delivery_notify.py` - existing completion/failure notification path that can inform the Hermes final reply surface.
- `scripts/chat_approved_delivery_autorun.py` - healthy-path automation seam whose outcomes must feed the final Hermes result.
- `scripts/validate_approved_delivery_pipeline.py` - cross-surface convergence checks that should gate final success reporting.
- `scripts/product_proof_contract.py` - canonical product-proof vocabulary and blocking reasons that final Hermes responses must respect.
- `tests/test_chat_delivery_notifications.py` - existing final notification expectations for success and failure outcomes.
- `tests/test_chat_autorun_flow.py` - healthy-path automation behavior that must still terminate in authoritative final truth.
- `tests/test_approved_delivery_pipeline_cli.py` - final status, proof, and rendered-review expectations relevant to owner-facing completion.
- `tests/test_project_delivery_pipeline_resume.py` - recovered final-state truth expectations that blocked recovery surfaces must preserve.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/render_approved_delivery_status.py`: already renders authoritative delivery status and final review information from persisted artifacts.
- `scripts/chat_final_delivery_notify.py`: already turns approved delivery outcomes into operator-facing success or failure notifications.
- `scripts/chat_approved_delivery_autorun.py`: already manages healthy-path continuation after approval and feeds eventual final outcomes.
- `scripts/validate_approved_delivery_pipeline.py`: already verifies that final visible status matches machine-readable authority and proof artifacts.

### Established Patterns
- Final success in this repo is only real when proof artifacts, status surfaces, and delivery authority converge on the same truth.
- Blocked and recovered states are expected to be explicit, reason-coded, and resumable rather than hidden behind optimistic messaging.
- Owner-facing messaging should be concise, but it still needs fast paths to the canonical artifacts that justify the visible result.

### Integration Points
- The Hermes final reply should likely render from the same approved-delivery status/final-review surfaces already used in the current pipeline.
- Blocked recovery messaging should likely reuse existing reason-coded delivery and governance artifacts rather than introducing a second blocked-state vocabulary.
- Final result reporting should sit at the end of the same start-to-approve-to-deliver run identity introduced in earlier phases.

</code_context>

<specifics>
## Specific Ideas

- Auto-selected the "one final Hermes reply" model so final success feels like the completion of the original project request.
- Defaulted to deriving both success and blocked outcomes from persisted authority/rendered-review truth rather than transient process memory.
- Preserved the existing recovery mechanics behind the scenes so clearer owner messaging does not create a second exceptional-path model.

</specifics>

<deferred>
## Deferred Ideas

- Rich chat-native retry, redirect, or cancel commands remain future recovery-scope work beyond this phase.
- Multi-recipient or multi-channel final notification expansion remains out of scope for the initial Hermes-first operator surface.
- Workflow-engine replacement or deeper background-service rearchitecture remains out of scope; this phase should package the shipped backbone more naturally.

</deferred>

---

*Phase: 29-hermes-final-delivery-experience-and-blocked-recovery*
*Context gathered: 2026-05-05*
