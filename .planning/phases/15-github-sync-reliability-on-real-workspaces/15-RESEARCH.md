# Phase 15: GitHub Sync Reliability on Real Workspaces - Research

**Researched:** 2026-04-29
**Domain:** Approved-project GitHub sync reliability in the governed delivery pipeline
**Confidence:** HIGH

<user_constraints>
## User Constraints (from CONTEXT.md)

No `*-CONTEXT.md` file exists under `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/phases/15-github-sync-reliability-on-real-workspaces`, so there are no phase-specific locked decisions beyond the user prompt, roadmap, requirements, and CLAUDE.md directives. [VERIFIED: codebase grep]
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| GHSYNC-01 | Exclude generated dependency/build directories such as `node_modules`, `.next`, `dist`, and other non-source snapshots from the canonical workspace commit | Snapshot filtering must be added at the sync helper seam that currently does `git add -A` over the whole workspace. [VERIFIED: codebase grep] |
| GHSYNC-02 | Succeed on the real Windows + pnpm workspace shape without long-path failures | Long-path mitigation belongs before or during staging in the Git sync helper, because the current implementation stages the entire workspace tree without path filtering. [VERIFIED: codebase grep] |
| GHSYNC-03 | Converge the configured remote when the workspace remote does not match the approved project repository | The current helper already has remote add/set-url behavior, so Phase 15 should extend and regression-test that seam rather than redesigning sync ownership. [VERIFIED: codebase grep] |
| GHSYNC-04 | Use a working Git transport strategy for the operator environment instead of failing only because HTTPS push is unavailable while SSH is healthy | Transport handling belongs in the same sync helper where push currently happens via one hard-coded `git push -u <remote> <branch>` path. [VERIFIED: codebase grep] |
| GHSYNC-05 | Write evidence that distinguishes staging, commit, remote, and push failures | Failure-boundary evidence belongs in `scripts/github_delivery_common.py` and must continue flowing through governance audit/event/status layers already used by the pipeline. [VERIFIED: codebase grep] |
</phase_requirements>

## Summary

Phase 15 is a focused hardening phase on the existing GitHub sync path, not a redesign of approved-project delivery. The current architecture already has the right ownership split: `scripts/start_approved_project_delivery.py` orchestrates pipeline state, `scripts/approved_delivery_governance.py` wraps credentialed actions with audit/event recording, and `scripts/github_delivery_common.py` owns the raw Git/GitHub repository prepare and sync mechanics. [VERIFIED: codebase grep] The main reliability gap is concentrated inside `sync_workspace_to_github`, which currently stages the entire workspace via `git add -A`, uses a single remote URL, and reports all sync failures under the generic `github_sync_failed` block reason with message-only differentiation. [VERIFIED: codebase grep]

The live-workspace failure shape described in roadmap and requirements aligns with that implementation: Windows + pnpm workspaces create large generated trees, and the helper currently offers no canonical source snapshot filter before staging. [VERIFIED: codebase grep] Because the pipeline already persists evidence, audit artifacts, blocked states, and downstream-stage blocking, the safest Phase 15 approach is to preserve those outer patterns and only harden the Git sync helper plus the narrow controller seams that copy helper outputs into authority records. [VERIFIED: codebase grep]

**Primary recommendation:** Keep repository preparation, governance wrapping, event rendering, and authority updates intact; implement Phase 15 by upgrading `sync_workspace_to_github` into a filtered, Windows-aware, remote-converging, transport-adaptive sync primitive with granular evidence fields and regression tests. [VERIFIED: codebase grep]

## Project Constraints (from CLAUDE.md)

- Frontend UI/UX skill enforcement applies only to frontend work; this phase is backend/script/test research, so no `/ui-ux-pro-max` invocation is required. [CITED: C:/Users/42236/Desktop/dev/profit-corp-hermes/CLAUDE.md]
- Do not recommend frontend implementation steps that bypass `/ui-ux-pro-max` if future work becomes user-facing UI. [CITED: C:/Users/42236/Desktop/dev/profit-corp-hermes/CLAUDE.md]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Canonical workspace snapshot selection | API / Backend | Database / Storage | Snapshot rules are enforced by Python delivery scripts before Git commit creation; no browser/runtime tier is involved. [VERIFIED: codebase grep] |
| Git remote convergence | API / Backend | — | Remote URL add/set logic is already implemented inside the Git sync helper. [VERIFIED: codebase grep] |
| Git transport fallback | API / Backend | — | Push behavior is controlled by Python helper command construction, not by status rendering or workspace generation. [VERIFIED: codebase grep] |
| Evidence artifact writing | API / Backend | Database / Storage | Evidence JSON is written into `.hermes/` in the workspace and then referenced by authority/status artifacts. [VERIFIED: codebase grep] |
| Blocked-result propagation | API / Backend | Database / Storage | `block_pipeline` persists stage, status, block reason, evidence path, and event entries into approved-project artifacts. [VERIFIED: codebase grep] |
| Operator-visible failure reporting | API / Backend | — | Status and final review markdown are rendered from authority + event data by `render_approved_delivery_status.py`. [VERIFIED: codebase grep] |

