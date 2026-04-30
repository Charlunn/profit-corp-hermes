---
phase: 08-shared-supabase-backend-guardrails
plan: 01
subsystem: infra
tags: [shared-supabase, template-contract, workspace-bootstrap, guardrails, unittest]
requires:
  - phase: 07-template-assetization-and-platform-contract
    provides: single-template registry metadata and canonical contract
  - phase: 07-template-assetization-and-platform-contract
    provides: Hermes-managed template instantiation workflow and workspace metadata
provides:
  - shared-backend governance fields in the template registry
  - canonical contract rules for single shared Supabase and APP_KEY_ table boundaries
  - instantiated workspace guardrail metadata in `.hermes/shared-backend-guardrails.json`
affects: [phase-08, phase-09, phase-10]
tech-stack:
  added: []
  patterns: [registry-backed shared-backend authority, hermes guardrail metadata handoff, contract-first platform governance]
key-files:
  created: []
  modified:
    - assets/shared/templates/standalone-saas-template.json
    - docs/platform/standalone-saas-template-contract.md
    - scripts/instantiate_template_project.py
    - tests/test_template_registry.py
    - tests/test_template_contract.py
    - tests/test_instantiate_template_project.py
key-decisions:
  - "Keep shared-backend governance inside the existing registry, contract, and instantiate flow instead of creating a parallel authority artifact."
  - "Persist shared-backend guardrails into `.hermes/shared-backend-guardrails.json` so later validators consume machine-readable workspace truth instead of documentation only."
patterns-established:
  - "Pattern 1: Registry and contract both declare shared Supabase boundaries, protected paths, and APP_KEY_ naming rules."
  - "Pattern 2: Workspace bootstrap emits both project metadata and shared-backend guardrail metadata under `.hermes/` for downstream checks."
requirements-completed: [BACK-01, BACK-04, BACK-05]
duration: 0min
completed: 2026-04-27
---

# Phase 8 Plan 01: Shared Backend Authority Summary

**Hermes 现在把单一共享 Supabase、共享表边界和受保护流程复用规则固化为注册表、平台契约与工作区 `.hermes` 护栏元数据。**

## Performance

- **Duration:** session-completion
- **Started:** 2026-04-26T15:36:00Z
- **Completed:** 2026-04-27T00:00:00Z
- **Tasks:** 2
- **Files modified:** 6

## Accomplishments
- 在 `assets/shared/templates/standalone-saas-template.json` 中加入 `shared_backend` 治理字段，声明 `shared-supabase` 模型、共享表集合、受保护路径与客户端禁写共享表集合。
- 在 `docs/platform/standalone-saas-template-contract.md` 中把单一共享 Supabase、`APP_KEY_` 业务表约束、共享表边界和客户端禁写规则写成可测试权威契约。
- 在 `scripts/instantiate_template_project.py` 中新增 `.hermes/shared-backend-guardrails.json` 写入与 dry-run 摘要输出，并补齐对应测试覆盖。

## Task Commits

No commits were created in this execution run.

## Files Created/Modified
- `assets/shared/templates/standalone-saas-template.json` - 新增共享后端治理真相源字段。
- `docs/platform/standalone-saas-template-contract.md` - 扩展单一共享 Supabase、共享表边界和客户端禁写规则的权威契约。
- `scripts/instantiate_template_project.py` - 在实例化阶段写入 `.hermes/shared-backend-guardrails.json`，并在 dry-run 输出共享后端摘要。
- `tests/test_template_registry.py` - 锁定共享后端注册表字段。
- `tests/test_template_contract.py` - 锁定共享 Supabase 契约文本与验证命令。
- `tests/test_instantiate_template_project.py` - 验证 guardrails 文件生成、字段对齐和 dry-run 摘要。

## Decisions Made
- 继续复用 Phase 7 的 registry/contract/bootstrap 结构，不为 shared backend 再造第二套 authority 文档或脚本入口。
- 让实例化产物在 `.hermes` 下同时携带 `project-metadata.json` 和 `shared-backend-guardrails.json`，确保后续 conformance gate 有稳定输入。

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- 无需外部认证或额外依赖安装。
- 阶段执行过程中未创建原子提交，因此本总结只记录代码与测试结果，不记录 commit hash。

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- 共享后端 authority inputs 已齐备，Phase 8 Plan 02 可直接消费 `.hermes/shared-backend-guardrails.json`、注册表与权威契约执行阻断式校验。
- 生成工作区现在具备 machine-readable shared-backend guardrails，后续验证无需猜测默认后端模式。

---
*Phase: 08-shared-supabase-backend-guardrails*
*Completed: 2026-04-27*
