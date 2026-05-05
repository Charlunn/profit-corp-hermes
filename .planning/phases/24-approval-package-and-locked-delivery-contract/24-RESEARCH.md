# Phase 24: Approval Package and Locked Delivery Contract - Research

**Researched:** 2026-05-04 [VERIFIED: local system date]
**Domain:** Approval governance, proposal packaging, authoritative contract persistence, and drift enforcement in the existing Hermes delivery pipeline [VERIFIED: .planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md]
**Confidence:** HIGH [VERIFIED: codebase review + passing local tests]

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
### Proposal bundle shape
- **D-01:** Hermes should produce one final proposal bundle derived from qualified artifacts, not a loose collection of discovery notes the operator must reconcile manually.
- **D-02:** The proposal must summarize pain point, target user, pricing path, market rationale, build scope, expected launch outcome, and the reasons the candidate passed qualification gates.
- **D-03:** The proposal should remain concise for chat consumption, but every claim must backlink to authoritative artifacts so approval is evidence-backed rather than trust-me orchestration.

### Chat approval protocol
- **D-04:** Approval and rejection from chat should map onto the existing governed approval/event model rather than bypassing it with an untracked bot-only state change.
- **D-05:** Hermes should treat one explicit reply in the originating conversation as the authoritative approval decision, and decision handling must be idempotent so duplicate chat messages do not fork authority.
- **D-06:** If the operator response is ambiguous, incomplete, or cannot be linked to the proposal/run id, the run should block instead of guessing a contract state.

### Locked contract persistence
- **D-07:** Approval must persist one authoritative contract record that downstream delivery reads as source of truth for scope, pricing, required languages, acceptance gates, and approved product framing.
- **D-08:** The locked contract should extend the existing approved-project authority bundle rather than inventing a second downstream delivery record type.
- **D-09:** Chat-origin metadata, qualification proof links, and proposal identity should be persisted into the authoritative contract so later delivery/handoff can trace back to the exact approved decision.

### Drift and reopen governance
- **D-10:** Downstream delivery may not silently change approved scope, pricing, or acceptance gates; any such change should open a blocked drift/reopen state with explicit reason codes.
- **D-11:** Scope expansion or protected-platform deviations after approval should continue to use governance-backed reopen mechanics rather than side-channel operator messages.
- **D-12:** Operator-facing status and final review surfaces must be able to explain whether the active delivery still matches the approved contract and what exact contract field drifted when it does not.

### the agent's Discretion
- Exact proposal markdown/chat formatting, as long as required evidence-backed sections remain present and concise.
- Exact contract field nesting inside the approved-project record, as long as downstream specialists can read stable canonical fields.
- Exact idempotency key for chat approval handling, as long as duplicate approval messages cannot produce divergent authority state.

### Deferred Ideas (OUT OF SCOPE)
- Rich multi-operator approval workflows remain out of scope for this milestone.
- Full post-approval autonomous continuation and final chat handoff belong to Phase 25.
- Recovery commands from chat after approval failure remain later-scope work beyond the one-shot approve/reject contract.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PROP-01 | Hermes presents one operator-facing proposal bundle that summarizes pain point, target user, scope, pricing, market rationale, and expected launch path. [VERIFIED: .planning/REQUIREMENTS.md] | Reuse the approved-project brief pattern and extend it with proposal-only sections plus backlink evidence. [VERIFIED: tests/test_delivery_ready_brief.py, assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md] |
| PROP-02 | Operator can approve or reject the proposal from chat, and approval persists a single authoritative approved-project contract. [VERIFIED: .planning/REQUIREMENTS.md] | Route chat replies through `scripts/request_governance_approval.py` semantics, then persist into `APPROVED_PROJECT.json` rather than a second record type. [VERIFIED: scripts/request_governance_approval.py, scripts/start_approved_project_delivery.py, .planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md] |
| AUTO-01 | Approved-project contracts lock scope, pricing, language requirements, and acceptance gates so downstream delivery cannot drift silently. [VERIFIED: .planning/REQUIREMENTS.md] | Keep `APPROVED_PROJECT.json` as the source of truth, enforce explicit block reasons, and use governed scope reopen for drifted changes. [VERIFIED: scripts/start_approved_project_delivery.py, scripts/request_scope_reopen.py, tests/test_scope_reopen_flow.py] |
</phase_requirements>

