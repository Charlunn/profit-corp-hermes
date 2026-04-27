# Orchestrator 输入模板（v0.2）

> 用于在流程开始前统一输入，避免需求漂移与上下文膨胀。

## 1) Basic Context
- `goal`:
- `task_type`: feature | bug | release | logging | payment/auth/migration
- `risk`: low | med | high
- `surface`: ui | api | db | infra | multi

## 2) Scope & Non-goals
- 本次范围（做什么）：
- 非目标（不做什么）：
- `scope_default`: approved-brief-only

## 3) Constraints
- 时间约束：
- 兼容性约束：
- 合规/安全约束：

## 4) Acceptance Criteria
- [ ] 验收标准 1
- [ ] 验收标准 2
- [ ] 验收标准 3

## 5) Dependencies & Assumptions
- 依赖项：
- 假设：

### Approved-project Delivery Bundle
- `approved brief path`: `.hermes/PROJECT_BRIEF_ENTRYPOINT.md`
- `template contract path`: `docs/platform/standalone-saas-template-contract.md`
- `shared-backend guardrails path`: `.hermes/shared-backend-guardrails.json`
- `project metadata path`: `.hermes/project-metadata.json`
- `gsd constraints source`: `.planning/phases/09-claude-code-delivery-team-orchestration/09-01-PLAN.md`
- required bundle fields: approved brief, template contract, .hermes/shared-backend-guardrails.json, .hermes/project-metadata.json, GSD constraints

## 6) Risk Register
- 风险项：
- 风险等级：
- 缓解策略：

## 7) Initial Routing Decision
- 命中 skill：
- 加载级别：L0 | L1 | L2
- 选择理由：
