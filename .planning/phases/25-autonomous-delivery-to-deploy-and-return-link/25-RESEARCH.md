# Phase 25: Autonomous Delivery to Deploy and Return Link - Research

**Researched:** 2026-05-04  
**Domain:** 批准后自治交付编排、权威状态驱动恢复、聊天线程最终回执  
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
### Post-approval autonomous continuation
- **D-01:** Approval should hand off directly into the existing approved-project delivery backbone using persisted authoritative state, not require a separate human `resume` command on healthy runs.
- **D-02:** Automation should advance by reading and updating the same `APPROVED_PROJECT.json`, append-only events, and rendered status/final review artifacts already used by the shipped pipeline.
- **D-03:** Any stage transition that cannot be proven from authoritative artifacts should block rather than pretending autonomy succeeded.

### Specialist proof and real implementation evidence
- **D-04:** Autonomous continuation must keep the stricter v1.1.2 proof gates: real specialist artifacts, valid `/ui-ux-pro-max` coverage where applicable, workspace-change evidence, and product-proof artifacts remain mandatory.
- **D-05:** The orchestrator may automate stage progression, but it may not replace specialist output with synthetic placeholder proof or ad hoc markdown summaries.
- **D-06:** Pricing, monetization, languages, and other approved contract fields must survive into the delivered workspace surfaces and release evidence, not disappear after approval.

### Final chat-thread handoff
- **D-07:** Completion should send one derived final response to the originating chat thread containing the live deployment link, concise ship summary, and links/paths to authoritative final artifacts.
- **D-08:** Failure or blocked completion should send the same style of final thread response, but with explicit blocked reason, failed stage, and next recovery context instead of a fake success.
- **D-09:** Final chat replies should be rendered from persisted authority/final-review truth, not composed from transient process memory.

### Exceptional recovery vs healthy-path autonomy
- **D-10:** Healthy runs should need no manual resumes after approval, but exceptional failures should still preserve a resumable blocked state rather than hiding recovery requirements.
- **D-11:** Chat-visible completion/failure should stay aligned with the same blocked/recovered truth already enforced in delivery status and final review artifacts.
- **D-12:** Phase 25 should extend existing resume/recovery mechanics to notification/orchestration boundaries rather than inventing a second exceptional-path model for chat runs.

### the agent's Discretion
- Exact scheduler/polling mechanism that advances approved runs after chat approval, as long as it preserves authoritative state transitions and healthy-path autonomy.
- Exact final chat message layout, as long as deployment link, concise summary, and blocked context remain explicit.
- Exact artifact backlink set included in the final response, as long as operators can reach the authoritative review/status bundle quickly.

### Deferred Ideas (OUT OF SCOPE)
- Rich multi-recipient notification subscriptions remain out of scope for this phase.
- Chat-native operator recovery commands remain future expansion beyond healthy-path autonomy plus explicit blocked reporting.
- Broad workflow-engine replacement or background-service rearchitecture remains out of scope; this phase should extend the existing artifact-driven delivery pipeline.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| AUTO-02 | After approval, Hermes continues through design, development, testing, GitHub, and Vercel without requiring manual stage resumes on healthy runs. | 复用 `start_approved_project_delivery.py` 的既有阶段机与 `resume_approved_project_delivery()`，把“审批后触发”接到现有 authority/event/render/validate 模型上，而不是新建 runner。[VERIFIED: codebase grep] |
| AUTO-03 | Hermes must use real specialist output and real implementation evidence for delivery proof instead of self-generated placeholder artifacts. | 保留 UI 产物校验、结构化阶段证据、workspace change inventory、testing verification evidence、product proof 与 validator 交叉校验门禁。[VERIFIED: codebase grep] |
| AUTO-04 | When deployment completes, Hermes returns the live link and concise ship summary to the originating chat thread. | 最终聊天回复必须从 `APPROVED_PROJECT.json` + `approved-delivery-events.jsonl` + `FINAL_OPERATOR_REVIEW.md`/`DELIVERY_PIPELINE_STATUS.md` 派生，并用 Phase 22 的聊天线程标识完成回帖。[VERIFIED: codebase grep][ASSUMED] |
</phase_requirements>

