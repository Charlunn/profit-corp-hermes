# Phase 9: Claude Code Delivery Team Orchestration - Context

**Gathered:** 2026-04-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Standardize the Claude Code-powered specialist delivery team, its role boundaries, and its handoff contracts so an approved SaaS project can move through implementation without the owner manually orchestrating every step.

</domain>

<decisions>
## Implementation Decisions

### Delivery team topology
- **D-01:** Use a single delivery orchestrator role to drive the workflow, load the approved project context, and sequence specialist work rather than having the owner manually route each step.
- **D-02:** The specialist team should follow the existing five-stage operating shape already present in the repo: design, development, testing, git versioning, and release readiness.
- **D-03:** Each specialist role should be narrowly responsible for one stage output and should hand off through explicit artifacts instead of freeform chat state.

### Handoff contract
- **D-04:** Every delivery run must start from the same fixed input bundle: approved project brief, template contract, shared-backend guardrails, project identity metadata, and GSD operating constraints.
- **D-05:** Stage handoffs should reuse the existing markdown-first template pattern: one stage summary, declared outputs, evidence links, gate decision, open risks, and next-stage input.
- **D-06:** The final delivery handoff should use a stable operator-facing artifact that summarizes end-to-end outcome, impact surface, verification evidence, gate status, rollback plan, and release recommendation.

### Scope and safety boundaries
- **D-07:** Delivery roles may customize only approved product surfaces and must treat shared auth, payment, entitlement, shared-table, and shared-backend rules as protected platform primitives.
- **D-08:** Scope enforcement should default to “approved brief only”; any request to modify protected platform behavior or expand feature scope must trigger an explicit scope reopen rather than being absorbed silently during delivery.
- **D-09:** Delivery automation should consume the existing conformance gate and governance rules instead of inventing a second parallel safety system.

### Audit trail and replayability
- **D-10:** Hermes should record each major delivery action as a role-attributed workflow event so a run can be replayed from artifacts after the fact.
- **D-11:** Auditability should be dual-surface: machine-readable event metadata for sequencing and a human-readable latest view for operators.
- **D-12:** Replayability should come from stable stage artifacts plus explicit role/action records, not from trying to reconstruct the workflow from raw terminal history.

### Claude's Discretion
- Exact role names, as long as they map cleanly onto the five-stage workflow
- Exact file layout for delivery-run event logs and latest-view summaries
- Exact metadata schema for role/action records, as long as role, action, artifact, timestamp, and outcome remain explicit
- Exact wording of scope-reopen and blocked-delivery statuses

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §Phase 9 — phase goal and success criteria for delivery-team orchestration
- `.planning/REQUIREMENTS.md` — `TEAM-01`, `TEAM-02`, `TEAM-03`, `TEAM-04`, `TEAM-05`, `TEAM-06`
- `.planning/PROJECT.md` — approved-to-delivery factory goal, one-time owner approval gate, and shared-template/shared-backend constraints
- `.planning/STATE.md` — current milestone state and Phase 9 focus

### Prior phase contracts that must carry forward
- `.planning/phases/06-execution-handoff-and-team-readiness/06-CONTEXT.md` — locks the Core 9 handoff model, lightweight readiness metadata, and concise downstream artifact expectations
- `.planning/phases/07-template-assetization-and-platform-contract/07-01-SUMMARY.md` — establishes the governed template registry and canonical contract pattern
- `.planning/phases/08-shared-supabase-backend-guardrails/08-01-SUMMARY.md` — establishes workspace guardrail metadata handoff
- `.planning/phases/08-shared-supabase-backend-guardrails/08-02-SUMMARY.md` — establishes the single conformance gate and shared-backend enforcement path

