#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_HOME_DEFAULT="$HOME/.hermes"
HERMES_CONFIG_FILE="$HERMES_HOME_DEFAULT/config.yaml"
TEMPLATE_FILE="$ROOT_DIR/config/hermes.config.yaml.example"
PROFILES=(ceo scout cmo arch accountant)
SKIP_CRON=0
SKIP_PROFILES=0
SKIP_SMOKE=0
SKIP_MIGRATION=0
SKIP_DOCTOR=0
PYTHON_BIN=""
GLOBAL_CONFIG_OVERWRITTEN=0
PROFILE_CONFIG_OVERWRITTEN=0
CHANGED_PROFILES=()
OVERWRITE_SYNCED_SKILLS=0

log() { printf '[bootstrap] %s\n' "$*"; }
warn() { printf '[bootstrap] WARN: %s\n' "$*"; }
err() { printf '[bootstrap] ERROR: %s\n' "$*" >&2; exit 1; }

usage() {
  cat <<'EOF'
Usage: bash scripts/bootstrap_hermes.sh [--skip-cron] [--skip-profiles] [--skip-smoke] [--skip-migration] [--skip-doctor]

Options:
  --skip-cron      Do not create/update cron jobs
  --skip-profiles  Do not create/update ceo/scout/cmo/arch/accountant profiles
  --skip-smoke     Do not run scripts/smoke_test_pipeline.sh at the end
  --skip-migration Do not prompt for hermes claw migrate --dry-run
  --skip-doctor    Skip hermes doctor and sanity checks
EOF
}

parse_args() {
  while [ $# -gt 0 ]; do
    case "$1" in
      --skip-cron) SKIP_CRON=1 ;;
      --skip-profiles) SKIP_PROFILES=1 ;;
      --skip-smoke) SKIP_SMOKE=1 ;;
      --skip-migration) SKIP_MIGRATION=1 ;;
      --skip-doctor) SKIP_DOCTOR=1 ;;
      -h|--help) usage; exit 0 ;;
      *) err "Unknown option: $1" ;;
    esac
    shift
  done
}

require_cmd() {
  command -v "$1" >/dev/null 2>&1 || err "Missing required command: $1"
}

resolve_python() {
  if command -v python3 >/dev/null 2>&1; then
    PYTHON_BIN="python3"
    log "Python runtime: python3"
    return 0
  fi
  if command -v python >/dev/null 2>&1; then
    PYTHON_BIN="python"
    log "Python runtime: python"
    return 0
  fi
  err "Missing required command: python3 or python"
}

install_hermes_if_missing() {
  if command -v hermes >/dev/null 2>&1; then
    log "Hermes already installed: $(command -v hermes)"
    return 0
  fi

  log "Hermes not found. Installing via official installer..."
  curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

  if [ -f "$HOME/.bashrc" ]; then
    # shellcheck disable=SC1090
    source "$HOME/.bashrc" || true
  fi

  command -v hermes >/dev/null 2>&1 || err "Hermes install finished but command not found. Re-open shell and rerun."
  log "Hermes installed successfully"
}

setup_default_config() {
  mkdir -p "$HERMES_HOME_DEFAULT"

  if [ ! -f "$HERMES_CONFIG_FILE" ]; then
    cp "$TEMPLATE_FILE" "$HERMES_CONFIG_FILE"
    GLOBAL_CONFIG_OVERWRITTEN=1
    log "Created $HERMES_CONFIG_FILE from template"
    return 0
  fi

  read -r -p "~/.hermes/config.yaml exists. Overwrite with project template? [y/N] " ans
  case "${ans:-N}" in
    [yY]|[yY][eE][sS])
      cp "$TEMPLATE_FILE" "$HERMES_CONFIG_FILE"
      GLOBAL_CONFIG_OVERWRITTEN=1
      log "Overwrote $HERMES_CONFIG_FILE"
      ;;
    *)
      log "Keeping existing Hermes config"
      ;;
  esac
}

create_or_update_profile() {
  local profile="$1"
  local profile_home="$HERMES_HOME_DEFAULT/profiles/$profile"
  local profile_template="$ROOT_DIR/profiles/$profile/config.yaml.example"
  local soul_src="$ROOT_DIR/profiles/$profile/SOUL.md"

  if [ ! -d "$profile_home" ]; then
    log "Creating profile: $profile"
    hermes profile create "$profile" >/dev/null
  else
    log "Profile exists: $profile"
  fi

  mkdir -p "$profile_home"

  if [ -f "$profile_home/config.yaml" ]; then
    read -r -p "Profile '$profile' config exists. Overwrite with project template? [y/N] " ans
    case "${ans:-N}" in
      [yY]|[yY][eE][sS])
        cp "$profile_template" "$profile_home/config.yaml"
        PROFILE_CONFIG_OVERWRITTEN=1
        CHANGED_PROFILES+=("$profile")
        log "Overwrote profile config: $profile"
        ;;
      *)
        log "Keeping existing profile config: $profile"
        ;;
    esac
  else
    cp "$profile_template" "$profile_home/config.yaml"
    PROFILE_CONFIG_OVERWRITTEN=1
    CHANGED_PROFILES+=("$profile")
    log "Created profile config: $profile"
  fi

  cp "$soul_src" "$profile_home/SOUL.md"

  if [ -d "$ROOT_DIR/skills" ]; then
    mkdir -p "$profile_home/skills"
  fi

  log "Profile synced: $profile"
}

