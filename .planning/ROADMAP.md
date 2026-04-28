# Roadmap: Profit-Corp Hermes

## Milestones

- ✅ **v1.0 milestone** — Phases 1-6 (shipped 2026-04-26) — see `.planning/milestones/v1.0-ROADMAP.md`
- ◆ **v1.1 SaaS Delivery Factory** — Phases 7-13 (execution complete; pending milestone close)

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
<summary>◆ v1.1 SaaS Delivery Factory (Phases 7-13) — EXECUTION COMPLETE, AWAITING MILESTONE CLOSE</summary>

- [x] Phase 7: Template Assetization and Platform Contract (3/3 plans) — completed 2026-04-26
- [x] Phase 8: Shared Supabase Backend Guardrails (2/2 plans + verification closure) — completed 2026-04-28
- [x] Phase 9: Claude Code Delivery Team Orchestration (3/3 plans) — completed 2026-04-27
- [x] Phase 10: Approved Project Delivery Pipeline (3/3 plans) — completed 2026-04-27
- [x] Phase 11: GitHub and Vercel Automation (3/3 plans + live UAT closure) — completed 2026-04-28
- [x] Phase 12: Credential Governance and Operator Handoff (3/3 plans) — completed 2026-04-28
- [x] Phase 13: v1.1 Closure and Planning-State Reconciliation (3/3 plans) — completed 2026-04-28

</details>

## Proposed Roadmap

**7 phases** | **39 requirements mapped** | All covered ✓

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 7 | Template Assetization and Platform Contract | Register the standalone SaaS template as a governed Hermes asset and codify how new projects may extend it safely. | TMPL-01, TMPL-02, TMPL-03, TMPL-04, TMPL-05, TMPL-06 | 4 |
| 8 | Shared Supabase Backend Guardrails | Enforce the single-Supabase, shared-platform contract so generated SaaS projects stay inside safe shared-table and app-prefix boundaries. | BACK-01, BACK-02, BACK-03, BACK-04, BACK-05, BACK-06 | 4 |
| 9 | Claude Code Delivery Team Orchestration | Define the specialist delivery team, role contracts, and GSD operating boundaries for approved-project execution. | TEAM-01, TEAM-02, TEAM-03, TEAM-04, TEAM-05, TEAM-06 | 4 |
| 10 | Approved Project Delivery Pipeline | Turn a one-time owner approval into an automated delivery workflow with tracked state and reliable blocking behavior. | PIPE-01, PIPE-02, PIPE-03, PIPE-04, PIPE-05, PIPE-06, PIPE-07 | 4 |
| 11 | GitHub and Vercel Automation | Use platform-managed credentials to sync generated projects to GitHub and move them through a deployable Vercel flow. | SHIP-01, SHIP-02, SHIP-03, SHIP-04, SHIP-05, SHIP-06, SHIP-07, SHIP-08 | 4 |
| 12 | Credential Governance and Operator Handoff | Add the audit, credential-scope, platform-justification, and operator review controls needed to keep automated delivery trustworthy. | GOV-01, GOV-02, GOV-03, GOV-04, GOV-05, GOV-06 | 4 |
| 13 | v1.1 Closure and Planning-State Reconciliation | Close remaining verification/UAT gaps and reconcile canonical planning surfaces so v1.1 roadmap, requirements, and state match final evidence. | BACK-01..06, TEAM-01..06, PIPE-01..07, SHIP-01..08, GOV-01..06 | 3 |

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
**Plans:** 2/2 plans complete
Plans:
- [x] `08-01-PLAN.md` — extend the template authority contract, registry metadata, and workspace guardrail artifact for the shared Supabase model. (completed 2026-04-26)
- [x] `08-02-PLAN.md` — expand the unified conformance gate to block shared-backend boundary violations and protected helper drift. (completed 2026-04-26)
**Success Criteria:**
1. Hermes can validate that generated projects target the shared Supabase backend model by default.
2. Hermes can enforce `APP_KEY_` naming for product-specific business tables and block unprefixed business tables.
3. Hermes preserves the global shared-table boundary around `users`, `orders`, `payments`, and `subscriptions`.
4. Hermes can detect direct client-side writes to shared payment or entitlement state and flag or block them.

### Phase 9: Claude Code Delivery Team Orchestration
**Goal:** Standardize the specialist development team and its handoff contracts so approved SaaS delivery no longer depends on ad-hoc owner orchestration.
**Requirements:** TEAM-01, TEAM-02, TEAM-03, TEAM-04, TEAM-05, TEAM-06
**Plans:** 3/3 plans complete
Plans:
- [x] `09-01-PLAN.md` — lock the fixed delivery team contract, shared input bundle, and stage/final handoff templates. (completed 2026-04-27)
- [x] `09-02-PLAN.md` — build workspace-local delivery-run bootstrap, append-only event logging, and rendered status artifacts. (completed 2026-04-27)
- [x] `09-03-PLAN.md` — wire scope-reopen governance, replay validation, and operator command-entry integration. (completed 2026-04-27)
**Success Criteria:**
1. Hermes defines the specialist delivery roles, responsibilities, and expected artifacts for each step of project execution.
2. Each role receives the approved brief, template rules, and GSD constraints before implementation begins.
3. Delivery roles are prevented from operating outside approved scope without an explicit scope reopen.
4. Hermes records which role performed each major delivery action and can replay the overall workflow from those artifacts.

