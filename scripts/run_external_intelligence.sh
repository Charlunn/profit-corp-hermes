#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
COLLECTOR_PATH="$ROOT_DIR/scripts/collect_external_signals.py"
PYTHON_BIN=""

resolve_python() {
  if command -v python >/dev/null 2>&1 && python -V >/dev/null 2>&1; then
    PYTHON_BIN="python"
  elif [ -x "/c/Users/42236/AppData/Local/hermes/hermes-agent/venv/Scripts/python" ]; then
    PYTHON_BIN="/c/Users/42236/AppData/Local/hermes/hermes-agent/venv/Scripts/python"
  elif command -v py >/dev/null 2>&1; then
    PYTHON_BIN="py -3"
  else
    printf '[external-intelligence] missing usable python interpreter\n' >&2
    exit 1
  fi
}

resolve_python

if [ "$PYTHON_BIN" = "py -3" ]; then
  py -3 "$COLLECTOR_PATH" --window-hours 24 "$@"
else
  "$PYTHON_BIN" "$COLLECTOR_PATH" --window-hours 24 "$@"
fi
