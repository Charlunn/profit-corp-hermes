# Phase 19: Specialist Evidence and UI Artifact Gates - Research

**Researched:** 2026-05-04
**Domain:** Approved-project delivery governance, specialist evidence gating, and UI artifact validation
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
### Specialist evidence bundle
- **D-01:** Every specialist stage must pass through one canonical evidence bundle made of the markdown handoff, transcript evidence, workspace-change inventory, and structured stage-evidence JSON persisted under `.hermes/stage-evidence/`.
- **D-02:** Structured stage evidence is the machine-readable gate record for specialist completion and must carry `run_id`, `stage`, `role`, `handoff_path`, `workspace_change_inventory_path`, and non-empty `evidence_links` for every specialist stage.
- **D-03:** Testing remains stricter than the other specialist stages: its structured evidence must also include explicit verification evidence so testing cannot pass on handoff text alone.

### UI artifact governance
- **D-04:** UI gating applies only to UI delivery surfaces and only to the `design` and `development` specialist stages; non-UI deliveries should not be blocked by `/ui-ux-pro-max` requirements.
- **D-05:** The governed UI artifact pair is `.hermes/ui-ux-design-system.md` plus `.hermes/ui-ux-design-system.summary.json`, and both must exist before a UI specialist stage can be considered ready.
- **D-06:** The UI summary must validate project-specific coverage for screen inventory, primary workflow, monetization surface, multilingual coverage, responsive rules, accessibility rules, and user-state coverage including `empty`, `loading`, `error`, and `success`.
- **D-07:** Development must revalidate the UI artifact against the approved brief contract and fail closed on stale, empty, or drifted design truth rather than treating the design artifact as a one-time file-existence check.

### Substance and template rejection
- **D-08:** Specialist completion must persist explicit substance results alongside the stage event so downstream validators and operator views can see whether the stage was product-specific or template-only.
- **D-09:** Workspace-change inventory is the primary evidence source for classifying specialist work as `product_only`, `protected_platform`, or `blocked_for_missing_information`; missing or unsafe inventories fail closed rather than falling back to optimistic assumptions.
- **D-10:** Template-only specialist output must be rejected at the specialist gate itself, with persisted `template_only`, `issues`, and touched-path evidence recorded in stage events and surfaced to status/review artifacts.

### Blocked-state operator guidance
- **D-11:** When a specialist or UI gate blocks, the authority record, append-only event, and operator-facing status must all preserve the same block reason, evidence path, failed gate name, and resume target so recovery continues from truth instead of re-derivation.
- **D-12:** Phase 19 blocked-state guidance should explain exactly which evidence artifact is missing or stale and what repair action is needed, but the broader recovered-run regression proof remains Phase 21 scope.

### the agent's Discretion
- The exact JSON field layout inside structured stage evidence, as long as the required gate fields and downstream validator needs remain satisfied.
- The precise wording of blocked-state operator messages and repair-action guidance, as long as they stay explicit, machine-linked, and resume-friendly.
- Whether UI artifact preflight writes only a stub contract or a richer starter artifact before specialist execution, as long as missing or stale UI truth still blocks downstream UI stages.

