# Phase 16: Vercel Auth and Deploy Reliability - Research

**Researched:** 2026-04-29  
**Domain:** Vercel CLI auth, governed delivery orchestration, authority/status metadata persistence  
**Confidence:** MEDIUM

## User Constraints

### Locked Decisions
- Repair the approved-project GitHub/Vercel shipping path so the live operator environment can complete delivery without manual rescue and the authority/status surfaces converge to the true final state. [VERIFIED: `.planning/ROADMAP.md`]
- Preserve the one-approval automated delivery model; remove manual recovery steps required in the live test. [VERIFIED: `.planning/PROJECT.md`, `.planning/ROADMAP.md`]
- Keep the approved-project delivery architecture; repair broken auth/sync/deploy/status boundaries rather than redesigning orchestration wholesale. [VERIFIED: `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`]
- Prioritize real operator-environment compatibility over token-only automation assumptions. [VERIFIED: `.planning/ROADMAP.md`]

### Claude's Discretion
- Recommend exact helper boundaries, persistence rules, and tests for Phase 16 implementation.
- Recommend which Phase 15 hardening patterns should be mirrored for Vercel.

### Deferred Ideas
- DNS/domain automation, post-deploy canary automation, and broader multi-user/team workflows remain out of scope. [VERIFIED: `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`]
- Authority/status final convergence rendering is Phase 17 except for metadata/evidence persistence that Phase 16 must provide. [VERIFIED: `.planning/ROADMAP.md`, `.planning/PROJECT.md`]

## Phase Requirements

| ID | Description | Research Support |
|---|---|---|
| VERC-01 | Use local authenticated Vercel CLI session when `VERCEL_TOKEN` is absent | Centralize Vercel auth resolution in `scripts/vercel_delivery_common.py`; mirror GitHub's env-or-CLI pattern and persist `auth_source` evidence |
| VERC-02 | Still support explicit `VERCEL_TOKEN` for automation | Keep env token as first-class auth path; do not regress current token flow |
| VERC-03 | Record real linked project name, scope, deploy URL, deployment evidence | Stop pre-writing default Vercel metadata in `scripts/start_approved_project_delivery.py`; only persist authoritative fields from link/deploy results |
| VERC-04 | Distinguish invalid token, inaccessible scope, missing CLI, actual deploy failure | Split coarse blocked reasons in `scripts/vercel_delivery_common.py`; surface them through governance audit, authority record, and tests |

## Summary

Phase 16 should be implemented as a Vercel-specific replay of the Phase 14/15 GitHub hardening pattern, not as an isolated patch. The codebase already has the right architectural seams: `scripts/vercel_delivery_common.py` owns CLI/auth/link/env/deploy behavior, `scripts/start_approved_project_delivery.py` owns pipeline-stage orchestration and authority persistence, and `scripts/approved_delivery_governance.py` owns append-only audit/event wrapping. The current reliability gap is not that Vercel delivery is missing; it is that the existing implementation assumes token-only auth, collapses distinct failure modes into generic blocked outcomes, and writes default/inherited Vercel metadata before the system has authoritative linkage/deploy evidence.

The most important planning decision is to treat Vercel auth resolution and Vercel metadata provenance as first-class contracts. Today, `_require_vercel()` blocks any run without `VERCEL_TOKEN`, even when the operator may already be logged into the Vercel CLI. Separately, the delivery pipeline pre-populates `shipping.vercel.project_name`, `project_url`, and `team_scope` from environment/defaults before real linkage occurs, which is the clearest path to stale metadata showing up as if it were authoritative.

