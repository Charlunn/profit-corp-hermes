# START HERE（统一入口）

> 用于你自己和 AI 在每次任务开始时快速对齐，避免上下文膨胀和规范遗漏。

## 1) 先标记任务类型（必做）
从以下选择一个：
- `feature`
- `bug`
- `release`
- `logging`
- `payment/auth/migration`（高风险）

## 2) 先读哪些文档（最多 3 个）
- 全流程优先：先看 [Orchestrator Workflow](../../skills/library/normalized/orchestrator-workflow.md)
- 一屏执行：看 [Orchestrator Quick Run](quick-run/orchestrator-workflow-card.md)
- 模板快捷入口：
  - [Orchestrator 输入模板](templates/orchestrator-input-template-v0.2.md)
  - [阶段交接模板](templates/stage-handoff-template-v0.2.md)
  - [最终交付模板](templates/final-delivery-template-v0.2.md)
- 总是先读：[Engineering Playbook v0.2](standards/engineering-playbook-v0.2.md)
- 按任务读一个 skill：
  - feature -> [feature-to-pr](skills/feature-to-pr.md)
  - bug -> [bugfix-safety](skills/bugfix-safety.md)
  - logging -> [logging-convention](skills/logging-convention.md)
- 合并/发布前必读：[发布一页纸检查清单](release/release-checklist-one-page.md)

## 3) 10 秒路由
1. 打标签：`task_type` + `risk` + `surface`
2. 在 [skill-manifest-v0.2](routing/skill-manifest-v0.2.md) 选 1~3 个 skill
3. 默认 L0；高风险升级到 L1/L2

## 4) 本次必须产出物
- 变更摘要
- 影响面（UI/API/DB/权限/日志）
- 风险点
- 验证证据 + 证据链接
- 回滚方案

## 5) 合并前硬门禁（必须全通过）
- 分层依赖无违规
- lint/format/type-check 通过
- 主路径 + 失败路径验证证据齐全
- 日志结构化且可追踪
- 回滚步骤可执行

## 6) 会话结束前（控制上下文）
### 软卸载（同会话）
仅保留：阶段摘要 + 门禁状态 + 未决风险

### 硬卸载（新会话）
仅交接：`goal` / `done` / `open_risks` / `next_action` / `gates_status`

---

如果不确定怎么选：先按 `bugfix-safety` 的保守路径执行，再补充路由信息。
