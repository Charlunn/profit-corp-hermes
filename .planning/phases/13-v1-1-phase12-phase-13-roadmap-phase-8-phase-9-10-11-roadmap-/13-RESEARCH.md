# Phase 13: v1.1 Audit Closure - Research

**Researched:** 2026-04-28
**Domain:** verification closure, planning-state reconciliation, and live operator UAT
**Confidence:** HIGH

<user_constraints>
## User Constraints

No phase-specific `*-CONTEXT.md` exists in the Phase 13 directory yet, so the effective scope comes from the user request plus current planning docs. [VERIFIED: codebase read `.planning/phases/13-v1-1-phase12-phase-13-roadmap-phase-8-phase-9-10-11-roadmap-`] [VERIFIED: codebase read `.planning/ROADMAP.md`]

### Locked Scope
- Cover formal verification/closure for Phase 8 Shared Supabase Backend Guardrails. [VERIFIED: codebase read `.planning/ROADMAP.md`]
- Repair roadmap/requirements/state drift for Phases 9, 10, and 11, plus normalize the malformed Phase 13 roadmap entry. [VERIFIED: codebase read `.planning/ROADMAP.md`] [VERIFIED: codebase read `.planning/REQUIREMENTS.md`] [VERIFIED: codebase read `.planning/STATE.md`]
- Complete final human UAT closure for Phase 11 GitHub + Vercel automation. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`]

### Out of Scope
- No net-new delivery-factory feature area is implied by current evidence; this phase is an audit/remediation/closure phase, not a new product capability phase. [VERIFIED: codebase read `.planning/ROADMAP.md`] [VERIFIED: codebase read `.planning/STATE.md`]
</user_constraints>

## Summary

Phase 13 should be treated as a closure phase with three responsibilities: convert Phase 8 from “implemented but not formally closed” into a verified phase, execute the deferred live human UAT that still blocks true closure for Phase 11, and then reconcile the canonical planning surfaces so ROADMAP, REQUIREMENTS, and STATE match the evidence already present in Phases 8-12. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-01-SUMMARY.md`] [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-02-SUMMARY.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`] [VERIFIED: codebase read `.planning/ROADMAP.md`] [VERIFIED: codebase read `.planning/REQUIREMENTS.md`] [VERIFIED: codebase read `.planning/STATE.md`]

The current drift is concrete, not speculative: Phase 8 has completion summaries and full BACK requirement completion claims in its plan summaries but no `08-VERIFICATION.md`; ROADMAP still marks Phases 8-11 as planned/incomplete in multiple places even though 9/10/11 each have passing verification files and 8 has completed execution summaries; REQUIREMENTS still leaves `BACK-01..06` and `TEAM-01..06` unchecked even though Phase 8 and 9 artifacts claim those requirements are complete; and STATE progress metadata still reports only 5 completed phases and 38% progress despite completed verification artifacts for Phases 7, 9, 10, 11, and 12. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-01-SUMMARY.md`] [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-02-SUMMARY.md`] [VERIFIED: codebase read `.planning/phases/09-claude-code-delivery-team-orchestration/09-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/10-approved-project-delivery-pipeline/10-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/12-credential-governance-and-operator-handoff/12-VERIFICATION.md`] [VERIFIED: codebase read `.planning/REQUIREMENTS.md`] [VERIFIED: codebase read `.planning/ROADMAP.md`] [VERIFIED: codebase read `.planning/STATE.md`]

**Primary recommendation:** Decompose Phase 13 into three ordered plans: (1) Phase 8 formal verification artifact + closure evidence, (2) Phase 11 live human UAT execution and closure evidence, and (3) canonical planning-state reconciliation for Phases 8-13 after the evidence base is complete. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`] [VERIFIED: codebase read `.planning/ROADMAP.md`] [VERIFIED: codebase read `.planning/STATE.md`]

## Project Constraints (from CLAUDE.md)

