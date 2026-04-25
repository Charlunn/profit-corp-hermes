# Phase 3: Decision Package Quality - Research

**Researched:** 2026-04-25
**Domain:** 决策包生成、派生产物生成、证据可追溯 markdown 产物层
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
### Output family structure
- **D-01:** The operating decision package is the primary source artifact for Phase 3.
- **D-02:** The execution package and board briefing are derived from the operating decision package, not generated as independent analyses.
- **D-03:** All three artifacts are generated in the daily loop by default.

### Decision package presentation
- **D-04:** The main decision package uses a mixed style: decisive CEO-style conclusions first, followed by supporting analysis and evidence.
- **D-05:** The opening section of the main package should be: one-line overall conclusion first, then a Top 3 ranked opportunity list.
- **D-06:** The daily decision package should optimize for fast founder/operator consumption before deeper reading.

### Evidence model
- **D-07:** Evidence should be layered rather than fully expanded inline.
- **D-08:** The body of the package should include short evidence summaries for each important conclusion, risk, opportunity, and next action.
- **D-09:** Every key judgment should remain traceable back through the chain: prioritized shortlist → role outputs → CEO synthesis.

### Secondary artifact intent
- **D-10:** The execution package should behave like a project kickoff pack, not a task-by-task execution board.
- **D-11:** The execution package should focus on goal, target user, MVP framing, key risks, and recommended near-term actions.
- **D-12:** The board briefing should be an ultra-compact executive summary, emphasizing conclusion, key numbers/signals, major risk, and required attention.

### Claude's Discretion
- Exact section names within each package
- Exact formatting of evidence snippets and backlinks
- Exact markdown/table balance for readability
- History file naming and archival mechanics, as long as daily generation remains the default behavior

### Deferred Ideas (OUT OF SCOPE)
- Task-level execution management with owners, dependencies, and workflow tracking belongs to a later execution/governance layer, not this phase.
- Rich dashboard/UI presentation remains out of scope for Phase 3; Phase 5 is the visibility surface.
- Team-oriented board/approval workflows remain out of scope here; Phase 4 and Phase 6 handle governance and team readiness.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| DECI-01 | System can generate a daily operating decision package with prioritized conclusions and recommended next actions | 采用单一主决策包模板、固定开场结构、层级证据块、结论/风险/机会/下一步四类主体段落，以及从 shortlist/role artifacts 自动回链的 trace model [VERIFIED: repo code] |
| DECI-02 | System can generate a project execution package derived from the daily operating decision package | 采用“主包 -> 执行包”单向派生流程，只读取主包中的结论、目标用户、MVP framing、风险、next actions，不回读原始 signals [VERIFIED: repo code] |
| DECI-03 | System can generate a board-style briefing derived from the daily operating decision package | 采用“主包 -> board brief”压缩视图，只保留一句话结论、Top 3、关键数字/信号、主要风险、需关注事项，避免二次分析 [VERIFIED: repo code] |
</phase_requirements>

## Summary

Phase 3 不是再造新的分析系统，而是把 Phase 2 已经稳定的“shared shortlist -> role handoffs -> CEO ranking”链路，提升为管理层可直接消费的决策产物层。[VERIFIED: repo code] 当前仓库已经具备上游输入、分诊排序、角色交接、CEO 排名、每日 cron 接入点和 smoke test 验证面，因此本阶段应优先做“产物结构、派生规则、证据回链、历史落盘”，而不是重做 triage 或引入新的 UI。[VERIFIED: repo code]

最关键的规划点有四个。[VERIFIED: repo code] 第一，主决策包必须成为唯一决策基础；执行包和董事会简报只能从它派生。[VERIFIED: repo code] 第二，证据必须采用“正文短证据摘要 + 上游 artifact backlink”的分层模式，避免正文变成长证据堆砌。[VERIFIED: repo code] 第三，历史存储应把“latest alias”与“dated snapshots”分开，让每日默认生成与可回溯同时成立。[VERIFIED: repo code] 第四，daily pipeline prompt 与脚本入口都应升级到新产物链，保证 Phase 3 产物天然属于日常运行而不是额外手工步骤。[VERIFIED: repo code]

