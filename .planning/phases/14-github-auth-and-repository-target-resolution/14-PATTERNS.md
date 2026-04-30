# Phase 14: GitHub Auth and Repository Target Resolution - Patterns

## Core implementation patterns to follow

### 1. Blocked-result helper pattern
The existing delivery helpers return a uniform blocked payload instead of raising for expected operator/runtime failures.

Reference pattern:
- `scripts/github_delivery_common.py::_blocked()`
- `scripts/vercel_delivery_common.py::_blocked()`

Shape to preserve:
- `ok: False`
- `block_reason`
- `error`
- `evidence_path`
- optional `stderr_summary` / contextual fields

Phase 14 changes should keep this exact contract. Do not introduce ad-hoc exceptions for expected auth/owner-resolution failures when a blocked result is the established operator-facing pattern.

### 2. Authority-first metadata update pattern
The controller owns approved-project shipping metadata. Helpers validate/execute one stage; controller persists canonical state.

Reference points:
- `scripts/start_approved_project_delivery.py:1137-1154`
- `scripts/start_approved_project_delivery.py:1156-1205`
- `scripts/start_approved_project_delivery.py:update_pipeline_state(...)`
- `scripts/start_approved_project_delivery.py:append_next_pipeline_event(...)`

Pattern:
1. Resolve metadata in controller
2. Call helper with explicit inputs
3. On failure, call `block_pipeline(...)`
4. On success, reload record, append event, update `shipping.github`, move `resume_from_stage`

For Phase 14, repo owner/name/url derivation belongs in the controller layer, not buried inside the low-level GitHub helper.

### 3. Thin helper / explicit input pattern
`prepare_github_repository()` assumes caller already resolved a correct owner/name/url tuple.

Reference:
- `scripts/github_delivery_common.py:167-278`

This helper is a thin executor/validator layer. It should stay that way. Do not overload it with broad milestone logic. Small additions like auth-source detection are acceptable if they remain helper-scoped, but project-specific fallback policy should live in `start_approved_project_delivery.py`.

### 4. Local CLI / subprocess pattern
Current subprocess pattern is simple and synchronous.

Reference:
- `scripts/github_delivery_common.py::_run_command()`
- `scripts/vercel_delivery_common.py::_run_command()`

Pattern characteristics:
- `subprocess.run(...)`
- `capture_output=True`
- `text=True`
- helper-specific env injection when needed
- stderr summarized through `_safe_summary(...)`

Phase 14 auth detection should reuse this model if it probes `gh auth status`, `gh auth token`, or `gh api user`. Do not introduce a different process abstraction just for GitHub auth.

### 5. Live-state over fallback pattern
The bug came from weak fallback defaults in controller code.

Problematic references:
- `scripts/start_approved_project_delivery.py:1141-1146`
- `scripts/start_approved_project_delivery.py:1159-1164`

Current anti-pattern:
- owner falls back to `project_slug`

Preferred Phase 14 pattern:
- explicit operator override
- existing authority metadata if already known
- authenticated operator identity from CLI state
- repo-name fallback may use `project_slug`
- owner fallback must never use `project_slug`

This is the most important pattern correction for this phase.

## Test patterns to follow

### 1. Helper-focused unit tests
Best existing analog:
- `tests/test_phase11_github_sync.py`

This file already covers:
- create vs attach flows
- missing CLI vs missing auth blocked reasons
- shell env token acceptance
- sync behavior contracts

Phase 14 should extend this file or add a nearby focused helper test if needed. Likely additions:
- authenticated `gh` CLI session accepted without env token
- explicit env token still wins
- owner/name resolution regression cases

### 2. Controller / authority-flow tests
Best existing analogs:
- `tests/test_project_delivery_pipeline_bootstrap.py`
- `tests/test_project_delivery_pipeline_resume.py`

These are the right place for:
- first-run owner/name/url derivation
- resume behavior preserving existing GitHub metadata
- blocked-state transitions and `resume_from_stage`
- authority record convergence after repository-preparation success/failure

### 3. Status/render regression checks
If Phase 14 changes authority metadata shape or blocked reasons that must appear in operator surfaces, existing status-oriented tests should be touched only where those fields are rendered or asserted.

Reference usages from grep:
- `tests/test_project_delivery_pipeline_bootstrap.py` already checks blocked reasons inside rendered status content

## Files that best fit current structure

### Most likely implementation files
- `scripts/github_delivery_common.py`
  - GitHub auth source resolution
  - helper-side evidence payload updates
- `scripts/start_approved_project_delivery.py`
  - repository owner/name/url derivation
  - controller-side metadata persistence
  - first-run and resume consistency

### Most likely test files
- `tests/test_phase11_github_sync.py`
- `tests/test_project_delivery_pipeline_bootstrap.py`
- `tests/test_project_delivery_pipeline_resume.py`

### Validation-only artifacts
Use as regression evidence targets, not implementation targets:
- `assets/shared/approved-projects/lead-capture-copilot/APPROVED_PROJECT.json`
- `assets/shared/approved-projects/lead-capture-copilot/DELIVERY_PIPELINE_STATUS.md`
- workspace `.hermes/github-repository-prepare.json`

## Things that would violate current patterns

- Moving all owner/name/auth logic into `github_delivery_common.py` and making the controller passive
- Introducing a totally separate GitHub auth/config module when the repo already uses script-local helpers
- Returning mixed shapes for auth failures instead of the standard blocked payload
- Solving owner fallback by hardcoding one operator username in source
- Using project slug as owner fallback again, even indirectly
- Writing tests only against the live approved-project fixture and not the isolated helper/controller test suites

## Recommended mapping for Phase 14 planning

- Controller resolves canonical GitHub identity, helper validates and executes
- Helper accepts both env-token auth and healthy `gh` CLI auth as valid sources
- Authority record persists resolved owner/name/url and optionally auth-source evidence
- Fresh-run and resume-run behavior get separate test coverage
- `tests/test_phase11_github_sync.py` is the primary helper regression anchor
- pipeline bootstrap/resume tests are the primary authority-state regression anchors
