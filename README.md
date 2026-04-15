# profit-corp-hermes

Hermes-native full migration target for `profit-corp`.

This repo keeps original `profit-corp` unchanged, and runs the system with:
- **5 persistent profiles**: `ceo/scout/cmo/arch/accountant`
- **Cron-first orchestration**
- **Memory + Skills self-learning** with guardrails
- **Formal state contract** for stable operations

## Structure
- `assets/shared/` — ledger, templates, governance artifacts
- `assets/workspaces/` — role prompts and identity assets
- `profiles/` — per-role config templates + SOUL files
- `orchestration/cron/` — cron prompts and command helpers
- `scripts/` — bootstrap, smoke test, and recovery scripts
- `docs/` — migration, runbook, coordination, state contract, guardrails, operations
- `docs/skill-governance/` — skill 标准化治理文档（playbook/routing/release/templates）

## Quick start (Linux)
```bash
bash scripts/bootstrap_hermes.sh
```

Skip optional stages when needed:
```bash
bash scripts/bootstrap_hermes.sh --skip-cron --skip-smoke --skip-migration --skip-doctor
```

## Quick start (Windows PowerShell)
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_hermes.ps1
```

Skip optional stages when needed:
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_hermes.ps1 -SkipCron -SkipSmoke -SkipMigration
```

## Skills registration (project -> Hermes profiles)
Project skill source:
- `skills/common/` (available to all profiles)
- `skills/ceo/` (CEO-specific directives)

Bootstrap now syncs these into `~/.hermes/profiles/<role>/skills/` with overwrite confirmation.

## One-pass test flow
1. Bootstrap and sync skills:
   - Linux: `bash scripts/bootstrap_hermes.sh --skip-smoke`
   - Windows: `powershell -ExecutionPolicy Bypass -File .\\scripts\\bootstrap_hermes.ps1 -SkipSmoke -SkipMigration`
2. Verify profile skills folders contain synced files.
3. Trigger CEO command skills (`new_project`, `daily_pipeline`, `revenue/bounty with confirm`).
4. Verify announcement read/write via `skills/ceo/ceo_publish_announcement.md` + `skills/common/read_shareholder_announcements.md`.
5. Validate ledger read/write policy (`read_ledger` for all roles, writes only through `manage_finance.py`).
6. Run regression checks:
   - `bash scripts/smoke_test_pipeline.sh`
   - `bash scripts/recover_cron.sh`
   - `bash orchestration/cron/commands.sh ensure`
   - `hermes -p ceo cron list`

## Core ops commands
```bash
bash scripts/smoke_test_pipeline.sh
bash scripts/recover_cron.sh
bash orchestration/cron/commands.sh ensure
```

## Key docs
- `docs/MIGRATION_OPENCLAW_TO_HERMES.md`
- `docs/RUNBOOK_LINUX.md`
- `docs/MULTI_PROFILE_COORDINATION.md`
- `docs/STATE_CONTRACT.md`
- `docs/SELF_LEARNING_GUARDRAILS.md`
- `docs/OPERATIONS.md`
- `docs/skill-governance/README.md`
