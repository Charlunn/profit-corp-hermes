# Architecture Research

**Domain:** Approved-project delivery governance hardening
**Milestone:** v1.1.2
**Researched:** 2026-05-03
**Confidence:** HIGH

## Scope

This research is intentionally narrow. It does **not** propose a redesign of the approved-project pipeline. It describes how four governance-hardening requirements should integrate into the existing brownfield architecture:

1. stricter specialist evidence gating
2. `/ui-ux-pro-max` artifact validation
3. handoff contract alignment
4. removal of `/demo` proof assumptions

The right approach is to extend the existing authority-record and append-only event model, not replace it.

## Current Architecture Baseline

The existing approved-project system already has the correct backbone for this work:

- `APPROVED_PROJECT.json` is the cross-stage authority record
- `approved-delivery-events.jsonl` is the append-only execution history
- workspace-local `.hermes/` artifacts hold run-local evidence and stage handoffs
- `DELIVERY_PIPELINE_STATUS.md` and `FINAL_OPERATOR_REVIEW.md` are rendered operator views
- `validate_approved_delivery_pipeline.py` is the top-level cross-link validator
- `start_approved_project_delivery.py` is the main integration orchestrator
- `check_template_conformance.py` enforces template/platform boundaries
- `request_platform_justification.py` handles protected-surface approval state

That means v1.1.2 should be an **integration hardening milestone**, not a new subsystem.

## Recommended Integration Model

```text
Approved bundle
(APPROVED_PROJECT.json + PROJECT_BRIEF.md)
        |
        v
start_approved_project_delivery.py
        |
        +--> workspace instantiation
        +--> conformance check
        +--> delivery run bootstrap
        +--> specialist stages
                 |
                 +--> stage handoff artifact
                 +--> transcript evidence
                 +--> workspace change inventory
                 +--> stage substance validation
                 +--> UI artifact validation when relevant
        |
        +--> protected-surface / platform-justification gate
        +--> GitHub/Vercel governed actions
        +--> final handoff capture
        |
        v
authority surfaces
- APPROVED_PROJECT.json
- approved-delivery-events.jsonl
- DELIVERY_PIPELINE_STATUS.md
- FINAL_OPERATOR_REVIEW.md
        |
        v
validate_approved_delivery_pipeline.py
```

## Integration Points by Requirement

### 1. Stricter Specialist Evidence Gating

#### Recommendation

Keep the current specialist stage model, but make stage completion depend on **evidence completeness + substance completeness**, not just artifact existence.

#### Existing surfaces to modify

- `scripts/start_approved_project_delivery.py`
- `scripts/render_approved_delivery_status.py`
- `scripts/validate_approved_delivery_pipeline.py`
- tests around approved delivery pipeline and resume behavior

#### Existing mechanisms to build on

The code already has good primitives:

- per-stage transcript capture: `.hermes/<stage>-claude-code.txt`
- workspace inventory: `.hermes/workspace-changes.json`
- stage substance evaluation via `validate_stage_substance(...)`
- event-level `substance` payload with `template_only` and `issues`

#### What to tighten

Add a stricter stage pass contract at the point where specialist stages are persisted:

A specialist stage should only be marked ready/completed when all are true:
- stage handoff file exists
- transcript evidence exists
- workspace change inventory exists
- `substance.template_only == false`
- `substance.issues` is empty
- handoff explicitly names changed files, user-visible behavior, and pain-point mapping

#### Truth location

- **Current truth for stage outcome:** `approved-delivery-events.jsonl`
- **Current truth for latest stage state:** `APPROVED_PROJECT.json.pipeline`
- **Local stage evidence truth:** workspace `.hermes/` artifacts

Do **not** create a second authority store. Persist stricter evidence results into the existing event payload and pipeline state.

#### Suggested event shape extension

Use the existing `substance` block and extend it rather than inventing a new top-level record:

```json
"substance": {
  "template_only": false,
  "issues": [],
  "handoff_contract_ok": true,
  "evidence_complete": true,
  "ui_artifact_validated": true,
  "product_proof_paths": [...]
}
```

This keeps event history as the granular truth while allowing status rendering and regression tests to inspect one schema.

### 2. `/ui-ux-pro-max` Artifact Validation

#### Recommendation

