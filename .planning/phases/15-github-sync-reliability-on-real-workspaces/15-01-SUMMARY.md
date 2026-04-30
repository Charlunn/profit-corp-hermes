---
phase: 15-github-sync-reliability-on-real-workspaces
plan: 01
subsystem: infra
tags: [github, git, snapshot, windows, pnpm, testing]

# Dependency graph
requires:
  - phase: 14-github-auth-and-repository-target-resolution
    provides: canonical GitHub repository identity and authority-backed repository metadata
provides:
  - canonical workspace snapshot filtering for GitHub sync
  - generated-directory exclusions that avoid Windows path-heavy staging failures
  - operator-visible snapshot evidence in github-sync.json
affects: [github_sync, approved_delivery, vercel_linkage]

# Tech tracking
tech-stack:
  added: []
  patterns: [explicit snapshot staging, generated-path exclusion contract, helper evidence-first sync diagnostics]

key-files:
  created: []
  modified:
    - scripts/github_delivery_common.py
    - tests/test_phase11_github_sync.py

key-decisions:
  - "Use explicit path staging instead of whole-workspace `git add -A` for the canonical delivery snapshot."
  - "Exclude generated directories at the helper seam and record the applied snapshot policy in helper evidence."

patterns-established:
  - "GitHub sync stages a deterministic source-only snapshot rather than the full generated workspace tree."
  - "Snapshot evidence records included paths and excluded categories for operator auditability."

requirements-completed: [GHSYNC-01, GHSYNC-02]

# Metrics
duration: unknown
completed: 2026-04-29
---

# Phase 15 Plan 01 Summary

**GitHub sync now stages a deterministic source-only snapshot that excludes generated workspace trees and records the applied snapshot policy in evidence.**

## Performance

- **Duration:** unknown
- **Started:** unknown
- **Completed:** 2026-04-29T14:20:00Z
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- Replaced whole-workspace staging with explicit snapshot path staging in the GitHub sync helper.
- Excluded generated directories such as `node_modules`, `.next`, `dist`, `build`, and related caches from the canonical sync snapshot.
- Added regression coverage proving generated artifacts stay out of staged paths while evidence records the snapshot contract.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add red tests for canonical workspace snapshot filtering** - `not committed` (test)
2. **Task 2: Implement filtered snapshot staging and evidence in the sync helper** - `not committed` (fix)

**Plan metadata:** pending current phase commit

## Files Created/Modified
- `scripts/github_delivery_common.py` - Adds snapshot path derivation, generated-directory exclusions, and snapshot evidence fields.
- `tests/test_phase11_github_sync.py` - Verifies explicit-path staging replaces raw `git add -A` and that evidence captures snapshot filtering details.

## Decisions Made
- Staged only explicit included source files instead of relying on repo-level ignore behavior.
- Kept snapshot-policy evidence in `github-sync.json` so downstream status and audits can explain what was intentionally excluded.

## Deviations from Plan

None - plan executed within the intended helper/test seam.

## Issues Encountered
- None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Phase 15-02 can build on a stable source-only snapshot path without revisiting Windows long-path staging failures.
- Downstream sync diagnostics can now reuse snapshot evidence fields rather than inferring them from git behavior.

## Self-Check: PASSED
- Snapshot staging no longer relies on whole-workspace `git add -A`.
- Regression tests cover generated-directory exclusion and snapshot evidence output.

---
*Phase: 15-github-sync-reliability-on-real-workspaces*
*Completed: 2026-04-29*
