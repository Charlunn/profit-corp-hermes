# Phase 9: Claude Code Delivery Team Orchestration - Research

**Researched:** 2026-04-27
**Domain:** Claude Code delivery orchestration, staged handoff contracts, scope governance, and replayable workflow artifacts
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### Delivery team topology
- **D-01:** Use a single delivery orchestrator role to drive the workflow, load the approved project context, and sequence specialist work rather than having the owner manually route each step. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- **D-02:** The specialist team should follow the existing five-stage operating shape already present in the repo: design, development, testing, git versioning, and release readiness. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- **D-03:** Each specialist role should be narrowly responsible for one stage output and should hand off through explicit artifacts instead of freeform chat state. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]

### Handoff contract
- **D-04:** Every delivery run must start from the same fixed input bundle: approved project brief, template contract, shared-backend guardrails, project identity metadata, and GSD operating constraints. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- **D-05:** Stage handoffs should reuse the existing markdown-first template pattern: one stage summary, declared outputs, evidence links, gate decision, open risks, and next-stage input. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- **D-06:** The final delivery handoff should use a stable operator-facing artifact that summarizes end-to-end outcome, impact surface, verification evidence, gate status, rollback plan, and release recommendation. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]

### Scope and safety boundaries
- **D-07:** Delivery roles may customize only approved product surfaces and must treat shared auth, payment, entitlement, shared-table, and shared-backend rules as protected platform primitives. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- **D-08:** Scope enforcement should default to “approved brief only”; any request to modify protected platform behavior or expand feature scope must trigger an explicit scope reopen rather than being absorbed silently during delivery. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- **D-09:** Delivery automation should consume the existing conformance gate and governance rules instead of inventing a second parallel safety system. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]

### Audit trail and replayability
- **D-10:** Hermes should record each major delivery action as a role-attributed workflow event so a run can be replayed from artifacts after the fact. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- **D-11:** Auditability should be dual-surface: machine-readable event metadata for sequencing and a human-readable latest view for operators. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- **D-12:** Replayability should come from stable stage artifacts plus explicit role/action records, not from trying to reconstruct the workflow from raw terminal history. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]