Treat the UI artifact as a **governed prerequisite artifact** for UI-relevant specialist stages, not as an informal note.

#### Existing surfaces to modify

- `scripts/start_approved_project_delivery.py`
- possibly `scripts/validate_approved_delivery_pipeline.py`
- specialist-stage tests

#### Existing surfaces already present

- UI contract defaults in `DEFAULT_UI_ARTIFACT_CONTRACT`
- UI artifact path: `.hermes/ui-ux-design-system.md`
- preflight generator: `ensure_ui_ux_preflight(...)`
- stage targeting via `UI_SPECIALIST_STAGES = {"design", "development"}`
- CLAUDE.md rule that frontend work must invoke `/ui-ux-pro-max`

#### Problem in current model

The current flow can generate a UI preflight artifact, but the architecture still treats artifact presence as close to sufficient. For governance hardening, presence is not enough; the artifact must prove contract coverage.

#### What to validate

For UI-relevant projects/stages, validate that `.hermes/ui-ux-design-system.md` includes:
- explicit reference to `/ui-ux-pro-max`
- screen inventory
- primary conversion / primary workflow
- monetization surface
- empty/loading/error/success states
- responsive behavior
- accessibility rules
- multilingual behavior
- English and Chinese coverage at minimum, plus required language surfaces from product requirements

#### Truth location

- **Authority for requirement:** `APPROVED_PROJECT.json.product_requirements.ui_artifact_contract`
- **Authority for concrete artifact:** workspace `.hermes/ui-ux-design-system.md`
- **Authority for validation result:** stage event `substance.ui_artifact_validated` and/or pipeline evidence path

Do not move design truth into the authority record itself. The authority record should declare the contract; the workspace artifact should satisfy it.

#### Integration rule

- validation belongs in the specialist-stage completion path, before stage success is appended
- status rendering should show whether UI artifact validation passed for design/development
- final pipeline validation should fail if UI stages passed without valid UI artifact coverage when the project surface is UI-driven

### 3. Handoff Contract Alignment

#### Recommendation

Unify the runtime-generated stage handoff format with the validator’s expected contract. Right now this is the biggest architectural drift.

#### Existing mismatch

`validate_delivery_handoff.py` expects:
- stage sections `## 1) Stage Summary` through `## 6) Next Stage Input`
- required metadata tokens including `` `run_id` `role` `stage` `scope_status` `next_stage` ``

But `build_specialist_handoff_markdown(...)` in `start_approved_project_delivery.py` currently emits:
- nine sections, including `Changed Files`, `User Visible Behavior`, and `Pain Point Mapping`
- `Gate Decision` as section 7
- `Next Stage Input` as section 9

That means the producer and validator are not aligned on the canonical handoff schema.

#### Best integration choice

Do **not** loosen validation to accept arbitrary formats. Instead, align generation and validation around one canonical contract.

#### Opinionated recommendation

Make `validate_delivery_handoff.py` the source of structural truth, then extend it deliberately to include the new governance-hardening fields that v1.1.2 needs.

Recommended canonical stage handoff sections:
1. Stage Summary
2. Outputs Produced
3. Evidence Links
4. Changed Files
5. User Visible Behavior
6. Pain Point Mapping
7. Gate Decision
8. Open Risks
9. Next Stage Input

Then update both:
- `build_specialist_handoff_markdown(...)`
- `validate_delivery_handoff.py`

This is better than collapsing the richer handoff back to the older six-section template because changed files, user-visible behavior, and pain-point mapping are exactly the evidence gates needed for this milestone.

#### Truth location

- **Stage handoff structure truth:** `validate_delivery_handoff.py`
- **Stage handoff instance truth:** workspace `.hermes/stage-handoffs/*.md`
- **Cross-stage summary truth:** `approved-delivery-events.jsonl`

The validator, not the generator, should define the contract. The generator should conform to it.

### 4. Removal of `/demo` Proof Assumptions

#### Recommendation

Remove `/demo` as a privileged proof surface. Product proof should be inferred from approved workflow implementation paths and user-visible behavior, not from one special route existing.

#### Existing problematic surface

`materialize_product_surface(...)` currently writes both:
- `src/app/page.tsx`
- `src/app/dashboard/page.tsx`
- `src/app/demo/page.tsx`

