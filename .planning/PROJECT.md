# Profit-Corp Hermes

## What This Is

Profit-Corp Hermes is an AI-operated company management core built on a multi-profile Hermes runtime. It continuously discovers user pain points from public discussions across the web, evaluates whether those signals are viable mini-SaaS opportunities, and now carries approved opportunities all the way into governed SaaS delivery.

The system is no longer just an analysis and management layer. It now spans the full path from signal discovery and operating decision support to template-governed project instantiation, specialist agent execution, GitHub/Vercel shipping, and operator-facing delivery handoff.

## Core Value

Turn noisy web-wide user pain signals into a clear, actionable operating view: which problems are worth pursuing, what matters most, what is risky, and what the company should build, launch, and operationalize next.

## Current State

**Latest shipped milestone:** v1.1 SaaS Delivery Factory (shipped 2026-04-28)

Hermes now supports a full approved-to-delivery SaaS factory flow on top of the original operating core:
- governed template asset registration and contract enforcement
- shared Supabase backend guardrails
- Claude Code specialist delivery-team orchestration
- approved-project bootstrap, blocked-state tracking, resume, and handoff
- constrained GitHub/Vercel automation with operator-visible audit artifacts

## Current Milestone: v1.1.1 Delivery Pipeline Reliability Fixes

**Goal:** Turn the approved-project delivery path back into a repeatable, self-converging automation flow by fixing the defects exposed during the live Hermes instance test.

**Target features:**
- Fix GitHub auth detection, owner fallback, and repo/sync defaults so new approved projects can create and sync their own repositories without manual rescue
- Fix workspace snapshot behavior and transport/path handling so GitHub sync succeeds on the real Windows + pnpm environment used in live delivery
- Fix Vercel auth handling and final authority/status convergence so a real successful deploy is reflected as a clean completed pipeline state

## Next Milestone Goals

- Repair the specific GitHub/Vercel delivery defects found during the live end-to-end Hermes instance test
- Preserve the one-approval automated delivery model while removing the manual recovery steps that were required to finish the test run
- Make operator-facing authority/status artifacts converge to the true final state after successful shipping and deployment

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
- ✓ `standalone-saas-template` is now a governed Hermes platform asset with canonical contract, protected-layer rules, and conformance enforcement — Validated in v1.1
- ✓ Approved product opportunities can now move through governed workspace bootstrap, delivery orchestration, GitHub sync, Vercel deploy, and final handoff artifacts — Validated in v1.1
- ✓ Platform-managed GitHub/Vercel delivery automation now runs through constrained, auditable governance paths instead of open-ended credential use — Validated in v1.1
- ✓ GitHub sync now stages a source-only canonical snapshot, converges workspace remotes, retries through operator-healthy transport paths, and persists granular sync evidence — Validated in Phase 15: GitHub Sync Reliability on Real Workspaces

### Active

- [ ] Restore automatic GitHub credential detection for approved-project delivery without requiring manual shell token export
- [ ] Restore correct GitHub repository owner/repo targeting for new approved projects
- [ ] Restore Vercel deployment automation so the pipeline can use the available operator auth path without manual CLI rescue
- [ ] Restore authority/status artifact convergence so successful live delivery renders as completed instead of staying blocked

### Out of Scope

- Building product-specific end-user SaaS features inside this repo before a future milestone explicitly targets one customer app
- Fully custom per-product infrastructure stacks as the default path — new SaaS projects should start from the shared template and shared Supabase platform contract unless the owner explicitly approves a platform change
- Manual project-by-project developer setup as the default path — the system should continue pushing toward repeatable automated delivery workflows

## Context

This repository is a Hermes-native migration target for an existing profit-corp operating model. The codebase now contains both the original operating intelligence layer and a shipped v1.1 delivery-factory layer that can turn approved opportunities into governed, deployable SaaS workspaces.

A standalone mini-SaaS template exists at `C:\Users\42236\Desktop\standalone-saas-template`. It uses Next.js with Supabase Auth, shared PayPal checkout/capture flows, entitlement helpers, and shared public tables (`users`, `orders`, `payments`, `subscriptions`). Hermes now treats that template as a governed platform asset rather than a loose external starting point.

The current deployment model remains Vercel for frontend delivery and a single shared Supabase project for SaaS backends. New projects isolate product data through app-key conventions and shared-boundary enforcement instead of spinning up a separate backend per SaaS by default.

## Constraints

- **Existing foundation**: This remains a brownfield repo with established roles, scripts, and governance docs — new work should extend the current system rather than replacing it wholesale
- **Runtime model**: The system depends on Hermes profiles and cron orchestration — implementation choices should stay compatible with that operating model
- **Governance**: Shared-state writes must respect `docs/STATE_CONTRACT.md` and the `assets/shared/manage_finance.py` write path
- **Operator workflow**: The owner wants a one-time approval gate before delivery automation continues; downstream development should automate after approval, not require repeated manual orchestration by default
- **Shared backend model**: Frontends should target Vercel while SaaS products share one Supabase project, using template-enforced naming and boundary rules to isolate product data
- **Template contract**: Shared auth, payment, entitlement, and core public table flows from `standalone-saas-template` are platform primitives rather than per-product rebuild targets
- **Deployment ambition**: GitHub sync and direct Vercel deployment are part of the intended operating path, so credential, permission, and release boundaries must remain explicit

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Make the system an AI company management core, not a single-purpose planner | The user wants a structure that can work efficiently like a real company | — Pending |
| Use operating decision package as the primary output | The user wants a management layer that turns signals into decisions | Validated in Phase 3 |
| Support project execution packs and board-style briefings as secondary outputs | Management decisions need downstream execution and communication artifacts | Validated in Phase 6 |
| Prioritize improving output quality and governance together | The user explicitly wants both more professional outputs and stronger company-like controls | Output quality validated in Phase 3; governance validated in v1.1 |
| Use daily operating rhythm as the main cycle | The user wants the system to function as an ongoing operating mechanism, not just on-demand analysis | — Pending |
| Focus initial intelligence gathering on web-wide user pain signals, with competitor/trend research as optional support | The user wants flexible whole-web discovery rather than a fixed list of canonical sources | — Pending |
| Optimize for solo operator visibility first, then team expansion | The system should be immediately useful now while remaining extensible later | Visibility validated in Phase 5; team-ready downstream contracts validated in Phase 6 |
| Standardize new SaaS builds on a shared template and shared Supabase platform contract | The user wants approved products to move quickly through a repeatable build pipeline instead of starting infrastructure from scratch each time | Validated in v1.1 |
| Use a one-time owner approval gate before automatic delivery execution | The user wants human approval on product direction, but does not want repeated manual gating once a build is approved | Validated in v1.1 |
| Push Hermes toward automated GitHub sync and Vercel-ready deployment handoff | The goal is not just design guidance, but deployable SaaS outputs that can be launched rapidly after approval | Validated in v1.1 |
| Use verification and live-UAT evidence as the only source of truth for milestone-close reconciliation | Canonical docs drifted during execution and needed one final evidence-backed normalization pass | Validated in Phase 13 |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**Current state:** v1.1 shipped — Hermes now spans both opportunity intelligence and governed SaaS delivery. The next milestone should define what to extend beyond the delivery-factory baseline rather than reopening already-closed v1.1 scope.

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-04-29 after v1.1.1 milestone kickoff*