- If a plan in this phase grows into frontend UI implementation or visual redesign work, `/ui-ux-pro-max` must be invoked first; otherwise the rule does not apply. [VERIFIED: codebase read `CLAUDE.md`]
- The current Phase 13 scope is planning/verification/UAT/documentation oriented, so no frontend-specific skill invocation is required by default. [VERIFIED: codebase read `CLAUDE.md`] [VERIFIED: codebase read `.planning/ROADMAP.md`]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Phase 8 formal closure | API / Backend | Database / Storage | Closure evidence is produced from Python validation/tests and phase artifacts, not browser behavior. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`] |
| Phase 11 live GitHub/Vercel UAT | API / Backend | Database / Storage | The live flow depends on CLI-driven repo/deploy automation and authority/workspace artifacts. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-RESEARCH.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`] |
| Roadmap/requirements/state reconciliation | Database / Storage | API / Backend | Canonical truth is persisted in markdown/state artifacts consumed by the workflow. [VERIFIED: codebase read `.planning/ROADMAP.md`] [VERIFIED: codebase read `.planning/REQUIREMENTS.md`] [VERIFIED: codebase read `.planning/STATE.md`] |
| Operator-visible closure evidence | Frontend Server (SSR/orchestrator host) | Database / Storage | Operators consume generated markdown verification/status/handoff artifacts rather than a UI app. [VERIFIED: codebase read `.planning/phases/10-approved-project-delivery-pipeline/10-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`] |

## Standard Stack

### Core
| Library / Tool | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.11.15 | Run existing unittest verification and CLI-based audit/validation flows | Existing phase validation and verification artifacts are all built around Python scripts and `unittest`. [VERIFIED: local env `python --version`] [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`] |
| `unittest` | stdlib | Re-run Phase 8 and Phase 11 automated suites before writing closure artifacts | Existing validation contracts already specify unittest commands. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`] [VERIFIED: codebase read `.planning/phases/10-approved-project-delivery-pipeline/10-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`] |
| Markdown planning artifacts | repo-native | Canonical closure surfaces for verification, roadmap, requirements, and state | The repo’s planning workflow treats markdown artifacts as authoritative operator-facing state. [VERIFIED: codebase read `.planning/ROADMAP.md`] [VERIFIED: codebase read `.planning/REQUIREMENTS.md`] [VERIFIED: codebase read `.planning/STATE.md`] |

### Supporting
| Library / Tool | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `gh` CLI | missing on this machine | Required for real GitHub bootstrap/sync UAT | Install or provide on the execution host before live Phase 11 UAT. [VERIFIED: local env probe] |
| `vercel` CLI | global missing; `npx vercel@latest` = 52.0.0 | Required for real Vercel link/env/deploy UAT | Use `npx vercel@latest` as the immediate fallback on this machine. [VERIFIED: local env probe] |
| git | 2.53.0.windows.1 | Required by live GitHub sync verification | Use during real repo sync checks. [VERIFIED: local env `git --version`] |
| Node.js / npm | Node v24.14.0 / npm 11.9.0 | Required for `npx vercel@latest` fallback and any Node-based operator helpers | Use when global `vercel` is unavailable. [VERIFIED: local env probe] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Separate “doc cleanup” first | Evidence-first closure then doc reconciliation | Updating canonical docs before the pending Phase 11 live UAT would force a second round of drift edits. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`] |
| Combining all closure work into one plan | Three narrow ordered plans | One large plan would mix verification, live external testing, and canonical state repair, which increases overlap and makes evidence provenance harder to keep clean. [ASSUMED] |
| Marking Phase 8 complete from summaries alone | Create an explicit `08-VERIFICATION.md` | Phase 9/10/11/12 all have dedicated verification artifacts, and Phase 8 currently does not. [VERIFIED: codebase read `.planning/phases/09-claude-code-delivery-team-orchestration/09-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/10-approved-project-delivery-pipeline/10-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/12-credential-governance-and-operator-handoff/12-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-01-SUMMARY.md`] |

**Installation:**
```bash
# Required for live UAT on this machine
gh --version      # currently missing
npx vercel@latest --version
```

## Architecture Patterns

### System Architecture Diagram

```text
Existing phase artifacts
  |
  +--> Phase 8 summaries + validation -----------+
  +--> Phase 9/10/11 verification files ---------+--> Phase 13 audit pass
  +--> Phase 11 HUMAN-UAT checklist -------------+       |
  +--> ROADMAP / REQUIREMENTS / STATE -----------+       +--> identify evidence gaps
                                                          +--> run automated re-checks
                                                          +--> run live operator UAT
                                                          +--> write missing verification artifacts
                                                          +--> reconcile canonical planning docs
                                                                 |
                                                                 v
                                                        Updated closure surfaces
                                                        - 08-VERIFICATION.md
                                                        - 11-HUMAN-UAT.md / 11-VERIFICATION.md
                                                        - ROADMAP.md
                                                        - REQUIREMENTS.md
                                                        - STATE.md
                                                        - Phase 13 goal/requirements/plans
