# Skill: feature-planning（中立版）

- 名称：feature-planning
- 版本：v0.2
- 来源：google/eng-practices, thoughtbot/guides, microsoft engineering playbook（重写）

## 适用场景
- 需求到实施计划的标准化拆解
- 微型 SaaS 新功能、功能增强

## 非适用场景
- 紧急故障止血（应走 bugfix-safety）

## 输入要求
- 业务目标
- 验收标准
- 风险边界（时间/兼容/合规）

## 执行步骤
1. 明确范围：定义做/不做。
2. 影响评估：UI/API/DB/权限/日志。
3. 任务切片：按 small diff 拆分里程碑。
4. 验证设计：主路径 + 失败路径。
5. 交付计划：输出实施顺序与回滚点。

## 输出契约
- 变更摘要
- 影响面
- 风险点
- 验证计划
- 回滚方案

## DoD
- [ ] 验收标准逐条映射到任务与验证
- [ ] 不包含无关重构
- [ ] 风险与回滚清晰可执行

## 风险与回滚
- 风险：需求漂移、范围扩散
- 回滚：以子任务边界为回滚点，逐段回退