## Standard Stack

### Core
| Library / Tool | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python stdlib (`pathlib`, `subprocess`, `json`, `urllib.parse`, `re`) | stdlib | Delivery orchestration, Git subprocess execution, evidence writing | Current delivery pipeline already uses stdlib-only scripting for GitHub sync helpers and controller logic. [VERIFIED: codebase grep] |
| Git CLI | 2.53.0.windows.1 | Repository state, staging, branch, remote, push operations | Current helper uses `git` for all sync mechanics; Phase 15 should harden this existing path instead of replacing it. [VERIFIED: environment command] |
| GitHub CLI (`gh`) | 2.91.0 | Repository preparation and auth discovery in adjacent flow | Repository prepare already depends on `gh`; Phase 15 should preserve this division and focus only on sync reliability. [VERIFIED: environment command] |

### Supporting
| Library / Tool | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `scripts/approved_delivery_governance.py` wrapper | repo-local | Writes audit artifacts and append-only events around credentialed actions | Use unchanged as the authority/audit envelope for any Git sync helper improvements. [VERIFIED: codebase grep] |
| `scripts/render_approved_delivery_status.py` renderer | repo-local | Surfaces GitHub sync evidence/audit links and blocked status to operators | Extend only if new Phase 15 evidence fields must be surfaced. [VERIFIED: codebase grep] |
| `tests/test_phase11_github_sync.py` | repo-local | Unit seam for raw GitHub sync helper behavior | Add helper-level regression tests here for filters, remote mismatch, transport fallback, and failure-boundary evidence. [VERIFIED: codebase grep] |
| `tests/test_project_delivery_pipeline_bootstrap.py` and `tests/test_project_delivery_pipeline_resume.py` | repo-local | Pipeline integration seams for authority/event propagation | Add controller-level assertions here only for persisted metadata and blocked-stage behavior. [VERIFIED: codebase grep] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Continue shelling out to Git CLI | GitPython or dulwich [ASSUMED] | Would expand scope and bypass the repo’s existing tested subprocess-based helper boundary. [VERIFIED: codebase grep] |
| Helper-only evidence JSON + governance audit JSON | Single unified artifact [ASSUMED] | Would drift into broader audit architecture changes that belong outside Phase 15. [VERIFIED: codebase grep] |

**Installation:**
```bash
No new npm packages should be introduced for Phase 15. [VERIFIED: codebase grep]
```

**Version verification:**
- `git --version` -> `git version 2.53.0.windows.1` [VERIFIED: environment command]
- `gh --version` -> `gh version 2.91.0 (2026-04-22)` [VERIFIED: environment command]
- `node --version` -> `v24.14.0` [VERIFIED: environment command]
- `pnpm --version` -> `10.33.0` [VERIFIED: environment command]

## Architecture Patterns

### System Architecture Diagram

```text
Approved project authority record
        |
        v
start_approved_project_delivery.py
  - resolve repo identity
  - call governed github_repository action
  - call governed github_sync action
  - persist pipeline/shipping state
        |
        v
approved_delivery_governance.py
  - run helper
  - write audit artifact
  - append event stream record
        |
        v
github_delivery_common.py
  - ensure git repo state
  - converge remote
  - checkout branch
  - stage filtered snapshot
  - commit if needed
  - push via working transport
  - write helper evidence JSON
        |
        v
Authority record + events + status renderer
  - blocked/completed stage state
  - sync evidence path
  - sync audit path
  - downstream stage gating
```

### Recommended Project Structure
```text
scripts/
├── github_delivery_common.py          # Raw git/github sync primitives
├── approved_delivery_governance.py    # Audit/event wrapper for governed actions
├── start_approved_project_delivery.py # Pipeline controller and authority updates
├── render_approved_delivery_status.py # Operator-facing status/final review render
└── validate_approved_delivery_pipeline.py # Authority/status linkage validation

tests/
├── test_phase11_github_sync.py                # Helper-level sync behavior
├── test_project_delivery_pipeline_bootstrap.py# Pipeline persistence/integration
└── test_project_delivery_pipeline_resume.py   # Resume-stage continuity
```

