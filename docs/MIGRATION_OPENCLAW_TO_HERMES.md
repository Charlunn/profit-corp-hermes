# OpenCLAW → Hermes Full Migration (profit-corp)

## Scope
`profit-corp-hermes` is the full Hermes-native migration target. Original `profit-corp` remains untouched for rollback.

## Target Architecture
- Multi-agent form: **5 persistent Hermes profiles** (`ceo/scout/cmo/arch/accountant`)
- Orchestration: **Hermes Cron first**
- Learning loop: **persistent memory + skill evolution (with guardrails)**
- State governance: **formal state contract + permission matrix**

## Migration Matrix

| OpenCLAW concept | Old source | Hermes-native replacement |
|---|---|---|
| Multi-agent list + default | `openclaw.json -> agents.list/default` | `hermes profile create` + `ceo` as gateway entry profile |
| Agent-to-agent sessions | `sessions_spawn/sessions_send/sessions_history` | `delegate_task` (single + parallel batch) |
| Channel bindings | `openclaw.json -> bindings/channels` | `ceo gateway setup` + profile-scoped gateway config |
| Native cron | `openclaw.json -> cron` + `openclaw cron add` | `hermes -p ceo cron create/edit/run/list` |
| Shared behavior prompts | `workspaces/*/AGENTS.md` | rewritten `assets/workspaces/*/AGENTS.md` (Hermes-native) |
| Financial engine | `shared/manage_finance.py` + `LEDGER.json` | direct reuse under `assets/shared/` |
| Setup script | `setup_corp.sh` | `scripts/bootstrap_hermes.sh` + noninteractive variant |

## Governance Additions
- `docs/STATE_CONTRACT.md` defines state layers, write permissions, transitions, and conflict rules.
- `docs/SELF_LEARNING_GUARDRAILS.md` constrains memory/skills auto-learning behavior.
- `docs/MULTI_PROFILE_COORDINATION.md` defines delegation and artifact ownership.

## Reused Assets
- `assets/shared/LEDGER.json`
- `assets/shared/manage_finance.py`
- `assets/shared/TEMPLATES.md`
- `assets/shared/CORP_CULTURE.md`
- `assets/shared/KNOWLEDGE_BASE.md`
- `assets/shared/SHAREHOLDER_ANNOUNCEMENTS.md`
- `assets/workspaces/{ceo,scout,cmo,arch,accountant}/{AGENTS.md,SOUL.md,IDENTITY.md,USER.md}`

## New Hermes-native Artifacts
- `profiles/*/config.yaml.example`
- `orchestration/cron/daily_pipeline.prompt.md`
- `orchestration/cron/health_check.prompt.md`
- `orchestration/cron/commands.sh`
- `scripts/smoke_test_pipeline.sh`
- `scripts/recover_cron.sh`

## Recommended Run Order
1. Run bootstrap:
   ```bash
   bash scripts/bootstrap_hermes.sh
   ```
2. Configure model/provider:
   ```bash
   hermes model
   ```
3. Optional baseline import preview:
   ```bash
   hermes claw migrate --dry-run
   ```
4. Ensure cron jobs:
   ```bash
   bash orchestration/cron/commands.sh ensure
   ```
5. Validate with smoke checks:
   ```bash
   bash scripts/smoke_test_pipeline.sh
   ```

## Rollback
If migration behavior is unsatisfactory, continue on original `profit-corp` with no data loss from this repo.
