# Phase 14: GitHub Auth and Repository Target Resolution - Research

**Researched:** 2026-04-29
**Domain:** GitHub credential source resolution, approved-project repository targeting, and authority metadata defaults
**Confidence:** HIGH

## Summary

Phase 14 should repair the *entry contract* to the GitHub shipping path, not the whole sync/deploy pipeline. The live instance test proved two upstream failures before any meaningful repository work could happen: GitHub auth detection rejected a machine where `gh auth status` was healthy, and repository owner defaults fell back to `project_slug`, producing `lead-capture-copilot/lead-capture-copilot` instead of an operator-owned repo. These two defects sit at the boundary between operator machine state, approved-project authority metadata, and the GitHub helper layer.

The current auth behavior is defined in `scripts/github_delivery_common.py`. `_has_github_auth()` only returns true when `GH_TOKEN` or `GITHUB_TOKEN` exist in process env, and `_require_gh()` blocks immediately with `missing_github_auth` if neither env var is set (`scripts/github_delivery_common.py:126-153`). The helper never inspects `gh auth status`, `gh auth token`, or any other authenticated CLI state. In the live test, `gh auth status` was healthy but the pipeline still blocked until token env vars were manually injected into the exact shell command.

The current owner/repo targeting bug is defined in `scripts/start_approved_project_delivery.py:1141-1164`. During post-bootstrap GitHub metadata population, `github_owner` defaults to `APPROVED_DELIVERY_GITHUB_OWNER` and then falls back to `project_slug`; `github_repo` falls back similarly. For a new project with no env overrides, that produces an invalid owner such as `lead-capture-copilot`. The live evidence captured that exact failure in `.hermes/github-repository-prepare.json` with `HTTP 404: Not Found (https://api.github.com/users/lead-capture-copilot)`.

## Current Behavior Map

### Auth source resolution
- `scripts/github_delivery_common.py:126-130` — `_has_github_auth()` checks only `GH_TOKEN` / `GITHUB_TOKEN`
- `scripts/github_delivery_common.py:138-153` — `_require_gh()` requires `gh` binary plus env-token auth and emits `missing_gh_cli` or `missing_github_auth`
- Implication: local CLI login is ignored even when `gh auth status` is valid

### Repository targeting
- `scripts/start_approved_project_delivery.py:1141-1147` — first-time GitHub metadata defaults owner/repo from env, then `project_slug`
- `scripts/start_approved_project_delivery.py:1159-1164` — resume path repeats the same fallback logic
- `scripts/github_delivery_common.py:192-278` — `prepare_github_repository()` expects validated `repository_owner`, `repository_name`, and URL but assumes caller already resolved the right identity

### Create vs attach split
- `prepare_github_repository()` already supports `repository_mode in {create, attach}` and keeps the branching isolated in one helper (`scripts/github_delivery_common.py:167-245`)
- This means Phase 14 should not redesign the helper split. It should instead make upstream metadata resolution deterministic so both modes receive sane owner/name/url inputs

## Recommended Target Behavior

1. **Auth resolution should be layered**
   - First accept explicit `GH_TOKEN` / `GITHUB_TOKEN` for non-interactive automation
   - If absent, treat an already-authenticated `gh` CLI session as valid operator auth
   - Persist which auth path was used into evidence so operators can see whether env-token or CLI-session auth powered the action

2. **Repository owner resolution should come from operator-controlled sources, never the project slug**
   - Precedence should be explicit and stable, for example: env override → authority record existing shipping metadata → authenticated operator identity
   - `project_slug` may remain a repo-name fallback, but not an owner fallback

3. **Create vs attach should stay separated but share canonical identity resolution**
   - Identity resolution should happen before `prepare_github_repository()` so both create and attach consume the same normalized owner/name/url triple
   - Authority record should persist the chosen `repository_mode`, resolved owner/name/url, and how they were derived

## Key Edge Cases to Plan For

- `gh` installed, `gh auth status` healthy, no `GH_TOKEN`/`GITHUB_TOKEN`
- `GH_TOKEN` or `GITHUB_TOKEN` intentionally provided and should override local CLI state
- new approved project with no GitHub shipping metadata yet
- resumed approved project with existing shipping metadata that must remain stable across retries
- invalid owner fallback must never silently degrade to `project_slug`
- attach flow should inspect an existing approved target repo without mutating owner/repo defaults unexpectedly

## Most Likely Files to Change

Primary implementation files:
- `scripts/github_delivery_common.py`
- `scripts/start_approved_project_delivery.py`

Likely tests to update/add:
- GitHub delivery pipeline/unit tests under `tests/` that cover prepare/create/attach/auth blocked states
- any CLI or approved-delivery pipeline tests that assert blocked reasons or shipping metadata shape

Validation-only / evidence files:
- `assets/shared/approved-projects/lead-capture-copilot/APPROVED_PROJECT.json`
- `assets/shared/approved-projects/lead-capture-copilot/DELIVERY_PIPELINE_STATUS.md`
- workspace `.hermes/github-repository-prepare.json`

## Recommended planning focus

- add a dedicated GitHub auth source resolver instead of embedding token-only checks in `_has_github_auth()`
- add a dedicated repository identity resolver in `start_approved_project_delivery.py` before calling `prepare_github_repository()`
- lock owner fallback so only repo name can inherit from `project_slug`, never owner
- persist auth-source and owner/repo derivation details into GitHub prepare evidence and authority metadata
- cover both create and attach flows with regression tests built from the live failure cases
- verify both fresh-run and resume-run behavior so retries do not reintroduce bad defaults
