# Profit-Corp Hermes Operations

## Daily operator checklist
1. Ensure cron baseline is healthy:
   ```bash
   bash orchestration/cron/commands.sh ensure
   bash orchestration/cron/commands.sh status
   ```
2. Verify scheduled jobs and recent outputs:
   ```bash
   hermes -p ceo cron list
   ```
3. Run regression smoke checks:
   ```bash
   bash scripts/smoke_test_pipeline.sh
   ```
4. Verify financial state integrity:
   ```bash
   python3 -m py_compile assets/shared/manage_finance.py
   ```
5. Review treasury and low-point agents in `assets/shared/LEDGER.json`.

## Incident handling

### A) Treasury falls below threshold
- Trigger immediate audit:
  ```bash
  hermes -p ceo chat -q "Run accountant audit and produce 3 urgent actions"
  ```
- Apply corrective actions and record rationale in `assets/shared/CORP_CULTURE.md`.
- If state conflict is suspected, follow `docs/STATE_CONTRACT.md` conflict rules before any write.

### B) Cron job missing, duplicated, or paused
- One-command recovery path:
  ```bash
  bash scripts/recover_cron.sh
  ```
- Manual controls (when needed):
  ```bash
  bash orchestration/cron/commands.sh ensure
  bash orchestration/cron/commands.sh remove-duplicates
  bash orchestration/cron/commands.sh resume-all
  bash orchestration/cron/commands.sh status
  ```
- If corruption persists, rebuild jobs:
  ```bash
  bash orchestration/cron/commands.sh recreate
  ```

### C) Profile config drift
- Resync profiles from templates:
  ```bash
  SETUP_PROFILES=1 SETUP_CRON=0 RUN_SMOKE_TEST=0 bash scripts/bootstrap_hermes_noninteractive.sh
  ```
- Validate after resync:
  ```bash
  hermes profile list
  bash scripts/smoke_test_pipeline.sh
  ```

### D) State write conflict or abnormal transition
- Pause automatic writes for investigation:
  ```bash
  bash orchestration/cron/commands.sh pause-all
  ```
- Inspect last produced artifacts and ownership chain per `docs/MULTI_PROFILE_COORDINATION.md`.
- For governed high-impact actions, inspect `assets/shared/governance/GOVERNANCE_STATUS.md` and `assets/shared/governance/governance_events.jsonl` before retrying.
- Resume after conflict resolution:
  ```bash
  bash orchestration/cron/commands.sh resume-all
  ```

### E) Governance-blocked high-impact action
- Review latest governance state:
  ```bash
  python scripts/render_governance_status.py --dry-run
  ```
- Create or inspect approval state with:
  ```bash
  python scripts/request_governance_approval.py --help
  ```
- Only run protected actions through the governed wrapper:
  ```bash
  bash orchestration/cron/commands.sh run-governed-action <action-id> <command...>
  ```
- Finance mutations remain authoritative through `assets/shared/manage_finance.py`; governance only decides whether they may proceed.

## Operating Visibility
- Read the latest operator surface first:
  ```bash
  python scripts/generate_operating_visibility.py
  ```
  Then inspect:
  ```bash
  more assets/shared/visibility/OPERATING_VISIBILITY.md
  ```
- Cron/operator entrypoint for the same artifact:
  ```bash
  bash orchestration/cron/commands.sh run-visibility
  ```
- Treat `assets/shared/visibility/OPERATING_VISIBILITY.md` as read-only. Do not edit it manually; always regenerate it from trusted artifacts.
- The view is intentionally calm by default: healthy runs stay compact, while blocked / pending / failed / stale conditions are promoted into `## Top Alerts`.
- The surface is limited to Top 3 next actions and is optimized for solo-operator focus. It is not a backlog, queue, or dashboard.
- Investigate alerts by following the cited source paths and trace IDs back to:
  - `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`
  - `assets/shared/governance/GOVERNANCE_STATUS.md`
  - `assets/shared/external_intelligence/LATEST_SUMMARY.md`
  - `assets/shared/trace/decision_package_trace.json`

