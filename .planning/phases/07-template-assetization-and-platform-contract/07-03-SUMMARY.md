---
phase: 07-template-assetization-and-platform-contract
plan: 03
subsystem: infra
tags: [template-conformance, protected-manifest, workspace-validation, unittest]
requires:
  - phase: 07-template-assetization-and-platform-contract
    provides: governed template registry metadata and canonical contract
  - phase: 07-template-assetization-and-platform-contract
    provides: Hermes-managed template instantiation workflow and workspace metadata
provides:
  - blocking conformance CLI for generated template workspaces
  - protected manifest sha256 drift detection against the registered template source
  - integration coverage for healthy pass, identity failure, missing protected path, and fingerprint drift
affects: [phase-07, phase-09, phase-10]
tech-stack:
  added: []
  patterns: [stdlib python cli, registry-backed conformance gate, temp-workspace integration tests]
key-files:
  created:
    - scripts/check_template_conformance.py
    - tests/test_check_template_conformance.py
  modified: []
decisions:
  - "Use a small explicit protected manifest in code and compare workspace files to the registered template source with sha256 to block protected-layer drift."
  - "Render one operator-readable conformance report with status, blocking violations, verified paths, and fingerprint checks so later delivery phases can fail fast without extra parsing ambiguity."
metrics:
  duration: 27min
  completed_date: 2026-04-26
---

# Phase 7 Plan 03: Template Conformance Gate Summary

**Hermes 现在能在交接前用阻断式一致性闸门校验模板工作区，明确拦截身份缺失、受保护路径缺失和受保护层指纹漂移。**

## Performance

- **Duration:** 27 min
- **Completed:** 2026-04-26
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments

- 新增 `scripts/check_template_conformance.py`，实现基于注册表与 Hermes 平台契约的阻断式工作区一致性校验 CLI。
- 一致性校验覆盖 `.env` 身份值、`.hermes` 交接产物、关键受保护路径、`src/app/demo/page.tsx` 与 `src/lib/app-definition.ts` 共享不变量，以及受保护清单的 `sha256` 指纹比对。
- 新增 `tests/test_check_template_conformance.py`，验证健康工作区通过，以及 `APP_KEY` 缺失、`src/app/api/paypal/capture/route.ts` 缺失、`src/app/api/auth/session/route.ts` 指纹漂移三类阻断失败场景。

## Task Commits

1. **Task 1: 实现阻断式模板一致性 CLI 的 RED 测试** - `3c4aa32` (test)
2. **Task 1-2: 实现一致性闸门并补齐集成覆盖** - `dfdefaf` (feat)

## Files Created/Modified

- `/c/Users/42236/Desktop/dev/profit-corp-hermes/.claude/worktrees/agent-a75ebb42/scripts/check_template_conformance.py` - Phase 7 模板工作区阻断式一致性校验 CLI。
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/.claude/worktrees/agent-a75ebb42/tests/test_check_template_conformance.py` - 一致性闸门健康/失败场景集成测试。

## Decisions Made

- 使用代码内显式 protected manifest，并以注册模板源为基准做 `sha256` 指纹比较，而不是只做存在性检查。
- 让失败场景也输出同一份结构化报告，保证后续交接链路能直接读取 `## Blocking Violations` 与 `## Fingerprint Checks`。

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

- 无认证门槛或外部服务登录需求。
- 测试夹具需要复用受允许的 `assets/workspaces/projects` 根目录来满足既有工作区写入保护；该约束与 Phase 7 既有契约保持一致。

## Known Stubs

None.

## Threat Flags

None.

## Verification

- `python -m py_compile scripts/check_template_conformance.py`
- `python -m unittest tests.test_check_template_conformance`

## Self-Check: PASSED

- Found `/c/Users/42236/Desktop/dev/profit-corp-hermes/.claude/worktrees/agent-a75ebb42/scripts/check_template_conformance.py`
- Found `/c/Users/42236/Desktop/dev/profit-corp-hermes/.claude/worktrees/agent-a75ebb42/tests/test_check_template_conformance.py`
- Found commit `3c4aa32`
- Found commit `dfdefaf`

---
*Phase: 07-template-assetization-and-platform-contract*
*Completed: 2026-04-26*
