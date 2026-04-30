# Phase 4: Governance and Control Layer - Research

**Researched:** 2026-04-25
**Domain:** governance enforcement, append-only audit trails, approval gates, state-transition control
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
### Governance event model
- **D-01:** Governance events must be recorded in a dedicated governance log rather than merged into `LEDGER.json` or scattered only across markdown artifacts.
- **D-02:** The governance log must use an append-only JSONL event-stream format.
- **D-03:** Each governance event must carry a full context field set including `action_id`, `event_type`, `actor`, `target_artifact`, `related_decision_package`, `status_before`, `status_after`, `approved_by`, and `timestamp`.
- **D-04:** The system must maintain a human-readable governance latest view in addition to the JSONL stream.
- **D-05:** The latest view must be grouped by governance action, not rendered as a flat raw timeline.
- **D-06:** Governance actions must bind back to `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` so the audit chain starts from the Phase 3 decision foundation.

### State progression and blocking
- **D-07:** High-impact actions and critical stage failures hard-block downstream progression by default.
- **D-08:** High-impact classification should be driven primarily by action type instead of only numeric thresholds.
- **D-09:** When a critical step fails, the workflow must stop at the failure point and record a failed governance event instead of auto-rolling forward.
- **D-10:** Only the CEO can override a hard block and continue the workflow.

### Write permissions and fallback control
- **D-11:** Each governed asset retains a strict primary writer boundary.
- **D-12:** CEO fallback takeover of another role's primary artifact must emit an explicit governance event with reason, target asset, original primary writer, and related operating decision package.
- **D-13:** The governance layer acts as a gatekeeping and recording layer only; it must not directly mutate protected state or business artifacts.
- **D-14:** Existing authoritative write paths remain the only mutation routes, especially `assets/shared/manage_finance.py` for ledger writes.
- **D-15:** The write-permission matrix must become executable validation rules instead of remaining documentation-only policy text.

### Claude's Discretion
- Exact file names and directory layout for the governance stream and latest view
- Exact schema field names beyond the locked minimum fields
- Exact enum names for statuses, actions, and failure codes
- Exact implementation shape of the governance checker layer

### Deferred Ideas (OUT OF SCOPE)
- Rich dashboard-style governance visualization belongs to Phase 5
- Multi-user/team approval workflows belong to later collaboration phases
- Sophisticated rollback orchestration is deferred as long as Phase 4 enforces stop-at-failure semantics
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GOV-01 | System records explicit approval outcomes for high-impact operating actions | Use a gate-before-mutate governance action wrapper that classifies high-impact actions by action type, writes `requested` / `approved` / `rejected` / `override` / `failed` events to JSONL, and requires an explicit approval artifact before any protected writer runs. [VERIFIED: repo code] |
| GOV-02 | System records an auditable trace linking signals, analyses, decisions, and governance outcomes | Extend the existing Phase 3 trace chain by adding governance references keyed by `action_id` and `related_decision_package`, with backlinks to `decision_package_trace.json`, role artifacts, and governed targets. [VERIFIED: repo code] |
</phase_requirements>

## Summary

Phase 4 should not invent a separate governance system outside the repo’s existing artifact-first operating model. The codebase already uses authoritative write paths, append-style audit records, fail-fast shell orchestration, and human-readable latest artifacts. The right move is to add a governance control layer in front of high-impact actions so approval state becomes executable before existing mutation paths run, not after the fact. [VERIFIED: repo code]

The most important architectural decision is **gate-before-mutate**. `assets/shared/manage_finance.py` already embodies a strong boundary: ledger writes happen through one authoritative script with locking and CSV audit output, while policy docs in `docs/STATE_CONTRACT.md` define when writes are allowed. Phase 4 should operationalize those policy rules by introducing governance request/decision helpers that classify actions, validate actor/target permissions, require explicit approval for high-impact operations, and only then invoke the existing authoritative writer. This preserves D-13/D-14 and keeps governance from becoming an alternate write path. [VERIFIED: repo code]

The second key planning point is to treat governance as an **append-only event stream plus operator summary view**. The repo already maintains latest + history pairs for external intelligence and decision artifacts, and `AUDIT_LOG.csv` demonstrates an append-first audit mindset. Phase 4 should follow that shape with `governance_events.jsonl` as the machine-checkable source of truth and a `GOVERNANCE_STATUS.md`-style latest view grouped into pending approvals, recently approved, recently rejected, overrides, and currently blocked actions. The markdown view is for operators; the JSONL stream is for enforcement and later verification. [VERIFIED: repo code]

