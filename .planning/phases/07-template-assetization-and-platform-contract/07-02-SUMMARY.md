---
phase: 07-template-assetization-and-platform-contract
plan: 02
subsystem: infra
tags: [template-instantiation, workspace-bootstrap, identity-injection, unittest]
requires:
  - phase: 07-template-assetization-and-platform-contract
    provides: single-template registry metadata and canonical contract
provides:
  - shared template helper contract for registry loading, identity validation, and safe workspace writes
  - stdlib instantiate CLI that copies the governed template into a Hermes-managed workspace
  - integration coverage for workspace generation, identity injection, dry-run, and workspace-root safety
affects: [phase-07, phase-09, phase-10]
tech-stack:
  added: []
  patterns: [shared python helper module, registry-backed template resolution, hermes-managed workspace bootstrap]
key-files:
  created:
    - scripts/template_contract_common.py
    - scripts/instantiate_template_project.py
    - tests/test_instantiate_template_project.py
  modified: []
key-decisions:
  - "Use assets/workspaces/projects as the only allowed generated workspace root and enforce it centrally in template_contract_common.py."
  - "Inject only non-secret identity values into .env while rewriting secret-bearing runtime keys to explicit placeholders for later phases."
  - "Ignore node_modules, .next, and .git during template copy so workspace bootstrap stays deterministic and independent from upstream local install state."
patterns-established:
  - "Pattern 1: Reuse a shared helper module for registry loading, workspace path guards, and APP identity derivation across Phase 7 scripts."
  - "Pattern 2: Create Hermes handoff entrypoints inside generated workspaces via .hermes/project-metadata.json and PROJECT_BRIEF_ENTRYPOINT.md."
requirements-completed: [TMPL-04, TMPL-05]
duration: 22min
completed: 2026-04-26
---

# Phase 7 Plan 02: Template Instantiation and Identity Injection Summary

**Hermes 现可从受治理模板直接生成受控项目工作区，并把产品身份注入到 `.env`、app-definition 与 `.hermes` 交接入口中。**

## Performance

- **Duration:** 22 min
- **Started:** 2026-04-26T09:46:00Z
- **Completed:** 2026-04-26T10:08:00Z
- **Tasks:** 2
- **Files modified:** 3

## Accomplishments
- 新增 `scripts/template_contract_common.py`，集中模板注册表读取、`APP_KEY`/`APP_NAME`/`APP_URL` 校验、派生身份载荷生成，以及 `assets/workspaces/projects` 写入保护。
- 新增 `scripts/instantiate_template_project.py`，支持从注册模板复制项目、重写非密钥身份配置、生成 `.hermes/project-metadata.json` 与 `PROJECT_BRIEF_ENTRYPOINT.md`。
- 新增 `tests/test_instantiate_template_project.py`，覆盖共享辅助契约、CLI 参数、成功实例化、dry-run 无写入和越界工作区阻断行为。

## Task Commits

Each task was committed atomically:

1. **Task 1: Create shared helper contracts for registry, workspace safety, and identity injection** - `ecdb351` (test)
2. **Task 2: Implement instantiate-from-template CLI and integration tests** - `4f8cb67` (feat)

## Files Created/Modified
- `scripts/template_contract_common.py` - Phase 7 共享模板契约辅助层，提供注册表读取、身份校验、派生 identity payload 与工作区写入保护。
- `scripts/instantiate_template_project.py` - 从治理注册表解析模板、复制到 Hermes 工作区、注入身份、写入 `.hermes` 交接元数据的 CLI。
- `tests/test_instantiate_template_project.py` - 模板实例化脚本与共享辅助函数的集成/单元测试覆盖。

## Decisions Made
- 将 `assets/workspaces/projects` 固定为唯一允许的生成根目录，并通过 `ensure_allowed_workspace_path()` 在共享模块中统一执行。
- 只写入本阶段允许的非秘密身份值：`APP_KEY`、`APP_NAME`、`APP_URL`、`PAYPAL_BRAND_NAME`；其余运行时敏感值统一保留为 `__REQUIRED__` 占位。
- 复制模板时显式忽略 `node_modules`、`.next`、`.git`，避免本地上游安装产物影响实例化成功率与工作区确定性。

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking Issue] 规避上游模板本地安装产物导致的复制失败**
- **Found during:** Task 2
- **Issue:** 直接 `copytree()` 复制外部模板时，Windows 下上游 `node_modules` 深层路径导致测试工作区复制失败。
- **Fix:** 在实例化 CLI 中对 `node_modules`、`.next`、`.git` 使用 `shutil.ignore_patterns(...)`，仅复制交付所需源文件与配置。
- **Files modified:** `scripts/instantiate_template_project.py`
- **Commit:** `4f8cb67`

## Issues Encountered
- 无需认证或外部服务登录。
- 测试期间产生的临时工作区目录已在提交前清理，未纳入版本控制。

## Known Stubs
- `.env` 中的 `NEXT_PUBLIC_SUPABASE_URL`、`NEXT_PUBLIC_SUPABASE_ANON_KEY`、`SUPABASE_SERVICE_ROLE_KEY`、`NEXT_PUBLIC_PAYPAL_CLIENT_ID`、`PAYPAL_CLIENT_SECRET` 仍为 `__REQUIRED__` 占位；这是 Phase 7 预期行为，用于避免在模板实例化阶段注入秘密值。

## Next Phase Readiness
- Phase 7 后续 conformance 脚本可直接复用 `template_contract_common.py` 的注册表与身份校验辅助函数。
- 生成工作区已具备 `.hermes` 元数据与项目 brief 入口，可供后续交接与自动化链路消费。

## Self-Check: PASSED
- Found `scripts/template_contract_common.py`
- Found `scripts/instantiate_template_project.py`
- Found `tests/test_instantiate_template_project.py`
- Found commit `ecdb351`
- Found commit `4f8cb67`

---
*Phase: 07-template-assetization-and-platform-contract*
*Completed: 2026-04-26*
