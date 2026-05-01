# profit-corp-hermes

Hermes-native full migration target for `profit-corp`.

This repo is not just a planner or signal collector anymore. It is the full operating path for:
- **company-level intelligence and governance**
- **web-wide pain-point discovery**
- **decision-package generation**
- **approved-project bundle creation**
- **governed multi-stage product delivery**
- **GitHub / Vercel release automation**
- **operator-visible final handoff and validation**

## Architecture at a glance

Profit-Corp Hermes now has **two layers of organization**, not just one flat set of roles.

### 1. Company decision layer
These are the long-lived Hermes company roles:
- `ceo` — final decision maker and orchestrator
- `scout` — pain-point discovery and signal collection
- `cmo` — market framing and commercialization angle
- `arch` — technical framing and build-shape judgment
- `accountant` — finance, audit, and operating risk control

This layer is responsible for:
- discovering real pain signals from the web
- turning them into ranked opportunities
- producing market / technical / operating decision artifacts
- deciding which opportunities are worth greenlighting
- governing financial and operational risk

### 2. Product delivery layer
Once an opportunity is approved, execution no longer relies on a single `arch` role doing everything. It moves into a **specialist delivery team / orchestrated delivery pipeline** with these stages:
- design
- development
- testing
- git versioning
- release readiness

This layer is responsible for:
- taking an approved project bundle as input
- instantiating a governed workspace from the shared SaaS template
- preserving stage handoffs and evidence
- shipping through GitHub and Vercel
- producing final operator-facing handoff artifacts

So the current system is:
- **company roles for judgment**
- **delivery team for execution**

`arch` still exists, but it is now one role inside the company decision layer — it is **not** the entire development system anymore.

## What this system does

Profit-Corp Hermes continuously discovers user pain points from public discussions, turns them into role-specific operating artifacts, and can then push an approved opportunity all the way through governed mini-SaaS delivery.

The main artifact chain is:
1. external signals → prioritized shortlist
2. `PAIN_POINTS.md` / `MARKET_PLAN.md` / `TECH_SPEC.md` / `CEO_RANKING.md`
3. `OPERATING_DECISION_PACKAGE.md` + execution/board derivatives
4. `assets/shared/approved-projects/<project>/APPROVED_PROJECT.json`
5. workspace bootstrap → GitHub sync → Vercel deploy → final handoff

## Repo structure
- `assets/shared/` — ledger, intelligence outputs, decision packages, approved-project bundles, governance artifacts
- `assets/workspaces/` — role prompts and identity assets
- `profiles/` — per-role config templates + SOUL files
- `orchestration/cron/` — cron prompts and command helpers
- `scripts/` — bootstrap, signal analysis, delivery, smoke test, and recovery scripts
- `docs/` — migration, runbooks, state contract, operations, guardrails
- `docs/skill-governance/` — skill 标准化治理文档

## Evolution by milestone

### v1.0 — Operating intelligence core
- established the multi-role Hermes company core
- built external signal intake, triage, and role handoff generation
- shipped operating decision packages, execution handoffs, governance, and operator visibility

### v1.1 — SaaS delivery factory
- promoted `standalone-saas-template` into a governed platform asset
- added approved-project bundles as the handoff from decision to build
- introduced the specialist delivery team / delivery orchestrator stages
- shipped governed GitHub sync, Vercel deployment, and final delivery handoff

### v1.1.1 — Delivery reliability fixes
- repaired GitHub auth, repo targeting, and workspace sync reliability
- repaired Vercel auth, scope handling, and deploy metadata persistence
- tightened authority / status / review / validator truth convergence
- improved workspace restore and delivery regression coverage

For a user-facing version log, see `CHANGELOG.md`.

## Quick start

### Linux / macOS / Git Bash
```bash
bash scripts/bootstrap_hermes_noninteractive.sh
```

### Windows PowerShell
```powershell
powershell -ExecutionPolicy Bypass -File .\scripts\bootstrap_hermes.ps1
```

If you only want to resync profiles/skills without rebuilding cron:
```bash
SETUP_PROFILES=1 SETUP_CRON=0 RUN_SMOKE_TEST=0 bash scripts/bootstrap_hermes_noninteractive.sh
```

## First-use validation path

### 1. Verify Hermes runtime
```bash
bash scripts/smoke_test_pipeline.sh
bash orchestration/cron/commands.sh ensure
bash orchestration/cron/commands.sh status
```

### 2. Run pain-point discovery and role artifacts
```bash
bash scripts/run_external_intelligence.sh
bash scripts/run_signal_analysis_loop.sh --window-hours 48 --limit 3
```

This should refresh:
- `assets/shared/PAIN_POINTS.md`
- `assets/shared/MARKET_PLAN.md`
- `assets/shared/TECH_SPEC.md`
- `assets/shared/CEO_RANKING.md`
- `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`

### 3. Build or inspect an approved project bundle
For an existing bundle, inspect:
```bash
more assets/shared/approved-projects/<project>/APPROVED_PROJECT.json
more assets/shared/approved-projects/<project>/PROJECT_BRIEF.md
```

To generate a new bundle from the current operating decision package:
```bash
python scripts/start_approved_project_delivery.py --approval-mode decision-package --decision-package-path assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md
```

### 4. Run governed delivery
```bash
bash orchestration/cron/commands.sh start-approved-delivery assets/shared/approved-projects/<project>/APPROVED_PROJECT.json
bash orchestration/cron/commands.sh render-approved-delivery-status assets/shared/approved-projects/<project>
bash orchestration/cron/commands.sh validate-approved-delivery-pipeline assets/shared/approved-projects/<project>
```

If blocked, inspect status first, fix the prerequisite, then resume:
```bash
bash orchestration/cron/commands.sh resume-approved-delivery assets/shared/approved-projects/<project>/APPROVED_PROJECT.json
```

## Delivery prerequisites

Before real deploy validation, make sure the operator machine has:
- authenticated `gh` CLI session or exported GitHub token
- authenticated Vercel CLI session or `VERCEL_TOKEN`
- project-local PayPal / Supabase env values available through Claude local settings or shell env

Do **not** commit secrets into repo files. Keep them in local environment/config only.

## Skills registration (project -> Hermes profiles)
Project skill source:
- `skills/common/` (available to all profiles)
- `skills/ceo/` (CEO-specific directives)

核心运行时规范技能（已激活到 `skills/common/`）：
- `feature_planning`
- `bugfix_safety`
- `observability_check`
- `migration_safety`
- `release_readiness`
- `test_strategy_planner`
- `regression_planner`
- `release_verification`
- `rollback_decision_policy`

完整规范库请查看：`skills/library/normalized/`。

Bootstrap 会把这些同步到 `~/.hermes/profiles/<role>/skills/`。

## Core ops commands
```bash
bash scripts/smoke_test_pipeline.sh
bash scripts/recover_cron.sh
bash orchestration/cron/commands.sh ensure
bash orchestration/cron/commands.sh run-daily
```

## Key docs
- `CHANGELOG.md` — milestone-based version history
- `docs/OPERATIONS.md` — operator runbook, including approved delivery
- `docs/MIGRATION_OPENCLAW_TO_HERMES.md`
- `docs/RUNBOOK_LINUX.md`
- `docs/MULTI_PROFILE_COORDINATION.md`
- `docs/STATE_CONTRACT.md`
- `docs/SELF_LEARNING_GUARDRAILS.md`
- `docs/skill-governance/README.md`
