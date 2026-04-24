---
phase: 01-external-intelligence-foundation
verified: 2026-04-24T09:25:00Z
status: gaps_found
score: 6/8 must-haves verified
requirements:
  - SIGN-01
  - SIGN-02
  - SIGN-03
  - ANLY-01
---

# Phase 1: External Intelligence Foundation Verification Report

**Phase Goal:** Establish reliable external-source intake for trend, competitor, and complaint signals, with structured normalization and source history.
**Verified:** 2026-04-24T09:25:00Z
**Status:** gaps_found

## Result
Phase 1 established the structural intake foundation: approved-source registry slots exist for trend, competitor, and complaint categories; normalized signal schema and storage locations are defined; a deterministic collector and shell wrapper are implemented; run history persists to `assets/shared/external_intelligence/history/runs.jsonl`; and the intake path is wired into cron helpers, daily pipeline flow, and smoke checks.

The blocking gap is that no approved public source URLs are configured or enabled yet, so the system cannot currently demonstrate real ingestion of trend, competitor, and complaint signals from approved public sources. This means the phase foundation is in place, but the phase goal is not fully achieved in actual runtime behavior.

## Requirements Check
- **SIGN-01** — BLOCKED: trend source slot exists, but no approved trend URL is configured or enabled in `assets/shared/external_intelligence/SOURCES.yaml`.
- **SIGN-02** — BLOCKED: competitor source slot exists, but no approved competitor URL is configured or enabled in `assets/shared/external_intelligence/SOURCES.yaml`.
- **SIGN-03** — BLOCKED: complaint source slot exists, but no approved complaint/community URL is configured or enabled in `assets/shared/external_intelligence/SOURCES.yaml`.
- **ANLY-01** — PASS: collector emits one normalized structure with deterministic IDs, timestamps, evidence path, category metadata, and append-only history targets.

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | A checked-in source registry defines at least one source slot for each category: trend, competitor, and complaint | ✓ VERIFIED | `assets/shared/external_intelligence/SOURCES.yaml` contains `trend-public-01`, `competitor-public-01`, `complaint-public-01` with matching categories |
| 2 | The repo contains a documented normalized signal schema and storage layout for raw captures, run logs, and signal history | ✓ VERIFIED | `assets/shared/external_intelligence/LATEST_SUMMARY.md` defines normalized fields; storage paths are implemented in `scripts/collect_external_signals.py` |
| 3 | Shared-state governance explicitly describes how external intelligence artifacts are written and read | ✓ VERIFIED | `docs/STATE_CONTRACT.md` adds `assets/shared/external_intelligence/` and keeps the `manage_finance.py` ledger rule intact |
| 4 | The repo includes a deterministic collector that reads the checked-in source registry and emits normalized signal records | ✓ VERIFIED | `scripts/collect_external_signals.py` loads `SOURCES.yaml`, supports `--window-hours`, `--dry-run`, `--source-id`, and writes JSONL history paths |
| 5 | The collector supports at least one public-source entry for each category: trend, competitor, and complaint | ✓ VERIFIED | Source registry has one starter slot per category and collector supports `rss` and `page` kinds used by those slots |
| 6 | The operator has a stable command path to run external-intelligence collection outside ad-hoc manual steps | ✓ VERIFIED | `scripts/run_external_intelligence.sh` and `orchestration/cron/commands.sh` `run-intelligence` action both execute successfully |
| 7 | Operator can run a repeatable collection flow that ingests trend, competitor, and complaint signals from approved public sources | ✗ FAILED | All starter sources have empty `base_url` values and `enabled: false`, so no approved public-source ingestion occurs in live runs |
| 8 | Signal history is persisted so later phases can compare new signals against previously seen inputs | ? PARTIAL | `runs.jsonl` is persisted and `signals.jsonl` path exists in code, but no real source has been enabled to prove normalized signal history accumulation |

