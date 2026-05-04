---
phase: 19
slug: specialist-evidence-and-ui-artifact-gates
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-05-04
updated: 2026-05-04
---

# Phase 19 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4.2 running unittest-style tests |
| **Config file** | none |
| **Quick run command** | `pytest tests/test_approved_delivery_pipeline_cli.py -q` |
| **Full suite command** | `pytest tests/test_approved_delivery_pipeline_cli.py -q` |
| **Estimated runtime** | ~15 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_approved_delivery_pipeline_cli.py -q`
- **After every plan wave:** Run `pytest tests/test_approved_delivery_pipeline_cli.py -q`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 20 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 19-01-01 | 01 | 1 | GATE-01 / GATE-02 | T-19-01 / T-19-03 | Specialist stages block on missing or contradictory evidence bundle data | integration | `pytest tests/test_approved_delivery_pipeline_cli.py -q` | yes | green |
| 19-01-02 | 01 | 1 | UI-01 / UI-02 / UI-03 | T-19-02 / T-19-04 | UI-scoped design/development block on missing or stale `/ui-ux-pro-max` artifact truth | integration | `pytest tests/test_approved_delivery_pipeline_cli.py -q` | yes | green |
| 19-02-01 | 02 | 2 | GATE-03 | T-19-05 / T-19-06 | Specialist stages reject template-only or unsafe inventory outcomes before pass | integration | `pytest tests/test_approved_delivery_pipeline_cli.py -q` | yes | green |
| 19-02-02 | 02 | 2 | GATE-03 | T-19-07 / T-19-08 | Machine-readable substance outcomes persist across event and authority layers | integration | `pytest tests/test_approved_delivery_pipeline_cli.py -q` | yes | green |
| 19-03-01 | 03 | 3 | GATE-02 / UI-03 | T-19-09 / T-19-12 | Specialist/UI blocks render explicit failed gate, evidence path, repair action, and resume target | integration | `pytest tests/test_approved_delivery_pipeline_cli.py -q` | yes | green |
| 19-03-02 | 03 | 3 | GATE-02 / GATE-03 | T-19-10 / T-19-11 | Recovered truth remains authoritative while historical specialist/UI blocks stay visible as context | integration | `pytest tests/test_approved_delivery_pipeline_cli.py -q` | yes | green |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [x] `tests/test_approved_delivery_pipeline_cli.py` - explicit UI artifact missing/stale coverage added
- [x] `tests/test_approved_delivery_pipeline_cli.py` - transcript strictness coverage added against the locked contract
- [x] `tests/test_approved_delivery_pipeline_cli.py` - specialist blocked-state repair-guidance coverage added

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all missing references
- [x] No watch-mode flags
- [x] Feedback latency < 20s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** complete
