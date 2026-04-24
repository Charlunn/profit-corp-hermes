# Architecture

**Analysis Date:** 2026-04-24

## Pattern Overview

**Overall:** File-driven multi-profile operations workspace for Hermes

**Key Characteristics:**
- Repository is mostly declarative: prompts, governance docs, templates, and role definitions drive behavior
- Execution is shell-orchestrated through Hermes CLI rather than through an application server
- Shared mutable state is intentionally narrow and governed by contract in `docs/STATE_CONTRACT.md`
- CEO acts as the coordination gateway while other profiles own bounded artifacts

## Layers

**Governance Layer:**
- Purpose: Define state rules, ownership, safety boundaries, and recovery procedures
- Contains: `docs/STATE_CONTRACT.md`, `docs/MULTI_PROFILE_COORDINATION.md`, `docs/SELF_LEARNING_GUARDRAILS.md`, `docs/OPERATIONS.md`
- Depends on: repository conventions and human/operator adherence
- Used by: all scripts, skills, and profiles as the source of truth for behavior

**Profile Definition Layer:**
- Purpose: Define role identity, personality, and baseline runtime settings
- Contains: `profiles/*/SOUL.md`, `profiles/*/config.yaml.example`, `assets/workspaces/*/{AGENTS.md,SOUL.md,IDENTITY.md,USER.md}`
- Depends on: Hermes profile system
- Used by: bootstrap scripts and Hermes runtime

**Skill Layer:**
- Purpose: Encode reusable operational actions and safety policies
- Contains: `skills/common/*.md`, `skills/ceo/*.md`, `skills/library/normalized/*.md`
- Depends on: governance layer for allowed behavior and shared-state rules
- Used by: synced Hermes profiles under `~/.hermes/profiles/<role>/skills/`

**Orchestration Layer:**
- Purpose: Schedule and trigger recurring workflows
- Contains: `orchestration/cron/daily_pipeline.prompt.md`, `orchestration/cron/health_check.prompt.md`, `orchestration/cron/commands.sh`
- Depends on: Hermes cron commands and CEO profile availability
- Used by: operators and recovery scripts

**State Layer:**
- Purpose: Hold shared durable business state and audit artifacts
- Contains: `assets/shared/LEDGER.json`, `assets/shared/AUDIT_LOG.csv`, `assets/shared/CORP_CULTURE.md`, `assets/shared/SHAREHOLDER_ANNOUNCEMENTS.md`
- Depends on: restricted write paths, especially `assets/shared/manage_finance.py`
- Used by: all roles for read access; write access is restricted by policy

**Automation Layer:**
- Purpose: Bootstrap environment, validate health, and recover from drift
- Contains: `scripts/bootstrap_hermes.sh`, `scripts/bootstrap_hermes.ps1`, `scripts/bootstrap_hermes_noninteractive.sh`, `scripts/smoke_test_pipeline.sh`, `scripts/recover_cron.sh`
- Depends on: Hermes CLI, shell runtime, config templates, and state files
- Used by: human operators during setup and incident handling

## Data Flow

**Bootstrap Flow:**
1. Operator runs `scripts/bootstrap_hermes.sh` or `scripts/bootstrap_hermes.ps1`
2. Script verifies prerequisites and installs Hermes if missing
3. Global config is copied from `config/hermes.config.yaml.example` into `~/.hermes/config.yaml`
4. Profiles are created/updated from `profiles/*/config.yaml.example` and `profiles/*/SOUL.md`
5. Skills from `skills/common/` and `skills/<role>/` are synced into Hermes profile directories
6. Optional doctor/migration/smoke/cron setup steps complete environment initialization

**Daily Operations Flow:**
1. Scheduler or operator invokes `orchestration/cron/commands.sh run-daily`
2. Hermes runs the CEO daily pipeline prompt from `orchestration/cron/daily_pipeline.prompt.md`
3. CEO delegates or coordinates Scout/CMO/Arch/Accountant work per `docs/MULTI_PROFILE_COORDINATION.md`
4. Shared artifacts under `assets/shared/` are updated by the owning role
5. Financial state changes go through `assets/shared/manage_finance.py`
6. Audit/recovery checks use `scripts/smoke_test_pipeline.sh` and `scripts/recover_cron.sh`

**State Management:**
- File-based with one explicit authoritative state file: `assets/shared/LEDGER.json`
- High-risk mutations are serialized through file locking in `assets/shared/manage_finance.py`
- Other business artifacts are role-owned markdown documents with CEO-controlled sequencing

## Key Abstractions

**Profile:**
- Purpose: Persistent operator identity inside Hermes
- Examples: `ceo`, `scout`, `cmo`, `arch`, `accountant`
- Pattern: Role-scoped runtime config + SOUL + synced skills

**Skill:**
- Purpose: Reusable, policy-constrained action recipe
- Examples: `skills/ceo/ceo_daily_pipeline.md`, `skills/common/read_ledger.md`, `skills/common/release_verification.md`
- Pattern: Markdown instruction modules synced into runtime profile folders

**Shared Artifact:**
- Purpose: Durable coordination medium across profiles
- Examples: `assets/shared/LEDGER.json`, `assets/shared/CORP_CULTURE.md`, `assets/shared/KNOWLEDGE_BASE.md`
- Pattern: File-as-contract with explicit ownership rules

**Cron Command Hub:**
- Purpose: Stable shell façade over Hermes cron primitives
- Examples: `orchestration/cron/commands.sh` actions `ensure`, `recreate`, `run-daily`, `pause-all`
- Pattern: thin wrapper around Hermes CLI with duplicate cleanup and operational naming

## Entry Points

**Bootstrap Entry:**
- Location: `scripts/bootstrap_hermes.sh`, `scripts/bootstrap_hermes.ps1`
- Triggers: manual setup or re-sync
- Responsibilities: install Hermes, provision configs, create profiles, sync skills, optionally run smoke checks

**Cron Operations Entry:**
- Location: `orchestration/cron/commands.sh`
- Triggers: operator shell commands and recovery scripts
- Responsibilities: create/list/status/resume/pause/recreate named cron jobs

**Finance Engine Entry:**
- Location: `assets/shared/manage_finance.py`
- Triggers: approved revenue/bounty/audit flows
- Responsibilities: locked read-modify-write of ledger and audit logging

## Error Handling

**Strategy:** Fail fast in scripts (`set -euo pipefail`) and use explicit pass/fail reporting in smoke checks

**Patterns:**
- Shell scripts abort on unexpected command failure unless a path is intentionally best-effort (`|| true`)
- Finance operations print user-visible warnings/errors instead of hiding state issues
- Recovery scripts prefer deterministic re-ensure/recreate workflows over in-place patching

## Cross-Cutting Concerns

**Logging:**
- Operational logs are shell-prefixed (`[bootstrap]`, `[cron]`, `[smoke]`, `[recover]`)
- Financial events are appended to `assets/shared/AUDIT_LOG.csv`

**Validation:**
- Smoke checks verify required commands and critical files in `scripts/smoke_test_pipeline.sh`
- Governance docs encode procedural validation before writes

**Authorization:**
- There is no app-level auth layer; authorization is role/process based and documented in `docs/STATE_CONTRACT.md`
- Approval gates for risky actions are encoded in docs and CEO skills

---

*Architecture analysis: 2026-04-24*
*Update when major patterns change*