```

### Recommended Project Structure
```text
.planning/
├── ROADMAP.md                         # canonical phase list and completion state
├── REQUIREMENTS.md                    # canonical requirement completion state
├── STATE.md                           # canonical current-focus and progress state
└── phases/
    ├── 08-shared-supabase-backend-guardrails/
    │   ├── 08-VALIDATION.md
    │   ├── 08-01-SUMMARY.md
    │   ├── 08-02-SUMMARY.md
    │   └── 08-VERIFICATION.md        # add in Phase 13
    ├── 11-github-and-vercel-automation/
    │   ├── 11-HUMAN-UAT.md           # update with real outcomes
    │   └── 11-VERIFICATION.md        # update from partial to passed/blocked
    └── 13-v1-1-phase12-phase-13-roadmap-phase-8-phase-9-10-11-roadmap-/
        └── 13-RESEARCH.md            # this file
```

### Pattern 1: Evidence first, canonical docs second
**What:** Complete or refresh the phase-local evidence artifacts before editing ROADMAP/REQUIREMENTS/STATE. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`] [VERIFIED: codebase read `.planning/ROADMAP.md`]
**When to use:** Always in this phase.
**Example:**
```markdown
# Source: .planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md
### 1. Real GitHub bootstrap/sync
expected: A real target repository is created or attached...
result: pending
```

### Pattern 2: Dedicated verification artifact per completed phase
**What:** Close Phase 8 with a standalone verification artifact instead of relying on execution summaries alone. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-01-SUMMARY.md`] [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-02-SUMMARY.md`]
**When to use:** For any phase whose implementation exists but whose formal closure artifact is missing.
**Example:**
```markdown
# Source pattern: .planning/phases/10-approved-project-delivery-pipeline/10-VERIFICATION.md
## Goal Verdict
**Status:** passed
```

### Pattern 3: One reconciliation pass updates all canonical status surfaces
**What:** After evidence is complete, update ROADMAP, REQUIREMENTS, and STATE in the same plan so they cannot diverge again immediately. [VERIFIED: codebase read `.planning/ROADMAP.md`] [VERIFIED: codebase read `.planning/REQUIREMENTS.md`] [VERIFIED: codebase read `.planning/STATE.md`]
**When to use:** Final plan of Phase 13.
**Example:**
```yaml
# Source: .planning/STATE.md
progress:
  total_phases: 13
  completed_phases: 5
  completed_plans: 17
  percent: 38
```

### Anti-Patterns to Avoid
- **Updating ROADMAP before Phase 11 UAT is actually executed:** This would create another round of drift if the live checks fail or block. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`]
- **Treating automated verification as equivalent to live UAT:** Phase 11 explicitly separates them. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`]
- **Repairing only one canonical surface:** ROADMAP, REQUIREMENTS, and STATE are all currently inconsistent with phase artifacts. [VERIFIED: codebase read `.planning/ROADMAP.md`] [VERIFIED: codebase read `.planning/REQUIREMENTS.md`] [VERIFIED: codebase read `.planning/STATE.md`]

## Concrete Gaps to Close

