# Pitfalls Research

**Domain:** AI-operated company management core / multi-agent operating system
**Researched:** 2026-04-24
**Confidence:** MEDIUM

## Critical Pitfalls

### Pitfall 1: Mistaking role prompts for a real operating system

**What goes wrong:**
The project appears multi-agent on paper, but role outputs are inconsistent, unauditable, and not durable enough for daily use.

**Why it happens:**
Teams over-invest in persona prompts before creating signal schemas, handoff artifacts, and workflow state.

**How to avoid:**
Make deterministic ingestion, structured signal records, and artifact-based handoffs the base layer before expanding role sophistication.

**Warning signs:**
- Same source leads to materially different outputs day to day
- No durable record of why CEO reached a decision
- Recovery requires rereading long chat context instead of artifacts

**Phase to address:**
Phase 1–2

---

### Pitfall 2: Output polish without evidence quality

**What goes wrong:**
Decision packs look professional but are driven by weak, duplicated, stale, or noisy inputs.

**Why it happens:**
Presentation work is easier to feel than source validation and triage infrastructure.

**How to avoid:**
Build source adapters, dedupe, signal scoring, and evidence linking before heavy report polishing.

**Warning signs:**
- Reports repeat anecdotes without source diversity
- Competitor and user-signal sections feel generic
- Operator cannot trace a recommendation back to evidence

**Phase to address:**
Phase 1–3

---

### Pitfall 3: Governance that exists only in documentation

**What goes wrong:**
Approval rules, budget controls, and audit requirements are documented but can be bypassed in everyday operation.

**Why it happens:**
Governance is treated as policy text instead of executable workflow constraints.

**How to avoid:**
Wrap decisions and state mutations with explicit gates, structured approval artifacts, and append-only audit logs.

**Warning signs:**
- Strategic actions can happen without recorded approval
- Ledger-related decisions are discussed outside sanctioned mutation paths
- No concise audit record for daily loop outputs

**Phase to address:**
Phase 3–4

---

### Pitfall 4: Trying to do full autonomy too early

**What goes wrong:**
The system acts beyond the operator’s comfort level, reducing trust and making correction expensive.

**Why it happens:**
Autonomy is mistaken for usefulness.

**How to avoid:**
Keep semi-autonomous loops with explicit review for financial, strategic, or irreversible actions.

**Warning signs:**
- Operator stops trusting outputs
- Manual correction work increases after each run
- Important actions happen without a clean approval step

**Phase to address:**
Phase 2–4

---

### Pitfall 5: Dashboard-first development

**What goes wrong:**
A UI is built before the operating loop is reliable, producing visibility theater instead of actual clarity.

**Why it happens:**
Dashboards create a strong impression of progress.

**How to avoid:**
Make visibility read from stable decision/state artifacts only after the daily loop and governance signals are trustworthy.

**Warning signs:**
- Dashboard metrics don’t match actual decisions
- Manual interpretation is still required to know what to do next
- The UI becomes a second source of truth

**Phase to address:**
Phase 4–5

---

## Technical Debt Patterns

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Put ingestion logic inside prompts | Fast to prototype | Impossible to test/debug/reuse well | Only for one-off exploration, not daily loops |
| Store everything as unstructured markdown blobs | Easy to inspect | Hard to dedupe, score, diff, and summarize systematically | Acceptable early if paired with small structured indexes |
| Reuse one report template for all audiences | Faster output generation | Decision pack, execution pack, and board brief lose clarity | Acceptable only before output types are differentiated |
| Add more roles to fix quality | Feels like richer reasoning | Coordination complexity explodes | Rarely acceptable in v1 |

## Integration Gotchas

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|------------------|
| Public forums | Scrape HTML directly with no source abstraction | Build source-specific adapters and expect breakage |
| Competitor intelligence | Treat homepage changes as strategy evidence | Capture structured competitor events with evidence links |
| Hermes cron | Assume recurring jobs imply durable workflow state | Persist state artifacts explicitly between runs |
| LLM orchestration helper | Replace repo-native governance with framework magic | Use frameworks only to strengthen state/flow, not to hide it |

## Performance Traps

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|----------------|
| No dedupe or clustering | Daily reports balloon with repeated signals | Deduplicate by source/content/signature before analysis | Breaks as soon as source count grows modestly |
| Re-analyzing all history every run | Slow, expensive loops | Use incremental source journal + only analyze new/high-priority deltas | Breaks once daily history accumulates |
| Too many parallel role passes on raw input | Token cost spikes and output quality drops | Pre-triage signals before role analysis | Breaks when forum complaint volume rises |

## Security Mistakes

| Mistake | Risk | Prevention |
|---------|------|------------|
| Mixing strategic approvals with unlogged chat decisions | No auditability for high-impact decisions | Require structured approval records for strategic actions |
| Letting ingestion scripts write shared state broadly | State corruption or unclear ownership | Keep write scopes narrow and documented |
| Treating public forum content as trustworthy fact | Strategic misreads and manipulation risk | Require evidence grading and source context |

## UX Pitfalls

| Pitfall | User Impact | Better Approach |
|---------|-------------|-----------------|
| Overlong reports with weak prioritization | Operator still doesn’t know what to do next | Put top decisions, risks, and actions first |
| Too much framework jargon in outputs | Reports feel technical, not managerial | Use management language with linked evidence appendix |
| Too many simultaneous priorities | Daily loop becomes stressful rather than clarifying | Force ranking: now / next / later |

## "Looks Done But Isn't" Checklist

- [ ] **Daily decision package:** Often missing explicit recommendation ranking — verify top actions are prioritized
- [ ] **Signal ingestion:** Often missing dedupe/history tracking — verify repeated complaints collapse into clusters
- [ ] **Governance flow:** Often missing executable approval step — verify high-impact actions record approval outcome
- [ ] **Visibility layer:** Often missing linkage to evidence — verify operator can trace claims back to sources
- [ ] **Role collaboration:** Often missing distinct responsibilities — verify outputs are not just generic rephrasings of each other

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|---------------|----------------|
| Prompt-only operating flow | MEDIUM | Introduce signal schema, artifact handoffs, and minimal state store incrementally |
| Low-quality evidence base | MEDIUM | Rebuild source pipeline, dedupe history, and add evidence citations to outputs |
| Governance bypass | HIGH | Freeze high-impact actions, reintroduce approval/audit wrappers, and backfill logs |
| Autonomy overreach | MEDIUM | Pull decisions back to approval-required mode and narrow automatic actions |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|------------------|--------------|
| Prompt-only operating flow | Phase 1 | Daily loop persists structured inputs/outputs outside chat context |
| Weak evidence quality | Phase 2 | Decision package cites prioritized, deduped signal evidence |
| Governance only in docs | Phase 3 | Strategic/budget actions require recorded approval artifacts |
| Dashboard-first distortion | Phase 4 | Visibility view reads directly from trusted artifacts/state |

## Sources

- Official framework docs reviewed during research
- Current project constraints in `.planning/PROJECT.md`
- Existing repo governance and architecture documents

---
*Pitfalls research for: AI-operated company management core / multi-agent operating system*
*Researched: 2026-04-24*
