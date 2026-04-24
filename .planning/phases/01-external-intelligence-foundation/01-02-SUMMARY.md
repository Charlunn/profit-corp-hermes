---
phase: 01-external-intelligence-foundation
plan: 02
subsystem: data
tags: [python, external-intelligence, rss, html, jsonl, ingestion]
requires:
  - phase: 01-01
    provides: source registry, normalized schema contract, storage layout
provides:
  - Registry-driven collector CLI
  - Normalized signal history persistence
  - Raw artifact capture and dedupe-safe reruns
affects: [phase-1-cron-wiring, phase-2-triage, phase-3-decision-packages]
tech-stack:
  added: [python collector script]
  patterns: [registry-driven ingestion, append-only jsonl history, raw evidence capture]
key-files:
  created: [scripts/collect_external_signals.py, assets/shared/external_intelligence/history/.gitkeep, assets/shared/external_intelligence/raw/.gitkeep]
  modified: []
key-decisions:
  - "Support only deterministic rss/page source kinds in Phase 1 to avoid brittle authenticated scraping."
  - "Keep YAML loading dependency-optional by falling back to a minimal parser when PyYAML is unavailable."
patterns-established:
  - "Collector persists raw payloads separately from normalized signal history."
  - "Duplicate detection is keyed by deterministic signal_id derived from URL, title, and published timestamp."
requirements-completed: [SIGN-01, SIGN-02, SIGN-03, ANLY-01]
duration: 20min
completed: 2026-04-24
---

# Phase 1: External Intelligence Foundation Summary

**Registry-driven public-source collector with normalized signal IDs, raw evidence capture, and append-only run history**

## Performance

- **Duration:** 20 min
- **Started:** 2026-04-24T09:22:00Z
- **Completed:** 2026-04-24T09:42:00Z
- **Tasks:** 3
- **Files modified:** 3

## Accomplishments
- Added a Python collector CLI that reads the checked-in source registry and supports `--window-hours`, `--dry-run`, and `--source-id`.
- Implemented normalized records, raw payload persistence, and append-only `signals.jsonl` / `runs.jsonl` history paths.
- Added deterministic `rss` and `page` adapters with duplicate-safe rerun behavior.

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the registry-driven collector entrypoint** - `ed6d5c7` (feat)
2. **Task 2: Implement normalization and evidence-preserving persistence** - `ed6d5c7` (feat)
3. **Task 3: Support the first category-specific adapters and dedupe-safe reruns** - `ed6d5c7` (feat)

**Plan metadata:** `ed6d5c7` (docs: complete plan)

## Files Created/Modified
- `scripts/collect_external_signals.py` - External intelligence collector with registry loading, fetching, normalization, dedupe, and run reporting
- `assets/shared/external_intelligence/history/.gitkeep` - Commits the normalized history directory structure
- `assets/shared/external_intelligence/raw/.gitkeep` - Commits the raw evidence directory structure

## Decisions Made
- Used the Hermes-managed Python interpreter for validation because the system `python3` alias resolves to the Windows Store shim in this environment.
- Allowed dry runs with zero enabled sources so the operator can validate wiring before approving live URLs.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
- `python3 -m py_compile` initially failed because the shell-resolved `python3` alias pointed at the Windows app-execution stub rather than a real interpreter.
- Resolved by validating with `C:/Users/42236/AppData/Local/hermes/hermes-agent/venv/Scripts/python`, which is available in this repo environment.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- Plan 03 can now wrap `scripts/collect_external_signals.py` in shell/cron entrypoints and add smoke checks.
- Live collection still requires enabling approved source URLs in `assets/shared/external_intelligence/SOURCES.yaml`.

---
*Phase: 01-external-intelligence-foundation*
*Completed: 2026-04-24*
