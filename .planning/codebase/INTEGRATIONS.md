# External Integrations

**Analysis Date:** 2026-04-24

## APIs & External Services

**Hermes Runtime:**
- Hermes CLI - Primary external runtime used for profile lifecycle, cron scheduling, and chat execution
  - Integration method: shell commands in `scripts/bootstrap_hermes.sh`, `scripts/smoke_test_pipeline.sh`, and `orchestration/cron/commands.sh`
  - Auth: whatever account/provider configuration the local Hermes installation uses
  - Commands used: `hermes profile create`, `hermes profile use`, `hermes profile list`, `hermes -p ceo cron *`, `hermes -p ceo chat`

**Installer Source:**
- GitHub raw installer endpoint - Used only when Hermes is missing
  - Integration method: `curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash` in `scripts/bootstrap_hermes.sh:76-78` and analogous PowerShell flow in `scripts/bootstrap_hermes.ps1:62-69`
  - Auth: none observed
  - Risk profile: remote bootstrap dependency during first-run setup

## Data Storage

**Databases:**
- None - No SQL/NoSQL database client or connection string patterns were found in the repository

**File Storage:**
- Local filesystem - All durable state is repo files plus user-home Hermes config
  - Shared business state: `assets/shared/LEDGER.json`, `assets/shared/SHAREHOLDER_ANNOUNCEMENTS.md`, `assets/shared/CORP_CULTURE.md`, `assets/shared/KNOWLEDGE_BASE.md`
  - User runtime state: `~/.hermes/config.yaml` and `~/.hermes/profiles/<role>/`

**Caching:**
- None observed

## Authentication & Identity

**Auth Provider:**
- No in-repo auth provider integration
- Identity is profile-based within Hermes (`ceo`, `scout`, `cmo`, `arch`, `accountant`) rather than application-level user auth

**OAuth Integrations:**
- None observed

## Monitoring & Observability

**Error Tracking:**
- None observed (no Sentry, Datadog, Rollbar, etc.)

**Analytics:**
- None observed

**Logs:**
- Shell stdout/stderr and CSV audit log
  - `assets/shared/AUDIT_LOG.csv` is written by `assets/shared/manage_finance.py`
  - Operational visibility is driven by `hermes ... cron list/status` and smoke scripts rather than centralized logging

## CI/CD & Deployment

**Hosting:**
- Not a hosted app; repository is meant to be bootstrapped into a local/host-managed Hermes environment

**CI Pipeline:**
- None detected in-repo (`.github/workflows/` absent from surveyed files)

## Environment Configuration

**Development:**
- Required tools: `hermes`, `bash`, and `python3`/`python`
- Config templates: `config/hermes.config.yaml.example` and `profiles/*/config.yaml.example`
- Secrets location: not defined in-repo; expected to be managed by the user's Hermes/provider configuration

**Staging:**
- No separate staging environment documented

**Production:**
- No distinct production deployment target; “production” effectively means the active Hermes operator environment and its cron jobs

## Webhooks & Callbacks

**Incoming:**
- None observed

**Outgoing:**
- None observed beyond shell invocations to Hermes CLI and installer download

## Integration Notes

- `orchestration/cron/commands.sh` is the integration hub for Hermes cron operations
- `scripts/bootstrap_hermes.sh` and `scripts/bootstrap_hermes.ps1` are the main boundaries where this repo touches external systems
- `assets/shared/manage_finance.py` is intentionally isolated from external services; it only touches local files

---

*Integration audit: 2026-04-24*
*Update when adding/removing external services*
