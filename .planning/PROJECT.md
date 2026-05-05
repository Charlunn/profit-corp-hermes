# Profit-Corp Hermes

## What This Is

Profit-Corp Hermes is an AI-operated company management core that discovers user pain points from public discussions, evaluates which ones justify a paid mini-SaaS, and carries approved opportunities through governed delivery.

The system now spans signal discovery, approval governance, template-based workspace bootstrap, specialist execution, GitHub/Vercel shipping, and operator-facing handoff. After `v1.1.2`, Hermes also enforces stricter proof that approved-project delivery produced a real product rather than a template-skinned placeholder.

## Core Value

Turn noisy web-wide user pain signals into clear, governed decisions about what is worth building next - and ensure approved opportunities become real, launchable SaaS products rather than ceremonial agent output.

## Current State

**Latest shipped milestone:** v1.2 Autonomous Project Launch Loop (shipped 2026-05-05)

Hermes now has both a repaired approved-to-delivery automation backbone and stricter governance over what counts as successful delivery:
- governed GitHub auth can use either explicit env tokens or an already-authenticated `gh` CLI session
- approved projects derive canonical GitHub owner/repository identity instead of slug-based fallbacks
- GitHub sync uses source-only snapshots, remote convergence, and transport fallback for real Windows + pnpm workspaces
- governed Vercel delivery can use either explicit `VERCEL_TOKEN` or a healthy local CLI login session
- authority and operator-visible status artifacts converge to the true recovered final state after successful GitHub/Vercel completion
- specialist stages now fail closed on missing evidence, stale `/ui-ux-pro-max` artifacts, template-only work, and weak product-proof claims

The biggest unresolved gap is now operator experience above the shipped pipeline: Hermes can intake, qualify, approve, deliver, deploy, and notify, but the owner still has to think in terms of milestone internals instead of treating Hermes as the single conversational company surface.

## Current Milestone

**v1.3 Hermes-First Autonomous Company Interface**

**Goal:** Make Hermes the only operator-facing interface so the owner can ask Hermes to start a new project, approve the resulting proposal, and receive the final deployed URL without touching internal scripts or phase-level commands.

**Target features:**
- Hermes-native "start new project" entrypoint that triggers the full launch loop from a single top-level intent
- Hermes-managed internal role orchestration so `ceo`, `scout`, `cmo`, `arch`, and delivery specialists collaborate behind one interface
- Hermes-native approval and recovery flow where the owner only sees proposal, approve/reject, blocked context, and final shipped result
- hidden internal execution of qualification, contract freeze, delivery, deploy, and final notification so the pipeline stays governed but feels like one Hermes capability

## Next Milestone Goals

- make Hermes the single front door for project launch, approval, execution, and shipped-result retrieval
- preserve the shipped 22-25 backbone while hiding milestone-internal script choreography from the operator
- ensure company roles and delivery specialists are configured and invoked inside Hermes rather than exposed as user-run steps
- reduce healthy-path interaction to intent + approval + final URL, with explicit Hermes-mediated recovery only on real blockers

## Requirements

### Validated

