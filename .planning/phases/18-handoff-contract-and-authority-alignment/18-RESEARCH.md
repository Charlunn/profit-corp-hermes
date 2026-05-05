# Phase 18: Handoff Contract and Authority Alignment - Research

**Researched:** 2026-05-04  
**Domain:** approved-project delivery 治理契约收敛  
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Phase 18 统一采用 **9 段 canonical specialist handoff contract**，不再接受“生成 9 段、校验 6 段”的结构漂移。
- **D-02:** canonical sections 固定为：`Stage Summary`、`Outputs Produced`、`Evidence Links`、`Changed Files`、`User Visible Behavior`、`Pain Point Mapping`、`Gate Decision`、`Open Risks`、`Next Stage Input`。
- **D-03:** handoff validator 应成为 **结构契约的权威定义者**；handoff generator 必须严格对齐 validator 所要求的同一套结构，而不是反过来放宽 validator 去兼容多种格式。
- **D-04:** `Changed Files`、`User Visible Behavior`、`Pain Point Mapping` 不是可选增强项，而是本里程碑治理所需的必填结构，因为后续 evidence gate 与 real-product proof 都依赖这些信息。
- **D-05:** Phase 18 采用 **双层 machine-readable 分工**：`APPROVED_PROJECT.json` 保存 latest canonical state，`approved-delivery-events.jsonl` 保存 append-only 历史与每次 gate/evidence 明细。
- **D-06:** status markdown 与 final operator review 必须从 authority latest state + append-only events 派生，不允许各自发明独立状态语义。
- **D-07:** handoff markdown 继续保留给人读，但与 handoff 对应的 gate/evidence/outcome 需要有 machine-readable 结构，供 validator、renderer、resume logic 共用。
- **D-08:** 当 authority JSON、event history、status markdown、final operator review 出现冲突时，**以 authority 中的 latest canonical state 为当前真相**。
- **D-09:** `approved-delivery-events.jsonl` 的职责是说明 blocked → resumed → recovered 的历史轨迹，而不是定义“当前现在算什么状态”。
- **D-10:** status 与 final review 是 operator-facing 派生视图，必须服从 authority latest state；它们可以显示最近一次 block/recovery 背景，但不能覆盖当前态。
- **D-11:** 保留 blocked history 作为审计证据，但不能让过期 blocked 字段在恢复成功后继续污染当前 authoritative state。
- **D-12:** operator 第一眼必须能看清当前是 `blocked`、`resumed/in_progress`、还是 `completed`，以及当前卡在哪个 stage。
- **D-13:** operator-facing artifacts 必须明确显示最近一次 block reason、关联 evidence path、以及当前恢复推进到了哪一步。
- **D-14:** operator surfacing 目标是“快速判断现在该不该继续、该修什么”，不是展开全部历史细节；完整历史交给 events 承载。

### Claude's Discretion
- latest canonical state 在 `APPROVED_PROJECT.json` 中的精确字段命名与嵌套层级
- event payload 中 handoff/gate/evidence 明细的具体字段布局
- status markdown 与 final review 呈现“当前态 + 最近阻塞背景”的具体排版
- validator 报错文案与断言粒度，只要不改变上述权威分层与契约方向
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| HANDOFF-01 | Runtime-generated stage handoffs and handoff validators must share one normalized section contract | 统一 `validate_delivery_handoff.py` 为结构权威，并让 `build_specialist_handoff_markdown(...)`、模板、测试全部对齐 9 段 canonical contract |
| HANDOFF-02 | Authority, event history, status, and final review must converge on same latest governance truth | 把 latest truth 收敛到 `APPROVED_PROJECT.json.pipeline`，把历史/证据留在 `approved-delivery-events.jsonl`，renderer 与 cross-link validator 只消费 authority latest state + event history |
</phase_requirements>

## Summary

本阶段不是新增治理子系统，而是修复现有 brownfield delivery pipeline 内部“写一套、验一套、展示另一套”的契约漂移。当前运行时 handoff generator 已经输出 9 段 specialist handoff，而 handoff validator 与旧模板仍停留在 6 段基线，导致 HANDOFF-01 在结构层面天然不成立。当前 operator-facing status 与 final review 虽然已开始尊重 authority pipeline state，但 final review 仍由同一份 status markdown 直接镜像写出，说明它们尚未形成“同源但不同职责”的派生视图边界。

