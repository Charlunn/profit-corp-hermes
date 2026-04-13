# Multi-Profile Coordination Contract

## Profiles
- `ceo`: 决策与调度中心（外部入口）
- `scout`: 痛点发现与线索评分
- `cmo`: 商业化与市场策略
- `arch`: 技术可行性与方案
- `accountant`: 财务与执行审计

## Coordination Principles
1. 所有跨角色任务通过 CEO 统一编排。
2. 角色只写自己的目标产物，不直接修改他人核心文档。
3. 共享事实源统一在 `assets/shared/`。
4. 任意关键结论必须引用文件或可验证数字。
5. 状态边界与写入权限以 `docs/STATE_CONTRACT.md` 为准。

## Delegation Template
```python
delegate_task(
  goal="<clear target>",
  context="<input files + expected output files + acceptance criteria>",
  toolsets=["terminal", "file", "web"],
  max_iterations=50
)
```

并行模板：
```python
delegate_task(tasks=[
  {"goal": "...", "context": "...", "toolsets": ["web", "file"]},
  {"goal": "...", "context": "...", "toolsets": ["terminal", "file"]}
])
```

## Shared Read / Restricted Write
- 所有角色可读取共享状态（含 `assets/shared/LEDGER.json` 与公告板）。
- 资金与积分写入仅允许通过 `assets/shared/manage_finance.py` 执行。
- 任何角色不得手工直接编辑 ledger 关键字段。

## Artifact Ownership
- Scout -> `assets/shared/PAIN_POINTS.md`
- CMO -> `assets/shared/MARKET_PLAN.md`
- Arch -> `assets/shared/TECH_SPEC.md`
- CEO -> 决策记录写入 `assets/shared/CORP_CULTURE.md`
- Accountant -> 审计输出 + `manage_finance.py` 执行结果

## Concurrency Safety
- `assets/shared/manage_finance.py` 已包含文件锁。
- 避免多个角色并发写同一业务文档；由 CEO 控制写入时序。
