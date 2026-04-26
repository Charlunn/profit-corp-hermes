# Profit-Corp Hermes

## What This Is

Profit-Corp Hermes is an AI-operated company management core built on a multi-profile Hermes runtime. It is designed to continuously discover user pain points from public discussions across the web, evaluate whether those signals are viable mini-SaaS opportunities, and turn that information into management-grade outputs for a founder/operator.

The system is not just a prompt collection: it aims to function like a real small company's management layer, with distinct roles, daily operating rhythm, shared state, governance rules, and auditable decision flow. The primary output is a recurring operating decision package that helps the operator choose which pain point to pursue, what to build quickly, and how to launch a paid mini-SaaS with supporting pricing, marketing, and execution guidance.

## Core Value

Turn noisy web-wide user pain signals into a clear, actionable operating view: which problems are worth pursuing, what matters most, what is risky, and what the company should build and launch next.

## Requirements

### Validated

- ✓ Multi-profile role architecture already exists for `ceo`, `scout`, `cmo`, `arch`, and `accountant` — existing
- ✓ Cron-first orchestration foundation already exists via `orchestration/cron/commands.sh` and prompt files — existing
- ✓ Shared state governance already exists through `docs/STATE_CONTRACT.md` and `assets/shared/manage_finance.py` — existing
- ✓ Skill sync and profile bootstrap flow already exists via `scripts/bootstrap_hermes.sh`, `scripts/bootstrap_hermes.ps1`, and `skills/` — existing
- ✓ Brownfield codebase documentation now exists under `.planning/codebase/` — existing
- ✓ Stable daily operating loop now produces a reliable operating decision package — Validated in Phase 3: Decision Package Quality
- ✓ Final outputs now provide management-grade conclusions, evidence links, and downstream derived artifacts — Validated in Phase 3: Decision Package Quality
- ✓ Execution handoff now provides a stable Core 9 planning/delivery contract with lightweight ownership and readiness metadata — Validated in Phase 6: Execution Handoff and Team Readiness
- ✓ Board briefing now provides a one-screen governance/risk/finance/required-attention contract aligned to the operating decision package — Validated in Phase 6: Execution Handoff and Team Readiness

### Active

- [ ] Strengthen governance so approvals, budgets, state transitions, audit trails, and review loops are operational rather than merely documented
- [ ] Make company state visible at a glance for a solo operator now and a future team later
- [ ] Prioritize external inputs from user complaints, pain-point discussions, and public communities across the web, with competitor/trend research used as optional support for pricing and marketing

### Out of Scope

- Real customer-facing product delivery platform — this repo is the internal AI management core, not the end-user SaaS product
- Full autonomous execution without human approval — the system should support semi-autonomous operation, but founder/operator oversight remains required
- Internal-project-only planning as the main driver — external pain signals should still drive idea selection and launch decisions

## Context

This repository is a Hermes-native migration target for an existing profit-corp operating model. The current codebase already contains role definitions, skill libraries, cron orchestration helpers, recovery scripts, state contracts, and a finance ledger with restricted mutation rules.

The user's goal is not to build a single tool, but to evolve this brownfield foundation into a genuine AI operating company structure. The desired organizational model resembles a management team: Scout gathers pain signals and market evidence, CMO interprets commercial implications and launch positioning, Arch assesses technical feasibility and speed-to-ship, CEO integrates decisions, and Accountant enforces audit/cost discipline.

The first-stage success condition is not “full autonomy,” but management visibility: the operator should be able to see the current opportunity set, risks, viability, and next actions through a daily rhythm. Over time, the system should become strong enough to support a small team and generate high-quality recurring decision outputs.

The most important information inputs in the near term are user complaints and pain signals from public discussions across the web. There is no single source of truth for this work; people can express the same pain in many places. Competitor and trend research can still matter, but mainly as secondary enrichment for pricing, positioning, and marketing once a promising idea is identified.

## Constraints

- **Existing foundation**: This is a brownfield repo with established roles, scripts, and governance docs — new work should extend the current system rather than replacing it wholesale
- **Runtime model**: The system depends on Hermes profiles and cron orchestration — implementation choices should stay compatible with that operating model
- **Governance**: Shared-state writes must respect `docs/STATE_CONTRACT.md` and the `assets/shared/manage_finance.py` write path
- **Operator workflow**: The system must be useful for a solo operator now, but should not block later team use
- **Primary cadence**: Daily loop is the core operating rhythm for v1
- **Input bias**: Phase 1 should emphasize flexible web-wide pain-point discovery rather than a fixed approved source list
- **Output quality**: Deliverables should balance analysis depth with strong decision recommendations, not just dump collected information

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Make the system an AI company management core, not a single-purpose planner | The user wants a structure that can work efficiently like a real company | — Pending |
| Use operating decision package as the primary output | The user wants a management layer that turns signals into decisions | Validated in Phase 3 |
| Support project execution packs and board-style briefings as secondary outputs | Management decisions need downstream execution and communication artifacts | Validated in Phase 6 |
| Prioritize improving output quality and governance together | The user explicitly wants both more professional outputs and stronger company-like controls | Output quality validated in Phase 3; governance remains pending |
| Use daily operating rhythm as the main cycle | The user wants the system to function as an ongoing operating mechanism, not just on-demand analysis | — Pending |
| Focus initial intelligence gathering on web-wide user pain signals, with competitor/trend research as optional support | The user wants flexible whole-web discovery rather than a fixed list of canonical sources | — Pending |
| Optimize for solo operator visibility first, then team expansion | The system should be immediately useful now while remaining extensible later | Visibility validated in Phase 5; team-ready downstream contracts validated in Phase 6 |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**Current state:** Phase 6 complete — execution handoff and board briefing contracts are now stable downstream operating artifacts, while the repo still awaits a milestone-level closeout for remaining governance/visibility requirement tracking.

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-26 after Phase 6 completion*