### Phase 8
- `08-VERIFICATION.md` is missing even though both Phase 8 plans have completion summaries and Plan 02 claims `BACK-01..BACK-06` were completed. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-01-SUMMARY.md`] [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-02-SUMMARY.md`]
- `08-VALIDATION.md` still has `status: draft`, pending task rows, and “Approval: pending,” so its state was never reconciled after execution. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`]

### Phase 9
- Phase 9 itself has a passing verification artifact, but project-level canonical docs still do not reflect completion because REQUIREMENTS leaves `TEAM-01..06` unchecked and ROADMAP progress still lists Phase 9 as planned. [VERIFIED: codebase read `.planning/phases/09-claude-code-delivery-team-orchestration/09-VERIFICATION.md`] [VERIFIED: codebase read `.planning/REQUIREMENTS.md`] [VERIFIED: codebase read `.planning/ROADMAP.md`]

### Phase 10
- `10-VERIFICATION.md` says passed and all `PIPE-01..07` requirements are checked in REQUIREMENTS, but ROADMAP still shows “0/3 plans planned” in both the milestone summary and progress table. [VERIFIED: codebase read `.planning/phases/10-approved-project-delivery-pipeline/10-VERIFICATION.md`] [VERIFIED: codebase read `.planning/REQUIREMENTS.md`] [VERIFIED: codebase read `.planning/ROADMAP.md`]

### Phase 11
- `11-VERIFICATION.md` is explicitly `human_needed`, and `11-HUMAN-UAT.md` still shows all three live checks pending. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`]
- ROADMAP progress still shows Phase 11 as planned/incomplete despite implementation completion and deferred live closure. [VERIFIED: codebase read `.planning/ROADMAP.md`]

### Project-level canonical docs
- ROADMAP contains a malformed generated Phase 13 title/slug, missing Goal/Requirements, and stale completion rows for Phases 8-11. [VERIFIED: codebase read `.planning/ROADMAP.md`]
- REQUIREMENTS still leaves `BACK-01..06` and `TEAM-01..06` pending even though phase artifacts claim those requirement sets are complete. [VERIFIED: codebase read `.planning/REQUIREMENTS.md`] [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-02-SUMMARY.md`] [VERIFIED: codebase read `.planning/phases/09-claude-code-delivery-team-orchestration/09-VERIFICATION.md`]
- STATE frontmatter progress is stale relative to current artifact reality and Phase 13’s current-focus note. [VERIFIED: codebase read `.planning/STATE.md`]

## Recommended Plan Breakdown

### Plan 13-01: Formalize Phase 8 closure
**Use for:** missing verification artifact and stale validation metadata. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`]
**Scope:**
- Re-run Phase 8 automated suites documented in `08-VALIDATION.md`. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`]
- Create `08-VERIFICATION.md` using the same proof style used by Phases 9-12. [VERIFIED: codebase read `.planning/phases/09-claude-code-delivery-team-orchestration/09-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/10-approved-project-delivery-pipeline/10-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/12-credential-governance-and-operator-handoff/12-VERIFICATION.md`]
- Reconcile `08-VALIDATION.md` from draft/pending to final verified state if tests pass. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`]
**Why first:** Phase 8 is the only evidence gap that can be closed without external credentials or human platform access. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`]

### Plan 13-02: Execute Phase 11 live human UAT
**Use for:** the only remaining live closure gate called out explicitly by the repo. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`]
**Scope:**
- Run the three pending live checks in `11-HUMAN-UAT.md`: real GitHub bootstrap/sync, real Vercel link/env/deploy, and operator artifact usability review. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`]
- Update `11-HUMAN-UAT.md` with actual results and evidence paths. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`]
- Update `11-VERIFICATION.md` from partial/human-needed to final pass or explicit blocked state based on live outcomes. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`]
**Why second:** canonical doc reconciliation should use the final live result, not a placeholder. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`]

