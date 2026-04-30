# Codebase Structure

**Analysis Date:** 2026-04-24

## Directory Layout

```text
profit-corp-hermes/
├── assets/                 # Shared state and workspace identity artifacts
│   ├── shared/             # Ledger, culture, templates, governance artifacts
│   └── workspaces/         # Role-specific AGENTS/SOUL/IDENTITY/USER docs
├── config/                 # Global Hermes config template
├── docs/                   # Runbooks, migration docs, contracts, operations guidance
├── orchestration/          # Cron prompts and shell helpers
│   └── cron/               # Named cron prompt payloads and command wrapper
├── profiles/               # Per-role profile templates for Hermes home sync
├── scripts/                # Bootstrap, smoke, and recovery automation
├── skills/                 # Project skills and normalized standards library
│   ├── common/             # Shared skills synced to all profiles
│   ├── ceo/                # CEO-only directives
│   └── library/normalized/ # Governance/reference skill library
└── README.md               # Project overview and operator quick start
```

## Directory Purposes

**`assets/shared/`:**
- Purpose: shared business state and durable coordination files
- Contains: `LEDGER.json`, `manage_finance.py`, announcements, knowledge base, templates
- Key files: `assets/shared/LEDGER.json`, `assets/shared/manage_finance.py`
- Subdirectories: none observed

**`assets/workspaces/`:**
- Purpose: role identity source files for Hermes-native workspaces
- Contains: per-role `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md`
- Key files: `assets/workspaces/ceo/AGENTS.md`, `assets/workspaces/scout/SOUL.md`
- Subdirectories: one directory per role (`ceo`, `scout`, `cmo`, `arch`, `accountant`)

**`config/`:**
- Purpose: baseline global Hermes configuration template
- Contains: YAML example config
- Key files: `config/hermes.config.yaml.example`
- Subdirectories: none observed

**`docs/`:**
- Purpose: human-readable governance, migration, and operations documentation
- Contains: contracts, runbooks, operations policy, migration plan
- Key files: `docs/STATE_CONTRACT.md`, `docs/OPERATIONS.md`, `docs/MULTI_PROFILE_COORDINATION.md`
- Subdirectories: `docs/skill-governance/`

**`orchestration/cron/`:**
- Purpose: cron prompt definitions and command management wrapper
- Contains: `*.prompt.md` plus `commands.sh`
- Key files: `orchestration/cron/commands.sh`, `orchestration/cron/daily_pipeline.prompt.md`
- Subdirectories: none observed

**`profiles/`:**
- Purpose: per-role profile templates copied into `~/.hermes/profiles/<role>/`
- Contains: `SOUL.md` and `config.yaml.example` for each role
- Key files: `profiles/ceo/config.yaml.example`, `profiles/accountant/SOUL.md`
- Subdirectories: one directory per role

**`scripts/`:**
- Purpose: operator automation entry points
- Contains: shell and PowerShell bootstrap/recovery/smoke scripts
- Key files: `scripts/bootstrap_hermes.sh`, `scripts/bootstrap_hermes.ps1`, `scripts/smoke_test_pipeline.sh`, `scripts/recover_cron.sh`
- Subdirectories: none observed

**`skills/`:**
- Purpose: reusable instruction modules synced into Hermes runtime
- Contains: shared skills, CEO skills, and normalized standards library
- Key files: `skills/common/read_ledger.md`, `skills/ceo/ceo_daily_pipeline.md`, `skills/library/normalized/INDEX.md`
- Subdirectories: `common/`, `ceo/`, `library/normalized/`

## Key File Locations

**Entry Points:**
- `scripts/bootstrap_hermes.sh` - Main Unix bootstrap entry
- `scripts/bootstrap_hermes.ps1` - Main Windows bootstrap entry
- `orchestration/cron/commands.sh` - Cron management entry
- `assets/shared/manage_finance.py` - Financial mutation entry

**Configuration:**
- `config/hermes.config.yaml.example` - Global Hermes config template
- `profiles/*/config.yaml.example` - Per-role config templates
- `README.md` - Top-level operational setup guidance

**Core Logic:**
- `assets/shared/manage_finance.py` - Ledger mutation and audit logging logic
- `orchestration/cron/commands.sh` - Cron orchestration logic
- `scripts/smoke_test_pipeline.sh` - Validation logic

**Testing:**
- `scripts/smoke_test_pipeline.sh` - End-to-end smoke verification
- No dedicated `tests/` directory detected

**Documentation:**
- `docs/` - Operational and governance docs
- `docs/skill-governance/README.md` - Skill standardization guidance

## Naming Conventions

**Files:**
- Markdown docs use uppercase or snake_case/kebab-case depending on function (`README.md`, `STATE_CONTRACT.md`, `ceo_daily_pipeline.md`)
- Shell scripts use snake_case with `.sh` suffix (`bootstrap_hermes.sh`, `recover_cron.sh`)
- YAML templates use `config.yaml.example`

**Directories:**
- Lowercase plural nouns for collections (`assets`, `profiles`, `scripts`, `skills`, `docs`)
- Lowercase role names for profile/workspace folders (`ceo`, `scout`, `cmo`, `arch`, `accountant`)

**Special Patterns:**
- `*.prompt.md` for cron prompt payloads in `orchestration/cron/`
- `AGENTS.md`, `SOUL.md`, `IDENTITY.md`, `USER.md` for role identity bundles
- `config.yaml.example` as the template copied into runtime profile directories

## Where to Add New Code

**New Role Skill:**
- Implementation: `skills/<role>/` or `skills/common/`
- Runtime sync target: `~/.hermes/profiles/<role>/skills/`
- Supporting docs if needed: `docs/skill-governance/`

**New Governance/Runbook Document:**
- Primary docs: `docs/`
- Shared state contracts or operational procedures should live near related existing docs

**New Cron Workflow:**
- Prompt definition: `orchestration/cron/<name>.prompt.md`
- Shell control path: extend `orchestration/cron/commands.sh`
- Validation updates: `scripts/smoke_test_pipeline.sh`

**New Shared Artifact or State Tooling:**
- State file or helper: `assets/shared/`
- Permission/governance update: `docs/STATE_CONTRACT.md`
- Skill entrypoints: `skills/common/` or role-specific skill files

## Special Directories

**`assets/shared/`:**
- Purpose: authoritative shared state and corporate memory
- Source: edited directly in repo, with `LEDGER.json` mutations constrained to `manage_finance.py`
- Committed: Yes

**`skills/library/normalized/`:**
- Purpose: full standards library not necessarily synced as active runtime skills
- Source: curated governance/reference material
- Committed: Yes

**`~/.hermes/` (external runtime target):**
- Purpose: generated runtime home for Hermes config and profiles
- Source: populated by bootstrap scripts
- Committed: No (outside repo)

---

*Structure analysis: 2026-04-24*
*Update when directory structure changes*