### Claude's Discretion
- Exact role names, as long as they map cleanly onto the five-stage workflow [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- Exact file layout for delivery-run event logs and latest-view summaries [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- Exact metadata schema for role/action records, as long as role, action, artifact, timestamp, and outcome remain explicit [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- Exact wording of scope-reopen and blocked-delivery statuses [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]

### Deferred Ideas (OUT OF SCOPE)
- Automatic project brief generation and automatic project kickoff belong to Phase 10, not this phase. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- Direct GitHub sync and Vercel deployment execution belong to Phase 11, not this phase. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- Credential-scope controls, deeper audit controls, and final operator review hardening belong to Phase 12, not this phase. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- Expanding into broad multi-user collaboration workflow remains out of scope for this phase. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| TEAM-01 | Hermes can define a specialist Claude Code-powered development team for post-approval SaaS delivery with explicit role responsibilities. [CITED: .planning/REQUIREMENTS.md] | Standard Stack, Architecture Patterns, and Recommended Project Structure define one orchestrator plus five stage-specialist roles. [VERIFIED: repo research] |
| TEAM-02 | Hermes can define the required inputs, outputs, and handoff artifacts for each development role in the delivery workflow. [CITED: .planning/REQUIREMENTS.md] | Handoff templates and delivery event schema recommend fixed start-input, per-stage handoff, and final-delivery artifacts. [VERIFIED: repo research] |
| TEAM-03 | Hermes can give each delivery role access to the approved template rules, project brief, and GSD operating constraints before implementation starts. [CITED: .planning/REQUIREMENTS.md] | Fixed input bundle and orchestrator-input extension recommendations define exactly what must be loaded before stage execution. [VERIFIED: repo research] |
| TEAM-04 | Hermes can constrain delivery roles so they only operate within approved project scope unless the owner reopens scope. [CITED: .planning/REQUIREMENTS.md] | Scope enforcement model reuses template contract, shared-backend guardrails, and governance approval wrapper for explicit scope reopen flow. [VERIFIED: repo research] |
| TEAM-05 | Hermes can record which role performed each major delivery action for auditability. [CITED: .planning/REQUIREMENTS.md] | Delivery event log + latest view pattern mirrors existing governance JSONL plus markdown status architecture. [VERIFIED: repo research] |
| TEAM-06 | Hermes can run a repeatable approved-project delivery workflow without requiring the owner to manually orchestrate every development step. [CITED: .planning/REQUIREMENTS.md] | One orchestrator role, fixed five-stage sequence, explicit gate semantics, and cron-style command entrypoints provide repeatable orchestration. [VERIFIED: repo research] |
</phase_requirements>

## Summary

This repo already has the core patterns needed for Phase 9: centralized orchestration, markdown-first contracts, append-only event logs, human-readable latest views, and blocking governance/conformance gates. The missing work is not inventing a new delivery system; it is adapting those existing patterns from the current CEO operating workflow into an approved-project SaaS delivery workflow with explicit specialist stage ownership. [CITED: docs/MULTI_PROFILE_COORDINATION.md] [CITED: docs/STATE_CONTRACT.md] [CITED: docs/OPERATIONS.md] [CITED: docs/skill-governance/templates/stage-handoff-template-v0.2.md] [CITED: docs/skill-governance/templates/final-delivery-template-v0.2.md] [VERIFIED: scripts/request_governance_approval.py] [VERIFIED: scripts/enforce_governed_action.py] [VERIFIED: scripts/check_template_conformance.py]

The strongest pattern match is: treat delivery orchestration exactly like governance already treats protected actions. Use one machine-readable append-only stream for delivery events, one markdown latest view for operators, and fixed markdown artifacts for stage handoff and final delivery. Scope enforcement should not be a new policy engine; it should route protected-platform changes and feature expansion through the existing governance approval path, while product-safe work stays inside the approved brief plus the template contract and shared-backend guardrails. [VERIFIED: scripts/governance_common.py] [VERIFIED: scripts/render_governance_status.py] [CITED: docs/platform/standalone-saas-template-contract.md] [VERIFIED: scripts/instantiate_template_project.py] [VERIFIED: scripts/check_template_conformance.py]

**Primary recommendation:** Build Phase 9 as a contract-and-artifact layer on top of existing patterns: add a delivery orchestrator workflow spec, fixed delivery-run directories, JSONL delivery events, a markdown latest-status view, and explicit scope-reopen commands that reuse existing governance/conformance enforcement. [VERIFIED: repo research]

## Project Constraints (from CLAUDE.md)

No `CLAUDE.md` file exists at the project root, so there are no additional repo-local directives to carry into planning beyond the checked-in contracts and planning context. [VERIFIED: repo root inspection]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Delivery workflow sequencing | Frontend Server (SSR/orchestrator host) | API / Backend | The repo already centralizes orchestration through a single coordinator role and shell/Python entrypoints rather than browser code. [CITED: docs/MULTI_PROFILE_COORDINATION.md] [CITED: assets/workspaces/ceo/AGENTS.md] [VERIFIED: orchestration/cron/commands.sh] |
| Stage handoff artifact generation | API / Backend | Database / Storage | Existing artifact generation is file-based and produced by scripts, so delivery handoffs should also be emitted server-side into durable files. [CITED: docs/skill-governance/templates/stage-handoff-template-v0.2.md] [CITED: docs/skill-governance/templates/final-delivery-template-v0.2.md] [VERIFIED: scripts/render_governance_status.py] |
| Approved-scope enforcement | API / Backend | Database / Storage | Existing enforcement lives in Python governance and conformance scripts, not in interactive prompts alone. [VERIFIED: scripts/request_governance_approval.py] [VERIFIED: scripts/enforce_governed_action.py] [VERIFIED: scripts/check_template_conformance.py] |
| Protected-platform boundary validation | API / Backend | Database / Storage | The current blocking gate statically validates workspace files, SQL boundaries, and client-side mutations through `check_template_conformance.py`. [VERIFIED: scripts/check_template_conformance.py] |
| Role-attributed delivery audit log | Database / Storage | API / Backend | The repo already uses append-only JSONL as the authority stream and markdown latest views as derived surfaces. [VERIFIED: scripts/governance_common.py] [CITED: docs/OPERATIONS.md] |
| Operator latest-status review | Frontend Server (SSR/orchestrator host) | Database / Storage | Operators currently consume generated markdown status views, not a UI app dashboard. [CITED: docs/OPERATIONS.md] [VERIFIED: scripts/render_governance_status.py] [VERIFIED: scripts/generate_operating_visibility.py via grep] |
| Delivery replay from artifacts | Database / Storage | API / Backend | Replay depends on durable stage files plus ordered event records, matching the repo’s artifact-first pattern. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md] [VERIFIED: scripts/governance_common.py] |

## Standard Stack

### Core
| Library / Tool | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.11.15 | Delivery orchestration scripts, artifact rendering, and enforcement CLIs | Existing governance, template instantiation, and conformance gates are all Python scripts, so Phase 9 should extend the same runtime. [VERIFIED: environment probe] [VERIFIED: scripts/request_governance_approval.py] [VERIFIED: scripts/enforce_governed_action.py] [VERIFIED: scripts/check_template_conformance.py] |
| `unittest` | stdlib in Python 3.11.15 | Contract-locking and CLI behavior tests | Existing template and conformance workflows are already tested with `python -m unittest`, so planner should extend that pattern instead of adding a new test runner. [VERIFIED: environment probe] [VERIFIED: tests/test_template_contract.py] [VERIFIED: tests/test_instantiate_template_project.py] [VERIFIED: tests/test_check_template_conformance.py] |
| Markdown contracts | repo-native | Human-readable stage and final delivery artifacts | The repo’s skill governance and handoff system is explicitly markdown-first. [CITED: docs/skill-governance/README.md] [CITED: docs/skill-governance/templates/orchestrator-input-template-v0.2.md] [CITED: docs/skill-governance/templates/stage-handoff-template-v0.2.md] [CITED: docs/skill-governance/templates/final-delivery-template-v0.2.md] |
| JSONL event stream | repo-native | Append-only machine-readable delivery audit log | Governance already uses JSONL as the authoritative stream and derives status markdown from it, which is the best fit for delivery events too. [VERIFIED: scripts/governance_common.py] [VERIFIED: assets/shared/governance/governance_events.jsonl] |

### Supporting
| Tool / Pattern | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Hermes CLI | Hermes Agent v0.10.0 (2026.4.16) | Existing orchestration host and cron entrypoint | Use for operator-triggered or cron-triggered delivery orchestration entrypoints, not for artifact storage itself. [VERIFIED: environment probe] [VERIFIED: orchestration/cron/commands.sh] |
| `scripts/instantiate_template_project.py` | repo-local | Supplies `.hermes/project-metadata.json`, `.hermes/shared-backend-guardrails.json`, and `PROJECT_BRIEF_ENTRYPOINT.md` | Use as the required Phase 9 start bundle source for every delivery run. [VERIFIED: scripts/instantiate_template_project.py] [VERIFIED: tests/test_instantiate_template_project.py] |
| `scripts/check_template_conformance.py` | repo-local | Single blocking gate for protected-platform and shared-backend invariants | Run before final delivery handoff and after any stage that may affect protected boundaries. [VERIFIED: scripts/check_template_conformance.py] [VERIFIED: tests/test_check_template_conformance.py] |
| Governance approval wrapper | repo-local | Explicit approval/override/block flow for high-impact actions | Reuse for scope reopen and protected-surface escalation instead of inventing a parallel approval system. [VERIFIED: scripts/request_governance_approval.py] [VERIFIED: scripts/enforce_governed_action.py] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Markdown + JSONL artifacts | Database-backed workflow app | A DB-backed system could support richer querying later, but it would break the repo’s existing artifact-first pattern and add new operational complexity too early. [CITED: docs/skill-governance/README.md] [CITED: .planning/phases/06-execution-handoff-and-team-readiness/06-CONTEXT.md] |
| Reusing governance approval for scope reopen | New delivery-specific approval engine | A dedicated engine could model more cases later, but Phase 9 explicitly says to consume existing conformance and governance rules rather than invent a second safety system. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md] |
| One orchestrator + five stage roles | Freeform owner-routed specialist prompts | Freeform routing conflicts with the repo’s centralized orchestration model and would not satisfy TEAM-06 repeatability well. [CITED: docs/MULTI_PROFILE_COORDINATION.md] [CITED: skills/library/normalized/orchestrator-workflow.md] |

**Installation:**
```bash
# No new package manager dependency is required for the recommended Phase 9 foundation.
# Reuse existing Python stdlib + Hermes CLI + repo scripts.
```

**Version verification:**
- `python --version` returned `Python 3.11.15`. [VERIFIED: environment probe]
- `hermes --version` returned `Hermes Agent v0.10.0 (2026.4.16)`. [VERIFIED: environment probe]
- No npm package additions are required for the recommended baseline. [VERIFIED: repo research]

## Architecture Patterns

### System Architecture Diagram

```text
Approved SaaS workspace
  └── .hermes/project-metadata.json
  └── .hermes/shared-backend-guardrails.json
  └── .hermes/PROJECT_BRIEF_ENTRYPOINT.md
            |
            v
Delivery Orchestrator Input Builder
  - loads approved brief bundle
  - loads template contract
  - loads GSD operating constraints
            |
            v
Delivery Orchestrator
  - creates delivery run id
  - writes run manifest
  - emits delivery_events.jsonl:start
            |
            +------------------------------+
            |                              |
            v                              v
      Design Specialist               Scope Guard
      - scope map                     - safe surfaces only
      - stage handoff                 - protected change? -> reopen request
            |                              |
            +--------------PASS------------+
                           |
                           v
                    Development Specialist
                    - implement approved work
                    - evidence + handoff
                           |
                           v
                     Testing Specialist
                     - run targeted tests
                     - run conformance gate as needed
                     - evidence + handoff
                           |
                           v
                  Git Versioning Specialist
                  - structured commit evidence
                  - rollback note
                  - handoff
                           |
                           v
                 Release Readiness Specialist
                 - final delivery artifact
                 - gate snapshot
                 - release recommendation
                           |
                           v
      delivery_events.jsonl (authority stream) ----> DELIVERY_STATUS.md (latest operator view)
                           |
                           v
                     Replay / Audit Consumer
                     - reconstruct stage order
                     - verify who did what
                     - inspect evidence paths
```

This flow matches the repo’s existing orchestrator-first, gate-first, artifact-first operating style. [CITED: docs/MULTI_PROFILE_COORDINATION.md] [CITED: skills/library/normalized/orchestrator-workflow.md] [CITED: docs/OPERATIONS.md] [VERIFIED: scripts/governance_common.py]

### Recommended Project Structure
```text
assets/
└── workspaces/
    └── projects/
        └── <workspace>/
            └── .hermes/
                ├── delivery-run-manifest.json          # fixed start bundle + run metadata
                ├── delivery-events.jsonl               # append-only role/action stream
                ├── DELIVERY_STATUS.md                  # latest operator view
                ├── DELIVERY_SCOPE.md                   # approved scope + non-goals + reopen rules
                ├── stage-handoffs/
                │   ├── 01-design.md
                │   ├── 02-development.md
                │   ├── 03-testing.md
                │   ├── 04-git-versioning.md
                │   └── 05-release-readiness.md
                └── FINAL_DELIVERY.md                   # operator-facing final artifact

scripts/
├── start_delivery_run.py                               # initialize manifest/events/status from approved bundle
├── append_delivery_event.py                            # validated event append helper
├── render_delivery_status.py                           # derive DELIVERY_STATUS.md latest view
├── request_scope_reopen.py                             # governance-backed scope reopen request helper
└── validate_delivery_handoff.py                        # contract checks for stage/final artifacts

docs/
└── skill-governance/
    └── templates/
        ├── orchestrator-input-template-v0.2.md        # extend for approved-project delivery bundle
        ├── stage-handoff-template-v0.2.md             # reuse directly or minimally extend
        └── final-delivery-template-v0.2.md            # reuse directly or minimally extend
```

The file layout above follows existing `.hermes` handoff placement and current markdown/jsonl status patterns. [VERIFIED: scripts/instantiate_template_project.py] [VERIFIED: scripts/governance_common.py] [CITED: docs/skill-governance/templates/stage-handoff-template-v0.2.md] [CITED: docs/skill-governance/templates/final-delivery-template-v0.2.md]

### Pattern 1: One orchestrator, one stage owner, one artifact per stage
**What:** Assign exactly one specialist role to each of the five normalized stages, and require each stage to emit a handoff artifact before the next stage begins. [CITED: skills/library/normalized/orchestrator-workflow.md] [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
**When to use:** Always for approved-project delivery runs. [CITED: .planning/ROADMAP.md]
**Example:**
```markdown
## 1) Stage Summary
- `stage`: design
- `summary`: approved scope mapped to safe extension surfaces only.

## 2) Outputs Produced
- `DELIVERY_SCOPE.md`
- `scope-map.json`

## 4) Gate Decision
- `gate_decision`: PASS
- `reason`: no protected-platform change requested.
```
Source pattern: `docs/skill-governance/templates/stage-handoff-template-v0.2.md`. [CITED: docs/skill-governance/templates/stage-handoff-template-v0.2.md]

### Pattern 2: Fixed input bundle at run start
**What:** Treat `.hermes/project-metadata.json`, `.hermes/shared-backend-guardrails.json`, `.hermes/PROJECT_BRIEF_ENTRYPOINT.md`, the platform contract, and GSD constraints as mandatory inputs before any specialist starts work. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md] [VERIFIED: scripts/instantiate_template_project.py]
**When to use:** Run initialization only; if any item is missing, block the run. [VERIFIED: repo research]
**Example:**
```json
{
  "run_id": "delivery-20260427-001",
  "workspace": "lead-capture",
  "required_inputs": [
    ".hermes/project-metadata.json",
    ".hermes/shared-backend-guardrails.json",
    ".hermes/PROJECT_BRIEF_ENTRYPOINT.md",
    "docs/platform/standalone-saas-template-contract.md"
  ]
}
```
The fixed-input idea is directly aligned to D-04 and current `.hermes` outputs. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md] [VERIFIED: scripts/instantiate_template_project.py]