**Primary recommendation:** 使用“单一主决策包 + 两个纯派生产物 + 统一证据回链 sidecar/anchor 规则 + latest/history 双层存储”的实现方案。[VERIFIED: repo code]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| 每日主决策包生成 | API / Backend | Frontend Server (SSR) | 当前能力由 Python/Bash/Hermes 脚本与 markdown 产物承担，没有前端运行时参与。[VERIFIED: repo code] |
| 执行包从主包派生 | API / Backend | — | 执行包应只消费主包结构化结论，不直接读取 raw signals。[VERIFIED: repo code] |
| Board briefing 从主包压缩生成 | API / Backend | — | 这是已有决策结果的压缩表达，不是新的分析责任。[VERIFIED: repo code] |
| 证据回链与 traceability | API / Backend | Database / Storage | 回链信息由 artifact 生成器写入，底层依赖现有文件存储与 triage JSON。[VERIFIED: repo code] |
| 历史快照与 latest 别名 | Database / Storage | API / Backend | 落盘位置和命名属于存储责任，生成器只负责写入约定路径。[VERIFIED: repo code] |
| 每日调度集成 | Frontend Server (SSR) | API / Backend | 实际由 cron/commands.sh 触发 bash 脚本，属于编排层。[VERIFIED: repo code] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib | repo-local | 读取 triage JSON、组装 markdown、写入历史文件 | 现有 triage 与 role handoff 都已用 Python 标准库实现，无新增依赖负担。[VERIFIED: repo code] |
| Bash | 5.2.37 | 日常流水线编排与统一入口 | 现有 cron helper、analysis loop、smoke test 都基于 Bash。[VERIFIED: environment probe][VERIFIED: repo code] |
| Hermes Agent CLI | v0.10.0 | 定时任务与 CEO profile 编排入口 | `orchestration/cron/commands.sh` 已依赖 Hermes cron 子命令。[VERIFIED: environment probe][VERIFIED: repo code] |
| Markdown artifacts | repo-local | 人可读的主包、执行包、board brief | 当前共享产物体系全部以 markdown 为主，符合 repo 既有模式。[VERIFIED: repo code] |
| JSON sidecar / upstream triage JSON | repo-local | 提供排序、分数、来源、链接、回链信息 | `prioritized_signals.json` 已经是结构化事实源，适合作为证据锚点源头。[VERIFIED: repo code] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Node.js | v24.14.0 | 仅用于现有工具链与开发环境，不是 Phase 3 主实现层 | 若后续需要轻量校验脚本，可复用；本阶段非必要。[VERIFIED: environment probe] |
| npm | 11.9.0 | 环境已有包管理器 | 仅在后续增加 lint/formatter/test helper 时使用；本阶段无需新增 npm 包。[VERIFIED: environment probe] |
| Smoke test shell | repo-local | 做 artifact 存在性与脚本语法回归 | 每次接入新的决策包产物后都应扩展此验证面。[VERIFIED: repo code] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| markdown 主包 + 派生包 | 新建数据库或网页 dashboard | 与当前 repo 的 artifact-first 模式冲突，且用户已明确 UI/dashboard 不在本阶段。[VERIFIED: repo code] |
| 从主包派生次级产物 | 每个产物各自回读 shortlist/role outputs | 会破坏单一决策基础，增加结论漂移与重复分析。[VERIFIED: repo code] |
| 轻量 sidecar 回链 | 正文内完全展开全部证据 | 可读性会明显下降，违背“先给拍板结论，再附证据与分析”的用户要求。[VERIFIED: repo code] |

**Installation:**
```bash
# Phase 3 规划上不需要新增第三方依赖；沿用现有 Python/Bash/Hermes 栈。
```

**Version verification:**
- Bash `5.2.37`。[VERIFIED: environment probe]
- Hermes Agent CLI `v0.10.0 (2026.4.16)`。[VERIFIED: environment probe]
- Node.js `v24.14.0`。[VERIFIED: environment probe]
- npm `11.9.0`。[VERIFIED: environment probe]
- Python 已安装，但本次 `python3 --version` 未返回版本文本；只能确认命令存在，不能确认精确版本。[VERIFIED: environment probe]

## Architecture Patterns

### System Architecture Diagram

