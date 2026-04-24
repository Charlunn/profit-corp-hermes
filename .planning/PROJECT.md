# Profit-Corp Hermes

## What This Is

Profit-Corp Hermes is an AI-operated company management core built on a multi-profile Hermes runtime. It is designed to continuously collect external market intelligence, competitor movement, and user complaint signals from forums and public discussions, then turn that information into management-grade outputs for a founder/operator.

The system is not just a prompt collection: it aims to function like a real small company's management layer, with distinct roles, daily operating rhythm, shared state, governance rules, and auditable decision flow. The primary output is a recurring operating decision package, with supporting project execution packages and board-style briefings.

## Core Value

Turn noisy external signals into a clear, actionable daily operating view: what is happening, what matters, what is risky, and what the company should do next.

## Requirements

### Validated

- ✓ Multi-profile role architecture already exists for `ceo`, `scout`, `cmo`, `arch`, and `accountant` — existing
- ✓ Cron-first orchestration foundation already exists via `orchestration/cron/commands.sh` and prompt files — existing
- ✓ Shared state governance already exists through `docs/STATE_CONTRACT.md` and `assets/shared/manage_finance.py` — existing
- ✓ Skill sync and profile bootstrap flow already exists via `scripts/bootstrap_hermes.sh`, `scripts/bootstrap_hermes.ps1`, and `skills/` — existing
- ✓ Brownfield codebase documentation now exists under `.planning/codebase/` — existing

### Active

- [ ] Build a stable daily operating loop that collects external intelligence and produces a reliable operating decision package
- [ ] Improve the professionalism and usefulness of final outputs so they read like management consulting + CEO decision materials
- [ ] Strengthen governance so approvals, budgets, state transitions, audit trails, and review loops are operational rather than merely documented
- [ ] Make company state visible at a glance for a solo operator now and a future team later
- [ ] Prioritize external inputs: industry trends, competitor intelligence, and user complaint signals from public forums and communities

### Out of Scope

- Real customer-facing product delivery platform — this repo is the internal AI management core, not the end-user SaaS product
- Full autonomous execution without human approval — the system should support semi-autonomous operation, but founder/operator oversight remains required
- Internal-project-only planning as the main driver — internal project state matters, but phase 1 is driven primarily by external signals

## Context

This repository is a Hermes-native migration target for an existing profit-corp operating model. The current codebase already contains role definitions, skill libraries, cron orchestration helpers, recovery scripts, state contracts, and a finance ledger with restricted mutation rules.

The user's goal is not to build a single tool, but to evolve this brownfield foundation into a genuine AI operating company structure. The desired organizational model resembles a management team: Scout gathers information, CMO interprets commercial implications, Arch assesses technical feasibility, CEO integrates decisions, and Accountant enforces audit/cost discipline.

The first-stage success condition is not “full autonomy,” but management visibility: the operator should be able to see the current situation, risks, opportunities, and next actions through a daily rhythm. Over time, the system should become strong enough to support a small team and generate high-quality recurring decision outputs.

The most important information inputs in the near term are external: industry trend shifts, competitor moves, and especially user complaints and pain signals from forums and public discussion spaces.

## Constraints

- **Existing foundation**: This is a brownfield repo with established roles, scripts, and governance docs — new work should extend the current system rather than replacing it wholesale
- **Runtime model**: The system depends on Hermes profiles and cron orchestration — implementation choices should stay compatible with that operating model
- **Governance**: Shared-state writes must respect `docs/STATE_CONTRACT.md` and the `assets/shared/manage_finance.py` write path
- **Operator workflow**: The system must be useful for a solo operator now, but should not block later team use
- **Primary cadence**: Daily loop is the core operating rhythm for v1
- **Input bias**: Phase 1 should emphasize external intelligence over internal telemetry
- **Output quality**: Deliverables should balance analysis depth with strong decision recommendations, not just dump collected information

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Make the system an AI company management core, not a single-purpose planner | The user wants a structure that can work efficiently like a real company | — Pending |
| Use operating decision package as the primary output | The user wants a management layer that turns signals into decisions | — Pending |
| Support project execution packs and board-style briefings as secondary outputs | Management decisions need downstream execution and communication artifacts | — Pending |
| Prioritize improving output quality and governance together | The user explicitly wants both more professional outputs and stronger company-like controls | — Pending |
| Use daily operating rhythm as the main cycle | The user wants the system to function as an ongoing operating mechanism, not just on-demand analysis | — Pending |
| Focus initial intelligence gathering on external signals | The user said phase 1 should mainly use industry trends, competitor intelligence, and forum/user complaints | — Pending |
| Optimize for solo operator visibility first, then team expansion | The system should be immediately useful now while remaining extensible later | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-24 after initialization*