### Pattern 3: Dual-surface auditability
**What:** Store append-only delivery events in JSONL, then derive a markdown latest view from that stream. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md] [VERIFIED: scripts/governance_common.py] [VERIFIED: scripts/render_governance_status.py]
**When to use:** Every major delivery action and every stage gate transition. [VERIFIED: repo research]
**Example:**
```json
{"run_id":"delivery-20260427-001","event_id":"delivery-20260427103000","role":"developer","stage":"development","action":"stage_completed","artifact":".hermes/stage-handoffs/02-development.md","outcome":"pass","timestamp":"2026-04-27T10:30:00Z"}
```
This should mirror governance event discipline: explicit actor, artifact, status transition, and timestamp. [VERIFIED: scripts/governance_common.py]

### Pattern 4: Scope reopen as a governed escalation, not a silent branch
**What:** If a request touches protected platform paths, shared-table boundaries, or expands beyond approved scope, stop the current stage and emit a reopen request instead of improvising. [CITED: docs/platform/standalone-saas-template-contract.md] [VERIFIED: scripts/check_template_conformance.py] [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
**When to use:** Any protected-layer change, product-scope expansion, or ambiguous instruction during delivery. [VERIFIED: repo research]
**Example:**
```bash
python scripts/request_scope_reopen.py \
  --run-id delivery-20260427-001 \
  --stage development \
  --role developer \
  --target-artifact src/lib/paypal.ts \
  --reason "Requested change touches protected payment layer" \
  --related-workspace assets/workspaces/projects/lead-capture
```
This should wrap `request_governance_approval.py`, not replace it. [VERIFIED: scripts/request_governance_approval.py]

### Anti-Patterns to Avoid
- **Freeform chat-only handoff:** The phase explicitly requires artifact-based handoff and replay from artifacts, not terminal history reconstruction. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- **Second safety system for delivery:** Do not build a new approval engine separate from governance plus conformance. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- **Stage-skipping orchestration:** The normalized orchestrator workflow forbids skipping testing and git versioning on the path to release readiness. [CITED: skills/library/normalized/orchestrator-workflow.md]
- **Letting specialists mutate protected platform files by convention only:** Existing repo safety relies on explicit blocking scripts, not policy prose alone. [VERIFIED: scripts/check_template_conformance.py] [VERIFIED: scripts/enforce_governed_action.py]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Scope approval state | New workflow approval engine | `scripts/request_governance_approval.py` + `scripts/enforce_governed_action.py` | Existing governance already models request/approve/reject/override/blocked states and latest-view rendering. [VERIFIED: scripts/request_governance_approval.py] [VERIFIED: scripts/enforce_governed_action.py] [VERIFIED: scripts/governance_common.py] |
| Protected-platform boundary checking | Custom delivery-only file allowlist checker | `scripts/check_template_conformance.py` | Existing gate already blocks protected path drift, shared-table violations, and forbidden client writes. [VERIFIED: scripts/check_template_conformance.py] [VERIFIED: tests/test_check_template_conformance.py] |
| Delivery status dashboard | New UI/dashboard subsystem | Markdown latest view derived from JSONL | The repo already treats markdown latest views as the operator surface. [CITED: docs/OPERATIONS.md] [VERIFIED: scripts/render_governance_status.py] |
| Stage handoff format | Novel bespoke delivery schema | Existing stage and final templates | The required fields already match Phase 9 decisions closely. [CITED: docs/skill-governance/templates/stage-handoff-template-v0.2.md] [CITED: docs/skill-governance/templates/final-delivery-template-v0.2.md] |
| New role grammar | Custom multi-agent workflow model | Existing five-stage `orchestrator-workflow` contract | The five-stage model is already normalized and matches D-02. [CITED: skills/library/normalized/orchestrator-workflow.md] [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md] |

**Key insight:** Phase 9 is a reuse-and-standardize phase, not a net-new orchestration architecture phase. The planner should optimize for extending established repo contracts, not expanding the surface area. [VERIFIED: repo research]

## Common Pitfalls

### Pitfall 1: Treating scope enforcement as prompt text instead of executable gates
**What goes wrong:** Specialists are told to stay in scope, but no durable artifact or command enforces what “in scope” means. [VERIFIED: repo research]
**Why it happens:** Prompt-only guardrails are easier to add than blocked command paths and validated artifacts. [ASSUMED]
**How to avoid:** Create a delivery-scope artifact at run start, validate protected-surface requests through governance, and require conformance before final handoff. [VERIFIED: scripts/request_governance_approval.py] [VERIFIED: scripts/check_template_conformance.py]
**Warning signs:** Stage handoffs mention “small extra change” or “minor platform adjustment” without a reopen record. [ASSUMED]

### Pitfall 2: Recording stage summaries without machine-readable sequencing
**What goes wrong:** Humans can read the run, but later automation cannot reliably answer who did what and in what order. [VERIFIED: repo research]
**Why it happens:** Markdown alone is readable but weak for ordered replay. [CITED: .planning/phases/06-execution-handoff-and-team-readiness/06-CONTEXT.md]
**How to avoid:** Emit both stage markdown and a JSONL event for stage_started, artifact_written, gate_passed, gate_failed, scope_reopen_requested, and run_completed. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md] [VERIFIED: scripts/governance_common.py]
**Warning signs:** Operators need terminal history to reconstruct whether a stage actually passed. [VERIFIED: repo research]

