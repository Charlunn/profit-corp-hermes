# Roadmap: Profit-Corp Hermes

## Milestones

- ✅ **v1.0 milestone** — Phases 1-6 (shipped 2026-04-26) — see `.planning/milestones/v1.0-ROADMAP.md`
- ◆ **v1.1 SaaS Delivery Factory** — Phases 7-12 (planned)

## Phases

<details>
<summary>✅ v1.0 milestone (Phases 1-6) — SHIPPED 2026-04-26</summary>

- [x] Phase 1: Pain-Signal Discovery Foundation (4/4 plans) — completed 2026-04-25
- [x] Phase 2: Signal Triage and Role Analysis Loop (3/3 plans) — completed 2026-04-25
- [x] Phase 3: Decision Package Quality (3/3 plans) — completed 2026-04-25
- [x] Phase 4: Governance and Control Layer (3/3 plans) — completed 2026-04-25
- [x] Phase 5: Operating Visibility Surface (2/2 plans) — completed 2026-04-25
- [x] Phase 6: Execution Handoff and Team Readiness (3/3 plans) — completed 2026-04-26

</details>

<details open>
<summary>◆ v1.1 SaaS Delivery Factory (Phases 7-12) — IN PROGRESS</summary>

- [x] Phase 7: Template Assetization and Platform Contract — completed 2026-04-26
- [ ] Phase 8: Shared Supabase Backend Guardrails
- [ ] Phase 9: Claude Code Delivery Team Orchestration
- [ ] Phase 10: Approved Project Delivery Pipeline (0/3 plans) — planned
- [ ] Phase 11: GitHub and Vercel Automation
- [ ] Phase 12: Credential Governance and Operator Handoff

</details>

## Proposed Roadmap

**6 phases** | **39 requirements mapped** | All covered ✓

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 7 | Template Assetization and Platform Contract | Register the standalone SaaS template as a governed Hermes asset and codify how new projects may extend it safely. | TMPL-01, TMPL-02, TMPL-03, TMPL-04, TMPL-05, TMPL-06 | 4 |
| 8 | Shared Supabase Backend Guardrails | Enforce the single-Supabase, shared-platform contract so generated SaaS projects stay inside safe shared-table and app-prefix boundaries. | BACK-01, BACK-02, BACK-03, BACK-04, BACK-05, BACK-06 | 4 |
| 9 | Claude Code Delivery Team Orchestration | Define the specialist delivery team, role contracts, and GSD operating boundaries for approved-project execution. | TEAM-01, TEAM-02, TEAM-03, TEAM-04, TEAM-05, TEAM-06 | 4 |
| 10 | Approved Project Delivery Pipeline | Convert a user-approved opportunity into a live delivery workflow with project brief generation, template instantiation, and tracked execution state. | PIPE-01, PIPE-02, PIPE-03, PIPE-04, PIPE-05, PIPE-06, PIPE-07 | 4 |
| 11 | GitHub and Vercel Automation | Enable platform-managed repository sync, deployable Vercel linking, environment configuration, and deployment execution for generated SaaS projects. | SHIP-01, SHIP-02, SHIP-03, SHIP-04, SHIP-05, SHIP-06, SHIP-07, SHIP-08 | 4 |
| 12 | Credential Governance and Operator Handoff | Add the audit, credential-scope, platform-justification, and operator review controls needed to keep automated delivery trustworthy. | GOV-01, GOV-02, GOV-03, GOV-04, GOV-05, GOV-06 | 4 |

### Phase Details

### Phase 7: Template Assetization and Platform Contract
**Goal:** Register `standalone-saas-template` as a first-class Hermes platform asset and define the authoritative template rules for safe reuse.
**Requirements:** TMPL-01, TMPL-02, TMPL-03, TMPL-04, TMPL-05, TMPL-06
**Success Criteria:**
1. Hermes stores canonical metadata for the template source, purpose, and supported stack.
2. Delivery workflows can read one authoritative contract describing allowed customization points and protected platform layers.
3. Hermes can create a new project workspace from the template and inject project identity values without manual copy-paste setup.
4. Hermes can run a conformance check that detects whether a generated project still respects the template contract before handoff or deployment.

### Phase 8: Shared Supabase Backend Guardrails
**Goal:** Make the shared-backend platform rules executable so new SaaS projects cannot silently drift outside the one-Supabase model.
**Requirements:** BACK-01, BACK-02, BACK-03, BACK-04, BACK-05, BACK-06
**Success Criteria:**
1. Hermes can validate that generated projects target the shared Supabase backend model by default.
2. Hermes can enforce `APP_KEY_` naming for product-specific business tables and block unprefixed business tables.
3. Hermes preserves the global shared-table boundary around `users`, `orders`, `payments`, and `subscriptions`.
4. Hermes can detect direct client-side writes to shared payment or entitlement state and flag or block them.

