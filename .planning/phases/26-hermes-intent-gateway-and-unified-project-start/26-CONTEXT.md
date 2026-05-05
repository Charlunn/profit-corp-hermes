# Phase 26: Hermes Intent Gateway and Unified Project Start - Context

**Gathered:** 2026-05-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Let the owner tell Hermes to start a new project through one Hermes-native entrypoint, and have that request become the single authoritative launch path without exposing scripts, milestone commands, or transport-specific startup choices.

This phase owns the top-level operator intent contract, Hermes-native run creation, healthy-path language at project start, and the boundary between the visible Hermes request and the existing governed launch backbone. It does not yet define how internal roles collaborate after the run starts, and it does not replace the shipped authority/event pipeline that already powers qualification, approval, and delivery.

</domain>

<decisions>
## Implementation Decisions

### Hermes-native start contract
- **D-01:** Hermes should expose one canonical "start project" intent surface that accepts the owner's project-start request without asking them to choose scripts, phases, or backend entrypoints.
- **D-02:** The start surface should normalize operator intent into one governed launch request record with durable identity, instead of letting multiple top-level command shapes create competing run semantics.
- **D-03:** Healthy-path start interactions should speak in Hermes terms such as request accepted, proposal in progress, or run blocked, rather than naming internal phase or script machinery.

### Authoritative run creation
- **D-04:** The Hermes-native start path must create one authoritative run using the shipped 22-25 governed artifact model instead of inventing a second state machine for v1.3.
- **D-05:** The top-level request should persist enough canonical metadata to connect the visible Hermes conversation, downstream qualification/proposal artifacts, and final delivery lifecycle under one run identity.
- **D-06:** If Hermes cannot prove enough start metadata to initialize a governed run, it should block immediately instead of silently downgrading into an ad hoc or partially tracked workflow.

### Operator-visible abstraction
- **D-07:** Hermes should hide transport and script details on the healthy path, but internal startup actions must remain inspectable through authoritative artifacts for governance and debugging.
- **D-08:** The first Hermes response after project start should confirm what Hermes is doing next in owner-facing language rather than exposing milestone choreography.
- **D-09:** Any start-time blocker should be reported as a Hermes-level problem statement with clear recovery context, not as a raw command failure or missing phase instruction.

### Backbone reuse boundary
- **D-10:** Phase 26 should wrap the already-shipped conversational intake and governed startup backbone with a Hermes-first interface layer rather than replacing the underlying launch machinery.
- **D-11:** Existing chat/start orchestration seams should be treated as implementation substrate that the new Hermes entrypoint calls into, preserving artifact compatibility with later phases.
- **D-12:** Hermes-native project start should remain the only intentional operator-facing launch contract even if multiple lower-level automation paths still exist internally for testing or resume.

### the agent's Discretion
- Exact phrasing of the owner-facing start acknowledgement, as long as it is Hermes-native and does not expose internal command choreography on healthy runs.
- Exact shape of the canonical project-start intent payload, as long as one governed run identity and source-of-truth artifact model are preserved.
- Exact adapter seam between the Hermes entrypoint and the shipped launch scripts, as long as no second authoritative run model is introduced.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and milestone contract
- `.planning/ROADMAP.md` - Phase 26 goal and success criteria for one Hermes-native project-start entrypoint.
- `.planning/REQUIREMENTS.md` - `HERMES-01`, `HERMES-02`, and `HERMES-03`.
- `.planning/PROJECT.md` - v1.3 milestone intent to make Hermes the only operator-facing company surface.
- `.planning/STATE.md` - current milestone state and concern about hiding pipeline internals without forking authority truth.