### Deferred Ideas (OUT OF SCOPE)
- Real product proof beyond specialist-stage substance checks stays in Phase 20, especially `/demo` and identity-only loophole removal as the canonical final-proof rule.
- Full bootstrap/resume regression hardening across fresh, blocked, resumed, and recovered runs stays in Phase 21 even though Phase 19 must preserve resume-friendly gate data.
- Adding new specialist roles, new delivery stages, or broader operator dashboard surfaces remains out of scope for this phase.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GATE-01 | Every specialist stage must persist a run-scoped handoff artifact, transcript evidence, and workspace-change evidence before the stage can pass | Extend the existing stage handoff, transcript, workspace inventory, and structured stage-evidence flow instead of adding a second gate system. [VERIFIED: scripts/start_approved_project_delivery.py] |
| GATE-02 | Stage completion must fail closed when required evidence is missing, empty, stale, malformed, or contradicts the recorded stage outcome | Reuse the existing fail-closed block reasons and validator checks for missing, empty, stale, and mismatch states; add any missing specialist-stage assertions in the same contract path. [VERIFIED: scripts/start_approved_project_delivery.py] [VERIFIED: scripts/validate_delivery_handoff.py] |
| GATE-03 | Stage substance validation must reject template-only work and record machine-readable gate outcomes that downstream validators and renderers can consume | Keep `substance` on specialist events as the canonical machine-readable surface and hard-stop stage completion when `template_only=true` or workspace classification is unsafe. [VERIFIED: scripts/validate_approved_delivery_pipeline.py] [VERIFIED: scripts/approved_delivery_governance.py] |
| UI-01 | UI-relevant approved-project runs must require a persisted `/ui-ux-pro-max` artifact before design can pass or frontend implementation can continue | Use the existing UI preflight artifact pair and restrict enforcement to UI delivery surface plus `design` and `development` stages. [VERIFIED: scripts/start_approved_project_delivery.py] |
| UI-02 | `/ui-ux-pro-max` artifact validation must check project-specific content coverage for screen inventory, workflow/conversion path, monetization surface, multilingual coverage, responsive rules, and accessibility rules | Keep the summary JSON as the canonical machine-readable coverage artifact and preserve the current required coverage keys and required UI states. [VERIFIED: scripts/start_approved_project_delivery.py] [VERIFIED: scripts/validate_delivery_handoff.py] |
| UI-03 | Design and development handoffs for UI scope must reference the validated design artifact and fail when artifact truth is stale or incomplete relative to the approved product contract | Revalidate summary `brief_contract` and `summary_hash` at both stages and require `ui_artifact_path` plus `ui_artifact_summary_path` in structured stage evidence. [VERIFIED: scripts/start_approved_project_delivery.py] [VERIFIED: scripts/validate_delivery_handoff.py] |
</phase_requirements>

## Summary

Phase 19 should be planned as a brownfield hardening pass over the existing Python delivery-governance pipeline, not as a redesign. The repo already has the core primitives this phase needs: specialist stage configs, UI artifact constants, fail-closed block reasons, structured stage-evidence validation, workspace-change classification, and downstream approved-delivery validation. [VERIFIED: scripts/start_approved_project_delivery.py] [VERIFIED: scripts/validate_delivery_handoff.py] [VERIFIED: scripts/approved_delivery_governance.py] [VERIFIED: scripts/validate_approved_delivery_pipeline.py]

The planning focus should be contract tightening and regression depth. The strongest approach is to make stage completion write one canonical evidence bundle, treat `.hermes/stage-evidence/*.json` as the authoritative machine-readable gate record, enforce `/ui-ux-pro-max` only for UI surface `design` and `development`, and make every block render the same failed gate, evidence path, repair action, and resume target across authority JSON, append-only events, and operator-facing markdown. [VERIFIED: 19-CONTEXT.md] [VERIFIED: scripts/start_approved_project_delivery.py] [VERIFIED: scripts/validate_approved_delivery_pipeline.py]

**Primary recommendation:** Use the existing `start_approved_project_delivery.py` -> `validate_delivery_handoff.py` -> `validate_approved_delivery_pipeline.py` chain as the only gate path, and plan Phase 19 around stricter evidence persistence, stricter UI summary revalidation, and targeted regression fixtures for blocked and recovered truth. [VERIFIED: scripts/start_approved_project_delivery.py] [VERIFIED: scripts/validate_delivery_handoff.py] [VERIFIED: scripts/validate_approved_delivery_pipeline.py]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Specialist stage completion gating | API / Backend | Database / Storage | The gating logic lives in Python orchestration scripts and writes file-backed authority/evidence artifacts rather than browser state. [VERIFIED: scripts/start_approved_project_delivery.py] |
| Structured stage-evidence persistence | Database / Storage | API / Backend | `.hermes/stage-evidence/*.json` is the persisted machine-readable record, while Python orchestration owns writing and validating it. [VERIFIED: 19-CONTEXT.md] [VERIFIED: scripts/start_approved_project_delivery.py] |
| UI artifact preflight and stale-truth validation | API / Backend | Database / Storage | UI artifact enforcement is executed by delivery orchestration before and after specialist stages, and the artifacts are persisted as workspace files. [VERIFIED: scripts/start_approved_project_delivery.py] |
| Workspace-change substance classification | API / Backend | Database / Storage | Classification logic runs in `approved_delivery_governance.py` and emits JSON evidence under `.hermes`. [VERIFIED: scripts/approved_delivery_governance.py] |
| Operator blocked-state guidance | API / Backend | Browser / Client | Authority JSON and event history are the source of truth; markdown status/review surfaces only render that truth. [VERIFIED: 19-CONTEXT.md] [VERIFIED: scripts/validate_approved_delivery_pipeline.py] |
| Final operator visibility of specialist evidence | Browser / Client | API / Backend | Status and final-review markdown must expose artifact links and gate outcomes, but they are derived from backend-owned evidence. [VERIFIED: scripts/validate_approved_delivery_pipeline.py] |

