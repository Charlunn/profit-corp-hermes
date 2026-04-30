---
phase: 16
slug: vercel-auth-and-deploy-reliability
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-29
---

# Phase 16 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` |
| **Config file** | none — existing delivery tests use importlib-based script loading |
| **Quick run command** | `python -m unittest tests.test_phase11_vercel_flow -v` |
| **Full targeted suite** | `python -m unittest tests.test_phase11_vercel_flow tests.test_project_delivery_pipeline_bootstrap tests.test_project_delivery_pipeline_resume tests.test_phase12_credential_governance -v` |
| **Estimated runtime** | ~10–20 seconds |

---

## Sampling Rate

- **After every helper/controller task commit:** Run `python -m unittest tests.test_phase11_vercel_flow -v`
- **After every plan wave:** Run `python -m unittest tests.test_phase11_vercel_flow tests.test_project_delivery_pipeline_bootstrap tests.test_project_delivery_pipeline_resume tests.test_phase12_credential_governance -v`
- **Before `/gsd-verify-work`:** Full targeted suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Plan Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 16-01-01 | 01 | 1 | VERC-01, VERC-02, VERC-04 | T-16-01 / T-16-02 / T-16-03 | Helper resolves explicit-token or local-CLI auth correctly and emits separated missing-cli/auth/scope/deploy outcomes | unit | `python -m unittest tests.test_phase11_vercel_flow -v` | ✅ | ⬜ pending |
| 16-02-01 | 02 | 2 | VERC-03, VERC-04 | T-16-04 / T-16-05 / T-16-06 | Controller persists only authoritative Vercel metadata/evidence and consumer surfaces read persisted truth without stale defaults | integration | `python -m unittest tests.test_project_delivery_pipeline_bootstrap tests.test_project_delivery_pipeline_resume -v` | ✅ | ⬜ pending |
| 16-03-01 | 03 | 3 | VERC-01, VERC-02, VERC-03, VERC-04 | T-16-07 / T-16-08 / T-16-09 | Governance and regression suites preserve the real Vercel auth/deploy outcome boundary across fresh and resumed runs | unit + integration | `python -m unittest tests.test_phase11_vercel_flow tests.test_project_delivery_pipeline_bootstrap tests.test_project_delivery_pipeline_resume tests.test_phase12_credential_governance -v` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_phase11_vercel_flow.py` — add red tests for local CLI auth without token, explicit-token continuity, invalid-auth vs inaccessible-scope vs deploy-failure separation, and helper evidence auth-source fields
- [ ] `tests/test_project_delivery_pipeline_bootstrap.py` — add assertions that Vercel project/scope/URL are not persisted before link success and are replaced by current-run truth after success
- [ ] `tests/test_project_delivery_pipeline_resume.py` — add recovery assertions that stale Vercel metadata/evidence are replaced on resumed runs
- [ ] `tests/test_phase12_credential_governance.py` — add audit/event assertions for refined Vercel outcome taxonomy and target metadata visibility

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Real operator machine can reuse a live Vercel CLI login and complete `vercel_linkage` / `vercel_deploy` without exported `VERCEL_TOKEN` | VERC-01, VERC-03 | Repo tests can simulate CLI/auth boundaries but cannot prove the owner machine’s real Vercel login state | Run approved-project delivery on the operator machine with a valid Vercel CLI login and no exported `VERCEL_TOKEN`; confirm `vercel_linkage` and `vercel_deploy` complete and authority artifacts show the real linked project/scope/deploy URL |
| Operator-visible blocked outcomes match the actual live failure class | VERC-04 | Automated tests stub stderr signatures but cannot sample every real CLI/environment variation | Intentionally test one invalid-token run and one inaccessible-scope run, then confirm the blocked/failure reason shown in authority/status artifacts matches the actual cause |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verification
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all required new Vercel regression seams
- [ ] No watch-mode flags
- [ ] Feedback latency < 20s
- [ ] `nyquist_compliant: true` set in frontmatter after validation is fully wired

**Approval:** pending
