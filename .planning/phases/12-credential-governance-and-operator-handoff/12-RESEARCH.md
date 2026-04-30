# Phase 12: Credential Governance and Operator Handoff - Research

**Date:** 2026-04-27
**Phase:** 12
**Status:** Complete

## Objective

Research how to implement credential governance, protected-platform change justification, and final operator review controls on top of the existing approved-project delivery pipeline.

## Key Findings

- Phase 12 should harden the existing approved-delivery authority pipeline instead of creating a second deployment subsystem.
- GitHub and Vercel credential use should remain constrained to the approved delivery path: repository preparation, code sync, Vercel linkage, environment application, and deployment.
- Auditability should reuse the current append-only approved-delivery event stream plus evidence files, not a separate audit database or standalone logger.
- Platform-vs-product enforcement should be a deterministic touched-path classification step driven by the protected surfaces already defined in `docs/platform/standalone-saas-template-contract.md`.
- Final operator review should stay markdown-first and authority-layer scoped, with exception-first visibility for blocked deliveries, approval failures, deployment failures, and protected-change attempts.

## Current Stack and Existing Foundations

### Existing scripts and helpers
- `scripts/start_approved_project_delivery.py` already owns the authority-layer stage machine from approval through handoff.
- `scripts/github_delivery_common.py` already encapsulates constrained GitHub repository preparation and sync behavior, including blocked evidence for missing `gh` or auth.
- `scripts/vercel_delivery_common.py` already encapsulates constrained Vercel linkage, env application, and deploy gating, including blocked evidence for missing `VERCEL_TOKEN` or missing prerequisites.
- `scripts/render_approved_delivery_status.py` already renders a concise operator latest view from authority events and shipping metadata.
- `scripts/validate_approved_delivery_pipeline.py` already validates blocked evidence, GitHub/Vercel linkage visibility, and final handoff linkage.

### Existing contracts and patterns
- `docs/STATE_CONTRACT.md` already defines governed high-impact action behavior and state boundaries.
- `docs/OPERATIONS.md` already documents the approved-project start/status/validate/resume flow.
- `docs/platform/standalone-saas-template-contract.md` already defines protected platform paths, protected behaviors, and conformance invariants.
- The repo already prefers script-driven orchestration, append-only artifacts, and markdown latest views over service-side hidden state.

## Recommended Architecture

### 1. Credential-governed action wrapper layer
Wrap each credential-bearing GitHub/Vercel action in a narrow governance-aware entrypoint that:
- records action intent
- invokes the existing helper
- persists success/blocked/failure evidence
- appends an authority-layer event linked to the approved project and delivery run

### 2. Protected-change classification gate
Before GitHub sync and before Vercel deploy, inspect the candidate changed paths and classify them as:
- product-level only
- protected platform / shared-backend touching
- blocked because justification is required or missing

This should be driven by deterministic path matching against protected surfaces in the template/shared-backend contract.

### 3. Platform-justification approval bridge
If protected surfaces are touched:
- generate a justification artifact in the approved-project authority area
- request governed approval through the existing governance machinery
- persist a blocked state with evidence and resume-from-stage metadata until approval is granted

### 4. Final operator review artifact
Produce one authority-layer markdown review artifact that consolidates:
- approval summary
- protected-change classification result
- governance/justification status
- GitHub action outcomes
- Vercel action outcomes
- blocked prerequisite evidence
- final handoff status
- clear action-required section

## Planning Implications by Requirement

### GOV-01
Hermes needs one documented, platform-controlled credential path. Planning should extend existing wrappers and authority-layer scripts rather than exposing direct delivery-role CLI access.

### GOV-02
Credential use must be restricted to approved delivery actions only. Planning should define an explicit allowlist and enforce it at wrapper/authority level.

### GOV-03
Every repository creation, sync, environment configuration, and deployment action needs a durable audit trail. Planning should reuse append-only events plus per-action evidence artifacts.

### GOV-04
Hermes must distinguish platform-level changes from product-level changes. Planning should add deterministic touched-path classification before shipping stages proceed.

### GOV-05
Protected template/shared-backend modifications must require explicit justification. Planning should reuse governance request/approval flows and blocked resume semantics.

### GOV-06
Hermes must surface blocked deliveries, failed approvals, deployment failures, and final handoff status in an operator-visible review artifact. Planning should keep this artifact authority-layer, markdown-first, and exception-oriented.

## Recommended Implementation Slices

### Slice A - Credential audit contract
Define the machine-readable shape for credential-bearing actions:
- action type
- target repository/project/service
- stage
- outcome
- evidence path
- delivery run linkage
- timestamp
- block/failure reason

### Slice B - Protected-surface detection
Add deterministic path classification using:
- protected template files and routes
- shared-backend contract files and paths
- possibly known authority/governance surfaces if needed to prevent delivery-time self-mutation

### Slice C - Governance bridge
Add a platform-justification artifact plus approval/request plumbing that reuses existing governance event/status patterns.

### Slice D - Operator review renderer
Render one final authority-layer review artifact from the approved-project record, event stream, shipping metadata, justification artifacts, and final handoff linkage.

### Slice E - Validation and tests
Extend validator/test coverage so the governance layer is provable and resumable.

## Pitfalls to Avoid

- Do not create a second source of truth for audit history.
- Do not detect protected changes only after sync or deploy has already happened.
- Do not assume `gh` or `vercel` are always installed; preserve blocked-state evidence paths.
- Do not rely on markdown-only governance state without machine-readable backing data.
- Do not make protected-surface matching so broad that normal product delivery is constantly blocked.

## Validation Architecture

Phase 12 validation should extend the existing `unittest`-style strategy already used by the repo.

### Automated checks to plan for
- unit tests for protected-path classification
- unit tests for credential-action audit payload generation
- unit tests for justification artifact validation
- integration-style tests for blocked/resume behavior when protected changes require governed approval
- integration-style tests for final review artifact rendering with blocked, failed, and completed states
- validator expansion in `scripts/validate_approved_delivery_pipeline.py` to assert:
  - audit artifacts exist for credential-bearing stages
  - protected-change / justification blocks are visible
  - final operator review contains required governance and failure visibility

### Manual / environment-sensitive checks
- confirm blocked evidence remains explicit when `gh` is unavailable or GitHub auth is missing
- confirm blocked evidence remains explicit when `VERCEL_TOKEN` is unavailable or Vercel linkage/env prerequisites are missing

## Environment Notes

- Python and Node-based tooling appear to be part of the repo’s expected workflow.
- GitHub CLI and Vercel CLI availability should be treated as environment-sensitive and not assumed by the plan.
- Plans should preserve current blocked-state behavior instead of assuming live external automation will always succeed.

## Canonical Files for Planning

- `.planning/phases/12-credential-governance-and-operator-handoff/12-CONTEXT.md`
- `.planning/ROADMAP.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `docs/STATE_CONTRACT.md`
- `docs/OPERATIONS.md`
- `docs/platform/standalone-saas-template-contract.md`
- `scripts/start_approved_project_delivery.py`
- `scripts/github_delivery_common.py`
- `scripts/vercel_delivery_common.py`
- `scripts/render_approved_delivery_status.py`
- `scripts/validate_approved_delivery_pipeline.py`

## Planning Summary

Phase 12 should be planned as a narrow governance hardening layer on top of the existing authority pipeline, centered on:
1. protected-change detection
2. credentialed-action audit wrapping
3. governed platform-justification flow
4. final operator-facing review rendering
5. validator and test expansion
