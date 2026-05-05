# Phase 28: Hermes Proposal and Approval Surface - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-05-05
**Phase:** 28-Hermes Proposal and Approval Surface
**Areas discussed:** proposal surface shape, approval and rejection semantics, locked delivery contract persistence, hard-block governance at the Hermes surface

---

## Proposal surface shape

| Option | Description | Selected |
|--------|-------------|----------|
| One concise proposal object | Hermes presents a single approval-ready recommendation with backlinks | Yes |
| Multi-artifact review bundle | Owner reviews several parallel docs before deciding | |
| Raw subsystem outputs | Discovery/qualification artifacts are shown directly | |

**User's choice:** Auto-selected one concise proposal object.
**Notes:** This best matches the milestone goal of Hermes as the only visible company surface.

---

## Approval and rejection semantics

| Option | Description | Selected |
|--------|-------------|----------|
| Reply-to-Hermes approval | Owner approves or rejects by replying in the same conversation | Yes |
| Separate command/tool approval | Owner must invoke a dedicated approval command | |
| Soft inferred approval | Hermes guesses approval from vague conversation signals | |

**User's choice:** Auto-selected reply-to-Hermes approval with durable linkage.
**Notes:** The underlying approval still needs to be idempotent and governed rather than conversationally inferred.

---

## Locked delivery contract persistence

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse approved-project contract | Persist the same locked delivery contract the pipeline already consumes | Yes |
| New conversation-only contract | Keep approval state primarily in Hermes messages | |
| Dual contract systems | Maintain one chat contract and one delivery contract | |

**User's choice:** Auto-selected reuse of the approved-project contract.
**Notes:** This keeps downstream delivery and validation compatible with the shipped backbone.

---

## Hard-block governance at the Hermes surface

| Option | Description | Selected |
|--------|-------------|----------|
| Preserve hard blocks | Missing proof or broken approval linkage still blocks | Yes |
| Convert gaps to warnings | Hermes can proceed with caveats for a smoother UX | |
| Hide blockers behind retries | Hermes retries silently rather than surfacing gating truth | |

**User's choice:** Auto-selected preservation of hard blocks.
**Notes:** Cleaner conversation design should not weaken the core governance promise of the system.

---

## the agent's Discretion

- Exact proposal layout and section order
- Exact phrase-matching and idempotency approach for approve/reject replies
- Exact set of backlink references exposed in the Hermes proposal surface

## Deferred Ideas

- Final delivery and blocked recovery response design belongs to Phase 29
- Multi-party approval models remain future scope
