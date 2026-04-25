# Phase 4: Governance and Control Layer - Patterns

**Mapped:** 2026-04-25
**Purpose:** Identify the closest existing repo patterns to reuse for governance event logging, approval gates, audit trace extension, and state-control enforcement.

## Phase 4 reuse map

| Plan | Goal | Closest existing files/patterns | How to reuse |
|------|------|---------------------------------|--------------|
| 04-01 | Define governance event model and approval artifact structure | `assets/shared/trace/decision_package_trace.json`, `assets/shared/AUDIT_LOG.csv`, `assets/shared/decision_packages/`, `assets/shared/execution_packages/`, `assets/shared/board_briefings/` | Reuse JSON/append-log structure and latest + history layout for governance artifacts. |
| 04-02 | Wrap high-impact decisions with executable approval and audit steps | `orchestration/cron/commands.sh`, `scripts/run_signal_analysis_loop.sh`, `docs/STATE_CONTRACT.md` §State Transition / Approval Gates, `docs/OPERATIONS.md` incident stop/resume flows | Reuse thin shell wrappers, fail-fast sequencing, and policy gates translated into pre-flight checks before protected actions. |
| 04-03 | Connect governance records to existing state and finance constraints | `assets/shared/manage_finance.py`, `skills/common/run_accountant_audit.md`, `docs/STATE_CONTRACT.md` §Write Permission Matrix / Conflict Rules | Reuse authoritative writer boundary, locking, audit logging, and role ownership constraints rather than inventing new write paths. |

## Pattern 1: Append-only audit output

### Existing source
- `assets/shared/manage_finance.py`
- `assets/shared/AUDIT_LOG.csv`

### Why it matches
`manage_finance.py` writes durable audit rows with timestamp, event type, actor, amount, and reasoning after authoritative state changes. This is the repo’s clearest example of append-first auditability for critical operations.

### How Phase 4 should reuse it
- Keep the same append-only mindset.
- Upgrade to JSONL instead of CSV because governance events need richer nested context.
- Preserve the principle that every meaningful action transition leaves a durable row/event.

### Do not copy blindly
- Do not use CSV for governance; the event shape is too rich.
- Do not log only success cases; governance must also record `requested`, `blocked`, `rejected`, `override`, and `failed`.

## Pattern 2: Latest + history artifact layout

### Existing source
- `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` + `history/`
- `assets/shared/execution_packages/EXECUTION_PACKAGE.md` + `history/`
- `assets/shared/board_briefings/BOARD_BRIEFING.md` + `history/`
- `assets/shared/external_intelligence/LATEST_SUMMARY.md` + `history/signals.jsonl`

### Why it matches
The repo already distinguishes operator-facing latest views from durable history. Latest files are for day-to-day consumption; history preserves auditability and drift analysis.

### How Phase 4 should reuse it
- Add a governance latest view under a dedicated governance subtree.
- Use JSONL as the authoritative history/event log.
- Optionally add dated markdown snapshots later, but Phase 4’s must-have is latest markdown + JSONL stream.

### Do not copy blindly
- Do not flatten governance into the decision package directories.
- Do not rely on markdown latest alone as the authority source.

## Pattern 3: Fail-fast shell orchestration

### Existing source
- `orchestration/cron/commands.sh`
- `scripts/run_signal_analysis_loop.sh`

### Why it matches
Both scripts use `#!/usr/bin/env bash` and `set -euo pipefail`, then run thin orchestration steps in sequence. They stop on failure and keep business logic in underlying scripts.

### How Phase 4 should reuse it
- Add governance wrappers as thin shell or Python entrypoints around protected actions.
- Keep policy evaluation outside shell glue where possible.
- Exit non-zero immediately after recording blocked/failed governance events.

### Do not copy blindly
- Do not bury governance rules inside a large shell `case` block.
- Do not continue after blocked critical steps just because an event was logged.

## Pattern 4: Authoritative single-writer boundary

### Existing source
- `assets/shared/manage_finance.py`
- `docs/STATE_CONTRACT.md` §Write Permission Matrix
- `skills/common/run_accountant_audit.md`

### Why it matches
The repo already protects ledger writes behind a single script and documents role ownership for business artifacts. The audit skill explicitly says to run the script rather than hand-edit `LEDGER.json`.

### How Phase 4 should reuse it
- Governance validates whether an action may proceed.
- If allowed, governance calls the existing authoritative writer.
- Governance never mutates `LEDGER.json` or role-owned markdown directly.

### Do not copy blindly
- Do not create a governance script that writes protected targets directly.
- Do not weaken primary-writer boundaries in the name of convenience.

## Pattern 5: Trace sidecar for audit chain extension

### Existing source
- `assets/shared/trace/decision_package_trace.json`
- `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`

### Why it matches
Phase 3 already established a structured trace chain from shortlist and role outputs into the operating decision package via `judgment_links`.

### How Phase 4 should reuse it
- Reference the operating package path in every governance action.
- Add optional `related_trace.trace_path` and `judgment_ids` fields for actions that derive from specific next-step or risk judgments.
- Use `action_id` as the governance-side handle rather than modifying the Phase 3 trace file for every event.

