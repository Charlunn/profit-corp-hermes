---
phase: 15-github-sync-reliability-on-real-workspaces
plan: 02
subsystem: infra
tags: [github, git, remote, ssh, transport, evidence]

# Dependency graph
requires:
  - phase: 15-github-sync-reliability-on-real-workspaces
    provides: canonical source-only snapshot staging and helper evidence base
provides:
  - remote convergence for mismatched GitHub workspace remotes
  - transport fallback from HTTPS to SSH when push transport differs from operator environment
  - step-specific sync evidence for remote, branch, stage, commit, and push boundaries
affects: [github_sync, approved_delivery, authority_status]

# Tech tracking
tech-stack:
  added: []
  patterns: [remote convergence helper, transport fallback sequencing, failed-step evidence contract]

key-files:
  created: []
  modified:
    - scripts/github_delivery_common.py
    - scripts/start_approved_project_delivery.py
    - tests/test_phase11_github_sync.py

key-decisions:
  - "Treat the approved HTTPS repository URL as canonical metadata while allowing SSH as the effective push transport when needed."
  - "Persist failed-step and attempted-command metadata at the helper layer instead of collapsing all sync failures into one opaque message."

patterns-established:
  - "GitHub sync converges the workspace remote before branch/push work begins."
  - "Push transport fallback records every attempted transport and preserves canonical authority metadata."

requirements-completed: [GHSYNC-03, GHSYNC-04, GHSYNC-05]

# Metrics
duration: unknown
completed: 2026-04-29
---

# Phase 15 Plan 02 Summary

**GitHub sync now converges workspace remotes, retries push through an operator-healthy transport path, and emits granular failure-boundary evidence.**

## Performance

- **Duration:** unknown
- **Started:** unknown
- **Completed:** 2026-04-29T14:28:00Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- Added helper-level remote convergence with explicit `remote_action` evidence.
- Added HTTPS→SSH push fallback and persisted attempted transport metadata.
- Added granular helper diagnostics such as `failed_step`, `attempted_command`, and `push_attempts`, then copied the relevant sync metadata into `shipping.github`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add red tests for remote convergence, transport fallback, and failure-boundary evidence** - `not committed` (test)
2. **Task 2: Implement remote convergence, transport adaptation, and structured helper evidence** - `not committed` (fix)
3. **Task 3: Persist sync evidence metadata through the controller without status-semantics drift** - `not committed` (fix)

**Plan metadata:** pending current phase commit

## Files Created/Modified
- `scripts/github_delivery_common.py` - Adds remote convergence, transport fallback, and failed-step evidence fields.
- `scripts/start_approved_project_delivery.py` - Persists sync transport and remote metadata into `shipping.github`.
- `tests/test_phase11_github_sync.py` - Verifies remote mismatch convergence, SSH fallback, and commit/push failure boundary evidence.

## Decisions Made
- Preserved canonical repository identity as HTTPS authority metadata even when the effective push path is SSH.
- Kept controller changes narrow: only copy through metadata that downstream artifacts and later phases need.

## Deviations from Plan

None - plan executed within the intended helper/controller seam.

## Issues Encountered
- The generic `github_sync_failed` block reason remained in outer pipeline status semantics; the plan addressed the ambiguity by making helper evidence step-specific rather than redesigning phase-level status precedence.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Phase 15-03 can validate the full helper/controller contract end to end using the new sync evidence fields.
- Phase 16 can rely on more accurate `shipping.github` metadata and sync failure boundaries when diagnosing Vercel-stage failures.

## Self-Check: PASSED
- Remote mismatch, transport fallback, and failure-boundary coverage is present in helper tests.
- `shipping.github` now retains sync transport/remote metadata required downstream.

---
*Phase: 15-github-sync-reliability-on-real-workspaces*
*Completed: 2026-04-29*
