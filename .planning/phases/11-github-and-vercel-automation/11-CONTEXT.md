# Phase 11: GitHub and Vercel Automation - Context

**Gathered:** 2026-04-27
**Status:** Ready for planning

<domain>
## Phase Boundary

Use platform-managed credentials to take a generated SaaS workspace from approved-delivery state into GitHub repository sync, Vercel project linkage, environment configuration, deploy execution, and delivery outcome reporting.

</domain>

<decisions>
## Implementation Decisions

### GitHub repository authority
- **D-01:** Phase 11 should start from the existing Phase 10 approved-project authority bundle and workspace linkage, not from ad-hoc repository commands run directly against a workspace.
- **D-02:** Repository preparation should support both creating a new GitHub repository and attaching to a pre-existing approved target repository, with the authority record capturing which path was used.
- **D-03:** GitHub automation should use a constrained platform-managed CLI/token path oriented to repository bootstrap and code sync only, not a generic arbitrary GitHub operator shell.

### Code sync and branch linkage
- **D-04:** Generated project code should sync to one canonical default branch per approved project run, with the authority record persisting repository URL/name, default branch, and delivery-run linkage.
- **D-05:** Initial sync should favor deterministic full-project bootstrap semantics over PR-first or multi-branch collaboration flows, because this phase is about first deployment readiness for a newly generated SaaS.
- **D-06:** Sync failures must hard-block downstream deployment and persist explicit evidence in the approved-project status layer rather than letting Vercel steps run on stale or partial repository state.

### Vercel project linkage and environment setup
- **D-07:** Vercel automation should attach the generated workspace to one deployable Vercel project per approved SaaS and persist the Vercel project identifier/linkage in the authority record.
- **D-08:** Deployment environment values should be applied through a declared required-variable contract before deployment, not by relying on manual dashboard setup after code sync.
- **D-09:** Environment configuration should distinguish reusable platform-level variables from project-identity values derived from the approved bundle so the deploy path stays repeatable across SaaS projects.

### Deployment gating and outcome reporting
- **D-10:** Deployment should only trigger after GitHub sync, Vercel linkage, and required environment configuration all pass explicit checks.
- **D-11:** Missing credentials, missing repository linkage, missing Vercel linkage, or missing required environment values should produce durable blocked states with evidence paths and resume points instead of silent skips.
- **D-12:** Deployment success or failure should flow back into both the approved-project authority surface and the workspace-local handoff artifacts so operators can trace one run from approval through deploy result.

### Claude's Discretion
- Exact artifact names and JSON schema additions for GitHub/Vercel linkage metadata, as long as repo, branch, Vercel project, deploy status, and evidence links stay explicit.
- Exact command wrapper names and script boundaries for GitHub/Vercel helpers, as long as they remain consistent with the existing `orchestration/cron/commands.sh` pattern.
- Exact split between separate GitHub and Vercel helper scripts versus one higher-level orchestrator helper, as long as blocking/resume semantics remain stable.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §Phase 11 — phase goal and success criteria for GitHub sync, Vercel linkage, environment setup, and deployment execution
- `.planning/REQUIREMENTS.md` — `SHIP-01`, `SHIP-02`, `SHIP-03`, `SHIP-04`, `SHIP-05`, `SHIP-06`, `SHIP-07`, `SHIP-08`
- `.planning/PROJECT.md` — approved-to-delivery factory goal, shared template/backend constraints, and deployment ambition
- `.planning/STATE.md` — current milestone position and existing blocker note about credential/permission/release-boundary design

### Prior phase contracts that must carry forward
- `.planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md` — locked delivery-team boundaries, auditability expectations, and artifact-first orchestration model
- `.planning/phases/10-approved-project-delivery-pipeline/10-CONTEXT.md` — approved-project authority bundle, workspace linkage, blocked/resume semantics, and deferred Phase 11 handoff boundary

### Existing operator and governance flow
- `docs/OPERATIONS.md` §Approved project delivery pipeline — start/status/resume/validate workflow and blocked prerequisite handling expectations
- `docs/STATE_CONTRACT.md` — state mutation boundaries and governed high-impact action rules that Phase 11 must respect
- `docs/MULTI_PROFILE_COORDINATION.md` — orchestrator-first sequencing and artifact ownership rules
- `docs/platform/standalone-saas-template-contract.md` — governed template contract and platform-primitive boundaries that deployment automation must preserve