### Existing operational contracts and templates
- `docs/platform/standalone-saas-template-contract.md` — protected platform layer, safe extension layer, required workspace artifacts, and conformance rules
- `docs/MULTI_PROFILE_COORDINATION.md` — orchestrator-first delegation model, artifact ownership, and shared-state coordination principles
- `docs/STATE_CONTRACT.md` — state boundaries, primary-writer model, approval gates, and governed high-impact action rules
- `docs/OPERATIONS.md` — operator workflow, governed-action path, and visibility/recovery expectations
- `docs/skill-governance/README.md` — normalized skill governance source of truth
- `docs/skill-governance/routing/skill-manifest-v0.2.md` — task routing, loading levels, and unload strategy for specialist skills
- `docs/skill-governance/templates/orchestrator-input-template-v0.2.md` — standard workflow start-input contract
- `docs/skill-governance/templates/stage-handoff-template-v0.2.md` — standard stage handoff artifact shape
- `docs/skill-governance/templates/final-delivery-template-v0.2.md` — standard final delivery artifact shape
- `docs/skill-governance/quick-run/orchestrator-workflow-card.md` — concise execution order and handoff expectations
- `skills/library/normalized/orchestrator-workflow.md` — five-stage orchestrator contract for design → development → testing → git versioning → release readiness

### Existing code and artifact entrypoints
- `scripts/instantiate_template_project.py` — emits `.hermes/project-metadata.json`, `.hermes/shared-backend-guardrails.json`, and `PROJECT_BRIEF_ENTRYPOINT.md`
- `scripts/check_template_conformance.py` — existing blocking conformance gate for template and shared-backend rules
- `orchestration/cron/commands.sh` — existing orchestrated command-entry pattern and governed-action wrapper
- `assets/workspaces/ceo/AGENTS.md` — current orchestrator communication and delegation contract

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `skills/library/normalized/orchestrator-workflow.md` — already defines a five-stage specialist workflow that can be adapted into the delivery-team operating contract.
- `docs/skill-governance/templates/stage-handoff-template-v0.2.md` — already provides a parser-friendly stage handoff structure with outputs, evidence, gate decision, risks, and next-stage input.
- `docs/skill-governance/templates/final-delivery-template-v0.2.md` — already provides a final operator handoff skeleton with test evidence and rollback planning.
- `scripts/instantiate_template_project.py` — already creates the `.hermes` handoff bundle that downstream delivery roles need before implementation starts.
- `scripts/check_template_conformance.py` — already provides the blocking validation surface that delivery roles should respect before handoff or deployment.

### Established Patterns
- The repo prefers markdown-first operational contracts plus small machine-readable sidecars, not app-only state or chat-only coordination.
- Orchestration is centralized: a single orchestrator routes work while specialist actors own distinct artifacts.
- High-impact controls already flow through explicit governance and conformance gates instead of implicit convention.
- Shared platform rules are treated as protected primitives, while product-specific work is expected to stay in safe extension surfaces.

### Integration Points
- Phase 9 should connect the approved-project delivery team to the existing template-instantiation outputs under `.hermes/`.
- Stage sequencing should build on the existing orchestrator-workflow and stage handoff templates instead of inventing a separate delivery grammar.
- Scope enforcement should hook into the current contract/conformance/governance stack, especially `standalone-saas-template-contract.md`, `check_template_conformance.py`, and governed actions.
- Auditability should integrate with the repo’s current latest-view plus machine-readable artifact pattern so later phases can consume delivery history without scraping terminal output.

</code_context>

<specifics>
## Specific Ideas

- Reuse the existing orchestrator pattern so approved-project delivery feels like a professional staged workflow, not a loose collection of one-off agent prompts.
- Keep role boundaries narrow and artifact-driven so the owner approves once, then watches clear stage outputs instead of micromanaging every step.
- Prefer one shared delivery grammar across all generated SaaS projects rather than custom handoff structures per run.

</specifics>

<deferred>
## Deferred Ideas

- Automatic project brief generation and automatic project kickoff belong to Phase 10, not this phase.
- Direct GitHub sync and Vercel deployment execution belong to Phase 11, not this phase.
- Credential-scope controls, deeper audit controls, and final operator review hardening belong to Phase 12, not this phase.
- Expanding into broad multi-user collaboration workflow remains out of scope for this phase.

</deferred>

---

*Phase: 09-claude-code-delivery-team-orchestration*
*Context gathered: 2026-04-27*
