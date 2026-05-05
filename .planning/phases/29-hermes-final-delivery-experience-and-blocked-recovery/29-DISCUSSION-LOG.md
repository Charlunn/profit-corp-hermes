# Phase 29: Hermes Final Delivery Experience and Blocked Recovery - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-05-05
**Phase:** 29-Hermes Final Delivery Experience and Blocked Recovery
**Areas discussed:** final success surface, blocked recovery surface, healthy-path autonomy and surfaced truth, recovery boundary

---

## Final success surface

| Option | Description | Selected |
|--------|-------------|----------|
| One final Hermes reply | Return URL plus concise ship summary as the natural workflow result | Yes |
| Separate reporting workflow | Require the owner to fetch final artifacts manually | |
| Verbose internal dump | Expose raw delivery logs and pipeline stages as the primary success output | |

**User's choice:** Auto-selected one final Hermes reply.
**Notes:** This keeps the operator experience aligned with the milestone goal of Hermes as the single company interface.

---

## Blocked recovery surface

| Option | Description | Selected |
|--------|-------------|----------|
| Explicit blocked reply | Report failed stage, reason, and recovery context clearly | Yes |
| Soft degraded warning | Keep the run looking mostly healthy despite blockers | |
| Raw artifact-only recovery | Force the owner to inspect status files to understand failure | |

**User's choice:** Auto-selected explicit blocked reply.
**Notes:** The owner should not need pipeline archaeology to know whether intervention is required.

---

## Healthy-path autonomy and surfaced truth

| Option | Description | Selected |
|--------|-------------|----------|
| Autonomous until final truth | Hermes continues after approval and reports only authoritative outcomes | Yes |
| Manual healthy-path resumes | Owner continues to trigger later stages explicitly | |
| Memory-based final response | Hermes summarizes from transient runtime state without artifact convergence | |

**User's choice:** Auto-selected autonomous progression tied to authoritative surfaced truth.
**Notes:** This preserves the v1.2 backbone while making the visible experience feel more natural.

---

## Recovery boundary

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse current recovery model | Surface existing resume/block truth more clearly | Yes |
| Build new chat-native recovery engine | Replace current blocked/resume mechanics entirely | |
| Hide recovery details | Avoid surfacing the exact recovery context | |

**User's choice:** Auto-selected reuse of the current recovery model.
**Notes:** Phase 29 is about owner-facing packaging of outcomes, not replacing the shipped exceptional-path machinery.

---

## the agent's Discretion

- Exact wording and layout for final success and blocked replies
- Exact backlink set surfaced with final messages
- Exact rendering seam used to convert delivery truth into Hermes-facing output

## Deferred Ideas

- Retry/redirect/cancel commands remain future recovery work
- Multi-channel final notification expansion remains future scope
