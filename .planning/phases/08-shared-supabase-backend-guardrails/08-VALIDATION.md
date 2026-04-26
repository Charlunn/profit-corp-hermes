---
phase: 08
slug: shared-supabase-backend-guardrails
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-26
---

# Phase 08 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` (stdlib) |
| **Config file** | none — direct `python -m unittest` invocation |
| **Quick run command** | `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_check_template_conformance` |
| **Full suite command** | `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_template_registry tests.test_template_contract tests.test_instantiate_template_project tests.test_check_template_conformance` |
| **Estimated runtime** | ~6 seconds |

---

## Sampling Rate

- **After every task commit:** Run `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_check_template_conformance`
- **After every plan wave:** Run `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_template_registry tests.test_template_contract tests.test_instantiate_template_project tests.test_check_template_conformance`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 10 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 08-01-01 | 01 | 1 | BACK-01 / BACK-04 / BACK-05 | T-08-01 / T-08-02 | Contract and registry explicitly define single shared Supabase, shared-table boundary, and shared flow reuse rules | unit | `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_template_registry tests.test_template_contract` | ✅ | ⬜ pending |
| 08-01-02 | 01 | 1 | BACK-01 / BACK-04 / BACK-05 | T-08-03 / T-08-04 | Instantiated workspaces contain `.hermes/shared-backend-guardrails.json` aligned with project metadata and contract | integration | `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_instantiate_template_project` | ✅ | ⬜ pending |
| 08-02-01 | 02 | 2 | BACK-01 / BACK-02 / BACK-03 / BACK-04 / BACK-05 / BACK-06 | T-08-05 / T-08-06 / T-08-07 / T-08-08 | Shared-backend conformance gate blocks SQL naming, boundary drift, protected helper drift, and client-side shared writes | integration | `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_check_template_conformance` | ✅ | ⬜ pending |
| 08-02-02 | 02 | 2 | BACK-01 / BACK-02 / BACK-03 / BACK-04 / BACK-05 / BACK-06 | T-08-05 / T-08-06 / T-08-07 / T-08-08 | Unified gate remains compatible with existing Phase 7 registry/contract/instantiate/conformance workflow | regression | `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_template_registry tests.test_template_contract tests.test_instantiate_template_project tests.test_check_template_conformance` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_check_template_conformance.py` — add healthy prefixed-table pass fixture for BACK-02
- [ ] `tests/test_check_template_conformance.py` — add unprefixed-table fail fixture for BACK-03
- [ ] `tests/test_check_template_conformance.py` — add forbidden extra-shared-table fail fixture for BACK-04
- [ ] `tests/test_check_template_conformance.py` — add client-side shared-write fail fixture for BACK-06
- [ ] `tests/test_check_template_conformance.py` — add protected helper drift coverage for `src/lib/entitlement.ts`, `src/lib/supabase-browser.ts`, `src/lib/supabase-server.ts`, and `src/lib/paypal.ts`

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all MISSING references
- [x] No watch-mode flags
- [x] Feedback latency < 10s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
