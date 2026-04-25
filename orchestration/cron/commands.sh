#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DAILY_PROMPT_FILE="$ROOT_DIR/orchestration/cron/daily_pipeline.prompt.md"
HEALTH_PROMPT_FILE="$ROOT_DIR/orchestration/cron/health_check.prompt.md"
EXTERNAL_INTELLIGENCE_PROMPT_FILE="$ROOT_DIR/orchestration/cron/external_intelligence.prompt.md"

DAILY_NAME="ProfitCorp Daily Pipeline"
HEALTH_NAME="ProfitCorp Health Check"
ANALYSIS_LOOP_NAME="ProfitCorp Analysis Loop"
ACTION="${1:-list}"

log() { printf '[cron] %s\n' "$*"; }
warn() { printf '[cron] WARN: %s\n' "$*"; }

cron_list_raw() {
  hermes -p ceo cron list 2>/dev/null || true
}

has_job_named() {
  local name="$1"
  cron_list_raw | grep -Fqi "$name"
}

job_ids_named() {
  local name="$1"
  cron_list_raw | grep -Fi "$name" | awk '{print $1}' | grep -E '^[A-Za-z0-9_-]+$' || true
}

first_job_id_named() {
  local name="$1"
  job_ids_named "$name" | head -n 1
}

create_daily_job() {
  hermes -p ceo cron create "0 8 * * *" "$(cat "$DAILY_PROMPT_FILE")" --name "$DAILY_NAME"
}

create_health_job() {
  hermes -p ceo cron create "*/30 * * * *" "$(cat "$HEALTH_PROMPT_FILE")" --name "$HEALTH_NAME"
}

create_jobs() {
  has_job_named "$DAILY_NAME" || create_daily_job
  has_job_named "$HEALTH_NAME" || create_health_job
}

remove_duplicates_for_name() {
  local name="$1"
  local first
  local ids
  first="$(first_job_id_named "$name")"
  [ -n "$first" ] || return 0
  ids="$(job_ids_named "$name")"
  while IFS= read -r id; do
    [ -z "$id" ] && continue
    if [ "$id" != "$first" ]; then
      log "Removing duplicate job $id for '$name'"
      hermes -p ceo cron remove "$id" || warn "Failed to remove duplicate $id"
    fi
  done <<< "$ids"
}

remove_duplicates() {
  remove_duplicates_for_name "$DAILY_NAME"
  remove_duplicates_for_name "$HEALTH_NAME"
}

resume_all() {
  local id
  for name in "$DAILY_NAME" "$HEALTH_NAME"; do
    id="$(first_job_id_named "$name")"
    [ -n "$id" ] || continue
    hermes -p ceo cron resume "$id" || warn "Resume failed for $name ($id)"
  done
}

ensure_jobs() {
  create_jobs
  remove_duplicates
}

recreate_jobs() {
  local id
  for name in "$DAILY_NAME" "$HEALTH_NAME"; do
    while IFS= read -r id; do
      [ -n "$id" ] || continue
      hermes -p ceo cron remove "$id" || warn "Failed removing $id"
    done <<< "$(job_ids_named "$name")"
  done
  create_jobs
}

list_jobs() {
  hermes -p ceo cron list
}

status_jobs() {
  hermes -p ceo cron status || true
  hermes -p ceo cron list || true
}

run_daily() {
  local id
  id="$(first_job_id_named "$DAILY_NAME")"
  [ -n "$id" ] || { echo "Daily pipeline job not found"; return 1; }
  hermes -p ceo cron run "$id"
}

run_intelligence() {
  bash "$ROOT_DIR/scripts/run_external_intelligence.sh"
}

run_analysis_loop() {
  bash "$ROOT_DIR/scripts/run_signal_analysis_loop.sh"
}

run_decision_packages() {
  python "$ROOT_DIR/scripts/generate_decision_package.py"
  python "$ROOT_DIR/scripts/derive_execution_package.py"
  python "$ROOT_DIR/scripts/derive_board_briefing.py"
  python "$ROOT_DIR/scripts/generate_operating_visibility.py"
}

run_visibility() {
  python "$ROOT_DIR/scripts/generate_operating_visibility.py"
}

run_governed_action() {
  [ "$#" -ge 2 ] || { echo "Usage: bash orchestration/cron/commands.sh run-governed-action <action-id> <command...>"; return 1; }
  local action_id="$1"
  shift
  python "$ROOT_DIR/scripts/enforce_governed_action.py" --action-id "$action_id" --command "$@"
}

pause_all() {
  local id
  for name in "$DAILY_NAME" "$HEALTH_NAME"; do
    id="$(first_job_id_named "$name")"
    [ -n "$id" ] || continue
    hermes -p ceo cron pause "$id" || warn "Pause failed for $name ($id)"
  done
}

case "$ACTION" in
  create) create_jobs ;;
  ensure) ensure_jobs ;;
  recreate) recreate_jobs ;;
  remove-duplicates) remove_duplicates ;;
  resume-all) resume_all ;;
  list) list_jobs ;;
  status) status_jobs ;;
  run-daily) run_daily ;;
  run-intelligence) run_intelligence ;;
  run-analysis-loop) run_analysis_loop ;;
  run-decision-packages) run_decision_packages ;;
  run-visibility) run_visibility ;;
  run-governed-action)
    shift
    run_governed_action "$@"
    ;;
  pause-all) pause_all ;;
  *)
    echo "Usage: bash orchestration/cron/commands.sh [create|ensure|recreate|remove-duplicates|resume-all|list|status|run-daily|run-intelligence|run-analysis-loop|run-decision-packages|run-visibility|run-governed-action|pause-all]"
    exit 1
    ;;
esac
