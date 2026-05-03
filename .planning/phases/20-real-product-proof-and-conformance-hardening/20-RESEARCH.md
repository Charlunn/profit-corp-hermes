# Phase 20: Real Product Proof and Conformance Hardening - Research

**Researched:** 2026-05-04
**Domain:** Approved-project delivery proof, conformance, and authority-surface validation `[VERIFIED: codebase grep]`
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Product proof should be derived from the existing `build_product_proof_summary(...)` seam and persisted as structured evidence, not inferred separately by conformance, status rendering, and final validation with different rules. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
- **D-02:** Acceptable proof must require both a product-facing primary workflow surface under `src/app/**` and supporting logic evidence under `src/lib/**`, `src/app/api/**`, or `supabase/**`; either one alone is insufficient. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
- **D-03:** Identity/bootstrap-only paths such as `src/lib/app-definition.ts` must always be listed as excluded proof, never promoted into product proof even when they changed alongside real work. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
- **D-04:** `/demo` routes must be treated as permanently excluded proof surfaces rather than a privileged shortcut for proving product delivery. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
- **D-05:** Template/example residue on primary workflow surfaces must remain a blocking failure, while residue on secondary surfaces may render as warnings until a later cleanup phase promotes them further. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
- **D-06:** Phase 20 should harden proof classification generically around path classes and residue detection instead of adding another brittle hard-coded allow/deny list beyond the existing contract constants. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
- **D-07:** Template conformance should keep enforcing baseline workspace-level proof prerequisites early: product-facing implementation exists, multilingual evidence exists, and primary surfaces do not still read like the raw template. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
- **D-08:** Approved-delivery final validation should enforce the stronger end-to-end proof contract: rendered status/review must name the exact workflow surfaces, supporting logic, excluded proof paths, residue findings, and proof verdict that justified success or failure. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
- **D-09:** Specialist-stage substance checks, conformance, and final pipeline validation must all consume the same proof vocabulary (`proof_verdict`, `primary_workflow_surfaces`, `supporting_logic_paths`, `excluded_proof_*`, `template_residue_*`, `failure_reasons`) so governance truth does not drift by surface. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
- **D-10:** Operator-facing status and final review must explicitly explain why a run passed or failed product proof, not just show that delivery reached handoff/GitHub/Vercel stages. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
- **D-11:** Proof failure messages should stay reason-coded and human-readable, using the existing failure-reason mapping pattern so operators can see whether the problem was demo-only proof, identity-only changes, missing workflow surfaces, missing supporting logic, or template residue. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
- **D-12:** Phase 20 should preserve the current authority-first model: proof verdicts and explanations are rendered from persisted structured artifacts/events, not re-derived ad hoc from markdown prose. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`

### Claude's Discretion
- Exact expansion of excluded-proof path constants beyond the already-observed `/demo` and identity-only seams `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
- Exact persistence location for any new proof snapshots, as long as status, final review, and validators read the same authoritative fields `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
- Exact wording and ordering of proof sections in handoffs/status markdown, as long as required proof tokens and paths remain explicit and stable `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`

### Deferred Ideas (OUT OF SCOPE)
- Expanding UI artifact coverage rules remains Phase 19 scope, not Phase 20. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
- Bootstrap/resume parity and recovered-state regression closure remain Phase 21 scope, though Phase 20 should preserve resume-safe proof fields. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
- Broader cleanup of secondary template/example residue across non-primary surfaces can be tightened in a future phase once primary-surface blocking is stable. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
- None from matched todos; `gsd-sdk query todo.match-phase 20` returned no relevant pending todos. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| PROOF-01 | Delivery proof must require product-specific workflow surfaces or supporting logic beyond `src/lib/app-definition.ts` and other identity-only bootstrap files `[VERIFIED: .planning/REQUIREMENTS.md]` | Use `build_product_proof_summary(...)` as the sole classifier, keep identity-only paths in `excluded_proof_paths`, and remove legacy fallback paths that can reintroduce identity-only proof into later stages `[VERIFIED: codebase grep]` |
| PROOF-02 | `/demo` routes and template/example residue must not count as acceptable proof of delivered product substance `[VERIFIED: .planning/REQUIREMENTS.md]` | Keep `/demo` excluded in the proof contract, extend conformance to consume the same proof summary, and treat primary-surface residue as blocking while keeping secondary residue as warnings `[VERIFIED: codebase grep]` |
| PROOF-03 | Final delivery validation must explain which workflow surfaces prove the workspace is no longer just a renamed template `[VERIFIED: .planning/REQUIREMENTS.md]` | Persist and render `proof_verdict`, workflow surfaces, supporting logic, excluded proof, residue, and mapped failure reasons across authority events, status, final review, and final validator `[VERIFIED: codebase grep]` |
</phase_requirements>

## Summary

Phase 20 should be planned as a contract-convergence hardening pass, not as a greenfield proof system. The repo already has a strict proof classifier in [scripts/product_proof_contract.py](C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/product_proof_contract.py:7) that excludes `src/lib/app-definition.ts`, excludes `/demo`, requires both primary workflow surfaces and supporting logic, and classifies primary-vs-secondary template residue. `[VERIFIED: codebase grep]`

The real gap is that other surfaces still use weaker or older logic. [scripts/check_template_conformance.py](C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/check_template_conformance.py:315) currently blocks only on “some product-facing page exists under `src/app`”, multilingual evidence exists, and primary marker residue exists; it does not yet require supporting logic or consume the proof-summary vocabulary. `[VERIFIED: codebase grep]` [CITED: docs/platform/standalone-saas-template-contract.md] Several paths in [scripts/start_approved_project_delivery.py](C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py:823) still retain legacy proof-path fallback and stage fixtures that include `/demo` and `src/lib/app-definition.ts` in touched/proof data. `[VERIFIED: codebase grep]`

The planning priority is therefore to route all proof decisions through one persisted structured payload and then remove every legacy escape hatch that can repopulate excluded paths later. The current final validator already checks for product-proof section visibility and exact rendered surfaces/reasons, so Phase 20 can tighten behavior by feeding it better authoritative data rather than inventing a second validator model. `[VERIFIED: codebase grep]`

**Primary recommendation:** Use `build_product_proof_summary(...)` as the only proof classifier, persist its full output once per governed stage/workspace inventory, and make conformance, specialist substance checks, status/final review, and final validation consume that exact payload. `[VERIFIED: codebase grep]`

## Project Constraints (from CLAUDE.md)

- Frontend UI work must invoke `/ui-ux-pro-max` before proposing implementation changes. `[VERIFIED: CLAUDE.md]`
- The skill output is the source of truth for layout, typography, color, spacing, responsiveness, accessibility, and interaction details. `[VERIFIED: CLAUDE.md]`
- If the installed skill is missing, restore it with `uipro init --ai claude` from project root before frontend UI work. `[VERIFIED: CLAUDE.md]`
- This phase is delivery-governance Python/script work, so the frontend-specific rule is not a direct implementation constraint unless Phase 20 expands into UI artifact work, which the context marks as deferred to Phase 19. `[VERIFIED: CLAUDE.md]` `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Product proof classification | API / Backend | Database / Storage | Python governance scripts own the classification logic and persist the result into authority/event artifacts; markdown is derived later. `[VERIFIED: codebase grep]` |
| Early workspace conformance gate | API / Backend | Database / Storage | `check_template_conformance.py` validates generated workspace contents before downstream delivery continues. `[VERIFIED: codebase grep]` |
| Specialist-stage substance enforcement | API / Backend | Database / Storage | `start_approved_project_delivery.py` writes workspace inventories and blocks stages using machine-readable substance checks. `[VERIFIED: codebase grep]` |
| Operator-facing proof visibility | Frontend Server (SSR) | API / Backend | Status/final-review markdown is rendered from authority/events by Python scripts, not by the generated product workspace. `[VERIFIED: codebase grep]` |
| Final cross-artifact validation | API / Backend | — | `validate_approved_delivery_pipeline.py` cross-checks authority, events, status, review, and workspace artifacts. `[VERIFIED: codebase grep]` |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.11.15 | Runtime for all proof/conformance/delivery scripts. `[VERIFIED: local env]` | The Phase 20 surface is already implemented entirely in Python scripts under `scripts/`. `[VERIFIED: codebase grep]` |
| Python stdlib (`argparse`, `json`, `pathlib`, `typing`) | bundled with Python 3.11.15 | CLI parsing, artifact IO, path handling, and payload typing. `[VERIFIED: codebase grep]` `[VERIFIED: local env]` | No external runtime dependency is required for the proof pipeline shown in this phase scope. `[VERIFIED: codebase grep]` |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| pytest | 8.4.2 | Regression coverage for pipeline bootstrap/resume/validator behavior. `[VERIFIED: local env]` | Use for Phase 20 regression cases across proof summary, conformance, and final validation surfaces. `[VERIFIED: tests/test_approved_delivery_pipeline_cli.py]` |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Reusing `build_product_proof_summary(...)` | Add independent logic in conformance/status/validator | This would recreate the exact drift Phase 20 is supposed to remove. `[VERIFIED: codebase grep]` |
| File-backed authority/event artifacts | New database/workflow engine | Explicitly out of scope for this milestone and unnecessary for the current problem. `[VERIFIED: .planning/REQUIREMENTS.md]` `[VERIFIED: .planning/PROJECT.md]` |

