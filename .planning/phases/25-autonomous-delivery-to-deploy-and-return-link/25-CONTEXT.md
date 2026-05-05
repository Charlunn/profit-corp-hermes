# Phase 25: Autonomous Delivery to Deploy and Return Link - Context

**Gathered:** 2026-05-04
**Status:** Ready for planning

<domain>
## Phase Boundary

After a proposal is approved, let Hermes continue automatically through governed specialist execution, GitHub, Vercel, and final handoff, then send the deployment link and concise result summary back to the originating chat thread.

This phase owns healthy-path autonomy after approval, final chat-thread completion/failure reporting, and proof that real specialist output and real implementation artifacts drove delivery. It does not reopen the earlier GitHub/Vercel reliability milestone work except where those seams must now be triggered automatically and reported back to chat.

</domain>

<decisions>
## Implementation Decisions

### Post-approval autonomous continuation
- **D-01:** Approval should hand off directly into the existing approved-project delivery backbone using persisted authoritative state, not require a separate human `resume` command on healthy runs.
- **D-02:** Automation should advance by reading and updating the same `APPROVED_PROJECT.json`, append-only events, and rendered status/final review artifacts already used by the shipped pipeline.
- **D-03:** Any stage transition that cannot be proven from authoritative artifacts should block rather than pretending autonomy succeeded.

### Specialist proof and real implementation evidence
- **D-04:** Autonomous continuation must keep the stricter v1.1.2 proof gates: real specialist artifacts, valid `/ui-ux-pro-max` coverage where applicable, workspace-change evidence, and product-proof artifacts remain mandatory.
- **D-05:** The orchestrator may automate stage progression, but it may not replace specialist output with synthetic placeholder proof or ad hoc markdown summaries.
- **D-06:** Pricing, monetization, languages, and other approved contract fields must survive into the delivered workspace surfaces and release evidence, not disappear after approval.

### Final chat-thread handoff
- **D-07:** Completion should send one derived final response to the originating chat thread containing the live deployment link, concise ship summary, and links/paths to authoritative final artifacts.
- **D-08:** Failure or blocked completion should send the same style of final thread response, but with explicit blocked reason, failed stage, and next recovery context instead of a fake success.
- **D-09:** Final chat replies should be rendered from persisted authority/final-review truth, not composed from transient process memory.

### Exceptional recovery vs healthy-path autonomy
- **D-10:** Healthy runs should need no manual resumes after approval, but exceptional failures should still preserve a resumable blocked state rather than hiding recovery requirements.
- **D-11:** Chat-visible completion/failure should stay aligned with the same blocked/recovered truth already enforced in delivery status and final review artifacts.
- **D-12:** Phase 25 should extend existing resume/recovery mechanics to notification/orchestration boundaries rather than inventing a second exceptional-path model for chat runs.

### the agent's Discretion
- Exact scheduler/polling mechanism that advances approved runs after chat approval, as long as it preserves authoritative state transitions and healthy-path autonomy.
- Exact final chat message layout, as long as deployment link, concise summary, and blocked context remain explicit.
- Exact artifact backlink set included in the final response, as long as operators can reach the authoritative review/status bundle quickly.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and milestone contract
- `.planning/ROADMAP.md` - Phase 25 goal and success criteria for autonomous approved-to-deploy completion.
- `.planning/REQUIREMENTS.md` - `AUTO-02` through `AUTO-04`.
- `.planning/PROJECT.md` - milestone intent to keep interaction to start plus approve on healthy paths.
- `.planning/STATE.md` - current milestone direction and concern about preserving governance while removing manual resumes.

### Prior decisions that constrain this phase
- `.planning/phases/19-specialist-evidence-and-ui-artifact-gates/19-CONTEXT.md` - specialist evidence and `/ui-ux-pro-max` gate rules that automation must still honor.
- `.planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md` - real product proof and template-residue blocking rules that final autonomy must preserve.
- `.planning/phases/21-bootstrap-resume-governance-regressions/21-CONTEXT.md` - bootstrap/resume parity and recovered-truth expectations.
- `.planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md` - locked-contract fields and drift rules that delivery must obey after approval.

### Existing artifacts and contracts
- `docs/platform/standalone-saas-template-contract.md` - required product, monetization, language, and platform-contract expectations that must survive into delivery.
- `docs/skill-governance/templates/final-delivery-template-v0.2.md` - final delivery artifact baseline consumed at the handoff boundary.
- `README.md` - current approved-delivery start/resume/render/validate commands that Phase 25 needs to trigger autonomously.

### Existing code and tests
- `scripts/start_approved_project_delivery.py` - primary orchestration backbone for stage progression, blocking, GitHub/Vercel actions, and final handoff.
- `scripts/start_delivery_run.py` - workspace-local delivery bootstrap manifest and stage-order contract.
- `scripts/render_approved_delivery_status.py` - derived operator-facing current-state and final-review rendering.
- `scripts/validate_approved_delivery_pipeline.py` - cross-surface validation for proof visibility, blocked-state truth, and final review completeness.
- `scripts/product_proof_contract.py` - canonical real-product proof vocabulary and failure reasons.
- `tests/test_project_delivery_pipeline_bootstrap.py` - healthy/blocked bootstrap expectations for approved delivery runs.
- `tests/test_project_delivery_pipeline_resume.py` - resumed/recovered final-state expectations that healthy automation must not break.
- `tests/test_approved_delivery_pipeline_cli.py` - end-to-end validator expectations for rendered truth, product proof, and final operator review.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/start_approved_project_delivery.py`: already contains the full post-approval stage map from approval through handoff, plus GitHub/Vercel actions, block reasons, and finalization behavior.
- `scripts/start_delivery_run.py`: already defines the specialist stage order and workspace-local manifest for autonomous delivery.
- `scripts/render_approved_delivery_status.py`: already renders authoritative stage/proof/failure state suitable for later chat-thread summaries.
- `scripts/validate_approved_delivery_pipeline.py`: already enforces that rendered/operator-facing artifacts agree with machine-readable authority truth.

### Established Patterns
- Delivery autonomy in this repo is artifact-driven: stage transitions are validated from persisted evidence, not from optimistic process completion.
- Healthy-path progression and exceptional-path resume share one state model rather than separate orchestration systems.
- Final success is not declared until proof artifacts, status surfaces, and final review all converge on the same truth.

### Integration Points
- Chat-triggered approval should likely call into the existing approved-delivery start/resume/finalize seams instead of inventing a new delivery runner.
- Final thread notifications should be generated from the same rendered status/final-review artifacts operators already use locally.
- Blocking and recovery notifications need to hook into the same reason-coded state transitions already emitted by the approved-delivery pipeline.

</code_context>

<specifics>
## Specific Ideas

- Auto-selected the stricter default that healthy-path autonomy should reuse the shipped approved-project delivery backbone rather than creating a second "chat mode" runner.
- Defaulted to keeping all v1.1.2 proof gates active during autonomous continuation so "autonomous" never means "less governed."
- Defaulted to deriving the final chat reply from authoritative final-review/status artifacts, which keeps success and failure reporting aligned with real delivery truth.

</specifics>

<deferred>
## Deferred Ideas

- Rich multi-recipient notification subscriptions remain out of scope for this phase.
- Chat-native operator recovery commands remain future expansion beyond healthy-path autonomy plus explicit blocked reporting.
- Broad workflow-engine replacement or background-service rearchitecture remains out of scope; this phase should extend the existing artifact-driven delivery pipeline.

</deferred>

---

*Phase: 25-autonomous-delivery-to-deploy-and-return-link*
*Context gathered: 2026-05-04*
