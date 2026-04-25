# Roadmap: Profit-Corp Hermes

## Overview

This roadmap evolves the existing Hermes-based company substrate into a reliable AI operating core for finding user pain points across the web, validating which opportunities are worth pursuing, and rapidly launching paid mini-SaaS products. The sequence starts by making web-wide pain-signal discovery trustworthy, then turns those signals into role-based analysis, raises the quality of recurring management outputs, wraps that loop in executable governance, makes the operating picture visible at a glance, and finally extends the system toward execution handoff and team readiness.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Pain-Signal Discovery Foundation** - Build repeatable web-wide pain-point discovery and normalization
- [x] **Phase 2: Signal Triage and Role Analysis Loop** - Convert pain signals into prioritized multi-role intelligence
- [x] **Phase 3: Decision Package Quality** - Produce professional management-grade outputs from trusted evidence
- [ ] **Phase 4: Governance and Control Layer** - Turn documented controls into executable approvals and audit flow
- [ ] **Phase 5: Operating Visibility Surface** - Make state, risk, opportunity, and next actions visible at a glance
- [ ] **Phase 6: Execution Handoff and Team Readiness** - Extend the core with execution packs, board briefs, and collaboration readiness

## Phase Details

### Phase 1: Pain-Signal Discovery Foundation
**Goal**: Establish reliable web-wide discovery of user complaint and pain-point signals, with structured normalization and source history, while leaving room for optional trend and competitor enrichment later.
**Depends on**: Nothing (first phase)
**Requirements**: SIGN-01, SIGN-02, ANLY-01
**Success Criteria** (what must be TRUE):
  1. Operator can run a repeatable collection flow that discovers user complaint and pain-point signals from across the public web instead of relying on one fixed canonical source list
  2. Newly collected signals are normalized into one consistent structure instead of remaining raw free-form notes
  3. Signal history is persisted so later phases can compare new signals against previously seen inputs
  4. Optional trend or competitor sources can be added without changing the normalized contract, but they are not required to prove Phase 1 complete
**Plans**: 4 plans

Plans:
- [ ] 01-01: Define discovery model, signal schema, and storage locations for web-wide pain-signal intake
- [ ] 01-02: Implement collection adapters or scripts for flexible public pain-point discovery
- [ ] 01-03: Persist normalized signal history and integrate the intake flow into the operating rhythm
- [ ] 01-04: Prove live web-wide pain-signal discovery and normalization

### Phase 2: Signal Triage and Role Analysis Loop
**Goal**: Prioritize collected signals and route them through the existing management roles to produce distinct analytical outputs.
**Depends on**: Phase 1
**Requirements**: ANLY-02, ANLY-03
**Success Criteria** (what must be TRUE):
  1. System deduplicates and priority-ranks incoming signals before management synthesis
  2. Scout, CMO, Arch, CEO, and Accountant each produce role-specific analysis from the same prioritized signal set
  3. Daily loop can complete an end-to-end analysis cycle without collapsing into one generic summary
**Plans**: 3 plans

Plans:
- [ ] 02-01: Build signal scoring, deduplication, and clustering rules
- [ ] 02-02: Define role handoff artifacts and wire multi-role analysis over prioritized inputs
- [ ] 02-03: Integrate CEO synthesis over role outputs as the end of the daily analysis loop

### Phase 3: Decision Package Quality
**Goal**: Turn the analysis loop into polished, management-grade deliverables with strong conclusions and evidence links.
**Depends on**: Phase 2
**Requirements**: DECI-01, DECI-02, DECI-03
**Success Criteria** (what must be TRUE):
  1. Daily operating decision package presents prioritized conclusions, risks, opportunities, and next actions clearly
  2. Project execution package can be generated from the operating decision package without re-analyzing raw signals
  3. Board-style briefing can be generated from the same decision foundation in a more executive summary format
**Plans**: 3 plans

Plans:
- [x] 03-01: Design artifact templates for decision pack, execution pack, and board briefing
- [x] 03-02: Improve synthesis quality with evidence-linked recommendations and mixed consulting/CEO style
- [x] 03-03: Integrate recurring output generation into the daily operating loop

### Phase 4: Governance and Control Layer
**Goal**: Make approvals, audit traces, and high-impact decision controls executable within the workflow.
**Depends on**: Phase 3
**Requirements**: GOV-01, GOV-02
**Success Criteria** (what must be TRUE):
  1. High-impact operating actions record explicit approval outcomes
  2. Operator can trace a final recommendation back through signal evidence, role analysis, and governance outcomes
  3. Strategic or budget-relevant transitions no longer rely only on policy text to be enforced
**Plans**: 3 plans

Plans:
- [ ] 04-01: Define governance event model and approval artifact structure
- [ ] 04-02: Wrap high-impact decisions with executable approval and audit steps
- [ ] 04-03: Connect governance records to existing state and finance constraints

### Phase 5: Operating Visibility Surface
**Goal**: Expose current state, risks, opportunities, and next actions in a concise operator-facing summary layer.
**Depends on**: Phase 4
**Requirements**: VIZ-01
**Success Criteria** (what must be TRUE):
  1. Operator can see current situation, top risks, top opportunities, and recommended next steps at a glance
  2. Visibility view is derived from trusted artifacts and governance state rather than ad-hoc manual interpretation
  3. Daily status can be reviewed quickly without reading every underlying artifact in full
**Plans**: 2 plans

Plans:
- [ ] 05-01: Design the visibility read model and summary artifact structure
- [ ] 05-02: Generate and update the operator-facing visibility surface from trusted workflow outputs

### Phase 6: Execution Handoff and Team Readiness
**Goal**: Extend the operating core into downstream execution support and future multi-user/team workflows.
**Depends on**: Phase 5
**Requirements**: DECI-02, DECI-03
**Success Criteria** (what must be TRUE):
  1. Project execution packages can support downstream planning/execution work consistently
  2. Board-style briefings remain aligned with the same evidence and governance trail as the core decision package
  3. System structure is ready for later team collaboration without rewriting the operating loop from scratch
**Plans**: 3 plans

Plans:
- [ ] 06-01: Strengthen execution handoff structure for planning and delivery workflows
- [ ] 06-02: Refine board-style brief generation for recurring strategic reporting
- [ ] 06-03: Add ownership and collaboration readiness for future team-based operation

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Pain-Signal Discovery Foundation | 4/4 | Complete | 2026-04-25 |
| 2. Signal Triage and Role Analysis Loop | 3/3 | Complete | 2026-04-25 |
| 3. Decision Package Quality | 3/3 | Complete | 2026-04-25 |
| 4. Governance and Control Layer | 0/3 | Not started | - |
| 5. Operating Visibility Surface | 0/2 | Not started | - |
| 6. Execution Handoff and Team Readiness | 0/3 | Not started | - |
