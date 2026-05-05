# Phase 22: Conversational Intake and Run Orchestration - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md; this log preserves the auto-selected alternatives.

**Date:** 2026-05-04
**Phase:** 22-conversational-intake-and-run-orchestration
**Mode:** auto discuss
**Areas discussed:** chat trigger contract, authoritative intake artifacts, downstream orchestration bridge, operator-visible status

## Chat trigger contract

| Option | Description | Selected |
|---|---|---|
| Normalized chat envelope | Map Discord/Telegram events into one governed intake schema before orchestration. | Yes |
| Platform-specific start flows | Keep separate Discord and Telegram orchestration contracts. | |
| Chat transcript only | Treat the original message text as the only durable intake source. | |

**User's choice:** Auto-selected normalized chat envelope.
**Notes:** Best fit with prior authority-first governance patterns and keeps later phases platform-agnostic.

## Authoritative intake artifacts

| Option | Description | Selected |
|---|---|---|
| Authority record + events + derived status | Persist one machine-readable source of truth plus append-only history and rendered status. | Yes |
| Event log only | Keep append-only history without a single current-state record. | |
| Bot-memory state | Hold run state inside the chat integration process. | |

**User's choice:** Auto-selected authority-first artifact family.
**Notes:** Aligns with approved-project and delivery governance contracts already used in the repo.

## Downstream orchestration bridge

| Option | Description | Selected |
|---|---|---|
| Thin chat adapter into existing pipeline | Normalize intake, then dispatch the governed startup path already used locally. | Yes |
| Chat-only workflow stack | Build a new orchestration path dedicated to chat starts. | |
| Manual operator handoff | Only create an intake artifact and wait for terminal commands. | |

**User's choice:** Auto-selected thin adapter into the existing governed path.
**Notes:** Avoids workflow drift and preserves reuse of resume/recovery behavior.

## Operator-visible status

| Option | Description | Selected |
|---|---|---|
| Derived chat replies from authoritative state | Reply to the originating conversation using rendered/derived run status. | Yes |
| Freeform bot updates | Let the integration compose status messages ad hoc. | |
| Local-status only | Keep status in files/terminal without chat-thread feedback. | |

**User's choice:** Auto-selected derived chat replies from authoritative state.
**Notes:** Keeps operator visibility tied to the same persisted truth that later recovery will use.

## the agent's Discretion

- Exact shape of the Discord and Telegram raw-to-normalized field mapping.
- Exact artifact directory layout for pre-approval chat runs.

## Deferred Ideas

- Multi-operator notification fan-out.
- Chat-native failure recovery commands.
- Additional chat channels beyond Discord and Telegram.
