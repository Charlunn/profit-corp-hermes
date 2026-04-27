---
phase: 12-credential-governance-and-operator-handoff
plan: 01
subsystem: infra
tags: [github, vercel, governance, audit, python, delivery-pipeline]
requires:
  - phase: 10-approved-project-delivery-pipeline
    provides: approved delivery authority record, append-only event stream, pipeline bootstrap flow
  - phase: 11-github-and-vercel-automation
    provides: GitHub/Vercel helper contracts and delivery-stage automation
offers:
  - governed credential wrapper surface for approved delivery actions
  - durable per-action audit artifacts linked to authority events
  - authority-enforced allowlist for GitHub and Vercel credential usage
provides:
  - governed credential wrapper surface for approved delivery actions
  - durable per-action audit artifacts linked to authority events
  - authority-enforced allowlist for GitHub and Vercel credential usage
affects: [approved-delivery, github-automation, vercel-automation, operator-handoff]
tech-stack:
  added: []
  patterns: [closed action allowlist, authority-side audit persistence, append-only event linkage]
key-files:
  created: [scripts/approved_delivery_governance.py, tests/test_phase12_credential_governance.py]
  modified: [scripts/append_approved_delivery_event.py, scripts/start_approved_project_delivery.py]
key-decisions:
  - "将 GitHub/Vercel 凭证行为收口到 authority 层的单一 allowlist 包装器，而不是继续让 pipeline 直接调用 helper。"
  - "成功、阻塞、失败三类结果统一写入审计 JSON，并通过既有 approved-delivery event stream 建立可追溯关联。"
patterns-established:
  - "Governed credential wrapper: authority record 先校验动作，再委托 GitHub/Vercel helper。"
  - "Audit-before-return: 每次凭证动作先落审计工件和 authority event，再把结果回传 pipeline。"
requirements-completed: [GOV-01, GOV-02, GOV-03]
duration: 1h 05m
completed: 2026-04-27
---

# Phase 12 Plan 01: Credential Governance and Operator Handoff Summary

**Approved delivery authority 路径现在通过封闭 allowlist 治理 GitHub/Vercel 凭证动作，并为每次动作持久化审计工件与 append-only 事件关联。**

## Performance

- **Duration:** 1h 05m
- **Started:** 2026-04-27T15:32:00Z
- **Completed:** 2026-04-27T16:37:35Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- 新增 authority-side `approved_delivery_governance` 包装层，限制允许的 GitHub/Vercel 凭证动作集合。
- 将 `github_repository`、`github_sync`、`vercel_linkage`、`vercel_deploy` 阶段切换为受治理包装器调用，并把 audit 路径写回 pipeline 元数据。
- 让 success、blocked、failed 三类结果都产出 durable audit artifact，并通过既有 approved-delivery event stream 建立 authority 级追溯链路。

## Task Commits

Each task was committed atomically:

1. **Task 1: Create the governed credential wrapper contract and red tests** - `b1b0a5b` (test)
2. **Task 2: Implement governed wrapper execution and audit persistence in the authority pipeline** - `6a1d4da` (feat)

**Plan metadata:** Pending current summary commit

## Files Created/Modified
- `scripts/approved_delivery_governance.py` - 提供受治理的动作 allowlist、审计载荷构建、事件追加，以及 GitHub/Vercel authority wrapper surface。
- `scripts/start_approved_project_delivery.py` - 将 GitHub/Vercel 凭证阶段改为通过 governed wrapper 执行，并把审计路径/authority linkage 写回 pipeline 状态。
- `scripts/append_approved_delivery_event.py` - 扩展状态与结果枚举，允许受治理流程持久化 `success` 与 `failed` 事件结果。
- `tests/test_phase12_credential_governance.py` - 覆盖 allowlist、成功审计、阻塞审计、失败审计及 append-only linkage 契约。

## Decisions Made
- 只允许五类 approved delivery credential action 通过治理层：repository prepare、github sync、vercel project link、vercel env apply、vercel deploy。
- 审计不引入第二套日志系统，而是复用 approved delivery 现有 authority event stream，并把 machine-readable audit JSON 作为 artifact 关联进去。
- `missing_*` 与 `*_incomplete` 保持 blocked 语义，其余非成功结果归一化为 failed，以保留明确 `block_reason` 与 `evidence_path`。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] 补齐失败治理事件的状态校验**
- **Found during:** Task 2 (Implement governed wrapper execution and audit persistence in the authority pipeline)
- **Issue:** governance failure event 会写入 `status="failed"`，但 append-only validator 不接受该状态，导致失败审计链路无法持久化。
- **Fix:** 在 `scripts/append_approved_delivery_event.py` 中放宽允许集合，新增 `failed` status，并补齐 `success`/`failed` outcome 兼容。
- **Files modified:** `scripts/append_approved_delivery_event.py`
- **Verification:** `python -m unittest tests.test_phase12_credential_governance -v`；`python -m unittest tests.test_phase12_credential_governance tests.test_project_delivery_pipeline_bootstrap -v`
- **Committed in:** `6a1d4da` (part of task commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** 属于治理审计正确性修复，没有扩展范围；修复后 plan 验收链路完整可验证。

## Issues Encountered
- 失败结果最初只能写出 audit JSON，不能通过事件 validator 追加 authority event；修复状态/结果枚举后恢复完整追溯链路。
- `shipping.github` 需要持久化 `authority_record_path`，否则 governed sync 无法从 pipeline 元数据恢复 authority linkage；已在实现阶段补齐。

## User Setup Required
None - no external service configuration required.

## Known Stubs
None.

## Next Phase Readiness
- Approved delivery pipeline 已具备 authority-controlled credential boundary，可继续做 operator-facing handoff、protected change gate 或更细粒度治理审计扩展。
- GitHub/Vercel helper 仍保留原有 blocked evidence contract，因此后续阶段可以在不改 helper side effect 的前提下继续增强 authority policy。

## Self-Check: PASSED
- Found commit `b1b0a5b` for TDD RED gate.
- Found commit `6a1d4da` for TDD GREEN gate.
- Summary file created at `.planning/phases/12-credential-governance-and-operator-handoff/12-01-SUMMARY.md`.

---
*Phase: 12-credential-governance-and-operator-handoff*
*Completed: 2026-04-27*
