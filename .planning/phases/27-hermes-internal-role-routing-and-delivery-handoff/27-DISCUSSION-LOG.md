# Phase 27: Hermes Internal Role Routing and Delivery Handoff - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-05-05
**Phase:** 27-Hermes Internal Role Routing and Delivery Handoff
**Areas discussed:** internal company-role orchestration, operator-visible abstraction of role work, approved-work handoff to delivery specialists, profile-and-skill governance

---

## Internal company-role orchestration

| Option | Description | Selected |
|--------|-------------|----------|
| Hermes owns role routing | Hermes internally chooses and sequences roles | Yes |
| Owner chooses roles | Operator decides which role to invoke next | |
| Hybrid manual routing | Hermes suggests roles but owner still orchestrates | |

**User's choice:** Auto-selected Hermes-owned role routing.
**Notes:** This matches the milestone goal that the owner talks to one system rather than coordinating company roles manually.

---

## Operator-visible abstraction of role work

| Option | Description | Selected |
|--------|-------------|----------|
| Explain work without exposing tools | Hermes reports what kind of work is happening in owner-facing language | Yes |
| Expose raw role identities in normal flow | Owner sees and manages explicit role handoffs | |
| Hide all role context completely | Hermes gives no indication of internal work or blockers | |

**User's choice:** Auto-selected explanation without exposing tools.
**Notes:** The owner should understand progress and blockers, but not have to operate the role system directly.

---

## Approved-work handoff to delivery specialists

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse approved-project handoff seams | Hermes hands approved work into the existing delivery backbone | Yes |
| Build a new Hermes-only delivery kickoff | Create a fresh delivery-start contract for v1.3 | |
| Manual post-approval operator resume | Keep owner responsible for starting delivery stages | |

**User's choice:** Auto-selected reuse of the approved-project handoff seams.
**Notes:** This preserves compatibility with the shipped automation backbone and its validators.

---

## Profile-and-skill governance

| Option | Description | Selected |
|--------|-------------|----------|
| Profile-and-skill driven routing | Keep routing inspectable in repo/profile contracts | Yes |
| Hidden prompt-only branching | Store routing logic implicitly in Hermes conversation behavior | |
| Per-run custom orchestration glue | Assemble routing case-by-case for each project | |

**User's choice:** Auto-selected profile-and-skill-driven routing.
**Notes:** This is the most maintainable brownfield path and aligns with how the repo already manages role behavior.

---

## the agent's Discretion

- Exact internal role sequence and trigger rules
- Exact owner-facing wording for role-progress updates
- Exact trace-artifact storage shape for routing and handoff observability

## Deferred Ideas

- Proposal/approval interaction specifics belong to Phase 28
- Final success and blocked recovery experience belongs to Phase 29