## Summary

Phase 24 should be planned as a brownfield contract-extension phase, not a greenfield proposal engine. The codebase already has the two critical seams this phase needs: an append-only governance approval model with `request/approve/reject/override` transitions, and a single approved-project authority bundle that downstream delivery reads through stable artifact paths and fixed field names. [VERIFIED: scripts/request_governance_approval.py, scripts/start_approved_project_delivery.py, tests/test_delivery_orchestration_contract.py]

The planning target is therefore to insert one evidence-backed proposal bundle immediately before the existing approved-project delivery entrypoint, make chat approval drive the same governance event stream, and enrich the approved-project record with proposal identity, chat-origin metadata, and qualification backlinks. That preserves D-04, D-08, and the repo-wide “one durable truth plus append-only history” pattern. [VERIFIED: .planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md, tests/test_approved_project_record.py, tests/test_scope_reopen_flow.py]

The main design risk is not formatting. It is authority fragmentation. If planning introduces a second contract file, approval state inferred from chat memory, or drift checks that only warn instead of block, Phase 24 will violate both the roadmap success criteria and the existing delivery governance contract. [VERIFIED: .planning/ROADMAP.md, .planning/REQUIREMENTS.md, tests/test_delivery_orchestration_contract.py, tests/test_scope_reopen_flow.py]

**Primary recommendation:** Extend `APPROVED_PROJECT.json` and `PROJECT_BRIEF.md` generation to produce a proposal-first, contract-backed approval flow, and treat chat approval as a governed event that writes into the same authority record downstream delivery already consumes. [VERIFIED: scripts/start_approved_project_delivery.py, scripts/request_governance_approval.py]

## Project Constraints (from CLAUDE.md)

