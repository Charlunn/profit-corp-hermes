# Phase 22: Conversational Intake and Run Orchestration - Context

**Gathered:** 2026-05-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Let Hermes accept a Discord or Telegram group-chat command as the canonical start signal for a new project run, persist one authoritative intake record for that run, and route the run into the same governed downstream discovery path that terminal-driven startup already uses.

This phase owns chat-trigger normalization, authoritative intake/run artifacts, chat-origin status visibility, and the bridge into the existing governed project pipeline. It does not yet decide whether a project is good enough to approve, and it does not replace the approved-project authority model that starts after proposal approval.

</domain>

<decisions>
## Implementation Decisions

### Chat trigger contract
- **D-01:** Discord and Telegram events should be normalized into one platform-agnostic chat intake envelope rather than giving each platform a custom orchestration path.
- **D-02:** The normalized envelope must persist at least `platform`, `channel_or_chat_id`, `thread_or_reply_context`, `requester`, `message_id`, `message_text`, `received_at`, and a generated governed `run_id`.
- **D-03:** Hermes should treat one explicit mention/command message as the canonical start trigger for a run, and later status replies should backlink to that originating conversation context instead of creating detached operator state.

### Authoritative intake artifacts
- **D-04:** Chat intake should use the same file-backed, authority-first governance style as approved delivery: one machine-readable authoritative record plus append-only events and derived status views, not ephemeral bot memory.
- **D-05:** The chat-origin record should live outside the approved-project bundle until qualification/approval succeeds, but it must already carry enough identity and trace data that later proposal and delivery artifacts can inherit the same `run_id`.
- **D-06:** Missing chat-origin metadata should fail closed before downstream discovery starts; Hermes should not silently downgrade to a terminal-like anonymous run when the source thread or requester cannot be proven.

### Downstream orchestration bridge
- **D-07:** Chat start should dispatch the same governed discovery and approved-project pipeline contracts that local startup uses, with a thin intake adapter in front rather than a second chat-only workflow stack.
- **D-08:** The intake adapter should hand off through durable artifacts/CLI entrypoints already used in the repo, so later phases can resume or replay a run from persisted truth instead of reconstructing it from chat transcripts.
- **D-09:** Healthy-path orchestration after intake should remain autonomous once the run is created; the operator should not need to translate the chat request into manual local commands.

### Operator-visible status
- **D-10:** Derived status surfaces must show that a run originated from chat and include the source platform/thread alongside current pipeline stage.
- **D-11:** Hermes should answer the originating conversation with short, derived status updates tied to the authoritative run state rather than composing freeform progress from scratch.
- **D-12:** Blocked chat runs must preserve the same reason-coded, resume-friendly truth already used elsewhere in Hermes so later recovery can escalate cleanly instead of losing source-channel context.

### the agent's Discretion
- Exact directory and filename scheme for pre-approval chat-run artifacts, as long as it is stable, authority-first, and resumable.
- Exact mapping of Discord vs Telegram raw fields into the normalized envelope, as long as the canonical chat-origin fields remain consistent.
- Exact wording and cadence of chat status updates, as long as they are derived from authoritative artifacts and not hidden in transient bot state.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and milestone contract
- `.planning/ROADMAP.md` - Phase 22 goal, success criteria, and milestone framing for chat-native startup.
- `.planning/REQUIREMENTS.md` - `CHAT-01` through `CHAT-03`.
- `.planning/PROJECT.md` - v1.2 intent to compress healthy-path operator interaction to start plus approve.
- `.planning/STATE.md` - current milestone position and known concern about mapping conversation events into the authority/event model.

### Prior decisions that constrain this phase
- `.planning/phases/10-approved-project-delivery-pipeline/10-CONTEXT.md` - authority-first approved-project pipeline and operator handoff expectations that the chat intake must feed rather than replace.
- `.planning/phases/17-authority-and-status-convergence/17-PATTERNS.md` - convergence pattern for current truth vs historical blocked state.
- `.planning/phases/21-bootstrap-resume-governance-regressions/21-CONTEXT.md` - resume-friendly, fail-closed truth model that new chat-origin runs must preserve.

### Existing governance and orchestration surfaces
- `docs/STATE_CONTRACT.md` - file-backed state boundaries and write-governance expectations.
- `docs/OPERATIONS.md` - operator-facing workflow assumptions for governed project execution.
- `README.md` - existing approved-project bootstrap and delivery commands that Phase 22 should route into rather than replace.
- `orchestration/cron/commands.sh` - current command-style orchestration entrypoints that can act as downstream dispatch seams.

### Existing code and tests
- `scripts/start_approved_project_delivery.py` - current authority-first approved-project bootstrap/resume pipeline.
- `scripts/start_delivery_run.py` - workspace-local delivery-run bootstrap contract and required input bundle.
- `scripts/render_approved_delivery_status.py` - derived operator-facing status rendering seam for later chat updates.
- `scripts/request_governance_approval.py` - append-only governance event pattern that chat-origin approvals and escalations should mirror.
- `tests/test_start_delivery_run.py` - durable bootstrap contract expectations relevant to chat-to-pipeline dispatch.
- `tests/test_project_delivery_pipeline_bootstrap.py` - governed bootstrap and blocked-state expectations that chat-origin runs must preserve.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/start_approved_project_delivery.py`: already defines a long-lived run model with `run_id`, append-only events, stage/state fields, and rendered status/final review artifacts.
- `scripts/start_delivery_run.py`: already creates the workspace-local `.hermes/` manifest, status, and event stream once a governed project run reaches delivery bootstrap.
- `scripts/request_governance_approval.py`: already provides a stable append-only governance-event contract with action ids and status transitions.
- `scripts/render_approved_delivery_status.py`: already centralizes operator-facing rendering from authoritative artifacts instead of transient process state.

### Established Patterns
- Hermes prefers one authoritative JSON record plus append-only JSONL plus derived markdown status rather than chat-memory or terminal-memory truth.
- New automation stages are expected to fail closed on missing prerequisite artifacts instead of silently filling gaps.
- Resume and recovery rely on persisted reason-coded state, not on reconstructing intent from logs.

### Integration Points
- A new chat intake adapter should likely stop at the boundary where `start_approved_project_delivery.py` or another governed run initializer can take over.
- Status rendering should extend existing derived status artifacts rather than invent a chat-only progress store.
- Governance/event append helpers are the natural seam for recording source-channel metadata and operator-visible run transitions.

</code_context>

<specifics>
## Specific Ideas

- Auto-selected all relevant gray areas because the request was to run discuss in `--auto` mode.
- Defaulted to a normalized chat envelope and one durable `run_id` spanning intake through later approval/delivery, because that best fits the repo's authority-first patterns.
- Defaulted to a thin chat adapter that dispatches existing governed startup paths instead of a second, platform-specific orchestration stack.

</specifics>

<deferred>
## Deferred Ideas

- Multi-operator subscriptions and notification fan-out remain future-scope expansion (`COLL-01`), not Phase 22.
- Chat-based recovery and redirect commands after failure belong to later recovery work (`RECO-01`), not initial run creation.
- Support for additional channels beyond Discord and Telegram belongs to future expansion (`CHAN-01`).

</deferred>

---

*Phase: 22-conversational-intake-and-run-orchestration*
*Context gathered: 2026-05-04*
