# Phase 18: Handoff Contract and Authority Alignment - Context

**Gathered:** 2026-05-04
**Status:** Ready for planning

<domain>
## Phase Boundary

对齐 approved-project delivery 中的阶段交接契约与 authority 真相模型：让运行时生成的 specialist handoff、handoff validator、authority JSON、event history、operator status、final operator review 都围绕同一套可执行契约与同一份 latest governance truth 工作。

本阶段只解决“交接结构统一 + 真相归一”的治理问题，不扩展新的 specialist 能力、不引入新的状态存储系统，也不处理 `/demo` 产品证明或 UI artifact 深度校验本身。

</domain>

<decisions>
## Implementation Decisions

### Handoff contract
- **D-01:** Phase 18 统一采用 **9 段 canonical specialist handoff contract**，不再接受“生成 9 段、校验 6 段”的结构漂移。
- **D-02:** canonical sections 固定为：`Stage Summary`、`Outputs Produced`、`Evidence Links`、`Changed Files`、`User Visible Behavior`、`Pain Point Mapping`、`Gate Decision`、`Open Risks`、`Next Stage Input`。
- **D-03:** handoff validator 应成为 **结构契约的权威定义者**；handoff generator 必须严格对齐 validator 所要求的同一套结构，而不是反过来放宽 validator 去兼容多种格式。
- **D-04:** `Changed Files`、`User Visible Behavior`、`Pain Point Mapping` 不是可选增强项，而是本里程碑治理所需的必填结构，因为后续 evidence gate 与 real-product proof 都依赖这些信息。

### Evidence schema layering
- **D-05:** Phase 18 采用 **双层 machine-readable 分工**：`APPROVED_PROJECT.json` 保存 latest canonical state，`approved-delivery-events.jsonl` 保存 append-only 历史与每次 gate/evidence 明细。
- **D-06:** status markdown 与 final operator review 必须从 authority latest state + append-only events 派生，不允许各自发明独立状态语义。
- **D-07:** handoff markdown 继续保留给人读，但与 handoff 对应的 gate/evidence/outcome 需要有 machine-readable 结构，供 validator、renderer、resume logic 共用。

### Truth precedence
- **D-08:** 当 authority JSON、event history、status markdown、final operator review 出现冲突时，**以 authority 中的 latest canonical state 为当前真相**。
- **D-09:** `approved-delivery-events.jsonl` 的职责是说明 blocked → resumed → recovered 的历史轨迹，而不是定义“当前现在算什么状态”。
- **D-10:** status 与 final review 是 operator-facing 派生视图，必须服从 authority latest state；它们可以显示最近一次 block/recovery 背景，但不能覆盖当前态。
- **D-11:** 保留 blocked history 作为审计证据，但不能让过期 blocked 字段在恢复成功后继续污染当前 authoritative state。

### Operator surfacing
- **D-12:** operator 第一眼必须能看清当前是 `blocked`、`resumed/in_progress`、还是 `completed`，以及当前卡在哪个 stage。
- **D-13:** operator-facing artifacts 必须明确显示最近一次 block reason、关联 evidence path、以及当前恢复推进到了哪一步。
- **D-14:** operator surfacing 目标是“快速判断现在该不该继续、该修什么”，不是展开全部历史细节；完整历史交给 events 承载。

### Claude's Discretion
- latest canonical state 在 `APPROVED_PROJECT.json` 中的精确字段命名与嵌套层级
- event payload 中 handoff/gate/evidence 明细的具体字段布局
- status markdown 与 final review 呈现“当前态 + 最近阻塞背景”的具体排版
- validator 报错文案与断言粒度，只要不改变上述权威分层与契约方向

</decisions>

<specifics>
## Specific Ideas

- 用户不希望继续卷入底层 schema 选择，明确要求由 Claude 采用推荐方案。
- 推荐并已锁定的方向是：**9 段统一 handoff 结构 + authority latest state / event append-only history 双层分工 + authority 当前态优先 + operator 先看当前态与最近阻塞原因**。
- 这一阶段应优先消灭“写的是一套、验的是另一套、展示的又是第三套”的治理漂移。

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and milestone constraints
- `.planning/ROADMAP.md` §Phase 18 — 定义本阶段目标、边界、以及 HANDOFF-01 / HANDOFF-02 覆盖范围
- `.planning/REQUIREMENTS.md` — `HANDOFF-01`、`HANDOFF-02` 的正式要求
- `.planning/PROJECT.md` — v1.1.2 的治理硬化目标与“real SaaS, not template surface”总方向
- `.planning/STATE.md` — 当前里程碑状态与下一阶段定位

