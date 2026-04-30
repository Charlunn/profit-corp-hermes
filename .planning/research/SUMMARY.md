# Project Research Summary

**Project:** Profit-Corp Hermes
**Domain:** AI-operated company management core / multi-agent operating system
**Researched:** 2026-04-24
**Confidence:** MEDIUM

## Executive Summary

This project fits a growing class of multi-agent operating systems where orchestration, durable state, and human oversight matter more than prompt cleverness alone. Official ecosystem guidance across current agent frameworks points in a similar direction: collaborative agents need explicit workflow control, durable handoffs, guardrails, and memory/state mechanisms rather than ad-hoc prompt chains.

For this repo specifically, the best approach is evolutionary, not replacement-driven. The existing Hermes profiles, cron orchestration, governance docs, and finance/state constraints already provide a viable substrate. The next steps should add a deterministic external-intelligence pipeline, artifact-based role collaboration, and stronger governance enforcement so the system can produce repeatable management-grade operating decisions.

The major risk is building a polished “AI company demo” that still lacks trustworthy input quality and executable governance. To avoid that, roadmap phases should begin with source intake, signal triage, and daily decision-loop reliability before moving into output polish, visibility layers, and team-scale expansion.

## Key Findings

### Recommended Stack

The most pragmatic stack is to keep Hermes as the orchestration runtime while adding Python-based deterministic tooling for ingestion, normalization, dedupe, and report assembly. This preserves the repo’s brownfield strengths while introducing the missing operating-system pieces.

**Core technologies:**
- Hermes runtime: profile execution and cron orchestration — already the repo’s execution backbone
- Python 3.11+: ingestion, scoring, normalization, and structured report utilities — strong fit for deterministic workflows
- Structured markdown/YAML/JSON artifacts: shared state and reviewable outputs — matches the governance-heavy repo design
- Stateful orchestration concepts: supervisor/routing/checkpoint patterns — recommended by modern multi-agent framework docs

### Expected Features

The most important table-stakes features are external signal intake, triage/deduplication, role-based analysis, daily operating decision packages, governance controls, and at-a-glance operating visibility.

**Must have (table stakes):**
- External intelligence intake and normalization — users expect the system to actually sense the market
- Signal triage and daily decision package generation — users expect clarity, not raw noise
- Governance and audit boundaries — required for trust in recurring operation
- Operating visibility summary — directly tied to the user’s success metric

**Should have (competitive):**
- Forum complaint intelligence engine — strong differentiator aligned with the user’s stated priority
- Consulting-grade + CEO-grade mixed output style — makes decisions feel executive, not generic
- Decision-to-execution package handoff — bridges management insight to delivery

**Defer (v2+):**
- Full team collaboration surfaces
- Real-time monitoring UI as the primary interface
- Internal telemetry-first operating model

### Architecture Approach

The recommended architecture is a layered operating loop: source adapters feed a normalized signal pipeline; role analyzers produce distinct business interpretations; CEO synthesizes a single operating decision; governance and audit wrappers enforce trust; structured artifacts provide history and visibility.

**Major components:**
1. Source intake and normalization — capture external market, competitor, and complaint signals
2. Signal processing and prioritization — dedupe, cluster, and rank what matters
3. Multi-role analysis and CEO synthesis — generate management conclusions from shared evidence
4. Governance and output generation — enforce approvals and produce decision/execution/brief artifacts

### Critical Pitfalls

1. **Prompt-only company simulation** — avoid by creating structured state and artifact handoffs early
2. **Output polish without evidence quality** — avoid by stabilizing ingestion and triage before presentation work
3. **Governance only in docs** — avoid by making approvals/audit steps executable in workflows
4. **Autonomy too early** — avoid by keeping founder approval on high-impact actions
5. **Dashboard-first development** — avoid by building visibility on top of trusted artifacts, not before them

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: External Intelligence Foundation
**Rationale:** Nothing else is trustworthy until external inputs are consistently collected and normalized.
**Delivers:** Source adapters, normalized signal schema, intake history, and repeatable daily collection.
**Addresses:** External intake, evidence quality.
**Avoids:** Prompt-only operation and weak evidence quality.

