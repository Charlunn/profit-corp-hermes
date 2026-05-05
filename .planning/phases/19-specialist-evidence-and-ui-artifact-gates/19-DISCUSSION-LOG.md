# Phase 19: Specialist Evidence and UI Artifact Gates - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md; this log preserves the auto-selected discussion path.

**Date:** 2026-05-04
**Phase:** 19-specialist-evidence-and-ui-artifact-gates
**Areas discussed:** Specialist evidence bundle, UI artifact governance, Substance and template rejection, Blocked-state operator guidance

---

## Specialist evidence bundle

| Option | Description | Selected |
|--------|-------------|----------|
| Canonical stage evidence bundle | Require handoff markdown, transcript evidence, workspace-change inventory, and structured JSON for every specialist stage | Yes |
| Partial artifact checks | Accept handoff plus whichever extra evidence the stage happened to produce | |
| Handoff-only completion | Let markdown handoff stand in for machine-readable evidence | |

**Auto choice:** Canonical stage evidence bundle
**Notes:** Chosen because `scripts/start_approved_project_delivery.py`, `scripts/validate_delivery_handoff.py`, and the existing CLI tests already assume structured evidence, stage-specific linkage, and non-empty evidence lists. Testing also keeps explicit verification evidence as a stricter subcase.

---

## UI artifact governance

| Option | Description | Selected |
|--------|-------------|----------|
| Brief-derived validated artifact pair | Require `.hermes/ui-ux-design-system.md` and `.summary.json`, validate coverage plus drift against the approved brief | Yes |
| File existence only | Block only when the markdown artifact is missing | |
| Policy-only reminder | Mention `/ui-ux-pro-max` in prompts but do not gate runtime progress | |

**Auto choice:** Brief-derived validated artifact pair
**Notes:** Chosen because the roadmap explicitly calls out project-specific coverage and stale-artifact risk, and current runtime code already has `validate_ui_ux_artifact(...)`, coverage keys, and stale-summary checks ready to be treated as the governed baseline.

---

## Substance and template rejection

| Option | Description | Selected |
|--------|-------------|----------|
| Stage-level substance verdicts | Persist template-only/product-only outcomes with issues and touched-path evidence at each specialist stage | Yes |
| End-of-pipeline only | Defer template-only detection until final validation | |
| Heuristic operator review | Leave substance judgment primarily to manual review text | |

**Auto choice:** Stage-level substance verdicts
**Notes:** Chosen because Phase 19 owns specialist evidence gates, and both `approved_delivery_governance.py` and `validate_approved_delivery_pipeline.py` already model touched-path classification and template-only rejection. Waiting until final validation would weaken the fail-closed requirement.

---

## Blocked-state operator guidance

| Option | Description | Selected |
|--------|-------------|----------|
| Persist explicit block truth | Carry block reason, failed gate, evidence path, and resume target across authority, events, status, and review | Yes |
| Minimal block status | Record only that a stage is blocked | |
| Recompute on resume | Derive missing details later from whatever artifacts remain | |

**Auto choice:** Persist explicit block truth
**Notes:** Chosen because prior phases already established authority/event/status convergence, and Phase 19 needs resume-friendly evidence paths without taking over the larger Phase 21 regression mission.

---

## the agent's Discretion

- Exact stage-evidence JSON field naming beyond the required gate fields.
- The formatting of operator-facing remediation text as long as it stays explicit and linked to real evidence artifacts.
- Whether UI preflight writes a minimal starter artifact or a richer seeded draft before specialist execution.

## Deferred Ideas

- Final product-proof loophole removal remains Phase 20 work.
- Full bootstrap/resume regression matrix remains Phase 21 work.
