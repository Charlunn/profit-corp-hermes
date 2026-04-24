# Coding Conventions

**Analysis Date:** 2026-04-24

## Naming Patterns

**Files:**
- Uppercase markdown filenames for top-level authority docs (`README.md`, `STATE_CONTRACT.md`, `OPERATIONS.md`)
- snake_case for executable scripts and many skill files (`bootstrap_hermes.sh`, `ceo_daily_pipeline.md`, `read_ledger.md`)
- `config.yaml.example` naming for runtime templates under `config/` and `profiles/`

**Functions:**
- Shell functions use lower_snake_case (`require_cmd`, `setup_profiles`, `create_jobs`)
- Python functions also use snake_case (`load_ledger`, `record_revenue`, `grant_bounty`)
- PowerShell functions use Verb-Noun PascalCase (`Resolve-Python`, `Sync-Profile`, `Setup-Profiles`)

**Variables:**
- Shell constants and globals prefer UPPER_SNAKE_CASE (`ROOT_DIR`, `HERMES_HOME_DEFAULT`, `DAILY_NAME`)
- Local shell vars use lowercase snake_case sparingly but many scripts keep uppercase globals even when mutable
- Python locals and module constants follow snake_case / UPPER_SNAKE_CASE split

**Types:**
- No user-defined typed language constructs observed in the surveyed codebase
- Data schemas are implicit in JSON/YAML/Markdown contracts rather than classes/interfaces

## Code Style

**Formatting:**
- No formatter config detected in repo root
- Shell scripts consistently begin with `#!/usr/bin/env bash` and `set -euo pipefail`
- Indentation is generally 2 spaces in shell/YAML/Markdown and 4 spaces in Python
- Strings in shell scripts often use double quotes for interpolation safety

**Linting:**
- No ESLint/Prettier/ShellCheck config detected
- Style enforcement appears convention-driven rather than tool-enforced
- Smoke checks focus on runtime correctness, not linting

## Import Organization

**Order:**
1. Standard library imports first in Python (`csv`, `json`, `sys`, `os`)
2. Conditional platform-specific import inside fallback block (`fcntl` guarded by `try/except ImportError`)
3. No complex internal module import graph observed

**Grouping:**
- Python imports are grouped at top of file with a blank line before major implementation blocks
- Shell scripts keep helper functions above orchestration logic and dispatch cases at the bottom

**Path Aliases:**
- None observed
- Scripts resolve repository-relative paths explicitly using `ROOT_DIR` / `BASE_DIR`

## Error Handling

**Patterns:**
- Shell scripts fail fast by default via `set -euo pipefail`
- Best-effort operational commands use `|| true` when recovery/status should continue even after partial failure
- Python CLI-style logic prints explicit warnings/errors to stdout rather than raising rich app exceptions

**Error Types:**
- Missing dependency checks are centralized in helper functions like `require_cmd`
- Invalid finance operations return early with visible error messages (`treasury` insufficient, agent missing)
- Recovery paths prefer explicit warnings over silent suppression

## Logging

**Framework:**
- Shell scripts use lightweight prefixed log helpers (`log`, `warn`, `err`, `ok`, `fail`)
- Python uses `print()` and appends structured rows to `assets/shared/AUDIT_LOG.csv`

**Patterns:**
- Prefix every shell message with subsystem tags such as `[bootstrap]`, `[cron]`, `[smoke]`, `[recover]`
- Report actionable success/failure states rather than verbose traces
- Operator-facing logs are human-readable and suitable for terminal use

## Comments

**When to Comment:**
- Comments explain operational intent, cross-platform behavior, and policy constraints
- Long-form block comments are used for tricky areas such as file locking in `assets/shared/manage_finance.py`
- Markdown docs carry the deeper rationale; scripts usually stay concise

**JSDoc/TSDoc:**
- Not applicable in surveyed files

**TODO Comments:**
- No active `TODO`/`FIXME` conventions were found in the searched repository files

## Function Design

**Size:**
- Scripts favor many small helpers plus one orchestration function (`main`, `setup_profiles`, `ensure_jobs`)
- Python finance logic uses focused functions per command/action rather than one giant handler only

**Parameters:**
- Shell helpers usually take a few positional parameters
- PowerShell uses named parameters and typed function args where helpful
- Python functions accept explicit scalar parameters instead of options objects

**Return Values:**
- Shell communicates success/failure primarily by exit code
- Python command helpers mutate state and print results; functions return early for invalid cases
- Guard clauses are common for missing commands, missing files, and invalid targets

## Module Design

**Exports:**
- No package/module export surface is designed here; scripts are entrypoints and markdown files are source artifacts
- Reuse is achieved by shell helper functions and shared markdown contracts, not importable packages

**Barrel Files:**
- None observed

## Style Guidance for New Changes

- Preserve shell fail-fast behavior unless a command is intentionally best-effort
- Keep naming aligned with existing snake_case conventions in scripts and skill filenames
- Route shared-state mutations through `assets/shared/manage_finance.py` rather than direct JSON edits
- Prefer explicit operator messaging over hidden behavior in automation scripts

---

*Convention analysis: 2026-04-24*
*Update when patterns change*
