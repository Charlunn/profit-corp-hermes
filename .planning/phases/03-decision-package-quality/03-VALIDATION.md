---
phase: 03
slug: decision-package-quality
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-04-25
---

# Phase 03 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Bash smoke test + Python `py_compile` syntax checks |
| **Config file** | none — 以 `scripts/smoke_test_pipeline.sh` 为主验证入口 |
| **Quick run command** | `bash scripts/smoke_test_pipeline.sh` |
| **Full suite command** | `bash scripts/smoke_test_pipeline.sh` |
| **Estimated runtime** | ~30 seconds |

---

## Sampling Rate

- **After every task commit:** Run `bash scripts/smoke_test_pipeline.sh`
- **After every plan wave:** Run `bash scripts/smoke_test_pipeline.sh`
- **Before `/gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 30 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 03-01-01 | 01 | 1 | DECI-01 | T-03-01 | 主决策包只读取 shortlist + role artifacts + CEO ranking，不直接伪造证据来源 | smoke | `python3 scripts/generate_decision_package.py --dry-run` | ❌ W0 | ⬜ pending |
| 03-01-02 | 01 | 1 | DECI-02 | T-03-02 | 执行包只从主决策包派生，不回读 raw signals | smoke | `python3 scripts/derive_execution_package.py --dry-run` | ❌ W0 | ⬜ pending |
| 03-01-03 | 01 | 1 | DECI-03 | T-03-03 | board briefing 只从主决策包压缩生成，不产生独立分析结论 | smoke | `python3 scripts/derive_board_briefing.py --dry-run` | ❌ W0 | ⬜ pending |
| 03-02-01 | 02 | 2 | DECI-01 | T-03-04 | 每条关键 judgment 含简证据摘要与可追溯 backlink | smoke | `bash scripts/smoke_test_pipeline.sh` | ✅ | ⬜ pending |
| 03-03-01 | 03 | 3 | DECI-01, DECI-02, DECI-03 | T-03-05 | daily loop 生成三类 latest 产物与 history snapshots | smoke | `bash scripts/smoke_test_pipeline.sh` | ✅ | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `scripts/generate_decision_package.py` — stubs for DECI-01
- [ ] `scripts/derive_execution_package.py` — stubs for DECI-02
- [ ] `scripts/derive_board_briefing.py` — stubs for DECI-03
- [ ] `scripts/smoke_test_pipeline.sh` — extend existence/dry-run checks for three package types
- [ ] `orchestration/cron/daily_pipeline.prompt.md` — add decision package layer generation step
- [ ] `assets/shared/trace/` — optional backlink sidecar directory if chosen during implementation

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| 主决策包是否符合“先拍板、后证据”的 founder 阅读路径 | DECI-01 | 文案层级与阅读节奏难以仅靠自动命令判断 | 读取最新 `OPERATING_DECISION_PACKAGE.md`，确认开头是“一句话结论 + Top 3 排序”，后续再展开风险/机会/next actions 与证据 |
| board briefing 是否足够极简且未丢失核心风险 | DECI-03 | 摘要压缩质量需要人工判断 | 读取最新 `BOARD_BRIEFING.md`，确认仅保留结论、关键数字/信号、主要风险、需关注事项 |

---

## Validation Sign-Off

- [ ] All tasks have `<automated>` verify or Wave 0 dependencies
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all MISSING references
- [ ] No watch-mode flags
- [ ] Feedback latency < 30s
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