### Pitfall 3: Mixing delivery-role ownership with existing business-artifact ownership rules
**What goes wrong:** New delivery roles directly overwrite protected or shared artifacts outside the existing primary-writer model. [CITED: docs/STATE_CONTRACT.md] [CITED: docs/MULTI_PROFILE_COORDINATION.md]
**Why it happens:** Delivery roles feel “new,” so implementers forget they still operate inside the same repo governance model. [ASSUMED]
**How to avoid:** Keep delivery artifacts in workspace-local `.hermes/` paths and reuse governance for any crossover to protected shared paths. [VERIFIED: scripts/instantiate_template_project.py] [VERIFIED: scripts/governance_common.py]
**Warning signs:** Delivery plan proposes writing central `assets/shared/*.md` files as part of project-specific execution. [VERIFIED: repo research]

### Pitfall 4: Creating another latest-status surface without an authority source
**What goes wrong:** A markdown delivery status file drifts from reality because it is manually edited or not derived from an authoritative stream. [VERIFIED: repo research]
**Why it happens:** Latest views are convenient to edit by hand. [ASSUMED]
**How to avoid:** Follow the governance pattern exactly: JSONL authority stream, markdown latest view rendered from it, latest view treated as read-only. [VERIFIED: scripts/governance_common.py] [CITED: docs/OPERATIONS.md]
**Warning signs:** Planner proposes “update status markdown” as a direct stage action rather than “append event and render status.” [VERIFIED: repo research]