### Pattern 1: Keep Git mechanics isolated in `github_delivery_common.py`
**What:** Raw sync mechanics already live in `sync_workspace_to_github`, while orchestration and authority persistence live elsewhere. [VERIFIED: codebase grep]
**When to use:** Any change to staging, remote setup, branch, push, or evidence payload shape for GitHub sync. [VERIFIED: codebase grep]
**Example:**
```python
# Source: scripts/start_approved_project_delivery.py
return run_governed_github_sync_action(
    authority_record_path=authority_record_path,
    stage="github_sync",
    workspace_path=workspace_path,
    repository_url=str(github_record.get("repository_url", "")).strip(),
    default_branch=str(github_record.get("default_branch", "")).strip() or "main",
    remote_name=str(github_record.get("remote_name", "origin")).strip() or "origin",
)
```

### Pattern 2: Preserve governed action wrapping for all credentialed GitHub work
**What:** The governance layer writes an audit artifact and an append-only event for every helper invocation. [VERIFIED: codebase grep]
**When to use:** Any Phase 15 helper enhancement must continue returning structured results consumed by `run_governed_github_sync_action`. [VERIFIED: codebase grep]
**Example:**
```python
# Source: scripts/approved_delivery_governance.py
result = dict(helper(...) or {})
audit_payload = _build_audit_payload(...)
audit_path = _write_json(_audit_path(project_dir, normalized_action), audit_payload)
_append_event(..., result=result, audit_path=audit_path, ...)
```

### Pattern 3: Persist GitHub sync outputs into authority shipping metadata, not ad hoc files only
**What:** After a successful sync, the pipeline copies repo URL, branch, commit, evidence path, and sync status into `record["shipping"]["github"]`. [VERIFIED: codebase grep]
**When to use:** Any new evidence fields worth surfacing to operators should be copied through this seam if they matter beyond the raw helper JSON. [VERIFIED: codebase grep]
**Example:**
```python
# Source: scripts/start_approved_project_delivery.py
github_record.update(
    {
        "repository_url": sync_result.get("repository_url", github_record.get("repository_url", "")),
        "default_branch": sync_result.get("default_branch", github_record.get("default_branch", "main")),
        "synced_commit": sync_result.get("synced_commit", "HEAD"),
        "sync_evidence_path": sync_result.get("evidence_path", sync_result.get("sync_evidence_path", "")),
        "last_sync_status": "completed",
    }
)
```

### Anti-Patterns to Avoid
- **Do not move sync logic into status rendering or authority-update code:** those layers already consume helper outputs and should remain consumers, not Git executors. [VERIFIED: codebase grep]
- **Do not collapse all failure modes into one generic message-only `github_sync_failed`:** Phase 15 explicitly requires distinguishing stage boundaries in evidence. [VERIFIED: requirements doc]
- **Do not redesign repository identity derivation in Phase 15:** owner/repo targeting belongs to Phase 14 per roadmap and requirements. [VERIFIED: roadmap doc]
- **Do not pull Vercel linkage/deploy semantics into this phase:** those are Phase 16 concerns. [VERIFIED: roadmap doc]

## Existing Patterns to Preserve

### Sync pattern to preserve
1. Repository identity is resolved before sync and stored under `shipping.github`. [VERIFIED: codebase grep]
2. Sync is invoked through `run_governed_github_sync_action`, not directly from the pipeline controller. [VERIFIED: codebase grep]
3. Success advances pipeline state to `vercel_linkage`; failure blocks downstream Vercel stages. [VERIFIED: codebase grep]

### Evidence pattern to preserve
1. Raw helper writes workspace-local evidence JSON in `.hermes/` via `_write_evidence`. [VERIFIED: codebase grep]
2. Governance wrapper writes a separate audit JSON and appends an event referencing both the stage and the evidence path. [VERIFIED: codebase grep]
3. Status/final-review rendering surfaces sync evidence and audit paths for operators. [VERIFIED: codebase grep]

### Blocked-result pattern to preserve
1. `block_pipeline` persists `stage`, `status=blocked`, `block_reason`, `evidence_path`, and `resume_from_stage`. [VERIFIED: codebase grep]
2. GitHub repository failure blocks `github_sync`, `vercel_linkage`, and `vercel_deploy`; GitHub sync failure blocks downstream Vercel stages. [VERIFIED: codebase grep]
3. Tests already assert blocked-state persistence into authority record, events, and status markdown. [VERIFIED: codebase grep]

