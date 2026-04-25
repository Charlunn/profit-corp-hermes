---
phase: 5
slug: operating-visibility-surface
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-25
---

# Phase 5 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Python `unittest` with script-level subprocess tests |
| **Config file** | none — current tests run directly via Python test modules |
| **Quick run command** | `python -m unittest tests.test_generate_operating_visibility -v` |
| **Full suite command** | `bash scripts/smoke_test_pipeline.sh` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python -m unittest tests.test_generate_operating_visibility -v`
- **After every plan wave:** Run `bash scripts/smoke_test_pipeline.sh`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 05-01-01 | 01 | 1 | VIZ-01 | T-05-01 / — | Visibility artifact preserves source hierarchy and renders current situation, risks, opportunities, and next steps from trusted artifacts only | unit | `python -m unittest tests.test_generate_operating_visibility -v` | ❌ W0 | ⬜ pending |
| 05-01-02 | 01 | 1 | VIZ-01 | T-05-02 / — | Status overlay promotes blocked, pending, failed, or stale conditions without rewriting the operating anchor | unit | `python -m unittest tests.test_generate_operating_visibility -v` | ❌ W0 | ⬜ pending |
| 05-02-01 | 02 | 2 | VIZ-01 | T-05-03 / — | Daily workflow produces non-empty `assets/shared/visibility/OPERATING_VISIBILITY.md` with exactly 3 or fewer evidence-backed actions | smoke | `bash scripts/smoke_test_pipeline.sh` | ⚠️ Needs update | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `tests/test_generate_operating_visibility.py` — stubs for VIZ-01 rendering, source hierarchy, exception promotion, and Top 3 action cap
- [ ] `scripts/generate_operating_visibility.py` — generator entrypoint under test
- [ ] `scripts/smoke_test_pipeline.sh` — add visibility artifact presence check and generator coverage

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Operator can scan the latest visibility artifact quickly without reading every source artifact in full | VIZ-01 | “At a glance” operator usefulness is qualitative even when the artifact structure is machine-checked | Generate fresh artifacts, open `assets/shared/visibility/OPERATING_VISIBILITY.md`, confirm the first screen shows overall situation, top risks, top opportunities, and at most 3 next actions with clear backlinks |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