- Multi-profile role architecture already exists for `ceo`, `scout`, `cmo`, `arch`, and `accountant` - existing
- Cron-first orchestration foundation already exists via `orchestration/cron/commands.sh` and prompt files - existing
- Shared state governance already exists through `docs/STATE_CONTRACT.md` and `assets/shared/manage_finance.py` write path - existing
- Skill sync and profile bootstrap flow already exists via `scripts/bootstrap_hermes.sh`, `scripts/bootstrap_hermes.ps1`, and `skills/` - existing
- Brownfield codebase documentation now exists under `.planning/codebase/` - existing
- Stable daily operating loop now produces a reliable operating decision package - Validated in Phase 3: Decision Package Quality
- Final outputs now provide management-grade conclusions, evidence links, and downstream derived artifacts - Validated in Phase 3: Decision Package Quality
- Execution handoff now provides a stable Core 9 planning/delivery contract with lightweight ownership and readiness metadata - Validated in Phase 6: Execution Handoff and Team Readiness
- Board briefing now provides a one-screen governance/risk/finance/required-attention contract aligned to the operating decision package - Validated in Phase 6: Execution Handoff and Team Readiness
- `standalone-saas-template` is now a governed Hermes platform asset with canonical contract, protected-layer rules, and conformance enforcement - Validated in v1.1
- Approved product opportunities can now move through governed workspace bootstrap, delivery orchestration, GitHub sync, Vercel deploy, and final handoff artifacts - Validated in v1.1
- Platform-managed GitHub/Vercel delivery automation now runs through constrained, auditable governance paths instead of open-ended credential use - Validated in v1.1
- GitHub sync now stages a source-only canonical snapshot, converges workspace remotes, retries through operator-healthy transport paths, and persists granular sync evidence - Validated in Phase 15
- Approved-project delivery can treat an already-authenticated `gh` CLI session as a valid GitHub auth source when env tokens are absent - Validated in Phase 14
- Approved-project delivery now derives canonical GitHub repository owner/name/url identity for new projects and resume flows - Validated in Phase 14
- Governed Vercel delivery can use either explicit token auth or an already-authenticated local CLI session - Validated in Phase 16
- Authority and operator-facing status surfaces now converge to the true recovered final state after GitHub/Vercel success - Validated in Phase 17
- Template conformance and instantiation metadata already carry multilingual (`en`, `zh` plus major internet languages), monetization, and UI-artifact requirements into workspace-local `.hermes` authority files - Validated after v1.1.1 close
- Approved-project specialist stages now fail closed unless transcript, handoff, workspace inventory, and stage evidence agree on the same run/stage truth - Validated in Phase 19
- UI-relevant delivery now blocks on missing, stale, or content-thin `/ui-ux-pro-max` artifacts tied to the approved product contract - Validated in Phase 19
- Stage handoffs, validators, authority, status rendering, and final review now share one normalized governance contract for outputs, evidence, risks, and readiness truth - Validated in Phases 18-19
- Real product proof now requires workflow surfaces and supporting logic instead of `/demo` or identity-only/template-only files - Validated in Phase 20
- Bootstrap and resume flows now enforce the same governance gates and preserve one authoritative blocked/resumed/recovered truth across operator surfaces - Validated in Phase 21

### Active

- [ ] Let the operator trigger a new project through Hermes as the only required control surface
- [ ] Qualify only fresh, real, buildable pain points with market and pricing proof before proposal approval
- [ ] Present one concise proposal for operator approval and persist a locked delivery contract after approval
- [ ] Continue approved runs through design, development, testing, GitHub, Vercel, and final link return without healthy-path manual resumes
- [ ] Hide milestone-internal script choreography behind Hermes-native intent routing and role execution

### Out of Scope

- Reopening GitHub auth, GitHub sync, Vercel auth, Vercel deployment, or recovered-status convergence as primary milestone work - those delivery-path reliability repairs shipped in v1.1.1 and should remain stable unless a new blocker appears
- Replacing the approved-project architecture with a new workflow engine or state store - brownfield constraint is to harden the current authority/event/artifact model rather than restart it
- Supporting fully custom per-product backend stacks as the default path - shared template plus shared Supabase remains the baseline until explicitly superseded
- Broad product-factory expansion into unrelated business functions or a generic messaging product - this milestone is about making Hermes the natural interface to the shipped launch-and-delivery loop
- Building unrelated end-user SaaS features inside Hermes itself - the focus remains delivery governance behavior, not product application scope inside this repo

## Context

This repository is a Hermes-native migration target for an existing profit-corp operating model. The codebase contains both the original operating intelligence layer and a shipped delivery-factory layer that can turn approved opportunities into governed, deployable SaaS workspaces.

A standalone mini-SaaS template exists at `C:\Users\42236\Desktop\standalone-saas-template`. It uses Next.js with Supabase Auth, shared PayPal checkout/capture flows, entitlement helpers, and shared public tables (`users`, `orders`, `payments`, `subscriptions`). Hermes treats that template as a governed platform asset rather than a loose external starter.

The current deployment model remains Vercel for frontend delivery and a single shared Supabase project for SaaS backends. New projects isolate product data through app-key conventions and shared-boundary enforcement instead of spinning up a separate backend per SaaS by default.

Research through `v1.2` shows the main remaining risk is no longer infrastructure reliability or missing governance gates. The missing piece is interaction packaging: the launch loop exists, but the owner experience is still too pipeline-aware and not Hermes-native enough.

## Constraints