- Frontend UI work must invoke `/ui-ux-pro-max` before proposing implementation changes. [VERIFIED: CLAUDE.md, AGENTS.md]
- `/ui-ux-pro-max` output is the design source of truth for layout, typography, color, spacing, responsiveness, accessibility, and interaction details. [VERIFIED: CLAUDE.md, AGENTS.md]
- If frontend UI work is touched and the skill is missing, restore it with `uipro init --ai claude` from the project root. [VERIFIED: CLAUDE.md]
- This phase is not primarily frontend work, but existing approved-project records already encode `/ui-ux-pro-max` as a required UI artifact contract for downstream delivery. [VERIFIED: scripts/start_approved_project_delivery.py, tests/test_approved_project_record.py]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Proposal bundle composition | API / Backend [VERIFIED: scripts/start_approved_project_delivery.py] | Database / Storage [VERIFIED: approved-project artifacts are persisted files in repo state] | Proposal content is derived and rendered by Python orchestration scripts, then persisted as contract artifacts. [VERIFIED: scripts/start_approved_project_delivery.py, tests/test_delivery_ready_brief.py] |
| Chat approval / rejection interpretation | API / Backend [VERIFIED: .planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md] | Database / Storage [VERIFIED: governance events are append-only persisted records] | The authoritative decision is a governed state transition, not a client-side chat UI state. [VERIFIED: scripts/request_governance_approval.py, .planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md] |
| Locked contract persistence | Database / Storage [VERIFIED: scripts/start_approved_project_delivery.py] | API / Backend [VERIFIED: scripts write the bundle] | The record of truth is `APPROVED_PROJECT.json` plus associated artifacts. [VERIFIED: scripts/start_approved_project_delivery.py, tests/test_approved_project_record.py] |
| Drift detection and reopen gating | API / Backend [VERIFIED: scripts/request_scope_reopen.py] | Database / Storage [VERIFIED: governance + delivery events are persisted] | Drift becomes a blocked governed event and recorded delivery status, not a UI-only warning. [VERIFIED: scripts/request_scope_reopen.py, tests/test_scope_reopen_flow.py] |
| Operator-facing proposal / status rendering | API / Backend [VERIFIED: Markdown artifacts are script-rendered] | Browser / Client [ASSUMED] | The repo currently renders Markdown/operator artifacts from scripts; later chat surfaces may display them, but display transport is not the authority owner. [VERIFIED: tests/test_delivery_ready_brief.py, assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python runtime | 3.11.15 [VERIFIED: local environment command `python --version`] | Existing orchestration scripts, JSON/Markdown contract generation, governance event handling. [VERIFIED: scripts/request_governance_approval.py, scripts/start_approved_project_delivery.py] | The entire approval and delivery contract path in this repo is already implemented in Python scripts. [VERIFIED: scripts/request_governance_approval.py, scripts/start_approved_project_delivery.py] |
| Python standard library (`argparse`, `json`, `pathlib`, `datetime`, `unittest`) | Bundled with Python 3.11.15 [VERIFIED: codebase imports + local environment `python --version`] | CLI entrypoints, artifact serialization, path handling, and unit tests. [VERIFIED: scripts/request_governance_approval.py, scripts/start_approved_project_delivery.py, tests/*.py] | Phase 24 can extend existing patterns without adding a new runtime dependency. [VERIFIED: codebase review] |
| Repo authority artifacts (`APPROVED_PROJECT.json`, `PROJECT_BRIEF.md`, governance JSONL/Markdown status) | Existing repo contract [VERIFIED: scripts/start_approved_project_delivery.py, scripts/request_governance_approval.py] | Persist proposal approval truth, downstream contract fields, and status views. [VERIFIED: scripts/start_approved_project_delivery.py, tests/test_delivery_orchestration_contract.py] | Downstream delivery already depends on these explicit paths and field names. [VERIFIED: tests/test_delivery_orchestration_contract.py] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 8.4.2 [VERIFIED: local environment command `pytest --version`] | Fast execution of phase-level regression tests. [VERIFIED: local environment command `pytest --version`] | Use for planner verification commands and focused regression on approval/brief/reopen behavior. [VERIFIED: tests/test_approved_project_record.py, tests/test_scope_reopen_flow.py] |
| Governance approval CLI (`scripts/request_governance_approval.py`) | Repo-local script revision as of 2026-05-04 [VERIFIED: codebase file present] | Request/approve/reject/override state transitions with append-only history. [VERIFIED: scripts/request_governance_approval.py] | Use as the only approval state transition entrypoint for chat decisions. [VERIFIED: .planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md, scripts/request_governance_approval.py] |
| Scope reopen CLI (`scripts/request_scope_reopen.py`) | Repo-local script revision as of 2026-05-04 [VERIFIED: codebase file present] | Governance-backed drift escalation for protected changes or scope expansion. [VERIFIED: scripts/request_scope_reopen.py] | Use when approved scope, pricing, or protected platform boundaries drift after approval. [VERIFIED: .planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md, tests/test_scope_reopen_flow.py] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Extend `APPROVED_PROJECT.json` [VERIFIED: .planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md] | Separate proposal contract file [ASSUMED] | This would increase record duplication and risk downstream divergence from the existing delivery contract readers. [VERIFIED: tests/test_delivery_orchestration_contract.py] |
| Governed approval events [VERIFIED: scripts/request_governance_approval.py] | Chat-memory-only approval state [ASSUMED] | This would violate the repo’s append-only authority pattern and remove durable auditability. [VERIFIED: .planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md, tests/test_delivery_orchestration_contract.py] |

**Installation:**
```bash
# No new package installation is indicated by the current codebase pattern. [VERIFIED: codebase review]
```

**Version verification:** The active local tooling for this phase is Python `3.11.15` and pytest `8.4.2`. [VERIFIED: local environment commands `python --version`, `pytest --version`]

## Architecture Patterns

### System Architecture Diagram

```text
Qualified artifacts from Phase 23
    |
    v
Proposal bundle builder
    |
    +--> Evidence backlinks resolver
    |
    v
Operator-facing proposal artifact + proposal/run identity
    |
    v
Chat reply intake from originating conversation
    |
    +--> ambiguous / missing proposal link? --> Blocked approval state
    |
    +--> explicit reject --> governance event append --> rejected status render
    |
    +--> explicit approve --> governance event append
                                  |
                                  v
                      Approved-project contract writer
                                  |
                                  +--> APPPROVED_PROJECT.json authority record
                                  +--> PROJECT_BRIEF.md / entrypoint artifacts
                                  +--> chat/proposal metadata + qualification backlinks
                                  |
                                  v
                        Downstream delivery pipeline
                                  |
                                  +--> drift from locked contract? --> scope reopen request + blocked status
                                  |
                                  v
                           Normal delivery continuation
```

### Recommended Project Structure
```text
scripts/
├── request_governance_approval.py     # Governed request/approve/reject/override transitions
├── start_approved_project_delivery.py # Authority bundle + brief generation + pipeline state
├── request_scope_reopen.py            # Drift / protected-change escalation
└── [phase-24 helper if needed]        # Proposal rendering or chat-to-governance bridge

assets/shared/approved-projects/
└── <project-slug>/
   ├── APPROVED_PROJECT.json           # Authoritative locked contract
   ├── PROJECT_BRIEF.md                # Stable downstream brief
   └── FINAL_OPERATOR_REVIEW.md        # Operator-facing downstream review

assets/shared/governance/
├── governance_events.jsonl            # Append-only approval history
└── GOVERNANCE_STATUS.md               # Operator-visible governance state
```

### Pattern 1: Single Authority Record Extension
**What:** Add proposal identity, chat-origin metadata, and qualification backlinks into the existing approved-project record instead of creating a parallel proposal contract. [VERIFIED: .planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md, tests/test_approved_project_record.py]
**When to use:** Whenever approval outcome must drive downstream scope, pricing, languages, acceptance gates, and operator traceability. [VERIFIED: .planning/REQUIREMENTS.md]
**Example:**
```python
# Source: scripts/start_approved_project_delivery.py
def collect_missing_inputs(payload: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    approval_evidence = payload.get("approval_evidence")
    if not isinstance(approval_evidence, dict) or not normalize_list(list(approval_evidence.values())):
        missing.append("approval_evidence")
    if not normalize_list(list(payload.get("acceptance_gates", []))):
        missing.append("acceptance_gates")
    required_languages = normalize_required_languages(list(payload.get("required_languages", [])))
    if not required_languages or "en" not in required_languages or "zh" not in required_languages:
        missing.append("required_languages")
    return missing
```

### Pattern 2: Governed Approval Transition, Not Direct State Mutation
**What:** Convert chat approval into `request` + `approve` or `reject` governance events, using the existing append-only event model. [VERIFIED: scripts/request_governance_approval.py]
**When to use:** For every operator decision that changes contract state. [VERIFIED: docs/STATE_CONTRACT.md, scripts/request_governance_approval.py]
**Example:**
```python
# Source: scripts/request_governance_approval.py
def require_pending(action_id: str) -> dict[str, Any]:
    latest = find_latest_event(action_id, load_jsonl(GOVERNANCE_EVENTS_PATH))
    if latest is None:
        raise GovernanceApprovalError(f"action_id not found: {action_id}")
    if str(latest.get("status_after", "")).lower() != "pending":
        raise GovernanceApprovalError(f"action_id is not pending: {action_id}")
    return latest
```

### Pattern 3: Drift Fails Closed Through Reopen
**What:** If delivery needs protected-path changes or out-of-brief expansion, emit a governed reopen request and stop normal stage completion. [VERIFIED: scripts/request_scope_reopen.py, tests/test_scope_reopen_flow.py]
**When to use:** For any post-approval attempt to change locked scope, platform boundaries, or protected implementation surfaces. [VERIFIED: .planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md]
**Example:**
```python
# Source: scripts/request_scope_reopen.py
def build_delivery_event(*, run_id: str, workspace: Path, role: str, stage: str, target_artifact: str, reason: str, timestamp: str) -> dict[str, Any]:
    return {
        "run_id": run_id,
        "role": role,
        "stage": stage,
        "action": "scope_reopen_requested",
        "artifact": target_artifact,
        "outcome": "pending",
        "gate_status": "pending",
        "scope_status": "scope-reopen-requested",
        "reason": reason,
    }
```

### Anti-Patterns to Avoid
- **Second approval truth store:** Adding a separate proposal contract file that downstream delivery can ignore. [VERIFIED: .planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md, tests/test_delivery_orchestration_contract.py]
- **Chat-state authority:** Treating freeform chat history as authoritative approval state. [VERIFIED: tests/test_delivery_orchestration_contract.py, tests/test_delivery_ready_brief.py]
- **Soft drift warnings:** Logging contract mismatch without opening a blocked reopen path. [VERIFIED: .planning/ROADMAP.md, tests/test_scope_reopen_flow.py]
- **Approval guessing:** Auto-approving ambiguous replies instead of blocking for missing proposal/run linkage. [VERIFIED: .planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Approval state machine | New bespoke chat-approval workflow engine [ASSUMED] | `scripts/request_governance_approval.py` transitions and append-only events. [VERIFIED: scripts/request_governance_approval.py] | The repo already has pending/approved/rejected/override semantics and status refresh. [VERIFIED: scripts/request_governance_approval.py] |
| Downstream contract handoff | New delivery record schema [ASSUMED] | Existing approved-project bundle and explicit artifact paths. [VERIFIED: scripts/start_approved_project_delivery.py, tests/test_delivery_orchestration_contract.py] | Delivery tooling already expects exact field names and paths. [VERIFIED: tests/test_delivery_orchestration_contract.py] |
| Drift remediation | Ad hoc operator DM or manual override note [ASSUMED] | `scripts/request_scope_reopen.py` with governance + delivery event writes. [VERIFIED: scripts/request_scope_reopen.py, tests/test_scope_reopen_flow.py] | The existing flow already blocks and records reopen state durably. [VERIFIED: tests/test_scope_reopen_flow.py] |

**Key insight:** The complexity in this domain is contract continuity, not proposal rendering. Reusing the current governance and approved-project seams avoids hidden state and downstream contract skew. [VERIFIED: scripts/request_governance_approval.py, scripts/start_approved_project_delivery.py, tests/test_delivery_orchestration_contract.py]

## Common Pitfalls

### Pitfall 1: Proposal Bundle Is Human-Readable but Not Machine-Lockable
**What goes wrong:** The operator sees a good proposal, but the approved fields do not map cleanly into `APPROVED_PROJECT.json`. [VERIFIED: .planning/REQUIREMENTS.md, tests/test_approved_project_record.py]
**Why it happens:** Proposal text is composed separately from the downstream authority schema. [ASSUMED]
**How to avoid:** Plan proposal sections so each required claim has a canonical storage field and a backlink source. [VERIFIED: .planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md, tests/test_approved_project_record.py]
**Warning signs:** Pricing, required languages, or acceptance gates appear in chat copy but not in the persisted record. [VERIFIED: .planning/REQUIREMENTS.md, tests/test_approved_project_record.py]

### Pitfall 2: Duplicate Chat Messages Fork Approval Authority
**What goes wrong:** Two approval messages create multiple approved outcomes or double-write contract state. [VERIFIED: D-05 in 24-CONTEXT.md]
**Why it happens:** `request_governance_approval.py` generates a fresh `action_id` per request and only guards decision transitions by pending status; idempotent chat binding is not implemented there automatically. [VERIFIED: scripts/request_governance_approval.py]
**How to avoid:** Add a planner task to define and persist a stable chat approval idempotency key bound to proposal identity + run id + conversation source. [VERIFIED: 24-CONTEXT.md; idempotency requirement is explicit]
**Warning signs:** Approval bridge code can re-enter `request` more than once for the same proposal without first resolving prior state. [ASSUMED]

### Pitfall 3: Drift Detection Covers Scope but Misses Pricing or Acceptance Gates
**What goes wrong:** Delivery appears “within brief” while monetization, language pack, or acceptance criteria have shifted. [VERIFIED: AUTO-01 in .planning/REQUIREMENTS.md]
**Why it happens:** Existing reopen examples focus on protected paths and explicit scope expansion, not yet on all proposal contract fields. [VERIFIED: scripts/request_scope_reopen.py, tests/test_scope_reopen_flow.py]
**How to avoid:** Treat pricing, required languages, and acceptance gates as first-class locked contract fields and compare them explicitly before downstream stage progression. [VERIFIED: .planning/REQUIREMENTS.md, .planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md]
**Warning signs:** Stage logic only checks file path drift or scope notes, with no contract-field diff for monetization or acceptance gates. [ASSUMED]

## Code Examples

Verified patterns from official repo sources:

### Required Contract Field Validation
```python
# Source: scripts/start_approved_project_delivery.py
if not normalize_list(list(payload.get("acceptance_gates", []))):
    missing.append("acceptance_gates")
if not normalize_list(list(payload.get("monetization", []))):
    missing.append("monetization")
required_languages = normalize_required_languages(list(payload.get("required_languages", [])))
if not required_languages or "en" not in required_languages or "zh" not in required_languages:
    missing.append("required_languages")
```

### Stable Artifact Path Contract
```python
# Source: scripts/start_approved_project_delivery.py
return {
    "authority_record_path": (project_directory / "APPROVED_PROJECT.json").as_posix(),
    "delivery_brief_path": (project_directory / "PROJECT_BRIEF.md").as_posix(),
    "project_metadata_path": ".hermes/project-metadata.json",
    "shared_backend_guardrails_path": ".hermes/shared-backend-guardrails.json",
    "approved_brief_entrypoint_path": ".hermes/PROJECT_BRIEF_ENTRYPOINT.md",
    "gsd_constraints_path": str(gsd_constraints_path).strip(),
}
```

### Pending-Only Decision Transition
```python
# Source: scripts/request_governance_approval.py
if args.command == "request":
    event = build_request_event(args)
elif args.command == "approve":
    event = build_decision_event(args, "approved", "approved")
elif args.command == "reject":
    event = build_decision_event(args, "rejected", "rejected")
append_event(event)
refresh_status_view()
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Delivery handoff inferred from informal artifacts or operator memory [ASSUMED] | Delivery now expects explicit approved brief and fixed bundle field names. [VERIFIED: tests/test_delivery_orchestration_contract.py, docs/skill-governance/templates/orchestrator-input-template-v0.2.md] | In place by v1.1 and validated through earlier phases referenced by Phase 24 context. [VERIFIED: .planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md, .planning/PROJECT.md] | Phase 24 must preserve exact path/field continuity. [VERIFIED: tests/test_delivery_orchestration_contract.py] |
| Post-approval changes could be described informally [ASSUMED] | Protected changes and out-of-brief work now open governed pending reopen state. [VERIFIED: scripts/request_scope_reopen.py, tests/test_scope_reopen_flow.py] | Present in current repo as of 2026-05-04. [VERIFIED: codebase files present] | Contract drift should block, not silently mutate. [VERIFIED: .planning/ROADMAP.md, tests/test_scope_reopen_flow.py] |

**Deprecated/outdated:**
- Freeform chat state as downstream delivery memory is incompatible with the current orchestration contract. [VERIFIED: tests/test_delivery_orchestration_contract.py]
- Replacing the approved-project authority model is explicitly out of scope for the milestone. [VERIFIED: .planning/REQUIREMENTS.md, .planning/PROJECT.md]

## Assumptions Log

> List all claims tagged `[ASSUMED]` in this research. The planner and discuss-phase use this
> section to identify decisions that need user confirmation before execution.

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Browser/client may later display operator-facing proposal/status, but it is not the authority owner. | Architectural Responsibility Map | Low; affects wording more than implementation direction. |
| A2 | A separate proposal contract file would materially worsen downstream duplication. | Standard Stack / Alternatives Considered | Medium; if another consumer truly needs a separate file, planner may need an explicit mirror strategy. |
| A3 | Chat-memory-only approval state is an available but inferior alternative. | Standard Stack / Alternatives Considered | Low; serves mainly as anti-pattern framing. |
| A4 | The current repo once relied more on informal artifacts or operator memory than explicit bundle fields. | State of the Art | Low; historical framing only. |
| A5 | Warning signs about duplicated request entry or non-field drift checks are inferred from current code shape, not explicitly tested. | Common Pitfalls | Medium; planner should still add explicit verification tasks. |

## Open Questions

1. **What exact proposal identity should bind chat replies idempotently?**
   - What we know: D-05 requires idempotent decision handling, and `request_governance_approval.py` itself only enforces pending-state transitions after an `action_id` is chosen. [VERIFIED: 24-CONTEXT.md, scripts/request_governance_approval.py]
   - What's unclear: Whether the canonical idempotency key should be proposal hash, run id + proposal version, or chat message id tuple. [ASSUMED]
   - Recommendation: Planner should include a small design task that locks one deterministic idempotency key and persists it into the approved-project record. [VERIFIED: 24-CONTEXT.md]

2. **Where should rejected proposal artifacts live?**
   - What we know: Current approved-project flow is optimized around approved bundles and downstream continuation. [VERIFIED: scripts/start_approved_project_delivery.py]
   - What's unclear: Whether rejection should still write a proposal artifact snapshot without creating a full approved-project bundle. [ASSUMED]
   - Recommendation: Planner should decide whether rejection writes a lightweight proposal decision record plus governance event only, while reserving `APPROVED_PROJECT.json` for approvals. [ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Approval/governance scripts and tests. [VERIFIED: codebase review] | ✓ [VERIFIED: local environment command `python --version`] | 3.11.15 [VERIFIED: local environment command `python --version`] | — |
| pytest | Fast regression execution for phase planning and verification. [VERIFIED: codebase review] | ✓ [VERIFIED: local environment command `pytest --version`] | 8.4.2 [VERIFIED: local environment command `pytest --version`] | `python -m unittest` for individual suites where needed. [VERIFIED: tests/*.py use `unittest`] |
| Node.js | GSD tooling and broader repo workflows. [VERIFIED: local environment command `node --version`, .planning/config.json] | ✓ [VERIFIED: local environment command `node --version`] | 24.14.0 [VERIFIED: local environment command `node --version`] | — |

**Missing dependencies with no fallback:**
- None identified for planning this phase. [VERIFIED: local environment audit]

**Missing dependencies with fallback:**
- None identified for planning this phase. [VERIFIED: local environment audit]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest 8.4.2` running `unittest`-style test modules. [VERIFIED: local environment command `pytest --version`, tests/*.py] |
| Config file | none detected in project root during local scan. [VERIFIED: root file scan] |
| Quick run command | `pytest tests/test_approved_project_record.py tests/test_delivery_ready_brief.py tests/test_scope_reopen_flow.py tests/test_delivery_orchestration_contract.py -q` [VERIFIED: local execution] |
| Full suite command | `pytest -q` [ASSUMED] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PROP-01 | Proposal/brief contains stable required sections and derives only from persisted fields. [VERIFIED: requirement + test behavior] | unit | `pytest tests/test_delivery_ready_brief.py -q` [VERIFIED: local environment] | ✅ [VERIFIED: file exists] |
| PROP-02 | Approval writes a single authority contract and blocks missing required approval inputs. [VERIFIED: requirement + test behavior] | unit | `pytest tests/test_approved_project_record.py -q` [VERIFIED: local environment] | ✅ [VERIFIED: file exists] |
| AUTO-01 | Drift/protected changes enter governed pending reopen state instead of silent continuation. [VERIFIED: requirement + test behavior] | unit | `pytest tests/test_scope_reopen_flow.py -q` [VERIFIED: local environment] | ✅ [VERIFIED: file exists] |
| PROP-02 / AUTO-01 | Downstream bundle consumers still require explicit bundle field names and no chat-memory contract. [VERIFIED: requirement mapping] | contract | `pytest tests/test_delivery_orchestration_contract.py -q` [VERIFIED: local environment] | ✅ [VERIFIED: file exists] |

### Sampling Rate
- **Per task commit:** `pytest tests/test_approved_project_record.py tests/test_delivery_ready_brief.py tests/test_scope_reopen_flow.py tests/test_delivery_orchestration_contract.py -q` [VERIFIED: local execution]
- **Per wave merge:** `pytest -q` [ASSUMED]
- **Phase gate:** Focused approval/brief/reopen/contract tests green before `/gsd-verify-work`. [VERIFIED: phase requirements + existing test coverage]

### Wave 0 Gaps
- [ ] Add a dedicated test for chat approval idempotency against duplicate originating messages. [VERIFIED: D-05 exists in 24-CONTEXT.md; no matching test found in inspected suites]
- [ ] Add a dedicated test for ambiguous chat reply linkage blocking contract state changes. [VERIFIED: D-06 exists in 24-CONTEXT.md; no matching test found in inspected suites]
- [ ] Add a dedicated test for pricing / acceptance-gate drift detection, not only protected-path reopen. [VERIFIED: AUTO-01 exists; current reopen tests focus on protected path and out-of-brief requests]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes [ASSUMED] | Reuse originating conversation identity captured by chat intake and require explicit approver metadata in governed events. [VERIFIED: 24-CONTEXT.md, scripts/request_governance_approval.py] |
| V3 Session Management | no [ASSUMED] | No dedicated session subsystem is evident in the Phase 24 code surface; treat conversation linkage as request metadata, not a new session model. [VERIFIED: inspected scripts] |
| V4 Access Control | yes [VERIFIED: scripts/request_governance_approval.py] | `validate_actor_target(...)` plus governed action typing should remain the approval gate. [VERIFIED: scripts/request_governance_approval.py] |
| V5 Input Validation | yes [VERIFIED: scripts/start_approved_project_delivery.py, scripts/request_governance_approval.py] | Fail closed on missing required fields, non-pending action ids, and ambiguous approval linkage. [VERIFIED: scripts/start_approved_project_delivery.py, scripts/request_governance_approval.py, 24-CONTEXT.md] |
| V6 Cryptography | no [VERIFIED: inspected scripts do not introduce crypto operations] | None in current phase scope; do not hand-roll signatures unless a later phase explicitly requires them. [VERIFIED: codebase review] |

### Known Threat Patterns for approval-governance stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Duplicate approval replay from chat bridge | Tampering [VERIFIED: D-05 problem statement] | Persist deterministic idempotency key and only allow one effective terminal decision per proposal identity. [VERIFIED: 24-CONTEXT.md] |
| Ambiguous or spoofed approval target | Spoofing [VERIFIED: D-06 problem statement] | Require proposal/run/conversation linkage and block when lookup is incomplete. [VERIFIED: 24-CONTEXT.md] |
| Silent downstream contract mutation | Tampering [VERIFIED: AUTO-01 + D-10] | Compare locked fields and route drift into governed reopen state. [VERIFIED: .planning/REQUIREMENTS.md, scripts/request_scope_reopen.py] |
| Loss of audit trail | Repudiation [VERIFIED: codebase governance pattern] | Keep append-only governance events and persisted status views instead of in-memory chat decisions. [VERIFIED: scripts/request_governance_approval.py] |

## Sources

### Primary (HIGH confidence)
- `scripts/start_approved_project_delivery.py` - checked approved-project record schema, required fields, artifact paths, and pipeline/block model. [VERIFIED: codebase review]
- `scripts/request_governance_approval.py` - checked request/approve/reject/override transitions and pending-state enforcement. [VERIFIED: codebase review]
- `scripts/request_scope_reopen.py` - checked governed reopen and delivery-event persistence pattern. [VERIFIED: codebase review]
- `tests/test_approved_project_record.py` - checked stable authority record expectations and blocked missing-input behavior. [VERIFIED: codebase review]
- `tests/test_delivery_ready_brief.py` - checked brief section order and field-derived rendering. [VERIFIED: codebase review]
- `tests/test_scope_reopen_flow.py` - checked reopen pending-state behavior and delivery status persistence. [VERIFIED: codebase review]
- `tests/test_delivery_orchestration_contract.py` - checked downstream bundle-field requirements and rejection of chat-memory delivery state. [VERIFIED: codebase review]
- `.planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md` - checked locked decisions and out-of-scope boundaries. [VERIFIED: codebase review]
- `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` - checked requirement mapping and success criteria. [VERIFIED: codebase review]
- Local environment commands `python --version`, `pytest --version`, `node --version`, and focused pytest execution - checked runtime/tooling availability and baseline regression health. [VERIFIED: local environment audit]

### Secondary (MEDIUM confidence)
- `docs/STATE_CONTRACT.md` - used for general state-governance boundary guidance despite partial encoding noise in local rendering. [VERIFIED: file present + readable snippets]
- `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` - used to confirm proposal/decision artifact style and backlink expectations. [VERIFIED: file present + readable snippets]
- `docs/skill-governance/templates/orchestrator-input-template-v0.2.md` - used to confirm exact downstream bundle path expectations. [VERIFIED: file present + readable snippets]

### Tertiary (LOW confidence)
- None. [VERIFIED: all material recommendations are grounded in repo files or local execution]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - the phase clearly extends an existing Python/governance/artifact stack and local runtime availability was verified. [VERIFIED: codebase review + local environment audit]
- Architecture: HIGH - the repo already enforces a single approved-project authority model and append-only governance pattern. [VERIFIED: scripts + tests]
- Pitfalls: MEDIUM - the major risks are strongly implied by context and current code shape, but some future chat-bridge failure modes are not yet covered by tests. [VERIFIED: 24-CONTEXT.md + inspected tests]

**Research date:** 2026-05-04 [VERIFIED: local system date]
**Valid until:** 2026-06-03 for repo-internal architecture, or until Phase 22/23 implementation materially changes intake/proposal data contracts. [ASSUMED]
