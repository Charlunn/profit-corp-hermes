---
phase: 16-vercel-auth-and-deploy-reliability
plan: 02
subsystem: testing
tags: [python, unittest, vercel, delivery-pipeline, authority-record]
requires:
  - phase: 16-01
    provides: Vercel auth-source resolution and failure taxonomy used by delivery helpers
provides:
  - Authoritative-only Vercel persistence coverage at bootstrap and resume boundaries
  - Controller persistence rules that avoid prewriting successful Vercel metadata before real link/deploy success
  - Validator rules that require Vercel linkage and deploy fields only when success evidence exists
affects: [phase-16, approved-delivery, vercel, status-validation]
tech-stack:
  added: []
  patterns: [authority-first persistence, success-gated validation, resume-time metadata replacement]
key-files:
  created: []
  modified:
    - scripts/start_approved_project_delivery.py
    - scripts/validate_approved_delivery_pipeline.py
    - tests/test_project_delivery_pipeline_bootstrap.py
    - tests/test_project_delivery_pipeline_resume.py
key-decisions:
  - "Treat Vercel project, scope, URL, and deploy fields as authoritative only after governed helper success returns them."
  - "Keep Phase 16 validator scope limited to success-gated presence checks instead of redesigning historical truth precedence."
patterns-established:
  - "Authority-first persistence: transient Vercel candidate inputs may guide helper calls but cannot be written into shipping.vercel before success."
  - "Resume convergence: resumed deliveries must overwrite stale Vercel metadata with current-run truth and evidence."
requirements-completed: [VERC-03, VERC-04]
duration: 18min
completed: 2026-04-29
---

# Phase 16 Plan 02: Vercel authority-truth convergence Summary

**Approved-delivery now records Vercel project and deploy metadata only after real governed success, while resume and validation surfaces converge on current-run evidence instead of stale defaults.**

## Performance

- **Duration:** 18 min
- **Started:** 2026-04-29T14:56:44Z
- **Completed:** 2026-04-29T15:14:44Z
- **Tasks:** 3
- **Files modified:** 4

## Accomplishments
- Added controller-boundary regression coverage that forbids prewritten Vercel success metadata after `github_sync` and verifies resume-time replacement of stale fields.
- Hardened `start_approved_project_delivery.py` so Vercel candidate inputs remain transient until governed link and deploy helpers return real success payloads.
- Tightened `validate_approved_delivery_pipeline.py` so operator-facing validation requires Vercel linkage and deploy fields only when authoritative success evidence is actually present.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add red controller tests for authoritative-only Vercel metadata persistence and resume convergence** - `6e23fc2` (test)
2. **Task 2: Remove prewritten Vercel authority defaults and persist current-run metadata/evidence only after success** - `20a8cd7` (fix)
3. **Task 3: Tighten status and validator consumers around authoritative Vercel metadata/evidence** - `b1112cb` (fix)

## Files Created/Modified
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\tests\test_project_delivery_pipeline_bootstrap.py` - Adds assertions that `github_sync` advances to `vercel_linkage` without claiming linked Vercel project truth.
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\tests\test_project_delivery_pipeline_resume.py` - Covers stale-metadata replacement on resume and completed-handoff no-replay behavior.
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\start_approved_project_delivery.py` - Removes prewritten Vercel success fields, persists auth/evidence only from real helper success, and tightens deploy gating.
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\validate_approved_delivery_pipeline.py` - Requires Vercel metadata and deploy linkage only when authoritative success evidence exists.

## Decisions Made
- Persisted `auth_source`, `auth_source_details`, link evidence, env-contract evidence, and deploy evidence only from successful governed helper results.
- Preserved Phase 16 scope by leaving `scripts/render_approved_delivery_status.py` unchanged because it already renders persisted Vercel fields without inferring defaults.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed validator mismatch after authority-write hardening**
- **Found during:** Task 3 (Tighten status and validator consumers around authoritative Vercel metadata/evidence)
- **Issue:** The validator still required Vercel project fields whenever `shipping.vercel` existed, which broke valid blocked/resume states that no longer prewrite successful metadata.
- **Fix:** Reworked `validate_vercel_linkage` to gate required link/deploy fields on actual success evidence and persisted deploy state.
- **Files modified:** `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\validate_approved_delivery_pipeline.py`
- **Verification:** `python -m unittest discover -s "C:/Users/42236/Desktop/dev/profit-corp-hermes/tests" -p "test_project_delivery_pipeline_bootstrap.py" -v`
- **Committed in:** `b1112cb`

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** The auto-fix was required to keep validator behavior aligned with the new authoritative-only persistence rule. No scope creep.

## Issues Encountered
- Direct `python -m unittest tests...` module invocation was not reliable in this environment, so verification used `unittest discover` against the same target files.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- Phase 16-02 is green against bootstrap, resume, and Vercel helper regressions.
- Downstream Phase 16 work can build on the invariant that `shipping.vercel` reflects only current authoritative success truth.

## Self-Check: PASSED
- Found: `C:\Users\42236\Desktop\dev\profit-corp-hermes\.planning\phases\16-vercel-auth-and-deploy-reliability\16-02-SUMMARY.md`
- Found commit: `6e23fc2`
- Found commit: `20a8cd7`
- Found commit: `b1112cb`