- **Existing foundation**: This remains a brownfield repo with established roles, scripts, and governance docs - new work should extend the current system rather than replacing it wholesale
- **Runtime model**: The system depends on Hermes profiles and cron orchestration - implementation choices should stay compatible with that operating model
- **Governance**: Shared-state writes must respect `docs/STATE_CONTRACT.md` and the `assets/shared/manage_finance.py` write path
- **Operator workflow**: The owner wants a one-time approval gate before delivery automation continues; downstream development should automate after approval, not require repeated manual orchestration by default
- **Shared backend model**: Frontends should target Vercel while SaaS products share one Supabase project, using template-enforced naming and boundary rules to isolate product data
- **Template contract**: Shared auth, payment, entitlement, and core public table flows from `standalone-saas-template` are platform primitives rather than per-product rebuild targets
- **Governance hardening scope**: New work should preserve the stricter specialist evidence, UI artifact, product-proof, and recovered-truth rules added in `v1.1.2`
- **Language coverage**: English and Chinese are mandatory and major internet languages remain part of the default product requirement contract unless a brief justifies a narrower set
- **Operator interaction model**: Healthy-path interaction should collapse to start plus approve, with escalation only for real blockers
- **Evidence freshness**: Proposed pain-point and market evidence must be recent enough to support a three-day validity window
- **Interface model**: Hermes must be the only intentional surface the owner talks to; scripts and phase-level commands are implementation details, not user workflow

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Make the system an AI company management core, not a single-purpose planner | The user wants a structure that can work efficiently like a real company | Pending |
| Use operating decision package as the primary output | The user wants a management layer that turns signals into decisions | Validated in Phase 3 |
| Support project execution packs and board-style briefings as secondary outputs | Management decisions need downstream execution and communication artifacts | Validated in Phase 6 |
| Prioritize improving output quality and governance together | The user explicitly wants both more professional outputs and stronger company-like controls | Output quality validated in Phase 3; governance validated in v1.1 |
| Use daily operating rhythm as the main cycle | The user wants the system to function as an ongoing operating mechanism, not just on-demand analysis | Pending |
| Focus initial intelligence gathering on web-wide user pain signals, with competitor/trend research as optional support | The user wants flexible whole-web discovery rather than a fixed list of canonical sources | Pending |
| Optimize for solo operator visibility first, then team expansion | The system should be immediately useful now while remaining extensible later | Visibility validated in Phase 5; team-ready downstream contracts validated in Phase 6 |
| Standardize new SaaS builds on a shared template and shared Supabase platform contract | The user wants approved products to move quickly through a repeatable build pipeline instead of starting infrastructure from scratch each time | Validated in v1.1 |
| Use a one-time owner approval gate before automatic delivery execution | The user wants human approval on product direction, but does not want repeated manual gating once a build is approved | Validated in v1.1 |
| Push Hermes toward automated GitHub sync and Vercel-ready deployment handoff | The goal is not just design guidance, but deployable SaaS outputs that can be launched rapidly after approval | Validated in v1.1 |
| Use verification and live-UAT evidence as the only source of truth for milestone-close reconciliation | Canonical docs drifted during execution and needed one final evidence-backed normalization pass | Validated in Phase 13 |
| Prioritize real-SaaS delivery governance over more transport repairs for the next milestone | The root problem is template-shaped output passing as delivery even after GitHub/Vercel reliability was repaired | Validated in v1.1.2 |
| Make `/ui-ux-pro-max` a blocking governed artifact for UI scope, not a policy-only suggestion | Frontend stages need executable design proof to stop template-like output and generic handoffs | Validated in v1.1.2 |
| Remove `/demo` and identity-only paths from acceptable product proof | Renaming template identity is necessary bootstrap work, but it is not evidence of a real paid SaaS workflow | Validated in v1.1.2 |
| Treat current audit gaps as process debt rather than failed governance scope | The runtime behavior satisfies the milestone, but closeout evidence is still incomplete | Accepted at v1.1.2 close |
| Move the next milestone toward chat-native autonomous project launch | The operator wants Hermes to behave like a minimally interruptive company loop rather than a terminal-operated toolchain | Validated in v1.2 |
| Keep the human approval gate but compress healthy-path interaction to start plus approve | The owner still wants control over project direction, but not repeated manual orchestration after approval | Validated in v1.2 |
| Make Hermes the only operator-facing entrypoint for the launch loop | The owner should talk to Hermes, not think in terms of scripts, phases, or handoff glue | Pending |
| Keep company roles and delivery specialists as Hermes-internal collaborators rather than user-exposed tools | The desired architecture is "Hermes handles everything" with role configuration living inside Hermes | Pending |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):
1. Requirements invalidated? Move to Out of Scope with reason
2. Requirements validated? Move to Validated with phase reference
3. New requirements emerged? Add to Active
4. Decisions to log? Add to Key Decisions
5. "What This Is" still accurate? Update if drifted

**Current state:** `v1.2` is shipped; `v1.3` is now defined around turning the shipped launch loop into a Hermes-first operator interface with hidden internal orchestration.

**After each milestone** (via `/gsd-complete-milestone`):
1. Full review of all sections
2. Core Value check - still the right priority?
3. Audit Out of Scope - reasons still valid?
4. Update Context with current state

---
*Last updated: 2026-05-05 after v1.3 milestone initialization*
