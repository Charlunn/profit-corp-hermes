#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
HERMES_HOME_DEFAULT="$HOME/.hermes"
HERMES_CONFIG_FILE="$HERMES_HOME_DEFAULT/config.yaml"
TEMPLATE_FILE="$ROOT_DIR/config/hermes.config.yaml.example"
PROFILE_LIST="${PROFILE_LIST:-ceo,scout,cmo,arch,accountant}"
PYTHON_BIN=""
OVERWRITE_SYNCED_SKILLS="${OVERWRITE_SYNCED_SKILLS:-0}"

log() { printf '[bootstrap-noninteractive] %s\n' "$*"; }
err() { printf '[bootstrap-noninteractive] ERROR: %s\n' "$*" >&2; exit 1; }

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
    log "Hermes already installed"
    return 0
  fi

  [ "${INSTALL_HERMES_IF_MISSING:-1}" = "1" ] || err "Hermes missing and INSTALL_HERMES_IF_MISSING!=1"

  curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash
  [ -f "$HOME/.bashrc" ] && source "$HOME/.bashrc" || true
  command -v hermes >/dev/null 2>&1 || err "Hermes not found after install"
}

install_ui_ux_pro_max() {
  if ! command -v npm >/dev/null 2>&1; then
    log "npm not found; skipping UI/UX Pro Max install"
    return 0
  fi

  if ! command -v uipro >/dev/null 2>&1; then
    log "Installing UI/UX Pro Max CLI"
    npm install -g uipro-cli || err "Failed to install uipro-cli"
  else
    log "UI/UX Pro Max CLI already installed"
  fi

  (cd "$ROOT_DIR" && uipro init --ai claude)
  log "UI/UX Pro Max skill installed for Claude Code"
}

copy_default_config() {
  mkdir -p "$HERMES_HOME_DEFAULT"

  if [ -f "$HERMES_CONFIG_FILE" ] && [ "${OVERWRITE_HERMES_CONFIG:-0}" != "1" ]; then
    log "Existing default config preserved: $HERMES_CONFIG_FILE"
    return 0
  fi

  cp "$TEMPLATE_FILE" "$HERMES_CONFIG_FILE"
  log "Default config written: $HERMES_CONFIG_FILE"
}

sync_profile() {
  local profile="$1"
  local profile_home="$HERMES_HOME_DEFAULT/profiles/$profile"
  local profile_template="$ROOT_DIR/profiles/$profile/config.yaml.example"
  local soul_src="$ROOT_DIR/profiles/$profile/SOUL.md"

  [ -d "$profile_home" ] || hermes profile create "$profile" >/dev/null
  mkdir -p "$profile_home"
  cp "$profile_template" "$profile_home/config.yaml"
  cp "$soul_src" "$profile_home/SOUL.md"
  log "Profile synced: $profile"
}

sync_profile_skills() {
  local profile="$1"
  local profile_home="$HERMES_HOME_DEFAULT/profiles/$profile"
  local target_dir="$profile_home/skills"
  local source_common="$ROOT_DIR/skills/common"
  local source_role="$ROOT_DIR/skills/$profile"

  mkdir -p "$target_dir"

  [ -d "$source_common" ] || [ -d "$source_role" ] || return 0

  if [ "$OVERWRITE_SYNCED_SKILLS" != "1" ] && [ -n "$(ls -A "$target_dir" 2>/dev/null || true)" ]; then
    log "Existing skills kept for $profile (set OVERWRITE_SYNCED_SKILLS=1 to replace)"
    return 0
  fi

  if [ -d "$source_common" ]; then
    cp -f "$source_common"/*.md "$target_dir"/ 2>/dev/null || true
  fi
  if [ -d "$source_role" ]; then
    cp -f "$source_role"/*.md "$target_dir"/ 2>/dev/null || true
  fi
  log "Skills synced: $profile"
}

setup_profiles() {
  [ "${SETUP_PROFILES:-1}" = "1" ] || { log "Skipping profile setup"; return 0; }

  local old_ifs="$IFS"
  IFS=','
  # shellcheck disable=SC2086
  set -- $PROFILE_LIST
  IFS="$old_ifs"

  for p in "$@"; do
    sync_profile "$p"
    sync_profile_skills "$p"
  done
}

ensure_ceo_default_profile() {
  hermes profile use ceo >/dev/null 2>&1 || true

  if hermes profile remove default >/dev/null 2>&1; then
    log "Removed default profile"
  elif hermes profile delete default >/dev/null 2>&1; then
    log "Removed default profile"
  else
    log "Default profile removal skipped"
  fi
}

run_optional_migration() {
  [ "${RUN_OPENCLAW_DRY_RUN:-0}" = "1" ] || return 0
  [ -d "$HOME/.openclaw" ] || err "RUN_OPENCLAW_DRY_RUN=1 but ~/.openclaw not found"
  hermes claw migrate --dry-run
}

setup_optional_cron() {
  [ "${SETUP_CRON:-1}" = "1" ] || { log "Skipping cron setup"; return 0; }
  bash "$ROOT_DIR/orchestration/cron/commands.sh" ensure
}

run_optional_smoke() {
  [ "${RUN_SMOKE_TEST:-1}" = "1" ] || { log "Skipping smoke test"; return 0; }
  bash "$ROOT_DIR/scripts/smoke_test_pipeline.sh"
}

main() {
  require_cmd bash
  require_cmd git
  require_cmd curl
  resolve_python

  install_hermes_if_missing
  install_ui_ux_pro_max
  copy_default_config
  setup_profiles
  ensure_ceo_default_profile
  run_optional_migration
  setup_optional_cron
  run_optional_smoke

  log "Running Hermes doctor"
  hermes doctor || log "Hermes doctor reported issues"
  "$PYTHON_BIN" -m py_compile "$ROOT_DIR/assets/shared/manage_finance.py" || true

  log "Done"
}

main "$@"