sync_profile_skills() {
  local profile="$1"
  local profile_home="$HERMES_HOME_DEFAULT/profiles/$profile"
  local target_dir="$profile_home/skills"
  local source_common="$ROOT_DIR/skills/common"
  local source_role="$ROOT_DIR/skills/$profile"
  local ans

  mkdir -p "$target_dir"

  if [ -d "$source_common" ] || [ -d "$source_role" ]; then
    if [ "$OVERWRITE_SYNCED_SKILLS" -eq 0 ] && [ -n "$(ls -A "$target_dir" 2>/dev/null || true)" ]; then
      read -r -p "Profile '$profile' skills exist. Overwrite synced skills from project? [y/N] " ans
      case "${ans:-N}" in
        [yY]|[yY][eE][sS]) OVERWRITE_SYNCED_SKILLS=1 ;;
        *)
          log "Keeping existing profile skills: $profile"
          return 0
          ;;
      esac
    fi

    if [ -d "$source_common" ]; then
      cp -f "$source_common"/*.md "$target_dir"/ 2>/dev/null || true
    fi
    if [ -d "$source_role" ]; then
      cp -f "$source_role"/*.md "$target_dir"/ 2>/dev/null || true
    fi
    log "Skills synced: $profile"
  fi
}

setup_profiles() {
  [ "$SKIP_PROFILES" -eq 1 ] && { log "Skipping profile setup"; return 0; }
  for p in "${PROFILES[@]}"; do
    create_or_update_profile "$p"
    sync_profile_skills "$p"
  done
}

ensure_ceo_default_profile() {
  hermes profile use ceo >/dev/null 2>&1 || warn "Failed to set ceo as active profile"

  if hermes profile remove default >/dev/null 2>&1; then
    log "Removed default profile"
  elif hermes profile delete default >/dev/null 2>&1; then
    log "Removed default profile"
  else
    log "Default profile removal skipped (may already be absent or command unsupported)"
  fi
}

run_migration_dry_run() {
  local ans
  [ "$SKIP_MIGRATION" -eq 1 ] && { log "Skipping claw migration dry-run"; return 0; }

  if [ ! -d "$HOME/.openclaw" ]; then
    warn "~/.openclaw not found; skipping claw migration dry-run"
    return 0
  fi

  read -r -p "Run 'hermes claw migrate --dry-run' now? [Y/n] " ans
  case "${ans:-Y}" in
    [nN]|[nN][oO])
      log "Skipped migration dry-run"
      ;;
    *)
      hermes claw migrate --dry-run || warn "Dry-run reported issues; inspect output"
      ;;
  esac
}

setup_cron_jobs() {
  [ "$SKIP_CRON" -eq 1 ] && { log "Skipping cron job setup"; return 0; }
  bash "$ROOT_DIR/orchestration/cron/commands.sh" ensure || warn "Cron setup reported issues"
}

run_smoke_test() {
  [ "$SKIP_SMOKE" -eq 1 ] && { log "Skipping smoke test"; return 0; }
  bash "$ROOT_DIR/scripts/smoke_test_pipeline.sh" || warn "Smoke test reported failures"
}

smoke_test() {
  log "Running Hermes doctor"
  hermes doctor || warn "Hermes doctor reported issues"

  log "Checking finance script syntax"
  "$PYTHON_BIN" -m py_compile "$ROOT_DIR/assets/shared/manage_finance.py" || warn "Ledger syntax check failed"

  log "Current profiles"
  hermes profile list || true

  log "Current cron jobs (ceo profile)"
  hermes -p ceo cron list || true
}

configure_models_interactive() {
  local ans p

  if ! command -v hermes >/dev/null 2>&1; then
    warn "Hermes not found; skipping interactive model configuration"
    return 0
  fi

  if [ "$GLOBAL_CONFIG_OVERWRITTEN" -eq 1 ]; then
    read -r -p "Global Hermes config changed. Configure default provider/model now? [Y/n] " ans
    case "${ans:-Y}" in
      [nN]|[nN][oO])
        warn "Skipped default model setup; configure later with 'hermes model'"
        ;;
      *)
        hermes model || warn "Default model setup did not complete"
        ;;
    esac
  fi

  if [ "${#CHANGED_PROFILES[@]}" -eq 0 ]; then
    return 0
  fi

  for p in "${CHANGED_PROFILES[@]}"; do
    read -r -p "Profile '$p' config changed. Configure provider/model for this profile now? [Y/n] " ans
    case "${ans:-Y}" in
      [nN]|[nN][oO])
        warn "Skipped model setup for $p; run '$p model' later"
        ;;
      *)
        "$p" model || hermes -p "$p" model || warn "Model setup failed for profile: $p"
        ;;
    esac
  done
}

main() {
  parse_args "$@"

  require_cmd bash
  require_cmd git
  require_cmd curl
  resolve_python

  log "Project root: $ROOT_DIR"
  install_hermes_if_missing
  setup_default_config
  setup_profiles
  ensure_ceo_default_profile
  configure_models_interactive

  log "Tip: run 'ceo gateway setup' as primary messaging entrypoint"

  run_migration_dry_run
  setup_cron_jobs
  run_smoke_test

  if [ "$SKIP_DOCTOR" -eq 1 ]; then
    log "Skipping Hermes doctor and sanity checks"
  else
    smoke_test
  fi

  if [ "$GLOBAL_CONFIG_OVERWRITTEN" -eq 1 ] || [ "$PROFILE_CONFIG_OVERWRITTEN" -eq 1 ]; then
    log "Model/provider interactive setup completed for overwritten configs where approved."
  fi

  log "Bootstrap complete"
}

main "$@"
