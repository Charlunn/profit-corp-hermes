# Phase 10: Approved Project Delivery Pipeline - Context

**Gathered:** 2026-04-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Turn a one-time owner approval into an automated project-delivery pipeline that creates a delivery-ready project brief, instantiates a workspace from the governed template, tracks pipeline state from initialization through handoff, and blocks cleanly when required preconditions are missing.

</domain>

<decisions>
## Implementation Decisions

### Approval-to-delivery trigger
- **D-01:** The pipeline must start from a single explicit owner approval signal rather than repeated manual kickoff commands after approval.
- **D-02:** Approval should produce a delivery-ready project record that becomes the single source of truth for the downstream pipeline run.
- **D-03:** The delivery trigger should reuse the existing orchestrator-first command pattern rather than inventing a separate long-running service or UI-first control plane.

### Project brief generation
- **D-04:** Hermes should generate one structured delivery-ready project brief from the approved opportunity before any workspace instantiation begins.
- **D-05:** The brief must carry enough implementation context for the Phase 9 delivery team to begin immediately: project identity, approved scope, target user, MVP framing, constraints, and acceptance gates.
- **D-06:** Brief generation should be deterministic and artifact-first, not dependent on reconstructing prior chat context.

### Workspace instantiation and attachment
- **D-07:** The pipeline should instantiate the new SaaS project from the governed shared template automatically once approval and brief generation pass.
- **D-08:** The instantiated workspace must be linked to the approved project brief and existing `.hermes` metadata/guardrail artifacts as part of pipeline initialization.
- **D-09:** Phase 10 should reuse the current template-instantiation and conformance foundations rather than duplicating template bootstrap logic.

### Delivery state model
- **D-10:** Hermes should track delivery state as a durable, operator-readable pipeline record with explicit stage/status transitions from approval through handoff.
- **D-11:** Delivery state should remain dual-surface: machine-readable workflow state plus a concise human-readable latest view.
- **D-12:** State progression should align to the Phase 9 delivery workflow stages, so later execution and replay do not need a translation layer.

### Blocking and failure behavior
- **D-13:** Missing preconditions should hard-block the pipeline with explicit reasons instead of silently skipping steps or degrading forward.
- **D-14:** Block conditions in this phase include missing approval, missing brief inputs, failed workspace instantiation, failed contract/guardrail validation, or missing required downstream delivery prerequisites.
- **D-15:** Blocked runs should persist enough state and evidence for later resume/retry rather than forcing the owner to restart from scratch.

### Claude's Discretion
- Exact artifact names for the approved-project record and latest-view status surfaces
- Exact enum values for pipeline stage and block reasons, as long as they remain stable and operator-readable
- Exact command entrypoints for triggering and resuming the pipeline
- Exact field ordering inside the generated project brief and delivery state artifacts

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §Phase 10 — phase goal and success criteria for the approved-project delivery pipeline
- `.planning/REQUIREMENTS.md` — `PIPE-01`, `PIPE-02`, `PIPE-03`, `PIPE-04`, `PIPE-05`, `PIPE-06`, `PIPE-07`
- `.planning/PROJECT.md` — approved-to-delivery factory goal, one-time owner approval gate, and minimal-manual-work objective
- `.planning/STATE.md` — current project position after Phase 9 completion

### Prior phase contracts that must carry forward
- `.planning/phases/07-template-assetization-and-platform-contract/07-01-SUMMARY.md` — governed template registry and canonical contract authority
- `.planning/phases/08-shared-supabase-backend-guardrails/08-01-SUMMARY.md` — `.hermes` guardrail metadata handoff from template instantiation
- `.planning/phases/08-shared-supabase-backend-guardrails/08-02-SUMMARY.md` — single conformance gate and shared-backend enforcement path
- `.planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md` — locked delivery-team boundaries, fixed input bundle, and replay/governance decisions
- `.planning/phases/09-claude-code-delivery-team-orchestration/09-RESEARCH.md` — architecture and runtime patterns for delivery-run bootstrap, state, and scope governance
- `.planning/phases/09-claude-code-delivery-team-orchestration/09-VERIFICATION.md` — confirms the delivery team, workspace-local event/state model, and governed scope reopen path now exist

