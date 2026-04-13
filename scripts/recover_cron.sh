#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

printf '[recover] Ensuring cron jobs...\n'
bash "$ROOT_DIR/orchestration/cron/commands.sh" ensure

printf '[recover] Resuming known cron jobs...\n'
bash "$ROOT_DIR/orchestration/cron/commands.sh" resume-all || true

printf '[recover] Cron status...\n'
bash "$ROOT_DIR/orchestration/cron/commands.sh" status

printf '[recover] Done\n'
