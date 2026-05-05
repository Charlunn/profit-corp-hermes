# Technology Stack Additions for Milestone v1.1.2

**Project:** Profit-Corp Hermes
**Focus:** Brownfield hardening for approved-project delivery governance
**Researched:** 2026-05-03
**Confidence:** HIGH

## Recommendation Summary

Do not add a new platform layer, workflow engine, database, or browser E2E stack for this milestone. The repo already has the right backbone: Python orchestration scripts, JSON/Markdown contract artifacts, Bash wrappers, and `unittest`-based regression coverage.

For v1.1.2, the right move is to harden the existing contract-driven pipeline with stricter schema validation, stronger artifact-evidence checks, explicit negative-path fixtures, and deterministic content classifiers. This milestone is about governance integrity inside the current delivery system, not about expanding infrastructure.

## Recommended Additions

### Core Implementation Approach

| Addition | Technology | Purpose | Why it fits this repo |
|----------|------------|---------|------------------------|
| Typed contract normalization | Existing Python stdlib + current JSON artifact pattern | Centralize parsing/validation of `APPROVED_PROJECT.json`, workspace `.hermes/*.json`, handoff metadata, and specialist evidence | The repo already uses Python for delivery orchestration and JSON as authority state; this improves reliability without introducing a new runtime |
| Optional strict schema layer | `pydantic` 2.x, only if current hand-rolled validation becomes too duplicated | Validate authority records, stage handoff metadata, UI artifact contracts, and workspace change inventory | Good fit only if several scripts are repeating the same dict-shape validation. Otherwise stay with stdlib to keep surface area small |
| Contract assertion helpers | `unittest` + shared Python test helpers | Reuse the same assertions across bootstrap/resume/validator tests | Repo already has strong `unittest` coverage in delivery tests; shared helpers reduce drift |
| Fixture builders for delivery states | Existing `tempfile`, `pathlib`, `json`, `unittest.mock` | Create reproducible authority/workspace/event fixtures for bootstrap and resume regressions | This is already the dominant testing style in `tests/test_project_delivery_pipeline_bootstrap.py` and `tests/test_project_delivery_pipeline_resume.py` |
| Deterministic artifact classifiers | Python stdlib (`re`, `json`, `pathlib`) | Detect forbidden `/demo` proof, identity-only product proof, missing specialist evidence, and missing `/ui-ux-pro-max` references | Better than adding AI-based validation for this milestone; governance checks should be auditable and stable |
| Golden content checks for handoff contracts | Existing markdown template tests | Ensure stage/final handoff templates stay aligned with required headings, metadata fields, and evidence semantics | The repo already has this pattern in `tests/test_delivery_handoff_contract.py` |

## Feature-by-Feature Stack Guidance

### 1. Stricter specialist evidence gating

**Use:** existing Python orchestration + JSON evidence artifacts + `unittest` contract tests.

#### Implementation techniques
- Introduce a single evidence-gating function in the delivery pipeline that evaluates each specialist stage against a stage-specific evidence contract before allowing progression.
- Treat the following as first-class required evidence, not optional metadata:
  - specialist transcript path
  - required skill list used for the stage
  - stage handoff artifact path
  - workspace change inventory path
  - stage-specific proof fields such as touched paths, product proof paths, and gate decision
- Make stage gating fail closed. If evidence is absent, malformed, or points to missing files, persist a block reason and stop the pipeline.
- Add per-stage required field maps rather than one generic “ok” boolean. Example: `design` requires UI artifact evidence; `development` requires product-proof evidence; `testing` requires verification evidence.
- Normalize all evidence into machine-checked JSON alongside markdown summaries so the validator does not need to scrape prose.

#### Repo-fit rationale
This repo already persists evidence paths and block reasons in authority and status artifacts. Tightening those checks is a natural extension of the current file-as-contract model.

#### Specific techniques to add
- Shared `validate_stage_evidence(stage, record, workspace)` helper.
- Shared `require_existing_file(path, block_reason)` helper.
- Shared `assert_stage_handoff_contract(content)` helper for tests.
- New negative tests for:
  - transcript path missing
  - handoff artifact missing
  - skills list missing when required
  - workspace change inventory missing or incomplete
  - evidence path points outside workspace/authority scope when that should be disallowed

### 2. Mandatory `/ui-ux-pro-max` artifact validation

**Use:** deterministic Python validation, not a new frontend toolchain.

The repo already encodes `/ui-ux-pro-max` as a requirement in `CLAUDE.md`, and the template contract already expects a `/ui-ux-pro-max` UI artifact contract in `.hermes/project-metadata.json`.

#### Implementation techniques
- Require the design stage to emit a concrete artifact such as `.hermes/ui-ux-design-system.md`.
- Validate all of the following before design can pass and before development can start:
  - artifact file exists
  - artifact is non-empty
  - artifact metadata ties back to the current `run_id`, stage, and workspace
  - artifact contract in `.hermes/project-metadata.json` is present and populated
  - dispatched skill list contains `ui-ux-pro-max` for design and any frontend-affecting development stage