## Project Constraints (from AGENTS.md)

- Frontend UI work must invoke `/ui-ux-pro-max` before proposing implementation steps or code changes. [VERIFIED: AGENTS.md]
- The resulting design-system output is the source of truth for layout, typography, color, spacing, responsiveness, accessibility, and interaction details. [VERIFIED: AGENTS.md]
- If frontend UI work touches user-facing implementation, `/ui-ux-pro-max` is still mandatory even when the request is implementation-only. [VERIFIED: AGENTS.md]
- If the installed skill is missing, restore it from the project root with `uipro init --ai Codex` before frontend UI work continues. [VERIFIED: AGENTS.md]

## Standard Stack

### Core

| Library / Tool | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.11.15 | Delivery orchestration, validators, JSON artifact writing, and CLI entrypoints | The existing approved-delivery pipeline and validators are Python scripts already wired into the repo. [VERIFIED: python --version] [VERIFIED: scripts/start_approved_project_delivery.py] |
| Python standard library (`json`, `pathlib`, `subprocess`, `argparse`) | Bundled with Python 3.11.15 | File-backed authority/evidence handling and CLI orchestration | The current implementation already relies on stdlib-only primitives for this path, which keeps Phase 19 low-risk and dependency-free. [VERIFIED: python --version] [VERIFIED: scripts/start_approved_project_delivery.py] [VERIFIED: scripts/approved_delivery_governance.py] |
| File-backed governance artifacts (`JSON`, `JSONL`, `Markdown`) | Repo contract | Authority truth, append-only events, status, handoffs, and structured evidence | Phase 19 explicitly extends the existing file-backed governance model rather than replacing it. [VERIFIED: REQUIREMENTS.md] [VERIFIED: 19-CONTEXT.md] |

### Supporting

| Library / Tool | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 8.4.2 | Test runner for the delivery-governance suite | Use for focused Phase 19 regression execution even though the tests are `unittest`-style. [VERIFIED: pytest --version] [VERIFIED: tests/test_approved_delivery_pipeline_cli.py] |
| git | 2.53.0.windows.1 | Fallback workspace diff collection when explicit inventory is missing | Use only as the existing fallback path inside workspace-change collection. [VERIFIED: git --version] [VERIFIED: scripts/approved_delivery_governance.py] |
| `/ui-ux-pro-max` skill | Installed in `.agents/skills` and `.claude/skills` | Goverened UI design authority artifact for UI scope | Use for UI delivery surfaces in `design` and `development` stages only. [VERIFIED: AGENTS.md] [VERIFIED: .agents/skills/ui-ux-pro-max/SKILL.md] [VERIFIED: scripts/start_approved_project_delivery.py] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Existing file-backed stage evidence | Database-backed workflow state | Out of scope because project requirements explicitly reject replacing the current authority/event/artifact model. [VERIFIED: PROJECT.md] [VERIFIED: REQUIREMENTS.md] |
| Existing Python validators | New standalone gate service | Would duplicate the current source of truth and increase drift risk across runtime, validator, and operator views. [VERIFIED: 19-CONTEXT.md] [VERIFIED: scripts/validate_delivery_handoff.py] [VERIFIED: scripts/validate_approved_delivery_pipeline.py] |
| Existing `/ui-ux-pro-max` artifact pair | Prompt-only UI policy enforcement | Explicitly disallowed by project rules and milestone scope because policy-only mentions do not count as compliance. [VERIFIED: AGENTS.md] [VERIFIED: REQUIREMENTS.md] |

**Installation:**
```bash
pip install pytest
```

This phase does not require a new application dependency beyond the existing Python stack; `pytest` is already available in the current environment. [VERIFIED: pytest --version]

## Architecture Patterns

### System Architecture Diagram

```text
Approved brief + authority JSON
        |
        v
start_approved_project_delivery.py
        |
        +--> UI preflight (UI surface only)
        |         |
        |         v
        |   .hermes/ui-ux-design-system.md
        |   .hermes/ui-ux-design-system.summary.json
        |
        +--> Specialist dispatch
        |         |
        |         v
        |   transcript + handoff markdown + workspace-change inventory
        |
        +--> Structured stage-evidence write
        |         |
        |         v
        |   .hermes/stage-evidence/<stage>.json
        |
        +--> Stage gate decision
                  |
          +-------+--------+
          |                |
          v                v
        pass            block
          |                |
          v                v
validate_delivery_handoff.py   authority/event/status sync
          |                |
          +-------+--------+
                  |
                  v
validate_approved_delivery_pipeline.py
                  |
                  v
Operator status + final review + resume target
```