## Code Examples

Verified patterns from official repo sources:

### Append-only event authority + derived latest view
```python
STATUS_GROUPS = OrderedDict(
    [
        ("pending", "Pending Approvals"),
        ("blocked", "Active Blocks"),
        ("approved", "Recent Approvals"),
        ("rejected", "Recent Rejections"),
        ("override", "Recent Overrides"),
    ]
)


def append_event(event: dict[str, Any], path: Path = GOVERNANCE_EVENTS_PATH) -> None:
    validate_event(event)
    ensure_governance_dir()
    ensure_allowed_write_path(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def refresh_status_view() -> None:
    write_text(GOVERNANCE_STATUS_PATH, render_status_markdown(load_jsonl(GOVERNANCE_EVENTS_PATH)))
```
Source: `scripts/governance_common.py`. [VERIFIED: scripts/governance_common.py]

### Governed gate-before-mutate wrapper
```python
def require_allowed_status(action_id: str) -> dict[str, Any]:
    latest = find_latest_event(action_id)
    if latest is None:
        raise GovernedActionError(f"action_id not found: {action_id}")
    status = str(latest.get("status_after", "")).lower()
    if status in {"approved", "override"}:
        return latest
    if status in {"pending", "rejected", "blocked", "failed"}:
        event = build_terminal_event(
            latest,
            event_type="blocked",
            status_after="blocked",
            reason=f"Governed action blocked because current approval status is {status}.",
            result_code="governance_blocked",
        )
        append_event(event)
        refresh_status_view()
        raise GovernanceBlocked(f"governed action blocked: {status}")
```
Source: `scripts/enforce_governed_action.py`. [VERIFIED: scripts/enforce_governed_action.py]

### Existing stage handoff contract shape
```markdown
## 1) Stage Summary
- `stage`:
- `summary`:

## 2) Outputs Produced
- 产物 1：

## 3) Evidence Links
- 链接 1：

## 4) Gate Decision
- `gate_decision`: PASS | FAIL
- `reason`:
```
Source: `docs/skill-governance/templates/stage-handoff-template-v0.2.md`. [CITED: docs/skill-governance/templates/stage-handoff-template-v0.2.md]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Owner/manual orchestration and ad-hoc role routing for delivery intent | Centralized orchestrator-first sequencing through explicit stage contracts | Phase 9 locked decisions on 2026-04-27 and existing repo orchestration pattern already established before this phase. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md] [CITED: docs/MULTI_PROFILE_COORDINATION.md] | Phase 9 should codify this into delivery-run artifacts and scripts instead of relying on operator memory. [VERIFIED: repo research] |
| Human-readable artifact only | Human-readable markdown plus machine-readable sidecar/event stream | Phase 6 kept markdown-primary with lightweight metadata; governance already demonstrates JSONL + markdown dual-surface. [CITED: .planning/phases/06-execution-handoff-and-team-readiness/06-CONTEXT.md] [VERIFIED: scripts/governance_common.py] | Delivery should use the same dual-surface pattern for replayability without heavy schema overhead. [VERIFIED: repo research] |
| Separate or implicit safety checks | Single conformance gate plus governance gate-before-mutate | Phase 8 completed unified conformance enforcement and Phase 4 already established governed actions. [VERIFIED: .planning/phases/08-shared-supabase-backend-guardrails/08-02-SUMMARY.md] [VERIFIED: scripts/check_template_conformance.py] [VERIFIED: scripts/enforce_governed_action.py] | Phase 9 should integrate with those gates rather than add new enforcement logic. [VERIFIED: repo research] |

**Deprecated/outdated:**
- Freeform downstream chat state as the primary delivery memory is outdated for this phase because D-03, D-10, and D-12 require explicit artifacts and replayable action records. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]
- Building a second delivery-only safety path is outdated for this phase because D-09 explicitly says to consume the existing governance and conformance system. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md]

## Open Questions (RESOLVED)

