# Skill: orchestrator-workflow（交付版）

- 名称：delivery-orchestrator
- 版本：v0.2
- 目标：作为单一交付编排入口，基于 approved-project 输入包串联五个固定 specialist 阶段：design -> development -> testing -> git versioning -> release readiness。

## 适用场景
- 已获批准的 mini-SaaS 项目需要进入标准化交付流程
- 希望 Claude Code 在固定边界内完成设计、开发、测试、提交与发布建议

## 非适用场景
- 未获得批准的想法探索
- 需要变更共享 auth/payment/entitlement/shared-table/shared-backend 受保护平台层
- 依赖聊天记忆、临时人工改派或原始会话记录才能继续的流程

## 输入要求
- `goal`：本次目标（一句话）
- `task_type`：feature | bug | release
- `risk`：low | med | high
- `surface`：ui | api | db | infra | multi
- approved-project 固定输入包：approved brief、template contract、.hermes/shared-backend-guardrails.json、.hermes/project-metadata.json、GSD constraints

## 角色拓扑（固定）
- `delivery-orchestrator`：唯一编排角色，负责加载输入包、按顺序发起阶段、阻断跳步、回收 artifact handoff。
- `design-specialist`：产出设计阶段 artifact，并确认 scope 仅覆盖 approved brief。
- `development-specialist`：实现批准范围内的改动，并交付开发产物与证据。
- `testing-specialist`：执行验证、补充失败路径证据，并在需要时运行 conformance gate。
- `git-versioning-specialist`：整理结构化提交与回滚信息，不得绕过前序测试门禁。
- `release-readiness-specialist`：汇总最终交付 artifact、门禁快照、回滚方案与发布建议。

## 阶段顺序（固定）
1. design
2. development
3. testing
4. git versioning
5. release readiness

> 不允许从 development 跳过 testing 或 git versioning 直接进入 release readiness。

## 阶段编排与门禁
### 1) design — owner: `design-specialist`
- 输入：approved brief、template contract、shared-backend guardrails、project metadata、GSD constraints
- 产出：stage handoff artifact
- 门禁：范围必须保持 approved-brief-only；若触及受保护平台层，触发 scope reopen

### 2) development — owner: `development-specialist`
- 输入：design 阶段 handoff artifact
- 产出：实现变更 + stage handoff artifact
- 门禁：只能修改批准范围内的产品表面；不得擅自扩展作用域

### 3) testing — owner: `testing-specialist`
- 输入：development 阶段 handoff artifact
- 产出：测试证据 + stage handoff artifact
- 门禁：主路径、失败路径、必要 conformance gate 全部通过后才能继续

### 4) git versioning — owner: `git-versioning-specialist`
- 输入：testing 阶段 handoff artifact
- 产出：结构化提交记录、回滚说明、stage handoff artifact
- 门禁：仅在测试已通过时执行提交准备

### 5) release readiness — owner: `release-readiness-specialist`
- 输入：git versioning 阶段 handoff artifact
- 产出：final delivery artifact
- 门禁：需要完整 gate snapshot、rollback plan、release recommendation

## 统一交接格式（artifact-first handoff）
每阶段结束必须输出可复用 artifact，而不是依赖聊天记忆：
- `run_id`:
- `role`:
- `stage`:
- `scope_status`:
- `summary`:
- `outputs_produced`:
- `evidence_links`:
- `gate_decision`: PASS | FAIL
- `open_risks`:
- `next_stage`:

## 失败处理
- 任一阶段 FAIL：停止进入下一阶段，回到当前阶段补齐缺口
- 若发现超出 approved brief 或触及受保护平台层：立即阻断并请求 scope reopen
- 不得引入第二套 safety system；复用现有 conformance 与 governance 机制

## 输出契约
- 单一 delivery-orchestrator 驱动的五阶段交付记录
- 每阶段 artifact handoff
- 最终 operator-facing final delivery artifact

## DoD
- [ ] 仅存在一个 `delivery-orchestrator`
- [ ] 五个 specialist 阶段均按固定顺序执行
- [ ] 所有交接均基于 artifact，而非聊天上下文
- [ ] 固定输入包在开始前已加载

## 风险与回滚
- 风险：跳步、作用域漂移、受保护平台层被误改
- 回滚：阻断当前阶段，保留 artifact 证据，必要时发起 scope reopen 或按提交记录回退
