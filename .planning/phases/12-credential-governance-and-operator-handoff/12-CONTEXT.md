# Phase 12: Credential Governance and Operator Handoff - Context

**Gathered:** 2026-04-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Keep the approved-project delivery pipeline safe and operator-trustworthy by constraining how platform-managed GitHub/Vercel credentials are used, making high-impact shipping actions auditable, requiring explicit justification before protected platform primitives are changed, and producing a final operator-facing review surface that clearly shows blocked, failed, and completed delivery outcomes.

</domain>

<decisions>
## Implementation Decisions

### Credential access path
- **D-01:** Phase 12 should keep GitHub and Vercel automation credentials inside one documented platform-controlled script path rather than exposing open-ended arbitrary CLI usage to delivery roles.
- **D-02:** Credential-bearing actions should be limited to the approved delivery chain already established in Phases 10-11: repository preparation, code sync, Vercel linkage, environment application, and deployment execution.
- **D-03:** The authority layer above the workspace should remain the control point for credentialed actions, so credentials are exercised through approved-project records and persisted stage state rather than direct workspace-local improvisation.

### Action restrictions and audit trail
- **D-04:** Every credentialed GitHub/Vercel action should emit a durable audit artifact that records the action type, target project/repository, outcome, evidence path, and operator-relevant linkage back to the approved delivery run.
- **D-05:** Auditability should extend the existing append-only event-stream pattern instead of introducing a second disconnected logging system.
- **D-06:** Failed or blocked credentialed actions must persist explicit reasons and evidence in both machine-readable authority artifacts and the human-readable latest review surface.

### Platform-change justification boundary
- **D-07:** Phase 12 must distinguish product-level delivery changes from protected platform-level changes by checking touched files and known protected surfaces before credentialed sync/deploy steps proceed.
- **D-08:** Any attempt to modify protected template primitives or shared-backend contracts should require an explicit platform-justification artifact and a governed approval path before the pipeline can continue.
- **D-09:** The platform-justification path should reuse existing governance/conformance contracts where possible instead of inventing a separate approval language just for deployment.

### Operator handoff and review surface
- **D-10:** Operators should get one final review artifact at the approved-project authority layer that summarizes approval status, blocked prerequisites, GitHub/Vercel outcomes, platform-justification decisions, and final handoff status in one place.
- **D-11:** The review surface should prioritize exception visibility — blocked deliveries, approval failures, deployment failures, and protected-platform modification attempts — rather than a verbose success-only transcript.
- **D-12:** The operator-facing review artifact should stay artifact-first and file-based, consistent with existing Hermes status surfaces, not depend on a separate dashboard or service UI.

### Claude's Discretion
- Exact filenames and schema shapes for new credential-governance and operator-review artifacts, as long as action scope, outcome, evidence, and authority linkage remain explicit.
- Exact mechanism for mapping touched paths to product-level vs platform-level changes, as long as protected template/shared-backend primitives are deterministically recognized.
- Exact wrapper split between new dedicated governance scripts and extensions to existing Phase 11 helpers, as long as credential use remains constrained and auditable.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §Phase 12 — phase goal and success criteria for credential controls, audit trail, platform justification, and operator review
- `.planning/REQUIREMENTS.md` — `GOV-01`, `GOV-02`, `GOV-03`, `GOV-04`, `GOV-05`, `GOV-06`
- `.planning/PROJECT.md` — approved-to-delivery factory goal, one-time owner approval gate, shared-template/shared-backend constraints, and deployment ambition
- `.planning/STATE.md` — current phase position plus existing note that full automation needs explicit credential/permission/release-boundary design

### Prior phase contracts that must carry forward
- `.planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md` — delivery-team scope boundaries, protected-platform primitives, and role-attributed audit expectations
- `.planning/phases/10-approved-project-delivery-pipeline/10-CONTEXT.md` — authority-layer pipeline record, blocked/resume semantics, and operator-readable status expectations
- `.planning/phases/11-github-and-vercel-automation/11-CONTEXT.md` — constrained GitHub/Vercel delivery path, linkage metadata, and deferred Phase 12 governance hardening boundary