1. **Should delivery events live per workspace or in a shared global stream?**
   - What we know: Existing governance events are global under `assets/shared/governance/governance_events.jsonl`, while template-instantiated project metadata lives inside workspace `.hermes/`. [VERIFIED: assets/shared/governance/governance_events.jsonl] [VERIFIED: scripts/instantiate_template_project.py]
   - Resolution for Phase 9: Store delivery events inside each workspace `.hermes/` as `delivery-events.jsonl`, and require stable `workspace_name` plus `run_id` fields so aggregation can be added later without changing the Phase 9 authority surface. This matches Plans 09-02 and 09-03. [VERIFIED: planning resolution]

2. **Should scope reopen use a dedicated CLI or a thin wrapper over governance approval?**
   - What we know: Existing governance CLI already validates actor/target/action-type and supports request/approve/reject/override. [VERIFIED: scripts/request_governance_approval.py] [VERIFIED: scripts/governance_common.py]
   - Resolution for Phase 9: Implement a thin `request_scope_reopen.py` wrapper that maps delivery-language inputs onto the existing governance approval contract instead of exposing raw governance parameters or creating a second approval system. This matches Plan 09-03. [VERIFIED: planning resolution]

3. **How much should stage templates be extended versus reused as-is?**
   - What we know: Current stage and final templates already cover summary, outputs, evidence, gate decision, risks, next-stage input, impact surface, rollback, and release recommendation. [CITED: docs/skill-governance/templates/stage-handoff-template-v0.2.md] [CITED: docs/skill-governance/templates/final-delivery-template-v0.2.md]
   - Resolution for Phase 9: Reuse the existing template families and add lightweight delivery metadata fields such as `run_id`, `role`, `stage`, `scope_status`, and `next_stage` while preserving the current parser-friendly markdown-first structure. This matches Plans 09-01 and 09-03. [VERIFIED: planning resolution]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Orchestration scripts, renderers, validators, tests | ✓ | 3.11.15 | — [VERIFIED: environment probe] |
| `unittest` | Phase 9 contract tests | ✓ | stdlib with Python 3.11.15 | — [VERIFIED: environment probe] |
| Bash | Command wrappers and operator commands | ✓ | GNU bash 5.2.37 | — [VERIFIED: environment probe] |
| Hermes CLI | Cron/operator entrypoint integration | ✓ | Hermes Agent v0.10.0 (2026.4.16) | Manual script execution if CLI orchestration is temporarily unavailable. [VERIFIED: environment probe] [VERIFIED: orchestration/cron/commands.sh] |

**Missing dependencies with no fallback:**
- None identified for the recommended Phase 9 baseline. [VERIFIED: environment probe]

**Missing dependencies with fallback:**
- None identified for the recommended Phase 9 baseline. [VERIFIED: environment probe]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Python `unittest` on Python 3.11.15 [VERIFIED: environment probe] |
| Config file | none — tests are direct `python -m unittest ...` modules. [VERIFIED: tests directory inspection] |
| Quick run command | `python -m unittest tests.test_instantiate_template_project tests.test_check_template_conformance` [VERIFIED: docs/platform/standalone-saas-template-contract.md] |
| Full suite command | `python -m unittest tests.test_template_registry tests.test_template_contract tests.test_instantiate_template_project tests.test_check_template_conformance tests.test_generate_operating_visibility tests.test_derived_packages tests.test_generate_decision_package tests.test_roadmap_phase_format` [VERIFIED: tests directory inspection] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| TEAM-01 | Specialist roles map cleanly to five delivery stages | unit | `python -m unittest tests.test_delivery_orchestration_contract -x` | ❌ Wave 0 |
| TEAM-02 | Each stage requires fixed inputs/outputs/handoff artifact fields | unit | `python -m unittest tests.test_delivery_handoff_contract -x` | ❌ Wave 0 |
| TEAM-03 | Run start blocks until approved brief bundle and guardrails exist | integration | `python -m unittest tests.test_start_delivery_run -x` | ❌ Wave 0 |
| TEAM-04 | Out-of-scope or protected-surface changes trigger reopen/block path | integration | `python -m unittest tests.test_scope_reopen_flow -x` | ❌ Wave 0 |
| TEAM-05 | Major actions are recorded with role/action/artifact/timestamp/outcome | unit | `python -m unittest tests.test_delivery_events -x` | ❌ Wave 0 |
| TEAM-06 | Full run can progress design→development→testing→git→release through artifacts | integration | `python -m unittest tests.test_delivery_run_replay -x` | ❌ Wave 0 |

### Sampling Rate
- **Per task commit:** `python -m unittest tests.test_delivery_orchestration_contract tests.test_delivery_handoff_contract tests.test_delivery_events -x` [VERIFIED: repo research]
- **Per wave merge:** `python -m unittest tests.test_start_delivery_run tests.test_scope_reopen_flow tests.test_delivery_run_replay tests.test_check_template_conformance -x` [VERIFIED: repo research]
- **Phase gate:** Full suite green before `/gsd-verify-work`. [CITED: .planning/config.json]

