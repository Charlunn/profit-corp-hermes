# Requirements: Profit-Corp Hermes

**Defined:** 2026-04-24
**Core Value:** Turn noisy web-wide user pain signals into a clear, actionable daily operating view: which problems are worth pursuing, what matters most, what is risky, and what the company should build and launch next.

## v1 Requirements

### External Signals

- [ ] **SIGN-01**: Operator can discover user complaint and pain-point signals from across the public web instead of depending on one fixed source list
- [ ] **SIGN-02**: System can enrich promising pain-point opportunities with optional competitor or trend research for pricing, positioning, or marketing when needed

### Analysis Pipeline

- [ ] **ANLY-01**: System can normalize raw external signals into a consistent structured format
- [ ] **ANLY-02**: System can deduplicate and priority-rank collected signals before final synthesis
- [ ] **ANLY-03**: System can route the same prioritized signal set through Scout, CMO, Arch, CEO, and Accountant analysis roles

### Decision Outputs

- [ ] **DECI-01**: System can generate a daily operating decision package with prioritized conclusions and recommended next actions
- [ ] **DECI-02**: System can generate a project execution package derived from the daily operating decision package
- [ ] **DECI-03**: System can generate a board-style briefing derived from the daily operating decision package

### Governance

- [ ] **GOV-01**: System records explicit approval outcomes for high-impact operating actions
- [ ] **GOV-02**: System records an auditable trace linking signals, analyses, decisions, and governance outcomes

### Operating Visibility

- [ ] **VIZ-01**: Operator can view the current situation, key risks, key opportunities, and recommended next steps at a glance

## v2 Requirements

### Source Expansion

- **SRCX-01**: Operator can add richer source adapters and broader public-source coverage beyond the initial source set
- **SRCX-02**: System can track source reliability and evidence confidence by source class

### Collaboration

- **COLL-01**: Multiple team members can review, approve, and operate the system with clear ownership boundaries
- **COLL-02**: System can assign and track work queues by role or human teammate

### Internal Intelligence

- **INTL-01**: System can combine external signals with internal project telemetry and operating metrics
- **INTL-02**: System can detect conflicts between external opportunity signals and internal execution constraints

### Real-Time Experience

- **REAL-01**: Operator can monitor important signal and decision changes continuously instead of relying only on daily cycles
- **REAL-02**: Operator can use a richer dashboard or UI without replacing artifact-based governance

## Out of Scope

| Feature | Reason |
|---------|--------|
| Full autonomy without operator approval | Conflicts with the project’s governance and trust requirements |
| Internal telemetry as the primary v1 input | v1 is intentionally biased toward external pain signals |
| Real-time dashboard as the first implementation focus | Visibility should be built after the daily operating core is trustworthy |
| Expanding beyond the current five core roles in v1 | Extra roles would add coordination complexity before the core loop is stable |
| End-user customer-facing SaaS product features | This repo is the internal AI management core, not the external product |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| SIGN-01 | Phase 1 | Completed |
| SIGN-02 | Phase 1 | Completed |
| ANLY-01 | Phase 1 | Completed |
| ANLY-02 | Phase 2 | Completed |
| ANLY-03 | Phase 2 | Completed |
| DECI-01 | Phase 3 | Completed |
| DECI-02 | Phase 6 | Completed |
| DECI-03 | Phase 6 | Completed |
| GOV-01 | Phase 4 | Pending |
| GOV-02 | Phase 4 | Pending |
| VIZ-01 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 11 total
- Mapped to phases: 11
- Unmapped: 0 ✓

---
*Requirements defined: 2026-04-24*
*Last updated: 2026-04-25 after web-wide discovery refocus*
