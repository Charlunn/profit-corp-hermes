# Skill: run_accountant_audit

## When to Use
- 需要审计当前资金风险与角色分配风险。
- 执行日常流水线后需要出审计摘要。

## Procedure
1. 调用 `python assets/shared/manage_finance.py audit`（或 `python3`）。
2. 汇总 treasury、低点角色、异常项。
3. 输出风险等级与建议动作（最多 3 条）。

## Verification
- 审计命令成功执行。
- 输出包含至少 1 条可执行建议。
- 未直接手改 `LEDGER.json`。