### Plan 13-03: Reconcile canonical planning state
**Use for:** all project-level drift plus Phase 13 normalization. [VERIFIED: codebase read `.planning/ROADMAP.md`] [VERIFIED: codebase read `.planning/REQUIREMENTS.md`] [VERIFIED: codebase read `.planning/STATE.md`]
**Scope:**
- Update ROADMAP phase rows, plan counts, and Phase 13 goal/requirements/title text. [VERIFIED: codebase read `.planning/ROADMAP.md`]
- Update REQUIREMENTS completion checkboxes and traceability rows for BACK and TEAM requirement families if Plan 13-01 confirms closure. [VERIFIED: codebase read `.planning/REQUIREMENTS.md`]
- Update STATE progress counts, current focus, pending todos, blockers, and roadmap evolution text to match actual evidence after Plans 13-01 and 13-02. [VERIFIED: codebase read `.planning/STATE.md`]
**Why last:** this is the reconciliation pass that should consume final evidence from the previous two plans. [VERIFIED: codebase read `.planning/STATE.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`]

## Files/Artifacts to Update Safely

| Artifact | Why update | Safe trigger |
|---------|------------|--------------|
| `.planning/phases/08-shared-supabase-backend-guardrails/08-VERIFICATION.md` | Missing formal closure artifact for Phase 8 | Only after rerunning Phase 8 suites and confirming results. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`] |
| `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md` | Still marked draft/pending | Only after `08-VERIFICATION.md` evidence is written. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`] |
| `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md` | Pending live test checklist | Update during live UAT execution with result + evidence path per item. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`] |
| `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md` | Currently partial / human_needed | Update only after live UAT verdict is known. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`] |
| `.planning/ROADMAP.md` | Contains stale statuses and malformed Phase 13 entry | Update only after Phase 8 and 11 evidence is final. [VERIFIED: codebase read `.planning/ROADMAP.md`] |
| `.planning/REQUIREMENTS.md` | BACK and TEAM remain pending despite completion claims | Update only after Phase 8 formal verification is in place. [VERIFIED: codebase read `.planning/REQUIREMENTS.md`] |
| `.planning/STATE.md` | Progress/frontmatter counts are stale | Update only in the final reconciliation plan so counts are computed once. [VERIFIED: codebase read `.planning/STATE.md`] |

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Phase completion proof | New ad-hoc closure format | Existing `*-VERIFICATION.md` pattern from Phases 9-12 | The repo already has a recognizable verification artifact contract. [VERIFIED: codebase read `.planning/phases/09-claude-code-delivery-team-orchestration/09-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/10-approved-project-delivery-pipeline/10-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/12-credential-governance-and-operator-handoff/12-VERIFICATION.md`] |
| Live UAT checklist | Freeform notes in STATE or ROADMAP | `11-HUMAN-UAT.md` as the dedicated live checklist | The pending Phase 11 closure items are already enumerated there. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`] |
| Status reconciliation | Separate side ledger | ROADMAP + REQUIREMENTS + STATE as the canonical trio | Those are the surfaces already consumed by planning workflow. [VERIFIED: codebase read `.planning/ROADMAP.md`] [VERIFIED: codebase read `.planning/REQUIREMENTS.md`] [VERIFIED: codebase read `.planning/STATE.md`] |

**Key insight:** Phase 13 should close the loop by aligning existing evidence with existing canonical docs, not by creating a fourth source of truth. [VERIFIED: codebase read `.planning/ROADMAP.md`] [VERIFIED: codebase read `.planning/REQUIREMENTS.md`] [VERIFIED: codebase read `.planning/STATE.md`]

## Common Pitfalls

### Pitfall 1: Declaring Phase 11 closed from automated tests alone
**What goes wrong:** ROADMAP or STATE gets updated to full completion even though the repo still marks live GitHub/Vercel/operator checks as pending. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`]
**Why it happens:** `11-VERIFICATION.md` explicitly separates implementation-complete from human acceptance complete. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`]
**How to avoid:** Treat `11-HUMAN-UAT.md` as the closure gate for Phase 13 Plan 13-02. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`]
**Warning signs:** `result: pending` remains in `11-HUMAN-UAT.md` after docs say Phase 11 is closed. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`]

### Pitfall 2: Updating REQUIREMENTS before Phase 8 has a formal verification artifact
**What goes wrong:** BACK requirements get checked off in REQUIREMENTS without an equivalent closure proof artifact to match the repo’s later phases. [VERIFIED: codebase read `.planning/REQUIREMENTS.md`] [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-01-SUMMARY.md`]
**Why it happens:** Phase 8 executed work but never wrote the final verification surface. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-01-SUMMARY.md`] [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-02-SUMMARY.md`]
**How to avoid:** Write `08-VERIFICATION.md` first, then reconcile REQUIREMENTS. [VERIFIED: codebase read `.planning/phases/10-approved-project-delivery-pipeline/10-VERIFICATION.md`]
**Warning signs:** BACK rows are checked with no dedicated verification file present. [VERIFIED: codebase read `.planning/REQUIREMENTS.md`]

