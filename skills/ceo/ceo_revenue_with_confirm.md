# Skill: ceo_revenue_with_confirm

## When to Use
- 需要登记收入并更新资金状态。

## Procedure
1. 解析参数：`<amt> <src> <note>`。
2. 若 `amt >= 1000`，必须等待 `/confirm` 后执行。
3. 执行：`python assets/shared/manage_finance.py revenue <amt> <src> "<note>"`（或 `python3`）。
4. 返回更新后的 treasury 与关键变化。

## Verification
- 高额度路径必须出现确认步骤。
- 命令执行后 `LEDGER.json` 的 treasury 变化与金额一致。
- 未出现手工编辑 ledger 的行为。
