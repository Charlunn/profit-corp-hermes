#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN=""
TRIAGE_ARGS=()
HANDOFF_ARGS=()
DECISION_ARGS=()
DERIVED_ARGS=()

resolve_python() {
  if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
    PYTHON_BIN="python3"
  elif command -v python >/dev/null 2>&1 && python -V >/dev/null 2>&1; then
    PYTHON_BIN="python"
  elif [ -x "/c/Users/42236/AppData/Local/hermes/hermes-agent/venv/Scripts/python" ]; then
    PYTHON_BIN="/c/Users/42236/AppData/Local/hermes/hermes-agent/venv/Scripts/python"
  elif command -v py >/dev/null 2>&1; then
    PYTHON_BIN="py -3"
  else
    printf '[analysis-loop] missing usable python interpreter\n' >&2
    exit 1
  fi
}

run_python() {
  if [ "$PYTHON_BIN" = "py -3" ]; then
    py -3 "$@"
  else
    "$PYTHON_BIN" "$@"
  fi
}

parse_args() {
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --window-hours)
        [ "$#" -ge 2 ] || { printf '[analysis-loop] missing value for --window-hours\n' >&2; exit 1; }
        TRIAGE_ARGS+=("$1" "$2")
        shift 2
        ;;
      --limit)
        [ "$#" -ge 2 ] || { printf '[analysis-loop] missing value for --limit\n' >&2; exit 1; }
        TRIAGE_ARGS+=("$1" "$2")
        HANDOFF_ARGS+=("$1" "$2")
        shift 2
        ;;
      --date)
        [ "$#" -ge 2 ] || { printf '[analysis-loop] missing value for --date\n' >&2; exit 1; }
        HANDOFF_ARGS+=("$1" "$2")
        DECISION_ARGS+=("$1" "$2")
        DERIVED_ARGS+=("$1" "$2")
        shift 2
        ;;
      --dry-run)
        TRIAGE_ARGS+=("$1")
        HANDOFF_ARGS+=("$1")
        DECISION_ARGS+=("$1")
        DERIVED_ARGS+=("$1")
        shift
        ;;
      *)
        TRIAGE_ARGS+=("$1")
        HANDOFF_ARGS+=("$1")
        shift
        ;;
    esac
  done
}

resolve_python
parse_args "$@"

run_python "$ROOT_DIR/scripts/triage_external_signals.py" "${TRIAGE_ARGS[@]}"
run_python "$ROOT_DIR/scripts/generate_role_handoffs.py" "${HANDOFF_ARGS[@]}"
run_python "$ROOT_DIR/scripts/generate_decision_package.py" "${DECISION_ARGS[@]}"
run_python "$ROOT_DIR/scripts/derive_execution_package.py" "${DERIVED_ARGS[@]}"
run_python "$ROOT_DIR/scripts/derive_board_briefing.py" "${DERIVED_ARGS[@]}"