**Installation:**
```bash
pip install pytest
```

**Version verification:** `python --version` returned `Python 3.11.15` and `pytest --version` returned `pytest 8.4.2`. `[VERIFIED: local env]`

## Architecture Patterns

### System Architecture Diagram
```text
approved workspace changes
        |
        v
write_workspace_change_inventory()
        |
        v
build_product_proof_summary() -----> classify template residue
        |
        +----> stage substance gate in start_approved_project_delivery.py
        |
        +----> persisted substance on specialist events / workspace inventory
        |
        +----> final handoff summary generation
        |
        +----> render_approved_delivery_status.py
        |
        +----> validate_approved_delivery_pipeline.py
```
`build_product_proof_summary(...)` already sits at the center of the current proof vocabulary and should remain the only classifier. `[VERIFIED: codebase grep]`

### Recommended Project Structure
```text
scripts/
├── product_proof_contract.py          # canonical proof classification
├── check_template_conformance.py      # early workspace gate
├── start_approved_project_delivery.py # stage persistence and blocking
├── render_approved_delivery_status.py # operator-facing derived status
└── validate_approved_delivery_pipeline.py # final cross-artifact validator

tests/
├── test_approved_delivery_pipeline_cli.py
├── test_project_delivery_pipeline_bootstrap.py
└── test_project_delivery_pipeline_resume.py
```
This structure already exists and matches the authority-first pattern locked in prior phases. `[VERIFIED: codebase grep]`

