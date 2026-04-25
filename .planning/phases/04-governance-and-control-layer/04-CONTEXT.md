# Phase 4: Governance and Control Layer - Context

**Gathered:** 2026-04-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Make approvals, audit traces, and high-impact decision controls executable within the workflow. This phase should turn the current governance rules from policy text into enforceable gates, auditable governance events, and state-transition controls without adding new product capabilities.

</domain>

<decisions>
## Implementation Decisions

### Governance event model
- **D-01:** Governance events should be recorded in a dedicated governance log instead of being merged into `LEDGER.json` or scattered only across markdown artifacts.
- **D-02:** The governance log should use a JSONL event-stream format so each approval, rejection, override, fallback, and transition event is append-only and machine-checkable.
- **D-03:** Each governance event should carry a full context field set, including at least `action_id`, `event_type`, `actor`, `target_artifact`, `related_decision_package`, `status_before`, `status_after`, `approved_by`, and `timestamp`.
- **D-04:** In addition to the JSONL event stream, the system should maintain a human-readable governance latest view for operator inspection.
- **D-05:** The human-readable governance latest view should organize information by governance action, not as a flat raw timeline.
- **D-06:** Governance actions must be strongly bound to the daily operating decision package so the audit chain always starts from the current authoritative decision layer.

### State progression and blocking
- **D-07:** High-impact actions and critical stage failures should hard-block downstream progression by default rather than silently continuing.
- **D-08:** High-impact actions should be classified primarily by action type, not only by numeric thresholds.
- **D-09:** When a critical step fails, the workflow should stop at the failure point and record a failed governance event instead of auto-rolling back or loosely degrading forward.
- **D-10:** Override authority exists, but only the CEO can explicitly override a hard block and allow the workflow to continue.

### Write permissions and fallback control
- **D-11:** The current primary-writer boundary should remain strict: each governed asset keeps a fixed primary writer rather than broad shared write access.
- **D-12:** If the CEO performs a fallback takeover of another role's primary artifact, that action must create an explicit governance event recording reason, target asset, original primary writer, and the related operating decision package.
- **D-13:** The governance layer should act as a gatekeeping and recording layer only; it must not directly mutate protected underlying state files or business artifacts.
- **D-14:** Existing single-write paths must remain authoritative, such as `manage_finance.py` for ledger mutations and role-specific generators/scripts for their owned outputs.
- **D-15:** The write-permission matrix should be encoded as executable validation rules, not left as documentation-only policy text.

### Claude's Discretion
- Exact file names and directory layout for the governance JSONL stream and latest summary view
- Exact event schema field naming as long as the required context is preserved
- Exact state enum names, failure code strings, and markdown formatting of the latest governance view
- Exact implementation shape of the rule-checking layer, provided it enforces the locked permission and approval decisions above

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §Phase 4 — phase goal, success criteria, and the 04-01/04-02/04-03 plan split
- `.planning/REQUIREMENTS.md` — GOV-01 and GOV-02 requirements for executable approvals and auditable traceability
- `.planning/PROJECT.md` — project-level governance priorities and operator workflow constraints
- `.planning/STATE.md` — confirms Phase 4 is the active next focus after Phase 3 completion

### Existing governance and operating rules
- `docs/STATE_CONTRACT.md` — current state layers, write-permission matrix, transition order, concurrency rules, and approval gates that Phase 4 must convert into executable enforcement
- `docs/OPERATIONS.md` — operator incident handling, audit trigger paths, cron pause/resume controls, and practical recovery expectations
- `skills/common/run_accountant_audit.md` — existing audit-path intent that should remain aligned with executable governance enforcement

### Prior phase outputs this phase must govern
- `.planning/phases/03-decision-package-quality/03-CONTEXT.md` — Phase 3 locked the operating decision package as the primary decision artifact and requires downstream governance to bind back to it
- `.planning/phases/03-decision-package-quality/03-VERIFICATION.md` — confirms the decision package / execution package / board briefing chain now exists and is ready to be governed
- `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` — authoritative daily decision artifact that governance events must reference
- `assets/shared/trace/decision_package_trace.json` — current trace sidecar that Phase 4 governance links should extend rather than bypass

### Codebase patterns and constraints
- `.planning/codebase/CONVENTIONS.md` — scripting conventions, fail-fast shell style, and explicit operator messaging patterns
- `.planning/codebase/INTEGRATIONS.md` — current Hermes CLI and local-file integration boundaries

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `docs/STATE_CONTRACT.md`: already defines the state layers, write-permission matrix, transition order, and approval gates that Phase 4 should operationalize.
- `docs/OPERATIONS.md`: already defines incident and audit procedures that can anchor executable governance behavior.
- `assets/shared/manage_finance.py`: existing single-path mutation mechanism for ledger changes should remain the only ledger write route.
- `assets/shared/AUDIT_LOG.csv`: existing financial audit trail pattern shows the repo already values append-style audit outputs, even though Phase 4 should use a dedicated governance stream.
- `orchestration/cron/commands.sh`: existing pause/resume and recovery commands are natural integration points for governance-controlled state progression.

### Established Patterns
- Shared business state is file-based and repo-local rather than database-backed, so governance should extend local artifact workflows instead of introducing a new persistence system.
- The repo already enforces special write paths for sensitive assets, especially the ledger, so Phase 4 should add gating around those paths rather than replace them.
- Operator-facing workflows prefer explicit scripts, markdown artifacts, and auditable append behavior over hidden automation.

### Integration Points
- Approval and override enforcement should sit in front of high-impact actions before downstream mutation scripts run.
- Governance records should connect the operating decision package from Phase 3 to later state and finance actions.
- State progression logic should integrate with existing daily pipeline and incident-handling flows, especially cron pause/resume and accountant audit triggers.

</code_context>

<specifics>
## Specific Ideas

- Governance should feel like a real operating control layer, not a loose reminder system.
- The latest governance view should help the operator quickly answer: what is pending, what was approved, what was rejected, what was overridden, and what is currently blocked.
- Hard-blocks should be the default posture for impactful actions; override should exist but remain exceptional and CEO-controlled.
- The audit chain should start from the daily operating decision package instead of letting governance drift into an unrelated parallel track.

</specifics>

<deferred>
## Deferred Ideas

- Rich operator dashboard presentation of governance state belongs to Phase 5 rather than this phase.
- Multi-user/team approval workflows and broader collaboration models remain for later phases.
- More granular state enum design and failure-code taxonomy can be refined during planning and implementation as long as the blocking semantics above stay locked.

</deferred>

---

*Phase: 04-governance-and-control-layer*
*Context gathered: 2026-04-25*
