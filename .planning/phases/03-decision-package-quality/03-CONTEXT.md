# Phase 3: Decision Package Quality - Context

**Gathered:** 2026-04-25
**Status:** Ready for planning

<domain>
## Phase Boundary

Turn the existing analysis loop into polished, management-grade deliverables with strong conclusions and evidence links. This phase must make the daily operating decision package clear and trustworthy, and ensure project execution packages plus board-style briefings can be generated from the same decision foundation without re-analyzing raw signals.

</domain>

<decisions>
## Implementation Decisions

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

</decisions>

<specifics>
## Specific Ideas

- The user wants the artifact to feel like: "先给拍板结论，再附证据与分析".
- The main package should open with: "一句话结论 + Top 3 排序".
- Evidence should stay light in the main read path, but preserve drill-down traceability to upstream artifacts.
- The board briefing should be more compact than the decision package, not a rewritten long-form report.
- The execution package should help the operator start a project from the day’s conclusion, not immediately decompose into owner/dependency task management.

</specifics>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §Phase 3 — phase goal, success criteria, and the 03-01/03-02/03-03 plan split
- `.planning/REQUIREMENTS.md` — DECI-01, DECI-02, and DECI-03 requirements that this phase satisfies
- `.planning/PROJECT.md` — project-level output quality goals, solo-operator workflow bias, and management-core framing
- `.planning/STATE.md` — confirms Phase 3 is the active focus after Phase 2 completion

### Prior phase handoff
- `.planning/phases/02-signal-triage-and-role-analysis-loop/02-03-SUMMARY.md` — stable shared-shortlist analysis loop and CEO ranking handoff now available to package generation

### Existing artifact contracts and prompts
- `assets/shared/TEMPLATES.md` — current shared markdown templates for Scout, CEO ranking, market plan, tech spec, and corporate memory
- `orchestration/cron/daily_pipeline.prompt.md` — current daily-loop sequence and output expectations that Phase 3 must upgrade rather than replace
- `orchestration/cron/external_intelligence.prompt.md` — upstream intake summary expectations feeding the daily loop

### Research context
- `.planning/research/SUMMARY.md` §Phase 3 — intended delivery shape for output-generation work
- `.planning/research/ARCHITECTURE.md` — decision/execution artifact directories and output-generation layer expectations
- `.planning/research/FEATURES.md` — daily decision package, execution package, and board briefing relationship
- `.planning/research/PITFALLS.md` — reminder that decision packages often fail when recommendation ranking is weak or evidence is vague

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `assets/shared/TEMPLATES.md`: existing template vocabulary already defines the upstream and adjacent artifacts Phase 3 should align with.
- `assets/shared/CEO_RANKING.md`: current CEO output is already a ranked shortlist artifact that can seed the new decision package structure.
- `assets/shared/PAIN_POINTS.md`: current lead/evidence formatting provides raw material for concise evidence summaries.
- `orchestration/cron/daily_pipeline.prompt.md`: current cron prompt already defines the order and responsibilities of the daily loop.

### Established Patterns
- Phase 2 established a single shared-shortlist flow; Phase 3 should preserve that same evidence base instead of allowing per-artifact re-analysis.
- Current outputs are markdown artifacts under `assets/shared/`, so Phase 3 should likely extend artifact generation in that style rather than introducing a UI/dashboard layer.
- The project already uses role-distinct artifacts (Scout, CMO, Architect, CEO), so decision-package generation should synthesize across them instead of replacing them.

### Integration Points
- Decision-package generation should plug in after `scripts/run_signal_analysis_loop.sh` and the role artifact generation it triggers.
- The daily cron pipeline in `orchestration/cron/daily_pipeline.prompt.md` is the primary integration point for recurring generation.
- Upstream evidence sources are the prioritized shortlist and role outputs; downstream consumers are later governance, visibility, execution, and briefing phases.

</code_context>

<deferred>
## Deferred Ideas

- Task-level execution management with owners, dependencies, and workflow tracking belongs to a later execution/governance layer, not this phase.
- Rich dashboard/UI presentation remains out of scope for Phase 3; Phase 5 is the visibility surface.
- Team-oriented board/approval workflows remain out of scope here; Phase 4 and Phase 6 handle governance and team readiness.

</deferred>

---

*Phase: 03-decision-package-quality*
*Context gathered: 2026-04-25*
