# Roadmap: Profit-Corp Hermes

## Milestones

- ✅ **v1.0 milestone** — Phases 1-6 (shipped 2026-04-26) — see `.planning/milestones/v1.0-ROADMAP.md`
- ✅ **v1.1 SaaS Delivery Factory** — Phases 7-13 (shipped 2026-04-28) — see `.planning/milestones/v1.1-ROADMAP.md`
- 🔄 **v1.1.1 Delivery Pipeline Reliability Fixes** — Phases 14-17 (planning)

## Current Milestone: v1.1.1 Delivery Pipeline Reliability Fixes

**Goal:** Repair the approved-project GitHub/Vercel shipping path so the live operator environment can complete delivery without manual rescue and the authority/status surfaces converge to the true final state.

## Phases

### Phase 14: GitHub Auth and Repository Target Resolution

**Goal**: Fix GitHub credential detection and repository targeting so a new approved project resolves the correct owner/repo and can enter the repository-preparation stage without manual env shims.
**Depends on**: Phase 13
**Plans**: 3 plans

Plans:
- [ ] 14-01: Unify GitHub auth source resolution across env-token and authenticated `gh` CLI flows
- [ ] 14-02: Replace project-slug owner fallback with operator-controlled owner/repo derivation and canonical repo metadata writes
- [ ] 14-03: Add regression coverage for create vs attach repository preparation against live-instance failure signatures

**Success Criteria** (what must be TRUE):
1. Approved delivery no longer blocks with `missing_github_auth` when `gh` is already authenticated for the operator machine.
2. New approved projects derive GitHub owner, repository name, and canonical URL from valid operator-controlled inputs instead of falling back to the project slug as owner.
3. Repository preparation evidence clearly shows which auth path and targeting metadata were used.

### Phase 15: GitHub Sync Reliability on Real Workspaces

**Goal**: Make GitHub sync succeed on the real Windows + pnpm generated workspace shape by fixing snapshot filtering, remote convergence, and transport behavior.
**Depends on**: Phase 14
**Plans**: 3 plans

Plans:
- [x] 15-01: Define canonical workspace snapshot filters and generated-project `.gitignore` expectations for delivery sync
- [x] 15-02: Harden git remote convergence, branch setup, and push transport behavior for the operator environment
- [x] 15-03: Add regression validation for Windows long-path, dependency-tree, and remote-mismatch failure cases

**Success Criteria** (what must be TRUE):
1. GitHub sync no longer stages `node_modules`, build outputs, or other non-source artifacts that caused the live long-path failure.
2. GitHub sync can converge a mismatched remote and use a working push transport for the real operator machine.
3. GitHub sync evidence distinguishes stage/add/commit/push failures so operators can see the true failure boundary.

### Phase 16: Vercel Auth and Deploy Reliability

**Goal**: Fix Vercel auth handling and deploy metadata capture so the approved-project pipeline can reuse the real operator auth path and record the actual linked/deployed project.
**Depends on**: Phase 15
**Plans**: 3 plans

Plans:
- [x] 16-01: Unify Vercel auth source resolution across explicit token and locally authenticated CLI flows
- [x] 16-02: Harden Vercel link/env/deploy execution so scope, project, and auth failures surface distinctly
- [ ] 16-03: Capture real deployment metadata and evidence from the linked approved project instead of stale or inherited values

**Success Criteria** (what must be TRUE):
1. Approved delivery can proceed when the operator machine has a valid local Vercel login even if `VERCEL_TOKEN` was not manually exported.
2. Vercel failures distinguish invalid token, inaccessible scope, missing CLI, and actual deploy failure as separate blocked outcomes.
3. Successful deploy writes the true project name, scope, deploy URL, deployment status, and evidence paths for the approved project.

### Phase 17: Authority and Status Convergence

**Goal**: Make the authority record, event stream, and operator status surfaces converge to the true recovered end state after GitHub/Vercel success.
**Depends on**: Phase 16
**Plans**: 3 plans

Plans:
- [ ] 17-01: Normalize post-success authority updates for GitHub sync, Vercel link, and Vercel deploy stages
- [ ] 17-02: Rework approved-delivery status rendering so current authority state overrides stale blocked history without hiding the audit trail
- [ ] 17-03: Add end-to-end recovery validation proving a once-blocked live run can finish and render as completed in authority/status artifacts

**Success Criteria** (what must be TRUE):
1. After GitHub sync and Vercel deploy succeed, `APPROVED_PROJECT.json` reflects the true final repo/deploy metadata and completed pipeline state.
2. `DELIVERY_PIPELINE_STATUS.md` and `FINAL_OPERATOR_REVIEW.md` render the current final truth while still preserving historical failures in the event history section.
3. A recovered approved delivery run reads as completed to the operator instead of remaining blocked after manual or automated recovery.

## Milestone Summary

**Key Decisions:**
- Treat the live Hermes instance test as authoritative evidence for v1.1.1 scope instead of reopening broad product-factory exploration
- Keep the approved-project delivery architecture and repair its broken auth, sync, deploy, and status boundaries in place
- Prioritize real operator-environment compatibility over idealized token-only automation assumptions

**Issues Targeted:**
- `missing_github_auth` despite valid `gh` login
- GitHub owner fallback to project slug
- Windows long-path / dependency snapshot failures during `github_sync`
- HTTPS push assumptions that fail while SSH is healthy
- Vercel token-only gating that ignores a valid local CLI login path
- Authority/status artifacts remaining blocked after a successful recovered live deploy

**Deferred:**
- DNS/domain automation
- post-deploy canary automation
- broader multi-user/team operating workflows

---

_For current project status, see .planning/PROJECT.md_
