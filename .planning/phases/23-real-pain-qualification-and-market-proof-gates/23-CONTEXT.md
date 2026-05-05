# Phase 23: Real-Pain Qualification and Market Proof Gates - Context

**Gathered:** 2026-05-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Require Hermes to prove that a candidate pain point is recent, real, narrow enough to build on the shared platform, and commercially plausible before it can become an operator-facing proposal.

This phase owns freshness, pain reality, feasibility, and market/pricing evidence gates before proposal approval. It does not yet define the final approval package shape or chat approval protocol, and it does not reopen the downstream approved-project delivery machinery.

</domain>

<decisions>
## Implementation Decisions

### Freshness gate
- **D-01:** Qualification should use artifact-backed evidence timestamps and fail any candidate whose required pain evidence is older than 72 hours at qualification time.
- **D-02:** Freshness should be evaluated from persisted source/evidence metadata inside shared discovery artifacts, not from prose summaries that require the operator to infer recency manually.
- **D-03:** If freshness cannot be proven for every required evidence link, the candidate should block before proposal generation instead of degrading into a warning.

### Real-pain qualification contract
- **D-04:** Hermes should require a structured qualification bundle that proves the pain is user-facing, specific, and narrow enough to support one focused SaaS workflow rather than a vague market theme.
- **D-05:** Qualification should reject ideas that only show generic demand, trend chatter, or broad business categories without a concrete repeated pain pattern and target operator/user segment.
- **D-06:** The qualification result should be machine-readable and reason-coded so later proposal and approval steps can tell exactly which gate passed or failed.

### Feasibility against the shared platform
- **D-07:** Buildability must be judged against the shipped shared-template and shared-Supabase contract, not against an imaginary custom stack that Hermes does not actually deliver by default.
- **D-08:** Qualification should block ideas that require protected-platform rewrites, broad custom backend work, or product scope too large for the governed template-based delivery path.
- **D-09:** Feasibility proof should explicitly connect the proposed workflow to known template/backend capabilities and known constraints, rather than leaving that check as planner intuition later.

### Market and pricing proof
- **D-10:** Market, competitor, and pricing evidence should become mandatory qualification artifacts for every proposal candidate, not optional narrative fields.
- **D-11:** Pricing proof should be tied to the actual pain/workflow and intended paid outcome, so Hermes cannot advance a candidate with a strong pain story but no believable monetization path.
- **D-12:** Missing or thin market/pricing evidence should stop the run before proposal approval rather than being carried as a soft caveat into operator review.

### the agent's Discretion
- Exact scoring formula used to summarize qualification results, as long as pass/fail truth remains artifact-backed and explainable.
- Exact storage location for the qualification bundle, as long as later proposal/approval steps can read it canonically.
- Exact competitor/pricing evidence schema, as long as it preserves freshness, traceability, and buildability relevance.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and milestone contract
- `.planning/ROADMAP.md` - Phase 23 goal and success criteria for qualification gating.
- `.planning/REQUIREMENTS.md` - `QUAL-01` through `QUAL-04`.
- `.planning/PROJECT.md` - milestone intent to stop weak ideas before approval and preserve the shared-template/shared-Supabase model.
- `.planning/STATE.md` - current milestone concerns and pending qualification-hardening goals.

### Prior decisions that constrain this phase
- `.planning/phases/01-external-intelligence-foundation/01-VERIFICATION.md` - persisted external-intelligence artifact family and run-history model.
- `.planning/phases/02-signal-triage-and-role-analysis-loop/02-VERIFICATION.md` - shared prioritized-signal flow and role-analysis loop that qualification should build on.
- `.planning/phases/03-decision-package-quality/03-CONTEXT.md` - operating decision package traceability and evidence backlink expectations.
- `.planning/phases/08-shared-supabase-backend-guardrails/08-RESEARCH.md` - shared-backend constraint logic that feasibility checks must honor.
- `.planning/phases/20-real-product-proof-and-conformance-hardening/20-CONTEXT.md` - preference for one canonical proof vocabulary and fail-closed gating, which qualification should mirror upfront.

### Existing artifacts and contracts
- `assets/shared/external_intelligence/LATEST_SUMMARY.md` - current discovery-summary surface fed by fresh source evidence.
- `assets/shared/external_intelligence/history/runs.jsonl` - run-history evidence timestamps and collection records.
- `assets/shared/external_intelligence/triage/prioritized_signals.json` - structured shortlist candidates with evidence links and scoring metadata.
- `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` - current operator-facing synthesis artifact that proposal gating will sit in front of.
- `docs/platform/standalone-saas-template-contract.md` - shared-template capabilities and protected-layer constraints used for buildability checks.
- `docs/STATE_CONTRACT.md` - durable shared-state write boundaries for any new qualification artifacts.

### Existing code and tests
- `scripts/generate_decision_package.py` - current evidence-backed decision-package synthesis path and trace sidecar contract.
- `scripts/start_approved_project_delivery.py` - approved-project bundle contract whose inputs should be blocked until qualification passes.
- `scripts/instantiate_template_project.py` - template metadata and managed-file assumptions relevant to feasibility checks.
- `tests/test_generate_decision_package.py` - latest/history/trace expectations for evidence-backed operator artifacts.
- `tests/test_approved_project_record.py` - approved-project record fields that future proposal gating will have to populate from qualified evidence.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `assets/shared/external_intelligence/triage/prioritized_signals.json`: already carries structured candidate-level evidence and scoring fields that can seed freshness and reality gates.
- `scripts/generate_decision_package.py`: already expects backlinkable evidence, run ids, and structured source metadata instead of freeform summaries.
- `docs/platform/standalone-saas-template-contract.md`: already describes the delivery platform constraints qualification must honor before a candidate can be approved.
- `scripts/start_approved_project_delivery.py`: already blocks missing pain point, monetization, required languages, and approval evidence once a project reaches the approved-project stage.

### Established Patterns
- Hermes favors durable machine-readable sidecars and explicit backlink fields over operator-inferred truth.
- Governance in this repo is usually fail-closed: missing required evidence blocks progress rather than producing a "best effort" artifact.
- Later pipeline stages already use reason-coded failures, so qualification should surface missing freshness/reality/feasibility/pricing in the same style.

### Integration Points
- Qualification should likely sit between prioritized-signal generation and proposal/approved-project bundle creation.
- Structured qualification output should become a canonical upstream input to proposal generation and approval packaging.
- Feasibility checks should read the existing template/shared-backend contracts rather than duplicating platform rules in yet another document.

</code_context>

<specifics>
## Specific Ideas

- Auto-selected the stricter default that freshness must be proven from persisted evidence metadata, not inferred from markdown prose.
- Auto-selected artifact-backed pass/fail gates for pain reality, feasibility, and pricing because later approval and delivery stages already rely on machine-readable truth.
- Defaulted to evaluating buildability against the actual shared template/shared Supabase platform instead of hypothetical custom-stack feasibility.

</specifics>

<deferred>
## Deferred Ideas

- Final proposal wording, operator-facing proposal presentation, and approval UX belong to Phase 24.
- Post-approval autonomous continuation belongs to Phase 25.
- Broader product portfolio strategy or long-horizon market expansion logic remains out of scope; this phase is about candidate gating for one buildable proposal.

</deferred>

---

*Phase: 23-real-pain-qualification-and-market-proof-gates*
*Context gathered: 2026-05-04*
