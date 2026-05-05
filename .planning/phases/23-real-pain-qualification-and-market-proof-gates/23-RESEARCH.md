# Phase 23: Real-Pain Qualification and Market Proof Gates - Research

**Researched:** 2026-05-04
**Domain:** Pre-approval qualification gating for discovery artifacts, buildability, and market proof
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
### Freshness gate
- **D-01:** Qualification should use artifact-backed evidence timestamps and fail any candidate whose required pain evidence is older than 72 hours at qualification time.
- **D-02:** Freshness should be evaluated from persisted source/evidence metadata inside shared discovery artifacts, not from prose summaries that require the operator to infer recency manually.
- **D-03:** If freshness cannot be proven for every required evidence link, the candidate should block before proposal generation instead of degrading into a warning.

### Real-pain qualification contract
- **D-04:** Hermes should require a structured qualification bundle that proves the pain is user-facing, specific, and narrow enough to support one focused SaaS workflow rather than a vague market theme.
- **D-05:** Qualification should reject ideas that only show generic demand, trend chatter, or broad business categories without a concrete repeated pain pattern and target operator/user segment.
- **D-06:** The qualification result should be machine-readable and reason-coded so later proposal and approval steps can tell exactly which gate passed or failed.

### Feasibility against the shared platform
- **D-07:** Buildability must be judged against the shipped shared-template and shared-Supabase contract, not against an imaginary custom stack that Hermes does not actually deliver by default.
- **D-08:** Qualification should block ideas that require protected-platform rewrites, broad custom backend work, or product scope too large for the governed template-based delivery path.
- **D-09:** Feasibility proof should explicitly connect the proposed workflow to known template/backend capabilities and known constraints, rather than leaving that check as planner intuition later.

### Market and pricing proof
- **D-10:** Market, competitor, and pricing evidence should become mandatory qualification artifacts for every proposal candidate, not optional narrative fields.
- **D-11:** Pricing proof should be tied to the actual pain/workflow and intended paid outcome, so Hermes cannot advance a candidate with a strong pain story but no believable monetization path.
- **D-12:** Missing or thin market/pricing evidence should stop the run before proposal approval rather than being carried as a soft caveat into operator review.

### Claude's Discretion
- Exact scoring formula used to summarize qualification results, as long as pass/fail truth remains artifact-backed and explainable.
- Exact storage location for the qualification bundle, as long as later proposal/approval steps can read it canonically.
- Exact competitor/pricing evidence schema, as long as it preserves freshness, traceability, and buildability relevance.

### Deferred Ideas (OUT OF SCOPE)
- Final proposal wording, operator-facing proposal presentation, and approval UX belong to Phase 24.
- Post-approval autonomous continuation belongs to Phase 25.
- Broader product portfolio strategy or long-horizon market expansion logic remains out of scope; this phase is about candidate gating for one buildable proposal.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| QUAL-01 | Hermes only proposes project candidates whose supporting pain evidence was collected within the last 72 hours. | Use persisted `collected_at` / `published_at` lineage from `signals.jsonl` through `prioritized_signals.json`; add fail-closed freshness gate before proposal generation. [VERIFIED: codebase grep] |
| QUAL-02 | Hermes must prove each proposed pain point is real, user-facing, and specific enough to support a narrow SaaS workflow. | Add structured qualification bundle with reason-coded `pain_reality`, `user_facing`, and `workflow_narrowness` checks stored as machine-readable JSON. [VERIFIED: codebase grep] |
| QUAL-03 | Hermes must prove the proposed product is feasible on the shared template, shared Supabase, and governed delivery stack before approval. | Reuse template contract protected/safe layer rules and approved-project blocking style to produce explicit feasibility evidence. [VERIFIED: codebase grep] |
| QUAL-04 | Hermes must attach market, competitor, and pricing evidence to each proposal and block approval when those artifacts are missing. | Extend the pre-approval contract so market/pricing artifacts are mandatory input, not derived defaults, and block downstream approval bundle generation when absent or stale. [VERIFIED: codebase grep] |
</phase_requirements>

## Summary