- Cross-check artifact contents for minimum required sections instead of only checking file existence. For this repo, minimum sections should match current governance needs: screen inventory, conversion flow, monetization surface, responsive rules, accessibility rules, multilingual coverage.
- Store a small JSON verification report, e.g. `.hermes/ui-ux-artifact-validation.json`, that records pass/fail and missing sections.

#### Repo-fit rationale
This preserves the existing artifact-first governance style. It also avoids fragile dependence on raw chat transcripts as the only proof that the UI skill ran.

#### Testing techniques
- Add validator tests that fail when:
  - the design system artifact is missing
  - `ui-ux-pro-max` is absent from the recorded skill list
  - the artifact exists but lacks required sections
  - development resumes without an accepted UI artifact

### 3. Handoff contract alignment

**Use:** expand current markdown-template contract tests and add structured metadata checks.

The repo already tests handoff templates in `tests/test_delivery_handoff_contract.py`. Build on that instead of introducing a doc-generation library.

#### Implementation techniques
- Keep markdown as the human-facing handoff format, but pair it with normalized JSON metadata for machine validation.
- Add a required metadata block for every stage handoff with at least:
  - `run_id`
  - `role`
  - `stage`
  - `scope_status`
  - `gate_decision`
  - `evidence_paths`
  - `next_stage`
- Add contract-alignment checks between:
  - stage handoff markdown
  - workspace change inventory JSON
  - authority record pipeline state
  - final delivery summary
- Detect drift where a handoff says PASS but the inventory or validator says evidence is missing.
- Prefer exact heading/order assertions and required-field assertions over fuzzy text matching.

#### Repo-fit rationale
This repo already uses Markdown as an operator artifact and JSON for state. Dual-format validation gives both auditability and deterministic checks without changing the operating model.

### 4. Removal of `/demo` and identity-only product-proof assumptions

**Use:** deterministic product-surface classification inside Python validators.

Current tests clearly still treat `src/app/demo/page.tsx` as valid product proof in bootstrap/resume fixtures. That assumption should be removed.

#### Implementation techniques
- Change product-proof rules so `/demo` routes never count toward required product evidence.
- Add an explicit denylist for proof-only paths such as:
  - `src/app/demo/**`
  - purely identity/config files like `src/lib/app-definition.ts`
  - template marker pages that only restate app name, auth, or payments setup
- Require proof from at least one approved user-facing workflow surface tied to the approved scope, for example:
  - primary landing/conversion page
  - core task workflow page
  - meaningful API route or supporting business logic used by that workflow
- Split proof into categories instead of one flat list:
  - `identity_paths`
  - `demo_paths`
  - `workflow_paths`
  - `supporting_logic_paths`
- Fail conformance and delivery validation if all proof falls into identity-only or demo-only buckets.
- Add template-marker scanning to reject unchanged starter copy on primary surfaces.

#### Repo-fit rationale
This directly addresses the repo’s stated goal of shipping real SaaS products, not template-shaped placeholders. It also builds on existing conformance checks that already reject raw template markers.

#### Testing techniques
- Update bootstrap/resume fixtures so they no longer rely on `src/app/demo/page.tsx` as acceptable proof.
- Add regression fixtures for:
  - only `app-definition.ts` changed
  - landing page renamed but still template text
  - `/demo` page present with no real workflow page
  - real workflow page present plus supporting logic path present

### 5. Stronger bootstrap/resume regression fixtures

**Use:** existing `unittest`, `tempfile`, `unittest.mock`, fixture-builder helpers.

#### Implementation techniques
- Extract reusable fixture factories from current long-form tests in:
  - `tests/test_project_delivery_pipeline_bootstrap.py`
  - `tests/test_project_delivery_pipeline_resume.py`
  - `tests/test_approved_delivery_pipeline_cli.py`
- Model fixtures by pipeline state, not by one giant happy-path setup. Example states:
  - authority ready / workspace absent
  - workspace present / metadata incomplete
  - design complete / UI artifact invalid
  - development complete / proof invalid
  - downstream credentials blocked / evidence linked
  - handoff completed / final review missing
- Add replayable JSONL event fixtures to prove resume behavior honors persisted state transitions.
- Add invariant tests that the same authority record either:
  - resumes safely from the persisted stage, or
  - fails with a precise block reason and evidence path.
- Add cross-file consistency assertions between:
  - `APPROVED_PROJECT.json`
  - `approved-delivery-events.jsonl`
  - `DELIVERY_PIPELINE_STATUS.md`
  - `.hermes/delivery-run-manifest.json`
  - `.hermes/FINAL_DELIVERY.md`

#### Repo-fit rationale
The repo already uses temp directories and mocked orchestration edges very effectively. Strengthening fixture structure gives better regression protection without adding slow external integration infrastructure.

## Recommended Python Patterns

### Keep using
| Pattern | Why |
|--------|-----|
| `unittest` + `unittest.mock` | Already the repo standard for delivery pipeline tests |
| `tempfile.TemporaryDirectory()` / temp roots | Best fit for authority/workspace fixture isolation |
| `pathlib.Path` | Already dominant in tests and scripts |
| JSONL event fixtures | Matches real pipeline event storage |
| Small pure helper functions for validation | Easier to regression test than embedding logic in command handlers |

