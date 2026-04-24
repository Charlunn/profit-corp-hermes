# Phase 1 Research — External Intelligence Foundation

**Phase:** 1 — External Intelligence Foundation  
**Date:** 2026-04-24  
**Status:** Ready for planning

## Goal

Establish a repeatable intake path for public trend, competitor, and complaint signals that fits the repo's existing Hermes + cron + file-artifact operating model.

## Repo Constraints That Matter

- Shared durable artifacts should live under `assets/shared/` and remain human-auditable.
- High-risk shared-state mutation rules in `docs/STATE_CONTRACT.md` apply; Phase 1 should avoid adding new direct writers to `LEDGER.json` or other protected state.
- Daily orchestration already flows through `orchestration/cron/commands.sh` and prompt files, so Phase 1 should plug into that pattern instead of inventing a new scheduler.
- Smoke coverage is shell-based in `scripts/smoke_test_pipeline.sh`; new intake pieces should be verifiable there.

## Recommended Technical Shape

### 1. Source model

Use a checked-in source registry file rather than hard-coded URLs inside prompts.

Recommended artifact:
- `assets/shared/external_intelligence/SOURCES.yaml`

Each source entry should declare:
- `id`: stable source identifier
- `category`: `trend | competitor | complaint`
- `kind`: `rss | sitemap | page | forum-search | manual-seed`
- `display_name`
- `base_url`
- `collection_method`: deterministic fetch strategy
- `enabled`: boolean
- `poll_window_hours`
- `dedupe_key_fields`: list such as `url`, `title`, `published_at`
- `notes`: operator-visible caveats

Why: it keeps approved public sources explicit, reviewable, and easy to extend without editing code paths.

### 2. Signal normalization schema

Normalize every collected item into one JSON object shape before downstream role analysis.

Recommended normalized fields:
- `signal_id`: deterministic hash of canonical URL + title + published timestamp
- `source_id`
- `source_category`: `trend | competitor | complaint`
- `collected_at`
- `published_at`
- `title`
- `summary`
- `url`
- `evidence_text`
- `entities`: array of named competitors/products/topics
- `tags`: array
- `language`
- `confidence`: `high | medium | low`
- `raw_artifact_path`
- `normalization_version`

Why: later phases need one consistent structure for scoring, dedupe, role routing, and evidence traceability.

### 3. Storage pattern

Use append-oriented history plus per-run raw snapshots.

Recommended artifacts:
- `assets/shared/external_intelligence/raw/<source_id>/<timestamp>.json`
- `assets/shared/external_intelligence/history/signals.jsonl`
- `assets/shared/external_intelligence/history/runs.jsonl`
- `assets/shared/external_intelligence/LATEST_SUMMARY.md`

Rationale:
- raw snapshots preserve source evidence for audits
- `signals.jsonl` gives append-friendly durable history
- `runs.jsonl` records run metadata, counts, and failures
- markdown summary keeps the operator-facing artifact aligned with the repo's existing document workflow

### 4. Collection strategy

Prefer deterministic adapters first:
- RSS/Atom feeds for trends when available
- static HTML fetch + parse for public competitor changelogs/blogs
- public forum or community pages with explicit pagination/search URLs
- manual seed sources only as a temporary fallback, but still normalize them into the same schema

Avoid Phase 1 dependence on brittle browser automation or unofficial logged-in scraping. Phase 1 needs repeatability more than maximum coverage.

### 5. Idempotency and history

Collector should be safe to rerun for the same window.

Implementation rules:
- derive `signal_id` deterministically
- append to history only when `signal_id` is new
- record duplicate counts in `runs.jsonl`
- preserve raw fetch artifact even if all normalized signals dedupe out for the run

### 6. Evidence attribution

Every normalized signal should retain:
- original URL
- source registry ID
- raw artifact path
- published timestamp if available
- extraction timestamp

This is necessary for later governance and management-grade outputs.

## Integration Recommendation

### Daily rhythm fit

Phase 1 should add a dedicated intake script and then hook it into the cron operating rhythm.

Recommended execution sequence:
1. run external-intelligence collector
2. persist normalized history + run log
3. generate concise summary artifact for CEO/Scout consumption
4. keep existing role-analysis loop changes for Phase 2

This avoids overloading the current `daily_pipeline.prompt.md` with collection logic before the collector exists.

### Suggested command surface

- `python3 scripts/collect_external_signals.py --window-hours 24`
- `bash scripts/run_external_intelligence.sh`
- optional cron action in `orchestration/cron/commands.sh` to run intake explicitly

## Public-Source Constraints

Phase 1 should only target approved public sources and should keep source approval in the checked-in registry. Do not require credentials, authenticated scraping, or mutation of third-party systems.

## Validation Hooks

Add smoke checks for:
- required source registry file exists
- collector script syntax is valid
- collector `--help` or `--dry-run` exits 0
- history directory and latest summary artifact are created after a sample run

## Planning Implications

A clean 3-plan split is:
1. define source registry, normalized schema, and storage layout
2. implement deterministic collectors for one initial source per category
3. persist history and wire the collector into the repo's operating rhythm + smoke checks

## Risks to Avoid

- embedding source definitions directly in prompts or shell scripts
- storing only markdown summaries without machine-readable history
- mixing raw source text with normalized records in one file
- adding direct writes to protected shared state unrelated to Phase 1
- trying to build ranking/scoring in Phase 1 before intake reliability exists

## Recommended starter sources

Use one public source per category for the first implementation slice:
- trend: RSS/blog/news feed with timestamps
- competitor: public product changelog or release notes page
- complaint: public forum/community search page or complaint thread listing

The exact sites can remain configurable in `SOURCES.yaml`.

## RESEARCH COMPLETE
