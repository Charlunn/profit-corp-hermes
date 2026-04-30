---
phase: 07-template-assetization-and-platform-contract
plan: 01
subsystem: infra
tags: [template-governance, contract, registry, unittest]
requires:
  - phase: 06-execution-handoff-and-team-readiness
    provides: stable downstream execution contracts and operator-readable artifacts
provides:
  - single-template registry metadata for standalone-saas-template
  - Hermes canonical platform contract for protected and safe extension layers
  - unittest coverage locking registry fields and contract structure
affects: [phase-07, phase-09, phase-10]
tech-stack:
  added: []
  patterns: [markdown-first operational contract, single-template registry artifact, unittest contract locking]
key-files:
  created:
    - assets/shared/templates/standalone-saas-template.json
    - docs/platform/standalone-saas-template-contract.md
    - tests/test_template_registry.py
    - tests/test_template_contract.py
  modified: []
key-decisions:
  - "Use one governed JSON registry record as the single source of template metadata for standalone-saas-template."
  - "Treat the Hermes contract as the operational source of truth while keeping README, ARCHITECTURE, and BUILDING_RULES as explicit upstream references."
patterns-established:
  - "Pattern 1: Lock registry invariants with direct JSON unittest assertions."
  - "Pattern 2: Express protected and safe template boundaries in a numbered operator-facing markdown contract."
requirements-completed: [TMPL-01, TMPL-02, TMPL-03]
duration: 16min
completed: 2026-04-26
---

# Phase 7 Plan 01: Template Assetization and Platform Contract Summary

**单模板注册表与权威平台契约将 standalone-saas-template 的元数据、保护层边界和安全扩展面固化为可测试的 Hermes 真相源。**

## Performance

- **Duration:** 16 min
- **Started:** 2026-04-26T09:29:36Z
- **Completed:** 2026-04-26T09:45:36Z
- **Tasks:** 2
- **Files modified:** 4

## Accomplishments
- 新增 `standalone-saas-template` 的单一治理注册表记录，固定模板来源、用途、栈版本与契约链接。
- 新增 Hermes 平台规范契约，明确上游引用层级、受保护平台层、安全扩展层和身份注入规则。
- 为注册表与契约分别补齐 `unittest` 约束，确保后续自动化读取时字段与章节不会漂移。

## Task Commits

Each task was committed atomically:

1. **Task 1: Create registry artifact and lock its schema with tests** - `aaa2ada` (test)
2. **Task 2: Write the Hermes canonical contract and lock its structure with tests** - `9c9e6e7` (test)
3. **Task 2: Write the Hermes canonical contract and lock its structure with tests** - `fbd242e` (feat)

**Plan metadata:** pending

_Note: TDD tasks may have multiple commits (test → feat → refactor)_

## Files Created/Modified
- `assets/shared/templates/standalone-saas-template.json` - Hermes 单模板注册表真相源。
- `docs/platform/standalone-saas-template-contract.md` - 平台保护层、扩展层和验证要求的权威契约。
- `tests/test_template_registry.py` - 锁定注册表字段、版本、引用和单模板范围。
- `tests/test_template_contract.py` - 锁定契约章节顺序、权威层级和验证命令文本。

## Decisions Made
- 使用 `assets/shared/templates/standalone-saas-template.json` 作为 Phase 7 当前唯一模板注册表记录，避免模板事实散落在脚本和文档中。
- 将 `docs/platform/standalone-saas-template-contract.md` 定义为下游工作流的 operational source of truth，同时显式回链 `README.md`、`ARCHITECTURE.md`、`BUILDING_RULES.md`。
- 在契约中把 auth、PayPal、entitlement、db-guards 和共享 public tables migration 归入受保护平台层，把品牌、产品页面、产品模块和 `APP_KEY_` 表归入安全扩展层。

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- `python -m unittest discover -s tests -p "test_*.py"` 会刷新现有派生产物，已在提交前按文件逐个恢复，不将无关测试副作用纳入本计划提交。

## TDD Gate Compliance
- Warning: Task 1 created a `test(07-01)` commit, but that commit also included the registry implementation artifact rather than a pure failing-test-only snapshot.
- Task 2 followed the expected `test(...)` → `feat(...)` sequence.

## Next Phase Readiness
- Phase 7 后续计划可以直接消费注册表与权威契约来实现模板实例化与一致性校验。
- 当前无认证门槛或外部服务依赖；后续主要风险在于脚本实现需要继续遵守已固化的保护层边界。

## Self-Check: PASSED
- Found `assets/shared/templates/standalone-saas-template.json`
- Found `docs/platform/standalone-saas-template-contract.md`
- Found commit `aaa2ada`
- Found commit `9c9e6e7`
- Found commit `fbd242e`

---
*Phase: 07-template-assetization-and-platform-contract*
*Completed: 2026-04-26*