### Pitfall 3: Repairing only ROADMAP and forgetting STATE frontmatter math
**What goes wrong:** high-level tables look correct, but workflow state still reports stale progress and completed phase counts. [VERIFIED: codebase read `.planning/STATE.md`] [VERIFIED: codebase read `.planning/ROADMAP.md`]
**Why it happens:** STATE stores separate machine-readable counters in frontmatter. [VERIFIED: codebase read `.planning/STATE.md`]
**How to avoid:** Reconcile human-readable and frontmatter fields in the same final plan. [VERIFIED: codebase read `.planning/STATE.md`]
**Warning signs:** `completed_phases: 5` persists after later phases are clearly verified. [VERIFIED: codebase read `.planning/STATE.md`]

## Code Examples

### Phase 11 live-UAT checklist shape to preserve
```markdown
# Source: .planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md
### 1. Real GitHub bootstrap/sync
expected: A real target repository is created or attached...
result: pending
```

### Phase verification verdict shape to reuse for Phase 8
```markdown
# Source: .planning/phases/10-approved-project-delivery-pipeline/10-VERIFICATION.md
## Goal Verdict
**Status:** passed
```

### STATE frontmatter fields that must be reconciled together
```yaml
# Source: .planning/STATE.md
progress:
  total_phases: 13
  completed_phases: 5
  total_plans: 17
  completed_plans: 17
  percent: 38
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Phase execution summaries as the main closure artifact | Dedicated verification artifacts plus explicit human-UAT checklist for live external validation | By Phases 9-12 in current repo state | Phase 13 should bring Phase 8 up to the same closure standard and finish Phase 11’s deferred live gate. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-01-SUMMARY.md`] [VERIFIED: codebase read `.planning/phases/09-claude-code-delivery-team-orchestration/09-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`] |