### Pattern 1: Canonical proof summary, many consumers
**What:** One reusable classifier produces a structured proof payload that all gates/renderers consume. `[VERIFIED: codebase grep]`
**When to use:** Every time a stage or validator needs to decide whether the workspace proves real product substance. `[VERIFIED: codebase grep]`
**Example:**
```python
# Source: scripts/product_proof_contract.py
proof_summary = build_product_proof_summary(
    touched_paths=touched_paths,
    workspace=workspace,
    marker_patterns=TEMPLATE_MARKER_PATTERNS,
)
```

### Pattern 2: Authority/event truth, markdown as a view
**What:** Persist the machine-readable proof payload on authority-linked artifacts/events, then render markdown from that truth. `[VERIFIED: .planning/phases/18-handoff-contract-and-authority-alignment/18-CONTEXT.md]` `[VERIFIED: codebase grep]`
**When to use:** Status pages, final review, and resume-safe failure analysis. `[VERIFIED: codebase grep]`

### Anti-Patterns to Avoid
- **Ad hoc proof inference in each surface:** It recreates drift between conformance, stage blocking, status, and final validation. `[VERIFIED: codebase grep]`
- **Legacy fallback proof paths:** `collect_product_proof_paths()` falls back to path-prefix scanning when `product_proof_paths` is empty, which can undermine stricter exclusion rules if left in place. `[VERIFIED: codebase grep]`
- **Fixture-driven loopholes in production logic:** Stage scaffolding in `start_approved_project_delivery.py` still seeds `/demo` and `src/lib/app-definition.ts` into touched-path sets for testing/git/release stages. `[VERIFIED: codebase grep]`

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Separate proof rules per script | Multiple hand-maintained allow/deny lists | `scripts/product_proof_contract.py` | The repo already encodes the proof taxonomy there, including failure-reason mapping and residue classes. `[VERIFIED: codebase grep]` |
| Human-only proof explanations | Markdown prose with no machine-readable source | Persisted proof fields on authority/events/inventory payloads | Phase 18 locked authority-first truth; Phase 20 should extend it, not bypass it. `[VERIFIED: .planning/phases/18-handoff-contract-and-authority-alignment/18-CONTEXT.md]` |
| Regex-only template checks on status/review | Surface-only string scans | Proof summary + final validator visibility checks | The validator already checks both required proof tokens and exact surfaced paths/reasons. `[VERIFIED: codebase grep]` |

