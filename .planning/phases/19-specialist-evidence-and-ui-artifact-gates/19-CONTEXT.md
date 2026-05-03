# Phase 19: Specialist Evidence and UI Artifact Gates - Context

**Gathered:** 2026-05-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Harden approved-project specialist delivery so a stage cannot pass unless it leaves behind complete, run-scoped evidence and, for UI work, a validated `/ui-ux-pro-max` artifact tied to the approved brief.

This phase covers specialist-stage evidence gates, UI artifact validation, template-only rejection at the specialist stage boundary, and blocked-state artifacts that explain what is missing and how resume should continue. It does not redefine real product proof rules beyond the specialist-stage gate boundary, and it does not own the full bootstrap/resume regression matrix for recovered runs.

</domain>

<decisions>
## Implementation Decisions

### Specialist evidence bundle
- **D-01:** Every specialist stage must pass through one canonical evidence bundle made of the markdown handoff, transcript evidence, workspace-change inventory, and structured stage-evidence JSON persisted under `.hermes/stage-evidence/`.
- **D-02:** Structured stage evidence is the machine-readable gate record for specialist completion and must carry `run_id`, `stage`, `role`, `handoff_path`, `workspace_change_inventory_path`, and non-empty `evidence_links` for every specialist stage.
- **D-03:** Testing remains stricter than the other specialist stages: its structured evidence must also include explicit verification evidence so testing cannot pass on handoff text alone.

### UI artifact governance
- **D-04:** UI gating applies only to UI delivery surfaces and only to the `design` and `development` specialist stages; non-UI deliveries should not be blocked by `/ui-ux-pro-max` requirements.
- **D-05:** The governed UI artifact pair is `.hermes/ui-ux-design-system.md` plus `.hermes/ui-ux-design-system.summary.json`, and both must exist before a UI specialist stage can be considered ready.
- **D-06:** The UI summary must validate project-specific coverage for screen inventory, primary workflow, monetization surface, multilingual coverage, responsive rules, accessibility rules, and user-state coverage including `empty`, `loading`, `error`, and `success`.
- **D-07:** Development must revalidate the UI artifact against the approved brief contract and fail closed on stale, empty, or drifted design truth rather than treating the design artifact as a one-time file-existence check.

### Substance and template rejection
- **D-08:** Specialist completion must persist explicit substance results alongside the stage event so downstream validators and operator views can see whether the stage was product-specific or template-only.
- **D-09:** Workspace-change inventory is the primary evidence source for classifying specialist work as `product_only`, `protected_platform`, or `blocked_for_missing_information`; missing or unsafe inventories fail closed rather than falling back to optimistic assumptions.
- **D-10:** Template-only specialist output must be rejected at the specialist gate itself, with persisted `template_only`, `issues`, and touched-path evidence recorded in stage events and surfaced to status/review artifacts.

### Blocked-state operator guidance
- **D-11:** When a specialist or UI gate blocks, the authority record, append-only event, and operator-facing status must all preserve the same block reason, evidence path, failed gate name, and resume target so recovery continues from truth instead of re-derivation.
- **D-12:** Phase 19 blocked-state guidance should explain exactly which evidence artifact is missing or stale and what repair action is needed, but the broader recovered-run regression proof remains Phase 21 scope.

