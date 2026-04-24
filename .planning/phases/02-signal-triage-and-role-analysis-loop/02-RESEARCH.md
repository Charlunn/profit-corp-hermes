# Phase 2 Research — Signal Triage and Role Analysis Loop

**Phase:** 2 — Signal Triage and Role Analysis Loop  
**Date:** 2026-04-25  
**Status:** Ready for planning

## Goal

Convert the normalized pain-signal history from Phase 1 into a prioritized, deduplicated working set that can be consumed by Scout, CMO, Arch, CEO, and Accountant without collapsing into one generic summary.

## Current Repo State That Matters

- Phase 1 now writes normalized discovery records to `assets/shared/external_intelligence/history/signals.jsonl` and run metadata to `assets/shared/external_intelligence/history/runs.jsonl`.
- `assets/shared/external_intelligence/LATEST_SUMMARY.md` is an operator-facing snapshot, but it is not yet the right artifact for role consumption or ranking decisions.
- `assets/shared/TEMPLATES.md` already defines downstream artifact expectations:
  - `PAIN_POINTS.md` expects scoring-ready leads with urgency, MVP-hours, monetization, competition, confidence, and evidence links.
  - CMO scorecards expect quantitative dimensions and a total score formula.
  - CEO ranking output expects a Top 3 ranked list plus recommendation.
- `orchestration/cron/daily_pipeline.prompt.md` already assumes a Scout → CMO → Architect → CEO → Accountant sequence, but the actual structured handoff artifacts for that loop do not exist yet.
- There is no existing Phase 2 directory or Phase 2 implementation code yet.

## Repo Constraints That Matter

- Shared durable artifacts should still live under `assets/shared/` and remain human-auditable.
- Phase 2 should reuse Phase 1 artifacts rather than inventing a parallel storage system.
- Phase 2 should not jump ahead into fully polished decision packages (`DECI-*`) or executable governance controls (`GOV-*`).
- Role-specific outputs should remain file-based and deterministic enough for later cron integration and verification.

## Recommended Technical Shape

### 1. Introduce a triage/read-model artifact layer

Phase 2 needs a stable intermediate artifact between raw normalized signals and role outputs.

Recommended artifacts:
- `assets/shared/external_intelligence/triage/prioritized_signals.json` — the current deduplicated, scored working set
- `assets/shared/external_intelligence/triage/clusters.json` — grouped related signals / repeated complaints / merged candidate ideas
- `assets/shared/PAIN_POINTS.md` — Scout-facing scoring-ready shortlist for the current loop

Why:
- `signals.jsonl` is append-only history and should remain the source ledger, not the active working set.
- A read model allows safe reruns and deterministic role input generation.
- `PAIN_POINTS.md` already fits the expected downstream workflow and template system.

### 2. Deduplication and clustering rules should be explicit and file-driven

Phase 2 should define deterministic heuristics for:
- near-duplicate complaint titles
- repeated URLs or repeated canonical topics
- grouped clusters of similar pain expressions
- cluster-level evidence counts and recency

Recommended dimensions:
- normalized title similarity
- shared URL/canonical URL
- overlapping keywords/entities
- recency from `collected_at` / `published_at`

Why:
- The same pain may appear many times across discovery runs or sites.
- Later ranking should operate on candidate opportunities, not raw duplicated fragments.

### 3. Scoring should align with existing templates

Use the fields already implied in `assets/shared/TEMPLATES.md` rather than inventing a brand-new score model.

Recommended first-pass dimensions for Scout/CMO handoff:
- urgency pain
- evidence strength / evidence count
- recency
- estimated MVP hours (heuristic placeholder allowed)
- monetization signal (heuristic placeholder allowed)
- competition signal (optional / low-weight)
- confidence

Why:
- This makes `PAIN_POINTS.md` directly usable.
- CMO scorecard math already exists in template form.
- It reduces translation work when the daily loop is wired.

### 4. Role outputs should be distinct and sequenced

Phase 2 must not end with a single generic synthesis blob.

Recommended handoff artifacts:
- Scout: `assets/shared/PAIN_POINTS.md`
- CMO: `assets/shared/MARKET_PLAN.md` seeded from ranked shortlist
- Architect: `assets/shared/TECH_SPEC.md` seeded from the same shortlist
- CEO: ranked recommendation artifact or structured section in `PAIN_POINTS.md`
- Accountant: audit/risk response remains command-driven, but should consume the same recommended idea context

Why:
- `ANLY-03` requires distinct role outputs over the same prioritized set.
- The existing daily pipeline prompt already encodes this sequence.

## Planning Implications

A clean 3-plan split is:
1. build scoring, dedupe, and clustering read models from `signals.jsonl`
2. generate role handoff artifacts over the same prioritized signal set
3. integrate CEO synthesis and end-to-end daily analysis loop verification

## Risks to Avoid

- mixing append-only history and mutable triage state in one file
- putting ranking/scoring only in markdown with no machine-readable intermediate model
- letting each role read raw `signals.jsonl` independently instead of consuming the same prioritized set
- implementing decision-package polish or governance enforcement in Phase 2
- adding brittle AI-only scoring with no deterministic fallback structure

## RESEARCH COMPLETE