**Key insight:** The hard part in this domain is consistency across gates and surfaces, not raw path matching. The existing proof contract is already strict enough; the risk is downstream surfaces silently relaxing it. `[VERIFIED: codebase grep]`

## Common Pitfalls

### Pitfall 1: Weak conformance gate passes a workspace that later fails stronger proof
**What goes wrong:** Conformance currently requires product pages and multilingual evidence, but not supporting logic evidence tied to the same proof contract. `[VERIFIED: codebase grep]`
**Why it happens:** `require_shared_invariants()` scans for any `src/app/**/page.tsx` and template residue, not for the full Phase 20 vocabulary. `[VERIFIED: codebase grep]`
**How to avoid:** Make conformance call the same proof classifier and fail on `missing_primary_workflow_surface`, `missing_supporting_logic`, `demo_only_proof`, and primary-surface residue. `[VERIFIED: codebase grep]`
**Warning signs:** A workspace passes conformance even though its only substantive work is a page shell, `/demo`, or identity/bootstrap edits. `[VERIFIED: codebase grep]`

### Pitfall 2: Legacy proof fallback reintroduces excluded paths
**What goes wrong:** Excluded paths disappear in the canonical proof summary but return through fallback or mocked inventories later. `[VERIFIED: codebase grep]`
**Why it happens:** `collect_product_proof_paths()` still has a legacy fallback, and multiple stage/test fixtures write `product_proof_paths` containing `/demo` and `src/lib/app-definition.ts`. `[VERIFIED: codebase grep]`
**How to avoid:** Remove or narrow fallback behavior and update all fixtures/helpers so only the canonical summary can define proof paths. `[VERIFIED: codebase grep]`
**Warning signs:** `product_proof_paths` includes `src/app/demo/page.tsx` or `src/lib/app-definition.ts` anywhere after inventory generation. `[VERIFIED: codebase grep]`

### Pitfall 3: Final review/status show tokens but not decisive evidence
**What goes wrong:** Operator surfaces can mention “Product Proof” but still fail to explain exactly which paths/reasons caused pass or fail. `[VERIFIED: codebase grep]`
**Why it happens:** Visibility checks are token-based first, then path/reason-based only if substance exists; incomplete persistence upstream weakens the rendered explanation. `[VERIFIED: codebase grep]`
**How to avoid:** Persist the full proof payload on every relevant event and make renderers consume it directly. `[VERIFIED: codebase grep]`
**Warning signs:** Status/review shows a verdict without naming supporting logic, excluded proof reasons, or template residue. `[VERIFIED: codebase grep]`

## Code Examples

Verified patterns from official repo sources:

### Canonical proof contract
```python
# Source: scripts/product_proof_contract.py
return {
    "proof_verdict": "pass" if not failure_reasons else "fail",
    "template_only": bool(failure_reasons),
    "touched_paths": normalized_paths,
    "product_proof_paths": proof_paths,
    "primary_workflow_surfaces": primary_surfaces,
    "supporting_logic_paths": supporting_logic_paths,
    "excluded_proof_paths": excluded_proof_paths,
    "excluded_proof_reasons": excluded_proof_reasons,
    "template_residue_blockers": primary_residue_paths,
    "template_residue_warnings": secondary_residue_paths,
    "failure_reasons": failure_reasons,
}
```

