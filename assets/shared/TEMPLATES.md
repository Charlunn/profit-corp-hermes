# Profit-Corp Communication Templates
[English] | [简体中文](TEMPLATES_CN.md)

## [Scout] PAIN_POINTS.md
```markdown
# Daily Intelligence Report - {{date}}
## Leads (Scoring-Ready)
### Lead: {{title}}
- **Idea ID**: {{idea_id}}
- **Problem**: {{description}}
- **Target User**: {{target_user}}
- **Evidence Links**: {{url_list}}
- **Latest Evidence Age (hours)**: {{hours}}
- **Urgency Pain (0-10)**: {{score}}
- **Estimated MVP Hours**: {{hours}}
- **Monetization Signal (0-10)**: {{score}}
- **Competition Signal (0-10)**: {{score}}
- **Confidence (0-10)**: {{score}}
- **Notes**: {{assumptions_or_risks}}
```

## [CMO] Idea Scorecard (Quantitative)
```markdown
### Scorecard: {{idea_id}} - {{title}}
- **UrgencyPain (0-10, weight 25%)**: {{score}}
- **OneDayFeasibility (0-10, weight 25%)**: {{score}}
- **MonetizationSpeed (0-10, weight 20%)**: {{score}}
- **EvidenceStrength (0-10, weight 15%)**: {{score}}
- **Recency (0-10, weight 10%)**: {{score}}
- **CompetitionGap (0-10, weight 5%)**: {{score}}
- **TotalScore (0-100)**: {{total}}
- **Formula**: `Total = 10 * (0.25*UrgencyPain + 0.25*OneDayFeasibility + 0.20*MonetizationSpeed + 0.15*EvidenceStrength + 0.10*Recency + 0.05*CompetitionGap)`
- **Hard Filters Passed**: {{yes_no}}
```

## [CEO] Top3 Ranking Output
```markdown
## Top 3 Ranked Micro-SaaS Ideas (last 48h)
| Rank | idea_id | Idea | TotalScore/100 | Urgency | Feasibility | Monetization | Evidence | Recency | Competition | MVP Hours |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | {{idea_id_1}} | {{idea_1}} | {{score_1}} | {{u1}} | {{f1}} | {{m1}} | {{e1}} | {{r1}} | {{c1}} | {{h1}} |
| 2 | {{idea_id_2}} | {{idea_2}} | {{score_2}} | {{u2}} | {{f2}} | {{m2}} | {{e2}} | {{r2}} | {{c2}} | {{h2}} |
| 3 | {{idea_id_3}} | {{idea_3}} | {{score_3}} | {{u3}} | {{f3}} | {{m3}} | {{e3}} | {{r3}} | {{c3}} | {{h3}} |

**Recommended**: {{idea_id_recommended}} — {{one_line_why}}

Reply with `1/2/3` or `idea_id` to continue automatically.
```

## [CMO] MARKET_PLAN.md
```markdown
# Market Strategy: {{project_name}}
- **Core USP**: {{unique_selling_point}}
- **Pricing**: {{model_and_price}}
- **Distribution**: {{where_to_find_customers}}
- **Risk Level**: {{low/med/high}}
```

## [Architect] TECH_SPEC.md
```markdown
# Technical Specification: {{project_name}}
- **Stack**: {{frontend/backend/db}}
- **File Tree**:
  ```
  {{directory_structure}}
  ```
- **MVP Features**: {{list}}
- **Build Time**: {{estimated_hours}}
```

## [Phase 3] OPERATING_DECISION_PACKAGE
主决策包是 Phase 3 的唯一决策基础，版式与 executive-first 摘要风格明确参考 `assets/shared/CEO_RANKING.md`。它必须先给 founder/operator 一个可以直接拍板的开场，再附上分层证据与回链，禁止把原始 evidence 全量堆到正文主路径。

- **Source relationship**: 读取 `assets/shared/external_intelligence/triage/prioritized_signals.json`、`assets/shared/PAIN_POINTS.md`、`assets/shared/MARKET_PLAN.md`、`assets/shared/TECH_SPEC.md`、`assets/shared/CEO_RANKING.md`，生成 latest 文件 `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`，并按日期写入 `assets/shared/decision_packages/history/YYYY-MM-DD-operating-decision-package.md`。
- **Trace contract**: 必须同时写 trace sidecar，至少保留 `generated_at`、`run_id`、`operating_package_path`、`derived_from.prioritized_shortlist_path`、`derived_from.role_outputs`、`judgment_links[]`，支持 prioritized shortlist -> role outputs -> CEO synthesis 的分层回链。
- **Opening contract**: 第一屏固定为一句话总判断，然后紧接 Top 3 排名；风格类比 `assets/shared/CEO_RANKING.md` 的紧凑高管阅读路径。
- **Body contract**: 按 D-01/D-04/D-05/D-06 组织为“一句话总判断 + Top 3 排名 + 机会/风险/下一步 + 分层证据回链”。每个关键判断正文只保留 1-3 行证据摘要，再给 repo-relative 上游路径与 judgment anchor。
- **History/latest rule**: latest 路径永远稳定，history 快照按日期命名，trace 侧车保留 run_id 与 judgment link 映射。

