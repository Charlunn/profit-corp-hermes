# Phase 12: Credential Governance and Operator Handoff - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-27
**Phase:** 12-credential-governance-and-operator-handoff
**Areas discussed:** Credential access path, Audit trail model, Platform-change boundary, Operator review surface

---

## Credential access path

| Option | Description | Selected |
|--------|-------------|----------|
| Platform-controlled wrappers | Route GitHub/Vercel actions through approved-project scripts and command wrappers only | ✓ |
| Workspace-local direct CLI | Let delivery roles run GitHub/Vercel CLI directly inside workspaces | |
| Shared admin shell | Expose a broader operator shell with reusable credentials for manual or scripted use | |

**User's choice:** `[auto]` Platform-controlled wrappers
**Notes:** Recommended because Phases 10-11 already centralize shipping through approved-project authority records and script wrappers; this preserves constrained credential use.

---

## Audit trail model

| Option | Description | Selected |
|--------|-------------|----------|
| Extend existing event stream | Add credentialed action evidence and outcomes to the approved-delivery append-only event flow | ✓ |
| Separate credential audit log | Create an independent parallel audit system for credential usage only | |
| Status-only logging | Surface final success/failure in markdown without durable machine-readable action records | |

**User's choice:** `[auto]` Extend existing event stream
**Notes:** Recommended because the repo already validates append-only authority events and latest-view status rendering; reusing that pattern keeps replay and validation coherent.

---

## Platform-change boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Protected-surface gate + justification | Detect changes to protected template/shared-backend surfaces and require explicit governed justification before shipping continues | ✓ |
| Conformance-only after the fact | Rely on late validation only, without a dedicated justification requirement | |
| Trust delivery roles | Allow protected-platform edits during delivery unless an operator notices and intervenes manually | |

**User's choice:** `[auto]` Protected-surface gate + justification
**Notes:** Recommended because the template contract already defines protected primitives; Phase 12 should turn that into an explicit governance checkpoint before sync/deploy.

---

## Operator review surface

| Option | Description | Selected |
|--------|-------------|----------|
| One exception-first authority review artifact | Show approval, blocked reasons, GitHub/Vercel outcomes, platform-justification decisions, and final handoff status in one operator-facing file | ✓ |
| Multiple specialized files | Keep separate governance, deployment, and handoff views with no consolidated operator summary | |
| Success-focused ship report | Emphasize completed actions and leave failures/blocked states in lower-level evidence files | |

**User's choice:** `[auto]` One exception-first authority review artifact
**Notes:** Recommended because Hermes already favors calm, markdown-first latest views; Phase 12 should make failures and blocked states visible without forcing manual reconstruction.

---

## Claude's Discretion

- Exact artifact names and JSON schema additions for credential-governance evidence and final review outputs
- Exact touched-path detection mechanism for platform-level versus product-level change classification
- Exact distribution of checks between existing Phase 11 helpers and any new Phase 12 governance wrapper scripts

## Deferred Ideas

- Secret vault rotation and broader credential lifecycle systems
- Multi-environment governance beyond the current first-deploy flow
- Portfolio-level dashboards across many approved-project delivery runs
