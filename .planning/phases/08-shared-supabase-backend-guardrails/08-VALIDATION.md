---
phase: 08
slug: shared-supabase-backend-guardrails
status: passed
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-26
updated: 2026-04-28T01:53:15Z
verification_artifact: .planning/phases/08-shared-supabase-backend-guardrails/08-VERIFICATION.md
---

# Phase 08 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution. Reconciled against a fresh full-suite rerun on 2026-04-28.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` (stdlib) |
| **Config file** | none — direct `python -m unittest` invocation |
| **Quick run command** | `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_check_template_conformance` |
| **Full suite command** | `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_template_registry tests.test_template_contract tests.test_instantiate_template_project tests.test_check_template_conformance -v` |
| **Latest rerun** | `2026-04-28T01:53:15Z` |
| **Latest outcome** | `24 tests in 6.667s — OK` |
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
| 08-01-01 | 01 | 1 | BACK-01 / BACK-04 / BACK-05 | T-08-01 / T-08-02 | Contract and registry explicitly define single shared Supabase, shared-table boundary, and shared flow reuse rules | unit | `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_template_registry tests.test_template_contract` | ✅ | ✅ green |
| 08-01-02 | 01 | 1 | BACK-01 / BACK-04 / BACK-05 | T-08-03 / T-08-04 | Instantiated workspaces contain `.hermes/shared-backend-guardrails.json` aligned with project metadata and contract | integration | `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_instantiate_template_project` | ✅ | ✅ green |
| 08-02-01 | 02 | 2 | BACK-01 / BACK-02 / BACK-03 / BACK-04 / BACK-05 / BACK-06 | T-08-05 / T-08-06 / T-08-07 / T-08-08 | Shared-backend conformance gate blocks SQL naming, boundary drift, protected helper drift, and client-side shared writes | integration | `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_check_template_conformance` | ✅ | ✅ green |
| 08-02-02 | 02 | 2 | BACK-01 / BACK-02 / BACK-03 / BACK-04 / BACK-05 / BACK-06 | T-08-05 / T-08-06 / T-08-07 / T-08-08 | Unified gate remains compatible with existing Phase 7 registry/contract/instantiate/conformance workflow | regression | `cd /c/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests.test_template_registry tests.test_template_contract tests.test_instantiate_template_project tests.test_check_template_conformance` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [x] `tests/test_check_template_conformance.py` — add healthy prefixed-table pass fixture for BACK-02
- [x] `tests/test_check_template_conformance.py` — add unprefixed-table fail fixture for BACK-03
- [x] `tests/test_check_template_conformance.py` — add forbidden extra-shared-table fail fixture for BACK-04
- [x] `tests/test_check_template_conformance.py` — add client-side shared-write fail fixture for BACK-06
- [x] `tests/test_check_template_conformance.py` — add protected helper drift coverage for `src/lib/entitlement.ts`, `src/lib/supabase-browser.ts`, `src/lib/supabase-server.ts`, and `src/lib/paypal.ts`

Wave 0 coverage is now fully satisfied by the existing regression suite and the 2026-04-28 rerun outcome recorded above.

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
- [x] Fresh full-suite rerun completed and matched the documented closure state
- [x] Formal verification artifact created at `.planning/phases/08-shared-supabase-backend-guardrails/08-VERIFICATION.md`

**Approval:** approved — full rerun passed on 2026-04-28 and Phase 8 closure state is now formally verified.