## Summary

Phase 25 的核心不是“再造一个自动部署系统”，而是把已存在的 approved-delivery 权威流水线变成审批后的健康路径默认入口，并在 handoff 之后把真实部署结果回传到原始聊天线程。[VERIFIED: codebase grep] 现有主干脚本已经覆盖从 `approval` 到 `handoff` 的完整阶段序列、append-only 事件、状态渲染、最终 review、GitHub/Vercel 交付与恢复逻辑；因此规划时应避免任何第二套“chat mode pipeline”或内存态编排器。[VERIFIED: codebase grep]

Phase 25 真正新增的责任有两块：其一，在 Phase 24 批准完成后自动触发既有 delivery backbone，并在健康路径持续推进，直到 `handoff` 完成；其二，将完成态或阻塞态从持久化权威产物渲染为面向聊天线程的一条最终消息，包含 live deploy link、简短交付总结，以及失败时的阻塞原因与恢复上下文。[VERIFIED: codebase grep][ASSUMED]

**Primary recommendation:** 用“chat approval -> enqueue approved authority path -> 调用既有 `start/resume/finalize` 主干 -> 从 persisted status/review 渲染单条最终聊天回执”的薄编排层实现本阶段，不要重写交付流水线。[VERIFIED: codebase grep][ASSUMED]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| 审批后自动启动交付 | API / Backend | Frontend Server (SSR) | 批准事件、队列推进、authority 更新和 CLI/脚本调度都属于后端编排，不应放在聊天客户端本身。[VERIFIED: codebase grep][ASSUMED] |
| 阶段状态与阻塞真相维护 | API / Backend | Database / Storage | 真相源是 `APPROVED_PROJECT.json`、事件流与渲染产物；状态机和恢复判断应由后端拥有。[VERIFIED: codebase grep] |
| 专家产物/产品证明门禁 | API / Backend | Database / Storage | 现有门禁来自脚本校验和文件证据，不是前端职责。[VERIFIED: codebase grep] |
| GitHub/Vercel 凭证化交付 | API / Backend | External Services | 现有实现通过本地 CLI 和凭证会话执行，属于后端外部服务编排。[VERIFIED: codebase grep][VERIFIED: local runtime] |
| 最终聊天线程回执 | API / Backend | External Services | 需要使用持久化的聊天来源元数据调用 Discord/Telegram API 回帖。[CITED: https://discord.com/developers/docs/resources/message][CITED: https://core.telegram.org/bots/api#sendmessage][ASSUMED] |

## Project Constraints (from CLAUDE.md)

- 仓库根目录存在 `CLAUDE.md`，其内容与 `AGENTS.md` 相同：仅在前端 UI 实现/改版类工作时，必须先调用 `/ui-ux-pro-max`，并以该技能输出作为设计权威。[VERIFIED: local file]
- 本阶段是后端编排与通知研究，不直接要求新增前端页面；但若 Phase 25 计划触及交付阶段中的前端实现接缝，仍必须保留既有 `/ui-ux-pro-max` 阻塞门禁，不能因“自治化”而绕过。[VERIFIED: local file][VERIFIED: codebase grep]

## Standard Stack

### Core
| Library / Tool | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.11.15 | 编排 approved-delivery authority、事件、渲染与校验脚本。[VERIFIED: local runtime] | 现有所有主干脚本与测试均为 Python 实现，无需引入新运行时。[VERIFIED: codebase grep] |
| `scripts/start_approved_project_delivery.py` | repo-local | 唯一标准 delivery state machine，负责 `approval` 到 `handoff` 的推进、阻塞、恢复与最终快照。[VERIFIED: codebase grep] | 已存在完整阶段序列和 `start`/`resume`/`finalize` 入口，是本阶段必须复用的主干。[VERIFIED: codebase grep] |
| `approved-delivery-events.jsonl` + `APPROVED_PROJECT.json` | repo-local | 权威事件流与当前状态真相源。[VERIFIED: codebase grep] | Context 已锁定 Phase 25 必须在同一 authority/event 模型上推进。[VERIFIED: codebase grep] |
| `render_approved_delivery_status.py` + `validate_approved_delivery_pipeline.py` | repo-local | 渲染 operator-facing truth，并验证 final review / product proof / blocked state / handoff 一致性。[VERIFIED: codebase grep] | 最终聊天回执应派生于这些持久化真相面，而不是临时内存总结。[VERIFIED: codebase grep] |

### Supporting
| Library / Tool | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| GitHub CLI `gh` | 2.91.0，发布于 2026-04-22。[VERIFIED: local runtime] | 既有 GitHub 仓库准备与同步流程依赖本地认证会话/CLI 能力。[VERIFIED: codebase grep] | 用于 `github_repository` / `github_sync` 阶段，不建议在 Phase 25 改写为直接 REST 客户端。[VERIFIED: codebase grep][CITED: https://cli.github.com/manual/gh_auth_status] |
| Vercel CLI | 53.0.1。[VERIFIED: local runtime] | 既有 Vercel link/deploy/metadata persistence 流程的标准执行面。[VERIFIED: codebase grep] | 用于 `vercel_linkage` / `vercel_deploy` 阶段，不建议本阶段替换为其他部署面。[VERIFIED: codebase grep][CITED: https://vercel.com/docs/cli/deploy] |
| Hermes Agent CLI | 0.10.0。[VERIFIED: local runtime] | design/development/testing 等专家阶段调度入口。[VERIFIED: local runtime][VERIFIED: codebase grep] | 仅用于真实 specialist output；不能被编排器伪造摘要取代。[VERIFIED: codebase grep] |
| Claude Code CLI | 2.1.126。[VERIFIED: local runtime] | 现有专家执行与 transcript 证据链的一部分。[VERIFIED: local runtime][VERIFIED: codebase grep] | 阶段证据 bundle 仍需 transcript，健康路径自治不能移除此证明。[VERIFIED: codebase grep] |
| Discord Create Message API | current docs | 向原始 Discord channel/thread 发送最终消息，可用 `message_reference` 形成回复关联。[CITED: https://discord.com/developers/docs/resources/message] | 当来源平台是 Discord 时使用；线程/频道定位应来自 Phase 22 持久化来源元数据。[CITED: https://discord.com/developers/docs/resources/message][ASSUMED] |
| Telegram Bot API `sendMessage` | current docs | 向原始 Telegram chat/topic 发送最终消息，可附 `reply_parameters`，并支持 `message_thread_id`。[CITED: https://core.telegram.org/bots/api#sendmessage] | 当来源平台是 Telegram 时使用；topic/thread 定位同样依赖 Phase 22 来源元数据。[CITED: https://core.telegram.org/bots/api#sendmessage][ASSUMED] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| 复用 `start_approved_project_delivery.py` | 新建 “chat-native autonomous runner” | 与 D-01/D-02/D-12 冲突，会复制状态机并制造 authority drift 风险。[VERIFIED: codebase grep] |
| 从 persisted status/review 渲染最终聊天消息 | 直接从进程内存拼接消息 | 与 D-09 冲突，失败恢复后无法保证聊天可见结果与权威产物一致。[VERIFIED: codebase grep] |
| 继续使用 `gh` / `vercel` CLI | 直接改写 GitHub/Vercel API 客户端 | 本阶段范围外，会重开已修复的 v1.1.1 可靠性面。[VERIFIED: codebase grep][ASSUMED] |

**Installation:**
```bash
# 本阶段无必须新增的 repo 内依赖；沿用现有 Python 脚本与外部 CLI。
# 运行前只需确认 python / gh / vercel / hermes / claude 已可用。
```

**Version verification:** Python 3.11.15、`gh` 2.91.0、Vercel CLI 53.0.1、Hermes Agent 0.10.0、Claude Code 2.1.126 已在本机验证可执行。[VERIFIED: local runtime]

## Architecture Patterns

### System Architecture Diagram

```text
Chat approval event
  -> Phase 22 persisted chat-origin metadata [ASSUMED]
  -> enqueue authority record path for approved project [ASSUMED]
  -> approved-delivery orchestrator shim
  -> start_approved_project_delivery.py
  -> APPROVED_PROJECT.json + approved-delivery-events.jsonl
  -> specialist stages (design -> development -> testing -> git_versioning -> release_readiness)
  -> GitHub repository + sync
  -> Vercel linkage + deploy
  -> render_approved_delivery_status.py / FINAL_OPERATOR_REVIEW.md
  -> validate_approved_delivery_pipeline.py
  -> final chat notifier
  -> Discord/Telegram reply in original thread/topic
```

### Recommended Project Structure
```text
scripts/
├── start_approved_project_delivery.py   # 既有唯一交付状态机
├── render_approved_delivery_status.py   # 既有状态/最终 review 渲染
├── validate_approved_delivery_pipeline.py # 既有真相一致性校验
├── start_delivery_run.py                # 既有 specialist 阶段清单
├── chat_approved_delivery_autorun.py    # 建议新增：审批后自治推进薄编排层 [ASSUMED]
└── chat_final_delivery_notify.py        # 建议新增：读取 persisted truth 并回帖 [ASSUMED]
```

### Pattern 1: Authority-Driven Stage Advancement
**What:** 每次推进都读写同一个 authority record + append-only 事件流，并在每个关键跃迁后渲染状态面。[VERIFIED: codebase grep]  
**When to use:** 任何审批后自治推进、恢复重试、最终 handoff 快照场景。[VERIFIED: codebase grep]  
**Example:**
```python
# Source: scripts/start_approved_project_delivery.py
result = start_approved_project_delivery(authority_path)
if result.get("ok") and result.get("stage") != "handoff":
    result = resume_approved_project_delivery(authority_path)
if result.get("ok") and result.get("stage") == "handoff":
    result = finalize_delivery_handoff(authority_path)
```
[VERIFIED: codebase grep]

### Pattern 2: Final Chat Reply Derived From Persisted Truth
**What:** 先读取 `APPROVED_PROJECT.json`、`approved-delivery-events.jsonl`、`DELIVERY_PIPELINE_STATUS.md`、`FINAL_OPERATOR_REVIEW.md`，再渲染一条面向聊天的 success/blocked 消息。[VERIFIED: codebase grep][ASSUMED]  
**When to use:** 完成回链、阻塞回链、恢复后再次回链。[VERIFIED: codebase grep][ASSUMED]  
**Example:**
```python
# Source: recommended Phase 25 pattern
record = load_json(authority_path)
status_md = Path(project_dir / "DELIVERY_PIPELINE_STATUS.md").read_text(encoding="utf-8")
final_review_md = Path(project_dir / "FINAL_OPERATOR_REVIEW.md").read_text(encoding="utf-8")
deploy_url = record.get("shipping", {}).get("vercel", {}).get("deploy_url", "")
blocked_reason = record.get("pipeline", {}).get("block_reason")
```
[VERIFIED: codebase grep][ASSUMED]

### Pattern 3: Thin Notifier, No Hidden State
**What:** 聊天通知层只消费已持久化的 authority truth，不保留独立状态机或“通知已成功”的内存真相。[VERIFIED: codebase grep][ASSUMED]  
**When to use:** 设计 Discord/Telegram adapter、重放最终通知、异常恢复后补发。[ASSUMED]  
**Example:**
```python
# Source: recommended Phase 25 pattern
if record["pipeline"]["status"] == "completed":
    send_success_reply(...)
else:
    send_blocked_reply(...)
```
[ASSUMED]

### Anti-Patterns to Avoid
- **第二套交付 runner：** 新建 chat-only pipeline 会复制 `PIPELINE_STAGES`、阻塞原因和恢复逻辑，极易产生 authority drift。[VERIFIED: codebase grep]
- **在通过 validator 前发送“成功”消息：** 现有模型要求 status/review/handoff 一致；绕过 validator 会破坏 D-03/D-09。[VERIFIED: codebase grep][ASSUMED]
- **用 orchestrator 生成假专家总结：** 现有 UI artifact、structured evidence、transcript、testing verification evidence 都是硬门禁。[VERIFIED: codebase grep]
- **把聊天线程 ID 仅保存在进程内存：** Phase 25 最终回帖依赖可恢复来源元数据；若不持久化，失败恢复后无法可靠回帖。[ASSUMED]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| 交付阶段状态机 | 新 YAML/JSON workflow engine | 既有 `start_approved_project_delivery.py` + authority/event model | 现有脚本已处理健康路径、阻塞、恢复、handoff、渲染和验证。[VERIFIED: codebase grep] |
| 专家产物证明 | 自定义“AI summary passed”布尔标志 | 既有 UI artifact、stage evidence、workspace inventory、product proof 门禁 | 这些门禁已被 runtime + validator 双重覆盖。[VERIFIED: codebase grep] |
| 最终交付摘要 | 从 stdout/stderr 拼临时 markdown | `FINAL_DELIVERY.md`、`DELIVERY_PIPELINE_STATUS.md`、`FINAL_OPERATOR_REVIEW.md` | D-07/D-09 要求最终消息源自权威产物。[VERIFIED: codebase grep] |
| GitHub/Vercel 发版 | 在本阶段重写 API 客户端 | 既有 `gh` / `vercel` CLI 集成 | 可靠性问题已在前序里修过，本阶段不应重开战场。[VERIFIED: codebase grep][ASSUMED] |

**Key insight:** Phase 25 是“现有 delivery backbone 的自动触发与最终通知编排”，不是“重建 delivery backbone”。[VERIFIED: codebase grep]

## Common Pitfalls

### Pitfall 1: 把“自治化”理解成“无证明直通”
**What goes wrong:** orchestration 直接推进到下阶段或直接宣布完成，但缺少 UI artifact、structured evidence、testing verification、product proof 之一。[VERIFIED: codebase grep]  
**Why it happens:** 误把健康路径自动推进当成跳过门禁。[VERIFIED: codebase grep]  
**How to avoid:** 所有推进继续走现有 `run_pipeline_from_stage()` 与 validator；聊天回执仅消费 validator 通过后的持久化真相。[VERIFIED: codebase grep][ASSUMED]  
**Warning signs:** `block_reason` 为空但 artifact 缺失，或最终消息里没有 status/review/handoff 回链。[VERIFIED: codebase grep][ASSUMED]

### Pitfall 2: 重新引入 authority drift
**What goes wrong:** 聊天编排层维护了自己的当前阶段/阻塞原因，导致与 `APPROVED_PROJECT.json` 或最后一条 blocked event 不一致。[VERIFIED: codebase grep]  
**Why it happens:** 新代码在 authority 外记录“通知状态”或“当前进度”。[ASSUMED]  
**How to avoid:** 最终通知层只存最小幂等发送标记，且该标记必须引用 authority path / event id，而不是复制业务状态。[ASSUMED]  
**Warning signs:** 类似 `authority_state_drift` 的恢复阻塞再次出现，或聊天说完成但 status surface 仍是 blocked。[VERIFIED: codebase grep][ASSUMED]

### Pitfall 3: 成功消息从临时内存渲染
**What goes wrong:** worker 在 Vercel deploy 成功后立即发消息，但 `FINAL_DELIVERY.md` / final review 尚未落盘或验证，导致回帖和权威工件不一致。[VERIFIED: codebase grep][ASSUMED]  
**Why it happens:** 把 deploy 成功误当成 handoff 完成。[VERIFIED: codebase grep]  
**How to avoid:** 以 `finalize_delivery_handoff()` 完成并生成 authority-level `FINAL_DELIVERY.md` 快照作为聊天 success 的前置条件。[VERIFIED: codebase grep]  
**Warning signs:** 聊天里有 deploy URL，但 approved project 目录没有 `FINAL_DELIVERY.md` 快照或 `pipeline.stage` 不是 `handoff` completed。[VERIFIED: codebase grep]

### Pitfall 4: 聊天线程定位模型不完整
**What goes wrong:** 只保存平台名和 channel id，未保存 thread/topic/message context，最终无法“返回原线程”。[ASSUMED]  
**Why it happens:** 把 Phase 22 来源元数据做得过薄。[ASSUMED]  
**How to avoid:** 对 Discord 至少持久化 channel/thread/message 引用；对 Telegram 至少持久化 chat_id、message id、必要时 message_thread_id。[CITED: https://discord.com/developers/docs/resources/message][CITED: https://core.telegram.org/bots/api#sendmessage][ASSUMED]  
**Warning signs:** 只能发到频道根部而非原话题，或失败恢复后丢失回复目标。[ASSUMED]

## Code Examples

Verified patterns from official/code sources:

### 继续使用既有交付入口
```python
# Source: scripts/start_approved_project_delivery.py
result = start_approved_project_delivery(authority_path)
result = resume_approved_project_delivery(authority_path)
result = finalize_delivery_handoff(authority_path)
```
[VERIFIED: codebase grep]

### Discord 最终回帖
```http
POST /channels/{channel.id}/messages
{
  "content": "Deployed: https://example.vercel.app",
  "message_reference": {
    "message_id": "1234567890"
  }
}
```
Source: Discord Message resource docs.[CITED: https://discord.com/developers/docs/resources/message]

### Telegram 最终回帖
```http
POST https://api.telegram.org/bot<TOKEN>/sendMessage
{
  "chat_id": -1001234567890,
  "text": "Deployed: https://example.vercel.app",
  "reply_parameters": { "message_id": 42 },
  "message_thread_id": 7
}
```
Source: Telegram Bot API `sendMessage`.[CITED: https://core.telegram.org/bots/api#sendmessage]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| 人工 `resume-approved-delivery` 驱动后续阶段 | 审批后健康路径默认自动推进，但仍复用同一恢复模型。[VERIFIED: codebase grep][ASSUMED] | v1.2 / Phase 25 目标。[VERIFIED: context file] | 减少人工触点，但不放松阻塞与恢复真相。[VERIFIED: context file] |
| 用“是否部署成功”代表整体成功 | 用 authority + events + status + final review + final handoff 收敛成功定义。[VERIFIED: codebase grep] | v1.1.1-v1.1.2 已形成现状。[VERIFIED: STATE.md][VERIFIED: README.md] | 聊天最终回执也必须遵守同一成功定义。[VERIFIED: codebase grep][ASSUMED] |

**Deprecated/outdated:**
- 手工从终端检查后再复制链接回聊天线程：这是 Phase 25 要消除的健康路径人工步骤，但异常恢复仍保留人工介入。[VERIFIED: requirements file][VERIFIED: context file]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Phase 22 将提供并持久化足够的聊天来源元数据（至少 platform + channel/chat + thread/topic/message 关联）供 Phase 25 回帖。 | Summary / Architecture Patterns / Pitfalls | 若没有这层元数据，Phase 25 无法可靠实现“返回原线程”。 |
| A2 | 需要新增一个薄的 autorun/notifier 编排层脚本，而不是仅靠现有 cron wrapper 即可无改动满足需求。 | Recommended Project Structure | 若现有入口已足够，则计划会多做一层不必要代码。 |
| A3 | 最终聊天成功消息应在 `validate_approved_delivery_pipeline.py` 通过后发送，而不是在 `vercel_deploy` 成功时立即发送。 | Patterns / Pitfalls | 若产品故意接受更早发送，当前建议会延后通知时机。 |
| A4 | 聊天通知层最多只应持久化幂等发送标记，而不应维护独立业务状态。 | Pitfalls | 若现有聊天基础设施强制需要更厚状态模型，规划需额外设计同步策略。 |

## Open Questions

1. **Phase 22 最终会把哪些聊天来源字段写入权威产物？**  
What we know: 需求要求记录 source channel/thread/requester/message intent，但当前仓库还没有可见的 Discord/Telegram runtime 实现。[VERIFIED: requirements file][VERIFIED: codebase grep]  
What's unclear: 精确字段名、落盘位置、是否包含 Discord thread id 与 Telegram topic/message_thread_id。[ASSUMED]  
Recommendation: 计划阶段先锁定一个 `chat_origin` 权威结构，再让 Phase 25 只消费该结构，不反向发明字段。[ASSUMED]

2. **自治推进采用什么触发机制最合适？**  
What we know: CONTEXT 允许 scheduler/polling 机制自由选择，但必须保持权威状态跃迁。[VERIFIED: context file]  
What's unclear: 是在 chat approval handler 内同步触发首轮推进，还是写入队列由独立 worker/poller 消费。[ASSUMED]  
Recommendation: 优先用“approval handler 只 enqueue，后台 worker 负责 start/resume/finalize”的幂等模型，避免聊天请求线程持有长任务。[ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | 核心脚本与测试 | ✓ | 3.11.15 | — |
| GitHub CLI `gh` | GitHub repository/sync stages | ✓ | 2.91.0 | 已支持 token/auth session；无更优本阶段 fallback。[VERIFIED: README.md][VERIFIED: local runtime] |
| Vercel CLI | Vercel linkage/deploy stages | ✓ | 53.0.1 | 已支持 token/auth session；无更优本阶段 fallback。[VERIFIED: README.md][VERIFIED: local runtime] |
| Hermes CLI | specialist dispatch | ✓ | 0.10.0 | 无；缺失将阻塞真实 specialist output。[VERIFIED: local runtime][VERIFIED: codebase grep] |
| Claude Code CLI | transcript/agent execution path | ✓ | 2.1.126 | 无；缺失将破坏既有证据链。[VERIFIED: local runtime][VERIFIED: codebase grep] |
| Discord API credentials | 最终 Discord 回帖 | 未验证 | — | 可先只规划接口；实现时若缺失则以 blocked notification path 记录。[ASSUMED] |
| Telegram Bot token | 最终 Telegram 回帖 | 未验证 | — | 可先只规划接口；实现时若缺失则以 blocked notification path 记录。[ASSUMED] |

**Missing dependencies with no fallback:**
- 如果目标 run 来自 Discord/Telegram，但没有对应 bot credentials 或来源元数据，AUTO-04 无法真实闭环。[ASSUMED]

**Missing dependencies with fallback:**
- 无明显安全 fallback；“人工复制链接回帖”不满足本阶段 success criteria，只能作为异常恢复说明，不应视为 Phase 25 成功实现。[VERIFIED: requirements file][ASSUMED]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Python `unittest`（repo 现状）。[VERIFIED: codebase grep] |
| Config file | none。[VERIFIED: codebase grep] |
| Quick run command | `python -m unittest tests.test_project_delivery_pipeline_bootstrap tests.test_project_delivery_pipeline_resume tests.test_approved_delivery_pipeline_cli` |
| Full suite command | `python -m unittest discover -s tests -p \"test_*.py\"` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| AUTO-02 | 审批后健康路径自动推进，且恢复仍复用同一 authority truth。 | unit/integration | `python -m unittest tests.test_project_delivery_pipeline_bootstrap tests.test_project_delivery_pipeline_resume -x` | ✅ |
| AUTO-03 | UI artifact、transcript、structured evidence、testing verification、product proof 继续作为强门禁。 | unit | `python -m unittest tests.test_approved_delivery_pipeline_cli -x` | ✅ |
| AUTO-04 | 完成或阻塞后向原聊天线程发送最终消息，且内容来自 persisted truth。 | unit/integration | `python -m unittest tests.test_chat_delivery_notifications -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m unittest tests.test_project_delivery_pipeline_bootstrap tests.test_project_delivery_pipeline_resume tests.test_approved_delivery_pipeline_cli`
- **Per wave merge:** `python -m unittest discover -s tests -p "test_*.py"`
- **Phase gate:** Full suite green，且新增聊天通知测试覆盖 success + blocked + retry/idempotency。[ASSUMED]

### Wave 0 Gaps
- [ ] `tests/test_chat_delivery_notifications.py` — 覆盖 Discord success reply、Discord blocked reply、Telegram success reply、Telegram blocked reply、重复触发幂等保护。[ASSUMED]
- [ ] `tests/test_chat_origin_contract.py` — 锁定 Phase 22 输出的 `chat_origin` authority schema，防止字段漂移破坏 Phase 25。[ASSUMED]
- [ ] 聊天回帖渲染函数测试夹具：completed handoff / blocked prerequisite / authority drift / validator-failed 各一组 fixture。[ASSUMED]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Discord/Telegram bot token、`gh`/Vercel 登录会话、Hermes/Claude 本地凭证均必须沿用现有本地配置，不写入 repo。[VERIFIED: README.md][ASSUMED] |
| V3 Session Management | no | 本阶段无新增用户会话面；仅消费已有 CLI 会话。[VERIFIED: README.md][ASSUMED] |
| V4 Access Control | yes | 最终聊天回帖只能写回已持久化的原始 channel/thread/chat/topic，不允许任意目标覆写。[ASSUMED] |
| V5 Input Validation | yes | 对 authority path、chat origin metadata、deploy URL、blocked reason、artifact links 做严格非空/格式校验；沿用现有 block-on-missing 原则。[VERIFIED: codebase grep][ASSUMED] |
| V6 Cryptography | no | 本阶段不应新增自研加密；沿用现有平台 token/CLI 凭证体系。[VERIFIED: README.md][ASSUMED] |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| 伪造成功通知 | Spoofing | 仅从 `pipeline.status=completed` 且 final handoff/status/review 已落盘的 authority truth 发送 success reply。[VERIFIED: codebase grep][ASSUMED] |
| 错线程回帖 | Tampering | 持久化并校验 chat origin metadata；发送前比对 run 绑定来源，不接受外部覆盖目标线程。[ASSUMED] |
| 凭证泄漏到工件 | Information Disclosure | 聊天摘要只暴露 deploy URL、工件路径和阻塞原因，不回显 token、env 值或 CLI 原始 stderr 全量内容。[VERIFIED: README.md][ASSUMED] |
| 重复发送/多次回帖 | Repudiation | 用 authority-linked idempotency marker 记录最后一次已发送终态事件，重复消费时短路。[ASSUMED] |

## Sources

### Primary (HIGH confidence)
- Local codebase grep/read - `scripts/start_approved_project_delivery.py`, `scripts/render_approved_delivery_status.py`, `scripts/validate_approved_delivery_pipeline.py`, `tests/test_project_delivery_pipeline_bootstrap.py`, `tests/test_project_delivery_pipeline_resume.py`, `tests/test_approved_delivery_pipeline_cli.py`
- Local project docs - `.planning/phases/25-autonomous-delivery-to-deploy-and-return-link/25-CONTEXT.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md`, `.planning/ROADMAP.md`, `README.md`
- Local runtime probes - `python --version`, `gh --version`, `vercel --version`, `hermes --version`, `claude --version`

### Secondary (MEDIUM confidence)
- GitHub CLI manual - https://cli.github.com/manual/gh_auth_status
- Vercel CLI deploy docs - https://vercel.com/docs/cli/deploy
- Discord developer docs, Message resource - https://discord.com/developers/docs/resources/message
- Telegram Bot API, `sendMessage` - https://core.telegram.org/bots/api#sendmessage

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - 主要依赖现有代码与本机运行时，证据直接可见。[VERIFIED: codebase grep][VERIFIED: local runtime]
- Architecture: MEDIUM - “薄编排层 + 最终通知层”方向强，但具体 queue/poller 机制仍由 planner 决定。[VERIFIED: context file][ASSUMED]
- Pitfalls: MEDIUM - 大部分来自现有 authority/recovery 设计与聊天接缝推演，聊天接缝本身仍待实现验证。[VERIFIED: codebase grep][ASSUMED]

**Research date:** 2026-05-04  
**Valid until:** 2026-06-03
