# Profit-Corp Hermes Linux Runbook

## 0) Windows PowerShell bootstrap
```powershell
cd C:\path\to\profit-corp-hermes
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_hermes.ps1
```

Optional flags:
- `-SkipProfiles` skip profile creation/sync
- `-SkipCron` skip cron job ensure
- `-SkipSmoke` skip `scripts/smoke_test_pipeline.sh`

## 1) Configure cloud delivery shortcut
```bash
cd /path/to/profit-corp-hermes
python scripts/configure_hermes_cloud.py
```

The configurator prompts for:
- Hermes provider/base URL/API key/default model
- whether to apply that Hermes model block to all role profiles
- Claude Code relay base URL/token/model
- Supabase, GitHub, and Vercel delivery env values

It writes secrets only into local operator files ignored by git.

## 2) Bootstrap
```bash
cd /path/to/profit-corp-hermes
bash scripts/bootstrap_hermes.sh
```

Optional flags:
- `--skip-profiles` skip profile creation/sync
- `--skip-cron` skip cron job ensure
- `--skip-smoke` skip `scripts/smoke_test_pipeline.sh`
- `--skip-migration` skip `hermes claw migrate --dry-run` prompt
- `--skip-doctor` skip `hermes doctor` and sanity checks

Bootstrap does:
1. Verify prerequisites (`bash`, `git`, `curl`, `python3` or `python`)
2. Install Hermes if needed
3. Sync default config (`~/.hermes/config.yaml`)
4. Create/sync profiles (`ceo/scout/cmo/arch/accountant`) + sync project skills
5. Optional `hermes claw migrate --dry-run`
6. Ensure cron jobs from `orchestration/cron/`
7. Run smoke checks + doctor + finance syntax check

## 3) CI/VPS shortcut
```bash
cd /path/to/profit-corp-hermes
python scripts/configure_hermes_cloud.py --skip-checks
bash scripts/bootstrap_hermes.sh --skip-migration
```

## 4) Skills sync & verification
Project skill source:
- `skills/common/` -> sync to all profiles
- `skills/ceo/` -> sync to CEO profile

Runtime core standards in `skills/common/`:
- `feature_planning`
- `bugfix_safety`
- `observability_check`
- `migration_safety`
- `release_readiness`
- `test_strategy_planner`
- `regression_planner`
- `release_verification`
- `rollback_decision_policy`

Full standards library (for staged promotion):
- `skills/library/normalized/`

Governance reference:
- `docs/skill-governance/README.md`

Check synced skills:
```bash
ls ~/.hermes/profiles/ceo/skills
ls ~/.hermes/profiles/scout/skills
ls ~/.hermes/profiles/cmo/skills
ls ~/.hermes/profiles/arch/skills
ls ~/.hermes/profiles/accountant/skills
```

Validate command-skill behavior:
- `ceo_new_project`
- `ceo_daily_pipeline`
- `ceo_revenue_with_confirm`
- `ceo_bounty_with_confirm`

Validate announcement board:
- publish via `ceo_publish_announcement`
- read via `read_shareholder_announcements`

## 4) Multi-profile lifecycle
```bash
hermes profile list
hermes profile use ceo
ceo chat
scout chat
```

## 5) Gateway
Use CEO profile as external entrypoint:
```bash
ceo gateway setup
ceo gateway run
```

## 6) Cron operations
```bash
bash orchestration/cron/commands.sh ensure
bash orchestration/cron/commands.sh list
bash orchestration/cron/commands.sh status
bash orchestration/cron/commands.sh run-daily
```

## 7) Recovery & smoke test
```bash
bash scripts/smoke_test_pipeline.sh
bash scripts/recover_cron.sh
```

## 8) Sanity checks
```bash
hermes doctor
hermes profile list
hermes -p ceo cron list
python3 -m py_compile assets/shared/manage_finance.py
```

## 9) Rollback
Keep using original `profit-corp` if needed; this repo is parallel and non-destructive.