The third planning point is to extend the existing Phase 3 trace chain instead of building a parallel one. `assets/shared/trace/decision_package_trace.json` already links judgments back to shortlist and role artifacts, and `OPERATING_DECISION_PACKAGE.md` is now the authoritative operating layer. Governance should add `action_id`-keyed events that reference the operating decision package path plus relevant judgment IDs, so auditors can traverse: prioritized signals → role outputs → CEO synthesis → operating decision package → governance event → protected action outcome. That satisfies GOV-02 without forcing Phase 4 to re-model upstream evidence. [VERIFIED: repo code]

**Primary recommendation:** implement Phase 4 as a thin governance control layer made of (1) executable action classification + permission rules, (2) append-only governance event recording, (3) operator-facing latest governance view, and (4) wrappers around high-impact actions and state transitions that enforce approval before calling existing authoritative scripts. [VERIFIED: repo code]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Governance event recording | API / Backend | Database / Storage | Repo-local file storage is the durable state layer; JSONL events fit the existing local artifact model. [VERIFIED: repo code] |
| Approval artifact generation | API / Backend | — | Approval logic belongs in scripts/helpers, not in markdown-only policy text. [VERIFIED: repo code] |
| Human-readable governance status | API / Backend | Frontend Server (SSR) | The repo currently exposes status through markdown artifacts and CLI output, not a web UI. [VERIFIED: repo code] |
| High-impact action classification | API / Backend | — | Classification is a rule-engine concern near the scripts that launch protected actions. [VERIFIED: repo code] |
| Ledger/state mutation | Existing authoritative writers | — | `manage_finance.py` and role-specific generators remain the only mutation entrypoints. [VERIFIED: repo code] |
| Daily-pipeline stop/continue enforcement | Frontend Server (SSR) | API / Backend | In this repo the orchestration layer is shell/cron, so gating belongs around shell entrypoints and command wrappers. [VERIFIED: repo code] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib | repo-local | Read/write JSONL, evaluate rules, render markdown latest views | Existing stateful scripts already use stdlib-only Python and file-based storage. [VERIFIED: repo code] |
| Bash | 5.2.37 | Fail-fast orchestration and pre-flight gates around governed actions | Existing orchestration already uses thin shell wrappers and `set -euo pipefail`. [VERIFIED: repo code][VERIFIED: environment probe] |
| Markdown artifacts | repo-local | Operator-readable latest governance state and approval context | Repo favors markdown-first operational visibility. [VERIFIED: repo code] |
| JSON / JSONL | repo-local | Structured latest trace sidecars and append-only event logs | Phase 3 trace sidecar and Phase 1/2 history already use JSON-family storage. [VERIFIED: repo code] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| CSV append log | repo-local | Existing pattern reference from `AUDIT_LOG.csv` | Use as a design analog only; governance itself should use JSONL, not CSV. [VERIFIED: repo code] |
| Hermes CLI | local runtime | Existing scheduler/executor boundary | Govern cron-triggered actions by wrapping `commands.sh` and pipeline scripts, not by modifying Hermes itself. [VERIFIED: repo code] |
| Existing trace sidecar | repo-local | Upstream evidence linkage | Reuse `decision_package_trace.json` identifiers instead of rebuilding upstream trace models. [VERIFIED: repo code] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Dedicated governance JSONL + latest view | Store governance fields inside `LEDGER.json` | Breaks the ledger’s finance-only authority boundary and overloads one file with unrelated concerns. [VERIFIED: repo code] |
| Gate-before-mutate wrappers | Post-hoc logging after mutation | Cannot enforce hard blocks and would fail GOV-01’s explicit approval requirement. [VERIFIED: repo code] |
| Action-type classification | Pure numeric thresholds | Misses non-financial but high-impact actions such as archive, fallback takeover, and state progression failures. [VERIFIED: repo code] |
| Reusing Phase 3 trace IDs | Fresh standalone governance provenance model | Duplicates the evidence chain and risks drift between decision and governance layers. [VERIFIED: repo code] |

**Installation:**
```bash
# No new third-party dependency is required for Phase 4 planning.
# Reuse stdlib Python + bash + existing repo-local artifacts.
```

## Architecture Patterns

### System Architecture Diagram

```text
[OPERATING_DECISION_PACKAGE.md]
           ↓
[governed action request]
           ↓
[classify action type + validate target/actor]
           ↓
[if high-impact → require approval outcome]
           ↓
[append governance event JSONL]
           ↓
[if allowed → invoke authoritative writer]
           ↓
[record succeeded/failed event]
           ↓
[render governance latest markdown view]
```

This fits the repo’s current operating shape: decision artifacts drive action, shell wrappers coordinate control flow, and authoritative writers own actual state mutation. [VERIFIED: repo code]

