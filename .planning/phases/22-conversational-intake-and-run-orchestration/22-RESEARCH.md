# Phase 22: Conversational Intake and Run Orchestration - Research

**Researched:** 2026-05-04
**Domain:** Chat-native intake, authority artifacts, and governed run dispatch
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
- **D-01:** Discord and Telegram events should be normalized into one platform-agnostic chat intake envelope rather than giving each platform a custom orchestration path.
- **D-02:** The normalized envelope must persist at least `platform`, `channel_or_chat_id`, `thread_or_reply_context`, `requester`, `message_id`, `message_text`, `received_at`, and a generated governed `run_id`.
- **D-03:** Hermes should treat one explicit mention/command message as the canonical start trigger for a run, and later status replies should backlink to that originating conversation context instead of creating detached operator state.
- **D-04:** Chat intake should use the same file-backed, authority-first governance style as approved delivery: one machine-readable authoritative record plus append-only events and derived status views, not ephemeral bot memory.
- **D-05:** The chat-origin record should live outside the approved-project bundle until qualification/approval succeeds, but it must already carry enough identity and trace data that later proposal and delivery artifacts can inherit the same `run_id`.
- **D-06:** Missing chat-origin metadata should fail closed before downstream discovery starts; Hermes should not silently downgrade to a terminal-like anonymous run when the source thread or requester cannot be proven.
- **D-07:** Chat start should dispatch the same governed discovery and approved-project pipeline contracts that local startup uses, with a thin intake adapter in front rather than a second chat-only workflow stack.
- **D-08:** The intake adapter should hand off through durable artifacts/CLI entrypoints already used in the repo, so later phases can resume or replay a run from persisted truth instead of reconstructing it from chat transcripts.
- **D-09:** Healthy-path orchestration after intake should remain autonomous once the run is created; the operator should not need to translate the chat request into manual local commands.
- **D-10:** Derived status surfaces must show that a run originated from chat and include the source platform/thread alongside current pipeline stage.
- **D-11:** Hermes should answer the originating conversation with short, derived status updates tied to the authoritative run state rather than composing freeform progress from scratch.
- **D-12:** Blocked chat runs must preserve the same reason-coded, resume-friendly truth already used elsewhere in Hermes so later recovery can escalate cleanly instead of losing source-channel context.

### the agent's Discretion
- Exact directory and filename scheme for pre-approval chat-run artifacts, as long as it is stable, authority-first, and resumable.
- Exact mapping of Discord vs Telegram raw fields into the normalized envelope, as long as the canonical chat-origin fields remain consistent.
- Exact wording and cadence of chat status updates, as long as they are derived from authoritative artifacts and not hidden in transient bot state.