### Existing operational contracts and templates
- `docs/platform/standalone-saas-template-contract.md` — required workspace artifacts, protected platform rules, and conformance expectations
- `docs/MULTI_PROFILE_COORDINATION.md` — orchestrator-first sequencing and artifact ownership rules
- `docs/STATE_CONTRACT.md` — approval gates, primary-writer boundaries, and state mutation constraints
- `docs/OPERATIONS.md` — operator workflow, governed action path, and latest-view expectations
- `docs/skill-governance/templates/orchestrator-input-template-v0.2.md` — delivery-start input contract that now expects the approved-project bundle
- `docs/skill-governance/templates/stage-handoff-template-v0.2.md` — per-stage handoff contract consumed by the Phase 9 delivery team
- `docs/skill-governance/templates/final-delivery-template-v0.2.md` — final operator handoff artifact contract
- `skills/library/normalized/orchestrator-workflow.md` — fixed five-stage delivery workflow

### Existing code and pipeline entrypoints
- `scripts/instantiate_template_project.py` — template workspace bootstrap and `.hermes` metadata generation
- `scripts/check_template_conformance.py` — existing blocking conformance gate for generated workspaces
- `scripts/start_delivery_run.py` — initializes workspace-local delivery run state from the approved bundle
- `scripts/append_delivery_event.py` — role-attributed delivery event writer
- `scripts/render_delivery_status.py` — latest-view renderer from the delivery event stream
- `scripts/request_scope_reopen.py` — governance-backed scope reopen wrapper
- `scripts/validate_delivery_handoff.py` — stage/final handoff validator and replay checker
- `orchestration/cron/commands.sh` — operator command-entry pattern now extended with delivery commands
- `assets/workspaces/ceo/AGENTS.md` — current CEO orchestration and delegation contract

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/instantiate_template_project.py` already knows how to create a governed workspace from the shared template and seed `.hermes/project-metadata.json`, `.hermes/shared-backend-guardrails.json`, and `PROJECT_BRIEF_ENTRYPOINT.md`.
- `scripts/check_template_conformance.py` already provides the single blocking conformance gate that Phase 10 should reuse after instantiation.
- `scripts/start_delivery_run.py`, `scripts/append_delivery_event.py`, and `scripts/render_delivery_status.py` already provide the runtime foundation for a delivery-ready workspace once the approved bundle exists.
- `docs/skill-governance/templates/orchestrator-input-template-v0.2.md` already encodes the approved-project delivery bundle fields Phase 10 must generate.
- `orchestration/cron/commands.sh` already provides a command-wrapper pattern for starting and supervising pipeline steps.

### Established Patterns
- The repo prefers artifact-first, script-driven workflows over interactive service state or UI-only control planes.
- High-impact progression is governed by explicit blocking gates, append-only event/state records, and human-readable latest views.
- Workspace-local `.hermes` artifacts are the durable bridge between template instantiation and downstream delivery execution.
- Delivery orchestration is already normalized as a fixed staged workflow, so Phase 10 should feed that workflow instead of redefining it.

### Integration Points
- Phase 10 should connect owner approval to `instantiate_template_project.py`, then attach the resulting workspace to the Phase 9 delivery-run bootstrap path.
- The generated project brief must become a first-class input artifact for `start_delivery_run.py` and the delivery orchestrator.
- Pipeline state tracking should sit above workspace bootstrap and delivery-run execution, with clear block/resume semantics when prerequisites fail.
- Contract/conformance failures should route through the existing validation path rather than custom ad-hoc stop logic.

</code_context>

<specifics>
## Specific Ideas

- Treat approval-to-delivery as a true pipeline handoff, not a loose sequence of manual operator commands.
- Keep the project brief and delivery state artifacts stable enough that later automation phases can pick them up without guessing.
- Make blocked states feel explicit and resumable, so operators see exactly why automation stopped and what input is missing.

</specifics>

<deferred>
## Deferred Ideas

- GitHub repository sync, branch linkage, and deployment linkage belong to Phase 11, not this phase.
- Credential-scope controls, deployment audit hardening, and final operator review surfaces beyond the handoff state belong to Phase 12.
- Broad multi-project analytics and portfolio-level dashboards remain out of scope for this phase.
- Product-specific feature implementation remains out of scope; this phase is about pipeline automation, not shipping a customer app itself.

</deferred>

---

*Phase: 10-approved-project-delivery-pipeline*
*Context gathered: 2026-04-27*
