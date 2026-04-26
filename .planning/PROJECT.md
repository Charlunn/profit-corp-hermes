# Profit-Corp Hermes

## What This Is

Profit-Corp Hermes is an AI-operated company management core built on a multi-profile Hermes runtime. It is designed to continuously discover user pain points from public discussions across the web, evaluate whether those signals are viable mini-SaaS opportunities, and turn that information into management-grade outputs for a founder/operator.

The system is not just a prompt collection: it aims to function like a real small company's management layer, with distinct roles, daily operating rhythm, shared state, governance rules, and auditable decision flow. The primary output is a recurring operating decision package that helps the operator choose which pain point to pursue, what to build quickly, and how to launch a paid mini-SaaS with supporting pricing, marketing, and execution guidance.

## Core Value

Turn noisy web-wide user pain signals into a clear, actionable operating view: which problems are worth pursuing, what matters most, what is risky, and what the company should build and launch next.

## Current Milestone: v1.1 SaaS Delivery Factory

**Goal:** Turn Hermes into an approved-to-delivery mini-SaaS factory that can take an approved opportunity through shared-template setup, agent-driven implementation, repository sync, and deployment handoff with minimal manual work.

**Target features:**
- Bring `standalone-saas-template` into Hermes as a governed reusable asset with explicit platform contracts and extension rules
- Standardize a Claude Code-powered specialist development team with GSD constraints, reusable responsibilities, and a one-time owner approval gate
- Build a post-approval delivery pipeline that can instantiate new SaaS projects, apply app-specific configuration, and start execution automatically
- Push the delivery chain through GitHub sync and as much direct Vercel deployment automation as feasible while preserving shared Supabase platform rules

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

- [ ] Turn Hermes into an approved-to-delivery mini-SaaS factory that can move from opportunity selection to templated product build, repository sync, and deployment handoff with minimal manual work
- [ ] Operationalize a shared-template platform contract so every new SaaS reuses the same Supabase/Auth/PayPal foundation instead of rebuilding infrastructure
- [ ] Expand Hermes from solo operator support into a professional Claude Code-powered development team with explicit approval gates, role boundaries, and reusable delivery workflows

### Out of Scope

- Building product-specific end-user SaaS features inside this repo before the delivery factory is ready — this milestone is about platformized production capability, not shipping one customer app
- Fully custom per-product infrastructure stacks — new SaaS projects should start from the shared template and shared Supabase platform contract unless the owner explicitly approves a platform change
- Manual project-by-project developer setup as the default path — the goal is to make approved projects routable into a repeatable automated delivery workflow

## Context

This repository is a Hermes-native migration target for an existing profit-corp operating model. The current codebase already contains role definitions, skill libraries, cron orchestration helpers, recovery scripts, state contracts, and a finance ledger with restricted mutation rules.

The user's goal is no longer only to improve management visibility. The next milestone expands Hermes into a mini-SaaS delivery factory: after Hermes identifies and the user approves a product opportunity, a professional agent development team should be able to stand up a new project quickly on top of a shared SaaS template and hand back deployable output.

A standalone mini-SaaS template already exists at `C:\Users\42236\Desktop\standalone-saas-template`. It uses Next.js with Supabase Auth, shared PayPal checkout/capture flows, entitlement helpers, and shared public tables (`users`, `orders`, `payments`, `subscriptions`). The template contract requires product-specific business tables to use the `APP_KEY_` prefix and treats shared auth/payment/entitlement layers as stable platform primitives.

The intended deployment model is Vercel for frontend delivery and a single shared Supabase project for all SaaS backends. New projects should isolate product data through the template's app-key conventions rather than by spinning up a separate backend per SaaS, unless the platform contract is intentionally revised.

The user wants the post-approval path to be as automated as practical: once a product direction is approved, Hermes should be able to instantiate a project from the template, coordinate specialized development agents using Claude Code plus GSD controls, sync the result to GitHub, and, if feasible, push all the way through to Vercel deployment.

## Constraints

- **Existing foundation**: This is a brownfield repo with established roles, scripts, and governance docs — new work should extend the current system rather than replacing it wholesale
- **Runtime model**: The system depends on Hermes profiles and cron orchestration — implementation choices should stay compatible with that operating model
- **Governance**: Shared-state writes must respect `docs/STATE_CONTRACT.md` and the `assets/shared/manage_finance.py` write path
- **Operator workflow**: The owner wants a one-time approval gate before delivery automation continues; downstream development should automate after approval, not require repeated manual orchestration by default
- **Shared backend model**: Frontends should target Vercel while all SaaS products share one Supabase project, using template-enforced naming and boundary rules to isolate product data
- **Template contract**: Shared auth, payment, entitlement, and core public table flows from `standalone-saas-template` should be reused as platform primitives rather than reimplemented per product
- **Deployment ambition**: The target state is GitHub sync plus as much direct Vercel deployment automation as practical, which means credential, permission, and release boundaries must be designed explicitly

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
| Standardize new SaaS builds on a shared template and shared Supabase platform contract | The user wants approved products to move quickly through a repeatable build pipeline instead of starting infrastructure from scratch each time | — Pending |
| Use a one-time owner approval gate before automatic delivery execution | The user wants human approval on product direction, but does not want repeated manual gating once a build is approved | — Pending |
| Push Hermes toward automated GitHub sync and Vercel-ready deployment handoff | The goal is not just design guidance, but deployable SaaS outputs that can be launched rapidly after approval | — Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**Current state:** Phase 6 complete — execution handoff and board briefing contracts are now stable downstream operating artifacts. The next milestone shifts focus from analysis/readiness toward turning Hermes into an approved-to-delivery SaaS production system built around a shared template, shared Supabase backend model, and automated developer-team execution.

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-26 after milestone v1.1 initialization*
