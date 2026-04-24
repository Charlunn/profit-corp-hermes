# Architecture Research

**Domain:** AI-operated company management core / multi-agent operating system
**Researched:** 2026-04-24
**Confidence:** MEDIUM

## Standard Architecture

### System Overview

```text
┌─────────────────────────────────────────────────────────────┐
│                    Intelligence Intake Layer                │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Trend Feeds  │  │ Competitors  │  │ Forum Complaints │   │
│  └──────┬───────┘  └──────┬───────┘  └────────┬─────────┘   │
│         │                 │                   │             │
├─────────┴─────────────────┴───────────────────┴─────────────┤
│                   Signal Processing Layer                   │
├─────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────┐  │
│  │ normalize → dedupe → cluster → score → route         │  │
│  └───────────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────────┤
│                    Multi-Role Analysis Layer               │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌──────────────┐    │
│  │ Scout   │  │ CMO     │  │ Arch    │  │ Accountant   │    │
│  └────┬────┘  └────┬────┘  └────┬────┘  └──────┬───────┘    │
│       └────────────┴──────┬─────┴──────────────┘            │
│                           ▼                                  │
│                         CEO synthesis                        │
├─────────────────────────────────────────────────────────────┤
│                   Governance & Output Layer                 │
│  decision pack │ execution pack │ board brief │ audit log   │
├─────────────────────────────────────────────────────────────┤
│                      State & History Layer                  │
│   source journal │ signal ledger │ approvals │ finances     │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| Source adapters | Pull external signals into a common schema | Feed/API/scrape utilities with source-specific parsers |
| Signal processing | Deduplicate, cluster, enrich, and prioritize raw inputs | Deterministic scoring + LLM-assisted clustering/classification |
| Role analyzers | Transform the same signal set through distinct business functions | Role-scoped prompts/skills operating on shared signal packets |
| CEO synthesis | Turn role analysis into one operating recommendation | Structured synthesis with explicit tradeoffs and decisions |
| Governance engine | Enforce approval, budget, and audit rules | Workflow gates + append-only audit artifacts |
| Output generator | Produce polished recurring artifacts | Templates for decision packs, execution packs, and board briefs |

## Recommended Project Structure

```text
assets/
├── shared/
│   ├── signals/              # normalized signal journal and snapshots
│   ├── decisions/            # recurring operating decision packages
│   ├── execution/            # project execution packages
│   ├── briefs/               # board-style briefings
│   └── audits/               # review logs and approval records
orchestration/
├── cron/                     # recurring loop prompts and command helpers
skills/
├── common/                   # shared operating skills
├── ceo/                      # synthesis / final decision skills
├── scout/                    # future role-specific ingestion/triage skills (optional)
└── governance/               # approval / audit skills (optional)
scripts/
├── ingestion/                # deterministic source collection helpers
└── reporting/                # artifact assembly helpers
```

### Structure Rationale

- **`assets/shared/signals/`:** separate raw/normalized signal state from finance and culture artifacts
- **`assets/shared/decisions/`:** recurring decision packages need durable history for operator review and trend analysis
- **`assets/shared/audits/`:** governance becomes operational only when reviews and approvals are explicit artifacts
- **`scripts/ingestion/`:** external collection should be deterministic and testable, not buried inside prompts

## Architectural Patterns

### Pattern 1: Deterministic Intake, LLM Interpretation

**What:** Use scripts/adapters for fetching and cleaning data, then use agents for analysis and synthesis.
**When to use:** Always for recurring external signal collection.
**Trade-offs:** More implementation work up front, but much better repeatability and debugging.

**Example:**
```text
forum page -> parser -> normalized signal JSON -> Scout analysis -> CEO decision pack
```

### Pattern 2: Shared Artifact Handoffs

**What:** Each role writes structured artifacts instead of only passing transient chat output.
**When to use:** Any multi-step daily loop or approval workflow.
**Trade-offs:** More files and discipline, but strong auditability and resumability.

**Example:**
```text
Scout brief -> CMO opportunity note -> Arch feasibility note -> CEO synthesis
```

### Pattern 3: Governance Wrapper Around Decisions

**What:** High-impact actions and state transitions are wrapped by explicit checks and approval steps.
**When to use:** Strategy changes, budgets, rewards, or recurring operating commitments.
**Trade-offs:** Slightly slower throughput, much better trust and control.

## Data Flow

### Request Flow

```text
[Daily cron trigger]
    ↓
[source collection] → [normalization] → [signal scoring] → [role analysis]
    ↓                                                     ↓
[history store] ← [audit/update] ← [CEO synthesis] ← [role outputs]
    ↓
[decision package + visibility summary + optional execution artifacts]
```

### State Management

```text
[source journal / signal state]
    ↓
[role workflows] ←→ [governance checks] → [approved outputs / audit history]
```

### Key Data Flows

1. **External intelligence flow:** public sources → normalized signals → role analysis → CEO decision package
2. **Governance flow:** proposed action → approval/budget check → decision log → follow-up artifact
3. **Visibility flow:** latest signal clusters + decisions + blockers → operator-facing summary

## Scaling Considerations

| Scale | Architecture Adjustments |
|-------|--------------------------|
| Solo founder / early v1 | File artifacts + Hermes cron + lightweight Python helpers are sufficient |
| Small team | Add stronger queue/state records, artifact ownership, and role-specific work folders |
| Larger org / many domains | Introduce structured database/event storage and more formal workflow engine boundaries |

### Scaling Priorities

1. **First bottleneck:** noisy source ingestion — fix with dedupe, source adapters, and scoring discipline
2. **Second bottleneck:** artifact sprawl / coordination ambiguity — fix with stricter templates and ownership boundaries

## Anti-Patterns

### Anti-Pattern 1: Prompt-Only Company Simulation

**What people do:** create many “roles” but leave all logic inside long prompts.
**Why it's wrong:** impossible to debug, audit, or run reliably every day.
**Do this instead:** move collection, state, and artifact contracts into scripts/files.

### Anti-Pattern 2: Beautiful Reports Without a Signal Engine

**What people do:** polish decision documents before the source/triage system is stable.
**Why it's wrong:** outputs look impressive but are based on inconsistent evidence.
**Do this instead:** stabilize input normalization and prioritization before heavy presentation work.

## Integration Points

### External Services

| Service | Integration Pattern | Notes |
|---------|---------------------|-------|
| Public feeds/forums/sites | Adapter-based fetch + normalize | Prefer feeds/APIs; isolate scraping logic |
| Hermes cron | Named recurring jobs | Already present in repo |
| Future LLM orchestration helpers | Supervisor/state machine wrapper | Keep optional and modular |

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| Ingestion ↔ analysis | structured signal files / records | Must be schema-stable |
| Role analysis ↔ CEO | summarized role artifacts | Avoid passing raw source noise directly |
| CEO ↔ governance | explicit approval / audit artifact | Critical for trust |

## Sources

- Official CrewAI docs (flows, crews, guardrails, memory, observability)
- Official AutoGen docs (Core/AgentChat multi-agent runtime concepts)
- Project context in `.planning/PROJECT.md`
- Brownfield codebase map in `.planning/codebase/`

---
*Architecture research for: AI-operated company management core / multi-agent operating system*
*Researched: 2026-04-24*