**Deprecated/outdated:**
- ROADMAP rows that still show Phases 8-11 as planned/incomplete are outdated relative to phase-level evidence. [VERIFIED: codebase read `.planning/ROADMAP.md`] [VERIFIED: codebase read `.planning/phases/09-claude-code-delivery-team-orchestration/09-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/10-approved-project-delivery-pipeline/10-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Three plans are the cleanest decomposition for Phase 13. | Recommended Plan Breakdown | Planner may choose a different but still valid split. |
| A2 | Phase 13 should not introduce net-new product requirements beyond closure/remediation scope. | User Constraints / Summary | If user wants new AUDIT-specific requirement IDs, traceability structure would need to change. |
| A3 | Canonical docs should be reconciled only once at the end. | Alternatives Considered / Plan 13-03 | If the team prefers incremental doc sync after each closure step, task ordering would shift. |

## Open Questions

1. **Should Phase 13 define new requirement IDs or only close existing drift?** [ASSUMED]
   - What we know: ROADMAP says Goal/Requirements are TBD, while the actual work described is closure of existing Phase 8/9/10/11 obligations. [VERIFIED: codebase read `.planning/ROADMAP.md`]
   - What's unclear: whether the project wants separate audit-specific requirement IDs for milestone-close governance. [ASSUMED]
   - Recommendation: Prefer no new product requirement family unless the user explicitly wants milestone-close traceability distinct from BACK/TEAM/SHIP closure. [ASSUMED]

2. **Should the malformed Phase 13 slug/path be renamed now or left stable and only the displayed title fixed?** [ASSUMED]
   - What we know: the current Phase 13 directory name is malformed and the roadmap text is generated/noisy. [VERIFIED: codebase read `.planning/ROADMAP.md`] [VERIFIED: codebase read `.planning/phases/13-v1-1-phase12-phase-13-roadmap-phase-8-phase-9-10-11-roadmap-`]
   - What's unclear: whether renaming the directory would break any external tooling or references. [ASSUMED]
   - Recommendation: Fix displayed roadmap title/goal first; rename the directory only if planner confirms all references can be updated safely. [ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Phase 8 automated re-verification | ✓ | 3.11.15 | — [VERIFIED: local env `python --version`] |
| Node.js | `npx vercel@latest` fallback for live UAT | ✓ | v24.14.0 | — [VERIFIED: local env probe] |
| npm | `npx vercel@latest` fallback for live UAT | ✓ | 11.9.0 | — [VERIFIED: local env probe] |
| git | Real GitHub sync UAT | ✓ | 2.53.0.windows.1 | — [VERIFIED: local env `git --version`] |
| GitHub CLI (`gh`) | Real GitHub bootstrap/sync UAT | ✗ | — | install `gh` before live UAT [VERIFIED: local env probe] |
| Vercel CLI | Real Vercel link/env/deploy UAT | ✗ global | — | `npx vercel@latest` 52.0.0 [VERIFIED: local env probe] |
| GitHub token / auth | Real GitHub bootstrap/sync UAT | ? | — | none — operator must provide validated auth [ASSUMED] |
| Vercel token / project/team auth | Real Vercel link/env/deploy UAT | ? | — | none — operator must provide validated auth [ASSUMED] |

**Missing dependencies with no fallback:**
- GitHub authentication availability is unverified and required for real Phase 11 GitHub UAT. [ASSUMED]
- Vercel authentication/project linkage availability is unverified and required for real Phase 11 deploy UAT. [ASSUMED]

**Missing dependencies with fallback:**
- Global `vercel` CLI is missing, but `npx vercel@latest` is available immediately. [VERIFIED: local env probe]
- `gh` CLI itself is missing; no equivalent repo-local fallback is documented in current phase artifacts. [VERIFIED: local env probe]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Python `unittest` (stdlib) [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`] |
| Config file | none — direct `python -m unittest` invocations [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`] |
| Quick run command | `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_check_template_conformance` [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`] |
| Full suite command | `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_template_registry tests.test_template_contract tests.test_instantiate_template_project tests.test_check_template_conformance` for Phase 8, plus the recorded Phase 11 suites before live UAT evidence updates. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| BACK-01..06 | Shared-backend authority + guardrail gate still pass as documented | integration/regression | `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_template_registry tests.test_template_contract tests.test_instantiate_template_project tests.test_check_template_conformance` | ✅ [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`] |
| SHIP-01..08 | Automated GitHub/Vercel pipeline behavior still passes before live UAT | integration | `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_phase11_github_sync tests.test_phase11_vercel_flow tests.test_project_delivery_pipeline_bootstrap tests.test_approved_delivery_pipeline_cli -v` | ✅ [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`] |
| HUMAN-UAT-01 | Real GitHub bootstrap/sync against live target | manual-live | `gh` + project runbook steps | ✅ checklist exists [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`] |
| HUMAN-UAT-02 | Real Vercel link/env/deploy against live target | manual-live | `vercel`/`npx vercel@latest` + project runbook steps | ✅ checklist exists [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`] |
| HUMAN-UAT-03 | Operator artifact usability review | manual-live | inspect status/handoff artifacts after live run | ✅ checklist exists [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`] |

### Sampling Rate
- **Per task commit:** rerun the Phase-specific suite touched by the current closure task. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`]
- **Per wave merge:** rerun full Phase 8 or Phase 11 recorded suites before updating verification docs. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`]
- **Phase gate:** Do not reconcile canonical planning docs until Phase 8 verification and Phase 11 live UAT evidence are both final. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`]

