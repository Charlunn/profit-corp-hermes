# Profit-Corp Hermes

## Current Milestone

- **v1.3 Hermes-First Autonomous Company Interface** - Phases 26-29 (planned 2026-05-05)

## Milestones

- **v1.3 Hermes-First Autonomous Company Interface** - Phases 26-29 (planned)
- **v1.2 Autonomous Project Launch Loop** - Phases 22-25 (shipped 2026-05-05)
- **v1.1.2 Real-SaaS Delivery Governance Hardening** - Phases 18-21 (shipped 2026-05-04)
- **v1.1.1 Delivery Pipeline Reliability Fixes** - Phases 14-17 (shipped 2026-04-30)
- **v1.1 SaaS Delivery Factory** - Phases 7-13 (shipped 2026-04-28)
- **v1.0 milestone** - Phases 1-6 (shipped 2026-04-26)

## Proposed Roadmap

**4 phases** | **12 requirements mapped** | All covered

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 26 | Hermes Intent Gateway and Unified Project Start | Turn "start a new project" into one Hermes-native entrypoint that hides pipeline internals | HERMES-01, HERMES-02, HERMES-03 | Complete (2026-05-05) |
| 27 | Hermes Internal Role Routing and Delivery Handoff | Make Hermes orchestrate company roles and delivery specialists internally | ROLE-01, ROLE-02, ROLE-03 | Complete (2026-05-05) |
| 28 | Hermes Proposal and Approval Surface | Make proposal presentation and approval feel like one Hermes conversation instead of a bundle of subsystems | PROP-01, PROP-02, PROP-03 | Complete (2026-05-05) |
| 29 | Hermes Final Delivery Experience and Blocked Recovery | Return the final URL or blocked recovery context as the natural result of the same Hermes workflow | AUTO-01, AUTO-02, AUTO-03 | Complete (2026-05-05) |

## Phase Details

### Phase 26: Hermes Intent Gateway and Unified Project Start

**Goal:** Let the owner tell Hermes to start a project without selecting scripts, phases, or transport-specific entrypoints.

**Requirements:** `HERMES-01`, `HERMES-02`, `HERMES-03`

**Success criteria:**
1. Hermes exposes one top-level "start project" capability that becomes the canonical launch path.
2. That capability creates one authoritative run using the shipped 22-25 governed machinery instead of inventing a second state model.
3. Healthy-path operator output speaks in Hermes terms rather than script or phase names.
4. Internal launch details remain inspectable for governance but are not required for normal operator use.

### Phase 27: Hermes Internal Role Routing and Delivery Handoff

**Goal:** Keep all company and delivery roles behind Hermes so the owner talks to one system while Hermes coordinates the specialists.

**Requirements:** `ROLE-01`, `ROLE-02`, `ROLE-03`

**Success criteria:**
1. Hermes invokes `ceo`, `scout`, `cmo`, and `arch` internally as part of project discovery and qualification.
2. Hermes hands approved work to delivery specialists without requiring the owner to run stage-specific commands.
3. Hermes role configuration remains profile-and-skill driven instead of ad hoc runtime glue.
4. Operator-facing messages can explain which internal role is acting without forcing the owner to control that role directly.

### Phase 28: Hermes Proposal and Approval Surface

**Goal:** Present one proposal and one approval loop as a clean Hermes conversation surface while preserving the locked contract underneath.

**Requirements:** `PROP-01`, `PROP-02`, `PROP-03`

**Success criteria:**
1. Hermes renders one concise evidence-backed proposal with pain, target user, feasibility, pricing proof, and launch framing.
2. The owner can approve or reject the proposal by replying to Hermes instead of thinking about pipeline artifacts.
3. Approval still persists the same locked delivery contract already enforced by the shipped governance backbone.
4. Missing freshness, feasibility, pricing proof, or approval linkage still blocks hard rather than being smoothed over in the interface.

### Phase 29: Hermes Final Delivery Experience and Blocked Recovery

**Goal:** Make final success and blocked recovery feel like normal Hermes outputs from the same start-to-finish workflow.

**Requirements:** `AUTO-01`, `AUTO-02`, `AUTO-03`

**Success criteria:**
1. Hermes continues approved work through design, development, testing, GitHub, Vercel, and final handoff without healthy-path manual resumes.
2. Final success returns the live URL and concise ship summary as the natural result of the original Hermes request.
3. Blocked outcomes return failed stage, reason, and recovery context in owner-facing language.
4. Success and blocked replies still derive from authoritative persisted truth rather than transient process memory.