### Phase 2: Signal Triage and Role Analysis Loop
**Rationale:** Once inputs exist, the system must turn noise into prioritized role-specific reasoning.
**Delivers:** Deduplication, scoring, clustering, Scout/CMO/Arch/Accountant analysis artifacts, CEO synthesis handoff.
**Uses:** Structured artifacts and deterministic processing.
**Implements:** Multi-role analysis layer.

### Phase 3: Operating Decision Package Quality
**Rationale:** The user explicitly wants more professional management outputs.
**Delivers:** Strong decision pack template, evidence-linked recommendations, mixed consulting + CEO output style, secondary pack scaffolds.
**Uses:** Report templates and structured artifact generation.
**Implements:** Output generation layer.

### Phase 4: Governance and Executable Controls
**Rationale:** Quality alone is insufficient if approvals, budgets, and audits remain advisory.
**Delivers:** Approval records, audit trail flow, governance checks wrapped around strategic/budget-impacting actions.
**Uses:** Existing repo contracts and finance constraints.
**Implements:** Governance wrapper layer.

### Phase 5: Management Visibility Surface
**Rationale:** The user’s first-stage success metric is operating visibility.
**Delivers:** At-a-glance summary of situation, risks, opportunities, and next actions from trusted artifacts.
**Uses:** Decision history, signal state, governance status.
**Implements:** Visibility/read-model layer.

### Phase 6: Execution and Team Readiness
**Rationale:** After the operating core works, downstream execution packs and team expansion become valuable.
**Delivers:** Project execution package generation, board-style briefings, clearer role ownership for future team use.

### Phase Ordering Rationale

- Inputs must stabilize before analysis quality can stabilize.
- Analysis loop must work before output polish is meaningful.
- Governance should wrap a real decision process, not a hypothetical one.
- Visibility should read from trusted operating artifacts, not lead them.
- Team readiness should follow a proven solo-operator loop.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase 1:** source adapter choices and public-source collection constraints
- **Phase 4:** governance workflow design and approval artifact patterns
- **Phase 6:** team collaboration/ownership model if expanded beyond solo operator use

Phases with standard patterns (skip research-phase):
- **Phase 3:** report templating and artifact generation are comparatively standard once inputs are stable

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM | Strong direction from project context + framework guidance, but some source/tool choices remain open |
| Features | HIGH | Closely aligned with explicit user statements and current repo constraints |
| Architecture | MEDIUM | Layered workflow model is clear, but exact implementation details depend on runtime decisions |
| Pitfalls | MEDIUM | Well-supported by current multi-agent ecosystem patterns and repo realities |

**Overall confidence:** MEDIUM

### Gaps to Address

- Public-source acquisition strategy needs concrete implementation choices per source type
- Team-scale collaboration model should wait until the solo daily loop proves useful
- Exact visibility surface format (markdown summary vs dashboard vs both) should be decided after artifact structure stabilizes

## Sources

### Primary (HIGH confidence)
- `https://docs.crewai.com/` — orchestration, flows vs crews, guardrails, memory, observability
- `https://microsoft.github.io/autogen/stable/` — Core/AgentChat multi-agent runtime concepts
- `.planning/PROJECT.md` — project goals and constraints
- `.planning/codebase/` — current brownfield reality

### Secondary (MEDIUM confidence)
- `https://code.claude.com/docs/en/overview` — Claude Code docs target for agentic engineering workflow concepts (target confirmed; direct page fetch timed out)
- `https://docs.langchain.com/oss/python/langgraph/overview` — LangGraph docs target for stateful orchestration patterns (target confirmed; direct page fetch timed out)

---
*Research completed: 2026-04-24*
*Ready for roadmap: yes*