### Prior decisions that constrain this phase
- `.planning/phases/22-conversational-intake-and-run-orchestration/22-CONTEXT.md` - canonical start-run identity, authority-first intake artifacts, and downstream bridge expectations.
- `.planning/phases/23-real-pain-qualification-and-market-proof-gates/23-CONTEXT.md` - qualification gating contract that the new Hermes start flow must feed rather than bypass.
- `.planning/phases/24-approval-package-and-locked-delivery-contract/24-CONTEXT.md` - one-shot approval and locked-contract expectations that should remain downstream of the new start path.
- `.planning/phases/25-autonomous-delivery-to-deploy-and-return-link/25-CONTEXT.md` - healthy-path autonomy and final-result contract that the Hermes-first run identity must survive through.
- `.planning/phases/21-bootstrap-resume-governance-regressions/21-CONTEXT.md` - fail-closed bootstrap/resume truth model that start-time Hermes packaging must preserve.

### Existing artifacts and orchestration seams
- `docs/STATE_CONTRACT.md` - durable state boundaries and write-governance rules for any new Hermes-native run artifact.
- `docs/OPERATIONS.md` - existing operator workflow assumptions that will be partially hidden behind the new Hermes front door.
- `README.md` - current approved-project and orchestration commands that should become implementation details, not user workflow.
- `orchestration/cron/commands.sh` - current orchestration entrypoints and durable command seams available for reuse.

### Existing code and tests
- `scripts/start_chat_project_run.py` - current canonical intake/bootstrap seam that can inform the new Hermes-native start adapter.
- `scripts/chat_intake_common.py` - normalized intake contract and run identity helpers already used before downstream qualification begins.
- `scripts/render_chat_run_status.py` - existing owner-facing startup/status rendering seam that can be repackaged in Hermes-first language.
- `scripts/start_approved_project_delivery.py` - authoritative downstream run contract that the Phase 26 entrypoint must ultimately feed.
- `tests/test_chat_run_bootstrap.py` - durable startup bootstrap expectations relevant to one authoritative run creation.
- `tests/test_chat_intake_contract.py` - normalized intake contract expectations that should inform the top-level Hermes request shape.
- `tests/test_chat_origin_contract.py` - run identity and source-linkage expectations that remain useful even as Hermes becomes the visible interface.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/start_chat_project_run.py`: already creates the durable pre-approval run bundle and bridges into governed downstream flow.
- `scripts/chat_intake_common.py`: already centralizes normalized intake fields and run-id creation rather than leaving them ad hoc in prompt logic.
- `scripts/render_chat_run_status.py`: already provides a derived, operator-facing summary surface for early-stage run status.
- `scripts/start_approved_project_delivery.py`: already defines the authoritative delivery-side run/state contract that this phase must reuse, not replace.

### Established Patterns
- Hermes prefers one authoritative JSON record plus append-only events and derived status views rather than transient conversational memory.
- New top-level orchestration capabilities are expected to fail closed on missing identity or prerequisite metadata.
- Operator-visible messages should be derived from persisted truth, while low-level implementation details remain inspectable for governance.

### Integration Points
- The new Hermes-native start surface should likely adapt into `start_chat_project_run.py` or shared intake helpers instead of creating a parallel launch engine.
- Early owner-visible progress should likely reuse or extend the existing rendered status surfaces with more Hermes-native wording.
- Downstream qualification, proposal, and delivery stages should continue to inherit the same canonical run identity created at project start.

</code_context>

<specifics>
## Specific Ideas

- Auto-selected the single-entrypoint default because the milestone explicitly wants Hermes to be the only intentional control surface.
- Defaulted to reusing the shipped intake/run backbone under a thinner Hermes-facing layer so v1.3 does not fork authority truth.
- Chose Hermes-native owner language over chat/script jargon on the healthy path while preserving inspectable artifacts underneath.

</specifics>

<deferred>
## Deferred Ideas

- Detailed internal company-role sequencing belongs to Phase 27.
- Proposal rendering, approval semantics, and locked contract presentation belong to Phase 28.
- Final success and blocked recovery presentation belong to Phase 29.

</deferred>

---

*Phase: 26-hermes-intent-gateway-and-unified-project-start*
*Context gathered: 2026-05-05*