### Final validator proof visibility contract
```python
# Source: scripts/validate_approved_delivery_pipeline.py
for token in (
    "product proof",
    "primary workflow surfaces",
    "supporting logic evidence",
    "excluded proof",
    "proof verdict",
):
    ...
for path in latest_substance.get("primary_workflow_surfaces", []):
    ...
for path in latest_substance.get("supporting_logic_paths", []):
    ...
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Identity/bootstrap edits could still appear in proof-oriented fixtures and legacy path lists | Canonical proof contract explicitly excludes identity-only paths from proof and lists them under `excluded_proof_paths` | Present in current `product_proof_contract.py` as of 2026-05-04 repo state `[VERIFIED: codebase grep]` | Phase 20 should finish propagating that stricter model to every consumer. `[VERIFIED: codebase grep]` |
| `/demo` acted as a materialized proof surface in stage scaffolding | Canonical proof contract now marks `/demo` as excluded proof and emits `demo_only_proof` failures | Present in current `product_proof_contract.py` and stage context as of 2026-05-04 `[VERIFIED: codebase grep]` | Remaining planning work is to remove `/demo` from all remaining stage/test shortcuts. `[VERIFIED: codebase grep]` |

**Deprecated/outdated:**
- Legacy “proof paths by path-prefix fallback” behavior in `collect_product_proof_paths()` is outdated for Phase 20 because it can drift from the canonical classifier. `[VERIFIED: codebase grep]`
- Stage fixture payloads that hardcode `/demo` and `src/lib/app-definition.ts` inside `product_proof_paths` are outdated for Phase 20’s stricter contract. `[VERIFIED: codebase grep]`

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | No additional external packages beyond Python stdlib and pytest are needed to implement Phase 20. `[ASSUMED]` | Standard Stack | Low; if wrong, the planner would miss an install/test step. |

## Open Questions

1. **Should conformance persist the full proof summary artifact or only consume it transiently?**
   - What we know: Phase 20 allows discretion on persistence location as long as all surfaces read the same authoritative fields. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
   - What's unclear: Whether the planner should add a dedicated proof snapshot file or rely only on workspace inventory/event substance. `[VERIFIED: codebase grep]`
   - Recommendation: Prefer one durable JSON artifact under `.hermes/` plus event copies/references so Phase 21 resume work inherits a stable proof source. `[ASSUMED]`

2. **Should `src/app/page.tsx` remain excluded as a primary proof surface?**
   - What we know: `PRIMARY_SURFACE_EXCLUDED_PATHS` currently excludes `src/app/page.tsx`. `[VERIFIED: codebase grep]`
   - What's unclear: The context locks `/demo` and identity-only exclusions, but it leaves exact expansion of excluded-proof constants to discretion. `[VERIFIED: .planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md]`
   - Recommendation: Revisit this constant explicitly during planning and keep it only if the root page is always branding/marketing shell in this template. `[ASSUMED]`

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | delivery scripts and validators | ✓ `[VERIFIED: local env]` | 3.11.15 `[VERIFIED: local env]` | — |
| pytest | regression verification | ✓ `[VERIFIED: local env]` | 8.4.2 `[VERIFIED: local env]` | `python -m unittest` for some suites, but pytest is the current direct path. `[VERIFIED: local env]` `[VERIFIED: tests]` |
| `rg` | fast code search during development | Partially unusable `[VERIFIED: local env]` | installed but `Access is denied` on execution `[VERIFIED: local env]` | Use PowerShell `Select-String` / `Get-ChildItem` during this phase. `[VERIFIED: local env]` |

**Missing dependencies with no fallback:**
- None identified for planning/research. `[VERIFIED: local env]`

**Missing dependencies with fallback:**
- `rg` execution is blocked in this environment, but PowerShell-native search is sufficient for this phase. `[VERIFIED: local env]`

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest 8.4.2` `[VERIFIED: local env]` |
| Config file | none detected in requested phase scope `[VERIFIED: codebase grep]` |
| Quick run command | `pytest tests/test_approved_delivery_pipeline_cli.py -q` `[VERIFIED: tests]` |
| Full suite command | `pytest tests/test_approved_delivery_pipeline_cli.py tests/test_project_delivery_pipeline_bootstrap.py tests/test_project_delivery_pipeline_resume.py -q` `[VERIFIED: local test run]` |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| PROOF-01 | identity-only changes and missing supporting logic fail product proof | unit/integration | `pytest tests/test_project_delivery_pipeline_bootstrap.py -q` | ✅ `[VERIFIED: tests]` |
| PROOF-02 | `/demo` and template residue do not count as acceptable proof | unit/integration | `pytest tests/test_project_delivery_pipeline_bootstrap.py tests/test_project_delivery_pipeline_resume.py -q` | ✅ `[VERIFIED: tests]` |
| PROOF-03 | final status/review/validator explain exact proof surfaces and reasons | integration | `pytest tests/test_approved_delivery_pipeline_cli.py -q` | ✅ `[VERIFIED: tests]` |

### Sampling Rate
- **Per task commit:** `pytest tests/test_approved_delivery_pipeline_cli.py -q` `[VERIFIED: tests]`
- **Per wave merge:** `pytest tests/test_project_delivery_pipeline_bootstrap.py tests/test_project_delivery_pipeline_resume.py -q` `[VERIFIED: tests]`
- **Phase gate:** `pytest tests/test_approved_delivery_pipeline_cli.py tests/test_project_delivery_pipeline_bootstrap.py tests/test_project_delivery_pipeline_resume.py -q` `[VERIFIED: local test run]`

