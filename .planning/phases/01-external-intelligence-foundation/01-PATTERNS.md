# Phase 1 Pattern Map — External Intelligence Foundation

**Phase:** 1 — External Intelligence Foundation  
**Date:** 2026-04-24

## Closest Existing Repo Patterns

### 1. Shared artifact storage

Closest analogs:
- `assets/shared/LEDGER.json`
- `assets/shared/CORP_CULTURE.md`
- `assets/shared/KNOWLEDGE_BASE.md`
- `assets/shared/TEMPLATES.md`

Pattern to reuse:
- durable shared artifacts live in `assets/shared/`
- markdown is used for operator-readable summaries
- structured machine-readable files also live beside human-readable artifacts when they are authoritative

Phase 1 recommendation:
- create `assets/shared/external_intelligence/` as the root for source registry, raw captures, history, and latest summary

### 2. Deterministic Python utility

Closest analog:
- `assets/shared/manage_finance.py`

Pattern to reuse:
- single-purpose Python entrypoint
- path resolution relative to `__file__`
- durable append/write behavior
- safe rerun expectations

Phase 1 recommendation:
- put collector logic in `scripts/collect_external_signals.py`
- keep it deterministic and file-oriented rather than prompt-only
- use relative path resolution so it runs cross-platform from repo root or cron wrappers

### 3. Shell entrypoint / orchestration wrapper

Closest analogs:
- `orchestration/cron/commands.sh`
- `scripts/smoke_test_pipeline.sh`
- `scripts/recover_cron.sh`

Pattern to reuse:
- shell wrappers expose stable named actions
- repo root inferred from script location
- smoke checks validate key files and command execution

Phase 1 recommendation:
- add `scripts/run_external_intelligence.sh` as the stable operator entrypoint
- extend `orchestration/cron/commands.sh` only for named orchestration actions, not parsing logic
- extend smoke test with collector syntax/help checks and artifact existence checks

### 4. Cron prompt pattern

Closest analogs:
- `orchestration/cron/daily_pipeline.prompt.md`
- `orchestration/cron/health_check.prompt.md`

Pattern to reuse:
- one prompt per cron concern
- concise execution contract in markdown
- human-readable, repo-committed prompt payloads

Phase 1 recommendation:
- if a dedicated intake cron prompt is needed, place it at `orchestration/cron/external_intelligence.prompt.md`
- if intake is invoked as part of daily operations, keep the prompt focused on calling the shell/Python entrypoint and summarizing artifacts, not reimplementing parsing in prompt text

## Recommended File Placement

### New directory root
- `assets/shared/external_intelligence/`

### Inside that directory
- `SOURCES.yaml` — approved public-source registry
- `README.md` or `LATEST_SUMMARY.md` — operator-facing current snapshot
- `history/signals.jsonl` — append-only normalized signal history
- `history/runs.jsonl` — append-only run metadata
- `raw/<source_id>/...` — raw fetched artifacts grouped by source

### Execution logic
- `scripts/collect_external_signals.py` — normalized collection + persistence
- `scripts/run_external_intelligence.sh` — stable shell wrapper for operator/cron use

### Orchestration
- `orchestration/cron/external_intelligence.prompt.md` — optional dedicated intake cron prompt
- `orchestration/cron/commands.sh` — only if adding named action such as `run-intelligence`

### Verification
- `scripts/smoke_test_pipeline.sh` — extend with collector checks

## Naming Conventions To Match

- shell files: snake_case with `.sh`
- Python utility: snake_case with `.py`
- operator/governance markdown: uppercase or descriptive title style
- shared state directories: lowercase under `assets/shared/`

## File Ownership Guidance

- Source registry + normalized history are shared infrastructure artifacts, not role-owned business conclusions
- CEO should orchestrate when these artifacts are read downstream
- Scout is the most natural primary consumer in later phases, but Phase 1 should keep artifact ownership neutral and shared

## Conflict Avoidance

To keep later parallel plan execution safe:
- Plan 01 should own schema/storage definition files under `assets/shared/external_intelligence/`
- Plan 02 should own collector implementation files in `scripts/`
- Plan 03 should own orchestration and smoke-test wiring in `orchestration/cron/` and `scripts/smoke_test_pipeline.sh`

This yields minimal same-wave overlap and clean dependencies.

## Summary

Use `assets/shared/external_intelligence/` for durable artifacts, `scripts/collect_external_signals.py` for deterministic collection, `scripts/run_external_intelligence.sh` for stable execution, and existing cron/smoke patterns for orchestration and verification.