Phase 18 的最小可行改造面应严格收敛在五个现有 surface：handoff generator、handoff validator、authority latest-state schema、event payload schema、status/final-review renderer 与 cross-link validator。不应引入新数据库、新工作流引擎或新的 operator 主视图。推荐路径是：先统一 9 段 handoff contract，再把 machine-readable gate/evidence/outcome 嵌入既有 event payload 与 authority latest state，最后让 status/final review 只作为 latest truth + recent blocked context 的派生展示。

## Current Drift Inventory

### Drift 1: Generator 9 sections vs Validator 6 sections
- `build_specialist_handoff_markdown(...)` 已输出 9 段 specialist handoff。
- `validate_delivery_handoff.py` 仍以 6 段 `REQUIRED_STAGE_HEADINGS` 为校验基线。
- `docs/skill-governance/templates/stage-handoff-template-v0.2.md` 仍反映旧 6 段心智模型。

### Drift 2: Handoff markdown richer than machine-readable event payload
- event `substance` 当前仅覆盖 `template_only`、`issues`、`touched_paths` 等较窄字段。
- handoff 中的 `Changed Files`、`User Visible Behavior`、`Pain Point Mapping` 尚未被稳定投影成 machine-readable shared schema。

### Drift 3: Latest truth exists, but semantic boundaries are still fuzzy
- `APPROVED_PROJECT.json.pipeline` 已承担 current stage/status truth。
- `latest_blocked_prerequisite` 同时承载 blocked 可见性与恢复后残留背景，容易混淆“当前仍 blocked”与“最近一次曾 blocked”。

### Drift 4: Final review is still a status mirror
- renderer 会把同一份 markdown 同时写到 `DELIVERY_PIPELINE_STATUS.md` 和 `FINAL_OPERATOR_REVIEW.md`。
- 需要改为“同源，不同排版/职责”。

## Recommended Brownfield Changes

### 1) Canonicalize the handoff contract first
**改造面：**
- `scripts/validate_delivery_handoff.py`
- `scripts/start_approved_project_delivery.py`
- `docs/skill-governance/templates/stage-handoff-template-v0.2.md`
- handoff-focused tests

**推荐落点：**
- 在 validator 中显式定义 canonical 9 headings 常量。
- `validate_stage_handoff(...)` 校验标题顺序、段落存在、最小非空内容、metadata token。
- generator 不做兼容分支，只按 canonical 9 headings 输出。

### 2) Introduce a shared machine-readable handoff summary block
**推荐字段方向：**
```json
"handoff_summary": {
  "contract_version": "specialist-handoff/v1",
  "sections_present": [
    "stage_summary",
    "outputs_produced",
    "evidence_links",
    "changed_files",
    "user_visible_behavior",
    "pain_point_mapping",
    "gate_decision",
    "open_risks",
    "next_stage_input"
  ],
  "changed_files": [],
  "user_visible_behavior": [],
  "pain_point_mapping": [],
  "gate_decision": {
    "status": "pass|blocked|resume_required",
    "reason": "",
    "evidence_paths": []
  },
  "open_risks": [],
  "next_stage_input": []
}
```
- event payload 应写入该结构；authority 只保留 latest summarized pointers，不复制整份历史。

### 3) Separate latest canonical truth from latest blocked background
**推荐 authority schema 方向：**
```json
"pipeline": {
  "current_stage": "...",
  "current_status": "blocked|in_progress|completed",
  "latest_governance": {
    "status": "blocked|resumed|recovered|completed",
    "stage": "...",
    "event_id": "...",
    "event_ts": "...",
    "gate_decision": "pass|blocked"
  },
  "latest_block_context": {
    "event_id": "...",
    "stage": "...",
    "reason": "...",
    "evidence_paths": [],
    "resolved_by_event_id": "..."
  }
}
```
- `latest_governance` 定义 current truth。
- `latest_block_context` 只做最近阻塞背景，不定义当前态。

