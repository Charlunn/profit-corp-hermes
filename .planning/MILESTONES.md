# Milestones

## v1.3 - Hermes-First Autonomous Company Interface

**Shipped:** 2026-05-05
**Phases:** 4 | **Plans:** 11 | **Tasks:** 11
**Timeline:** 2026-05-05 -> 2026-05-05
**Git range:** `c1068a0` -> `689b24b`

### Delivered
- Added one Hermes-native project-start entrypoint that reuses the existing governed run identity and bootstrap truth
- Internalized company-role routing and approved-work delivery handoff so Hermes stays the only visible operator surface
- Collapsed proposal and approval into one Hermes-native recommendation and conversational approve/reject loop backed by the locked delivery contract
- Locked final shipped success and blocked recovery against the authoritative approved-delivery status and notification surfaces

### Known Gaps
- Open-artifact audit still reports the legacy `Phase 11 / 11-HUMAN-UAT.md` entry even though it is marked passed with zero pending scenarios
- No dedicated `v1.3-MILESTONE-AUDIT.md` artifact was present at close

### Notes
- See `.planning/milestones/v1.3-ROADMAP.md` and `.planning/milestones/v1.3-REQUIREMENTS.md` for full archived detail
- Known deferred items at close: 1 (see `STATE.md` Deferred Items)

## v1.1.2 - Real-SaaS Delivery Governance Hardening

**Shipped:** 2026-05-04
**Phases:** 4 | **Plans:** 11 | **Tasks:** 11
**Timeline:** 2026-05-04 -> 2026-05-04
**Git range:** `working-tree milestone`

### Delivered
- Unified specialist handoff generation, validation, authority truth, and operator-facing review around one canonical governance contract
- Made specialist stages fail closed on missing transcript, handoff, workspace inventory, structured evidence, and stale or thin `/ui-ux-pro-max` artifacts
- Blocked template-only and identity-only delivery from passing as real SaaS proof, including `/demo`-based loopholes
- Carried the stricter evidence and proof model through bootstrap, blocked, resumed, and recovered-final-state flows with targeted regression coverage
- Preserved the repaired GitHub/Vercel/shared-Supabase delivery backbone while raising the product-substance bar for approved-project completion

### Known Gaps
- Open-artifact audit still reports the legacy `Phase 11 / 11-HUMAN-UAT.md` entry even though it is marked passed with zero pending scenarios

### Notes
- See `.planning/milestones/v1.1.2-ROADMAP.md`, `.planning/milestones/v1.1.2-REQUIREMENTS.md`, and `.planning/v1.1.2-MILESTONE-AUDIT.md` for full archived detail
- Post-close cleanup added `18-VERIFICATION.md`, completed Nyquist validation artifacts for Phases 18-21, and brought the milestone audit to `passed`

## v1.1.1 - Delivery Pipeline Reliability Fixes

**Shipped:** 2026-04-30
**Phases:** 4 | **Plans:** 10 | **Tasks:** 30
**Timeline:** 2026-04-29 -> 2026-04-30
**Git range:** `c5ab649` -> `cb1464a`

### Delivered
- Restored governed GitHub auth detection so approved delivery can use either exported tokens or an already-authenticated `gh` CLI session
- Repaired canonical GitHub repository owner/name/url targeting so new approved projects stop falling back to slug-based repo identity
- Hardened GitHub sync for real Windows + pnpm workspaces through source-only snapshots, remote convergence, transport fallback, and granular sync evidence
- Restored governed Vercel auth and deploy reliability with explicit-token plus local-CLI auth paths and authoritative deploy metadata persistence
- Reworked authority, status rendering, and validator precedence so recovered successful runs now display the true final completed state while preserving blocked history as audit evidence
- Locked the repaired delivery path behind regression coverage across helper, controller, bootstrap, resume, governance, and CLI validator seams

### Known Gaps
- Open-artifact audit still reported `Phase 11 / 11-HUMAN-UAT.md` even though it is marked passed with zero pending scenarios; milestone close acknowledged it and carried the note into STATE.md
- A fresh live end-to-end delivery run is still required to validate the repaired path on the real operator environment after this milestone close

### Notes
- See `.planning/milestones/v1.1.1-ROADMAP.md` and `.planning/milestones/v1.1.1-REQUIREMENTS.md` for full archived detail
- Next work should start with live end-to-end validation before defining the next milestone

## v1.1 - SaaS Delivery Factory

**Shipped:** 2026-04-28
**Phases:** 7 | **Plans:** 20 | **Tasks:** 35
**Timeline:** 2026-04-26 -> 2026-04-28
**Git range:** `da8143c` -> `9c01d1f`

### Delivered
- Turned `standalone-saas-template` into a governed Hermes platform asset with a canonical contract and blocking conformance gate
- Enforced shared Supabase guardrails for app-key naming, shared-table boundaries, helper drift, and client-side shared-state writes
- Standardized a Claude Code specialist delivery team with governed scope reopen, replayable handoffs, and operator command wrappers
- Built an approved-project delivery pipeline that can bootstrap, track, validate, block, resume, and hand off delivery runs
- Shipped GitHub sync and Vercel deployment automation, then closed Phase 11 with real live GitHub/Vercel/operator evidence
- Reconciled ROADMAP.md, REQUIREMENTS.md, and STATE.md to the final verification and live-UAT evidence set for milestone close

### Known Gaps
- Milestone close proceeded without a dedicated `v1.1-MILESTONE-AUDIT.md` artifact
- Phase 11 live closure required recovery work during Phase 13 before the final archive could reflect the true shipped state

### Notes
- Deferred collaboration, realtime UX, and internal telemetry items remain in STATE.md / PROJECT.md for future milestones
- See `.planning/milestones/v1.1-ROADMAP.md` and `.planning/milestones/v1.1-REQUIREMENTS.md` for full archived detail

## v1.0 - milestone

**Shipped:** 2026-04-26
**Phases:** 6 | **Plans:** 18 | **Tasks:** 44
**Timeline:** 2026-04-24 -> 2026-04-26
**Git range:** `164c0fe` -> `3aa6fef`

### Delivered
- Established repeatable web-wide pain-signal intake with normalized storage and source history
- Built a shared-shortlist triage and role-analysis loop across Scout, CMO, Arch, CEO, and Accountant
- Shipped management-grade operating decision packages with execution-pack and board-brief derivatives
- Added executable governance approvals, audit trails, and blocking controls around high-impact actions
- Added a calm, operator-facing visibility surface with smoke-tested cron integration
- Strengthened downstream execution handoff and one-screen board briefing contracts for future team readiness

### Known Gaps
- Milestone close proceeded without a dedicated `v1.0-MILESTONE-AUDIT.md` artifact
- Original `.planning/REQUIREMENTS.md` checkbox list was not normalized during execution; archive reflects final completed status from traceability and verification artifacts

### Notes
- Deferred collaboration, realtime UX, and internal telemetry items remain in STATE.md / PROJECT.md for future milestones
- See `.planning/milestones/v1.0-ROADMAP.md` and `.planning/milestones/v1.0-REQUIREMENTS.md` for full archived detail