### Deferred Ideas (OUT OF SCOPE)
- Multi-operator subscriptions and notification fan-out remain future-scope expansion (`COLL-01`), not Phase 22.
- Chat-based recovery and redirect commands after failure belong to later recovery work (`RECO-01`), not initial run creation.
- Support for additional channels beyond Discord and Telegram belongs to future expansion (`CHAN-01`).
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| CHAT-01 | Operator can start a new project run by mentioning Hermes in a Discord or Telegram group. | Use one normalized intake adapter over `discord.py` and `python-telegram-bot`, then create one authoritative chat-run record before any downstream work. [VERIFIED: REQUIREMENTS.md] [CITED: https://discordpy.readthedocs.io/en/stable/intents.html] [CITED: https://docs.python-telegram-bot.org/en/stable/telegram.ext.application.html] |
| CHAT-02 | Hermes records the originating chat platform, channel/thread, requester, and message intent in the authoritative project-run artifacts. | Persist a canonical envelope and append-only intake events before discovery starts. [VERIFIED: 22-CONTEXT.md] [VERIFIED: codebase grep] |
| CHAT-03 | Chat-triggered project runs invoke the same governed approved-project pipeline instead of a separate ad hoc path. | Bridge into existing `start_approved_project_delivery.py`, `start_delivery_run.py`, and cron wrappers. [VERIFIED: REQUIREMENTS.md] [VERIFIED: codebase grep] |
</phase_requirements>

## Summary

Phase 22 should be planned as a thin chat-ingress layer in front of the existing governed Hermes pipeline, not as a new orchestration system. The repo already uses the exact patterns this phase should reuse: authoritative JSON records, append-only JSONL event streams, derived status Markdown, fail-closed validation, and resume-by-artifact startup. Those patterns are visible in `scripts/start_approved_project_delivery.py`, `scripts/start_delivery_run.py`, `scripts/append_approved_delivery_event.py`, and `scripts/render_approved_delivery_status.py`. [VERIFIED: codebase grep]

There is no existing first-class Discord or Telegram runtime in the repo, so the planner should define the platform-neutral intake schema first and keep SDK bindings at the edge. For Discord, mention-driven text intake requires explicit planning around message-content access. For Telegram, the current Python SDK supports both polling and webhook styles, which means Phase 22 can start with a simple worker process and defer public-ingress complexity unless operations already require webhooks. [CITED: https://discordpy.readthedocs.io/en/stable/intents.html] [CITED: https://docs.python-telegram-bot.org/en/stable/telegram.ext.application.html] [CITED: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks]

The current machine has Python `3.11.15`, `pytest 8.4.2`, Hermes CLI `0.10.0`, and Git `2.53.0.windows.1`, but no Discord or Telegram token env vars were present in this session. The planner should therefore treat live bot auth as a Wave 0 dependency and prioritize unit/contract tests over live integration first. [VERIFIED: shell command] [VERIFIED: PyPI JSON API]

**Primary recommendation:** create one Python chat-run intake adapter that writes durable chat-origin truth first, then dispatches the existing governed run path.

## Project Constraints (from CLAUDE.md)

- Frontend-only rule: any frontend UI implementation or styling work must invoke `/ui-ux-pro-max` first and use its design-system output as the source of truth. [VERIFIED: CLAUDE.md]
- This phase is backend/orchestration-focused unless later planning adds a user-facing UI beyond chat replies. [VERIFIED: CLAUDE.md] [ASSUMED]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Discord trigger intake | API / Backend | -- | Bot event receipt and validation belong server-side. [VERIFIED: 22-CONTEXT.md] |
| Telegram trigger intake | API / Backend | -- | Telegram updates are bot/server concerns before any artifact write. [CITED: https://docs.python-telegram-bot.org/en/stable/telegram.update.html] |
| Canonical chat envelope persistence | API / Backend | Database / Storage | Repo conventions persist current truth in files plus append-only history. [VERIFIED: docs/STATE_CONTRACT.md] [VERIFIED: codebase grep] |
| Append-only chat event stream | Database / Storage | API / Backend | Existing run/governance flows validate and append events through scripts. [VERIFIED: codebase grep] |
| Derived chat-run status rendering | API / Backend | Database / Storage | Existing operator surfaces are rendered from authoritative files, not process memory. [VERIFIED: codebase grep] |
| Downstream governed dispatch | API / Backend | Database / Storage | Existing entrypoints are Python scripts and cron wrappers that should be reused. [VERIFIED: README.md] [VERIFIED: orchestration/cron/commands.sh] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.11.15 | Main implementation runtime. [VERIFIED: shell command] | Matches the existing orchestration stack. [VERIFIED: codebase grep] |
| `discord.py` | 2.7.1, published 2026-03-03 | Discord message/gateway intake. [VERIFIED: PyPI JSON API] | Official Python Discord SDK with documented intent handling. [CITED: https://discordpy.readthedocs.io/en/stable/intents.html] |
| `python-telegram-bot` | 22.7, published 2026-03-16 | Telegram group command intake and replies. [VERIFIED: PyPI JSON API] | Official current Python Telegram SDK with `Application` runtime. [CITED: https://docs.python-telegram-bot.org/en/stable/telegram.ext.application.html] |
| JSON + JSONL artifacts | stdlib | Authority record and event history. [VERIFIED: codebase grep] | Already the dominant Hermes governance pattern. [VERIFIED: docs/STATE_CONTRACT.md] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest` | 8.4.2 | Contract/regression tests. [VERIFIED: shell command] | Use for new phase tests and quick contract runs. [VERIFIED: tests/] |
| Hermes CLI | 0.10.0 | Existing governed orchestration seams. [VERIFIED: shell command] | Use only where the current repo already standardizes on it. [VERIFIED: orchestration/cron/commands.sh] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Discord raw mention parsing | Discord application commands | Reduces message-content pressure, but may not satisfy the intended "mention Hermes" UX without clarification. [CITED: https://discord.com/developers/docs/topics/gateway#privileged-intents] [ASSUMED] |
| Telegram polling | Telegram webhook mode | Webhooks require public ingress and secret-token setup; polling is simpler for a CLI/cron-oriented repo. [CITED: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks] [ASSUMED] |
| Chat-only orchestrator | Existing startup scripts | A second orchestrator would duplicate pipeline truth. [VERIFIED: 22-CONTEXT.md] |

**Installation:**
```bash
pip install discord.py==2.7.1 python-telegram-bot==22.7
```

**Version verification:** `discord.py` latest was `2.7.1` with upload timestamp `2026-03-03T18:40:46.240241Z`; `python-telegram-bot` latest was `22.7` with upload timestamp `2026-03-16T09:36:03.174235Z`. [VERIFIED: PyPI JSON API]

## Architecture Patterns

### System Architecture Diagram
```text
Discord mention or command      Telegram group command
             |                           |
             v                           v
       Transport adapter           Transport adapter
                    \             /
                     v           v
              Normalized intake envelope
       {platform, chat, thread/reply, requester,
        message_id, message_text, received_at, run_id}
                           |
                           v
              Authoritative chat-run record
                           |
                +----------+----------+
                |                     |
                v                     v
       append chat-run events    render derived status
                |                     |
                +----------+----------+
                           |
                           v
              thin dispatch bridge / CLI seam
                           |
                           v
         existing Hermes discovery and delivery path
```

### Recommended Project Structure
```text
assets/shared/chat-runs/
|-- latest/
|   |-- <run-id>.json
|   `-- <run-id>-STATUS.md
`-- history/
    `-- chat-run-events.jsonl

scripts/
|-- chat_intake_common.py
|-- start_chat_project_run.py
`-- render_chat_run_status.py
```
[ASSUMED]

### Pattern 1: Normalize First, Dispatch Later
Persist one platform-neutral intake envelope before calling any discovery/startup step. [VERIFIED: 22-CONTEXT.md]

### Pattern 2: Authority Record Plus Append-Only Events
Mirror the approved-delivery pattern: one current truth file plus event history. [VERIFIED: codebase grep]

### Pattern 3: Thin Bridge Into Existing Pipeline
Do not create a second discovery or approval stack for chat-origin runs; call existing governed commands/scripts from a small adapter layer. [VERIFIED: 22-CONTEXT.md] [VERIFIED: orchestration/cron/commands.sh]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Discord transport | Custom WebSocket client | `discord.py` | Gateway/intents behavior is already solved in the official SDK. [CITED: https://discordpy.readthedocs.io/en/stable/intents.html] |
| Telegram runtime | Custom Bot API loop | `python-telegram-bot` | Update parsing and runtime lifecycle are already solved in the official SDK. [CITED: https://docs.python-telegram-bot.org/en/stable/telegram.ext.application.html] |
| Event append validation | Freeform file appends | One validated append helper | Existing Hermes patterns already enforce required fields and append ordering. [VERIFIED: codebase grep] |
| Status composition | Ad hoc reply strings | One derived renderer | Existing status surfaces are rendered from authoritative artifacts. [VERIFIED: codebase grep] |
| Intake idempotency | In-memory duplicate suppression | Persisted trigger identity | Restarts/redelivery can otherwise create duplicate runs. [ASSUMED] |

## Common Pitfalls

### Pitfall 1: Discord mention parsing without explicit intent planning
**What goes wrong:** The bot connects but cannot reliably interpret freeform group-chat triggers. [CITED: https://discordpy.readthedocs.io/en/stable/intents.html]  
**Why it happens:** Mention/text command parsing depends on message-content access and command shape. [CITED: https://discordpy.readthedocs.io/en/stable/intents.html]  
**How to avoid:** Add a Wave 0 planning task that locks Discord trigger semantics before implementation. [ASSUMED]

### Pitfall 2: Writing chat state directly into approved-project artifacts
**What goes wrong:** Pre-approval chat origin becomes entangled with post-approval delivery truth. [VERIFIED: 22-CONTEXT.md]  
**Why it happens:** D-05 explicitly keeps chat-origin records outside the approved-project bundle until later phases. [VERIFIED: 22-CONTEXT.md]  
**How to avoid:** Create a separate pre-approval chat-run bundle keyed by `run_id`. [ASSUMED]

### Pitfall 3: Platform-specific downstream branching
**What goes wrong:** Discord and Telegram end up with separate orchestration semantics and resume paths. [VERIFIED: 22-CONTEXT.md]  
**How to avoid:** Normalize both transports into one envelope and one bridge layer. [VERIFIED: 22-CONTEXT.md]

## Code Examples

### Validated append-only event writer pattern
```python
# Source: scripts/append_approved_delivery_event.py [VERIFIED: codebase grep]
REQUIRED_EVENT_FIELDS = (
    "project_slug",
    "stage",
    "status",
    "action",
    "timestamp",
    "outcome",
)
```

### Telegram Application bootstrap
```python
# Source: https://docs.python-telegram-bot.org/en/stable/telegram.ext.application.html
from telegram.ext import Application, CommandHandler

app = Application.builder().token("TOKEN").build()
app.add_handler(CommandHandler("hermes", handle_hermes))
app.run_polling()
```

### Discord intent-aware bootstrap
```python
# Source: https://discordpy.readthedocs.io/en/stable/intents.html
import discord

intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Terminal-only startup | Authority-first startup plus resumable approved-project pipeline | Present in repo by 2026-05-04 | Chat intake should bridge into existing authority/event contracts, not replace them. [VERIFIED: README.md] [VERIFIED: 22-CONTEXT.md] |
| Single status file mentality | Current truth plus append-only history plus derived status | Present in repo by 2026-05-04 | Phase 22 should emit at least one authority JSON, one event JSONL, and one derived status surface. [VERIFIED: codebase grep] |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | `assets/shared/chat-runs/` is the right pre-approval root. | Recommended Project Structure | Low |
| A2 | Telegram polling is the best first runtime mode here. | Alternatives Considered | Medium |
| A3 | Persisted message identity should be the main dedupe key. | Don't Hand-Roll | Medium |

## Open Questions

1. **Discord trigger semantics**
   - What we know: CHAT-01 and D-03 require a mention/command message in group chat. [VERIFIED: REQUIREMENTS.md] [VERIFIED: 22-CONTEXT.md]
   - What is unclear: Whether true freeform `@Hermes ...` text is required, or a structured Discord command is acceptable.
   - Recommendation: Lock this before implementation because it changes setup and tests. [ASSUMED]

2. **Telegram polling vs webhook**
   - What we know: the official Python SDK supports both. [CITED: https://docs.python-telegram-bot.org/en/stable/telegram.ext.application.html] [CITED: https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks]
   - What is unclear: Whether Hermes will run behind durable public ingress.
   - Recommendation: Plan for polling first unless operations already provide ingress. [ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Bot worker, authority scripts, tests | yes | 3.11.15 | -- |
| `pytest` | Contract/regression tests | yes | 8.4.2 | `python -m pytest` |
| Hermes CLI | Existing governed seams | yes | 0.10.0 | Direct Python script calls in unit tests |
| Git | Existing repo automation | yes | 2.53.0.windows.1 | -- |
| Discord token | Live Discord intake | no | -- | None |
| Telegram token | Live Telegram intake | no | -- | None |

**Missing dependencies with no fallback:**
- Discord bot credentials. [VERIFIED: shell command]
- Telegram bot credentials. [VERIFIED: shell command]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | `pytest 8.4.2` over existing Python test modules. [VERIFIED: shell command] [VERIFIED: tests/] |
| Config file | none -- direct invocation today. [VERIFIED: codebase grep] |
| Quick run command | `pytest tests/test_start_delivery_run.py tests/test_project_delivery_pipeline_bootstrap.py tests/test_project_delivery_pipeline_resume.py -q` |
| Full suite command | `pytest -q` |

### Phase Requirements -> Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| CHAT-01 | Group-chat trigger creates one governed chat run. | unit + contract | `pytest tests/test_chat_intake_contract.py -q` | no - Wave 0 |
| CHAT-02 | Authority artifacts persist origin metadata and intent. | unit | `pytest tests/test_chat_run_bootstrap.py -q` | no - Wave 0 |
| CHAT-03 | Chat run dispatches the existing governed path. | unit + contract | `pytest tests/test_chat_run_bootstrap.py -q` | no - Wave 0 |

### Wave 0 Gaps
- [ ] `tests/test_chat_intake_contract.py` for normalized envelope fields and fail-closed provenance validation. [ASSUMED]
- [ ] `tests/test_chat_run_bootstrap.py` for intake artifact creation and bridge dispatch behavior. [ASSUMED]
- [ ] `tests/test_chat_run_status.py` for derived status rendering of chat-origin runs. [ASSUMED]

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Platform bot tokens in local env/config only. [VERIFIED: README.md] |
| V3 Session Management | no | This phase is artifact-driven, not browser-session-driven. [VERIFIED: 22-CONTEXT.md] |
| V4 Access Control | yes | Fail closed when source chat/requester provenance is incomplete. [VERIFIED: 22-CONTEXT.md] |
| V5 Input Validation | yes | Validate all required canonical envelope fields before authority writes. [VERIFIED: 22-CONTEXT.md] |
| V6 Cryptography | conditional | If webhook mode is used later, use official secret-token support instead of custom logic. [CITED: https://core.telegram.org/bots/api#setwebhook] [ASSUMED] |

## Sources

### Primary (HIGH confidence)
- Local codebase inspection: `scripts/start_approved_project_delivery.py`, `scripts/start_delivery_run.py`, `scripts/append_approved_delivery_event.py`, `scripts/render_approved_delivery_status.py`, `orchestration/cron/commands.sh`, `tests/test_start_delivery_run.py`, `tests/test_project_delivery_pipeline_bootstrap.py`, `tests/test_project_delivery_pipeline_resume.py`
- `README.md`
- `.planning/phases/22-conversational-intake-and-run-orchestration/22-CONTEXT.md`
- `.planning/REQUIREMENTS.md`
- `.planning/STATE.md`
- `docs/STATE_CONTRACT.md`
- https://discordpy.readthedocs.io/en/stable/intents.html
- https://docs.python-telegram-bot.org/en/stable/telegram.ext.application.html
- https://docs.python-telegram-bot.org/en/stable/telegram.update.html
- https://pypi.org/pypi/discord.py/json
- https://pypi.org/pypi/python-telegram-bot/json

### Secondary (MEDIUM confidence)
- https://github.com/python-telegram-bot/python-telegram-bot/wiki/Webhooks
- https://discord.com/developers/docs/topics/gateway#privileged-intents
- https://core.telegram.org/bots/api

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - versions were verified against PyPI and match the repo's Python orchestration direction.
- Architecture: MEDIUM - existing artifact patterns are clear, but exact chat-run layout and Discord trigger semantics still need locked planning decisions.
- Pitfalls: MEDIUM - Discord intent constraints are verified; some runtime and dedupe details remain assumptions.

**Research date:** 2026-05-04
**Valid until:** 2026-06-03
