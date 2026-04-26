---
phase: 08-shared-supabase-backend-guardrails
plan: 02
subsystem: infra
tags: [shared-supabase, conformance-gate, sql-boundary, fingerprint-drift, unittest]
requires:
  - phase: 08-shared-supabase-backend-guardrails
    provides: shared-backend registry fields, canonical contract rules, and `.hermes/shared-backend-guardrails.json`
  - phase: 07-template-assetization-and-platform-contract
    provides: blocking conformance CLI and integration-test fixture pattern
provides:
  - unified shared-backend conformance checks inside `check_template_conformance.py`
  - protected helper fingerprint drift detection for auth/paypal/entitlement/supabase layers
  - SQL boundary and client-side shared-write blocking coverage
affects: [phase-08, phase-09, phase-10]
tech-stack:
  added: []
  patterns: [single gate enforcement, temp-workspace mutation fixtures, static shared-table boundary scanning]
key-files:
  created: []
  modified:
    - scripts/check_template_conformance.py
    - tests/test_check_template_conformance.py
key-decisions:
  - "Extend the existing conformance gate instead of creating a second shared-backend validator CLI."
  - "Use deterministic migration and client-file scans plus fingerprint checks to block boundary drift without adding new parser dependencies."
patterns-established:
  - "Pattern 1: Shared backend policy violations surface through the same `## Status / ## Blocking Violations / ## Verified Paths / ## Fingerprint Checks` report contract."
  - "Pattern 2: Temp workspace tests prove each guardrail by mutating exactly one SQL file or client file and asserting a blocking failure."
requirements-completed: [BACK-01, BACK-02, BACK-03, BACK-04, BACK-05, BACK-06]
duration: 0min
completed: 2026-04-27
---

# Phase 8 Plan 02: Shared Backend Conformance Gate Summary

**Hermes 现在可用同一个 conformance gate 自动阻断共享后端漂移、未加 APP_KEY_ 前缀的业务表、伪装共享表，以及客户端直接写共享状态。**

## Performance

- **Duration:** session-completion
- **Started:** 2026-04-26T15:36:00Z
- **Completed:** 2026-04-27T00:00:00Z
- **Tasks:** 3
- **Files modified:** 2

## Accomplishments
- 扩展 `scripts/check_template_conformance.py`，新增 shared-backend artifact 检查、受保护 helper 指纹校验、SQL `create table` 边界检查，以及 `"use client"` 文件共享表 mutation 阻断。
- 扩展 `tests/test_check_template_conformance.py`，覆盖健康工作区通过、缺失 guardrails 文件失败、未加前缀业务表失败、额外共享表失败、protected helper drift 失败，以及客户端写 `payments/subscriptions` 失败。
- 保持 Phase 7 已建立的统一报告结构与单 CLI 入口，并确认 registry/contract/instantiate/conformance 回归套件全绿。

## Task Commits

No commits were created in this execution run.

## Files Created/Modified
- `scripts/check_template_conformance.py` - 统一模板一致性与共享 Supabase 护栏阻断逻辑。
- `tests/test_check_template_conformance.py` - 新增 BACK-01..BACK-06 通过/失败集成覆盖与回归断言。

## Decisions Made
- 把 shared-backend 校验直接并入现有 conformance gate，保证后续交付链只认一个阻断入口。
- 用 stdlib 级别文本/路径扫描解决 SQL 命名边界和 client-side shared write 检测，避免引入 AST 或 SQL parser 依赖。

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- 先做 RED 测试后，暴露了 guardrails 元数据缺失与 unified gate 覆盖不足的问题；随后在现有实例化与 conformance 流程内补齐实现并回归验证。
- 报告结构被严格保持为四段顺序，避免新增 shared-backend 校验后破坏下游消费者。

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Phase 8 的共享后端 authority + enforcement 已闭环，后续阶段可直接依赖统一 gate 做交付前阻断。
- 当前代码状态已经具备可提交条件；若需要，还可继续把 planning validation/state 做更细粒度同步。

## Verification
- `python -m unittest tests.test_template_registry tests.test_template_contract tests.test_instantiate_template_project tests.test_check_template_conformance`

---
*Phase: 08-shared-supabase-backend-guardrails*
*Completed: 2026-04-27*