That makes `/demo` look semi-canonical. For governance hardening, that is the wrong abstraction because it encourages proof-by-demo-route instead of proof-by-product-workflow.

#### Existing surfaces to modify

- `scripts/start_approved_project_delivery.py`
- tests that assume `/demo` exists or counts as proof
- possibly conformance/proof helpers if they inspect fixed paths

#### What to replace it with

Keep proof rules centered on:
- `collect_product_proof_paths(...)`
- changed file inventory
- handoff-declared user-visible behavior
- pain-point mapping
- template-marker removal from real product surfaces

#### Better rule

A delivery proves product substance when:
- at least one real approved workflow surface changed beyond `src/lib/app-definition.ts`
- user-facing behavior is described in the handoff
- template-only markers are absent from core product surfaces
- proof paths come from actual changed workflow files, not a hard-coded `/demo` page assumption

#### Truth location

- **Implementation proof truth:** `.hermes/workspace-changes.json` plus actual workspace files
- **Narrative proof truth:** stage handoff markdown
- **Enforced judgment truth:** event `substance` payload and validator result

Do not replace `/demo` with another hard-coded path. Make proof path discovery generic.

## New vs Modified Surfaces

### New surfaces recommended

These are small additive surfaces, not a redesign:

1. Optional stage-evidence validation fields inside event `substance`
2. Optional UI artifact validation helper in `start_approved_project_delivery.py`
3. Optional explicit validator helpers for handoff contract and UI artifact contract

### Modified surfaces required

1. `scripts/start_approved_project_delivery.py`
   - tighten specialist success gating
   - validate UI artifact contents, not just existence
   - stop assuming `/demo` is proof
   - persist richer `substance` truth into events

2. `scripts/validate_delivery_handoff.py`
   - align required headings with the runtime-generated specialist handoff contract
   - require changed files / user-visible behavior / pain-point mapping sections

3. `scripts/validate_approved_delivery_pipeline.py`
   - enforce new specialist evidence gates at the authority-bundle level
   - fail if UI-relevant stages passed without valid UI artifact evidence
   - fail if product proof still depends on template/demo assumptions

4. `scripts/render_approved_delivery_status.py`
   - expose new evidence-gating truth in operator-facing views
   - show UI artifact validation state and handoff contract status where relevant

5. tests
   - `tests/test_approved_delivery_pipeline_cli.py`
   - `tests/test_approved_project_record.py`
   - `tests/test_project_delivery_pipeline_resume.py`
   - `tests/test_project_delivery_pipeline_bootstrap.py`
   - likely handoff-validation tests

## Authority and Truth Boundaries

### Recommended truth map

| Concern | Source of truth | Why |
|--------|------------------|-----|
| latest pipeline stage/status | `APPROVED_PROJECT.json.pipeline` | stable resume surface |
| immutable execution history | `approved-delivery-events.jsonl` | append-only audit truth |
| specialist artifact instances | workspace `.hermes/stage-handoffs/*.md` | stage-local deliverable |
| transcript evidence | workspace `.hermes/<stage>-claude-code.txt` | proof of specialist execution |
| workspace proof inventory | workspace `.hermes/workspace-changes.json` | concrete changed-surface evidence |
| UI design authority artifact | workspace `.hermes/ui-ux-design-system.md` | stage-local design contract evidence |
| platform boundary decision | `platform-justification.json` + governance event log | approval traceability |
| operator-facing summary | rendered `DELIVERY_PIPELINE_STATUS.md` and `FINAL_OPERATOR_REVIEW.md` | derived views only |
| final cross-link correctness | `validate_approved_delivery_pipeline.py` | system-level guardrail |

### Important principle

Rendered markdown files are **derived views**, not primary truth. v1.1.2 should preserve that rule.

## Component Boundaries

| Component | Responsibility | Integrates With |
|-----------|----------------|-----------------|
| `start_approved_project_delivery.py` | orchestrates approved-project lifecycle and persists authority changes | authority record, events, workspace `.hermes/`, governed delivery wrappers |
| `validate_delivery_handoff.py` | defines and validates stage/final handoff contract | stage handoffs, final delivery artifact |
| `validate_approved_delivery_pipeline.py` | validates full approved-project authority bundle coherence | authority record, events, workspace evidence, status/final review |
| `render_approved_delivery_status.py` | renders operator-facing state from authority surfaces | authority record + event stream |
| `check_template_conformance.py` | enforces template/platform invariants | workspace files + metadata |
| `request_platform_justification.py` | resolves protected-surface approval state | classification evidence + governance event log |

