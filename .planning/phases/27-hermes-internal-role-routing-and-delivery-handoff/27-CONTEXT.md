# Phase 27: Hermes Internal Role Routing and Delivery Handoff - Context

**Gathered:** 2026-05-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Make Hermes internally orchestrate company roles and delivery specialists so the owner continues talking to one system while Hermes coordinates discovery, qualification, approval preparation, and post-approval handoff behind the scenes.

This phase owns Hermes-internal role routing, visible explanation of which kind of work Hermes is doing without turning roles into user-operated tools, and the internal bridge from approved proposal into the specialist delivery team. It does not define the proposal/approval surface itself, and it does not reopen the technical GitHub/Vercel delivery backbone beyond handing approved work into it.

</domain>

<decisions>
## Implementation Decisions

### Internal company-role orchestration
- **D-01:** Hermes should invoke `ceo`, `scout`, `cmo`, and `arch` as internal collaborators in a governed sequence rather than exposing them as separate operator commands.
- **D-02:** Role handoffs should remain artifact-backed and profile-driven so Hermes can explain progress truthfully without depending on hidden prompt memory.
- **D-03:** The owner should not have to decide which internal role runs next on healthy paths; Hermes owns that routing logic once the project-start intent is accepted.

### Operator-visible abstraction of role work
- **D-04:** Hermes may describe the kind of work happening, such as research, feasibility review, or proposal preparation, but should avoid requiring the owner to address or command specific internal roles directly.
- **D-05:** When a run blocks, Hermes should be able to say which internal role or gate is currently responsible without exposing raw multi-agent choreography as normal workflow.
- **D-06:** Healthy-path updates should frame role activity as Hermes progressing the project, not as the owner being handed off between subsystems.

### Approved-work handoff to delivery specialists
- **D-07:** Once a proposal is approved, Hermes should hand work to the delivery specialist team internally using the existing approved-project bundle and stage-contract seams.
- **D-08:** Delivery specialist orchestration should remain governed by profiles, skills, and stage evidence requirements rather than ad hoc runtime glue assembled per run.
- **D-09:** If Hermes cannot prove the approved bundle or role output needed for handoff, the run should block instead of improvising a delivery kickoff from incomplete context.

### Profile-and-skill governance
- **D-10:** Role routing should stay configured through repo/profile/skill contracts that are inspectable and maintainable, not through one-off prompt branching hidden inside the Hermes conversation surface.
- **D-11:** The internal routing layer should preserve the distinction between company roles and delivery specialists even though the owner experiences them as one Hermes capability.
- **D-12:** Hermes should reuse existing role-specific artifacts and handoff conventions where possible so internal collaboration remains compatible with shipped governance and validation surfaces.

### the agent's Discretion
- Exact routing graph among `ceo`, `scout`, `cmo`, `arch`, and delivery specialists, as long as Hermes remains the only visible operator surface.
- Exact wording for owner-facing progress messages that refer to internal role activity, as long as they stay Hermes-first and non-jargony.
- Exact storage location for any new role-routing trace artifacts, as long as they remain durable and consistent with current governance patterns.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and milestone contract
- `.planning/ROADMAP.md` - Phase 27 goal and success criteria for internal role orchestration and delivery handoff.
- `.planning/REQUIREMENTS.md` - `ROLE-01`, `ROLE-02`, and `ROLE-03`.
- `.planning/PROJECT.md` - milestone requirement that company roles remain Hermes-internal collaborators rather than user-facing tools.
- `.planning/STATE.md` - current planning state and note that Hermes-facing UX must hide internal choreography while preserving real blocked truth.

### Prior decisions that constrain this phase
- `.planning/phases/06-execution-handoff-and-team-readiness/06-CONTEXT.md` - downstream team-readiness and handoff contract patterns that still matter inside Hermes.
- `.planning/phases/18-handoff-contract-and-authority-alignment/18-CONTEXT.md` - shared machine-readable handoff/alignment expectations across stages.
- `.planning/phases/19-specialist-evidence-and-ui-artifact-gates/19-CONTEXT.md` - specialist evidence and `/ui-ux-pro-max` artifact rules that internal Hermes routing must still enforce.
- `.planning/phases/22-conversational-intake-and-run-orchestration/22-CONTEXT.md` - authoritative run/start context that internal role work should inherit.
- `.planning/phases/25-autonomous-delivery-to-deploy-and-return-link/25-CONTEXT.md` - existing autonomous handoff into delivery backbone that Hermes should internalize rather than replace.

### Existing artifacts and orchestration surfaces
- `docs/MULTI_PROFILE_COORDINATION.md` - current multi-profile collaboration model and coordination constraints.
- `docs/STATE_CONTRACT.md` - write-governance rules for any new role-routing or handoff artifacts.
- `assets/workspaces/` - role identity and workspace contracts for `ceo`, `scout`, `cmo`, `arch`, and related collaborators.
- `profiles/` - per-role profile configuration source used to keep routing profile-driven.
- `skills/` - current role and governance skill layout that should remain the internal control plane.

### Existing code and tests
- `scripts/generate_decision_package.py` - existing decision-synthesis seam likely fed by internal discovery/qualification roles.
- `scripts/generate_role_handoffs.py` - current handoff artifact generation seam relevant to internal Hermes routing.
- `scripts/qualify_project_candidates.py` - qualification-stage logic that internal role orchestration must drive.
- `scripts/start_approved_project_delivery.py` - authoritative approved-work handoff into the delivery backbone.
- `tests/test_delivery_handoff_contract.py` - delivery handoff expectations that Hermes-internal routing must satisfy.
- `tests/test_delivery_orchestration_contract.py` - downstream contract expectations for approved bundles and specialist execution.
- `tests/test_qualification_contract.py` - structured qualification output expectations that internal role work must preserve.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `assets/workspaces/*` and `profiles/*`: already encode role identity and profile-driven behavior Hermes can treat as internal collaborators.
- `scripts/generate_role_handoffs.py`: already expresses explicit handoff artifacts rather than leaving collaboration implicit.
- `scripts/qualify_project_candidates.py`: already captures a governed qualification step that internal role routing can trigger.
- `scripts/start_approved_project_delivery.py`: already defines the bundle contract required to hand approved work into specialist delivery.

### Established Patterns
- This repo prefers role/stage boundaries expressed through durable artifacts and profile contracts, not invisible freeform agent improvisation.
- Delivery specialist stages already fail closed on missing evidence, so internal Hermes routing must preserve those prerequisites.
- Operator-facing messaging should summarize work in business terms while the authoritative details live in inspectable artifacts.

### Integration Points
- Hermes-internal routing should likely reuse existing profile and workspace structures rather than inventing a new role definition system.
- Approved-work handoff should terminate at the same approved-project delivery seams already used in v1.2.
- Owner-facing progress updates should derive from role/stage truth rather than direct role transcript exposure.

</code_context>

<specifics>
## Specific Ideas

- Auto-selected a Hermes-owned routing model where roles stay internal collaborators rather than exposed tools.
- Defaulted to profile-and-skill-driven orchestration because the repo already encodes internal responsibilities that way.
- Chose approved-project bundle reuse for delivery handoff so post-approval flow remains compatible with shipped automation and validators.

</specifics>

<deferred>
## Deferred Ideas

- Exact proposal wording and owner approval/rejection interaction belong to Phase 28.
- Final live-link return and blocked recovery reply design belong to Phase 29.
- Broader multi-channel role orchestration beyond the first Hermes operator surface remains future work.

</deferred>

---

*Phase: 27-hermes-internal-role-routing-and-delivery-handoff*
*Context gathered: 2026-05-05*