**Primary recommendation:** Implement Phase 16 by introducing centralized Vercel auth-source resolution plus authoritative-only Vercel metadata persistence, then extend governance/status/test coverage around those new contracts.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|---|---|---|---|
| Resolve Vercel auth source | API / Backend | OS / local CLI environment | Auth choice is made in Python delivery helpers, but depends on machine-local CLI session or env token |
| Resolve/link approved Vercel project | API / Backend | External service (Vercel CLI/API) | The pipeline invokes CLI commands and interprets their outcomes |
| Apply env contract to Vercel project | API / Backend | External service | Governance and env application happen in delivery scripts, not in UI |
| Deploy approved project | API / Backend | External service | The backend orchestration owns deploy sequencing and evidence capture |
| Persist authoritative Vercel metadata | Database / Storage | API / Backend | `APPROVED_PROJECT.json` is the authority surface and is written by orchestration |
| Emit audit artifacts and events | Database / Storage | API / Backend | Governance wrappers create append-only evidence and audit paths |
| Render operator-visible status | API / Backend | Storage | Renderers consume authority + events; Phase 16 should feed them clean metadata |

## Standard Stack

### Core

| Library / Tool | Purpose | Why Standard |
|---|---|---|
| Python stdlib subprocess/pathlib/json | CLI orchestration, evidence writing, path management | Current delivery pipeline already uses it; Phase 16 should extend existing patterns |
| Vercel CLI | Project link, env apply, deploy | Existing helpers already depend on the CLI |
| Node.js / npx | Supports `npx vercel@latest` fallback | Existing helper resolves `npx`/`npx.cmd` |

## Architecture Patterns

### Pattern 1: Centralized auth-source resolution
- Create a Vercel equivalent of GitHub's `_resolve_github_auth(...)`.
- Return `ok`, `auth_source`, and `auth_source_details`.
- `_require_vercel()` should become a thin wrapper around command resolution plus auth resolution, not a token-only gate.

### Pattern 2: Authoritative-only metadata writes
- Do not pre-populate `shipping.vercel.project_name`, `project_url`, or `team_scope` from defaults immediately after GitHub sync.
- Treat env/defaults as candidate inputs, not authority truth.
- Require link/deploy result payloads to carry all authoritative fields needed downstream.

### Pattern 3: Distinct blocked outcomes with evidence
- Preserve `missing_vercel_cli`.
- Add separate reasons for invalid token/auth failure, inaccessible scope/team/project access failure, and actual deploy execution failure.
- Push those reasons through governance audit so blocked outcomes remain operator-visible.

### Anti-Patterns to Avoid
- Token-only gating in `_require_vercel()`.
- Writing defaults as authoritative truth.
- Treating `project_name` presence as proof of successful linkage.
- Collapsing unrelated failures into `vercel_linkage_failed` / `vercel_deploy_failed`.

## Exact Files and Tests by Requirement

### VERC-01 / VERC-02
**Primary code files**
- `scripts/vercel_delivery_common.py`
- `scripts/start_approved_project_delivery.py`
- `scripts/approved_delivery_governance.py`

**Best tests**
- `tests/test_phase11_vercel_flow.py`
- `tests/test_phase12_credential_governance.py`

### VERC-03
**Primary code files**
- `scripts/start_approved_project_delivery.py`
- `scripts/vercel_delivery_common.py`
- `scripts/render_approved_delivery_status.py`
- `scripts/validate_approved_delivery_pipeline.py`

**Best tests**
- `tests/test_phase11_vercel_flow.py`
- `tests/test_project_delivery_pipeline_bootstrap.py`
- `tests/test_project_delivery_pipeline_resume.py`
- `tests/test_approved_delivery_pipeline_cli.py`

### VERC-04
**Primary code files**
- `scripts/vercel_delivery_common.py`
- `scripts/approved_delivery_governance.py`
- `scripts/start_approved_project_delivery.py`

**Best tests**
- `tests/test_phase11_vercel_flow.py`
- `tests/test_phase12_credential_governance.py`
- `tests/test_project_delivery_pipeline_resume.py`

## Current Seams That Must Change