### Phase 9: Claude Code Delivery Team Orchestration
**Goal:** Standardize the specialist development team and its handoff contracts so approved SaaS delivery no longer depends on ad-hoc owner orchestration.
**Requirements:** TEAM-01, TEAM-02, TEAM-03, TEAM-04, TEAM-05, TEAM-06
**Success Criteria:**
1. Hermes defines the specialist delivery roles, responsibilities, and expected artifacts for each step of project execution.
2. Each role receives the approved brief, template rules, and GSD constraints before implementation begins.
3. Delivery roles are prevented from operating outside approved scope without an explicit scope reopen.
4. Hermes records which role performed each major delivery action and can replay the overall workflow from those artifacts.

### Phase 10: Approved Project Delivery Pipeline
**Goal:** Turn a one-time owner approval into an automated delivery workflow with tracked state and reliable blocking behavior.
**Requirements:** PIPE-01, PIPE-02, PIPE-03, PIPE-04, PIPE-05, PIPE-06, PIPE-07
**Plans:** 3 plans
Plans:
- [ ] `10-01-PLAN.md` — create the approved-project authority record and deterministic delivery-ready brief contract.
- [ ] `10-02-PLAN.md` — wire approval-to-workspace bootstrap, Phase 10 state tracking, blocking behavior, and resume/retry flow.
- [ ] `10-03-PLAN.md` — add validator, orchestrator command wrappers, and operator/CEO runbooks for start/status/resume/handoff.
**Success Criteria:**
1. An approved opportunity can be converted into a delivery-ready project brief without manual restructuring.
2. Hermes can automatically instantiate a project from the template and attach the approved brief to the delivery workspace.
3. Hermes tracks delivery state from initialization through handoff in a durable, operator-readable way.
4. Hermes blocks or stops the workflow when platform rules, credentials, or deployment preconditions are missing and reports the reason clearly.

### Phase 11: GitHub and Vercel Automation
**Goal:** Use platform-managed credentials to sync generated projects to GitHub and move them through a deployable Vercel flow.
**Requirements:** SHIP-01, SHIP-02, SHIP-03, SHIP-04, SHIP-05, SHIP-06, SHIP-07, SHIP-08
**Success Criteria:**
1. Hermes can create or prepare a GitHub repository for an approved SaaS project using platform-managed credentials.
2. Hermes can sync generated code to the target repository and record the repo, branch, and delivery-run linkage.
3. Hermes can link the project to Vercel, apply required deployment environment values, and trigger deployment when checks pass.
4. Hermes reports deployment outcomes back into the delivery record and blocks deployment when linkage, credentials, or environment configuration are incomplete.

### Phase 12: Credential Governance and Operator Handoff
**Goal:** Keep automated delivery safe by adding auditable credential controls, platform-change justification, and a final operator-facing review surface.
**Requirements:** GOV-01, GOV-02, GOV-03, GOV-04, GOV-05, GOV-06
**Success Criteria:**
1. Hermes uses platform-managed GitHub and Vercel credentials through a documented, constrained path rather than open-ended arbitrary access.
2. Hermes records an audit trail for repository creation, sync, environment setup, and deployment actions.
3. Hermes distinguishes platform-level changes from product-level changes and requires explicit justification before protected platform primitives are modified.
4. Hermes produces an operator-visible review artifact that surfaces blocked deliveries, approval failures, deployment failures, and final handoff status.

## Progress

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|----------------|--------|-----------|
| 1. Pain-Signal Discovery Foundation | v1.0 | 4/4 | Complete | 2026-04-25 |
| 2. Signal Triage and Role Analysis Loop | v1.0 | 3/3 | Complete | 2026-04-25 |
| 3. Decision Package Quality | v1.0 | 3/3 | Complete | 2026-04-25 |
| 4. Governance and Control Layer | v1.0 | 3/3 | Complete | 2026-04-25 |
| 5. Operating Visibility Surface | v1.0 | 2/2 | Complete | 2026-04-25 |
| 6. Execution Handoff and Team Readiness | v1.0 | 3/3 | Complete | 2026-04-26 |
| 7. Template Assetization and Platform Contract | v1.1 | 3/3 | Complete | 2026-04-26 |
| 8. Shared Supabase Backend Guardrails | v1.1 | 0/0 | Planned | — |
| 9. Claude Code Delivery Team Orchestration | v1.1 | 0/0 | Planned | — |
| 10. Approved Project Delivery Pipeline | v1.1 | 0/3 | Planned | — |
| 11. GitHub and Vercel Automation | v1.1 | 0/0 | Planned | — |
| 12. Credential Governance and Operator Handoff | v1.1 | 0/0 | Planned | — |
