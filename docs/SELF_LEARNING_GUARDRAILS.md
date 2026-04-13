# Self-learning Guardrails (Memory + Skills)

本文件定义 Hermes 自学习的允许范围、质量门槛与回滚策略，避免知识漂移。

## 1. Allowed Auto-learning

允许自动沉淀的内容：
1. 可复用流程（至少成功复现 2 次）
2. 长期有效偏好与约束（语言、输出风格、风险偏好）
3. 明确可验证的经验（失败原因 + 修复路径）

## 2. Disallowed Auto-learning

禁止自动沉淀：
1. 一次性任务细节和临时路径
2. 未验证假设、情绪化结论
3. 敏感信息（token、密码、私钥、个人隐私）
4. 与当前项目无关的大段背景噪音

## 3. Skill Quality Bar

自动创建/更新 skill 时必须包含：
- `When to Use`
- `Procedure`
- `Verification`

建议结构：
- 前置条件
- 失败分支与恢复分支
- 成功判据（可执行命令或可观察产物）

## 4. Memory Quality Bar

memory 条目必须：
- 简短（单条 1-3 句）
- 可复用（对后续决策有稳定价值）
- 可验证（最好附文件/命令上下文）

## 5. Change Governance

1. Skill 更新优先 `patch`，少用全量覆盖
2. 关键 skill（影响 cron / ledger / approvals）建议人工复核
3. 如新策略导致回归失败，回退到最近稳定版本并记录复盘

## 6. Alignment with Profiles

- `ceo/scout/cmo/arch/accountant` 的 AGENTS 自学习段必须遵循本护栏
- 若与 `STATE_CONTRACT.md` 冲突，以状态契约优先