### Prior phase decisions that must carry forward
- `.planning/phases/06-execution-handoff-and-team-readiness/06-CONTEXT.md` — 早期 handoff contract 倾向于稳定结构与轻量机器可读元数据，为本阶段的 specialist handoff 统一提供上游语义
- `.planning/phases/10-approved-project-delivery-pipeline/10-CONTEXT.md` — approved-project authority layer、blocked/resume semantics、以及 dual-surface state 的基础约束
- `.planning/phases/12-credential-governance-and-operator-handoff/12-CONTEXT.md` — final operator review、auditable event stream、authority-above-workspace 的治理边界
- `.planning/phases/17-authority-and-status-convergence/17-authority-and-status-convergence-01-SUMMARY.md` — recovered current truth 覆盖 stale blocked state 的最近收敛结论
- `.planning/phases/17-authority-and-status-convergence/17-authority-and-status-convergence-02-SUMMARY.md` — authority/event/status/final-review 收敛路径的延续上下文
- `.planning/phases/17-authority-and-status-convergence/17-authority-and-status-convergence-03-SUMMARY.md` — completed handoff-facing state 与恢复后真相的现有闭环约束

### Existing contracts and code surfaces
- `docs/skill-governance/templates/stage-handoff-template-v0.2.md` — 现有 stage handoff 模板基线
- `docs/skill-governance/templates/final-delivery-template-v0.2.md` — final delivery/final review 相关结构基线
- `scripts/start_approved_project_delivery.py` — runtime handoff generation、authority persistence、event append、status/final-review linkage 的核心 orchestrator
- `scripts/validate_delivery_handoff.py` — 当前 handoff validator；现存 6 段要求与 runtime 9 段输出之间的结构漂移源头
- `scripts/render_approved_delivery_status.py` — operator-facing latest-view renderer
- `scripts/validate_approved_delivery_pipeline.py` — authority/status/final-review cross-link validator

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/start_approved_project_delivery.py::build_specialist_handoff_markdown(...)` 已经输出 9 段结构，是 canonical contract 的最接近现成实现。
- `scripts/validate_delivery_handoff.py` 已经具备 heading order / metadata token / run replay 校验骨架，适合升级为 handoff structural authority。
- `scripts/validate_approved_delivery_pipeline.py` 已经承担 authority、status、final review、manifest、workspace artifact 的 cross-link 检查，是 Phase 18 真相收敛的自然落点。
- `scripts/render_approved_delivery_status.py` 已有 authority → operator latest view 的渲染职责，适合承接“当前态 + 最近阻塞背景”的统一展示。

### Established Patterns
- 该仓库偏好 **authority JSON + append-only JSONL + derived markdown**，而不是引入新的数据库或 workflow engine。
- 高影响状态流转优先通过 script-driven artifacts 持久化，而不是靠聊天上下文或隐式进程状态。
- blocked/resumed/recovered 语义在近几个 phase 已经存在，当前问题不是没有状态，而是不同 surface 对同一状态的解释不一致。
- status/final review 在架构上应是派生视图，而不是新的真相来源。

### Integration Points
- Phase 18 需要同时修改 handoff generator、handoff validator、approved delivery validator、status renderer、以及 authority/event persistence 的字段契约。
- 规划时应把“结构统一”和“真相优先级统一”拆成可验证的若干计划，避免一次性混改所有治理层。
- Phase 19 的 specialist evidence gate 与 UI artifact gate 将直接依赖本阶段统一后的 handoff/evidence contract，因此本阶段必须先稳定 contract 再扩 gate。

</code_context>

<deferred>
## Deferred Ideas

- `/ui-ux-pro-max` artifact 的内容完备性与 UI stage blocking 规则属于 Phase 19，不在本阶段展开。
- `/demo` 与 identity-only proof 剔除属于 Phase 20，不在本阶段定义产品证明规则本体。
- bootstrap/resume 全覆盖回归锁定属于 Phase 21，不在本阶段完成完整恢复矩阵。
- 新增 specialist 角色、额外 operator dashboard、或新的持久化系统都不属于本阶段。

</deferred>

---

*Phase: 18-handoff-contract-and-authority-alignment*
*Context gathered: 2026-05-04*