**Score:** 6/8 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `assets/shared/external_intelligence/SOURCES.yaml` | Approved-source registry template | ✓ EXISTS + SUBSTANTIVE | Three category-specific source entries with required fields |
| `assets/shared/external_intelligence/LATEST_SUMMARY.md` | Normalized schema + latest summary template | ✓ EXISTS + SUBSTANTIVE | Lists normalized fields and category sections |
| `docs/STATE_CONTRACT.md` | Governance coverage for external intelligence artifacts | ✓ EXISTS + SUBSTANTIVE | Adds external intelligence artifact family and concurrency notes |
| `scripts/collect_external_signals.py` | Deterministic collector | ✓ EXISTS + SUBSTANTIVE | Implements registry loading, adapters, normalization, dedupe, history/raw paths |
| `scripts/run_external_intelligence.sh` | Stable operator wrapper | ✓ EXISTS + SUBSTANTIVE | Resolves Python and runs collector with passthrough args |
| `orchestration/cron/external_intelligence.prompt.md` | Cron intake prompt | ✓ EXISTS + SUBSTANTIVE | Directs CEO intake flow and summary reading |
| `orchestration/cron/commands.sh` | Named command-hub action | ✓ EXISTS + SUBSTANTIVE | Includes `run-intelligence` action |
| `scripts/smoke_test_pipeline.sh` | Verification coverage | ✓ EXISTS + SUBSTANTIVE | Validates files, compile check, dry run, and `run-intelligence` |

**Artifacts:** 8/8 verified

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|-----|--------|---------|
| `scripts/run_external_intelligence.sh` | `scripts/collect_external_signals.py` | shell invocation | ✓ WIRED | Wrapper calls collector with `--window-hours 24` and passes through extra args |
| `orchestration/cron/commands.sh` | intake flow | `run-intelligence` action | ✓ WIRED | `run-intelligence` invokes `bash "$ROOT_DIR/scripts/run_external_intelligence.sh"` |
| `orchestration/cron/daily_pipeline.prompt.md` | external intelligence artifacts | pre-Scout step | ✓ WIRED | Daily pipeline adds intake step and reads `assets/shared/external_intelligence/LATEST_SUMMARY.md` |
| `scripts/collect_external_signals.py` | run history | `runs.jsonl` append | ✓ WIRED | Non-dry runs append metadata to `assets/shared/external_intelligence/history/runs.jsonl` |
| enabled public source config | actual signal ingestion | live collector run | ✗ NOT WIRED | No approved URLs are configured or enabled, so collection path produces no real signal records |

**Wiring:** 4/5 connections verified

## Evidence
- `assets/shared/external_intelligence/SOURCES.yaml`
- `assets/shared/external_intelligence/LATEST_SUMMARY.md`
- `assets/shared/external_intelligence/history/runs.jsonl`
- `scripts/collect_external_signals.py`
- `scripts/run_external_intelligence.sh`
- `orchestration/cron/commands.sh`
- `orchestration/cron/daily_pipeline.prompt.md`
- `orchestration/cron/external_intelligence.prompt.md`
- `scripts/smoke_test_pipeline.sh`
- `docs/STATE_CONTRACT.md`
- `bash scripts/run_external_intelligence.sh --dry-run`
- `bash orchestration/cron/commands.sh run-intelligence`
- `bash scripts/smoke_test_pipeline.sh`

## Human Verification Required
None — the blocking issue is missing configured approved sources, not a UI-only behavior.

## Gaps Summary

### Critical Gaps (Block Progress)

1. **Approved source activation missing**
   - Missing: Real approved public URLs and enabled source entries for trend, competitor, and complaint collection
   - Impact: The phase cannot yet ingest real public signals, so the primary phase goal remains unproven in runtime behavior
   - Fix: Populate `assets/shared/external_intelligence/SOURCES.yaml` with approved public source URLs, enable at least one source per category, then run the collector and verify normalized `signals.jsonl` entries are created

2. **Normalized signal history not yet proven with live inputs**
   - Missing: Actual normalized records in `assets/shared/external_intelligence/history/signals.jsonl`
   - Impact: Later phases cannot rely on real historical signal comparison until at least one live collection run succeeds
   - Fix: After enabling approved sources, execute the intake flow and verify `signals.jsonl` contains normalized records for at least one source per category

### Non-Critical Gaps (Can Defer)
None.

## Recommended Fix Plans

### 01-04-PLAN.md: Activate approved source registry and prove live ingestion

**Objective:** Configure approved public sources and verify that the live intake path produces normalized signal history.

**Tasks:**
1. Replace placeholder source entries with approved public URLs and enable one source per category.
2. Run the collector through the shell/cron entrypoints and capture normalized `signals.jsonl` output plus updated latest summary.
3. Add verification checks for live-ingestion success conditions and rerun smoke/phase verification.

**Estimated scope:** Small

## Verification Metadata

**Verification approach:** Goal-backward (derived from phase goal)
**Must-haves source:** PLAN.md frontmatter
**Automated checks:** 8 artifacts verified, 4/5 key links verified
**Human checks required:** 0
**Total verification time:** 12 min

---
*Verified: 2026-04-24T09:25:00Z*
*Verifier: Claude (manual fallback; gsd-verifier subagent unavailable due to tool channel error)*
