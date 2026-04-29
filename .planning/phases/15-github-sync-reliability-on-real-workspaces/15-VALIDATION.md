---
phase: 15
slug: github-sync-reliability-on-real-workspaces
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-29
---

# Phase 15 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` |
| **Config file** | none — existing script tests use importlib-based loading |
| **Quick run command** | `python -m unittest tests.test_phase11_github_sync` |
| **Full suite command** | `python -m unittest tests.test_phase11_github_sync tests.test_project_delivery_pipeline_bootstrap tests.test_project_delivery_pipeline_resume tests.test_phase12_credential_governance` |
| **Estimated runtime** | ~10 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m unittest tests.test_phase11_github_sync`
- **After every plan wave:** Run `python -m unittest tests.test_phase11_github_sync tests.test_project_delivery_pipeline_bootstrap tests.test_project_delivery_pipeline_resume tests.test_phase12_credential_governance`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 15 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 15-01-01 | 01 | 1 | GHSYNC-01, GHSYNC-02 | T-15-01 / T-15-02 | Generated dependency/build paths are excluded from canonical snapshot staging and Windows+pnpm path-heavy workspaces do not fail during staging | unit | `python -m unittest tests.test_phase11_github_sync` | ✅ | ⬜ pending |
| 15-02-01 | 02 | 1 | GHSYNC-03, GHSYNC-04 | T-15-03 / T-15-04 | Remote URL converges to approved authority metadata and push uses a working transport strategy without silently targeting the wrong remote | unit | `python -m unittest tests.test_phase11_github_sync` | ✅ | ⬜ pending |
| 15-03-01 | 03 | 2 | GHSYNC-05 | T-15-05 / — | Helper and controller evidence distinguish remote/setup, staging, commit, and push failure boundaries while preserving governance audit/event flow | unit + integration | `python -m unittest tests.test_phase11_github_sync tests.test_project_delivery_pipeline_bootstrap tests.test_project_delivery_pipeline_resume tests.test_phase12_credential_governance` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_phase11_github_sync.py` — add red tests for snapshot filters, remote mismatch convergence, transport fallback, and granular sync evidence
- [ ] `tests/test_project_delivery_pipeline_bootstrap.py` — add assertions for any newly persisted sync metadata/evidence fields
- [ ] `tests/test_project_delivery_pipeline_resume.py` — confirm resume continuity after sync metadata changes
- [ ] `tests/test_phase12_credential_governance.py` — verify governed audit/event contract still accepts refined sync failure boundaries

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Live Windows + pnpm approved-project workspace sync succeeds end-to-end | GHSYNC-02, GHSYNC-04 | Repo tests can simulate command boundaries but not the operator machine’s real path depth / transport setup | Run the approved-project delivery pipeline on the real operator machine, confirm `github_sync` completes without staging `node_modules`/build artifacts and without HTTPS-only push failure |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 15s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
