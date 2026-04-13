# Skill: ceo_daily_pipeline

## When to Use
- 需要触发一次完整日常流水线。

## Procedure
1. 优先调用 `bash orchestration/cron/commands.sh run-daily`。
2. 若 cron job 不存在，先 `bash orchestration/cron/commands.sh ensure` 后再 run。
3. 回收 Scout/CMO/Arch/Accountant 输出并生成 CEO 摘要。

## Verification
- `run-daily` 成功触发或给出明确失败原因。
- 产物链路有更新或审计输出。
- CEO 摘要包含风险与下一步动作。