### Authority-update pattern to preserve
1. Prepare-stage metadata is written into `shipping.github` before sync. [VERIFIED: codebase grep]
2. Sync success writes `repository_url`, `default_branch`, `synced_commit`, `sync_evidence_path`, and `last_sync_status`. [VERIFIED: codebase grep]
3. Resume flow expects these same stage transitions and event ordering to stay coherent. [VERIFIED: codebase grep]

## Failure Boundaries Likely in Current Helper/Controller Code

| Boundary | Current location | Current behavior | Phase 15 concern |
|---------|------------------|------------------|------------------|
| Git repo presence | `sync_workspace_to_github` `git rev-parse --is-inside-work-tree` | Blocks with `github_sync_failed` if workspace is not a repo. [VERIFIED: codebase grep] | Fine as-is; not a Phase 15 redesign target. |
| Remote missing | `git remote get-url` -> `git remote add` | Already converges absent remote. [VERIFIED: codebase grep] | Add regression coverage and preserve. |
| Remote mismatch | `git remote get-url` -> `git remote set-url` | Already converges mismatched remote URL. [VERIFIED: codebase grep] | Preserve and make evidence explicit. |
| Branch checkout | `git checkout -B <branch>` | Single failure bucket today. [VERIFIED: codebase grep] | Evidence should distinguish branch/remote prep from later stage failures. |
| Staging | `git add -A` | Stages whole workspace with no source filtering. [VERIFIED: codebase grep] | Primary Phase 15 defect surface for generated trees and long paths. |
| Commit creation | `git commit -m ...` | Single failure bucket today. [VERIFIED: codebase grep] | Evidence must distinguish commit failure from stage/push failure. |
| Push transport | `git push -u <remote> <branch>` | Single hard-coded push path. [VERIFIED: codebase grep] | Primary Phase 15 seam for HTTPS-vs-SSH fallback behavior. |
| Pipeline blocking | `block_pipeline` in controller | Correctly persists blocked state and downstream-stage blocks. [VERIFIED: codebase grep] | Preserve outer behavior while feeding it better helper evidence. |

## Best Code/Test Seams for Phase 15

### Code seams

| Need | Best seam | Why this seam |
|------|-----------|---------------|
| Snapshot filters | `scripts/github_delivery_common.py::sync_workspace_to_github` | This is where staging currently happens via `git add -A`; replacing broad staging with filtered staging is lowest-blast-radius. [VERIFIED: codebase grep] |
| Long-path protection | `scripts/github_delivery_common.py::sync_workspace_to_github` plus small helper functions | Long-path risk materializes during snapshot traversal/staging on Windows + pnpm workspaces. [VERIFIED: roadmap doc] |
| Remote convergence evidence | `scripts/github_delivery_common.py::sync_workspace_to_github` return payload | Remote add/set-url already happens here, so evidence about convergence belongs here too. [VERIFIED: codebase grep] |
| Transport fallback | `scripts/github_delivery_common.py::sync_workspace_to_github` | Push command construction is isolated here; transport adaptation should not leak into orchestration. [VERIFIED: codebase grep] |
| Authority copy-through | `scripts/start_approved_project_delivery.py` success path for `github_sync` | Any newly important helper fields must be copied into `shipping.github` here if operators or later phases need them. [VERIFIED: codebase grep] |
| Audit/event preservation | `scripts/approved_delivery_governance.py` unchanged or minimally extended | Governance wrapper already records audit/event artifacts for helper results. [VERIFIED: codebase grep] |

### Test seams

| Need | Best test file | Why |
|------|----------------|-----|
| Filtered staging and long-path exclusions | `tests/test_phase11_github_sync.py` | This file already stubs Git command sequences at the raw helper layer. [VERIFIED: codebase grep] |
| Remote mismatch convergence | `tests/test_phase11_github_sync.py` | Existing helper tests already cover missing-remote add flow and can be extended for `set-url` assertions. [VERIFIED: codebase grep] |
| Transport fallback command selection | `tests/test_phase11_github_sync.py` | Command-level stubbing is easiest here without pipeline noise. [VERIFIED: codebase grep] |
| Granular evidence propagation into authority record | `tests/test_project_delivery_pipeline_bootstrap.py` | Existing bootstrap tests assert `shipping.github` persistence and event order. [VERIFIED: codebase grep] |
| Resume continuity after sync changes | `tests/test_project_delivery_pipeline_resume.py` | Resume tests already validate stage continuity across `github_sync`. [VERIFIED: codebase grep] |
| Governance audit schema compatibility | `tests/test_phase12_credential_governance.py` | This file asserts audit/event contract for governed actions. [VERIFIED: codebase grep] |

