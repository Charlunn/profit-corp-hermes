---
phase: 11-github-and-vercel-automation
slug: github-and-vercel-automation
status: ready
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-27
---

# Phase 11 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Validation Architecture

### Goal-Backward Validation
The phase passes only if Hermes can take a generated approved SaaS project from Phase 10 delivery-run bootstrap into GitHub repository preparation, canonical code sync, Vercel linkage, environment-contract application, deployment execution, and deploy outcome reporting, while preserving durable blocked states, resume points, and operator-visible evidence.

### Required Evidence
- Approved-project authority artifacts persist GitHub repository mode, repository identity, canonical branch, synced commit, Vercel project linkage, env-contract evidence, deploy status, deploy URL, and stage-specific evidence paths.
- `github_repository` and `github_sync` execute before any Vercel stage and block downstream deployment on missing tool, missing auth, repository linkage failure, or sync failure.
- `vercel_linkage` and `vercel_deploy` execute only after successful GitHub sync and completed environment-contract checks.
- Status rendering and pipeline validation surfaces show repository linkage, Vercel linkage, blocked reasons, evidence paths, and deploy outcomes without requiring operators to inspect hidden local CLI state.
- Successful deploy outcomes are written into both authority-layer artifacts and workspace-local handoff artifacts.

### Validation Layers
1. **Contract tests**
   - Lock stage names, block reasons, shipping metadata schema, and required status/validator linkage fields for GitHub and Vercel automation.
2. **GitHub workflow tests**
   - Validate create/attach repo modes, canonical branch persistence, sync evidence, and GitHub-triggered blocked states.
3. **Vercel workflow tests**
   - Validate one-project linkage, env-contract separation, deploy gating, blocked states, and deploy outcome persistence.
4. **Operator surface tests**
   - Validate CLI wrappers, `DELIVERY_PIPELINE_STATUS.md`, and validator outputs expose repository/deployment state and resume guidance.

### Critical Failure Modes
- GitHub or Vercel automation runs outside the approved-project authority layer and loses durable linkage metadata.
- Deployment starts before GitHub sync or before required env-contract values are present.
- Missing `gh`, missing `GH_TOKEN`, missing `VERCEL_TOKEN`, missing Vercel linkage, or env-contract mismatch collapses into generic failures instead of resumable blocked states.
- Renderer/validator surfaces omit repo/deploy evidence, forcing operators to inspect local `.git` or CLI state manually.
- Deploy outcome reaches workspace-local handoff artifacts but not the authority-level status and validation surfaces, or vice versa.

### Suggested Verification Commands
- `python -m unittest tests.test_phase11_github_sync -v`
- `python -m unittest tests.test_phase11_vercel_flow -v`
- `python -m unittest tests.test_approved_delivery_pipeline_cli tests.test_project_delivery_pipeline_bootstrap -v`
- `python -m unittest discover -s tests -p 'test_*.py' -v`

### Exit Criteria
The phase is verification-ready only when Hermes can repository-prepare and sync a generated SaaS workspace, link it to one deployable Vercel project, apply the declared environment contract, trigger deployment only after prerequisites pass, and report blocked or successful outcomes through both authority-layer and workspace-local artifacts.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` |
| **Config file** | none detected |
| **Quick run command** | `python -m unittest tests.test_phase11_github_sync tests.test_phase11_vercel_flow -v` |
| **Full suite command** | `python -m unittest discover -s tests -p 'test_*.py' -v` |
| **Estimated runtime** | ~60-120 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m unittest tests.test_phase11_github_sync tests.test_phase11_vercel_flow -v`
- **After every plan wave:** Run `python -m unittest discover -s tests -p 'test_*.py' -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 120 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 11-01-01 | 01 | 1 | SHIP-01, SHIP-02, SHIP-03, SHIP-04, SHIP-05, SHIP-06, SHIP-07, SHIP-08 | T-11-01 / T-11-02 / T-11-03 | Stage graph, block reasons, and shipping metadata are explicit before external side effects are implemented | unit/integration | `python -m unittest tests.test_phase11_github_sync tests.test_phase11_vercel_flow -v` | ✅ planned | ⬜ pending |
| 11-01-02 | 01 | 1 | SHIP-01, SHIP-02, SHIP-03, SHIP-04, SHIP-05, SHIP-06, SHIP-07, SHIP-08 | T-11-01 / T-11-03 | Controller/event contracts accept only the approved GitHub/Vercel stages and block reasons | unit/integration | `python -m unittest tests.test_phase11_github_sync tests.test_phase11_vercel_flow tests.test_project_delivery_pipeline_bootstrap tests.test_approved_delivery_pipeline_cli -v` | ✅ planned | ⬜ pending |
| 11-02-01 | 02 | 2 | SHIP-01, SHIP-02, SHIP-03, SHIP-08 | T-11-04 / T-11-07 | GitHub helper surface is constrained to repo prep and sync, with sanitized evidence and explicit blocked states | unit | `python -m unittest tests.test_phase11_github_sync -v` | ✅ planned | ⬜ pending |
| 11-02-02 | 02 | 2 | SHIP-01, SHIP-02, SHIP-03, SHIP-08 | T-11-05 / T-11-06 | Approved-delivery pipeline persists repo identity, canonical branch, sync evidence, and GitHub failures before Vercel stages | integration | `python -m unittest tests.test_phase11_github_sync tests.test_project_delivery_pipeline_bootstrap -v` | ✅ planned | ⬜ pending |
| 11-03-01 | 03 | 3 | SHIP-04, SHIP-05, SHIP-06, SHIP-08 | T-11-08 / T-11-09 | Vercel helper surface links one project, applies env contract, and blocks deploy when prerequisites fail | unit | `python -m unittest tests.test_phase11_vercel_flow -v` | ✅ planned | ⬜ pending |
| 11-03-02 | 03 | 3 | SHIP-04, SHIP-05, SHIP-06, SHIP-07, SHIP-08 | T-11-09 / T-11-10 / T-11-11 | Deploy outcomes and blocked states are visible in authority artifacts, validators, wrappers, docs, and workspace handoff outputs | integration | `python -m unittest tests.test_phase11_vercel_flow tests.test_approved_delivery_pipeline_cli -v` | ✅ planned | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `tests/test_phase11_github_sync.py` — red/green contract coverage for GitHub repo preparation, canonical sync, and blocked states
- [x] `tests/test_phase11_vercel_flow.py` — red/green contract coverage for Vercel linkage, env contract, deploy gating, and outcome reporting
- [x] Extend `tests/test_approved_delivery_pipeline_cli.py` — wrapper and operator-surface assertions for Phase 11
- [x] Extend `tests/test_project_delivery_pipeline_bootstrap.py` — post-bootstrap stage and blocked-state persistence assertions
- [x] Existing Python `unittest` infrastructure is sufficient; no framework install wave required

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real credentialed GitHub auth and repo bootstrap against the target org | SHIP-01, SHIP-02 | Depends on live platform-managed credentials and org permissions not present in unit tests | Run execute-phase with valid `GH_TOKEN`, inspect authority/status artifacts, and confirm remote repository exists with recorded branch/commit |
| Real Vercel project linkage, env sync, and deploy URL reachability | SHIP-04, SHIP-05, SHIP-06, SHIP-07 | Depends on live Vercel team/project permissions and deployment platform behavior | Run execute-phase with valid `VERCEL_TOKEN`/team scope, confirm linked project, env-contract evidence, deploy URL, and final handoff references |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all missing references
- [x] No watch-mode flags
- [x] Feedback latency < 120s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-04-27
