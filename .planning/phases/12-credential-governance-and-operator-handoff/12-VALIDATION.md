---
phase: 12
slug: credential-governance-and-operator-handoff
status: draft
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-27
---

# Phase 12 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` |
| **Config file** | none — repo uses script/test entrypoints directly |
| **Quick run command** | `python -m unittest tests.test_approved_delivery_pipeline_cli tests.test_project_delivery_pipeline_bootstrap` |
| **Full suite command** | `python -m unittest tests.test_approved_delivery_pipeline_cli tests.test_project_delivery_pipeline_bootstrap tests.test_template_contract tests.test_check_template_conformance` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m unittest tests.test_approved_delivery_pipeline_cli tests.test_project_delivery_pipeline_bootstrap`
- **After every plan wave:** Run `python -m unittest tests.test_approved_delivery_pipeline_cli tests.test_project_delivery_pipeline_bootstrap tests.test_template_contract tests.test_check_template_conformance`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 12-01-01 | 01 | 1 | GOV-01, GOV-02 | T-12-01 | Credential-bearing actions run only through constrained authority wrappers with explicit allowlist behavior | unit/integration | `python -m unittest tests.test_approved_delivery_pipeline_cli` | ✅ | ⬜ pending |
| 12-01-02 | 01 | 1 | GOV-03 | T-12-02 | Repository, sync, env, and deploy actions emit durable audit artifacts and append linked authority events | unit/integration | `python -m unittest tests.test_project_delivery_pipeline_bootstrap` | ✅ | ⬜ pending |
| 12-02-01 | 02 | 2 | GOV-04, GOV-05 | T-12-03 | Protected platform changes are classified deterministically and block until governed justification exists | unit/integration | `python -m unittest tests.test_project_delivery_pipeline_bootstrap` | ✅ | ⬜ pending |
| 12-03-01 | 03 | 3 | GOV-06 | T-12-04 | Final operator review artifact surfaces blocked, failed, approval, and handoff states with evidence links | unit/integration | `python -m unittest tests.test_approved_delivery_pipeline_cli tests.test_project_delivery_pipeline_bootstrap` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

Existing infrastructure covers all phase requirements.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Missing `gh` / GitHub auth blocked-state clarity | GOV-01, GOV-02, GOV-03 | Depends on local CLI/auth environment | Trigger the GitHub preparation path without `gh` or auth, then confirm blocked evidence and operator review output reference the failure cleanly |
| Missing `VERCEL_TOKEN` / linkage prerequisite clarity | GOV-01, GOV-02, GOV-03, GOV-06 | Depends on local Vercel environment | Trigger Vercel linkage/deploy path without required token or linkage prerequisites, then confirm blocked evidence and operator review output surface the failure |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 30s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** approved 2026-04-27