### the agent's Discretion
- The exact JSON field layout inside structured stage evidence, as long as the required gate fields and downstream validator needs remain satisfied.
- The precise wording of blocked-state operator messages and repair-action guidance, as long as they stay explicit, machine-linked, and resume-friendly.
- Whether UI artifact preflight writes only a stub contract or a richer starter artifact before specialist execution, as long as missing or stale UI truth still blocks downstream UI stages.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` - Phase 19 scope, goals, key outcomes, and milestone risk framing.
- `.planning/REQUIREMENTS.md` - `GATE-01` to `GATE-03` and `UI-01` to `UI-03`.
- `.planning/PROJECT.md` - v1.1.2 milestone intent and the requirement to treat `/ui-ux-pro-max` as a blocking governed artifact.
- `.planning/STATE.md` - current milestone state and Phase 19 planning readiness.

### Prior decisions that constrain this phase
- `.planning/phases/18-handoff-contract-and-authority-alignment/18-CONTEXT.md` - canonical handoff contract, authority/event/status truth precedence, and operator-facing convergence rules.
- `.planning/phases/12-credential-governance-and-operator-handoff/12-CONTEXT.md` - operator review and authority-above-workspace governance direction that Phase 19 must preserve.
- `.planning/phases/17-authority-and-status-convergence/17-authority-and-status-convergence-01-SUMMARY.md` - recovered current truth must override stale blocked state.
- `.planning/phases/17-authority-and-status-convergence/17-authority-and-status-convergence-02-SUMMARY.md` - authority/event/status/final-review convergence continuation.
- `.planning/phases/17-authority-and-status-convergence/17-authority-and-status-convergence-03-SUMMARY.md` - completion-state recovery expectations carried into Phase 19.

### Existing contracts and runtime surfaces
- `docs/skill-governance/templates/stage-handoff-template-v0.2.md` - canonical nine-section specialist handoff template.
- `docs/skill-governance/templates/final-delivery-template-v0.2.md` - final delivery / final review baseline that downstream gate outputs eventually feed.
- `scripts/start_approved_project_delivery.py` - approved-project orchestrator, specialist dispatch, UI artifact preflight, stage evidence writing, blocking logic, and resume flow.
- `scripts/validate_delivery_handoff.py` - validator-owned specialist handoff and stage-evidence contract.
- `scripts/validate_approved_delivery_pipeline.py` - authority/event/status/final-review cross-link validator including template-only and blocked-state visibility rules.
- `scripts/approved_delivery_governance.py` - workspace-change inventory collection and classification for protected-platform vs product-only decisions.
- `scripts/instantiate_template_project.py` - bootstrap-time `/ui-ux-pro-max` contract language carried into generated workspaces.
- `tests/test_approved_delivery_pipeline_cli.py` - regression expectations for evidence gates, template-only rejection, blocked-state visibility, and recovered-truth behavior.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/start_approved_project_delivery.py`: already contains the specialist stage map, UI artifact constants, allowed block reasons, and gate hooks for UI validation and structured stage evidence.
- `scripts/validate_delivery_handoff.py`: already validates the nine-section handoff contract, stage-evidence JSON, UI artifact summary coverage, and testing verification evidence.
- `scripts/approved_delivery_governance.py`: already classifies workspace changes and persists workspace-change inventory evidence suitable for stage substance gates.
- `scripts/validate_approved_delivery_pipeline.py`: already checks blocked-state visibility, structured evidence linkage, template-only rejection, and current-state precedence across authority, events, status, and final review.
- `tests/test_approved_delivery_pipeline_cli.py`: already provides realistic approved-project fixtures for blocked, resumed, and recovered delivery states.

### Established Patterns
- Governance state is file-backed and fail-closed: authority JSON + append-only JSONL + derived markdown remain the enforced pattern.
- Runtime scripts prefer machine-readable evidence artifacts adjacent to human-readable markdown rather than freeform terminal output.
- Specialist stage gates are expected to persist both current-state truth and operator-readable explanations, not just return process exit codes.
- UI governance should be brief-derived and artifact-backed, not a policy reminder buried in prompts or template docs.

### Integration Points
- Specialist-stage completion flows in `scripts/start_approved_project_delivery.py` are the primary insertion point for Phase 19 gate hardening.
- `scripts/validate_delivery_handoff.py` and `scripts/validate_approved_delivery_pipeline.py` must stay aligned with any new or tightened structured-evidence fields.
- Workspace bootstrap and generated `.hermes` contract files may need small updates so UI artifact expectations and evidence paths are seeded consistently.
- Tests in `tests/test_approved_delivery_pipeline_cli.py` are the natural place to lock new fail-closed evidence and UI artifact scenarios before Phase 20 and Phase 21 build on them.

</code_context>

<specifics>
## Specific Ideas

- `/ui-ux-pro-max` should stop being ceremonial and become a real artifact contract with machine-readable coverage tied back to the approved brief.
- The strongest existing path is to extend the current stage-evidence JSON and status/final-review linkage rather than invent a second evidence system.
- Template-only rejection should happen at specialist-stage completion time, not only at the very end of the delivery pipeline.

</specifics>

<deferred>
## Deferred Ideas

- Real product proof beyond specialist-stage substance checks stays in Phase 20, especially `/demo` and identity-only loophole removal as the canonical final-proof rule.
- Full bootstrap/resume regression hardening across fresh, blocked, resumed, and recovered runs stays in Phase 21 even though Phase 19 must preserve resume-friendly gate data.
- Adding new specialist roles, new delivery stages, or broader operator dashboard surfaces remains out of scope for this phase.

</deferred>

---

*Phase: 19-specialist-evidence-and-ui-artifact-gates*
*Context gathered: 2026-05-04*
