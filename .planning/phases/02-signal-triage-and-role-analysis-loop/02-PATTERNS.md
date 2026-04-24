# Phase 2 Pattern Map — Signal Triage and Role Analysis Loop

**Phase:** 2 — Signal Triage and Role Analysis Loop  
**Date:** 2026-04-25

## Closest Existing Repo Patterns

### 1. Shared artifact storage

Closest analogs:
- `assets/shared/external_intelligence/history/signals.jsonl`
- `assets/shared/external_intelligence/history/runs.jsonl`
- `assets/shared/external_intelligence/LATEST_SUMMARY.md`
- `assets/shared/TEMPLATES.md`

Pattern to reuse:
- durable shared artifacts live under `assets/shared/`
- machine-readable state and human-readable summaries live side by side
- append-only history is separate from current working state

Phase 2 recommendation:
- add a mutable triage/read-model layer under `assets/shared/external_intelligence/triage/`
- keep operator-facing markdown in `assets/shared/PAIN_POINTS.md`

### 2. Deterministic Python utility

Closest analog:
- `scripts/collect_external_signals.py`

Pattern to reuse:
- single-purpose Python CLI
- path resolution relative to `__file__`
- deterministic file reads/writes
- append-only history plus explicit rerun-safe outputs

Phase 2 recommendation:
- implement triage/scoring logic in a dedicated script under `scripts/`
- keep scoring / dedupe / clustering file-oriented, not prompt-only

### 3. Shell entrypoint / orchestration wrapper

Closest analogs:
- `scripts/run_external_intelligence.sh`
- `orchestration/cron/commands.sh`
- `scripts/smoke_test_pipeline.sh`

Pattern to reuse:
- stable shell wrappers expose named actions
- orchestration commands should be explicit named entrypoints
- smoke coverage should validate files and command execution

Phase 2 recommendation:
- add one stable shell wrapper for triage/analysis loop if needed
- extend `orchestration/cron/commands.sh` with a named action rather than embedding logic in prompts
- extend smoke checks only where Phase 2 wiring needs runtime validation

### 4. Role contract pattern

Closest analog:
- `assets/shared/TEMPLATES.md`

Pattern to reuse:
- each role has a specific artifact contract
- quantitative fields already exist for Scout, CMO, and CEO outputs
- downstream artifacts should be generated from shared upstream context

Phase 2 recommendation:
- generate `PAIN_POINTS.md` first as the shared shortlist artifact
- route the same prioritized working set into `MARKET_PLAN.md`, `TECH_SPEC.md`, and CEO ranking output

## Recommended File Placement

### Shared triage state
- `assets/shared/external_intelligence/triage/prioritized_signals.json`
- `assets/shared/external_intelligence/triage/clusters.json`

### Role artifacts
- `assets/shared/PAIN_POINTS.md`
- `assets/shared/MARKET_PLAN.md`
- `assets/shared/TECH_SPEC.md`

### Execution logic
- `scripts/triage_external_signals.py` — dedupe, clustering, scoring, prioritized read model
- optional `scripts/run_signal_analysis_loop.sh` — stable wrapper for role loop execution

### Orchestration
- `orchestration/cron/commands.sh` — only if adding a named action such as `run-analysis-loop`
- `orchestration/cron/daily_pipeline.prompt.md` — update to consume triage artifacts explicitly once available

### Verification
- `scripts/smoke_test_pipeline.sh` — extend with triage script syntax and command checks if Phase 2 wiring reaches runtime

## Conflict Avoidance

To keep Phase 2 plans cleanly separated:
- Plan 02-01 should own scoring / dedupe / clustering logic and triage read-model files
- Plan 02-02 should own role handoff artifacts and shared role-input structure
- Plan 02-03 should own CEO synthesis integration and end-to-end daily-loop wiring

## Summary

Use `signals.jsonl` as immutable source history, add triage read models under `assets/shared/external_intelligence/triage/`, generate `PAIN_POINTS.md` as the shared shortlist artifact, and wire distinct role outputs over the same prioritized set.
