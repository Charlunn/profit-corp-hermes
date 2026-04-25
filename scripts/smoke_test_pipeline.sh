#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0
PYTHON_BIN=""

ok() { printf '[smoke] PASS: %s\n' "$*"; }
fail() { printf '[smoke] FAIL: %s\n' "$*"; FAILED=1; }

require_cmd() {
  if command -v "$1" >/dev/null 2>&1; then
    ok "command found: $1"
  else
    fail "missing command: $1"
  fi
}

resolve_python() {
  if command -v python3 >/dev/null 2>&1 && python3 -V >/dev/null 2>&1; then
    PYTHON_BIN="python3"
    ok "command found: python3"
  elif command -v python >/dev/null 2>&1 && python -V >/dev/null 2>&1; then
    PYTHON_BIN="python"
    ok "command found: python"
  else
    fail "missing usable command: python3/python"
  fi
}

check_file_nonempty() {
  local f="$1"
  if [ -s "$f" ]; then
    ok "file exists and non-empty: $f"
  else
    fail "file missing or empty: $f"
  fi
}

run_check() {
  local label="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    ok "$label"
  else
    fail "$label"
  fi
}

main() {
  require_cmd hermes
  resolve_python
  require_cmd bash

  check_file_nonempty "$ROOT_DIR/assets/shared/LEDGER.json"
  check_file_nonempty "$ROOT_DIR/assets/shared/manage_finance.py"
  check_file_nonempty "$ROOT_DIR/assets/shared/external_intelligence/SOURCES.yaml"
  check_file_nonempty "$ROOT_DIR/assets/shared/external_intelligence/triage/prioritized_signals.json"
  check_file_nonempty "$ROOT_DIR/assets/shared/external_intelligence/triage/clusters.json"
  check_file_nonempty "$ROOT_DIR/assets/shared/PAIN_POINTS.md"
  check_file_nonempty "$ROOT_DIR/assets/shared/MARKET_PLAN.md"
  check_file_nonempty "$ROOT_DIR/assets/shared/TECH_SPEC.md"
  check_file_nonempty "$ROOT_DIR/assets/shared/CEO_RANKING.md"
  check_file_nonempty "$ROOT_DIR/assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md"
  check_file_nonempty "$ROOT_DIR/assets/shared/execution_packages/EXECUTION_PACKAGE.md"
  check_file_nonempty "$ROOT_DIR/assets/shared/board_briefings/BOARD_BRIEFING.md"
  check_file_nonempty "$ROOT_DIR/assets/shared/trace/decision_package_trace.json"
  check_file_nonempty "$ROOT_DIR/scripts/collect_external_signals.py"
  check_file_nonempty "$ROOT_DIR/scripts/triage_external_signals.py"
  check_file_nonempty "$ROOT_DIR/scripts/generate_role_handoffs.py"
  check_file_nonempty "$ROOT_DIR/scripts/generate_decision_package.py"
  check_file_nonempty "$ROOT_DIR/scripts/derive_execution_package.py"
  check_file_nonempty "$ROOT_DIR/scripts/derive_board_briefing.py"
  check_file_nonempty "$ROOT_DIR/scripts/run_external_intelligence.sh"
  check_file_nonempty "$ROOT_DIR/scripts/run_signal_analysis_loop.sh"
  check_file_nonempty "$ROOT_DIR/orchestration/cron/external_intelligence.prompt.md"
  check_file_nonempty "$ROOT_DIR/orchestration/cron/daily_pipeline.prompt.md"
  check_file_nonempty "$ROOT_DIR/orchestration/cron/health_check.prompt.md"
  check_file_nonempty "$ROOT_DIR/orchestration/cron/commands.sh"

  for p in ceo scout cmo arch accountant; do
    check_file_nonempty "$ROOT_DIR/profiles/$p/config.yaml.example"
    check_file_nonempty "$ROOT_DIR/profiles/$p/SOUL.md"
  done

  if [ -n "$PYTHON_BIN" ]; then
    run_check "finance script syntax" "$PYTHON_BIN" -m py_compile "$ROOT_DIR/assets/shared/manage_finance.py"
    run_check "external intelligence collector syntax" "$PYTHON_BIN" -m py_compile "$ROOT_DIR/scripts/collect_external_signals.py"
    run_check "signal triage syntax" "$PYTHON_BIN" -m py_compile "$ROOT_DIR/scripts/triage_external_signals.py"
    run_check "role handoff generator syntax" "$PYTHON_BIN" -m py_compile "$ROOT_DIR/scripts/generate_role_handoffs.py"
    run_check "decision package generator syntax" "$PYTHON_BIN" -m py_compile "$ROOT_DIR/scripts/generate_decision_package.py"
    run_check "execution package generator syntax" "$PYTHON_BIN" -m py_compile "$ROOT_DIR/scripts/derive_execution_package.py"
    run_check "board briefing generator syntax" "$PYTHON_BIN" -m py_compile "$ROOT_DIR/scripts/derive_board_briefing.py"
  fi
  run_check "external intelligence dry run" bash "$ROOT_DIR/scripts/run_external_intelligence.sh" --dry-run
  run_check "signal analysis loop run" bash "$ROOT_DIR/scripts/run_signal_analysis_loop.sh" --window-hours 48 --limit 3 --date 2026-04-25
  check_file_nonempty "$ROOT_DIR/assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md"
  check_file_nonempty "$ROOT_DIR/assets/shared/execution_packages/EXECUTION_PACKAGE.md"
  check_file_nonempty "$ROOT_DIR/assets/shared/board_briefings/BOARD_BRIEFING.md"
  check_file_nonempty "$ROOT_DIR/assets/shared/trace/decision_package_trace.json"
  run_check "cron helper run-intelligence action" bash "$ROOT_DIR/orchestration/cron/commands.sh" run-intelligence
  run_check "cron helper run-analysis-loop action" bash "$ROOT_DIR/orchestration/cron/commands.sh" run-analysis-loop
  run_check "cron helper run-decision-packages action" bash "$ROOT_DIR/orchestration/cron/commands.sh" run-decision-packages
  run_check "cron helper list action" bash "$ROOT_DIR/orchestration/cron/commands.sh" list
  run_check "ceo cron list command" hermes -p ceo cron list
  run_check "profile list command" hermes profile list

  if [ "$FAILED" -eq 0 ]; then
    printf '\n[smoke] OVERALL: PASS\n'
  else
    printf '\n[smoke] OVERALL: FAIL\n'
    exit 1
  fi
}

main "$@"