### Add now
| Pattern | Purpose |
|--------|---------|
| Shared fixture builders | Reduce duplication across bootstrap/resume/CLI validator tests |
| Shared assertion mixins/helpers | Keep contract rules consistent across tests |
| Table-driven negative tests with `subTest()` | Efficient way to cover many gating failures |
| Machine-readable validation reports beside markdown artifacts | Lets validator and resume logic consume the same truth |

## Recommended Contract Techniques

| Technique | Apply To | Why |
|----------|----------|-----|
| Fail-closed required-field maps | `APPROVED_PROJECT.json`, stage evidence JSON, workspace change inventory | Governance should block on missing evidence, not infer success |
| Dual human/machine artifact design | Markdown summary + JSON metadata | Best fit for operator visibility plus deterministic validation |
| Stage-specific block reasons | Pipeline and validator output | Makes resume and operator triage precise |
| Exact heading/order assertions | Handoff templates | Prevents silent contract drift |
| Path classification rules | Product proof validation | Removes `/demo` and identity-only loopholes |

## Minimal Dependency Recommendation

### Recommended baseline
Do this milestone with the existing stack first:
- Python stdlib
- current repo scripts
- current `unittest` suite
- existing Markdown/JSON artifact model

### Optional addition only if duplication grows
| Library | Version | Purpose | When justified |
|---------|---------|---------|----------------|
| `pydantic` | 2.x | Central schema validation for authority records and stage evidence | Add only if validation logic becomes repetitive across multiple scripts and tests |

## What NOT to Add

| Avoid | Why not | Use instead |
|------|---------|-------------|
| New workflow/orchestration framework | This milestone is governance hardening inside an already working Hermes pipeline | Extend current Python orchestration scripts |
| Browser E2E stack like Playwright/Cypress for this milestone | Too heavy for the problem; these features are contract and governance checks, not frontend interaction regressions | Strengthen file-contract and pipeline-state tests first |
| New database for delivery state | Delivery authority already lives in JSON/JSONL artifacts; moving it now adds migration risk | Keep file-backed authority and harden validators |
| LLM-based artifact grading | Non-deterministic and hard to audit for gates that must block deployment | Use explicit required sections and path/content classifiers |
| Markdown parser dependency for simple heading checks | Overkill given current templates and existing tests | Use exact string/order assertions in Python |
| Re-researching GitHub/Vercel/shared-Supabase stack | Explicitly out of scope for this milestone | Limit changes to delivery governance and regression coverage |
| Treating `/demo` or app identity files as product proof | Conflicts with real-SaaS evidence goals | Require workflow-specific user-facing and supporting logic proof |

## Brownfield Change Plan

1. Extract shared validation helpers from `scripts/start_approved_project_delivery.py` and related validator scripts.
2. Tighten stage evidence contracts, especially for design/development/testing.
3. Introduce `/ui-ux-pro-max` artifact verification report generation and checks.
4. Update product-proof classification to exclude `/demo` and identity-only evidence.
5. Refactor tests around reusable fixtures and add negative-path resume/bootstrap cases.
6. Keep all new checks visible through persisted block reasons and evidence paths.

## Concrete Files Likely to Change

| File | Why |
|------|-----|
| `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py` | Main pipeline gating, specialist dispatch validation, product-proof rules |
| `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_approved_delivery_pipeline.py` | Cross-artifact validation and fail-closed checks |
| `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/render_approved_delivery_status.py` | Surface new block reasons and artifact-validation evidence |
| `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_project_delivery_pipeline_bootstrap.py` | Remove `/demo` assumptions and add stronger bootstrap fixtures |
| `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_project_delivery_pipeline_resume.py` | Resume-state regressions for evidence gating and UI artifact validity |
| `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_approved_delivery_pipeline_cli.py` | Validator failures for missing artifact/evidence links |
| `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_delivery_handoff_contract.py` | Expanded handoff contract alignment assertions |
| `C:/Users/42236/Desktop/dev/profit-corp-hermes/docs/platform/standalone-saas-template-contract.md` | Clarify `/demo` exclusion and real workflow proof expectations if not already explicit |

## Sources

- Internal project brief: `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/PROJECT.md`
- Existing stack baseline: `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/codebase/STACK.md`
- Existing testing baseline: `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/codebase/TESTING.md`
- Template contract: `C:/Users/42236/Desktop/dev/profit-corp-hermes/docs/platform/standalone-saas-template-contract.md`
- Handoff contract tests: `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_delivery_handoff_contract.py`
- Bootstrap regressions: `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_project_delivery_pipeline_bootstrap.py`
- Resume regressions: `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_project_delivery_pipeline_resume.py`
- CLI validation regressions: `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_approved_delivery_pipeline_cli.py`
- Operator pipeline validation flow: `C:/Users/42236/Desktop/dev/profit-corp-hermes/docs/OPERATIONS.md`