### Recommended helper shape

Add narrow internal helpers inside `scripts/github_delivery_common.py` rather than broad controller changes: [VERIFIED: codebase grep]
- `_canonical_snapshot_paths(...)` or equivalent to derive included paths [ASSUMED]
- `_stage_workspace_snapshot(...)` to separate staging from branch/remote/push [ASSUMED]
- `_converge_remote(...)` to make remote change evidence explicit [ASSUMED]
- `_push_with_transport_fallback(...)` to try canonical URL then fallback path [ASSUMED]
- Structured failure result builder fields like `failed_step`, `attempted_command`, and `remote_strategy` [ASSUMED]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| End-to-end delivery architecture rewrite | New orchestration stack | Existing `start_approved_project_delivery.py` + governance wrapper | Current architecture already persists stage/audit/event/status continuity; Phase 15 only needs sync hardening. [VERIFIED: codebase grep] |
| New audit/event subsystem | Parallel logging mechanism | Existing `run_governed_github_sync_action` and `block_pipeline` flows | Governance/event/status plumbing already exists and is covered by tests. [VERIFIED: codebase grep] |
| Generic filesystem crawler for all workspace content | Unbounded full-tree staging | Canonical source snapshot allow/deny rules in sync helper | Generated pnpm/Next/build trees are exactly the failure mode this phase must avoid. [VERIFIED: requirements doc] |
| Repo metadata re-derivation logic | New owner/repo resolution path | Existing Phase 14 identity flow | Owner/repo targeting is Phase 14 scope, not Phase 15. [VERIFIED: roadmap doc] |

**Key insight:** The repo already has the right control-plane shape; the defect is in the data-plane of Git sync execution. [VERIFIED: codebase grep]

## Runtime State Inventory

| Category | Items Found | Action Required |
|----------|-------------|------------------|
| Stored data | Approved-project authority records and append-only event streams persist GitHub sync state under `assets/shared/approved-projects/*/APPROVED_PROJECT.json` and `approved-delivery-events.jsonl`. [VERIFIED: codebase grep] | Code edit only for Phase 15 unless current stored records must be repaired during testing; no broad migration is required by the phase goal. [ASSUMED] |
| Live service config | Git remotes inside generated workspaces may already point at the wrong repository URL, and Phase 15 explicitly targets convergence of mismatched remotes. [VERIFIED: requirements doc] | Code edit plus runtime remote update during sync; this is live workspace state convergence, not authority-schema migration. [VERIFIED: requirements doc] |
| OS-registered state | None found in researched files for GitHub sync. [VERIFIED: codebase grep] | None. |
| Secrets/env vars | GitHub sync itself currently consumes repo URL/branch/remote from authority metadata; adjacent auth inputs are `GH_TOKEN`/`GITHUB_TOKEN` or authenticated `gh` CLI, but auth-source detection is Phase 14. [VERIFIED: codebase grep] | Leave auth-source logic unchanged in Phase 15 except as needed for transport use of already-healthy SSH. [VERIFIED: roadmap doc] |
| Build artifacts | Real workspaces may contain `node_modules`, `.next`, `dist`, and other generated trees that should not enter the canonical commit. [VERIFIED: requirements doc] | Code edit to snapshot filtering; no artifact migration after the fact unless a test fixture intentionally seeds them. |

## Common Pitfalls

### Pitfall 1: Fixing only the blocked message, not the staging set
**What goes wrong:** The helper still stages the entire workspace tree, so Windows + pnpm failures remain even if evidence messaging improves. [VERIFIED: codebase grep]
**Why it happens:** Current implementation uses `git add -A` without source filtering. [VERIFIED: codebase grep]
**How to avoid:** Make filtered snapshot selection the first substantive helper change. [VERIFIED: requirements doc]
**Warning signs:** Tests still accept a raw `git add -A` path with generated directories present. [VERIFIED: codebase grep]

### Pitfall 2: Solving transport by mutating repo targeting logic
**What goes wrong:** Phase 15 drifts back into Phase 14 owner/repo resolution work. [VERIFIED: roadmap doc]
**Why it happens:** Remote mismatch and transport issues both touch Git URLs, but they are different concerns. [VERIFIED: roadmap doc]
**How to avoid:** Treat approved repo identity as input and only converge workspace remote + push behavior. [VERIFIED: requirements doc]
**Warning signs:** Changes start modifying `resolve_github_repository_identity` defaults instead of sync execution. [VERIFIED: codebase grep]

