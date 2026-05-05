# Requirements: Profit-Corp Hermes

**Defined:** 2026-05-05
**Core Value:** Turn noisy web-wide user pain signals into clear, governed decisions about what is worth building next - and ensure approved opportunities become real, launchable SaaS products rather than ceremonial agent output.

## v1 Requirements

### Hermes Interface

- [x] **HERMES-01**: The owner can tell Hermes to start a new project without choosing scripts, phases, or backend entrypoints.
- [x] **HERMES-02**: Hermes translates that top-level intent into one authoritative project run using the existing governed launch loop.
- [x] **HERMES-03**: Hermes keeps internal pipeline mechanics hidden from the owner during healthy execution and only exposes proposal, approval, blocked recovery, and final shipped result.

### Internal Role Orchestration

- [x] **ROLE-01**: Hermes invokes `ceo`, `scout`, `cmo`, and `arch` as internal collaborators for discovery, qualification, market proof, and proposal synthesis.
- [x] **ROLE-02**: Hermes hands approved work to the delivery specialist team internally instead of requiring the owner to switch tools or run stage-specific commands.
- [x] **ROLE-03**: Role execution remains configured inside Hermes profiles and skills rather than being recast as ad hoc operator-run glue.

### Proposal and Approval Experience

- [x] **PROP-01**: Hermes presents one evidence-backed proposal that summarizes the pain point, target user, feasibility, pricing evidence, and launch framing.
- [x] **PROP-02**: The owner can approve or reject the proposal by replying to Hermes, and approval persists the same locked delivery contract already enforced by the shipped pipeline.
- [x] **PROP-03**: If Hermes cannot prove freshness, market evidence, feasibility, or approval linkage, it blocks instead of pretending the project is ready.

### Autonomous Delivery and Return Link

- [x] **AUTO-01**: After approval, Hermes continues through design, development, testing, GitHub, Vercel, and final handoff without healthy-path manual resumes.
- [x] **AUTO-02**: Hermes returns the final live deployment URL and concise ship summary as the normal success output of the same top-level project request.
- [x] **AUTO-03**: If delivery blocks, Hermes reports the failed stage, reason, and recovery context in owner-facing language without requiring the owner to inspect pipeline internals first.

## v2 Requirements

### Conversational Recovery

- **RECO-01**: The owner can tell Hermes to retry, redirect, or cancel a blocked run directly from the same conversation.
- **RECO-02**: Hermes can explain which internal role or gate is currently blocking and what evidence is still missing before retry.

### Multi-Channel Expansion

- **CHAN-01**: Hermes can expose the same project-start and approval loop consistently across additional channels beyond the initial operator surface.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Replacing the shipped authority/event/artifact pipeline with a brand new workflow engine | This milestone is about packaging the existing loop behind Hermes, not discarding the backbone that now works |
| Forcing the owner to manage discovery, approval, delivery, or deployment via raw scripts | Direct script choreography is the exact operator experience this milestone is meant to remove |
| Building a generic chat platform unrelated to project launch and delivery | The focus is Hermes as the company interface, not a standalone messaging product |
| Reopening GitHub/Vercel/shared-template reliability work as the main milestone scope | Those capabilities already shipped and should now be reused as internal Hermes machinery |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| HERMES-01 | Phase 26 | Complete |
| HERMES-02 | Phase 26 | Complete |
| HERMES-03 | Phase 26 | Complete |
| ROLE-01 | Phase 27 | Complete |
| ROLE-02 | Phase 27 | Complete |
| ROLE-03 | Phase 27 | Complete |
| PROP-01 | Phase 28 | Complete |
| PROP-02 | Phase 28 | Complete |
| PROP-03 | Phase 28 | Complete |
| AUTO-01 | Phase 29 | Complete |
| AUTO-02 | Phase 29 | Complete |
| AUTO-03 | Phase 29 | Complete |

**Coverage:**
- v1 requirements: 12 total
- Mapped to phases: 12
- Unmapped: 0

---
*Requirements defined: 2026-05-05*
*Last updated: 2026-05-05 after Phase 29 completion*
