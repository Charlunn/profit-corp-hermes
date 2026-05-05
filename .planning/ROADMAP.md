# Profit-Corp Hermes

## Current Milestone

- **v1.2 Autonomous Project Launch Loop** - Phases 22-25 (planned 2026-05-04)

## Milestones

- **v1.2 Autonomous Project Launch Loop** - Phases 22-25 (planned)
- **v1.1.2 Real-SaaS Delivery Governance Hardening** - Phases 18-21 (shipped 2026-05-04)
- **v1.1.1 Delivery Pipeline Reliability Fixes** - Phases 14-17 (shipped 2026-04-30)
- **v1.1 SaaS Delivery Factory** - Phases 7-13 (shipped 2026-04-28)
- **v1.0 milestone** - Phases 1-6 (shipped 2026-04-26)

## Proposed Roadmap

**4 phases** | **13 requirements mapped** | All covered

| # | Phase | Goal | Requirements | Success Criteria |
|---|-------|------|--------------|------------------|
| 22 | Conversational Intake and Run Orchestration | Let the operator start a new project from Discord/Telegram and create one authoritative project run | CHAT-01, CHAT-02, CHAT-03 | 4 |
| 23 | Real-Pain Qualification and Market Proof Gates | Require fresh, real, buildable pain evidence plus pricing and market proof before proposal approval | QUAL-01, QUAL-02, QUAL-03, QUAL-04 | 5 |
| 24 | Approval Package and Locked Delivery Contract | Produce a proposal that the operator can approve once, then freeze scope, pricing, and delivery contract | PROP-01, PROP-02, AUTO-01 | 4 |
| 25 | Autonomous Delivery to Deploy and Return Link | Run approved work through design, development, testing, shipping, deploy, and final link handoff without manual resumes | AUTO-02, AUTO-03, AUTO-04 | 5 |

## Phase Details

### Phase 22: Conversational Intake and Run Orchestration

**Goal:** Accept a group-chat command as the canonical trigger for starting a new project run and convert it into a governed Hermes intake.

**Requirements:** `CHAT-01`, `CHAT-02`, `CHAT-03`

**Success criteria:**
1. Discord or Telegram message intake can open a new project run without terminal commands.
2. The intake flow records source channel, requester, timestamp, and run identifier in authoritative artifacts.
3. The intake path can dispatch the same downstream discovery workflow that command-line project creation uses.
4. Operator-visible status shows that the run was started from chat and is progressing autonomously.

### Phase 23: Real-Pain Qualification and Market Proof Gates

**Goal:** Prevent weak ideas from becoming approved projects by hard-gating freshness, reality, feasibility, and monetization evidence.

**Requirements:** `QUAL-01`, `QUAL-02`, `QUAL-03`, `QUAL-04`

**Success criteria:**
1. Discovery only accepts candidate pain signals with evidence collected inside the last 72 hours.
2. Qualification artifacts prove the pain is real and not just generic interest or trend noise.
3. Feasibility checks can block ideas that are too broad, too custom, or incompatible with the shared template/backend model.
4. Market and pricing research become required artifacts rather than optional narrative fields.
5. A run cannot advance to proposal approval when any qualification gate is missing or failed.

### Phase 24: Approval Package and Locked Delivery Contract

**Goal:** Give the operator one concise proposal to approve, then freeze the approved scope into a delivery contract.

**Requirements:** `PROP-01`, `PROP-02`, `AUTO-01`

**Success criteria:**
1. Hermes produces one final proposal bundle with pain point, target user, pricing, market rationale, build scope, and expected launch outcome.
2. The operator can approve the proposal with one chat reply instead of running local commands.
3. Approval persists a locked contract that downstream specialists must follow for product scope, pricing, languages, and acceptance gates.
4. Delivery cannot silently drift away from the approved contract without opening a blocked state.

### Phase 25: Autonomous Delivery to Deploy and Return Link

**Goal:** After approval, continue automatically from design through deployment and return the live link plus final summary.

**Requirements:** `AUTO-02`, `AUTO-03`, `AUTO-04`

**Success criteria:**
1. Approved runs continue through specialist stages, GitHub, and Vercel without manual `resume` commands during healthy paths.
2. Delivery stages use actual specialist output and real implementation evidence instead of orchestrator-generated placeholder proof.
3. Pricing and monetization approved at proposal time appear in the delivered product surfaces and release evidence.
4. Completion sends a final chat response with deployment link, project summary, and blocked/failure context if the run does not finish.
5. Operator intervention is limited to start, approval, and exceptional failure recovery.