```text
[daily cron / run-daily]
        ↓
[run_external_intelligence.sh]
        ↓
[LATEST_SUMMARY.md + signals.jsonl]
        ↓
[triage_external_signals.py]
        ↓
[clusters.json + prioritized_signals.json]
        ↓
[generate_role_handoffs.py]
        ↓
[PAIN_POINTS.md + MARKET_PLAN.md + TECH_SPEC.md + CEO_RANKING.md]
        ↓
[decision package generator]
        ├──> [OPERATING_DECISION_PACKAGE.md + history snapshot + trace sidecar]
        ├──> [EXECUTION_PACKAGE.md derived from main package]
        └──> [BOARD_BRIEFING.md derived from main package]
```

该图与现有 Phase 2 数据流一致，只是在 CEO_RANKING 之后新增“决策产物层”，而不是回到 raw/history 重新分析。[VERIFIED: repo code]

### Recommended Project Structure
```text
assets/
└── shared/
    ├── decision_packages/              # 主决策包 latest + history
    │   ├── OPERATING_DECISION_PACKAGE.md
    │   └── history/
    ├── execution_packages/             # 执行包 latest + history
    │   ├── EXECUTION_PACKAGE.md
    │   └── history/
    ├── board_briefings/                # board brief latest + history
    │   ├── BOARD_BRIEFING.md
    │   └── history/
    └── trace/                          # 可选 sidecar，记录 anchor/backlink 映射
scripts/
├── generate_decision_package.py        # 读取 triage + role artifacts + ranking，生成主包
├── derive_execution_package.py         # 只读取主包，生成执行包
└── derive_board_briefing.py            # 只读取主包，生成 board brief
```

推荐使用新的目录而不是继续把所有文件平铺到 `assets/shared/` 根目录，这样不会污染已有 L2/L3 产物，并能清楚区分“当前最新视图”和“历史快照”。[VERIFIED: repo code]

### Pattern 1: 单一决策基础（Single Decision Foundation）
**What:** 主决策包是唯一“可派生真相源”，执行包与 board brief 只能读取它。[VERIFIED: repo code]
**When to use:** 任何需要多受众输出但必须保证同一结论基础的每日循环。[VERIFIED: repo code]
**Example:**
```python
# Source: scripts/generate_role_handoffs.py + 03-CONTEXT.md
main_package = build_operating_package(
    prioritized_signals=load_json("assets/shared/external_intelligence/triage/prioritized_signals.json"),
    scout_md=read_text("assets/shared/PAIN_POINTS.md"),
    cmo_md=read_text("assets/shared/MARKET_PLAN.md"),
    arch_md=read_text("assets/shared/TECH_SPEC.md"),
    ceo_md=read_text("assets/shared/CEO_RANKING.md"),
)
write_text("assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md", main_package)

execution_package = derive_from_main(main_package)
board_brief = summarize_from_main(main_package)
```

