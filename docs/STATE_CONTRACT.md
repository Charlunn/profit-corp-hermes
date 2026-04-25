# State Contract (Profit-Corp Hermes)

本文件定义 `profit-corp-hermes` 的状态边界、写入权限、迁移流程与冲突处理规则。

## 1. State Layers

### L1 — Hard State (authoritative)
- `assets/shared/LEDGER.json`
- 管理方式：只能通过 `python3 assets/shared/manage_finance.py ...` 更新
- 不允许手工直接改分数/金库字段

### L2 — Business Artifacts
- `assets/shared/PAIN_POINTS.md`
- `assets/shared/MARKET_PLAN.md`
- `assets/shared/TECH_SPEC.md`
- `assets/shared/external_intelligence/`（含 `SOURCES.yaml`、`raw/`、`history/`、`LATEST_SUMMARY.md`）
- 管理方式：按角色责任写入，CEO 负责时序编排；外部情报采集产物由 external-intelligence collector workflow 写入，所有 profile 可读

### L3 — Governance & Learning Artifacts
- `assets/shared/CORP_CULTURE.md`
- `assets/shared/KNOWLEDGE_BASE.md`
- `assets/shared/POST_MORTEM.md`（按需）
- 管理方式：重大决策、审计结论、复盘必须记录

## 2. Write Permission Matrix

| Asset | Primary writer | Secondary writer | Read scope |
|---|---|---|---|
| `LEDGER.json` | `manage_finance.py` | none | all profiles |
| `PAIN_POINTS.md` | scout | ceo (fallback) | all profiles |
| `MARKET_PLAN.md` | cmo | ceo (fallback) | all profiles |
| `TECH_SPEC.md` | arch | ceo (fallback) | all profiles |
| `external_intelligence/` artifacts | external-intelligence collector workflow | ceo (fallback for summaries only) | all profiles |
| `CORP_CULTURE.md` | ceo/accountant | none | all profiles |
| `KNOWLEDGE_BASE.md` | ceo/accountant | role owner for domain cards | all profiles |
| `POST_MORTEM.md` | accountant | ceo | all profiles |

规则：角色不得直接覆盖他人主产物文件，除非由 CEO 明确触发 fallback。

## 3. State Transition (Daily Pipeline)

状态推进顺序：
1. Scout 产出 `PAIN_POINTS.md`
2. CMO 产出 `MARKET_PLAN.md`
3. Arch 产出 `TECH_SPEC.md`
4. 外部情报采集流程更新 `assets/shared/external_intelligence/raw/`、`history/` 与 `LATEST_SUMMARY.md`
5. CEO 决策并写 `CORP_CULTURE.md`
6. Accountant 审计并更新 ledger（通过脚本）

若任一步失败：
- 不推进到下一步
- 记录失败原因到 `CORP_CULTURE.md` 或 `POST_MORTEM.md`
- 由 CEO 决定重试或降级执行

## 4. Conflict & Concurrency Rules

1. ledger 并发保护
- `manage_finance.py` 内置锁机制；禁止绕过脚本直接写 ledger

2. 文档写入冲突
- 同一业务文档同时仅允许一个角色写入
- CEO 负责编排顺序；并行只用于不同文档
- `assets/shared/external_intelligence/` 下的 raw/history/latest-summary 由 collector workflow 串行写入，不与 ledger 写入路径混用

3. 回滚策略
- 错误写入后优先追加修正记录，不做静默覆盖
- 关键状态异常时执行审计并生成 post-mortem

## 5. Approval Gates

- `/revenue` 当 `amt >= 1000` 必须 `/confirm`
- `/bounty` 当 `amount >= 500` 必须 `/confirm`
- `/archive` 永远需要 `/confirm`
- Phase 4 起，高影响 finance / archive / fallback takeover / state transition 动作必须先生成治理事件，再由 `scripts/enforce_governed_action.py` 放行后才可执行。
- CEO fallback 接管 `PAIN_POINTS.md` / `MARKET_PLAN.md` / `TECH_SPEC.md` 时，必须使用 `fallback.takeover.*` 类型治理动作，并在事件中记录 `primary_writer`、原因与 decision package backlink。
- `LEDGER.json` 的治理放行不改变权威写路径：即使审批通过，也只能继续调用 `manage_finance.py`，不得直接写 ledger 文件。

## 6. Skill Mapping to State Rules

- `skills/common/read_ledger.md`：所有角色可读 ledger（只读）。
- `skills/ceo/ceo_revenue_with_confirm.md`：资金变更仅通过 `manage_finance.py revenue`。
- `skills/ceo/ceo_bounty_with_confirm.md`：奖励变更仅通过 `manage_finance.py bounty`。
- `skills/common/run_accountant_audit.md`：审计走脚本路径，不手改状态文件。

上述技能必须遵守本契约：读开放、写受限、审批门槛不绕过。

## 7. Verification Checklist

- `python3 -m py_compile assets/shared/manage_finance.py`
- `bash scripts/smoke_test_pipeline.sh`
- `hermes -p ceo cron list`
