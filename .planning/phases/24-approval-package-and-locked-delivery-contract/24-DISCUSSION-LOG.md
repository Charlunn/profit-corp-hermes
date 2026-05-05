# Phase 24: Approval Package and Locked Delivery Contract - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md; this log preserves the auto-selected alternatives.

**Date:** 2026-05-04
**Phase:** 24-approval-package-and-locked-delivery-contract
**Mode:** auto discuss
**Areas discussed:** proposal bundle, chat approval protocol, locked contract persistence, drift governance

## Proposal bundle

| Option | Description | Selected |
|---|---|---|
| One concise evidence-backed proposal bundle | Give the operator a single approval object with backlinks to qualification evidence. | Yes |
| Multiple approval documents | Ask the operator to inspect several separate artifacts before approving. | |
| Narrative-only summary | Provide a short chat summary without durable proposal structure. | |

**User's choice:** Auto-selected one concise evidence-backed proposal bundle.
**Notes:** Best matches the milestone goal of one-shot approval.

## Chat approval protocol

| Option | Description | Selected |
|---|---|---|
| Governed chat approval mapped to existing approval events | Treat chat approve/reject as durable authority transitions. | Yes |
| Bot-local approval memory | Keep chat approvals inside the integration only. | |
| Manual terminal confirmation after chat | Require chat plus local command confirmation. | |

**User's choice:** Auto-selected governed chat approval mapped to existing events.
**Notes:** Preserves auditability and avoids approval-state drift.

## Locked contract persistence

| Option | Description | Selected |
|---|---|---|
| Extend approved-project authority record | Persist the locked contract in `APPROVED_PROJECT.json` and related artifacts. | Yes |
| Create separate contract record type | Add a new downstream record family dedicated to locked proposals. | |
| Keep contract only in markdown | Freeze the contract in prose without a machine-readable source of truth. | |

**User's choice:** Auto-selected extending the approved-project authority record.
**Notes:** Reuses the shipped delivery backbone and keeps downstream readers stable.

## Drift governance

| Option | Description | Selected |
|---|---|---|
| Block on drift and require governed reopen | Stop silent scope/pricing/acceptance changes and open explicit blocked state. | Yes |
| Warning-only drift detection | Report contract drift but allow delivery to continue. | |
| Specialist discretion | Let downstream specialists reinterpret approved scope. | |

**User's choice:** Auto-selected block on drift with governed reopen.
**Notes:** Necessary to satisfy the "locked delivery contract" requirement.

## the agent's Discretion

- Exact chat message syntax for approve/reject.
- Exact field nesting used to persist locked-contract values in the approved-project record.

## Deferred Ideas

- Multi-operator approval subscriptions.
- Chat-native recovery commands after approval.