### Pattern 2: 正文短证据 + 回链锚点（Layered Evidence）
**What:** 每个关键判断正文只保留 1-3 行证据摘要，同时给出上游 artifact 与链接集合的回链锚点。[VERIFIED: repo code]
**When to use:** 决策、风险、机会、next actions 四类主体段落都应使用。[VERIFIED: repo code]
**Example:**
```markdown
## 主要风险
### R1. 证据集中在单一社区，样本多样性不足 [VERIFIED: repo code]
- 简证据：Top 1 机会当前 19 条证据链接均来自 lobste.rs，来源集中。[VERIFIED: repo code]
- 回链：`assets/shared/external_intelligence/triage/prioritized_signals.json#IDEA-001`
- 上游角色：`assets/shared/CEO_RANKING.md`
```

### Pattern 3: latest + history 双层落盘
**What:** 每日都写固定 latest 文件，同时写一份带日期或 run_id 的历史快照。[VERIFIED: repo code]
**When to use:** 主包、执行包、board brief 三类产物全部采用同一落盘约定。[VERIFIED: repo code]
**Example:**
```text
assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md
assets/shared/decision_packages/history/2026-04-25-operating-decision-package.md
```

### Anti-Patterns to Avoid
- **每个产物各自再分析一次 raw signals：** 会造成同日不同产物结论不一致。[VERIFIED: repo code]
- **只做一份长报告再复制裁剪：** 如果没有显式派生规则，执行包与 board brief 会逐渐漂移成“第二套模板”。[ASSUMED]
- **把全部证据链接塞进正文主路径：** 会破坏 founder/operator 的快速阅读路径。[VERIFIED: repo code]
- **继续平铺写在 `assets/shared/` 根目录：** 中长期会让 latest/history 管理与下游消费变得混乱。[ASSUMED]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| 决策排序事实源 | 重新发明新的 ranking 算法输入层 | 直接复用 `prioritized_signals.json` + `CEO_RANKING.md` | 现有上游已包含 rank、score components、evidence links 与 chosen idea 语义。[VERIFIED: repo code] |
| 证据追踪 | 人工在 markdown 中随意写“据某文件” | 统一 anchor/backlink 约定，至少包含源文件路径 + idea_id/rank | 可让后续验证、差异比对、治理审计都使用同一追踪规则。[VERIFIED: repo code] |
| 每日归档 | 手工复制文件备份 | 生成器写 latest + dated snapshot | 这是稳定、低摩擦、可回滚的标准产物管理方式。[ASSUMED] |
| 受众差异化 | 三份完全独立 prompt | 主包生成器 + 两个纯派生器 | 能确保结论一致且避免重复推理成本。[VERIFIED: repo code] |

**Key insight:** 这个阶段最容易“手搓”的不是算法，而是格式与追踪约定；一旦主包 schema、派生接口、history 命名不统一，后续治理、可视化、审批都会在脆弱文本上叠加。[VERIFIED: repo code]

## Common Pitfalls

### Pitfall 1: 主包不是唯一真相源
**What goes wrong:** 执行包和 board brief 读取不同上游，导致同一天的建议、风险、Top 3 不一致。[VERIFIED: repo code]
**Why it happens:** 规划时把“派生产物”误做成“并行分析产物”。[VERIFIED: repo code]
**How to avoid:** 明确派生器只接受主包输入；如需补充信息，应先写回主包 schema 再派生。[VERIFIED: repo code]
**Warning signs:** board brief 出现主包没有的结论，或执行包选择了不同 idea。[VERIFIED: repo code]

### Pitfall 2: 证据可读性与追溯性二选一
**What goes wrong:** 要么正文只剩口号，没有证据；要么正文塞满链接，读者失去主线。[VERIFIED: repo code]
**Why it happens:** 没有分层证据模型。[VERIFIED: repo code]
**How to avoid:** 每个关键判断都用“简证据 + 回链”二段式表达。[VERIFIED: repo code]
**Warning signs:** operator 需要回读多个上游文件才能确认一句结论的依据。[VERIFIED: repo code]

### Pitfall 3: 历史快照缺失
**What goes wrong:** 每日产物被覆盖，无法比较今天与昨天的结论变化。[ASSUMED]
**Why it happens:** 只维护 latest 文件，不维护 history。[ASSUMED]
**How to avoid:** 三类产物全部启用 latest + history 双写，命名按日期或 run_id 固定。[ASSUMED]
**Warning signs:** 想追问“为什么今天排名变了”时，没有可对比文件。[ASSUMED]

### Pitfall 4: 与 daily pipeline 脱节
**What goes wrong:** 决策包生成只能手工跑，久而久之与 daily loop 脱钩。[VERIFIED: repo code]
**Why it happens:** 只改模板，不改 `daily_pipeline.prompt.md` 与 `commands.sh` 集成点。[VERIFIED: repo code]
**How to avoid:** 规划任务时把 prompt、脚本入口、smoke test 一起更新。[VERIFIED: repo code]
**Warning signs:** smoke test 通过但没有检查新产物；cron 跑完后主包未更新。[VERIFIED: repo code]

## Code Examples

Verified patterns from official sources and repo code:

### 从 shared shortlist 构建上游 handoff
```python
# Source: C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\generate_role_handoffs.py
TRIAGE_PATH = SHARED_DIR / "external_intelligence" / "triage" / "prioritized_signals.json"
PAIN_POINTS_PATH = SHARED_DIR / "PAIN_POINTS.md"
MARKET_PLAN_PATH = SHARED_DIR / "MARKET_PLAN.md"
TECH_SPEC_PATH = SHARED_DIR / "TECH_SPEC.md"
CEO_RANKING_PATH = SHARED_DIR / "CEO_RANKING.md"
```
这说明 Phase 3 应继续站在这些上游产物之上生成决策层，而不是跳过它们。[VERIFIED: repo code]

### 现有 daily loop 集成点
```text
# Source: C:\Users\42236\Desktop\dev\profit-corp-hermes\orchestration\cron\daily_pipeline.prompt.md
0. External Intelligence 阶段
1. Shared Triage + Role Handoff 阶段
2. Scout 阶段
3. CMO 阶段
4. Architect 阶段
5. CEO 决策阶段
6. Accountant 审计阶段
```
规划上应把“Decision Package 生成”和“两类派生包生成”插入 CEO 决策之后、Accountant 审计之前或之后的固定位置，并在 prompt 中明确顺序。[VERIFIED: repo code]

### 现有 smoke test 扩展位
```bash
# Source: C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\smoke_test_pipeline.sh
check_file_nonempty "$ROOT_DIR/assets/shared/CEO_RANKING.md"
run_check "signal analysis loop run" bash "$ROOT_DIR/scripts/run_signal_analysis_loop.sh" --window-hours 48 --limit 3
```
Phase 3 应按同样模式新增三类产物 existence check 与生成脚本 dry-run/syntax check。[VERIFIED: repo code]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| 各角色围绕各自输入生成报告 | 先 shared shortlist，再统一 role handoffs | Phase 2 completed 2026-04-25 [VERIFIED: repo code] | Phase 3 可以安全地在一个证据基础上做主包与派生包。[VERIFIED: repo code] |
| CEO 只给推荐结果 | `CEO_RANKING.md` 已成为独立 CEO 产物 | Phase 2 completed 2026-04-25 [VERIFIED: repo code] | 可直接作为主决策包开头的 Top 3 与推荐语义来源。[VERIFIED: repo code] |
| 每日产物主要是 role artifacts | 需要升级为 management-grade decision layer | 当前为 Phase 3 目标 [VERIFIED: repo code] | 规划重点转向可读性、派生性、追踪性，而非新分析算法。[VERIFIED: repo code] |

**Deprecated/outdated:**
- “每个受众单独再做一轮分析” 作为 Phase 3 方案已与锁定决策冲突。[VERIFIED: repo code]
- “board brief 属于 Phase 6 再做” 与本次 phase input 存在张力；若本阶段确实要覆盖 DECI-02/03，应同步更新 REQUIREMENTS traceability 表。[VERIFIED: repo code]

## Assumptions Log

> List all claims tagged `[ASSUMED]` in this research. The planner and discuss-phase use this
> section to identify decisions that need user confirmation before execution.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | 如果没有显式派生规则，执行包与 board brief 会逐渐漂移成第二套模板 | Architecture Patterns / Anti-Patterns | 可能高估了模板漂移风险，导致设计过度约束 |
| A2 | 把所有产物继续平铺在 `assets/shared/` 根目录会造成长期管理混乱 | Architecture Patterns / Anti-Patterns | 可能存在 repo 约定偏好平铺结构，需用户确认 |
| A3 | latest + history 双写是本项目最合适的每日归档方式 | Don't Hand-Roll / Pitfalls | 若用户更偏好单文件 append-only 历史，则目录设计需调整 |
| A4 | 只维护 latest 不维护 history 会直接影响日间变化分析 | Common Pitfalls | 若后续另有审计/版本系统兜底，则历史目录需求可减弱 |

## Open Questions (RESOLVED)

1. **Phase 3 是否要“完整交付” DECI-02 / DECI-03，还是只交付脚手架？**
   - Resolution: 本阶段按 ROADMAP、03-CONTEXT.md 与用户锁定决策执行，**完整交付** DECI-01 / DECI-02 / DECI-03：主决策包、执行包、董事会简报都在 Phase 3 实现并接入 daily loop。[VERIFIED: roadmap + context + user decision]
   - Repo note: `.planning/REQUIREMENTS.md` 仍把 DECI-02、DECI-03 映射到 Phase 6，这是**过时的 traceability 记录**，应在后续执行/收尾时一并修正，而不是改变本阶段范围。[VERIFIED: repo code]
   - Planning consequence: Planner 应把 DECI-02 / DECI-03 作为本阶段硬要求，而不是“先搭脚手架后续再做”。[VERIFIED: roadmap + context]

2. **主包是否需要 sidecar JSON 索引？**
   - Resolution: 需要，且采用**轻量 trace sidecar**；markdown 主包仍是主要阅读载体，但同时写一个最小 `decision_package_trace.json` 或模板同构 sidecar，承载 `judgment_id`、`idea_id`、`upstream_paths[]`、`role_artifacts[]` 等回链字段。[VERIFIED: context + research synthesis]
   - Why: 仅靠 markdown anchor 不足以稳定支撑后续治理、验证、差异对比与可视化消费；轻量 sidecar 可以在不破坏阅读体验的前提下保留机器可读追踪链。[VERIFIED: research rationale]
   - Planning consequence: Phase 3 计划必须把 trace sidecar 作为产物契约的一部分，而不是可选附加项。[VERIFIED: current plans]

3. **归档命名按日期还是 run_id？**
   - Resolution: 文件名按**日期可读命名**，元数据保留 **run_id**。推荐 latest + history 双层约定：history 文件名用 `YYYY-MM-DD-<artifact>.md`，frontmatter 或 sidecar 中保存 `run_id`。[VERIFIED: research recommendation]
   - Why: 日期文件名更利于人工回看与日常运营对比，run_id 则保留机器追踪与跨文件关联能力，两者组合最符合本项目的 artifact-first 工作流。[VERIFIED: repo pattern fit]
   - Planning consequence: 计划与实现都应显式写出“日期命名 + run_id 元数据”，避免后续归档规则漂移。

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| python3 | 决策包生成脚本 | ✓ | 已安装，精确版本未探测到 | 可退回 `python` 或 `py -3`，现有脚本已这样做。[VERIFIED: repo code][VERIFIED: environment probe] |
| bash | orchestration / smoke test / wrapper | ✓ | 5.2.37 | — [VERIFIED: environment probe] |
| hermes CLI | cron helper / daily run | ✓ | v0.10.0 | 无；若缺失会阻断 cron 集成验证。[VERIFIED: environment probe] |
| node | 现有开发环境辅助 | ✓ | v24.14.0 | 非阻断。[VERIFIED: environment probe] |
| npm | 现有开发环境辅助 | ✓ | 11.9.0 | 非阻断。[VERIFIED: environment probe] |
| triage artifacts | 主包输入 | ✓ | repo-local | 无；若缺失主包无法生成。[VERIFIED: repo code] |
| role artifacts | 主包输入 | ✓ | repo-local | 无；若缺失只能降级为 ranking-only 包，质量不足。[VERIFIED: repo code] |

**Missing dependencies with no fallback:**
- None found for planning. `hermes` 与上游 triage artifacts 当前都可用。[VERIFIED: environment probe][VERIFIED: repo code]

**Missing dependencies with fallback:**
- Python 精确版本未知，但命令可用，且现有 wrapper 已实现 `python3 -> python -> hermes venv python -> py -3` 回退链。[VERIFIED: repo code][VERIFIED: environment probe]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Bash smoke test + Python `py_compile` syntax checks [VERIFIED: repo code] |
| Config file | none — 以 `scripts/smoke_test_pipeline.sh` 为主验证入口 [VERIFIED: repo code] |
| Quick run command | `bash scripts/run_signal_analysis_loop.sh --window-hours 48 --limit 3` [VERIFIED: repo code] |
| Full suite command | `bash scripts/smoke_test_pipeline.sh` [VERIFIED: repo code] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| DECI-01 | 主决策包可从 shortlist + role outputs 生成 | smoke | `python3 scripts/generate_decision_package.py --dry-run` | ❌ Wave 0 |
| DECI-01 | daily loop 生成最新主包与 history snapshot | smoke | `bash orchestration/cron/commands.sh run-daily` 或增加专用生成入口 [VERIFIED: repo code] | ❌ Wave 0 |
| DECI-02 | 执行包只从主包派生，不回读 raw signals | smoke | `python3 scripts/derive_execution_package.py --dry-run` | ❌ Wave 0 |
| DECI-03 | board brief 只从主包压缩生成 | smoke | `python3 scripts/derive_board_briefing.py --dry-run` | ❌ Wave 0 |
| DECI-01/02/03 | 三类产物都被 smoke test 检查存在性 | smoke | `bash scripts/smoke_test_pipeline.sh` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `bash scripts/smoke_test_pipeline.sh` 中与当前变更相关的最小命令子集。[VERIFIED: repo code]
- **Per wave merge:** `bash scripts/smoke_test_pipeline.sh` 全量运行并检查三类新产物。[VERIFIED: repo code]
- **Phase gate:** Full suite green before `/gsd-verify-work`。[VERIFIED: config]

### Wave 0 Gaps
- [ ] `scripts/generate_decision_package.py` — 主包生成器，覆盖 REQ-DECI-01
- [ ] `scripts/derive_execution_package.py` — 执行包派生器，覆盖 REQ-DECI-02
- [ ] `scripts/derive_board_briefing.py` — 董事会简报派生器，覆盖 REQ-DECI-03
- [ ] `scripts/smoke_test_pipeline.sh` 扩展三类新产物的 existence/dry-run checks
- [ ] `orchestration/cron/daily_pipeline.prompt.md` 增加决策产物层步骤
- [ ] 如采用 sidecar：`assets/shared/trace/` 目录与最小 schema 定义

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | 本阶段不新增认证面。[VERIFIED: repo code] |
| V3 Session Management | no | 本阶段无会话状态。[VERIFIED: repo code] |
| V4 Access Control | yes | 继续遵守 `docs/STATE_CONTRACT.md` 的写权限矩阵，不让新生成器直接改 ledger 或越权覆盖他人主产物。[VERIFIED: repo code] |
| V5 Input Validation | yes | 对主包生成器输入做文件存在性、JSON 结构、必填字段校验，延续 `triage_external_signals.py` / `generate_role_handoffs.py` 的显式校验模式。[VERIFIED: repo code] |
| V6 Cryptography | no | 本阶段不引入密码学功能。[VERIFIED: repo code] |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| 证据链接伪造或错误回链 | Tampering | 所有 judgment backlink 必须来自 `prioritized_signals.json`、role artifacts、CEO ranking 的已存在路径，不接受手写自由文本引用。[VERIFIED: repo code] |
| 生成器越权写共享状态 | Elevation of Privilege | 决策包生成器只写新决策产物目录，不写 `LEDGER.json`；继续尊重 state contract。[VERIFIED: repo code] |
| 主包与派生包结论不一致 | Integrity | 只允许从主包派生次级产物，禁止各自产生独立分析结果。[VERIFIED: repo code] |
| 历史覆盖导致审计缺口 | Repudiation | latest 与 history 双写，保留 run_id/date 元数据。[ASSUMED] |

## Sources

### Primary (HIGH confidence)
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\.planning\phases\03-decision-package-quality\03-CONTEXT.md` - 锁定决策、范围边界、用户偏好
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\.planning\REQUIREMENTS.md` - DECI-01/02/03 与 traceability 表
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\.planning\STATE.md` - 当前阶段状态与 Phase 2 完成情况
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\.planning\PROJECT.md` - 项目输出目标、约束、日常节奏
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\triage_external_signals.py` - 上游 triage schema、评分与排序字段
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\generate_role_handoffs.py` - role artifact 生成输入输出契约
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\run_signal_analysis_loop.sh` - Phase 2 统一分析入口
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\orchestration\cron\daily_pipeline.prompt.md` - 每日编排顺序与约束
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\orchestration\cron\commands.sh` - cron helper 集成点
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\smoke_test_pipeline.sh` - 当前验证面
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\docs\STATE_CONTRACT.md` - 状态边界与写权限矩阵
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\assets\shared\external_intelligence\triage\prioritized_signals.json` - 现有 shortlist 事实源
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\assets\shared\CEO_RANKING.md` - 现有 CEO ranking 产物
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\.planning\phases\02-signal-triage-and-role-analysis-loop\02-03-SUMMARY.md` - Phase 2 handoff

### Secondary (MEDIUM confidence)
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\.planning\research\SUMMARY.md` - 项目级 Phase 3 方向
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\.planning\research\ARCHITECTURE.md` - artifact-first 架构建议
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\.planning\research\FEATURES.md` - 决策包/执行包/board brief 关系
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\.planning\research\PITFALLS.md` - 输出质量常见失败模式
- 环境探针：`python3` / `bash` / `node` / `npm` / `hermes --version` - 依赖可用性与版本

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - 完全基于现有 repo 栈与环境探针，无需猜测新框架。[VERIFIED: repo code][VERIFIED: environment probe]
- Architecture: HIGH - 锁定决策明确要求“主包为源、次包派生、每日生成、层级证据”。[VERIFIED: repo code]
- Pitfalls: MEDIUM - 其中 history 命名与 sidecar 深度仍有少量假设，需要计划时锁定。[VERIFIED: repo code][ASSUMED]

**Research date:** 2026-04-25
**Valid until:** 2026-05-25