### Pitfall 3: Writing granular failure info only to audit logs
**What goes wrong:** Operators still cannot tell the true helper failure boundary from the primary sync evidence file. [VERIFIED: requirements doc]
**Why it happens:** Governance audit currently stores top-level reason/error/evidence, but helper evidence is still coarse. [VERIFIED: codebase grep]
**How to avoid:** Put step-level failure data into `github-sync.json` first, then let governance mirror it. [VERIFIED: codebase grep]
**Warning signs:** `github-sync.json` still only contains `{ok:false, block_reason, message}` equivalents. [VERIFIED: codebase grep]

### Pitfall 4: Letting Phase 15 leak into final status truth reconciliation
**What goes wrong:** Work expands into stale-history-versus-current-truth rendering changes that roadmap assigns to Phase 17. [VERIFIED: roadmap doc]
**Why it happens:** Better sync evidence naturally touches operator-facing artifacts. [VERIFIED: codebase grep]
**How to avoid:** Only surface new sync evidence fields needed for Phase 15; do not redesign completed-vs-blocked rendering semantics here. [VERIFIED: roadmap doc]
**Warning signs:** Planned tasks start rewriting status precedence or final-review truth rules. [VERIFIED: roadmap doc]

## Code Examples

Verified patterns from current codebase:

### Governed GitHub sync dispatch
```python
# Source: scripts/approved_delivery_governance.py
return run_governed_action(
    action="github_sync",
    authority_record_path=authority_record_path,
    stage=stage,
    helper=lambda **_: sync_workspace_to_github(
        workspace_path=workspace_path,
        repository_url=repository_url,
        default_branch=default_branch,
        remote_name=remote_name,
        **kwargs,
    ),
)
```

### Current remote convergence seam
```python
# Source: scripts/github_delivery_common.py
existing_remote = run_git("git", "remote", "get-url", remote)
if int(getattr(existing_remote, "returncode", 1)) != 0:
    add_remote = run_git("git", "remote", "add", remote, repo_url)
elif str(getattr(existing_remote, "stdout", "")).strip() != repo_url:
    set_remote = run_git("git", "remote", "set-url", remote, repo_url)
```

### Current coarse staging seam that Phase 15 must replace or wrap
```python
# Source: scripts/github_delivery_common.py
add_result = run_git("git", "add", "-A")
if int(getattr(add_result, "returncode", 1)) != 0:
    return _blocked(
        workspace,
        "github-sync.json",
        "github_sync_failed",
        "Failed to stage workspace snapshot.",
        stderr_summary=_safe_summary(getattr(add_result, "stderr", "")),
    )
```

