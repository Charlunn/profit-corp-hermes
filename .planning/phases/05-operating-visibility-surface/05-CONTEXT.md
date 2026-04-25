# Phase 5: Operating Visibility Surface - Context

**Gathered:** 2026-04-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Expose current state, top risks, top opportunities, and recommended next actions in a concise operator-facing summary layer. This phase should let a solo operator review the daily situation quickly from trusted artifacts and governance state, without introducing a dashboard-first product surface or replacing the underlying artifact chain.

</domain>

<decisions>
## Implementation Decisions

### Freshness and alerts
- **D-01:** The visibility surface should stay calm by default and only elevate exceptions when there is a meaningful issue.
- **D-02:** Blocking states such as governance `blocked`, pending approvals, failed source collection, or clearly stale daily artifacts must be promoted to the top alert area.
- **D-03:** In healthy runs, the view should remain compact instead of rendering warning-heavy status chrome.

### Action framing
- **D-04:** The operator-facing summary should show only the Top 3 next actions.
- **D-05:** The action list should optimize for solo-operator focus rather than acting like a task board or broad work queue.
- **D-06:** Each surfaced action should remain tied back to trusted evidence or governance state instead of becoming a detached recommendation list.

### Source blending
- **D-07:** `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` is the primary anchor for the visibility surface.
- **D-08:** `assets/shared/governance/GOVERNANCE_STATUS.md` and `assets/shared/external_intelligence/LATEST_SUMMARY.md` should overlay current health, freshness, and blocking context on top of the operating decision anchor.
- **D-09:** `assets/shared/execution_packages/EXECUTION_PACKAGE.md` and `assets/shared/board_briefings/BOARD_BRIEFING.md` may be referenced as supporting derived views, but they should not outrank the operating decision package as the main source.

### Claude's Discretion
- Exact markdown structure and section titles for the final visibility artifact
- Exact thresholds or heuristics for when a summary becomes "stale", as long as stale status is explicit and machine-checkable
- Exact formatting of alert severity markers, evidence snippets, and backlink presentation
- Whether the final summary lives as a latest-view markdown artifact only or also emits optional historical snapshots, as long as the latest view remains the operator-default surface

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §Phase 5 — phase goal, success criteria, and the 05-01/05-02 plan split
- `.planning/REQUIREMENTS.md` — `VIZ-01` requirement for at-a-glance operating visibility
- `.planning/PROJECT.md` — project-level priority on solo-operator visibility and trusted daily operating view
- `.planning/STATE.md` — current roadmap position and active planning state

### Prior-phase decisions this phase must preserve
- `.planning/phases/03-decision-package-quality/03-CONTEXT.md` — locks the decision package as the primary conclusion-first artifact and keeps evidence layered with backlinks
- `.planning/phases/04-governance-and-control-layer/04-CONTEXT.md` — locks governance latest-view and block semantics that visibility must read rather than reinterpret
- `.planning/phases/04-governance-and-control-layer/04-RESEARCH.md` — recommends markdown latest-view layering and explicitly defers richer visibility work to Phase 5

### Trusted source artifacts for the visibility read model
- `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` — primary operator decision anchor with conclusions, risks, opportunities, and recommended next steps
- `assets/shared/trace/decision_package_trace.json` — trace sidecar linking visibility content back to shortlist and role outputs
- `assets/shared/governance/GOVERNANCE_STATUS.md` — current pending approvals, active blocks, and recent overrides
- `assets/shared/external_intelligence/LATEST_SUMMARY.md` — latest collection freshness, source failures, and run metadata
- `assets/shared/execution_packages/EXECUTION_PACKAGE.md` — derived execution-focused mirror of the operating package
- `assets/shared/board_briefings/BOARD_BRIEFING.md` — compact executive summary derived from the operating package

### Operational flow and state constraints
- `orchestration/cron/daily_pipeline.prompt.md` — defines the daily artifact-generation sequence the visibility layer must summarize
- `docs/STATE_CONTRACT.md` — governs authoritative state paths and external-intelligence write boundaries
- `docs/OPERATIONS.md` — documents operator status/recovery flow and governance inspection expectations

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`: already provides the clearest conclusion-first source for current situation, risks, opportunities, and next actions.
- `assets/shared/governance/GOVERNANCE_STATUS.md`: already implements a latest-view markdown status surface grouped by pending approvals, blocks, approvals, rejections, and overrides.
- `assets/shared/external_intelligence/LATEST_SUMMARY.md`: already exposes freshness and collection health metadata that can drive stale/failed-state summaries.
- `assets/shared/execution_packages/EXECUTION_PACKAGE.md` and `assets/shared/board_briefings/BOARD_BRIEFING.md`: provide supporting derived summaries that can be referenced without becoming the main anchor.

### Established Patterns
- The repo favors markdown latest-view artifacts over dashboard-first UI surfaces.
- Current trustworthy outputs are layered: latest artifact + trace sidecar + history store, rather than one monolithic system state file.
- Governance and decision outputs already separate authoritative source artifacts from operator-readable summaries, which Phase 5 should preserve.

### Integration Points
- The visibility surface should read from the daily pipeline outputs after Phase 3 and Phase 4 artifacts are generated.
- Governance status and external-intelligence freshness should be merged into the read model without creating new write paths into those authoritative sources.
- The visibility artifact should sit alongside existing shared operator artifacts under `assets/shared/` and remain compatible with cron-first generation.

</code_context>

<specifics>
## Specific Ideas

- The operator view should feel like a fast daily scan, not a long report and not a task-management board.
- The top action area should remain highly focused: only the 3 most important next moves.
- Exceptions should interrupt the calm summary only when something is actually blocked, pending, failed, or stale.
- Source hierarchy should remain explicit: operating decision package first, then freshness/governance overlays, then supporting derived packages.

</specifics>

<deferred>
## Deferred Ideas

- Rich dashboard or interactive UI treatment remains out of scope unless later phases explicitly add a real-time or dashboard capability.
- Broader work-queue or task-board behavior belongs to later execution/collaboration phases, not this visibility layer.
- More advanced multi-user alert routing belongs to future collaboration/team-readiness work.

</deferred>

---

*Phase: 05-operating-visibility-surface*
*Context gathered: 2026-04-25*