### Recommended Project Structure
```text
assets/
└── shared/
    └── governance/
        ├── GOVERNANCE_STATUS.md          # operator-facing latest view
        ├── governance_events.jsonl       # append-only machine-checkable source of truth
        └── history/                      # optional dated status snapshots if needed later
scripts/
├── governance_common.py                  # schema helpers, rule checks, append_event(), render_latest()
├── request_governance_approval.py        # emits requested / approved / rejected / override events
├── enforce_governed_action.py            # gate-before-mutate wrapper for protected actions
└── render_governance_status.py           # rebuilds latest markdown from JSONL
```

A `governance/` subtree under `assets/shared/` matches the existing artifact-first structure, keeps governance separate from finance state, and makes Phase 5 visibility work easier later. [ASSUMED from repo patterns]

### Pattern 1: Gate Before Authoritative Writer
**What:** Evaluate governance rules before calling protected mutation scripts or advancing pipeline state. [VERIFIED: repo code]
**When to use:** Any high-impact action such as finance changes, archive-like operations, fallback takeovers, or stage transitions. [VERIFIED: docs]
**Example:**
```python
request = build_action_request(
    action_type="finance.bounty",
    actor="ceo",
    target_artifact="assets/shared/LEDGER.json",
    related_decision_package="assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md",
)

rule_result = evaluate_governance_rules(request)
append_event("requested", request, rule_result)
if not rule_result.allowed:
    raise GovernanceBlocked(rule_result.reason)

run_manage_finance_bounty(...)
append_event("approved", request, rule_result)
```

### Pattern 2: Append-Only Governance Event Stream
**What:** Record every governance-relevant step as a JSONL event, including failed and override paths. [VERIFIED: repo code]
**When to use:** Request submission, approval, rejection, override, fallback takeover, blocked transition, and post-action result recording. [VERIFIED: docs]
**Example event shape:**
```json
{
  "action_id": "gov-20260425-001",
  "event_type": "approved",
  "action_type": "finance.revenue",
  "actor": "ceo",
  "target_artifact": "assets/shared/LEDGER.json",
  "related_decision_package": "assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md",
  "status_before": "pending",
  "status_after": "approved",
  "approved_by": "ceo",
  "timestamp": "2026-04-25T08:30:00Z"
}
```

### Pattern 3: Latest View Grouped by Governance Action
**What:** Render a markdown latest view that groups pending approvals, active blocks, recent approvals, recent rejections, and recent overrides. [VERIFIED: user constraint]
**When to use:** After each event append or as a rebuild step in smoke/audit flows. [ASSUMED from repo patterns]
**Example:**
```markdown
## Pending Approvals
- gov-20260425-003 — archive action blocked pending CEO approval

## Active Blocks
- gov-20260425-004 — finance.bounty rejected, downstream step halted

## Recent Overrides
- gov-20260425-005 — CEO override allowed fallback takeover of TECH_SPEC.md
```

### Pattern 4: Trace Extension Rather Than Trace Replacement
**What:** Governance references the Phase 3 operating package and, where relevant, the decision-package trace judgment IDs. [VERIFIED: repo code]
**When to use:** Any action derived from a recommendation, risk mitigation, or next-step from the operating package. [VERIFIED: repo code]
**Example:**
```json
{
  "related_decision_package": "assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md",
  "related_trace": {
    "trace_path": "assets/shared/trace/decision_package_trace.json",
    "judgment_ids": ["action-idea-001-prototype"]
  }
}
```

### Anti-Patterns to Avoid
- **Let governance directly edit `LEDGER.json` or role-owned markdown:** violates D-13/D-14 and breaks existing authority boundaries. [VERIFIED: repo code]
- **Only log successes:** if blocked, rejected, or failed events are omitted, operators cannot explain why the pipeline stopped. [VERIFIED: docs]
- **Treat all approvals as finance-only:** archive, fallback takeover, and state progression are also high-impact according to the existing contract. [VERIFIED: docs]
- **Render a raw timeline only:** a flat event dump is weaker for operators than grouped action-state summaries. [VERIFIED: user constraint]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| New mutation path for ledger/state | Direct governance writes | Call existing authoritative scripts after approval passes | Preserves current authority boundaries and lock semantics. [VERIFIED: repo code] |
| Parallel provenance tree | Separate governance-only evidence model | Reference `OPERATING_DECISION_PACKAGE.md` and `decision_package_trace.json` | Keeps one coherent audit chain. [VERIFIED: repo code] |
| Dashboard-first visibility | New app/UI | Markdown latest view grouped by action state | Matches current repo visibility style and Phase 5 scope split. [VERIFIED: repo code] |
| Open-ended policy engine | General-purpose DSL | Small explicit action-type rule table | Scope is limited and concrete for Phase 4. [ASSUMED] |