### Existing code and automation entrypoints
- `orchestration/cron/commands.sh` — normalized command-wrapper pattern and current approved-delivery entrypoints to extend for Phase 11
- `scripts/start_approved_project_delivery.py` — approved-project authority record, blocking model, workspace bootstrap, and resume/finalize logic
- `scripts/render_approved_delivery_status.py` — authority-surface status rendering pattern for operator-visible latest view
- `scripts/validate_approved_delivery_pipeline.py` — cross-link validation pattern spanning authority artifacts, workspace artifacts, blocked evidence, and final handoff
- `scripts/start_delivery_run.py` — workspace-local delivery manifest, scope file, and event bootstrap contract
- `scripts/render_delivery_status.py` — workspace-local latest-view rendering pattern from append-only delivery events
- `scripts/validate_delivery_handoff.py` — replay/validation expectations for workspace-local stage and final handoff artifacts
- `tests/test_approved_delivery_pipeline_cli.py` — CLI wrapper and approved-delivery status/validation behavior already locked by tests
- `tests/test_project_delivery_pipeline_bootstrap.py` — existing blocked-state, resume, final-handoff, and downstream prerequisite persistence patterns that Phase 11 should extend

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/start_approved_project_delivery.py` already provides the approved-project authority record, durable pipeline stages, block reasons, evidence-path persistence, and resume/finalize flow that GitHub/Vercel automation should extend rather than replace.
- `scripts/render_approved_delivery_status.py` already provides the operator-facing latest-view pattern for surfacing workspace path, blocked evidence, run linkage, and final handoff references.
- `scripts/validate_approved_delivery_pipeline.py` already proves cross-links between authority artifacts and workspace artifacts; Phase 11 can expand this validator with repository/deployment linkage checks.
- `scripts/start_delivery_run.py`, `scripts/render_delivery_status.py`, and `scripts/validate_delivery_handoff.py` already provide the workspace-local manifest/event/status contract where deploy results can be attached.
- `orchestration/cron/commands.sh` already exposes stable shell entrypoints for start/render/validate/resume flows and is the natural place to add GitHub/Vercel operator commands.

### Established Patterns
- The repo prefers script-driven, artifact-first orchestration with append-only events and human-readable latest views instead of hidden service state.
- Blocking conditions are treated as first-class workflow states with explicit `block_reason`, `evidence_path`, and `resume_from_stage` data.
- Authority-level approved-project records sit above workspace-local `.hermes` artifacts; Phase 11 should preserve that layering instead of collapsing everything into workspace-only state.
- Command entrypoints are normalized through `orchestration/cron/commands.sh`, with Python scripts holding the durable business logic.

### Integration Points
- Phase 11 should attach after Phase 10 `delivery_run_bootstrap` and before final operator handoff, enriching the approved-project authority record with repo/deploy metadata.
- GitHub/Vercel automation should consume approved-project identity data and workspace path already persisted by `scripts/start_approved_project_delivery.py`.
- Deployment prerequisite evidence should plug into the existing blocked-state reporting already referenced by `DELIVERY_PIPELINE_STATUS.md` and validated in tests.
- Final deployment outcome should feed both the authority validator path and the workspace-local `.hermes/FINAL_DELIVERY.md` / delivery-events stream.

</code_context>

<specifics>
## Specific Ideas

- Keep Phase 11 as a continuation of the approved-project pipeline rather than a separate deployment subsystem.
- Favor deterministic first-deploy automation for a newly generated SaaS over review-heavy collaboration flows like PR creation or multi-branch promotion.
- Treat GitHub repository linkage, Vercel project linkage, and required environment values as explicit tracked artifacts, not implicit external knowledge.

</specifics>

<deferred>
## Deferred Ideas

- Fine-grained credential scoping, credential storage hardening, and broader deployment audit controls belong to Phase 12.
- Multi-environment promotion workflows such as staging/preview/prod matrices are outside this phase unless required for basic Vercel deployability.
- Team collaboration features such as PR review loops, release approvals, or branch protection orchestration are beyond this first automation boundary.

</deferred>

---

*Phase: 11-github-and-vercel-automation*
*Context gathered: 2026-04-27*
