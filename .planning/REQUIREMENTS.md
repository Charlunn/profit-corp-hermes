# Requirements: Profit-Corp Hermes

**Defined:** 2026-05-04
**Core Value:** Turn noisy web-wide user pain signals into clear, governed decisions about what is worth building next - and ensure approved opportunities become real, launchable SaaS products rather than ceremonial agent output.

## v1 Requirements

### Conversational Intake

- [ ] **CHAT-01**: Operator can start a new project run by mentioning Hermes in a Discord or Telegram group.
- [ ] **CHAT-02**: Hermes records the originating chat platform, channel/thread, requester, and message intent in the authoritative project-run artifacts.
- [ ] **CHAT-03**: Chat-triggered project runs invoke the same governed approved-project pipeline instead of a separate ad hoc path.

### Qualification Gates

- [ ] **QUAL-01**: Hermes only proposes project candidates whose supporting pain evidence was collected within the last 72 hours.
- [ ] **QUAL-02**: Hermes must prove each proposed pain point is real, user-facing, and specific enough to support a narrow SaaS workflow.
- [ ] **QUAL-03**: Hermes must prove the proposed product is feasible on the shared template, shared Supabase, and governed delivery stack before approval.
- [ ] **QUAL-04**: Hermes must attach market, competitor, and pricing evidence to each proposal and block approval when those artifacts are missing.

### Proposal Approval

- [ ] **PROP-01**: Hermes presents one operator-facing proposal bundle that summarizes pain point, target user, scope, pricing, market rationale, and expected launch path.
- [ ] **PROP-02**: Operator can approve or reject the proposal from chat, and approval persists a single authoritative approved-project contract.

### Autonomous Delivery

- [ ] **AUTO-01**: Approved-project contracts lock scope, pricing, language requirements, and acceptance gates so downstream delivery cannot drift silently.
- [ ] **AUTO-02**: After approval, Hermes continues through design, development, testing, GitHub, and Vercel without requiring manual stage resumes on healthy runs.
- [ ] **AUTO-03**: Hermes must use real specialist output and real implementation evidence for delivery proof instead of self-generated placeholder artifacts.
- [ ] **AUTO-04**: When deployment completes, Hermes returns the live link and concise ship summary to the originating chat thread.

## v2 Requirements

### Recovery and Expansion

- **RECO-01**: Operator can recover or redirect a failed autonomous run directly from chat without opening the terminal.
- **COLL-01**: Multiple operators can subscribe to proposal approvals and delivery completion notifications for the same run.
- **CHAN-01**: Hermes can launch the same autonomous loop from additional channels beyond Discord and Telegram.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Building a generic multi-tenant chat platform inside Hermes | The milestone is about launching projects from chat, not creating a standalone messaging product |
| Replacing the existing approved-project authority model with a new workflow engine | Brownfield constraint is to extend the current authority/event/artifact system |
| Supporting arbitrary custom backend stacks per generated product | The approved delivery path still depends on the shared template and shared Supabase model |
| Fully eliminating all operator intervention during exceptional failures | This milestone targets healthy-path autonomy with explicit escalation only on real blockers |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| CHAT-01 | Phase 22 | Pending |
| CHAT-02 | Phase 22 | Pending |
| CHAT-03 | Phase 22 | Pending |
| QUAL-01 | Phase 23 | Pending |
| QUAL-02 | Phase 23 | Pending |
| QUAL-03 | Phase 23 | Pending |
| QUAL-04 | Phase 23 | Pending |
| PROP-01 | Phase 24 | Pending |
| PROP-02 | Phase 24 | Pending |
| AUTO-01 | Phase 24 | Pending |
| AUTO-02 | Phase 25 | Pending |
| AUTO-03 | Phase 25 | Pending |
| AUTO-04 | Phase 25 | Pending |

**Coverage:**
- v1 requirements: 13 total
- Mapped to phases: 13
- Unmapped: 0

---
*Requirements defined: 2026-05-04*
*Last updated: 2026-05-04 after milestone v1.2 initialization*