**Key insight:** Phase 4 is not about making governance “smart”; it is about making governance unavoidable. The strongest implementation is the smallest one that sits in front of existing writers, records every decision transition, and stops unsafe progression by default. [VERIFIED: docs]

## Common Pitfalls

### Pitfall 1: Logging after mutation
**What goes wrong:** Protected actions run even when approval state is missing, and governance becomes a reporting layer only.
**Why it happens:** Logging is easier to add after existing scripts than real gates.
**How to avoid:** Make approval validation the first step in wrappers around finance/state transitions.
**Warning signs:** A rejection event exists but the ledger or downstream artifact still changed. [VERIFIED: docs]

### Pitfall 2: Treating overrides as generic approvals
**What goes wrong:** The system cannot tell normal approvals from exceptional CEO-only override paths.
**Why it happens:** Override is stored as a free-text note instead of a distinct event type.
**How to avoid:** Encode `override` as its own action/event type with `approved_by=ceo` and explicit reason fields.
**Warning signs:** You cannot query how many hard blocks were bypassed in a day. [ASSUMED]

### Pitfall 3: Fallback takeover without audit binding
**What goes wrong:** CEO can edit another role’s artifact with no structured record.
**Why it happens:** Existing docs allow fallback semantically, but the repo has no executable enforcement yet.
**How to avoid:** Any fallback request must record original primary writer, takeover reason, target path, and related decision package before the fallback write proceeds.
**Warning signs:** `TECH_SPEC.md` changes under CEO flow with no governance event pointing to it. [VERIFIED: docs]

### Pitfall 4: Not halting on failure
**What goes wrong:** The pipeline keeps running after a failed critical step and leaves partial state that looks valid.
**Why it happens:** Existing shell orchestration is linear, so it is tempting to append failure logs and continue.
**How to avoid:** Preserve fail-fast behavior in shell wrappers and explicitly record failed/blocking events before exiting non-zero.
**Warning signs:** Later artifacts update after a blocked finance/state action. [VERIFIED: repo code]

## Code Examples

Verified patterns from repo code:

### Authoritative ledger write path with append-style audit
```python
# Source: assets/shared/manage_finance.py
with _ledger_lock():
    ledger = load_ledger()
    ...
    save_ledger(ledger)
    log_event("revenue", source_agent, amount, reasoning)
```
This is the exact pattern Phase 4 should protect rather than replace. [VERIFIED: repo code]

### Fail-fast orchestration wrapper style
```bash
# Source: orchestration/cron/commands.sh
run_analysis_loop() {
  bash "$ROOT_DIR/scripts/run_signal_analysis_loop.sh"
}
```
Phase 4 wrappers should stay thin in this same style and avoid embedding business logic in shell glue. [VERIFIED: repo code]

### Existing trace sidecar contract
```json
// Source: assets/shared/trace/decision_package_trace.json
{
  "operating_package_path": "assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md",
  "judgment_links": [...]
}
```
Governance should attach to this chain, not bypass it. [VERIFIED: repo code]

## Implementation Guidance for Planning

1. **04-01 should define the schema and paths first.** Lock the governance directory, JSONL schema, latest markdown sections, and action-type taxonomy before wiring any flows.
2. **04-02 should wrap high-impact actions and failures.** Implement request/approve/reject/override/failed event emission plus wrappers around finance and state-transition surfaces.
3. **04-03 should connect to existing state and finance boundaries.** Enforce the write-permission matrix from `docs/STATE_CONTRACT.md`, add fallback takeover rules, and keep `manage_finance.py` as the sole ledger writer.
4. **Verification must prove blocking behavior.** A rejected or missing approval must stop the downstream action and still append a machine-checkable governance event.

## Recommended Verification Surface

- Schema validation over `governance_events.jsonl`
- A smoke path that requests and approves a governed action, then confirms the authoritative writer ran
- A blocked path that omits approval and confirms the authoritative writer did not run
- A failure path that records a `failed` governance event and exits non-zero
- A CEO override path that records `override` distinctly from normal approval

## Final Recommendation

Plan Phase 4 as three narrow slices:
1. **Schema + artifacts** for governance events and latest status.
2. **Executable gates** around high-impact actions and critical step failures.
3. **State/finance integration** that encodes the write-permission matrix and fallback/override semantics without introducing a second mutation path.

## RESEARCH COMPLETE