### Wave 0 Gaps
- [ ] `tests/test_delivery_orchestration_contract.py` — locks role names, stage order, and required run-start bundle for REQ-TEAM-01/02/03. [VERIFIED: repo research]
- [ ] `tests/test_delivery_handoff_contract.py` — locks stage handoff and final delivery sections for REQ-TEAM-02. [VERIFIED: repo research]
- [ ] `tests/test_start_delivery_run.py` — covers missing-input blocking and run manifest generation for REQ-TEAM-03/06. [VERIFIED: repo research]
- [ ] `tests/test_scope_reopen_flow.py` — covers protected path escalation and blocked scope reopen flows for REQ-TEAM-04. [VERIFIED: repo research]
- [ ] `tests/test_delivery_events.py` — covers append-only event schema and latest-view rendering for REQ-TEAM-05. [VERIFIED: repo research]
- [ ] `tests/test_delivery_run_replay.py` — covers stage sequencing and artifact-based replay for REQ-TEAM-06. [VERIFIED: repo research]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Phase 9 does not add user login/authentication surfaces directly; it reuses existing platform contracts rather than introducing auth flows. [CITED: docs/platform/standalone-saas-template-contract.md] |
| V3 Session Management | no | Phase 9 is script/orchestration focused rather than session-state focused. [ASSUMED] |
| V4 Access Control | yes | Use existing primary-writer rules, actor-target validation, and governance approval/override semantics for controlled actions. [CITED: docs/STATE_CONTRACT.md] [VERIFIED: scripts/governance_common.py] [VERIFIED: scripts/request_governance_approval.py] |
| V5 Input Validation | yes | Validate CLI arguments, required fields, allowed targets, and required artifact presence before execution. [VERIFIED: scripts/request_governance_approval.py] [VERIFIED: scripts/enforce_governed_action.py] [VERIFIED: scripts/check_template_conformance.py] |
| V6 Cryptography | no | Phase 9 does not introduce custom cryptographic logic in the recommended design. [ASSUMED] |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Silent protected-platform drift during product delivery | Tampering | Reuse `check_template_conformance.py` as the blocking gate and treat protected paths as immutable by default. [VERIFIED: scripts/check_template_conformance.py] [CITED: docs/platform/standalone-saas-template-contract.md] |
| Role spoofing in delivery event records | Spoofing | Validate allowed actor/target/action combinations in the event append helper, mirroring governance validation rules. [VERIFIED: scripts/governance_common.py] [VERIFIED: scripts/request_governance_approval.py] |
| Manual status-file tampering | Tampering | Treat markdown latest views as derived read-only artifacts and render them from JSONL authority streams. [CITED: docs/OPERATIONS.md] [VERIFIED: scripts/governance_common.py] |
| Hidden scope expansion during development | Elevation of Privilege | Force explicit scope-reopen requests and blocked-stage outcomes before protected or non-approved changes proceed. [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md] [VERIFIED: scripts/enforce_governed_action.py] |
| Loss of operator audit trail after a failed run | Repudiation | Append immutable stage/action records to JSONL and keep artifacts per stage for replay. [VERIFIED: scripts/governance_common.py] [CITED: .planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md] |

## Recommended Sequencing

1. **Wave 0: Lock contracts first.** Add tests for role map, start bundle, stage/final artifact sections, event schema, and scope-reopen flow before implementation scripts. [VERIFIED: repo testing pattern]
2. **Wave 1: Start-run foundation.** Add `start_delivery_run.py`, delivery manifest schema, `.hermes/DELIVERY_SCOPE.md`, and delivery event/status helpers. [VERIFIED: repo research]
3. **Wave 2: Stage contract integration.** Extend or wrap existing orchestrator templates so each of the five stages has a named role, fixed artifact path, and gate transition. [CITED: skills/library/normalized/orchestrator-workflow.md] [CITED: docs/skill-governance/templates/stage-handoff-template-v0.2.md]
4. **Wave 3: Scope enforcement.** Add `request_scope_reopen.py` and integrate protected-surface checks with governance plus conformance. [VERIFIED: scripts/request_governance_approval.py] [VERIFIED: scripts/check_template_conformance.py]
5. **Wave 4: Final handoff and replay.** Add final-delivery rendering, latest status rendering, and replay validation tests from event stream plus artifacts. [CITED: docs/skill-governance/templates/final-delivery-template-v0.2.md] [VERIFIED: scripts/render_governance_status.py]
6. **Wave 5: Command integration.** Add one command wrapper entry in `orchestration/cron/commands.sh` for delivery-run lifecycle operations after the core contracts are stable. [VERIFIED: orchestration/cron/commands.sh]

This sequence minimizes rework because it locks contracts before wiring CLI entrypoints. [VERIFIED: repo research]

## Concrete Files to Add or Extend

### Add
- `scripts/start_delivery_run.py` — initialize delivery run manifest, scope artifact, first event, and latest-status render. [VERIFIED: repo research]
- `scripts/append_delivery_event.py` — validated append-only JSONL helper for delivery events. [VERIFIED: repo research]
- `scripts/render_delivery_status.py` — derive workspace-local `DELIVERY_STATUS.md` from `delivery-events.jsonl`. [VERIFIED: repo research]
- `scripts/request_scope_reopen.py` — delivery-friendly wrapper over governance approval for protected change or scope expansion. [VERIFIED: repo research]
- `scripts/validate_delivery_handoff.py` — lock required sections in stage/final delivery files. [VERIFIED: repo research]
- `tests/test_delivery_orchestration_contract.py` [VERIFIED: repo research]
- `tests/test_delivery_handoff_contract.py` [VERIFIED: repo research]
- `tests/test_start_delivery_run.py` [VERIFIED: repo research]
- `tests/test_scope_reopen_flow.py` [VERIFIED: repo research]
- `tests/test_delivery_events.py` [VERIFIED: repo research]
- `tests/test_delivery_run_replay.py` [VERIFIED: repo research]

