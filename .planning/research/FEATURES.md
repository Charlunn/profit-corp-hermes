# Feature Research

**Domain:** AI-operated company management core / multi-agent operating system
**Researched:** 2026-04-24
**Confidence:** MEDIUM

## Feature Landscape

### Table Stakes (Users Expect These)

Features users assume exist. Missing these = product feels incomplete.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| External signal intake | Without it, the system cannot sense the market | MEDIUM | Ingest industry news, competitor updates, and public complaint signals |
| Signal triage and deduplication | Raw sources are too noisy to act on directly | MEDIUM | Needs scoring, clustering, and suppression of repeats |
| Role-based analysis pipeline | A “company” system needs distinct analytical lenses | MEDIUM | Scout/CMO/Arch/CEO/Accountant each transform the same input differently |
| Daily operating decision package | Core promised output for the operator | HIGH | Must summarize what changed, what matters, risks, opportunities, and recommended actions |
| Audit trail and approval boundaries | Required to trust recurring automated decisions | MEDIUM | Especially for budget, state, and strategic changes |
| At-a-glance operating visibility | User’s stated phase-1 success metric | MEDIUM | Should show current situation, risks, opportunities, and next steps quickly |

### Differentiators (Competitive Advantage)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Forum complaint intelligence engine | Converts scattered user complaints into structured market pain maps | HIGH | Strong fit for user’s stated information bias |
| Consulting-grade / CEO-grade mixed output style | Makes results immediately useful for strategic thinking and execution | MEDIUM | Needs templates and quality controls, not just summarization |
| Decision → execution package handoff | Connects management output to implementation plans | HIGH | Produces project pack and roadmap from operating conclusions |
| Governance-aware operating loop | Makes the system feel like a real company, not a toy multi-agent demo | HIGH | Budget, approval, review, and audit embedded in flow |
| Team-ready role workspace model | Allows later expansion from solo operator to team use | MEDIUM | Requires stronger queues, ownership, and artifact discipline |

### Anti-Features (Commonly Requested, Often Problematic)

| Feature | Why Requested | Why Problematic | Alternative |
|---------|---------------|-----------------|-------------|
| Full autonomy everywhere | Feels impressive and “agentic” | Breaks trust, reviewability, and governance for strategic/company actions | Semi-autonomous flow with explicit approval gates |
| Real-time monitor-everything dashboard first | Feels like progress and visibility | High build cost before core judgment loop is stable | Start with daily loop + concise management reports |
| Too many specialist roles early | Seems more company-like | Creates coordination overhead and noisy handoffs | Keep current five-role core and sharpen responsibilities |
| Internal analytics as primary input in v1 | Easier to instrument than external intelligence | Conflicts with user’s stated goal of market-first sensing | Start with external signals, add internal metrics later |

## Feature Dependencies

```text
External signal intake
    └──requires──> source adapters and normalization
                       └──requires──> ingestion history / dedupe

Signal triage ──requires──> normalized signal records
Daily operating decision package ──requires──> role-based analysis pipeline
Project execution package ──enhances──> daily operating decision package
Board-style briefing ──enhances──> daily operating decision package
Governance workflow ──wraps──> decision package + execution package
Operating visibility ──requires──> all major artifacts to be structured
```

### Dependency Notes

- **Signal triage requires normalized records:** without a shared schema, repeated scraping and analysis become inconsistent
- **Decision package requires role-based analysis:** otherwise the system collapses into a single generic summary
- **Governance wraps outputs:** approvals and audits only make sense once the decision artifacts are stable enough to review
- **Visibility depends on structured artifacts:** dashboards or summary pages should read from decision/audit state, not from free-form prompt logs

## MVP Definition

### Launch With (v1)

- [ ] External source ingestion for industry trends, competitor intelligence, and forum/user complaints — core sensory system
- [ ] Signal normalization, triage, and priority scoring — converts noise into actionable inputs
- [ ] Role-based daily analysis pipeline — establishes real company-style collaboration
- [ ] Daily operating decision package — main deliverable for the operator
- [ ] Governance controls for approvals, budgets, and audit trails — keeps the system trustworthy
- [ ] Operating visibility summary — makes current state understandable at a glance

### Add After Validation (v1.x)

- [ ] Project execution package generation — add once decision quality is stable
- [ ] Board-style briefing generation — add once operating decision package structure is stable
- [ ] Better source adapters / richer source coverage — expand after core signal loop works

### Future Consideration (v2+)

- [ ] Team collaboration surfaces and work assignment queues — defer until solo workflow is proven
- [ ] Internal telemetry integration as first-class input — defer until market-first loop proves useful
- [ ] Real-time monitoring UI — defer until artifact/state model stabilizes

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| External signal intake | HIGH | MEDIUM | P1 |
| Signal triage and scoring | HIGH | MEDIUM | P1 |
| Daily operating decision package | HIGH | HIGH | P1 |
| Governance workflow | HIGH | HIGH | P1 |
| Operating visibility summary | HIGH | MEDIUM | P1 |
| Project execution package | MEDIUM | HIGH | P2 |
| Board-style briefing | MEDIUM | MEDIUM | P2 |
| Team-ready collaboration model | MEDIUM | HIGH | P3 |

**Priority key:**
- P1: Must have for launch
- P2: Should have, add when possible
- P3: Nice to have, future consideration

## Competitor Feature Analysis

| Feature | Generic multi-agent demos | Workflow orchestration frameworks | Our Approach |
|---------|---------------------------|-----------------------------------|--------------|
| Multi-role reasoning | Usually present, often shallow | Usually supported structurally, less domain-opinionated | Keep five stable roles with explicit management responsibilities |
| Durable workflow state | Often weak | Strong focus area | Adopt explicit artifacts/checkpoints instead of ad-hoc prompt chains |
| Human review / guardrails | Inconsistent | Increasingly first-class | Make approval and audit central to company actions |
| Output professionalism | Usually generic summaries | Not the framework’s job | Build template-driven decision packs with stronger editorial standards |

## Sources

- Official framework docs reviewed in this session: CrewAI, AutoGen, Claude Code docs targets, LangGraph docs target
- Current project context in `.planning/PROJECT.md`
- Existing brownfield architecture in `.planning/codebase/`

---
*Feature research for: AI-operated company management core / multi-agent operating system*
*Researched: 2026-04-24*
