# Skill: ceo_bounty_with_confirm

## When to Use
- 需要发放任务奖励并记录到账本。

## Procedure
1. 解析参数：`<amount> <agent> <task>`。
2. 若 `amount >= 500`，必须等待 `/confirm`。
3. 执行：`python assets/shared/manage_finance.py bounty <amount> <agent> "<task>"`（或 `python3`）。
4. 返回 treasury 与目标角色 points 变化。

## Verification
- 高额度路径必须二次确认。
- 账本更新后 points 与 treasury 同步变化。
- 审计命令可读到本次变更。