### Do not copy blindly
- Do not fork a second provenance tree that repeats upstream signal links.
- Do not make governance depend on parsing free-text markdown only when a trace file already exists.

## Pattern 6: Operator-readable summary view

### Existing source
- `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`
- `assets/shared/execution_packages/EXECUTION_PACKAGE.md`
- `assets/shared/board_briefings/BOARD_BRIEFING.md`
- `docs/OPERATIONS.md`

### Why it matches
The repo prefers human-readable markdown for day-to-day operation, with grouped sections and explicit action framing.

### How Phase 4 should reuse it
- Render a latest governance markdown view grouped by action state.
- Optimize for operator questions: what is pending, what is blocked, what was approved, what was overridden.
- Keep the machine authority in JSONL and the operator ergonomics in markdown.

### Do not copy blindly
- Do not dump raw JSONL into the markdown view.
- Do not present only a chronological list if the user needs action-centric grouping.

## Pattern 7: Policy docs as executable-source candidates

### Existing source
- `docs/STATE_CONTRACT.md`
- `docs/OPERATIONS.md`

### Why it matches
These docs already define approval gates, state progression order, fallback semantics, conflict handling, and pause/resume operations. Phase 4’s job is to encode these rules, not invent replacements.

### How Phase 4 should reuse it
- Convert approval gate rules into explicit action classification logic.
- Convert state transition order into executable blocking checks.
- Convert fallback rules into enforceable validation + event emission.

### Do not copy blindly
- Do not treat policy docs as sufficient on their own.
- Do not widen scope into full workflow redesign; encode only the documented governance constraints relevant to Phase 4.

## Candidate implementation anchors by plan

### 04-01 — Governance event model and approval artifact structure

**Best analogs**
- `assets/shared/trace/decision_package_trace.json`
- `assets/shared/AUDIT_LOG.csv`
- `assets/shared/decision_packages/` latest + history shape

**Recommended new files**
- `assets/shared/governance/governance_events.jsonl`
- `assets/shared/governance/GOVERNANCE_STATUS.md`
- `scripts/governance_common.py`
- `scripts/render_governance_status.py`

**What to borrow**
- JSON schema discipline from the trace sidecar
- Append-only persistence from the finance audit log
- Latest-view ergonomics from decision/execution/board artifacts

### 04-02 — Executable approval and audit steps

**Best analogs**
- `scripts/run_signal_analysis_loop.sh`
- `orchestration/cron/commands.sh`
- `docs/STATE_CONTRACT.md` §State Transition / Approval Gates

**Recommended new files**
- `scripts/request_governance_approval.py`
- `scripts/enforce_governed_action.py`
- targeted wrapper updates in `orchestration/cron/commands.sh` and/or governed runner scripts

**What to borrow**
- Thin orchestration wrappers
- Fail-fast sequencing
- Explicit operator-facing error messages before exit

### 04-03 — State and finance integration

**Best analogs**
- `assets/shared/manage_finance.py`
- `skills/common/run_accountant_audit.md`
- `docs/STATE_CONTRACT.md` write matrix and fallback rule text

**Recommended touch points**
- Governance rule table covering finance actions, archive-style actions, fallback takeover, and critical stage transitions
- Wrapper entrypoints that call `manage_finance.py` only after governance validation
- Fallback event emission when CEO acts on another role-owned asset

**What to borrow**
- Locking and authoritative-write pattern from `manage_finance.py`
- “Do not hand-edit state” principle from audit skill/docs
- Role ownership semantics from the state contract

## Anti-patterns to avoid

1. **Governance as a second writer**
   - Wrong: governance helpers directly edit `LEDGER.json` or role-owned markdown.
   - Right: governance only validates, records, and then calls the authoritative writer.

2. **Policy-only governance**
   - Wrong: update docs and add markdown notes, but protected actions still run unguarded.
   - Right: add executable checks before high-impact operations.

3. **Success-only event logs**
   - Wrong: only approved actions create audit records.
   - Right: request, block, reject, override, fail, and success paths all emit events.

4. **Parallel provenance chain**
   - Wrong: governance invents a separate evidence model unrelated to Phase 3 trace data.
   - Right: governance references the operating package and trace sidecar.

5. **Timeline-only latest view**
   - Wrong: markdown status file is a raw chronological dump.
   - Right: group by governance action state so the operator can act quickly.

## Recommended reuse order for implementation

1. Start from `docs/STATE_CONTRACT.md` to derive the executable rule table.
2. Use `decision_package_trace.json` and `OPERATING_DECISION_PACKAGE.md` as the upstream audit anchor.
3. Implement JSONL append helpers inspired by `manage_finance.py` + `AUDIT_LOG.csv`.
4. Add status rendering in the same operator-facing markdown style as existing shared artifacts.
5. Only then wrap high-impact actions in orchestration surfaces.

## Planning takeaway

The codebase already contains almost every pattern Phase 4 needs in partial form: append-only audit logging, latest/history artifact conventions, authoritative single-writer paths, fail-fast orchestration, and structured trace sidecars. The planning work should combine those existing shapes into one governance layer rather than introducing a new storage model, dashboard layer, or alternate mutation path.