The primary flow is already present; Phase 19 should harden each arrow so missing or stale evidence blocks immediately and renders consistently. [VERIFIED: scripts/start_approved_project_delivery.py] [VERIFIED: scripts/validate_delivery_handoff.py] [VERIFIED: scripts/validate_approved_delivery_pipeline.py]

### Recommended Project Structure

```text
scripts/
├── start_approved_project_delivery.py      # Runtime gating and persistence
├── validate_delivery_handoff.py            # Stage handoff/evidence contract validator
├── validate_approved_delivery_pipeline.py  # Authority/event/status/final-review cross-validator
└── approved_delivery_governance.py         # Workspace classification and governance helpers

docs/skill-governance/templates/
├── stage-handoff-template-v0.2.md          # Canonical stage handoff structure
└── final-delivery-template-v0.2.md         # Canonical final delivery structure

tests/
└── test_approved_delivery_pipeline_cli.py  # Regression coverage for fail-closed delivery governance
```

This is the correct implementation boundary for Phase 19 work. [VERIFIED: 19-CONTEXT.md] [VERIFIED: codebase file discovery]

### Pattern 1: Canonical Stage-Evidence Bundle

**What:** Every specialist stage should complete only after persisting the handoff markdown, Claude transcript, workspace-change inventory, and one structured JSON evidence record tied to the same `run_id`. [VERIFIED: 19-CONTEXT.md] [VERIFIED: scripts/validate_delivery_handoff.py]

**When to use:** Use this for all specialist stages, with testing adding `verification_evidence`. [VERIFIED: 19-CONTEXT.md] [VERIFIED: scripts/validate_delivery_handoff.py]

**Example:**
```python
# Source: scripts/validate_delivery_handoff.py
if str(payload.get("run_id", "")).strip() != run_id:
    raise DeliveryHandoffValidationError(f"{path.name} run_id mismatch")
if str(payload.get("handoff_path", "")).strip() != expected_handoff_path:
    raise DeliveryHandoffValidationError(f"{path.name} handoff path mismatch")
if not str(payload.get("workspace_change_inventory_path", "")).strip():
    raise DeliveryHandoffValidationError(f"{path.name} missing workspace change inventory path")
if not isinstance(payload.get("evidence_links"), list) or not payload.get("evidence_links"):
    raise DeliveryHandoffValidationError(f"{path.name} missing evidence links")
```

### Pattern 2: UI Artifact Summary as Machine-Readable Contract

**What:** Treat `.hermes/ui-ux-design-system.summary.json` as the real gate target, with the markdown artifact providing human-readable design authority. [VERIFIED: scripts/start_approved_project_delivery.py] [VERIFIED: scripts/validate_delivery_handoff.py]

**When to use:** Only for UI delivery surfaces at `design` and `development`. [VERIFIED: 19-CONTEXT.md] [VERIFIED: scripts/start_approved_project_delivery.py]

**Example:**
```python
# Source: scripts/start_approved_project_delivery.py
missing_coverage = [key for key in REQUIRED_UI_ARTIFACT_COVERAGE_KEYS if not normalize_list(list(coverage.get(key, [])))]
if missing_coverage:
    return (
        False,
        "ui_ux_artifact_coverage_incomplete",
        summary_path.as_posix(),
        "ui-ux artifact coverage missing: " + ", ".join(missing_coverage),
    )
if summary.get("summary_hash") != expected.get("summary_hash"):
    return False, "ui_ux_artifact_stale", summary_path.as_posix(), "ui-ux artifact summary hash drifted from approved brief"
```

### Pattern 3: Workspace Inventory Drives Substance Classification

**What:** Use workspace-change inventory as the canonical source for product-only vs protected-platform vs blocked-for-missing-information classification. [VERIFIED: 19-CONTEXT.md] [VERIFIED: scripts/approved_delivery_governance.py]

**When to use:** Use before specialist completion is marked pass, and persist the classification evidence path into stage evidence and downstream operator surfaces. [VERIFIED: scripts/approved_delivery_governance.py] [VERIFIED: scripts/validate_approved_delivery_pipeline.py]

**Example:**
```python
# Source: scripts/approved_delivery_governance.py
if not normalized_touched_paths and not unknown_paths:
    classification = "blocked_for_missing_information"
    block_reason = "missing_workspace_change_inventory"
elif unknown_paths:
    classification = "blocked_for_missing_information"
    block_reason = "workspace_change_inventory_incomplete"
elif protected_matches:
    classification = "protected_platform"
```