### Token-only auth gate
Current Vercel gate is token-only and is the direct blocker for VERC-01:
```python
if not source.get("VERCEL_TOKEN"):
    return None, _blocked(
        workspace,
        evidence_name,
        "missing_vercel_auth",
        "VERCEL_TOKEN is required for non-interactive Vercel automation.",
    )
```

### Stale metadata seam
Current pipeline writes default Vercel metadata before authoritative linkage:
```python
approved_vercel_project = str(os.environ.get("VERCEL_PROJECT", "")).strip() or f"{project_slug}-prod"
approved_vercel_team = str(os.environ.get("VERCEL_TEAM", "")).strip() or "profit-corp"
vercel_record["project_name"] = approved_vercel_project
vercel_record["project_url"] = f"https://vercel.com/{approved_vercel_team}/{approved_vercel_project}"
vercel_record["team_scope"] = approved_vercel_team
```

## Validation Architecture

| Property | Value |
|---|---|
| Framework | Python `unittest` |
| Quick run command | `python -m unittest tests.test_phase11_vercel_flow -v` |
| Full targeted phase command | `python -m unittest tests.test_phase11_vercel_flow tests.test_project_delivery_pipeline_bootstrap tests.test_project_delivery_pipeline_resume tests.test_phase12_credential_governance tests.test_approved_delivery_pipeline_cli -v` |

### Wave 0 Gaps
- Add Vercel CLI-auth success test without token to `tests/test_phase11_vercel_flow.py`.
- Add invalid-token vs inaccessible-scope vs deploy-failure reason matrix in `tests/test_phase11_vercel_flow.py`.
- Add authority stale-metadata replacement assertions in `tests/test_project_delivery_pipeline_bootstrap.py`.
- Add resume/recovery authority convergence assertions in `tests/test_project_delivery_pipeline_resume.py`.
- Consider strengthening validator requirements in `scripts/validate_approved_delivery_pipeline.py` and `tests/test_approved_delivery_pipeline_cli.py` if Phase 16 makes `team_scope`/`project_url` mandatory proof fields.

## In Scope
- Centralized Vercel auth-source resolution for token and locally authenticated CLI paths.
- Distinct blocked outcomes for CLI missing, invalid auth/token, inaccessible scope, and deploy execution failure.
- Authoritative Vercel metadata persistence for real linked project name, scope, deploy URL, and evidence paths.
- Regression coverage across helper, governance, pipeline bootstrap/resume, and validation/status boundaries.

## Out of Scope
- Replacing CLI-based Vercel automation with a new API-based delivery architecture.
- Broad status-surface redesign for historical-failure reconciliation; that belongs to Phase 17.
- New product feature work in generated SaaS apps.
- General platform expansion like DNS automation or collaboration workflows.

## Open Questions
1. What exact Vercel CLI command/output should define “authenticated local session”?
2. Should `team_scope` and `project_url` become validator-required fields after successful linkage?
3. Should non-authoritative candidate Vercel inputs be preserved anywhere, and if so only in evidence rather than authority truth fields?

## RESEARCH COMPLETE

**Phase:** 16 - Vercel Auth and Deploy Reliability  
**Confidence:** MEDIUM

### Key Findings
- `scripts/vercel_delivery_common.py` currently blocks all no-token runs; this is the direct seam for VERC-01 and must be replaced with centralized auth-source resolution.
- `scripts/start_approved_project_delivery.py` writes Vercel project/scope/URL defaults into authority before successful linkage; this is the strongest stale-metadata seam for VERC-03.
- Vercel blocked outcomes are currently too coarse; VERC-04 requires splitting them into operator-meaningful reasons.
- The correct design model already exists in GitHub Phase 14/15: centralized auth resolution, structured evidence, granular blocked reasons, and layered regression tests.
- Best test expansion points are `tests/test_phase11_vercel_flow.py`, `tests/test_phase12_credential_governance.py`, `tests/test_project_delivery_pipeline_bootstrap.py`, and `tests/test_project_delivery_pipeline_resume.py`.
