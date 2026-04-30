# Phase 5: Operating Visibility Surface - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-25
**Phase:** 05-Operating Visibility Surface
**Areas discussed:** Freshness & alerts, Action framing, Source blending

---

## Freshness & alerts

| Option | Description | Selected |
|--------|-------------|----------|
| 平静默认 + 异常置顶 | 正常时保持简洁；只有 blocked、pending approval、数据过期、采集失败时才高亮置顶。 | ✓ |
| 告警优先视图 | 顶部先显示所有风险/阻塞/过期项，其他机会和摘要往后放。 | |
| 分层状态 | 顶部固定显示整体状态（Healthy / Watch / Action Required），下面再分区展示 freshness、governance、opportunity。 | |
| 你来定 | 用户自由描述状态呈现方式。 | |

**User's choice:** 平静默认 + 异常置顶
**Notes:** 用户明确选择 1，偏好默认简洁、异常才打断阅读流。

---

## Action framing

| Option | Description | Selected |
|--------|-------------|----------|
| 只保留 Top 3 动作 | 只显示最重要的 3 个动作，强调聚焦，避免信息过载。 | ✓ |
| 按类型分组 | 按增长机会 / 风险处理 / 运营维护等来源分组。 | |
| 按紧急度分组 | 按现在做 / 今天做 / 可稍后分组。 | |
| 你来定 | 用户自由描述动作区结构。 | |

**User's choice:** 只保留 Top 3 动作
**Notes:** 用户补充说明“之后的都按照你推荐的来”，因此后续未继续打断式追问。

---

## Source blending

| Option | Description | Selected |
|--------|-------------|----------|
| 主决策包为主锚点，治理/新鲜度做覆盖层 | 以 operating decision package 为主锚点，再叠加 governance status 与 external intelligence freshness 的健康/阻塞信息。 | ✓ |
| 多来源并列汇总 | 决策包、治理、外部情报、执行包、董事会简报并列进入主摘要。 | |
| 治理状态优先，机会摘要次之 | 先看阻塞与审批，再看机会与动作。 | |
| 你来定 | 用户自由描述来源主次关系。 | |

**User's choice:** 主决策包为主锚点，治理/新鲜度做覆盖层
**Notes:** 根据用户“之后的都按照你推荐的来”的指示，采用推荐方案：决策包为主来源，治理与新鲜度负责异常覆盖，执行包和董事会简报仅作支持性引用。

---

## Claude's Discretion

- 可见性工件的具体 markdown 栏目命名
- stale 判定细则与严重级别标记样式
- supporting artifact 的引用排版方式

## Deferred Ideas

- Rich dashboard / interactive UI 形态 — 后续独立 phase
- 更完整的 task board / collaboration queue — 后续执行或协作 phase
