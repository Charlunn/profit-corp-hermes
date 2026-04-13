# Skill: read_ledger

## When to Use
- 需要快速查看公司 treasury 与各角色 points。
- 需要在决策前确认当前资金状态。

## Procedure
1. 读取 `assets/shared/LEDGER.json`。
2. 输出：`treasury`、`status`、`maturity_level`、各角色 points。
3. 只读，不做任何修改。

## Verification
- 输出中包含 `treasury` 数值。
- 输出中包含 `ceo/scout/cmo/arch/accountant` 的 points。
- 不产生任何文件变更。