这个 phase 最适合做成一个新的“资格闸门”脚本层，位置放在 `prioritized_signals.json` 之后、`generate_decision_package.py` 与 `start_approved_project_delivery.py` 之前。现有仓库已经有三类关键契约可复用：外部情报的时间戳与来源血缘、决策包的 fail-closed 结构校验、以及 approved-project 的 machine-readable block reason 体系，因此不需要先引入新的工作流引擎或数据库。 [VERIFIED: codebase grep]

实现重点不是“更聪明地打分”，而是把四类硬门槛写成可审计的工件：`freshness`、`pain reality`、`template feasibility`、`market/pricing proof`。当前 `prioritized_signals.json` 只有 `latest_evidence_age_hours`、`problem_summary`、`target_user`、`score_components` 等轻量字段，无法单独证明 72 小时 freshness、真实用户痛点、平台可构建性、或定价证据完整性，所以需要新增 canonical qualification artifact，而不是继续从 markdown prose 或默认值推断。 [VERIFIED: codebase grep]

另一个关键结论是：Phase 23 不应复用 `start_approved_project_delivery.py` 中的默认 monetization / language / UI contract 自动补全逻辑作为“证明”。那个脚本的职责是 approved-project bundle 构造，并且会在从 decision package 构建 payload 时填充默认 monetization、required languages 和 UI artifact contract；这与本 phase 的“必须先证明再批准”目标冲突。Phase 23 必须把缺失证据视为阻断，而不是默认生成。 [VERIFIED: codebase grep]

**Primary recommendation:** 新增一个 `qualification bundle + qualification gate` 层，输出机器可读 JSON 与简短 markdown 摘要，作为 proposal/approval 的唯一上游资格来源，并在缺证据时 fail closed。 [VERIFIED: codebase grep]

## Project Constraints (from CLAUDE.md)

