# Phase 10: Approved Project Delivery Pipeline - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the auto-selected implementation decisions.

**Date:** 2026-04-27
**Phase:** 10-approved-project-delivery-pipeline
**Areas discussed:** Approval-to-delivery trigger, Project brief generation, Workspace instantiation and attachment, Delivery state model, Blocking and failure behavior
**Mode:** auto

## Auto-Selected Gray Areas
- Approval-to-delivery trigger
- Project brief generation
- Workspace instantiation and attachment
- Delivery state model
- Blocking and failure behavior

## Auto Decisions Applied

### Approval-to-delivery trigger
- **Question:** What should turn an approved opportunity into a live pipeline run?
- **Auto-selected:** Use one explicit owner approval signal that produces a delivery-ready project record and triggers the orchestrator-first pipeline.
- **Why this default:** Matches the project’s one-time approval philosophy and existing command-entry orchestration pattern.

### Project brief generation
- **Question:** What artifact should downstream delivery start from?
- **Auto-selected:** Generate one deterministic delivery-ready project brief that captures project identity, scope, target user, MVP framing, constraints, and acceptance gates.
- **Why this default:** Gives the Phase 9 delivery team the fixed input bundle it now expects without reconstructing chat context.

### Workspace instantiation and attachment
- **Question:** How should the pipeline create and bind the new project workspace?
- **Auto-selected:** Reuse the existing template-instantiation path, then attach the approved brief and `.hermes` metadata/guardrail artifacts as pipeline initialization outputs.
- **Why this default:** Avoids duplicating template bootstrap logic and preserves the governed shared-template/shared-backend contract.

### Delivery state model
- **Question:** How should Hermes track pipeline progress?
- **Auto-selected:** Track state as a durable dual-surface pipeline record: machine-readable workflow state plus a concise human-readable latest view aligned to the Phase 9 delivery stages.
- **Why this default:** Reuses the repo’s existing artifact-first status pattern and avoids a translation layer between pipeline setup and delivery execution.

### Blocking and failure behavior
- **Question:** What should happen when prerequisites are missing or a stage fails?
- **Auto-selected:** Hard-block the pipeline with explicit persisted reasons and resume/retry state instead of silently degrading forward or forcing a restart.
- **Why this default:** Matches the repo’s governance/conformance gate philosophy and the milestone requirement for reliable blocking behavior.

## Corrections Made

No corrections — auto mode accepted the recommended defaults.

## Deferred Ideas
- GitHub sync and deploy linkage deferred to Phase 11.
- Credential governance and deeper operator-facing review hardening deferred to Phase 12.
- Portfolio-level analytics and dashboards remain out of scope.
- Product feature implementation remains out of scope for this phase.
