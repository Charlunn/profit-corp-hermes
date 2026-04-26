---
phase: 6
slug: execution-handoff-and-team-readiness
status: approved
nyquist_compliant: true
wave_0_complete: true
created: 2026-04-26
---

# Phase 6 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` |
| **Config file** | none — direct `unittest` discovery is used |
| **Quick run command** | `python -m unittest discover -s C:/Users/42236/Desktop/dev/profit-corp-hermes/tests -p test_derived_packages.py -v` |
| **Full suite command** | `python -m unittest discover -s C:/Users/42236/Desktop/dev/profit-corp-hermes/tests -p "test_*.py" -v` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m unittest discover -s C:/Users/42236/Desktop/dev/profit-corp-hermes/tests -p test_derived_packages.py -v`
- **After every plan wave:** Run `python -m unittest discover -s C:/Users/42236/Desktop/dev/profit-corp-hermes/tests -p "test_*.py" -v`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 06-01-01 | 01 | 1 | DECI-02, DECI-03 | T-06-01 / T-06-02 / T-06-03 | Contract tests fail fast if execution/board outputs drift from the locked Core 9 sections, exact metadata labels, readiness enum, single-signal board sections, or solo-first collaboration boundary. | unit | `python -m unittest discover -s C:/Users/42236/Desktop/dev/profit-corp-hermes/tests -p test_derived_packages.py -v` | ✅ | ✅ green |
| 06-01-02 | 01 | 1 | DECI-02, DECI-03 | T-06-01 / T-06-02 / T-06-03 | Contract tests also enforce execution risk-to-acceptance pairing, board one-item-per-section limits, absence of legacy headings, and latest/history write checks before generator changes land. | unit | `python -m unittest discover -s C:/Users/42236/Desktop/dev/profit-corp-hermes/tests -p test_derived_packages.py -v` | ✅ | ✅ green |
| 06-02-01 | 02 | 2 | DECI-02 | T-06-04 / T-06-05 / T-06-06 | Execution generator stays derived from the operating decision package and trace, reads governance status only for readiness, emits only `ready|blocked|needs-input`, and preserves the solo-first future-team-safe handoff contract. | unit | `python -m unittest discover -s C:/Users/42236/Desktop/dev/profit-corp-hermes/tests -p test_derived_packages.py -v` | ✅ | ✅ green |
| 06-02-02 | 02 | 2 | DECI-02 | T-06-04 / T-06-05 / T-06-06 | Latest and history execution artifacts regenerate from the script with all nine headings, top metadata block, paired acceptance gates, and no task-board drift. | unit + regeneration | `python C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/derive_execution_package.py --date 2026-04-25 && python -m unittest discover -s C:/Users/42236/Desktop/dev/profit-corp-hermes/tests -p test_derived_packages.py -v` | ✅ | ✅ green |
| 06-03-01 | 03 | 3 | DECI-03 | T-06-07 / T-06-08 / T-06-09 | Board generator stays trace-linked to the operating package, reads governance status plus `LEDGER.json` as the only overlay sources, and emits exactly one governance, risk, finance, and required-attention signal. | unit | `python -m unittest discover -s C:/Users/42236/Desktop/dev/profit-corp-hermes/tests -p test_derived_packages.py -v` | ✅ | ✅ green |
| 06-03-02 | 03 | 3 | DECI-03 | T-06-07 / T-06-08 / T-06-09 | Latest and history board artifacts regenerate through the existing script-owned path while keeping fast task-level verification within the phase latency target. | unit + regeneration | `python C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/derive_board_briefing.py --date 2026-04-25 && python -m unittest discover -s C:/Users/42236/Desktop/dev/profit-corp-hermes/tests -p test_derived_packages.py -v` | ✅ | ✅ green |
| 06-03-03 | 03 | 3 | DECI-02, DECI-03 | T-06-07 / T-06-08 / T-06-09 | Full downstream compatibility is proven by running the repo-wide unittest suite and smoke pipeline, with visibility consumer fixes limited to compatibility-only parsing/assertion updates if drift is detected. | integration + smoke | `python -m unittest discover -s C:/Users/42236/Desktop/dev/profit-corp-hermes/tests -p "test_*.py" -v && bash C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/smoke_test_pipeline.sh` | ✅ | ✅ green |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_derived_packages.py` — add exact Core 9 execution section-order assertions plus banned task-board vocabulary checks
- [ ] `tests/test_derived_packages.py` — add exact metadata-block assertions for `Owner`, `Primary Role`, `Handoff Target`, and `Readiness Status`
- [ ] `tests/test_derived_packages.py` — add readiness enum assertions limited to `ready|blocked|needs-input`
- [ ] `tests/test_derived_packages.py` — add execution `## Key Risks` ↔ `## Acceptance Gate` count/order pairing checks
- [ ] `tests/test_derived_packages.py` — add exact board-section assertions for `## Governance Signal`, `## Risk Signal`, `## Finance Signal`, and `## Required Attention`
- [ ] `tests/test_derived_packages.py` — add latest/history write-mode checks for both execution and board artifacts
- [ ] `tests/test_generate_operating_visibility.py` — extend compatibility assertions only if Phase 6 section/header changes break the supporting-view contract during verification

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Execution package reads as a concise human handoff pack instead of a task board | DECI-02 | Concision and handoff readability are partly judgment-based even after automated section checks | Read `assets/shared/execution_packages/EXECUTION_PACKAGE.md` after regeneration and confirm the top metadata block plus Core 9 sections stay within 1-3 high-value items each, remain addressed to the founder/operator, and do not introduce backlog/task-board/workflow expansion |
| Board briefing remains genuinely one-screen and executive-scannable | DECI-03 | Automated tests can check headings and signal counts, but not full scanability | Read `assets/shared/board_briefings/BOARD_BRIEFING.md` after regeneration and confirm the brief fits the intended one-screen rhythm with exactly one governance, risk, finance, and required-attention signal |
| Visibility compatibility remains intact without new readiness-surface requirements | DECI-02, DECI-03 | The compatibility-only decision is scope-sensitive and should be confirmed against real outputs | After execution and board regeneration, run the broader gate commands and inspect `assets/shared/visibility/OPERATING_VISIBILITY.md` only if tests or smoke checks indicate Phase 6 contract drift into the supporting-view path |

---

## Validation Sign-Off

- [x] All 7 plan tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers contract assertions for execution sections, metadata, readiness enum, risk/gate pairing, board signal sections, and latest/history writes
- [x] No watch-mode flags
- [x] Task-level feedback latency stays within ~30s by using `test_derived_packages.py` for per-task verification
- [x] Wave/phase gate runs full suite plus `bash C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/smoke_test_pipeline.sh`
- [x] `nyquist_compliant: true` set in frontmatter after plan/task synchronization is complete

**Approval:** approved 2026-04-26