### Wave 0 Gaps
- Existing tests are present, but many fixtures still encode pre-Phase-20 loopholes by hardcoding `/demo` and `src/lib/app-definition.ts` inside `product_proof_paths`. `[VERIFIED: codebase grep]`
- The current baseline full phase suite is red: 7 failures, 18 passes on 2026-05-04. `[VERIFIED: local test run]`
- Several current failures are Phase 19/UI-artifact related (`ui_ux_artifact_stale`), so the planner should isolate Phase 20 assertions carefully instead of assuming a clean baseline. `[VERIFIED: local test run]`

## Security Domain

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | no `[VERIFIED: codebase grep]` | Existing auth paths are not the focus of this phase. `[VERIFIED: .planning/REQUIREMENTS.md]` |
| V3 Session Management | no `[VERIFIED: codebase grep]` | Existing session behavior is outside Phase 20 scope. `[VERIFIED: .planning/REQUIREMENTS.md]` |
| V4 Access Control | no `[VERIFIED: codebase grep]` | Phase 20 is governance/proof validation, not authz logic changes. `[VERIFIED: .planning/REQUIREMENTS.md]` |
| V5 Input Validation | yes `[VERIFIED: codebase grep]` | Validate authority/event/inventory payload fields before trusting proof output. `[VERIFIED: codebase grep]` |
| V6 Cryptography | no `[VERIFIED: codebase grep]` | No new crypto requirement identified for this phase. `[VERIFIED: codebase grep]` |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Proof spoofing via excluded-path fallback | Tampering | Only trust canonical proof summary and fail if excluded paths appear in downstream proof fields. `[VERIFIED: codebase grep]` |
| Authority/render drift hides proof failure | Repudiation | Keep authority/event artifacts canonical and make validator enforce rendered proof visibility. `[VERIFIED: codebase grep]` |
| Template residue passes as real product | Spoofing | Block on primary-surface residue and surface secondary residue as warnings. `[VERIFIED: codebase grep]` |

## Sources

### Primary (HIGH confidence)
- `scripts/product_proof_contract.py` - checked canonical proof taxonomy, exclusions, residue classes, and failure reasons. `[VERIFIED: codebase grep]`
- `scripts/check_template_conformance.py` - checked current early-gate behavior and residue/language enforcement. `[VERIFIED: codebase grep]`
- `scripts/start_approved_project_delivery.py` - checked proof persistence, stage substance checks, legacy fallback, and final summary rendering. `[VERIFIED: codebase grep]`
- `scripts/render_approved_delivery_status.py` - checked operator-facing product-proof rendering contract. `[VERIFIED: codebase grep]`
- `scripts/validate_approved_delivery_pipeline.py` - checked final proof visibility requirements and current-state precedence enforcement. `[VERIFIED: codebase grep]`
- `.planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md` - checked locked decisions and scope. `[VERIFIED: file read]`
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`, `.planning/PROJECT.md` - checked milestone framing and requirement text. `[VERIFIED: file read]`

### Secondary (MEDIUM confidence)
- `docs/platform/standalone-saas-template-contract.md` - used for template conformance intent and workspace proof prerequisites. `[CITED: docs/platform/standalone-saas-template-contract.md]`
- `docs/OPERATIONS.md` - used for operator command flow and validation expectations. `[CITED: docs/OPERATIONS.md]`
- `docs/skill-governance/templates/stage-handoff-template-v0.2.md` and `.planning/phases/18-handoff-contract-and-authority-alignment/18-CONTEXT.md` - used for authority-first and handoff-contract carry-forward constraints. `[CITED: docs/skill-governance/templates/stage-handoff-template-v0.2.md]` `[VERIFIED: file read]`

### Tertiary (LOW confidence)
- None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - the phase is already implemented on Python stdlib plus pytest in the current repo and local environment. `[VERIFIED: codebase grep]` `[VERIFIED: local env]`
- Architecture: HIGH - the authority/event/derived-markdown layering and proof-contract seam are explicit in current code and Phase 18/20 context. `[VERIFIED: codebase grep]` `[VERIFIED: .planning/phases/18-handoff-contract-and-authority-alignment/18-CONTEXT.md]`
- Pitfalls: MEDIUM - the main pitfalls are directly visible in code and tests, but some baseline failures are Phase 19/UI-artifact related and can obscure clean Phase 20 isolation. `[VERIFIED: codebase grep]` `[VERIFIED: local test run]`

**Research date:** 2026-05-04
**Valid until:** 2026-06-03 for internal code-structure findings; rerun sooner if Phase 19 lands first and changes shared delivery gates. `[VERIFIED: .planning/STATE.md]` `[ASSUMED]`