### Current blocked-state persistence seam
```python
# Source: scripts/start_approved_project_delivery.py
update_pipeline_state(
    record,
    stage=stage,
    status="blocked",
    block_reason=block_reason,
    workspace_path=workspace_path or record.get("pipeline", {}).get("workspace_path", ""),
    evidence_path=evidence_path,
    resume_from_stage=stage,
    delivery_run_id=delivery_run_id or record.get("pipeline", {}).get("delivery_run_id", ""),
)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Generic credentialed action execution without a hard allowlist [ASSUMED] | Governed allowlist for GitHub/Vercel credential actions in `approved_delivery_governance.py` | Present in current repo as of 2026-04-29. [VERIFIED: codebase grep] | Phase 15 should remain inside the existing governed action envelope. |
| Repo sync that only needed branch persistence | Repo sync now also feeds authority/status/final-review surfaces with evidence links and sync metadata | Present in current repo as of 2026-04-29. [VERIFIED: codebase grep] | Helper result shape changes have downstream artifact implications. |

**Deprecated/outdated:**
- Using whole-workspace `git add -A` as the canonical snapshot definition is outdated for the real Windows + pnpm workspace shape targeted by this milestone. [VERIFIED: requirements doc]

## Explicitly Out of Scope for Phase 15

- GitHub auth source detection and owner/repo derivation repairs from Phase 14. [VERIFIED: roadmap doc]
- Vercel auth, linkage, env contract, and deploy reliability work from Phase 16. [VERIFIED: roadmap doc]
- Authority/status truth-precedence and recovered-success rendering redesign from Phase 17. [VERIFIED: roadmap doc]
- New product features in generated SaaS apps, orchestration redesign, DNS automation, canary automation, or broader collaboration/platform expansion. [VERIFIED: requirements doc]
- Replacing the Python subprocess Git helper with a new Git library stack. [VERIFIED: codebase grep]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | GitPython or dulwich would add unnecessary scope versus current CLI helper path | Standard Stack / Alternatives | Low — planner may overestimate refactor cost, but phase direction still favors existing seam |
| A2 | Unifying helper evidence fields through narrow internal helpers is the cleanest implementation shape | Best Code/Test Seams | Low — exact function factoring may differ while preserving seam ownership |
| A3 | Existing stored authority/event records will not require a formal migration for Phase 15 | Runtime State Inventory | Medium — if older records must surface new fields, planner may need a repair task |
| A4 | Older governance action style was less constrained than the current allowlist model | State of the Art | Low — historical comparison only, not needed for implementation |

## Open Questions

1. **What exact snapshot rule should define the canonical workspace commit?**
   - What we know: Requirements explicitly call out `node_modules`, `.next`, and `dist` as exclusions, and the current helper stages the full workspace. [VERIFIED: requirements doc] [VERIFIED: codebase grep]
   - What's unclear: The full denylist/allowlist for other generated directories such as `.turbo`, `coverage`, `out`, lockfile-adjacent caches, and template-specific artifacts. [ASSUMED]
   - Recommendation: Lock a canonical exclude set in Plan 15-01 and add tests that encode it as contract behavior.

2. **Should transport fallback rewrite the remote URL, use a push-only URL, or retry with an alternate computed URL?**
   - What we know: Requirement GHSYNC-04 is about successful operator transport when HTTPS push is unavailable but SSH is healthy. [VERIFIED: requirements doc]
   - What's unclear: Whether the approved operator expectation is to preserve HTTPS as canonical metadata while pushing through SSH, or to converge the canonical remote itself to SSH. [ASSUMED]
   - Recommendation: Keep canonical approved repo identity stable and record both canonical repo URL and effective push transport in evidence unless the user has already standardized on SSH-only remotes.

3. **How much new evidence should be copied into authority metadata versus left in helper JSON?**
   - What we know: Status validation currently requires repo name, repo URL, branch, commit, and sync evidence path, but not per-step sync diagnostics. [VERIFIED: codebase grep]
   - What's unclear: Whether operators need step-level failure summaries directly in authority/status surfaces or only in `github-sync.json` / audit JSON. [ASSUMED]
   - Recommendation: Persist minimum top-level fields in authority; keep detailed step diagnostics in helper evidence to avoid Phase 17 rendering drift.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Git CLI | GitHub sync helper | ✓ | 2.53.0.windows.1 | None; blocking if absent. [VERIFIED: environment command] |
| GitHub CLI (`gh`) | Adjacent repository-prepare stage, auth discovery context | ✓ | 2.91.0 | None for Phase 14/15 repository prepare flow. [VERIFIED: environment command] |
| Node.js | Generated pnpm workspace ecosystem context | ✓ | v24.14.0 | — [VERIFIED: environment command] |
| pnpm | Real workspace shape under investigation | ✓ | 10.33.0 | — [VERIFIED: environment command] |
| Python launcher via `python3` | Direct shell probe only | ✗ | — | Repo scripts may still run through `python`/`py`; current probe failed for `python3`. [VERIFIED: environment command] |

**Missing dependencies with no fallback:**
- None identified for the research scope itself. [VERIFIED: environment command]

**Missing dependencies with fallback:**
- `python3` command alias is unavailable in this shell probe, but Phase 15 research is about code seams rather than executing the delivery pipeline end-to-end. [VERIFIED: environment command]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Python `unittest` with importlib-based script loading. [VERIFIED: codebase grep] |
| Config file | none detected in researched files. [VERIFIED: codebase grep] |
| Quick run command | `python -m unittest tests.test_phase11_github_sync` [ASSUMED] |
| Full suite command | `python -m unittest discover -s tests` [ASSUMED] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| GHSYNC-01 | Generated dirs excluded from snapshot | unit | `python -m unittest tests.test_phase11_github_sync` [ASSUMED] | ✅ |
| GHSYNC-02 | Windows + pnpm shape avoids long-path staging failure | unit | `python -m unittest tests.test_phase11_github_sync` [ASSUMED] | ✅ |
| GHSYNC-03 | Remote mismatch converges to approved repo | unit + pipeline integration | `python -m unittest tests.test_phase11_github_sync tests.test_project_delivery_pipeline_bootstrap` [ASSUMED] | ✅ |
| GHSYNC-04 | Working push transport strategy used | unit | `python -m unittest tests.test_phase11_github_sync` [ASSUMED] | ✅ |
| GHSYNC-05 | Evidence distinguishes remote/stage/commit/push boundaries | unit + pipeline integration | `python -m unittest tests.test_phase11_github_sync tests.test_project_delivery_pipeline_bootstrap tests.test_phase12_credential_governance` [ASSUMED] | ✅ |

### Sampling Rate
- **Per task commit:** `python -m unittest tests.test_phase11_github_sync` [ASSUMED]
- **Per wave merge:** `python -m unittest tests.test_phase11_github_sync tests.test_project_delivery_pipeline_bootstrap tests.test_project_delivery_pipeline_resume tests.test_phase12_credential_governance` [ASSUMED]
- **Phase gate:** Full targeted suite green before `/gsd-verify-work` [ASSUMED]

### Wave 0 Gaps
- [ ] Add helper-level tests for snapshot filter behavior and excluded generated directories in `tests/test_phase11_github_sync.py`. [VERIFIED: codebase grep]
- [ ] Add helper-level tests for mismatched-remote `set-url` convergence in `tests/test_phase11_github_sync.py`. [VERIFIED: codebase grep]
- [ ] Add helper-level tests for transport fallback / alternate push strategy selection in `tests/test_phase11_github_sync.py`. [ASSUMED]
- [ ] Add helper-level tests for granular evidence payload fields that distinguish remote/setup/stage/commit/push failures. [VERIFIED: requirements doc]
- [ ] Add pipeline-level assertions that any newly persisted sync metadata survives bootstrap/resume authority updates without breaking event order. [VERIFIED: codebase grep]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Preserve existing GitHub auth-source handling from Phase 14; do not weaken credential gating in governed actions. [VERIFIED: codebase grep] |
| V3 Session Management | no | Not a web session feature; this phase is delivery automation behavior. [VERIFIED: requirements doc] |
| V4 Access Control | yes | Keep GitHub/Vercel credential use behind governed action allowlists and authority-linked audits. [VERIFIED: codebase grep] |
| V5 Input Validation | yes | Continue validating repo owner/name/branch/remote via existing regex validators in helper code. [VERIFIED: codebase grep] |
| V6 Cryptography | no | No cryptographic primitive changes are in scope. [VERIFIED: requirements doc] |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Pushing to the wrong repository because workspace remote drifted | Tampering | Converge remote URL from approved authority metadata before push. [VERIFIED: requirements doc] |
| Over-broad snapshot commits leaking generated or machine-local artifacts | Information Disclosure | Canonical source snapshot filters before staging. [VERIFIED: requirements doc] |
| Ambiguous failure evidence that hides the real boundary | Repudiation | Persist helper evidence plus governance audit/event linkage per stage. [VERIFIED: codebase grep] |
| Invalid repo/branch/remote inputs flowing into Git commands | Tampering | Preserve `_validate_owner`, `_validate_repo`, `_validate_branch`, `_validate_remote`, `_validate_repository_url`. [VERIFIED: codebase grep] |

## Sources

### Primary (HIGH confidence)
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/PROJECT.md` - milestone goal, current state, constraints
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/ROADMAP.md` - Phase 15/16/17 scope boundaries and success criteria
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/REQUIREMENTS.md` - GHSYNC-01..05 definitions
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/STATE.md` - live milestone context and blocker summary
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/github_delivery_common.py` - raw GitHub repository/sync helper behavior
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py` - pipeline orchestration and authority-update seams
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/approved_delivery_governance.py` - governance audit/event wrapper
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/render_approved_delivery_status.py` - operator-facing status/final-review rendering
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_approved_delivery_pipeline.py` - linkage validation expectations
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_phase11_github_sync.py` - helper-level test seams
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_project_delivery_pipeline_bootstrap.py` - bootstrap persistence/event tests
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_project_delivery_pipeline_resume.py` - resume continuity tests
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_phase12_credential_governance.py` - governance audit/event contract
- Environment probes: `git --version`, `gh --version`, `node --version`, `pnpm --version`, `python3 --version`

### Secondary (MEDIUM confidence)
- None. All main implementation guidance above is grounded in repo evidence or direct environment probes. [VERIFIED: codebase grep]

### Tertiary (LOW confidence)
- No external docs could be verified in-session due fetch restrictions, so any Git transport strategy specifics beyond repository evidence are marked `[ASSUMED]`. [VERIFIED: tool results]

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - current implementation is entirely discoverable from repo scripts and environment probes.
- Architecture: HIGH - controller/helper/governance/status boundaries are explicit in current code and tests.
- Pitfalls: HIGH - they map directly to stated requirements and current helper behavior.

**Research date:** 2026-04-29
**Valid until:** 2026-05-29