### Phase 10: Approved Project Delivery Pipeline
**Goal:** Turn a one-time owner approval into an automated delivery workflow with tracked state and reliable blocking behavior.
**Requirements:** PIPE-01, PIPE-02, PIPE-03, PIPE-04, PIPE-05, PIPE-06, PIPE-07
**Plans:** 3/3 plans complete
Plans:
- [x] `10-01-PLAN.md` — create the approved-project authority record and deterministic delivery-ready brief contract. (completed 2026-04-27)
- [x] `10-02-PLAN.md` — wire approval-to-workspace bootstrap, Phase 10 state tracking, blocking behavior, and resume/retry flow. (completed 2026-04-27)
- [x] `10-03-PLAN.md` — add validator, orchestrator command wrappers, and operator/CEO runbooks for start/status/resume/handoff. (completed 2026-04-27)
**Success Criteria:**
1. An approved opportunity can be converted into a delivery-ready project brief without manual restructuring.
2. Hermes can automatically instantiate a project from the shared template and attach the approved brief to the delivery workspace.
3. Hermes tracks delivery state from initialization through handoff in a durable, operator-readable way.
4. Hermes blocks or stops the workflow when platform rules, credentials, or deployment preconditions are missing and reports the reason clearly.

### Phase 11: GitHub and Vercel Automation
**Goal:** Use platform-managed credentials to sync generated projects to GitHub and move them through a deployable Vercel flow.
**Requirements:** SHIP-01, SHIP-02, SHIP-03, SHIP-04, SHIP-05, SHIP-06, SHIP-07, SHIP-08
**Plans:** 3/3 plans complete
Plans:
- [x] `11-01-PLAN.md` — lock GitHub/Vercel shipping stage contracts, blocked-state evidence, and persisted metadata scaffolding. (completed 2026-04-27)
- [x] `11-02-PLAN.md` — implement GitHub repository preparation, canonical sync, and durable repo linkage in the approved-delivery pipeline. (completed 2026-04-27)
- [x] `11-03-PLAN.md` — wire Vercel linkage, env-contract enforcement, deploy execution, and operator-visible outcome reporting. (completed 2026-04-27)
**Success Criteria:**
1. Hermes can create or prepare a GitHub repository for an approved SaaS project using platform-managed credentials.
2. Hermes can sync generated code to the target repository and record the repo, branch, and delivery-run linkage.
3. Hermes can link the project to Vercel, apply required deployment environment values, and trigger deployment when checks pass.
4. Hermes reports deployment outcomes back into the delivery record and blocks deployment when linkage, credentials, or environment configuration are incomplete.

### Phase 12: Credential Governance and Operator Handoff
**Goal:** Keep automated delivery safe by adding auditable credential controls, platform-change justification, and a final operator-facing review surface.
**Requirements:** GOV-01, GOV-02, GOV-03, GOV-04, GOV-05, GOV-06
**Plans:** 3/3 plans complete
Plans:
- [x] `12-01-PLAN.md` — harden the authority-controlled credential path with allowlisted actions and durable audit evidence. (completed 2026-04-28)
- [x] `12-02-PLAN.md` — add protected-surface classification plus governed platform-justification blocking before sync and deploy. (completed 2026-04-28)
- [x] `12-03-PLAN.md` — render the final operator review artifact and validator coverage for governance visibility. (completed 2026-04-28)
**Success Criteria:**
1. Hermes uses platform-managed GitHub and Vercel credentials through a documented, constrained path rather than open-ended arbitrary access.
2. Hermes records an audit trail for repository creation, sync, environment setup, and deployment actions.
3. Hermes distinguishes platform-level changes from product-level changes and requires explicit justification before protected platform primitives are modified.
4. Hermes produces an operator-visible review artifact that surfaces blocked deliveries, approval failures, deployment failures, and final handoff status.

### Phase 13: v1.1 Closure and Planning-State Reconciliation
**Goal:** Close the remaining Phase 8 and Phase 11 verification/UAT gaps, then reconcile the canonical planning surfaces so v1.1 documentation matches final execution evidence.
**Requirements:** BACK-01..06, TEAM-01..06, PIPE-01..07, SHIP-01..08, GOV-01..06
**Depends on:** Phase 12
**Plans:** 3/3 plans complete

Plans:
- [x] `13-01-PLAN.md` — formalize Phase 8 verification closure and align Phase 8 validation evidence. (completed 2026-04-28)
- [x] `13-02-PLAN.md` — complete the deferred Phase 11 live GitHub/Vercel/operator UAT closure. (completed 2026-04-28)
- [x] `13-03-PLAN.md` — reconcile ROADMAP, REQUIREMENTS, and STATE to the final Phase 8-12 evidence base. (completed 2026-04-28)

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
| 8. Shared Supabase Backend Guardrails | v1.1 | 2/2 | Complete | 2026-04-28 |
| 9. Claude Code Delivery Team Orchestration | v1.1 | 3/3 | Complete | 2026-04-27 |
| 10. Approved Project Delivery Pipeline | v1.1 | 3/3 | Complete | 2026-04-27 |
| 11. GitHub and Vercel Automation | v1.1 | 3/3 | Complete | 2026-04-28 |
| 12. Credential Governance and Operator Handoff | v1.1 | 3/3 | Complete | 2026-04-28 |
| 13. v1.1 Closure and Planning-State Reconciliation | v1.1 | 3/3 | Complete | 2026-04-28 |