## Suggested Build Order

This should ship as narrow, dependency-ordered hardening work.

### Phase 1: Handoff contract alignment

Why first:
- current producer/validator mismatch is foundational
- stricter evidence gating depends on a stable handoff contract

Implement:
- align `build_specialist_handoff_markdown(...)`
- align `validate_delivery_handoff.py`
- update handoff-focused tests

### Phase 2: Specialist evidence gate hardening

Why second:
- once handoff shape is stable, stage pass/fail rules can become strict without ambiguity

Implement:
- require transcript + inventory + non-template substance
- persist richer `substance` fields into events
- update status rendering and pipeline validator

### Phase 3: `/ui-ux-pro-max` artifact validation

Why third:
- builds on stage gating
- naturally plugs into design/development stage validation

Implement:
- validate UI artifact content against `ui_artifact_contract`
- persist pass/fail into event substance
- fail stage if UI project lacks valid artifact coverage

### Phase 4: remove `/demo` proof assumptions

Why fourth:
- easiest to reason about after stronger generic proof gates exist
- prevents swapping one brittle heuristic for another

Implement:
- remove hard dependency on `src/app/demo/page.tsx`
- update proof discovery and tests to rely on actual workflow files and handoff evidence

## Minimal Change Strategy

To avoid broad redesign, keep these constraints:

- no new database
- no new workflow engine
- no replacement of authority record/event stream model
- no replacement of conformance subsystem
- no new operator-facing primary artifact
- no new approval domain beyond existing platform justification flow

This milestone should feel like a **contract-tightening patch set** across the current delivery architecture.

## Concrete Integration Rules

1. `APPROVED_PROJECT.json` declares required contracts and latest state.
2. Workspace `.hermes/` artifacts hold local evidence and handoffs.
3. `approved-delivery-events.jsonl` records immutable stage judgments, including new evidence-gating results.
4. `DELIVERY_PIPELINE_STATUS.md` and `FINAL_OPERATOR_REVIEW.md` remain rendered summaries only.
5. `validate_delivery_handoff.py` owns handoff structure truth.
6. `validate_approved_delivery_pipeline.py` owns cross-surface coherence truth.
7. `/ui-ux-pro-max` validation is enforced only where UI-relevant stages require it.
8. Product proof must come from actual workflow implementation and evidence, not `/demo` route existence.

## Architecture Risks if Done Incorrectly

### Risk 1: Duplicate truth

If UI validation or specialist evidence results are stored only in markdown summaries, the system will drift.

**Prevention:** persist pass/fail into events and pipeline state; render markdown from those.

### Risk 2: Over-redesign

If v1.1.2 introduces a new approval subsystem or new artifact families, it will expand scope unnecessarily.

**Prevention:** extend existing authority/event/validator surfaces only.

### Risk 3: Validator/generator drift again

If handoff templates and validators evolve separately, the pipeline will keep breaking at late stages.

**Prevention:** treat validator-required contract as canonical and update tests around both producer and consumer.

## Bottom Line

The existing approved-project architecture is already suitable for governance hardening. The correct integration is:

- strengthen specialist stage evidence requirements inside the current event-driven pipeline
- validate `/ui-ux-pro-max` artifacts as governed prerequisites for UI stages
- align handoff generation with the validator-owned contract
- remove `/demo` as a proof shortcut and rely on generic product-substance evidence

This keeps truth where it already belongs:
- latest state in `APPROVED_PROJECT.json`
- audit history in `approved-delivery-events.jsonl`
- evidence in workspace `.hermes/`
- operator views as derived renderings
- final coherence in the existing validators

## Sources

- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/PROJECT.md`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/codebase/ARCHITECTURE.md`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/codebase/INTEGRATIONS.md`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_delivery_handoff.py`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_approved_delivery_pipeline.py`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/render_approved_delivery_status.py`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/check_template_conformance.py`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/request_platform_justification.py`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_approved_project_record.py`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_approved_delivery_pipeline_cli.py`
