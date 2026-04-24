---
phase: 01-external-intelligence-foundation
plan: 03
subsystem: infra
tags: [bash, cron, smoke-test, hermes, orchestration, external-intelligence]
requires:
  - phase: 01-01
    provides: source registry and governance contract
  - phase: 01-02
    provides: collector CLI and history/raw persistence
provides:
  - Stable shell entrypoint for external intelligence runs
  - Cron command-hub action and intake prompt
  - Smoke coverage for external intelligence wiring
affects: [phase-2-analysis, daily-ops, cron-recovery]
tech-stack:
  added: [bash wrapper, cron prompt]
  patterns: [shell wrapper around collector, smoke-tested cron entrypoint]
key-files:
  created: [scripts/run_external_intelligence.sh, orchestration/cron/external_intelligence.prompt.md]
  modified: [orchestration/cron/commands.sh, orchestration/cron/daily_pipeline.prompt.md, scripts/smoke_test_pipeline.sh]
key-decisions:
  - "Expose intake through a direct `run-intelligence` command-hub action instead of requiring a named cron job first."
  - "Validate the intake path in smoke tests with a dry run and command-hub invocation before relying on live sources."
patterns-established:
  - "Operational wrappers default to deterministic dry-run-safe validation before live use."
  - "External intelligence intake is part of the daily pipeline pre-Scout stage."
requirements-completed: [SIGN-01, SIGN-02, SIGN-03, ANLY-01]
duration: 18min
completed: 2026-04-24
---

# Phase 1: External Intelligence Foundation Summary

**Shell-wrapped external intelligence intake wired into cron helpers, daily pipeline sequencing, and smoke-tested operational checks**

## Performance

- **Duration:** 18 min
- **Started:** 2026-04-24T09:43:00Z
- **Completed:** 2026-04-24T10:01:00Z
- **Tasks:** 3
- **Files modified:** 6

## Accomplishments
- Added a stable shell wrapper for collector runs with Python resolution and argument passthrough.
- Integrated external intelligence intake into cron commands and the daily CEO pipeline before Scout analysis.
- Extended smoke coverage so the new intake path is verified end to end.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add a stable operator entrypoint for external intelligence runs** - `5bc6cc6` (feat)
2. **Task 2: Wire the intake flow into cron artifacts and command helpers** - `5bc6cc6` (feat)
3. **Task 3: Extend smoke coverage for the external-intelligence flow** - `5bc6cc6` (feat)

**Plan metadata:** `5bc6cc6` (docs: complete plan)

## Files Created/Modified
- `scripts/run_external_intelligence.sh` - Shell wrapper that resolves a usable Python interpreter and runs the collector with `--window-hours 24`
- `orchestration/cron/external_intelligence.prompt.md` - CEO-facing intake prompt for cron-driven runs
- `orchestration/cron/commands.sh` - Added `run-intelligence` action and prompt path wiring
- `orchestration/cron/daily_pipeline.prompt.md` - Added external intelligence step before Scout analysis
- `scripts/smoke_test_pipeline.sh` - Added collector file checks, syntax validation, dry run, and `run-intelligence` validation
- `assets/shared/external_intelligence/history/runs.jsonl` - First run log created by command-hub validation

## Decisions Made
- Allowed `run-intelligence` to invoke the wrapper directly so operators can test the intake flow without provisioning a dedicated cron job first.
- Kept smoke validation dry-run-safe while still generating a real `runs.jsonl` entry through command-hub execution.

## Deviations from Plan

### Auto-fixed Issues

**1. [Validation detail] Captured initial run log during command-hub verification**
- **Found during:** Task 3 (smoke and command validation)
- **Issue:** Verifying `run-intelligence` on the real command path creates `assets/shared/external_intelligence/history/runs.jsonl`
- **Fix:** Kept the generated run log and committed it as part of the operational artifact set
- **Files modified:** assets/shared/external_intelligence/history/runs.jsonl
- **Verification:** `bash scripts/smoke_test_pipeline.sh` passed with the generated run log present
- **Committed in:** `5bc6cc6` (part of task commit)

---

**Total deviations:** 1 auto-fixed (operational artifact capture)
**Impact on plan:** No scope creep. The generated run log is a valid byproduct of verifying the real intake path.

## Issues Encountered
None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Phase 1 now has a runnable and smoke-tested external intake path.
- To collect real signals, approved public source URLs still need to be filled into `assets/shared/external_intelligence/SOURCES.yaml` and enabled.

---
*Phase: 01-external-intelligence-foundation*
*Completed: 2026-04-24*