### Existing governance and platform contracts
- `docs/STATE_CONTRACT.md` — governed high-impact action rules and state mutation boundaries
- `docs/OPERATIONS.md` §Approved project delivery pipeline — start/status/validate/resume path and blocked prerequisite handling expectations
- `docs/platform/standalone-saas-template-contract.md` — protected platform layer, protected behavior rules, and conformance gate expectations
- `docs/MULTI_PROFILE_COORDINATION.md` — orchestrator-first sequencing and artifact ownership rules for high-impact actions

### Existing code and automation entrypoints
- `scripts/start_approved_project_delivery.py` — authority-level approved-project pipeline orchestration and current GitHub/Vercel action flow
- `scripts/render_approved_delivery_status.py` — current operator-facing latest-view renderer spanning approval, GitHub, Vercel, and final handoff linkage
- `scripts/validate_approved_delivery_pipeline.py` — current cross-link validation for authority artifacts, blocked evidence, GitHub linkage, and Vercel linkage
- `scripts/github_delivery_common.py` — GitHub credential-gated repository preparation and sync helpers
- `scripts/vercel_delivery_common.py` — Vercel credential-gated linkage, env contract, and deploy helpers
- `orchestration/cron/commands.sh` — approved-delivery wrapper commands and governed operator entry pattern

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/github_delivery_common.py` already centralizes GitHub repository creation/attach and sync operations, including blocked outputs for missing `gh` or GitHub auth.
- `scripts/vercel_delivery_common.py` already centralizes Vercel linkage, env-contract application, deploy gating, and blocked outputs for missing `VERCEL_TOKEN` or incomplete prerequisites.
- `scripts/start_approved_project_delivery.py` already owns the stage machine and allowed block reasons for approval → handoff progression, making it the natural place to enforce credential-governance and platform-justification checks.
- `scripts/render_approved_delivery_status.py` already builds a concise operator latest view from append-only events and shipping metadata.
- `scripts/validate_approved_delivery_pipeline.py` already validates blocked evidence, final handoff linkage, and GitHub/Vercel metadata visibility in the status surface.

### Established Patterns
- High-impact workflow actions are represented as explicit stages with durable `block_reason`, `evidence_path`, and resume semantics.
- The repo prefers script-driven wrappers plus append-only artifacts over hidden service state or freeform manual operator steps.
- Protected platform behavior is already codified in the template contract rather than inferred ad hoc from product workspaces.
- Operator surfaces are markdown-first latest views derived from machine-readable artifacts, not bespoke UIs.

### Integration Points
- Phase 12 should sit directly on top of the Phase 11 authority pipeline, wrapping or extending credential-bearing GitHub/Vercel stages instead of replacing them.
- Platform-vs-product change detection should integrate with the template contract and conformance expectations before repository sync/deploy proceeds.
- Audit artifacts for credential use should flow into the same approved-project event stream and status rendering path already used by the delivery pipeline.
- Final operator review should be produced at the approved-project authority directory so one artifact summarizes approval, shipping, governance, and handoff state together.

</code_context>

<specifics>
## Specific Ideas

- Treat credentials as platform capabilities that delivery automation may borrow only through a narrow approved path, not as general operator shell powers.
- Make protected-platform modification attempts feel visible and governable before code leaves Hermes for GitHub/Vercel.
- Favor a calm one-file operator review with strong exception surfacing over scattered evidence files that require manual reconstruction.

</specifics>

<deferred>
## Deferred Ideas

- Secret storage backends, vault rotation systems, or enterprise secret-management migrations are beyond this phase unless needed to satisfy the documented platform-controlled path.
- Multi-environment release governance beyond the current first-deploy path remains out of scope.
- Broader portfolio dashboards or centralized fleet analytics belong in a future milestone, not this operator handoff phase.

</deferred>

---

*Phase: 12-credential-governance-and-operator-handoff*
*Context gathered: 2026-04-27*