### Anti-Patterns to Avoid

- **Second evidence system:** Do not add a parallel gate record outside `.hermes/stage-evidence/`; the existing validators already expect one structured evidence artifact per stage. [VERIFIED: 19-CONTEXT.md] [VERIFIED: scripts/validate_delivery_handoff.py]
- **UI file-existence-only checks:** Do not treat the markdown UI artifact alone as sufficient; the summary JSON and approved-brief drift check are the actual gate. [VERIFIED: scripts/start_approved_project_delivery.py]
- **Optimistic workspace classification:** Do not infer `product_only` when inventory is missing, empty, or unsafe to normalize; the current governance helper already marks those cases as blocked. [VERIFIED: scripts/approved_delivery_governance.py]
- **End-of-pipeline-only template rejection:** Do not defer template-only rejection until final review; existing validator behavior and milestone scope require rejection at specialist completion. [VERIFIED: 19-CONTEXT.md] [VERIFIED: scripts/validate_approved_delivery_pipeline.py]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Stage evidence schema | A new bespoke validator per stage | Extend `validate_stage_evidence` and the manifest/event contract | One shared validator already enforces run, role, stage, handoff, inventory, UI, and testing evidence invariants. [VERIFIED: scripts/validate_delivery_handoff.py] |
| UI artifact coverage rules | Prompt heuristics or manual checklist parsing | The existing summary JSON coverage object plus `summary_hash` drift check | The repo already has machine-readable coverage keys and brief-contract comparison logic. [VERIFIED: scripts/start_approved_project_delivery.py] |
| Substance classification | Ad hoc path heuristics inside the orchestrator | `inspect_workspace_changes` and its persisted classification report | The governance helper already normalizes paths, detects unsafe paths, and emits evidence JSON. [VERIFIED: scripts/approved_delivery_governance.py] |
| Blocked-state rendering | New UI-only state model | Existing authority JSON + append-only events + status/final-review renderers | Current validators already require consistency across those surfaces. [VERIFIED: scripts/validate_approved_delivery_pipeline.py] |

**Key insight:** The repo already contains the gate surfaces this phase needs; Phase 19 should tighten invariants and test coverage, not add new storage or orchestration layers. [VERIFIED: 19-CONTEXT.md] [VERIFIED: codebase file discovery]

## Common Pitfalls

### Pitfall 1: Validator Drift Between Runtime and Review
**What goes wrong:** Runtime stage completion writes fields that downstream validators do not assert, or validators require fields runtime never writes. [VERIFIED: 19-CONTEXT.md]  
**Why it happens:** The stage gate spans multiple files: orchestrator, handoff validator, and approved-delivery validator. [VERIFIED: scripts/start_approved_project_delivery.py] [VERIFIED: scripts/validate_delivery_handoff.py] [VERIFIED: scripts/validate_approved_delivery_pipeline.py]  
**How to avoid:** Plan paired changes across all three files whenever the structured stage-evidence schema changes. [VERIFIED: 19-CONTEXT.md]  
**Warning signs:** A stage passes locally but `validate_delivery_handoff.py` or `validate_approved_delivery_pipeline.py` fails on missing linkage or field mismatch. [VERIFIED: scripts/validate_delivery_handoff.py] [VERIFIED: scripts/validate_approved_delivery_pipeline.py]

### Pitfall 2: UI Governance Regresses to Ceremony
**What goes wrong:** The pipeline only checks that `.hermes/ui-ux-design-system.md` exists, so stale or generic UI truth can slip into development. [VERIFIED: REQUIREMENTS.md]  
**Why it happens:** Markdown presence is cheaper to check than content coverage and brief drift. [ASSUMED]  
**How to avoid:** Keep the summary JSON as the pass/fail artifact and revalidate `brief_contract` plus `summary_hash` at both `design` and `development`. [VERIFIED: scripts/start_approved_project_delivery.py]  
**Warning signs:** Development passes even when product scope, language coverage, or screen inventory changed without a refreshed UI summary. [VERIFIED: scripts/start_approved_project_delivery.py]

