# 术语表（v0.2）

## Skill
围绕单一工程目标的可复用执行规范，包含输入、步骤、输出契约和 DoD。

## Output Contract
技能执行后必须产出的标准化结构，确保不同 AI 结果可比、可接力。

## DoD（Definition of Done）
完成定义。满足 DoD 才可进入合并或发布流程。

## Hard Gate（硬门禁）
必须通过的检查项，任一失败即不能合并/发布。

## Soft Gate（软门禁）
建议通过的质量项，不阻断但需要在 PR 中说明。

## Routing
根据任务标签将请求映射到 1~3 个 skill 的过程。

## Thin Load（薄加载）
仅加载 skill 的目标、输入、输出和 DoD 摘要，优先低成本执行。

## Thick Load（厚加载）
在高风险或复杂任务下加载完整 skill 细则。

## Global Checklist
与 skill 无关、每次都执行的全局兜底检查，防止遗漏关键工程风险。

## Small Diff
最小可合并改动，控制影响面并降低回归风险。

## Runbook
面向维护者的故障排查说明，强调“先看什么、再看什么、如何止血/回滚”。
