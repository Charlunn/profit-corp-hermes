---
phase: 14-github-auth-and-repository-target-resolution
plan: 01
subsystem: auth
tags: [github, gh-cli, approved-delivery, authority-metadata, testing]

# Dependency graph
requires: []
provides:
  - layered GitHub auth resolution that accepts env tokens or authenticated gh CLI sessions
  - canonical repository owner/name/url derivation for approved-project delivery bootstrap and resume flows
  - authority metadata and evidence fields that expose repository identity and GitHub auth source
affects: [github_sync, approved_delivery, delivery_pipeline_reliability]

# Tech tracking
tech-stack:
  added: []
  patterns: [authority-first metadata persistence, helper blocked-result contract, controller-side canonical repository identity resolution]

key-files:
  created: []
  modified:
    - scripts/github_delivery_common.py
    - scripts/start_approved_project_delivery.py
    - tests/test_phase11_github_sync.py
    - tests/test_project_delivery_pipeline_bootstrap.py
    - tests/test_project_delivery_pipeline_resume.py

key-decisions:
  - "Treat a healthy `gh auth status` session as a valid GitHub auth source when token env vars are absent."
  - "Resolve repository owner at the controller layer and never fall back to project_slug as the owner."
  - "Persist auth-source details and canonical repository metadata into shipping.github for operator-visible evidence."

patterns-established:
  - "GitHub helper returns explicit auth_source/auth_source_details alongside standard blocked-result behavior."
  - "Approved-delivery controller normalizes repository owner/name/url once, then reuses that canonical shape across fresh and resumed runs."

requirements-completed: [GHAUTH-01, GHAUTH-02, GHOWN-01, GHOWN-02]

# Metrics
duration: unknown
completed: 2026-04-29
---

# Phase 14: github-auth-and-repository-target-resolution Summary

**Approved-project delivery now accepts authenticated gh CLI sessions and persists canonical GitHub repository identity without slug-as-owner fallback.**

## Performance

- **Duration:** unknown
- **Started:** unknown
- **Completed:** 2026-04-29T12:15:03Z
- **Tasks:** 3
- **Files modified:** 5

## Accomplishments
- Added helper-level GitHub auth resolution that accepts `GH_TOKEN`, `GITHUB_TOKEN`, or a healthy `gh auth status` session.
- Added controller-side canonical repository owner/name/url resolution for bootstrap and resume flows without falling back to `project_slug` as owner.
- Extended authority metadata and regression coverage so repository preparation records auth-source details and canonical GitHub identity.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add red tests for GitHub auth-source and repository-identity resolution** - `not committed` (test)
2. **Task 2: Implement layered GitHub auth-source resolution in the helper layer** - `not committed` (fix)
3. **Task 3: Implement canonical repository identity resolution in the controller layer** - `not committed` (fix)

**Plan metadata:** `121061f` (pre-existing HEAD before this plan run)

_Note: This execution did not create local commits in the current session._

## Files Created/Modified
- `scripts/github_delivery_common.py` - Accepts env-token or gh-cli auth and records auth-source evidence for repository preparation.
- `scripts/start_approved_project_delivery.py` - Resolves canonical GitHub owner/name/url and persists prepare metadata into `shipping.github` across bootstrap and resume flows.
- `tests/test_phase11_github_sync.py` - Covers env-token auth, gh-cli auth fallback, and helper-level repository preparation evidence.
- `tests/test_project_delivery_pipeline_bootstrap.py` - Verifies bootstrap persists canonical repository identity and prepare metadata.
- `tests/test_project_delivery_pipeline_resume.py` - Verifies resume flows preserve or repair canonical GitHub metadata.

## Decisions Made
- Used `gh auth status` as the CLI-session probe instead of requiring exported token env vars.
- Kept repository-name fallback conservative while hard-blocking owner fallback to `project_slug`.
- Persisted auth-source details in authority metadata so operator-visible evidence explains why repository preparation succeeded.

## Deviations from Plan

### Auto-fixed Issues

**1. [Execution fix] Bootstrap persistence path expected mocked helper metadata keys**
- **Found during:** Task 3 (controller implementation)
- **Issue:** bootstrap test fixtures returned `prepare_*` keys while the real helper returns `evidence_path` and `auth_source`, leaving one mocked path without persisted metadata.
- **Fix:** taught the controller success path to preserve either helper naming shape and updated the targeted bootstrap fixture to include auth-source metadata.
- **Files modified:** `scripts/start_approved_project_delivery.py`, `tests/test_project_delivery_pipeline_bootstrap.py`
- **Verification:** `python -m unittest tests.test_project_delivery_pipeline_bootstrap.ApprovedDeliveryBootstrapTests.test_bundle_written_to_custom_root_bootstraps_without_brief_generation_block -v`
- **Committed in:** not committed

---

**Total deviations:** 1 auto-fixed
**Impact on plan:** Necessary for correctness of the controller persistence path and kept fully within Phase 14 scope.

## Issues Encountered
- Initial controller persistence updates missed one mocked bootstrap path that asserted `prepare_auth_source`; this was corrected and re-verified.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- GitHub repository preparation now accepts the real operator auth path and hands canonical repository identity into downstream GitHub sync work.
- Phase 15 can build on stable `shipping.github` metadata and explicit prepare evidence without revisiting owner/auth detection.

---
*Phase: 14-github-auth-and-repository-target-resolution*
*Completed: 2026-04-29*
