# Profit-Corp Hermes

## Roadmap

### Phase 14: GitHub Auth and Repo Target Reliability

**Goal:** Repair approved-project GitHub authentication detection and repository targeting so governed delivery uses the real authenticated operator identity and correct repo defaults.
**Depends on**: Phase 13
**Plans**: 2 plans

Plans:
- [x] 14-01: Fix GitHub credential detection and repository owner fallback in approved-project delivery
- [x] 14-02: Add regression coverage and operator-surface validation for authenticated GitHub repository targeting

**Success Criteria** (what must be TRUE):
1. Approved-project delivery can detect valid GitHub auth from the operator environment without requiring manual token export.
2. New approved projects target the correct GitHub owner/repository instead of falling back to the project slug.
3. Operator-facing artifacts and regressions prove the repaired GitHub targeting path is stable.

### Phase 15: GitHub Sync Reliability on Real Workspaces

**Goal**: Make approved-project GitHub sync succeed reliably on real Windows + pnpm workspaces by hardening snapshot, path, and transport behavior.
**Depends on**: Phase 14
**Plans**: 3 plans

Plans:
- [x] 15-01: Normalize GitHub sync workspace snapshots to source-only content for real workspaces
- [x] 15-02: Repair sync transport/path handling for real operator Windows workspaces
- [x] 15-03: Add end-to-end validation for GitHub sync on live-style workspaces

**Success Criteria** (what must be TRUE):
1. GitHub sync snapshots exclude lock/content that breaks real operator workspaces while preserving source truth.
2. Sync can converge remotes and push successfully on the live Windows workspace using healthy transport fallbacks.
3. Validator and tests prove real-workspace GitHub sync completes with authoritative evidence.

### Phase 16: Vercel Auth and Deploy Reliability

**Goal**: Repair approved-project Vercel auth and deploy behavior so live operator environments can link and deploy without manual CLI rescue while preserving governed evidence.
**Depends on**: Phase 15
**Plans**: 3 plans

Plans:
- [x] 16-01: Restore Vercel auth detection and failure taxonomy across governed helper paths
- [x] 16-02: Persist authoritative-only Vercel link/deploy metadata after real success and replace stale values on resume
- [x] 16-03: Close the final Vercel regression envelope across helper, controller, governance, bootstrap, and resume seams

**Success Criteria** (what must be TRUE):
1. Approved delivery can proceed when the operator machine has a valid local Vercel login even if `VERCEL_TOKEN` was not manually exported.
2. Vercel failures distinguish invalid token, inaccessible scope, missing CLI, and actual deploy failure as separate blocked outcomes.
3. Successful deploy writes the true project name, scope, deploy URL, deployment status, and evidence paths for the approved project.

### Phase 17: Authority and Status Convergence

**Goal**: Make the authority record, event stream, and operator status surfaces converge to the true recovered end state after GitHub/Vercel success.
**Depends on**: Phase 16
**Plans**: 3 plans

Plans:
- [ ] 17-01-PLAN.md — Normalize post-success authority writes for recovered GitHub sync and Vercel success stages
- [ ] 17-02-PLAN.md — Rework status rendering and validation so current authority truth overrides stale blocked state while preserving history
- [ ] 17-03-PLAN.md — Add end-to-end recovered-run regression coverage across bootstrap, resume, and validator surfaces

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