### 4) Keep event log append-only and granular
**推荐 event schema 方向：**
```json
{
  "action": "specialist_stage_completed|pipeline_blocked|pipeline_resumed|pipeline_recovered|pipeline_completed",
  "stage": "development",
  "status": "completed",
  "handoff": {
    "path": "...",
    "contract_version": "specialist-handoff/v1",
    "contract_ok": true
  },
  "evidence": {
    "transcript_path": "...",
    "workspace_changes_path": "...",
    "additional_paths": []
  },
  "gate": {
    "decision": "pass|blocked",
    "reason": "...",
    "blocking": true
  },
  "outcome": {
    "next_stage": "...",
    "resume_from": "...",
    "operator_action": "..."
  }
}
```

### 5) Split status vs final review by presentation, not truth source
**status 应显示：** 当前 `blocked / in_progress / completed`、当前 stage、最近 block reason、相关 evidence path、当前恢复推进位置。  
**final review 应显示：** 当前 latest governance conclusion、最近恢复/阻塞背景摘要、operator 下一步动作或 closure statement、authority/event/status cross-link pointers。

## Affected Files and Functions

### Highest-priority files
1. `scripts/validate_delivery_handoff.py`
   - `REQUIRED_STAGE_HEADINGS`
   - `validate_stage_handoff(...)`
2. `scripts/start_approved_project_delivery.py`
   - `build_specialist_handoff_markdown(...)`
   - `make_event(...)`
   - `update_pipeline_state(...)`
   - `block_pipeline(...)`
   - `finalize_delivery_handoff(...)`
3. `scripts/render_approved_delivery_status.py`
   - `build_status_markdown(...)`
4. `scripts/validate_approved_delivery_pipeline.py`
   - `validate_current_state_precedence(...)`
   - `validate_blocked_prerequisite_visibility(...)`

### Supporting docs/templates
- `docs/skill-governance/templates/stage-handoff-template-v0.2.md`
- `docs/skill-governance/templates/final-delivery-template-v0.2.md`

### Test surfaces
- `tests/test_approved_delivery_pipeline_cli.py`
- `tests/test_project_delivery_pipeline_resume.py`
- `tests/test_project_delivery_pipeline_bootstrap.py`
- `tests/test_approved_project_record.py`

## Recommended Implementation Order

### Wave 1: Handoff structural authority
- 升级 validator 到 9 段 canonical contract
- 对齐 generator
- 更新 stage handoff template
- 补结构回归测试

### Wave 2: Machine-readable gate/evidence/outcome contract
- 在 event payload 增加 `handoff` / `evidence` / `gate` / `outcome` 结构
- authority latest state 只保留 current truth + latest block background
- cross-link validator 校验 markdown 与 JSON 关键字段一致

### Wave 3: Operator surfacing alignment
- status 与 final review 改为同源不同排版
- 明确展示当前态、当前 stage、最近 block reason、恢复推进位置
- 删除“同一 markdown 复制两份”的实现

### Wave 4: Regression hardening
- blocked → resumed → recovered → completed
- stale blocked reason 不污染 current truth
- handoff markdown 与 event payload 关键字段同步
- final review/status 不再自创语义

## Test Recommendations

| Scenario | Why it matters | Primary Test Surface |
|----------|----------------|----------------------|
| runtime generator emits exact 9 canonical sections | 覆盖 HANDOFF-01 主契约 | handoff validator/unit tests |
| validator rejects old 6-section specialist handoff | 防止 drift 兼容回流 | handoff validator/unit tests |
| event payload contains machine-readable handoff/gate/evidence/outcome | 供 renderer/validator/resume 复用 | approved delivery pipeline CLI tests |
| blocked run records block context but not false current completion | current truth 与 history 分离 | bootstrap tests |
| resumed/recovered run updates authority current truth while preserving blocked history in events | 防 stale blocked pollution | resume tests |
| completed run shows completed current truth + recent block background only as context | D-12/D-13 operator surfacing | CLI/render tests |
| status and final review are both derived from same authority latest state | HANDOFF-02 核心收敛 | CLI/render tests |
| final review is not byte-identical status mirror anymore but remains semantically consistent | 区分视图职责 | render tests |
| cross-link validator fails when markdown handoff says pass but event gate says blocked | 防 human-readable / machine-readable drift | pipeline validator tests |

## Open Questions
- authority latest truth 最终字段命名采取最小侵入还是更显式分层
- final review 是否采用独立模板还是 renderer 内分支
- machine-readable handoff summary 是扩展 `substance` 还是提升为并列块

## RESEARCH COMPLETE