### Pitfall 3: Substance Gate Looks Only at Changed Files Count
**What goes wrong:** A stage can look “non-empty” while still only touching template identity files or protected platform surfaces. [VERIFIED: REQUIREMENTS.md] [VERIFIED: tests/test_approved_delivery_pipeline_cli.py]  
**Why it happens:** Simple file-count checks do not distinguish product-only, protected-platform, or missing-information states. [VERIFIED: scripts/approved_delivery_governance.py]  
**How to avoid:** Use workspace classification plus persisted `substance.template_only` and `issues` on the event, and block immediately on unsafe classifications. [VERIFIED: 19-CONTEXT.md] [VERIFIED: scripts/approved_delivery_governance.py] [VERIFIED: scripts/validate_approved_delivery_pipeline.py]  
**Warning signs:** Status/review markdown shows template-only warnings after a stage has already been marked pass. [VERIFIED: scripts/validate_approved_delivery_pipeline.py]

### Pitfall 4: Recovered Completion Still Shows Active Block State
**What goes wrong:** Authority or status surfaces carry stale `block_reason` or `latest_blocked_prerequisite.status=blocked` after the run recovers. [VERIFIED: scripts/validate_approved_delivery_pipeline.py] [VERIFIED: tests/test_approved_delivery_pipeline_cli.py]  
**Why it happens:** Block state is preserved for audit history, but current-state truth must be updated separately. [VERIFIED: 19-CONTEXT.md]  
**How to avoid:** Ensure each block/resolution path updates current pipeline state and preserves blocked history as resolved audit evidence only. [VERIFIED: scripts/start_approved_project_delivery.py] [VERIFIED: scripts/validate_approved_delivery_pipeline.py]  
**Warning signs:** Validator fails with `completed pipeline still carries blocked current-state fields in authority`. [VERIFIED: tests/test_approved_delivery_pipeline_cli.py]

## Code Examples

Verified patterns from the codebase:

### UI Artifact Coverage Contract
```python
# Source: scripts/validate_delivery_handoff.py
if expected_stage in {"design", "development"}:
    for field in ("ui_artifact_path", "ui_artifact_summary_path"):
        if not str(payload.get(field, "")).strip():
            raise DeliveryHandoffValidationError(f"{path.name} missing {field}")
    summary_payload = load_json(Path(str(payload.get("ui_artifact_summary_path"))), "ui-ux artifact summary")
    coverage = summary_payload.get("coverage", {})
    missing_coverage = [key for key in REQUIRED_UI_COVERAGE_KEYS if not isinstance(coverage.get(key), list) or not coverage.get(key)]
```

### Blocked-State Visibility Contract
```python
# Source: scripts/validate_approved_delivery_pipeline.py
if not block_reason:
    raise ApprovedDeliveryPipelineValidationError("blocked pipeline state missing persisted block reason")
if not evidence_path:
    raise ApprovedDeliveryPipelineValidationError("blocked pipeline state missing persisted evidence path")
if failed_gate and failed_gate.lower() not in lowered:
    raise ApprovedDeliveryPipelineValidationError("status view missing failed gate linkage")
if repair_action and repair_action.lower() not in lowered:
    raise ApprovedDeliveryPipelineValidationError("status view missing repair action guidance")
```