## Self-learning operations policy
- Follow `docs/SELF_LEARNING_GUARDRAILS.md` as the source of truth.
- Follow `docs/skill-governance/README.md` for standardized skill governance and templates.
- Only promote stable, repeatedly successful workflows into skills.
- Do not persist transient failures, one-off tasks, or sensitive information into memory/skills.
- Prefer patch-style updates and keep rollback path for critical skills.

## Skills operations
- Project skill source-of-truth:
  - `skills/common/` (all profiles)
  - `skills/ceo/` (CEO directives)
- Runtime core standards already activated in `skills/common/`:
  - `feature_planning`
  - `bugfix_safety`
  - `observability_check`
  - `migration_safety`
  - `release_readiness`
  - `test_strategy_planner`
  - `regression_planner`
  - `release_verification`
  - `rollback_decision_policy`
- Full standards library remains in `skills/library/normalized/` for staged promotion.
- Bootstrap syncs skills into `~/.hermes/profiles/<role>/skills/`.
- During sync, overwrite requires explicit confirmation.
- After synced config overwrite, bootstrap runs interactive provider/model setup in-place.

Skill-level policy:
- `read_ledger` is read-only and available to all roles.
- Revenue/bounty mutations only via `manage_finance.py` skills with confirm gate.
- Announcement updates go through `ceo_publish_announcement` and must follow board maintenance rules.

## Approved project delivery pipeline

### Start an approved delivery run
- Start from the approved-project authority bundle, not ad-hoc workspace commands:
  ```bash
  bash orchestration/cron/commands.sh start-approved-delivery assets/shared/approved-projects/<project>/APPROVED_PROJECT.json
  ```
- This wrapper reuses the existing Phase 10 controller and keeps the authority layer above the workspace layer.

### Inspect latest status before any retry
- Read the persisted latest view first:
  ```bash
  bash orchestration/cron/commands.sh render-approved-delivery-status assets/shared/approved-projects/<project>
  more assets/shared/approved-projects/<project>/DELIVERY_PIPELINE_STATUS.md
  ```
- Confirm the status view shows stage, workspace path, block reason, blocked prerequisite evidence, delivery-run linkage, and final handoff linkage.

### Validate handoff completeness
- Prove the approval-to-handoff chain before declaring success:
  ```bash
  bash orchestration/cron/commands.sh validate-approved-delivery-pipeline assets/shared/approved-projects/<project>
  ```
- Validation cross-checks `APPROVED_PROJECT.json`, `PROJECT_BRIEF.md`, `approved-delivery-events.jsonl`, `DELIVERY_PIPELINE_STATUS.md`, workspace `.hermes/delivery-run-manifest.json`, conformance evidence, and `.hermes/FINAL_DELIVERY.md`.

### Resolve blocked downstream prerequisites, then resume
- If credential, deployment, or other downstream prerequisite evidence is missing, inspect the persisted block reason and linked evidence artifact in `DELIVERY_PIPELINE_STATUS.md` before acting.
- Phase 11 adds explicit staged helpers for repository/deployment progression when you need to inspect or re-run a single segment:
  ```bash
  bash orchestration/cron/commands.sh prepare-approved-delivery-github assets/shared/approved-projects/<project>/APPROVED_PROJECT.json
  bash orchestration/cron/commands.sh sync-approved-delivery-github assets/shared/approved-projects/<project>/APPROVED_PROJECT.json
  bash orchestration/cron/commands.sh link-approved-delivery-vercel assets/shared/approved-projects/<project>/APPROVED_PROJECT.json
  bash orchestration/cron/commands.sh deploy-approved-delivery-vercel assets/shared/approved-projects/<project>/APPROVED_PROJECT.json
  ```
- After the missing prerequisite is resolved, resume from persisted state instead of restarting from scratch:
  ```bash
  bash orchestration/cron/commands.sh resume-approved-delivery assets/shared/approved-projects/<project>/APPROVED_PROJECT.json
  ```
- Do not create a second workspace or rerun manual bootstrap steps unless the authority record explicitly tells you the original workspace path is invalid.

If Hermes workflow is unstable:
1. Pause cron jobs (`pause-all`).
2. Execute manual CEO-driven run (`run-daily`) after checks.
3. Restore baseline with `recover_cron.sh`.
4. Re-run smoke test before returning to unattended operation.
