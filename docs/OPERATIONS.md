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

## Recovery mode
If Hermes workflow is unstable:
1. Pause cron jobs (`pause-all`).
2. Execute manual CEO-driven run (`run-daily`) after checks.
3. Restore baseline with `recover_cron.sh`.
4. Re-run smoke test before returning to unattended operation.
