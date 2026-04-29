# Requirements: Profit-Corp Hermes

**Defined:** 2026-04-29
**Core Value:** Turn noisy web-wide user pain signals into a clear, actionable operating view: which problems are worth pursuing, what matters most, what is risky, and what the company should build, launch, and operationalize next.

## v1.1.1 Requirements

Requirements for restoring delivery-pipeline reliability after the live Hermes instance test.

### GitHub Authentication and Targeting

- [ ] **GHAUTH-01**: Approved-project delivery can treat an already-authenticated `gh` CLI session as a valid GitHub auth source when explicit `GH_TOKEN` / `GITHUB_TOKEN` env vars are absent
- [ ] **GHAUTH-02**: Approved-project delivery can still use explicit `GH_TOKEN` / `GITHUB_TOKEN` env vars when they are intentionally provided for non-interactive runs
- [ ] **GHOWN-01**: New approved projects derive the GitHub repository owner from an operator-controlled source instead of falling back to the project slug as the owner
- [ ] **GHOWN-02**: New approved projects derive the repository name and canonical repository URL consistently for both create and attach flows

### GitHub Sync Reliability

- [ ] **GHSYNC-01**: GitHub sync excludes generated dependency/build directories such as `node_modules`, `.next`, `dist`, and other non-source snapshots from the canonical workspace commit
- [ ] **GHSYNC-02**: GitHub sync succeeds on the real Windows + pnpm workspace shape used by live approved-project delivery without failing on long paths
- [ ] **GHSYNC-03**: GitHub sync can converge the configured remote when the workspace remote does not match the approved project repository
- [ ] **GHSYNC-04**: GitHub sync can use a working Git transport strategy for the operator environment instead of failing solely because HTTPS push is unavailable while SSH is healthy
- [ ] **GHSYNC-05**: GitHub sync writes evidence that distinguishes stage failures caused by staging, commit, remote, or push behavior

### Vercel Delivery Reliability

- [ ] **VERC-01**: Vercel linkage and deployment can use an available local authenticated Vercel CLI session when explicit `VERCEL_TOKEN` is absent but operator login is already valid
- [ ] **VERC-02**: Vercel linkage and deployment can still use explicit `VERCEL_TOKEN` for non-interactive automation runs
- [x] **VERC-03**: Vercel deploy records the real linked project name, scope, deploy URL, and deployment evidence for the approved project instead of stale values from previous runs
- [x] **VERC-04**: Vercel delivery failures distinguish invalid token, inaccessible scope, missing CLI, and actual deployment failure as separate operator-visible outcomes

### Authority and Status Convergence

- [ ] **STAT-01**: After GitHub sync succeeds, the authority record converges to the correct repo metadata, sync status, commit, and resume stage
- [ ] **STAT-02**: After Vercel link and deploy succeed, the authority record converges to the correct Vercel project metadata, deploy URL, deployment status, and evidence paths
- [ ] **STAT-03**: `DELIVERY_PIPELINE_STATUS.md` renders the latest true final state from authority data and event history instead of continuing to show a stale blocked view after successful recovery
- [ ] **STAT-04**: Operator-facing status surfaces clearly separate historical failures from the current authoritative state so a successfully recovered delivery run reads as completed, not still blocked

## Future Requirements

Deferred to later milestones.

### Factory Expansion

- **FACT-01**: Hermes can automatically register custom domains and DNS for deployed SaaS projects
- **FACT-02**: Hermes can run post-deploy canary checks and rollback workflows automatically for each shipped SaaS project
- **FACT-03**: Hermes can support broader multi-user/team delivery workflows beyond the current solo-operator model

## Out of Scope

| Feature | Reason |
|---------|--------|
| Building new end-user product features in generated SaaS apps | This milestone is for delivery-pipeline reliability only |
| Replacing the approved-project delivery architecture with a new orchestration model | The goal is to repair the shipped path, not redesign it wholesale |
| General platform expansion such as DNS automation, presets, or collaboration surfaces | Deferred until the current delivery path is reliable again |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| GHAUTH-01 | Phase 14 | Pending |
| GHAUTH-02 | Phase 14 | Pending |
| GHOWN-01 | Phase 14 | Pending |
| GHOWN-02 | Phase 14 | Pending |
| GHSYNC-01 | Phase 15 | Passed |
| GHSYNC-02 | Phase 15 | Passed |
| GHSYNC-03 | Phase 15 | Passed |
| GHSYNC-04 | Phase 15 | Passed |
| GHSYNC-05 | Phase 15 | Passed |
| VERC-01 | Phase 16 | Pending |
| VERC-02 | Phase 16 | Pending |
| VERC-03 | Phase 16 | Pending |
| VERC-04 | Phase 16 | Pending |
| STAT-01 | Phase 17 | Pending |
| STAT-02 | Phase 17 | Pending |
| STAT-03 | Phase 17 | Pending |
| STAT-04 | Phase 17 | Pending |

**Coverage:**
- v1.1.1 requirements: 17 total
- Mapped to phases: 17
- Unmapped: 0

---
*Requirements defined: 2026-04-29*
*Last updated: 2026-04-29 after v1.1.1 milestone kickoff*
