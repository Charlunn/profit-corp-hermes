# Technology Stack

**Analysis Date:** 2026-04-24

## Languages

**Primary:**
- Markdown - Most operational logic, role prompts, governance docs, and skill definitions live in `README.md`, `docs/*.md`, `skills/**/*.md`, and `assets/workspaces/**/*.md`
- Bash - Unix automation and recovery flows in `scripts/*.sh` and `orchestration/cron/commands.sh`

**Secondary:**
- PowerShell - Windows bootstrap path in `scripts/bootstrap_hermes.ps1`
- Python 3 - Financial state management and validation in `assets/shared/manage_finance.py`
- JSON/YAML - Persistent state and config templates in `assets/shared/LEDGER.json`, `config/hermes.config.yaml.example`, and `profiles/*/config.yaml.example`

## Runtime

**Environment:**
- Hermes CLI runtime - Core execution environment assumed by `scripts/bootstrap_hermes.sh`, `scripts/smoke_test_pipeline.sh`, and `orchestration/cron/commands.sh`
- Python 3 - Required for ledger syntax checks and finance mutations via `assets/shared/manage_finance.py`
- Bash shell - Required for Linux/macOS bootstrap and cron orchestration
- PowerShell - Supported for Windows setup via `scripts/bootstrap_hermes.ps1`

**Package Manager:**
- No project-local package manager manifest detected (`package.json`, `pyproject.toml`, `go.mod`, etc. are absent)
- Dependency installation is delegated to external tooling and the Hermes installer script invoked by `scripts/bootstrap_hermes.sh`
- Lockfile: none present in repository root

## Frameworks

**Core:**
- Hermes multi-profile agent system - Operational model for `ceo`, `scout`, `cmo`, `arch`, and `accountant`
- Cron-first orchestration - Job management centered on `orchestration/cron/commands.sh` with prompt payloads in `orchestration/cron/*.prompt.md`

**Testing:**
- Shell-based smoke validation - `scripts/smoke_test_pipeline.sh`
- Python bytecode compile check - `python3 -m py_compile assets/shared/manage_finance.py`

**Build/Dev:**
- No compile/build pipeline in repo; artifacts are mostly source-of-truth docs, scripts, and templates
- Bootstrap scripts provision runtime state into `~/.hermes/` from repository templates

## Key Dependencies

**Critical:**
- `hermes` CLI - Required to create profiles, manage cron jobs, list status, and run role-scoped commands
- `python3` / `python` - Executes and validates `assets/shared/manage_finance.py`
- `bash` - Runs bootstrap, recovery, smoke tests, and cron helpers
- `curl` - Used by `scripts/bootstrap_hermes.sh` and `scripts/bootstrap_hermes.ps1` to install Hermes if missing
- Standard library Python modules (`csv`, `json`, `contextlib`, `datetime`, optional `fcntl`) - Power the finance engine in `assets/shared/manage_finance.py`

**Infrastructure:**
- File-based state in `assets/shared/LEDGER.json` and related docs under `assets/shared/`
- User-level Hermes home in `~/.hermes/` populated from `config/hermes.config.yaml.example` and `profiles/*/config.yaml.example`

## Configuration

**Environment:**
- Runtime configuration is template-driven, not env-heavy
- Main template: `config/hermes.config.yaml.example`
- Per-profile templates: `profiles/{ceo,scout,cmo,arch,accountant}/config.yaml.example`
- Shell scripts rely on CLI availability and home-directory defaults such as `~/.hermes/config.yaml`

**Build:**
- No build config files detected
- Operational configuration lives in YAML templates and markdown prompts rather than a compiler/bundler config

## Platform Requirements

**Development:**
- Cross-platform with separate setup flows: Bash on Unix-like systems and PowerShell on Windows
- Requires Hermes CLI access or network access to install it during bootstrap
- Requires filesystem access to write into `~/.hermes/`

**Production:**
- Designed to run as an operator-managed Hermes workspace rather than a deployed web service
- Persistent scheduled execution depends on Hermes cron support and prompt files in `orchestration/cron/`

---

*Stack analysis: 2026-04-24*
*Update after major dependency changes*