- 仅当前端 UI 工作时才强制调用 `/ui-ux-pro-max`；本 phase 属于后端/治理脚本研究，不触发该约束。 [VERIFIED: codebase grep]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Evidence freshness gate | API / Backend | Database / Storage | 72 小时判定依赖持久化 artifact 时间戳与 lineage，不应由人工或前端推断。 [VERIFIED: codebase grep] |
| Real-pain qualification | API / Backend | Database / Storage | 资格判定需要读取 triage artifact、输出 reason-coded verdict，并供后续脚本消费。 [VERIFIED: codebase grep] |
| Template feasibility gate | API / Backend | Database / Storage | 共享模板与 shared Supabase 约束已记录在平台契约文档，适合由脚本读取并执行规则。 [VERIFIED: codebase grep] |
| Market / competitor / pricing proof gate | API / Backend | Database / Storage | 市场证明应成为 approval 前的必填工件，而不是 UI 层注释或 operator 手工判断。 [VERIFIED: codebase grep] |
| Gate artifact persistence | Database / Storage | API / Backend | 新资格 bundle 需要写入 `assets/shared/...` 这一现有权威工件层。 [VERIFIED: codebase grep] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.11.15 | 资格判定脚本、JSON artifact 读写、时间窗口计算 | 仓库现有关键流水线脚本均为 Python CLI，且本机运行时为 3.11.15。 [VERIFIED: local CLI] |
| Python stdlib (`argparse`, `json`, `datetime`, `pathlib`, `dataclasses`) | bundled with Python 3.11.15 | CLI 参数、schema-like validation、UTC 时间判断、工件路径治理 | `collect_external_signals.py`、`triage_external_signals.py`、`generate_decision_package.py` 均使用 stdlib 完成 fail-closed artifact 处理。 [VERIFIED: codebase grep][CITED: https://docs.python.org/3/library/argparse.html] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 8.4.2 | 测试执行入口 | 仓库当前可用测试运行器；用于 phase 级快速回归。 [VERIFIED: local CLI] |
| unittest | bundled with Python 3.11.15 | 现有测试文件结构 | 当前 `tests/` 主要用 `unittest` 编写，新增资格闸门测试应延续该模式。 [VERIFIED: codebase grep][CITED: https://docs.python.org/3/library/unittest.html] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Python stdlib validation | `jsonschema` or `pydantic` | 这些库能减少手写校验，但仓库当前没有使用痕迹；对 Phase 23 来说，沿用现有 fail-closed Python dict validation 能更低风险接入。 [VERIFIED: codebase grep] |
| Markdown-only qualification notes | JSON + markdown dual artifact | 单独 markdown 不足以给 Phase 24/25 做精确阻断；JSON verdict 更符合现有 machine-readable pipeline。 [VERIFIED: codebase grep] |

**Installation:**
```bash
pip install pytest
```

**Version verification:** `python --version` 返回 `Python 3.11.15`，`pytest --version` 返回 `pytest 8.4.2`。仓库根目录未发现 `pyproject.toml`、`requirements.txt` 或 `package.json` 作为该 phase 的 Python 依赖清单。 [VERIFIED: local CLI][VERIFIED: codebase grep]

## Architecture Patterns

### System Architecture Diagram

```text
external_intelligence/history/signals.jsonl
  -> triage_external_signals.py
  -> prioritized_signals.json
  -> qualification_gate.py
       -> freshness check (72h, lineage-backed)
       -> pain reality check (real/user-facing/narrow)
       -> feasibility check (template/shared-Supabase constraints)
       -> market & pricing proof check
       -> qualification_bundle.json
       -> qualification_summary.md
  -> proposal / decision-package generation
  -> approved-project bundle creation
```

### Recommended Project Structure
```text
assets/
└── shared/
    └── qualification/
        ├── latest/
        │   ├── qualification_bundle.json
        │   └── QUALIFICATION_SUMMARY.md
        └── history/
            └── *.json
scripts/
├── qualify_project_candidates.py
└── qualification_common.py
tests/
├── test_qualification_gate.py
└── test_qualification_contract.py
```

### Pattern 1: Fail-Closed Artifact Validation
**What:** 先校验输入工件的 required fields，再生成输出；缺字段立即 block。 [VERIFIED: codebase grep]
**When to use:** 读取 `prioritized_signals.json`、市场/竞品/定价证据、以及模板可行性证明时。 [VERIFIED: codebase grep]
**Example:**
```python
# Source: scripts/generate_decision_package.py
required_keys = (
    "idea_id",
    "title",
    "problem_summary",
    "target_user",
    "evidence_links",
    "score_components",
    "estimated_mvp_hours",
    "total_score",
    "rank",
    "generated_from",
)
missing = [key for key in required_keys if key not in record]
if missing:
    raise DecisionPackageError(
        f"prioritized_signals[{index}] missing fields: {', '.join(missing)}"
    )
```

### Pattern 2: Persisted Timestamp, Not Summary Prose
**What:** freshness 必须从 artifact 中的 `collected_at` / `published_at` / generated lineage 计算，不从 markdown 叙述猜测。 [VERIFIED: codebase grep]
**When to use:** 实现 `QUAL-01` 时，对每个 evidence link 做独立验证。 [VERIFIED: codebase grep]
**Example:**
```python
# Source: scripts/triage_external_signals.py
published_raw = str(payload.get("published_at") or "").strip()
effective_at = parse_iso8601(published_raw, field="published_at") if published_raw else collected_at
if effective_at < cutoff:
    continue
```

### Pattern 3: Reason-Coded Blocking Contract
**What:** 用 `block_reason` 和 allowed reason set 表达 gate 失败，而不是只返回布尔值。 [VERIFIED: codebase grep]
**When to use:** Qualification gate 输出需要给 proposal/approval 阶段直接消费时。 [VERIFIED: codebase grep]
**Example:**
```python
# Source: scripts/start_approved_project_delivery.py
status = "blocked" if block_reason else "ready"
approved_project["pipeline"] = {
    "stage": "approval",
    "status": status,
    "block_reason": block_reason,
}
```

### Anti-Patterns to Avoid
- **把 Phase 23 做成 markdown checklist：** 现有下游脚本依赖 machine-readable truth；纯 prose 无法精确阻断。 [VERIFIED: codebase grep]
- **沿用 approved-project 默认 monetization 生成逻辑：** Phase 23 的目标是“先证明后批准”，默认填充值会掩盖证据缺口。 [VERIFIED: codebase grep]
- **从 `latest_evidence_age_hours` 单字段直接判断全部 freshness：** 该字段是聚合结果，不足以证明“每条 required evidence link”均在 72 小时内。 [VERIFIED: codebase grep]
- **把模板可行性写成主观备注：** 平台契约已经明确 protected layer、safe extension layer、shared-table rules，应输出结构化 verdict。 [VERIFIED: codebase grep] |

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Buildability truth | 自定义“看起来可做”的主观评分 | 读取 `docs/platform/standalone-saas-template-contract.md` 的 protected/safe layer 规则 | 现有模板契约已定义共享 Supabase、受保护路由、`APP_KEY_` 表边界与 blocking rules。 [VERIFIED: codebase grep] |
| Approval blocking semantics | 新 block 状态模型 | 复用 approved-project 的 `status` + `block_reason` 风格 | 下游流水线已经围绕 reason-coded block 构建。 [VERIFIED: codebase grep] |
| Evidence lineage | 手写自由文本 backlink | 复用 `generated_from`, history path, cluster path, source id 风格 | 现有 triage / decision package 已保留这些 lineage 字段。 [VERIFIED: codebase grep] |
| Product-proof expectations | 新建另一套“真实产品”标准 | 复用 `product_proof_contract.py` 的 template-only / primary surface / supporting logic 语言 | 可行性 gate 需要与后续 delivery proof vocabulary 一致。 [VERIFIED: codebase grep] |

**Key insight:** 这个 phase 缺的不是新基础设施，而是把现有 discovery、decision、template-contract、approval block 这四类契约提前串起来。 [VERIFIED: codebase grep]

## Common Pitfalls

### Pitfall 1: 把聚合 triage 分数误当作资格证明
**What goes wrong:** 仅凭 `total_score` 或 `score_components` 就让候选进入 proposal。 [VERIFIED: codebase grep]
**Why it happens:** 当前 triage 产物只表达排序，不表达“真实痛点是否已证明”。 [VERIFIED: codebase grep]
**How to avoid:** Phase 23 新增独立 qualification bundle，区分 ranking 与 gating。 [VERIFIED: codebase grep]
**Warning signs:** 资格输出里只有 score，没有 per-gate verdict、reason code、evidence paths。 [VERIFIED: codebase grep]

### Pitfall 2: 只校验候选整体 freshness，不校验每条 required evidence
**What goes wrong:** 某个候选因为最新一条证据是新鲜的而通过，但其他关键证据已过期。 [ASSUMED]
**Why it happens:** 当前 `prioritized_signals.json` 暴露的是聚合年龄字段。 [VERIFIED: codebase grep]
**How to avoid:** 在 qualification bundle 里为每条 required evidence 记录 `observed_at`, `source_id`, `passes_72h`. [ASSUMED]
**Warning signs:** gate 结果只含 `latest_evidence_age_hours`，没有 evidence-level breakdown。 [ASSUMED]

### Pitfall 3: 用默认 monetization 填补市场证明空白
**What goes wrong:** proposal 看起来有收费路径，但其实只是模板化默认文案。 [VERIFIED: codebase grep]
**Why it happens:** `start_approved_project_delivery.py` 能从 decision package 自动生成默认 monetization。 [VERIFIED: codebase grep]
**How to avoid:** Phase 23 之前必须提供真实市场、竞品、定价 artifact；缺失即 block。 [VERIFIED: codebase grep]
**Warning signs:** monetization 文本来自 `build_default_monetization()` 而不是外部证据。 [VERIFIED: codebase grep]

### Pitfall 4: feasibility gate 与模板契约脱节
**What goes wrong:** 候选在 proposal 阶段通过，进入 delivery 后才发现要改 protected auth/payment/backend 边界。 [VERIFIED: codebase grep]
**Why it happens:** feasibility 被留到 planner 直觉判断，未绑定平台契约。 [VERIFIED: codebase grep]
**How to avoid:** 明确输出 `requires_protected_layer_change`, `requires_unprefixed_table`, `requires_custom_backend` 等 reason code。 [ASSUMED]
**Warning signs:** “可行”结论没有引用模板契约条目或具体 capability mapping。 [ASSUMED]

## Code Examples

Verified patterns from official sources and the codebase:

### UTC freshness window
```python
# Source: scripts/triage_external_signals.py
cutoff = now_utc() - timedelta(hours=window_hours)
effective_at = parse_iso8601(published_raw, field="published_at") if published_raw else collected_at
if effective_at < cutoff:
    continue
```

### Machine-readable blocked verdict
```python
# Source: scripts/start_approved_project_delivery.py
missing = collect_missing_inputs(normalized_payload)
block_reason = resolve_block_reason(missing)
status = "blocked" if block_reason else "ready"
```

### Safe write-boundary enforcement
```python
# Source: scripts/generate_decision_package.py
def write_output(path: Path, content: str) -> None:
    ensure_allowed_write_path(path)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| 排序优先的 triage shortlist | 排序之后再加独立 qualification gate | Phase 23 scope, 2026-05-04 context | 把“最有意思”与“可批准”明确拆开。 [VERIFIED: codebase grep] |
| Proposal 触发后再补 approval bundle 默认值 | Proposal 之前就要求真实市场/定价/可行性证明 | Phase 23 requirements, 2026-05-04 | 防止弱证据候选进入 approved-project path。 [VERIFIED: codebase grep] |
| 人工阅读 markdown 判断平台可行性 | 结构化 feasibility verdict 绑定模板契约 | 基于现有模板合同与 block-style pipeline | 降低 planner intuition 漂移。 [VERIFIED: codebase grep] |

**Deprecated/outdated:**
- 把 `decision package` 直接当作 approval 输入真相源：当前脚本会为某些字段自动填默认值，不满足本 phase 的证明标准。 [VERIFIED: codebase grep]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Qualification bundle 应逐条持久化 required evidence verdict，而不是只存候选级 verdict。 | Common Pitfalls / Architecture Patterns | 若不需要 evidence-level 明细，计划会多做 schema 与测试。 |
| A2 | Feasibility gate 应新增 `requires_protected_layer_change`、`requires_unprefixed_table`、`requires_custom_backend` 这类 reason code。 | Common Pitfalls | 若项目偏好其他命名，计划需调整枚举与测试断言。 |

## Open Questions

1. **市场/竞品/定价证据的 canonical 输入来自哪里？**
   - What we know: 当前仓库有 `PAIN_POINTS.md`、`MARKET_PLAN.md`、`TECH_SPEC.md` 和 external intelligence artifacts，但没有现成 market-proof JSON contract。 [VERIFIED: codebase grep]
   - What's unclear: 这些证据是继续来自 role markdown，还是新增结构化 market artifact。 [VERIFIED: codebase grep]
   - Recommendation: 规划时优先要求一个新 JSON sidecar，markdown 只做 operator 摘要。 [ASSUMED]

2. **qualification artifact 的 canonical 存储位置是否应按 candidate 分 history？**
   - What we know: 仓库已有 `latest + history + trace` 模式，例如 decision packages 与 external intelligence。 [VERIFIED: codebase grep]
   - What's unclear: 是存 `assets/shared/qualification/latest/...`，还是按 `idea_id` / run_id 历史分桶。 [VERIFIED: codebase grep]
   - Recommendation: 规划时采用 `latest/ + history/` 双写模式，保持和现有 artifact family 一致。 [ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Qualification scripts and tests | ✓ | 3.11.15 | — |
| pytest | Quick validation runs | ✓ | 8.4.2 | `python -m unittest` |

**Missing dependencies with no fallback:**
- None. [VERIFIED: local CLI]

**Missing dependencies with fallback:**
- None. [VERIFIED: local CLI]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `unittest` test files executed via `pytest 8.4.2` or `python -m unittest`. [VERIFIED: codebase grep][VERIFIED: local CLI] |
| Config file | none detected in repo root. [VERIFIED: codebase grep] |
| Quick run command | `pytest tests/test_generate_decision_package.py tests/test_approved_project_record.py -q` |
| Full suite command | `pytest -q` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| QUAL-01 | Block candidates whose required evidence exceeds 72h or lacks proof | unit | `pytest tests/test_qualification_gate.py -q -k freshness` | ❌ Wave 0 |
| QUAL-02 | Require real, user-facing, narrow pain verdicts with reason codes | unit | `pytest tests/test_qualification_gate.py -q -k pain` | ❌ Wave 0 |
| QUAL-03 | Block infeasible candidates against shared template/shared Supabase constraints | unit | `pytest tests/test_qualification_gate.py -q -k feasibility` | ❌ Wave 0 |
| QUAL-04 | Require market / competitor / pricing artifacts before approval | unit | `pytest tests/test_qualification_gate.py -q -k market` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `pytest tests/test_qualification_gate.py -q`
- **Per wave merge:** `pytest tests/test_generate_decision_package.py tests/test_approved_project_record.py tests/test_template_contract.py -q`
- **Phase gate:** `pytest -q`

### Wave 0 Gaps
- [ ] `tests/test_qualification_gate.py` — covers QUAL-01 through QUAL-04.
- [ ] `tests/test_qualification_contract.py` — asserts required output fields, reason codes, and backlink invariants.
- [ ] 夹具数据：需要一组 fresh/stale/missing-market-proof candidate fixtures。 [ASSUMED]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | 本 phase 不新增认证面。 [VERIFIED: codebase grep] |
| V3 Session Management | no | 本 phase 不处理 session 生命周期。 [VERIFIED: codebase grep] |
| V4 Access Control | yes | 继续遵守 artifact 写边界与 allowlisted output paths。 [VERIFIED: codebase grep] |
| V5 Input Validation | yes | 对 JSON artifact 做 required-field、timestamp、reason-code 校验并 fail closed。 [VERIFIED: codebase grep] |
| V6 Cryptography | no | 本 phase 不新增加密原语。 [VERIFIED: codebase grep] |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Stale evidence accepted as current | Tampering | 用 UTC timestamp + 72h cutoff + per-evidence lineage 验证。 [VERIFIED: codebase grep][ASSUMED] |
| Silent defaulting hides missing proof | Repudiation | 缺少 market/pricing/pain proof 时直接 block，不自动补默认值。 [VERIFIED: codebase grep] |
| Writing authority artifacts outside approved paths | Tampering | 复用 allowlisted write path pattern。 [VERIFIED: codebase grep] |
| Ambiguous gate failure reasons | Repudiation | 输出 reason-coded machine-readable verdict。 [VERIFIED: codebase grep] |

## Sources

### Primary (HIGH confidence)
- `scripts/collect_external_signals.py` - checked run metadata, timestamp persistence, normalized signal schema. [VERIFIED: codebase grep]
- `scripts/triage_external_signals.py` - checked time-window filtering, prioritized shortlist schema, lineage fields, scoring vs gating boundaries. [VERIFIED: codebase grep]
- `scripts/generate_decision_package.py` - checked fail-closed validation, required keys, safe write boundaries, backlink model. [VERIFIED: codebase grep]
- `scripts/start_approved_project_delivery.py` - checked approved-project blocking contract, default monetization/language/UI fallback behavior, decision-package ingestion. [VERIFIED: codebase grep]
- `scripts/product_proof_contract.py` - checked proof vocabulary and template-only blockers. [VERIFIED: codebase grep]
- `docs/platform/standalone-saas-template-contract.md` - checked protected platform layer, safe extension layer, shared Supabase rules, blocking rules. [VERIFIED: codebase grep]
- `tests/test_generate_decision_package.py`, `tests/test_approved_project_record.py`, `tests/test_template_contract.py` - checked current validation expectations. [VERIFIED: codebase grep]
- `assets/shared/external_intelligence/triage/prioritized_signals.json` and `assets/shared/external_intelligence/history/runs.jsonl` - checked live artifact shape and persisted timestamps. [VERIFIED: codebase grep]
- https://docs.python.org/3/library/argparse.html - checked stdlib CLI documentation. [CITED: https://docs.python.org/3/library/argparse.html]
- https://docs.python.org/3/library/unittest.html - checked stdlib test framework documentation. [CITED: https://docs.python.org/3/library/unittest.html]

### Secondary (MEDIUM confidence)
- None.

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - 当前 phase 所需运行时和测试栈均已在本地与代码库中确认。 [VERIFIED: local CLI][VERIFIED: codebase grep]
- Architecture: HIGH - 上下游脚本、模板契约、以及现有 artifact family 已明确给出集成边界。 [VERIFIED: codebase grep]
- Pitfalls: MEDIUM - 大部分来自现有代码路径，但 evidence-level verdict 细化与 reason-code 命名仍有少量实现自由度。 [VERIFIED: codebase grep][ASSUMED]

**Research date:** 2026-05-04
**Valid until:** 2026-06-03