### Wave 0 Gaps
- [ ] `gh` CLI availability on the execution host — required for live GitHub UAT. [VERIFIED: local env probe]
- [ ] Confirm platform-managed GitHub authentication is available for the live run. [ASSUMED]
- [ ] Confirm platform-managed Vercel authentication plus project/team identifiers are available for the live run. [ASSUMED]
- [ ] Add `08-VERIFICATION.md` so Phase 8 has the same closure surface as Phases 9-12. [VERIFIED: codebase read `.planning/phases/08-shared-supabase-backend-guardrails/08-01-SUMMARY.md`]

## Security Domain

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Use platform-managed GitHub/Vercel auth paths already governed by prior phases; require explicit live-auth confirmation during UAT. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/12-credential-governance-and-operator-handoff/12-VERIFICATION.md`] |
| V4 Access Control | yes | Preserve allowlisted governed delivery actions and do not bypass the approved-delivery pipeline during UAT. [VERIFIED: codebase read `.planning/phases/12-credential-governance-and-operator-handoff/12-VERIFICATION.md`] |
| V5 Input Validation | yes | Reuse existing validator/verification artifacts and explicit checklist fields rather than freeform closure notes. [VERIFIED: codebase read `.planning/phases/10-approved-project-delivery-pipeline/10-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`] |
| V6 Cryptography | no | No new cryptographic implementation is part of this closure phase. [VERIFIED: codebase read `.planning/ROADMAP.md`] |

### Known Threat Patterns for this phase
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Secret leakage into UAT evidence | Information Disclosure | Record evidence paths and outcomes, not raw credential values, and reuse the governed credential path from Phase 12. [VERIFIED: codebase read `.planning/phases/12-credential-governance-and-operator-handoff/12-VERIFICATION.md`] |
| False completion caused by stale docs | Repudiation | Require verification/HUMAN-UAT artifacts before canonical status edits. [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md`] |
| Running live deploy tests outside the approved pipeline | Elevation of Privilege | Use the approved-delivery command surface and preserve authority/workspace evidence linkage. [VERIFIED: codebase read `.planning/phases/10-approved-project-delivery-pipeline/10-VERIFICATION.md`] [VERIFIED: codebase read `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md`] |

## Sources

### Primary (HIGH confidence)
- `.planning/ROADMAP.md` - current roadmap state, malformed Phase 13 entry, stale phase status rows.
- `.planning/REQUIREMENTS.md` - current requirement completion drift.
- `.planning/STATE.md` - current focus and stale progress metadata.
- `.planning/phases/08-shared-supabase-backend-guardrails/08-VALIDATION.md` - Phase 8 validation contract and stale status.
- `.planning/phases/08-shared-supabase-backend-guardrails/08-01-SUMMARY.md` - Phase 8 authority completion evidence.
- `.planning/phases/08-shared-supabase-backend-guardrails/08-02-SUMMARY.md` - Phase 8 enforcement completion evidence.
- `.planning/phases/09-claude-code-delivery-team-orchestration/09-VERIFICATION.md` - Phase 9 passed verification.
- `.planning/phases/10-approved-project-delivery-pipeline/10-VERIFICATION.md` - Phase 10 passed verification.
- `.planning/phases/11-github-and-vercel-automation/11-VERIFICATION.md` - Phase 11 automated completion plus deferred live UAT.
- `.planning/phases/11-github-and-vercel-automation/11-HUMAN-UAT.md` - pending human-UAT checklist.
- `.planning/phases/12-credential-governance-and-operator-handoff/12-VERIFICATION.md` - Phase 12 passed verification and governance controls.
- `CLAUDE.md` - project constraints.
- Local environment probes on 2026-04-28 - Python/Node/npm/git availability plus missing `gh` and global `vercel`.

### Secondary (MEDIUM confidence)
- None.

### Tertiary (LOW confidence)
- Plan decomposition preference and final doc-ordering strategy assumptions noted in the Assumptions Log.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - closure work relies on verified repo-native Python/unittest/markdown patterns and direct environment probes.
- Architecture: HIGH - the repo already shows the exact artifact and verification surfaces this phase must reconcile.
- Pitfalls: HIGH - each pitfall is grounded in current mismatches between phase artifacts and canonical docs.

**Research date:** 2026-04-28
**Valid until:** 2026-05-28
