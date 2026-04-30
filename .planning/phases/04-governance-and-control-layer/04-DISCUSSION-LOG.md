# Phase 4: Governance and Control Layer - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-25
**Phase:** 04-Governance and Control Layer
**Areas discussed:** 审计落账, 状态推进, 写权限

---

## 审计落账

| Option | Description | Selected |
|--------|-------------|----------|
| 独立治理日志 | 单独新增治理事件日志作为权威审计轨，专门记录 approval / rejection / override / transition；`LEDGER.json` 继续只管资金状态。 | ✓ |
| 并入现有审计 | 把审批和状态推进也塞进 `LEDGER.json` 或现有财务审计轨里。 | |
| 分散写入 | 不建统一日志，只把审批结果散落写进各 markdown 产物。 | |

**User's choice:** 独立治理日志
**Notes:** 用户明确希望治理事件和财务状态分层，不要把 Phase 4 的审计轨耦合进 ledger。

| Option | Description | Selected |
|--------|-------------|----------|
| JSONL 事件流 | 每条事件一行，适合后续自动校验和时间追踪。 | ✓ |
| Markdown 审计册 | 人类更易读，但结构化校验较弱。 | |
| CSV 事件表 | 可延续 CSV 风格，但嵌套上下文表达差。 | |

**User's choice:** JSONL 事件流
**Notes:** 审计轨优先为机器可查和可校验服务。

| Option | Description | Selected |
|--------|-------------|----------|
| 完整上下文字段 | 每条事件至少带 action_id / event_type / actor / target_artifact / related_decision_package / status_before / status_after / approved_by / timestamp。 | ✓ |
| 最小字段集 | 只记 action、result、time、actor 等最小字段。 | |
| 我自定义 | 用户自定义字段集。 | |

**User's choice:** 完整上下文字段
**Notes:** 用户希望后续自动校验和审计追责不缺上下文。

| Option | Description | Selected |
|--------|-------------|----------|
| 日志+latest视图 | 结构化 JSONL 外，再保留一个给人看的 governance latest 视图。 | ✓ |
| 只写日志 | 完全依赖查询脚本读 JSONL。 | |
| 只写latest | 不保留结构化事件流。 | |

**User's choice:** 日志+latest视图
**Notes:** 既要可校验，也要方便 operator 日常查看。

| Option | Description | Selected |
|--------|-------------|----------|
| 按治理动作聚合 | latest 视图按待审批/最近批准/最近拒绝/最近 override 等动作聚合。 | ✓ |
| 按时间线展示 | 像系统日志一样平铺。 | |
| 队列+最近完成 | 拆成待处理队列 + 最近完成事件。 | |

**User's choice:** 按治理动作聚合
**Notes:** 用户更看重每日决策视角，而不是纯日志视角。

| Option | Description | Selected |
|--------|-------------|----------|
| 强绑定主决策包 | 每条治理动作都强制引用当日 `OPERATING_DECISION_PACKAGE.md` 或其 action_id。 | ✓ |
| 允许脱离主包 | 某些治理动作可不绑定主包，只写理由。 | |
| 仅高影响绑定 | 只有高影响动作必须绑定主包。 | |

**User's choice:** 强绑定主决策包
**Notes:** 审计链必须从 Phase 3 的主决策包起步，不能变成松散的平行系统。

---

## 状态推进

| Option | Description | Selected |
|--------|-------------|----------|
| 硬阻断 | 高影响动作没有审批结果、或前一阶段失败时，后续状态推进直接阻断。 | ✓ |
| 可override继续 | 默认阻断，但允许写 override 事件后继续。 | |
| 宽松推进 | 默认可继续，只在少数动作阻断。 | |

**User's choice:** 硬阻断
**Notes:** Phase 4 应该把治理从“提醒”变成“真阻断”。

| Option | Description | Selected |
|--------|-------------|----------|
| 按动作类型判定 | 影响资金、归档、状态跃迁或治理/公司级状态的动作，一律视为高影响。 | ✓ |
| 按阈值判定 | 主要依赖金额/分值阈值。 | |
| 类型+阈值混合 | 类型先分层，再对部分动作细化阈值。 | |

**User's choice:** 按动作类型判定
**Notes:** 用户希望高影响动作定义简单、可自动检查、覆盖面完整。

| Option | Description | Selected |
|--------|-------------|----------|
| 停在失败点 | 关键步骤失败时不推进后续状态，只写 failed governance event。 | ✓ |
| 自动回滚 | 失败后自动回退到上个稳定状态。 | |
| 局部降级 | 冻结关键动作，但继续跑非关键步骤。 | |

**User's choice:** 停在失败点
**Notes:** 用户不希望 Phase 4 先引入复杂回滚逻辑，先保证失败可见且可阻断。

| Option | Description | Selected |
|--------|-------------|----------|
| 仅CEO可override | 只有 CEO 可以显式打破阻断继续推进。 | ✓ |
| CEO+Accountant | CEO 和 Accountant 都可 override。 | |
| 各角色自override | 各主写角色都可 override 自己的步骤。 | |

**User's choice:** 仅CEO可override
**Notes:** override 是例外动作，必须集中在最高治理角色手里。

---

## 写权限

| Option | Description | Selected |
|--------|-------------|----------|
| 严格主写者边界 | 继续保持每类资产只有固定主写者；CEO 只能走显式 fallback/override 流程。 | ✓ |
| CEO常驻超权 | CEO 可直接改任何治理或业务状态。 | |
| 主副都可写 | 主写者+同领域副写者都可写。 | |

**User's choice:** 严格主写者边界
**Notes:** 用户不想把治理做成“CEO 随时能改一切”的虚设制度。

| Option | Description | Selected |
|--------|-------------|----------|
| 接管必须留痕 | CEO fallback 接管时必须写结构化 governance event，记录原因、目标资产、原主写者、关联主决策包。 | ✓ |
| 口头接管即可 | 在 prompt 里声明即可。 | |
| 禁止接管 | CEO 不能 fallback 接管。 | |

**User's choice:** 接管必须留痕
**Notes:** 用户接受现实中的兜底接管，但必须留下清晰审计痕迹。

| Option | Description | Selected |
|--------|-------------|----------|
| 治理只做门禁 | Governance layer 负责拦截/记录/放行，不直接改底层状态文件。 | ✓ |
| 治理可直接写底层 | Governance 层可以直接代写底层文件。 | |
| 部分直写 | 财务类资产保持单一路径，其它可由治理层直写。 | |

**User's choice:** 治理只做门禁
**Notes:** 现有单一路径（如 `manage_finance.py`）必须保留为真正权威入口。

| Option | Description | Selected |
|--------|-------------|----------|
| 规则编码化 | 把写权限、fallback、审批条件明确编码成可执行检查。 | ✓ |
| 先文档化 | 先只做人类约定和日志。 | |
| 我自定义 | 用户自定义。 | |

**User's choice:** 规则编码化
**Notes:** 用户希望 Phase 4 真正把治理落地为可执行控制，而不是继续停留在说明文档层。

---

## Claude's Discretion

- 具体 JSONL 文件路径与 governance latest markdown 文件名
- 事件 schema 字段命名细节
- 状态枚举与失败码命名
- 规则检查器的具体实现方式

## Deferred Ideas

- 更丰富的治理状态 dashboard / UI 展示 —— 更适合 Phase 5
- 更广泛的多人协作审批模型 —— 更适合后续团队化阶段
- 更细的状态码与回滚体系 —— 可在计划/实现阶段细化，但不改变已锁定阻断语义