### Extend
- `docs/skill-governance/templates/orchestrator-input-template-v0.2.md` — add required approved-project delivery bundle fields. [CITED: docs/skill-governance/templates/orchestrator-input-template-v0.2.md]
- `docs/skill-governance/templates/stage-handoff-template-v0.2.md` — optionally add `role`, `run_id`, and `scope_status` metadata without changing the core six sections. [CITED: docs/skill-governance/templates/stage-handoff-template-v0.2.md] [ASSUMED]
- `docs/skill-governance/templates/final-delivery-template-v0.2.md` — optionally add run identity and conformance report link. [CITED: docs/skill-governance/templates/final-delivery-template-v0.2.md] [ASSUMED]
- `skills/library/normalized/orchestrator-workflow.md` — extend from generic five-stage workflow to approved-project delivery-specific role naming and gating notes. [CITED: skills/library/normalized/orchestrator-workflow.md]
- `assets/workspaces/ceo/AGENTS.md` — add delivery-orchestrator examples and scope-reopen handling language. [CITED: assets/workspaces/ceo/AGENTS.md]
- `orchestration/cron/commands.sh` — add delivery-run wrapper commands once scripts exist. [VERIFIED: orchestration/cron/commands.sh]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Prompt-only guardrails are easier to add than blocked command paths and validated artifacts. | Common Pitfalls / Pitfall 1 | Low — affects explanation quality, not implementation direction. |
| A2 | Stage handoffs that mention “small extra change” without a reopen record are a likely warning sign. | Common Pitfalls / Pitfall 1 | Low — heuristic may vary. |
| A3 | Delivery roles may be treated as “new” and therefore overlooked in existing ownership rules. | Common Pitfalls / Pitfall 3 | Low — rationale wording only. |
| A4 | Latest views are convenient to edit by hand. | Common Pitfalls / Pitfall 4 | Low — rationale wording only. |
| A5 | Future cross-project delivery analytics may or may not justify a shared global delivery stream. | Open Questions (RESOLVED) 1 | Medium — future analytics may still influence later aggregation work, but not Phase 9 file placement. |
| A6 | Planner may want a delivery-specific ergonomic wrapper over raw governance CLI. | Open Questions (RESOLVED) 2 | Low — resolved in favor of a thin wrapper, so remaining risk is implementation detail only. |
| A7 | Phase 9 may need added markdown metadata fields like `run_id`, `role`, and `scope_status`. | Open Questions (RESOLVED) 3 / Concrete Files to Extend | Medium — resolved in favor of lightweight metadata additions while preserving the markdown-first template structure. |
| A8 | V3 Session Management does not materially apply to this script/orchestration phase. | Security Domain | Low — ASVS mapping nuance only. |
| A9 | V6 Cryptography does not materially apply to this script/orchestration phase. | Security Domain | Low — ASVS mapping nuance only. |

## Sources

### Primary (HIGH confidence)
- `.planning/phases/09-claude-code-delivery-team-orchestration/09-CONTEXT.md` - locked decisions, phase boundary, and canonical references
- `.planning/REQUIREMENTS.md` - TEAM-01 through TEAM-06 requirements
- `.planning/ROADMAP.md` - Phase 9 goal and success criteria
- `.planning/STATE.md` - current milestone focus
- `.planning/PROJECT.md` - approved-to-delivery factory goal and constraints
- `.planning/phases/06-execution-handoff-and-team-readiness/06-CONTEXT.md` - Core 9 markdown-first handoff pattern
- `.planning/phases/07-template-assetization-and-platform-contract/07-01-SUMMARY.md` - template contract and registry pattern
- `.planning/phases/08-shared-supabase-backend-guardrails/08-01-SUMMARY.md` - `.hermes/shared-backend-guardrails.json` handoff pattern
- `.planning/phases/08-shared-supabase-backend-guardrails/08-02-SUMMARY.md` - unified conformance gate pattern
- `docs/platform/standalone-saas-template-contract.md` - protected platform layer and safe extension surfaces
- `docs/MULTI_PROFILE_COORDINATION.md` - orchestrator-first coordination and artifact ownership
- `docs/STATE_CONTRACT.md` - write-permission and approval-gate rules
- `docs/OPERATIONS.md` - latest-view and governed-action operator rules
- `docs/skill-governance/README.md` - markdown-first governance and quick-run entrypoints
- `docs/skill-governance/routing/skill-manifest-v0.2.md` - staged loading/unloading and routing rules
- `docs/skill-governance/templates/orchestrator-input-template-v0.2.md` - workflow input template
- `docs/skill-governance/templates/stage-handoff-template-v0.2.md` - stage handoff contract
- `docs/skill-governance/templates/final-delivery-template-v0.2.md` - final delivery contract
- `docs/skill-governance/quick-run/orchestrator-workflow-card.md` - fixed five-stage quick-run flow
- `skills/library/normalized/orchestrator-workflow.md` - normalized design→development→testing→git→release workflow
- `scripts/instantiate_template_project.py` - workspace `.hermes` input bundle generation
- `scripts/check_template_conformance.py` - blocking protected-surface and shared-backend validation
- `scripts/governance_common.py` - append-only JSONL + latest-view derivation pattern
- `scripts/request_governance_approval.py` - governed request/approve/reject/override path
- `scripts/enforce_governed_action.py` - gate-before-mutate execution wrapper
- `scripts/render_governance_status.py` - derived latest-view renderer
- `orchestration/cron/commands.sh` - existing command-wrapper pattern
- `assets/workspaces/ceo/AGENTS.md` - orchestrator communication rules
- `assets/shared/governance/GOVERNANCE_STATUS.md` - human-readable latest view example
- `assets/shared/governance/governance_events.jsonl` - machine-readable authority stream example
- `tests/test_template_contract.py` - stable contract-locking pattern
- `tests/test_instantiate_template_project.py` - `.hermes` artifact expectations
- `tests/test_check_template_conformance.py` - blocking conformance test pattern

### Secondary (MEDIUM confidence)
- Environment probe results: `python --version`, `hermes --version`, and bash version checks executed during research. [VERIFIED: environment probe]

### Tertiary (LOW confidence)
- None. All non-verified reasoning is listed in the Assumptions Log. [VERIFIED: research synthesis]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - recommendations are direct extensions of checked-in scripts, tests, and docs rather than external ecosystem guesses. [VERIFIED: repo research]
- Architecture: HIGH - the orchestrator-first, markdown-first, JSONL-plus-latest-view pattern is already implemented elsewhere in the repo. [VERIFIED: scripts/governance_common.py] [CITED: docs/MULTI_PROFILE_COORDINATION.md]
- Pitfalls: MEDIUM - most pitfalls are strongly implied by current contracts, but several warning-sign heuristics are assumptions. [VERIFIED: repo research] [ASSUMED]

**Research date:** 2026-04-27
**Valid until:** 2026-05-27
