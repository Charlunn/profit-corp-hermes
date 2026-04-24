# Stack Research

**Domain:** AI-operated company management core / multi-agent operating system
**Researched:** 2026-04-24
**Confidence:** MEDIUM

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| Hermes CLI runtime | current project runtime | Profile-based agent execution and cron scheduling | Already anchors this brownfield codebase; replacing it would discard existing profiles, skills, and cron flows |
| Python 3.11+ | 3.11+ | Durable state tools, ingestion utilities, scoring pipelines, and structured report generation | Strong ecosystem for scraping, parsing, ranking, and deterministic file operations |
| Markdown + YAML/JSON contracts | current repo pattern | Human-auditable artifacts and machine-readable workflow state | Fits the current repo’s governance-heavy, artifact-first operating style |
| LLM orchestration layer with durable workflow/state support | 2026 generation | Supervisor routing, retries, human approval, checkpoints, and resumable execution | Official docs across LangGraph/CrewAI/AutoGen converge on stateful orchestration + guardrails + human input for multi-agent systems |

### Supporting Libraries

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `feedparser` / RSS client | current stable | Structured ingestion from feeds, blogs, release notes, and public sources | Use when sources provide feeds instead of brittle scraping |
| `httpx` + `beautifulsoup4` | current stable | Controlled web fetching and forum/post parsing | Use for public pages, complaint threads, and competitor pages where API access is unavailable |
| `pydantic` | 2.x | Structured signal schemas, validation, and report models | Use for intelligence items, decision packages, and audit records |
| `sqlite` or lightweight local DB | built-in / current stable | Event journal, dedupe keys, and ingestion history | Use when markdown-only history becomes too fragile for repeated daily loops |
| `jinja2` | 3.x | Repeatable generation of decision packs, execution packs, and board briefings | Use once output formats stabilize and need consistent quality |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Shell smoke tests | Validate runtime, cron helpers, and critical files | Already established in `scripts/smoke_test_pipeline.sh` |
| Schema validation checks | Keep structured artifacts stable | Recommended once new ingestion/state files are introduced |
| Diff-friendly report templates | Maintain output quality | Prefer markdown templates committed to repo over opaque prompt-only rendering |

## Installation

```bash
# Core Python support for intelligence ingestion / report tooling
pip install httpx beautifulsoup4 feedparser pydantic jinja2

# Optional durable local store
pip install sqlite-utils
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|-------------------------|
| Hermes runtime + repo-native scripts | Rebuild around another orchestration runtime | Only if Hermes cannot provide the reliability hooks the project needs |
| Python ingestion/report utilities | Node.js ingestion stack | Use if future runtime standardization strongly favors JS/TS across all tooling |
| Artifact-first markdown outputs | UI-first dashboard as the primary system | Use later after report structure stabilizes; don’t start with a dashboard-only system |
| Stateful orchestration layer | Stateless prompt chaining | Avoid stateless chaining once approvals, retries, and auditability matter |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|-------------|
| Pure ad-hoc prompt chains with no persisted state | Breaks auditability, retries, and daily-loop continuity | Use explicit workflow state, checkpoints, and durable artifacts |
| Heavy autonomous execution without approval gates | Conflicts with the project’s governance and founder-oversight requirement | Keep human approval on financial, strategic, and high-impact transitions |
| Scraping-first everything | Public sites/forum HTML changes constantly and creates maintenance burden | Prefer feeds/APIs where possible; isolate scraping behind adapters |
| Dashboard-before-system | Produces a shiny surface without stable operating logic | Build ingestion, triage, decision, and governance core first |

## Stack Patterns by Variant

**If the system remains founder-operated in v1:**
- Use markdown artifacts + Python utilities + Hermes cron
- Because auditability and iteration speed matter more than multi-user infrastructure

**If the system expands to team operation:**
- Add structured state store, role-specific work queues, and template-driven output generation
- Because multiple actors need concurrency safety and repeatable review steps

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|-----------------|-------|
| Python 3.11+ | Pydantic 2.x, httpx current, Jinja2 3.x | Good default baseline for new utilities |
| Hermes runtime artifacts | Existing repo scripts and profile templates | Preserve current runtime assumptions while extending behavior |

## Sources

- `https://docs.crewai.com/` — official guidance emphasizing flows for orchestration, crews for collaboration, and built-in guardrails/memory/observability
- `https://microsoft.github.io/autogen/stable/` — official guidance for multi-agent systems via Core/AgentChat runtime patterns
- `https://code.claude.com/docs/en/overview` — official Claude Code docs target for agentic engineering workflows (redirect observed from Anthropic docs)
- `https://docs.langchain.com/oss/python/langgraph/overview` — official LangGraph documentation target for stateful orchestration (target discovered, direct fetch timed out during this session)

---
*Stack research for: AI-operated company management core / multi-agent operating system*
*Researched: 2026-04-24*
