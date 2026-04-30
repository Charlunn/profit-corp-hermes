---
phase: 16-vercel-auth-and-deploy-reliability
reviewed: 2026-04-29T00:00:00Z
depth: standard
files_reviewed: 8
files_reviewed_list:
  - scripts/vercel_delivery_common.py
  - tests/test_phase11_vercel_flow.py
  - scripts/start_approved_project_delivery.py
  - scripts/validate_approved_delivery_pipeline.py
  - tests/test_project_delivery_pipeline_bootstrap.py
  - tests/test_project_delivery_pipeline_resume.py
  - scripts/approved_delivery_governance.py
  - tests/test_phase12_credential_governance.py
findings:
  critical: 0
  warning: 4
  info: 0
  total: 4
status: issues_found
---

# Phase 16: Code Review Report

**Reviewed:** 2026-04-29T00:00:00Z
**Depth:** standard
**Files Reviewed:** 8
**Status:** issues_found

## Summary

Reviewed the Phase 16 Vercel auth/deploy reliability changes across helper, controller, validator, and governance seams. The main risks are pipeline resume-state corruption around the Vercel boundary, validator logic that still infers success from metadata instead of authoritative evidence, and governance events that snapshot stale shipping state.

## Warnings

### WR-01: Successful GitHub sync advances resume pointer past Vercel linkage

**File:** `scripts/start_approved_project_delivery.py:1358-1365`
**Issue:** After a successful `github_sync`, the pipeline state is set to `stage="vercel_linkage"` but `resume_from_stage="vercel_deploy"`. If the process stops here and is later resumed, `resume_approved_project_delivery()` will skip the actual linkage step and jump straight to deploy, even though the record is only at the pending-linkage state.
**Fix:** Keep the resume pointer aligned with the current pending stage until linkage actually succeeds.

```python
update_pipeline_state(
    record,
    stage="vercel_linkage",
    status="ready",
    workspace_path=workspace.as_posix(),
    delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
    resume_from_stage="vercel_linkage",
)
```

### WR-02: Fresh-run short-circuit can return from `vercel_linkage` without linking anything

**File:** `scripts/start_approved_project_delivery.py:1380-1389`
**Issue:** When `run_pipeline_from_stage()` reaches `vercel_linkage` from any earlier stage in the same run, it immediately returns success without calling `link_vercel_project()`. Combined with the incorrect resume pointer above, a normal bootstrap can stop at a "ready" linkage stage that never performed Vercel linking or env setup.
**Fix:** Only short-circuit when the caller explicitly wants to stop before linkage. Otherwise execute `link_vercel_project()` before returning success, or leave `resume_from_stage` at `vercel_linkage` and treat the stage as pending rather than completed work.

### WR-03: Validator still infers Vercel success from metadata instead of authoritative evidence

**File:** `scripts/validate_approved_delivery_pipeline.py:251-270`
**Issue:** `has_link_success` and `has_deploy_success` become true when fields like `project_name`, `team_scope`, `deploy_url`, or `deploy_status` are present, even if no success evidence path exists. That contradicts the Phase 16 authority-first rule and can misclassify stale or manually-inserted metadata as authoritative success.
**Fix:** Gate success checks on persisted success evidence such as `link_evidence_path`, `env_contract_path`/`env_contract.evidence_path`, and `deploy_evidence_path`/`deployment_evidence_path`, then validate the accompanying metadata only when that evidence exists.

### WR-04: Governance events persist pre-action shipping state instead of the action result

**File:** `scripts/approved_delivery_governance.py:384-401`
**Issue:** `_append_event()` writes `shipping` from the pre-action authority record. For governed Vercel actions, that means the appended event can omit the just-produced `project_url`, `team_scope`, `auth_source`, and `auth_source_details`, even though the audit artifact already has them. Event consumers reading `shipping` get stale data.
**Fix:** Merge action-result fields into the event shipping snapshot before appending, especially for the GitHub and Vercel action families.

---

_Reviewed: 2026-04-29T00:00:00Z_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