```markdown
# Operating Decision Package - {{date}}

## 一句话总判断
{{one_line_operator_decision}}

## Top 3 Opportunities
| Rank | idea_id | Opportunity | Why now | Evidence signal | Recommended motion |
|---|---|---|---|---|---|
| 1 | {{idea_id_1}} | {{title_1}} | {{why_now_1}} | {{signal_1}} | {{motion_1}} |
| 2 | {{idea_id_2}} | {{title_2}} | {{why_now_2}} | {{signal_2}} | {{motion_2}} |
| 3 | {{idea_id_3}} | {{title_3}} | {{why_now_3}} | {{signal_3}} | {{motion_3}} |

## Opportunities
### O1. {{opportunity_heading}}
- **Summary**: {{short_evidence_summary}}
- **Backlinks**: `assets/shared/external_intelligence/triage/prioritized_signals.json#{{idea_id}}`, `assets/shared/PAIN_POINTS.md`, `assets/shared/CEO_RANKING.md`

## Risks
### R1. {{risk_heading}}
- **Summary**: {{short_risk_evidence}}
- **Backlinks**: `assets/shared/MARKET_PLAN.md`, `assets/shared/TECH_SPEC.md`, `assets/shared/CEO_RANKING.md`

## Recommended Next Actions
- {{action_1}} — evidence: {{brief_reason}} — trace: `judgment_id={{judgment_id_1}}`
- {{action_2}} — evidence: {{brief_reason}} — trace: `judgment_id={{judgment_id_2}}`
```

## [Phase 3] EXECUTION_PACKAGE
执行包是纯派生产物，紧凑 kickoff bullet 结构明确参考 `assets/shared/MARKET_PLAN.md`。它只能从 `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` 单向派生，不能重读 raw signals、triage 或 role artifacts。

- **Source relationship**: 唯一输入是 latest 主决策包 `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` 或其 history 快照；latest 输出为 `assets/shared/execution_packages/EXECUTION_PACKAGE.md`，history 输出为 `assets/shared/execution_packages/history/YYYY-MM-DD-execution-package.md`。
- **Allowed fields**: 只保留 goal、target user、MVP framing、key risks、recommended near-term actions。
- **Forbidden fields**: 禁止出现 owner、dependency、task board、execution backlog 等治理层字段。
- **Derived-only rule**: 如果主包没有该信息，执行包必须显式标注“待主包补充”，而不是自行引入新结论。

```markdown
# Execution Package - {{date}}
- **Derived From**: `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`
- **Goal**: {{goal_from_operating_package}}
- **Target User**: {{target_user_from_operating_package}}
- **MVP Framing**: {{mvp_framing_from_operating_package}}
- **Key Risks**: {{risk_summary_from_operating_package}}
- **Recommended Near-Term Actions**:
  - {{action_1}}
  - {{action_2}}
```

## [Phase 3] BOARD_BRIEFING
董事会简报是纯派生产物，超短高管摘要风格同样明确参考 `assets/shared/CEO_RANKING.md`。它必须比主包更短，只保留结论、Top 3、关键数字/信号、major risk、Required Attention。

- **Source relationship**: 唯一输入是 `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` 或其 history 快照；latest 输出为 `assets/shared/board_briefings/BOARD_BRIEFING.md`，history 输出为 `assets/shared/board_briefings/history/YYYY-MM-DD-board-briefing.md`。
- **Compression rule**: 只压缩主包已存在的判断，不新增解释层分析。
- **Audience rule**: 面向超短管理阅读，强调 conclusion、Top 3、关键数字/信号、major risk、Required Attention。

```markdown
# Board Briefing - {{date}}
- **Derived From**: `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`
- **Conclusion**: {{one_line_conclusion}}

## Top 3
1. {{idea_id_1}} — {{short_reason_1}}
2. {{idea_id_2}} — {{short_reason_2}}
3. {{idea_id_3}} — {{short_reason_3}}

## Key Numbers / Signals
- {{number_or_signal_1}}
- {{number_or_signal_2}}

## Major Risk
- {{major_risk}}

## Required Attention
- {{required_attention_item}}
```

## [CEO/Accountant] CORP_CULTURE.md
```markdown
# Corporate Memory
## Entry: {{project_name}} - {{date}}
- **Outcome**: {{success/fail/reset}}
- **Lesson**: {{what_did_we_learn}}
- **Action**: {{strategy_change}}
```

## [CEO/Accountant] KNOWLEDGE_BASE.md Knowledge Card
Append to `shared/KNOWLEDGE_BASE.md` after every major decision:
```markdown
## Card: {{project_or_event_name}} — {{YYYY-MM-DD}}
- **Type**: decision | failure | pattern | milestone
- **Outcome**: {{GO/NO-GO/revenue/veto/archive/milestone}}
- **Lesson**: {{one-line key insight}}
- **Tags**: #{{tag1}} #{{tag2}}
```