### Workspace Classification Contract
```python
# Source: scripts/approved_delivery_governance.py
return {
    "classification": classification,
    "protected_matches": protected_matches,
    "unknown_paths": unknown_paths,
    "reasons": reasons,
    "touched_paths": normalized_touched_paths,
    "block_reason": block_reason,
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Policy-only `/ui-ux-pro-max` expectation | Artifact-backed UI governance with summary coverage and brief-drift checks | Present in current Phase 19 code/context as of 2026-05-04 | Phase 19 should harden this path instead of inventing another UI gate. [VERIFIED: REQUIREMENTS.md] [VERIFIED: 19-CONTEXT.md] [VERIFIED: scripts/start_approved_project_delivery.py] |
| Human-readable-only specialist handoffs | Handoff markdown plus structured stage-evidence JSON and replay events | Already established before Phase 19 planning | Planning should preserve one machine-readable source of truth for gates. [VERIFIED: 19-CONTEXT.md] [VERIFIED: scripts/validate_delivery_handoff.py] |
| Late template rejection in downstream validation | Template-only specialist output also exposed as event `substance` and validator failure | Already covered in current validator/test path | Phase 19 should move enforcement as early as specialist completion and add missing regressions there. [VERIFIED: 19-CONTEXT.md] [VERIFIED: scripts/validate_approved_delivery_pipeline.py] [VERIFIED: tests/test_approved_delivery_pipeline_cli.py] |

**Deprecated/outdated:**
- Policy-only UI mentions as sufficient compliance are explicitly out of scope for this milestone. [VERIFIED: REQUIREMENTS.md]
- Replacing file-backed authority with a new database or workflow engine is explicitly out of scope. [VERIFIED: REQUIREMENTS.md] [VERIFIED: PROJECT.md]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Markdown presence is cheaper to check than content coverage and brief drift. | Common Pitfalls - Pitfall 2 | Low; this only explains likely failure mode, not the recommended implementation. |

## Open Questions (RESOLVED)

1. **Transcript evidence rule**
   - **Decision:** Transcript evidence must be present and non-empty before any specialist stage can pass.
   - **Why:** Phase requirements already require transcript evidence as part of the specialist evidence bundle, and a present-but-empty transcript is not materially different from missing evidence in a fail-closed governance path. [VERIFIED: REQUIREMENTS.md] [VERIFIED: 19-CONTEXT.md]
   - **Implementation guidance:** Enforce the same non-empty transcript rule in runtime bundle validation, stage-evidence replay validation, and CLI regression fixtures so no stage can pass on path presence alone. [VERIFIED: scripts/start_approved_project_delivery.py] [VERIFIED: scripts/validate_delivery_handoff.py]

2. **Failed gate naming source**
   - **Decision:** Failed specialist/UI gate names must be sourced from one canonical taxonomy defined in `scripts/start_approved_project_delivery.py`, then reused unchanged by status/final-review rendering and validator checks.
   - **Why:** The orchestrator is already the runtime source for block reasons, repair action persistence, and event payload generation, so it is the correct authority for gate-name emission. [VERIFIED: scripts/start_approved_project_delivery.py] [VERIFIED: scripts/validate_approved_delivery_pipeline.py]
   - **Implementation guidance:** Use stable enum-like gate names for transcript, structured-evidence, UI-artifact, and substance failures; regression tests should assert those names appear consistently across authority, events, status, and final review. [VERIFIED: 19-CONTEXT.md] [VERIFIED: tests/test_approved_delivery_pipeline_cli.py]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Runtime scripts and validators | ✓ | 3.11.15 | — |
| pytest | Phase 19 regression execution | ✓ | 8.4.2 | `python -m pytest` with same environment |
| git | Workspace inventory fallback path | ✓ | 2.53.0.windows.1 | Explicit `.hermes/workspace-changes.json` inventory |
| `/ui-ux-pro-max` skill | UI artifact generation/validation workflow | ✓ | repo-local skill | None for UI-scope work; project rules require restoration if missing. [VERIFIED: AGENTS.md] |

**Missing dependencies with no fallback:**
- None. [VERIFIED: python --version] [VERIFIED: pytest --version] [VERIFIED: git --version]

**Missing dependencies with fallback:**
- None in the current environment. [VERIFIED: python --version] [VERIFIED: pytest --version] [VERIFIED: git --version]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | `pytest 8.4.2` running `unittest`-style tests [VERIFIED: pytest --version] [VERIFIED: tests/test_approved_delivery_pipeline_cli.py] |
| Config file | none detected in repo root during research [VERIFIED: codebase file discovery] |
| Quick run command | `pytest tests/test_approved_delivery_pipeline_cli.py -q` [VERIFIED: tests/test_approved_delivery_pipeline_cli.py] |
| Full suite command | `pytest -q` [ASSUMED] |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| GATE-01 | Specialist stages require handoff, transcript, workspace inventory, and structured evidence before pass | integration | `pytest tests/test_approved_delivery_pipeline_cli.py -q -k "handoff or structured"` | ✅ |
| GATE-02 | Missing, empty, stale, malformed, or contradictory evidence blocks stage completion | integration | `pytest tests/test_approved_delivery_pipeline_cli.py -q -k "blocked or stale or mismatch"` | ✅ |
| GATE-03 | Template-only specialist output is rejected and machine-readable outcomes persist | integration | `pytest tests/test_approved_delivery_pipeline_cli.py -q -k "template_only"` | ✅ |
| UI-01 | UI runs require `/ui-ux-pro-max` artifact pair before design/development pass | integration | `pytest tests/test_approved_delivery_pipeline_cli.py -q -k "ui"` | ❌ Wave 0 |
| UI-02 | UI summary coverage validates project-specific content keys and required states | integration | `pytest tests/test_approved_delivery_pipeline_cli.py -q -k "coverage"` | ❌ Wave 0 |
| UI-03 | Design/development fail on stale or drifted UI artifact truth | integration | `pytest tests/test_approved_delivery_pipeline_cli.py -q -k "stale"` | ❌ Wave 0 |

### Sampling Rate

- **Per task commit:** `pytest tests/test_approved_delivery_pipeline_cli.py -q`
- **Per wave merge:** `pytest tests/test_approved_delivery_pipeline_cli.py -q`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps

- [ ] Add explicit CLI/integration tests for missing UI artifact pair on UI-scoped `design` and `development`. [VERIFIED: REQUIREMENTS.md] [VERIFIED: scripts/start_approved_project_delivery.py]
- [ ] Add explicit tests for stale `brief_contract` and `summary_hash` drift blocking development. [VERIFIED: scripts/start_approved_project_delivery.py]
- [ ] Add explicit tests for missing or empty transcript evidence if the phase locks that contract. [VERIFIED: REQUIREMENTS.md]
- [ ] Add explicit tests that blocked-state status/final-review surfaces include failed gate name, evidence path, repair action, and resume target for specialist/UI blocks. [VERIFIED: 19-CONTEXT.md] [VERIFIED: scripts/validate_approved_delivery_pipeline.py]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no | Not a primary Phase 19 change surface; existing auth delivery path remains out of scope. [VERIFIED: REQUIREMENTS.md] |
| V3 Session Management | no | Not a primary Phase 19 change surface. [VERIFIED: REQUIREMENTS.md] |
| V4 Access Control | no | Not a primary Phase 19 change surface. [VERIFIED: REQUIREMENTS.md] |
| V5 Input Validation | yes | Validate JSON evidence shape, path linkage, run/stage matching, and UI summary coverage before pass. [VERIFIED: scripts/validate_delivery_handoff.py] [VERIFIED: scripts/validate_approved_delivery_pipeline.py] |
| V6 Cryptography | no | No new cryptographic controls are introduced in this phase. [VERIFIED: 19-CONTEXT.md] |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Artifact spoofing with mismatched `run_id` or `handoff_path` | Tampering | Enforce run/stage/role/handoff path matching in structured evidence validation. [VERIFIED: scripts/validate_delivery_handoff.py] |
| False-positive delivery completion through stale blocked fields | Repudiation | Validate current-state precedence so completed state cannot retain active blocked markers. [VERIFIED: scripts/validate_approved_delivery_pipeline.py] |
| Unsafe path injection in workspace inventory | Tampering | Normalize paths relative to workspace and block on unknown/outside-workspace paths. [VERIFIED: scripts/approved_delivery_governance.py] |
| Generic template output masquerading as real work | Spoofing | Persist `substance.template_only` and reject template-only specialist output. [VERIFIED: scripts/validate_approved_delivery_pipeline.py] [VERIFIED: tests/test_approved_delivery_pipeline_cli.py] |

## Sources

### Primary (HIGH confidence)

- `19-CONTEXT.md` - locked phase decisions, scope, integration points, and canonical references.
- `.planning/REQUIREMENTS.md` - authoritative requirement IDs and out-of-scope constraints.
- `.planning/PROJECT.md` - milestone-level governance constraints and brownfield boundaries.
- `scripts/start_approved_project_delivery.py` - runtime stage gating, UI artifact logic, and blocked-state persistence.
- `scripts/validate_delivery_handoff.py` - stage handoff and structured evidence contract.
- `scripts/validate_approved_delivery_pipeline.py` - authority/event/status/final-review cross-validation rules.
- `scripts/approved_delivery_governance.py` - workspace inventory collection and classification logic.
- `tests/test_approved_delivery_pipeline_cli.py` - current regression expectations for template-only rejection and recovered-state precedence.
- `AGENTS.md` - project-specific `/ui-ux-pro-max` enforcement rules.
- Local environment checks: `python --version`, `pytest --version`, `git --version`.

### Secondary (MEDIUM confidence)

- None.

### Tertiary (LOW confidence)

- None beyond the single explicit assumption logged above.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - The phase is constrained to existing Python scripts, existing file-backed artifacts, and locally verified tooling. [VERIFIED: scripts/start_approved_project_delivery.py] [VERIFIED: python --version] [VERIFIED: pytest --version]
- Architecture: HIGH - The responsible files and current data flow are explicit in code and phase context. [VERIFIED: 19-CONTEXT.md] [VERIFIED: scripts/validate_approved_delivery_pipeline.py]
- Pitfalls: HIGH - The main failure modes are already represented by current validators, block reasons, and tests. [VERIFIED: scripts/start_approved_project_delivery.py] [VERIFIED: tests/test_approved_delivery_pipeline_cli.py]

**Research date:** 2026-05-04
**Valid until:** 2026-06-03
