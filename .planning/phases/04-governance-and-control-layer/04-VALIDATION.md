---
phase: 04
slug: governance-and-control-layer
status: draft
nyquist_compliant: true
wave_0_complete: false
created: 2026-04-25
---

# Phase 04 — Validation Strategy

> Per-phase validation contract for governance enforcement, approval blocking, and audit-chain continuity.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Bash smoke test + Python `py_compile` + targeted CLI dry-runs |
| **Config file** | none — `scripts/smoke_test_pipeline.sh` remains the main regression gate |
| **Quick run command** | `python3 scripts/render_governance_status.py --dry-run` |
| **Full suite command** | `bash scripts/smoke_test_pipeline.sh` |
| **Estimated runtime** | ~30-60 seconds |

---

## Sampling Rate

- **After every task commit:** Run `python3 -m py_compile` on changed governance scripts and `python3 scripts/render_governance_status.py --dry-run`
- **After every plan wave:** Run `bash scripts/smoke_test_pipeline.sh`
- **Before `/gsd-verify-work`:** Full smoke suite plus one blocked-path governance check must be green
- **Max feedback latency:** 60 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 04-01-01 | 01 | 1 | GOV-01, GOV-02 | T-04-01 | Governance events require locked fields and bind to operating decision package | cli | `python3 scripts/render_governance_status.py --dry-run` | ❌ W0 | ⬜ pending |
| 04-01-02 | 01 | 1 | GOV-02 | T-04-03 | Latest governance markdown is derived from JSONL, not hand-maintained | smoke | `python3 scripts/render_governance_status.py --dry-run` | ❌ W0 | ⬜ pending |
| 04-02-01 | 02 | 2 | GOV-01 | T-04-06 | Governance request/approve/reject/override state transitions follow legal status flow | cli | `python3 scripts/request_governance_approval.py --help` | ❌ W0 | ⬜ pending |
| 04-02-02 | 02 | 2 | GOV-01 | T-04-07 | Missing or rejected approval blocks downstream action and records blocked/failed event | smoke | `bash scripts/smoke_test_pipeline.sh` | ❌ W0 | ⬜ pending |
| 04-03-01 | 03 | 3 | GOV-01, GOV-02 | T-04-10 | Actor/target combinations are checked against executable write-permission rules | smoke | `bash scripts/smoke_test_pipeline.sh` | ❌ W0 | ⬜ pending |
| 04-03-02 | 03 | 3 | GOV-01, GOV-02 | T-04-11 | Finance/fallback actions retain authoritative writer boundary and leave governance trail | smoke | `bash scripts/smoke_test_pipeline.sh` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

---

## Wave 0 Requirements

- [ ] `assets/shared/governance/governance_events.jsonl` — initial governance event stream path exists
- [ ] `assets/shared/governance/GOVERNANCE_STATUS.md` — initial latest view exists
- [ ] `scripts/governance_common.py` — schema helpers + path constants
- [ ] `scripts/render_governance_status.py` — dry-run markdown renderer
- [ ] `scripts/request_governance_approval.py` — request/approve/reject/override CLI stub
- [ ] `scripts/enforce_governed_action.py` — gate-before-mutate wrapper stub
- [ ] `scripts/smoke_test_pipeline.sh` — extended with governance checks

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Governance latest view是否真正回答“现在卡在哪、谁批了、谁拒了、谁 override 了” | GOV-01 | 可读性与 operator 决策效率难以只靠 grep 判断 | 打开 `assets/shared/governance/GOVERNANCE_STATUS.md`，确认按 Pending / Blocks / Recent Approvals / Rejections / Overrides 分组，且每项有 action_id、target、status、decision package backlink |
| 审计链是否能从决策包追到治理结果 | GOV-02 | 需要人工跨文件追读验证链路是否直观 | 随机选择一个 action_id，手动从 `GOVERNANCE_STATUS.md` → `governance_events.jsonl` → `OPERATING_DECISION_PACKAGE.md` → `decision_package_trace.json` 验证链路可读 |
| CEO override 是否保持“例外动作”语义而非普通批准 | GOV-01 | 语义清晰度与文案表达需要人工确认 | 检查 override 事件样例与 latest 视图，确认 override 有独立分组/标签和 reason |

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all missing governance entrypoints
- [x] No watch-mode flags
- [x] Feedback latency < 60s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** ready for execution review
