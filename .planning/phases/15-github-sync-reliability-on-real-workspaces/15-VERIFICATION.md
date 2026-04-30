---
status: passed
phase: 15-github-sync-reliability-on-real-workspaces
verified_at: 2026-04-29T14:42:00Z
requirements:
  - GHSYNC-01
  - GHSYNC-02
  - GHSYNC-03
  - GHSYNC-04
  - GHSYNC-05
---

# Phase 15 Verification

## Goal

Make GitHub sync succeed on the real Windows + pnpm generated workspace shape by fixing snapshot filtering, remote convergence, and transport behavior.

## Result

PASS

## Verified must-haves

### GHSYNC-01 / GHSYNC-02
- `scripts/github_delivery_common.py` now stages an explicit source-only snapshot instead of whole-workspace `git add -A`.
- Generated directories such as `node_modules`, `.next`, `dist`, `build`, `coverage`, `.turbo`, and related caches are excluded from the canonical sync snapshot.
- `tests/test_phase11_github_sync.py` verifies generated artifacts are not staged and that snapshot evidence is recorded.

### GHSYNC-03 / GHSYNC-04
- `scripts/github_delivery_common.py` now converges missing or mismatched remotes before branch/push work proceeds.
- Push behavior can retry through SSH when HTTPS is not the operator-working transport, while preserving explicit `push_attempts` evidence.
- `tests/test_phase11_github_sync.py` verifies remote convergence and HTTPS→SSH fallback behavior.

### GHSYNC-05
- `scripts/github_delivery_common.py` now writes step-specific sync diagnostics such as `failed_step`, `attempted_command`, `remote_action`, and `push_attempts`.
- `scripts/start_approved_project_delivery.py` persists downstream-relevant sync metadata into `shipping.github`.
- `tests/test_project_delivery_pipeline_bootstrap.py`, `tests/test_project_delivery_pipeline_resume.py`, and `tests/test_phase12_credential_governance.py` verify persistence and governance compatibility for refined sync evidence.

## Evidence

### Automated suites passed
- `python -m unittest tests.test_phase11_github_sync -v`
- `python -m unittest tests.test_project_delivery_pipeline_bootstrap tests.test_project_delivery_pipeline_resume -v`
- `python -m unittest tests.test_phase11_github_sync tests.test_project_delivery_pipeline_bootstrap tests.test_project_delivery_pipeline_resume tests.test_phase12_credential_governance -v`

### Review artifact
- `.planning/phases/15-github-sync-reliability-on-real-workspaces/15-REVIEW.md`

### Summaries present
- `.planning/phases/15-github-sync-reliability-on-real-workspaces/15-01-SUMMARY.md`
- `.planning/phases/15-github-sync-reliability-on-real-workspaces/15-02-SUMMARY.md`
- `.planning/phases/15-github-sync-reliability-on-real-workspaces/15-03-SUMMARY.md`

## Notes

- Dedicated executor / reviewer subagents were unavailable in this session because of runtime model-channel failures, so execution closeout, review, and verification were completed directly in the main session against the live codebase and passing tests.
- Manual-only live operator verification from `15-VALIDATION.md` still remains useful for real Windows + pnpm path depth and local transport setup, but the phase’s automated requirements contract is satisfied.

## Result Summary

**Phase 15 passes verification.**
