# Phase 20: Real Product Proof and Conformance Hardening - Context

**Gathered:** 2026-05-04
**Status:** Ready for planning

<domain>
## Phase Boundary

Harden Hermes so approved-project delivery only counts as successful when the generated SaaS workspace proves a real product workflow exists. This phase removes `/demo` and identity-only loopholes, raises template residue to a blocking governance failure on primary product surfaces, and makes final validation/operator review explain exactly which workflow surfaces and supporting logic prove real delivery.

</domain>

<decisions>
## Implementation Decisions

### Product proof source of truth
- **D-01:** Product proof should be derived from the existing `build_product_proof_summary(...)` seam and persisted as structured evidence, not inferred separately by conformance, status rendering, and final validation with different rules.
- **D-02:** Acceptable proof must require both a product-facing primary workflow surface under `src/app/**` and supporting logic evidence under `src/lib/**`, `src/app/api/**`, or `supabase/**`; either one alone is insufficient.
- **D-03:** Identity/bootstrap-only paths such as `src/lib/app-definition.ts` must always be listed as excluded proof, never promoted into product proof even when they changed alongside real work.

### Demo and template residue policy
- **D-04:** `/demo` routes must be treated as permanently excluded proof surfaces rather than a privileged shortcut for proving product delivery.
- **D-05:** Template/example residue on primary workflow surfaces must remain a blocking failure, while residue on secondary surfaces may render as warnings until a later cleanup phase promotes them further.
- **D-06:** Phase 20 should harden proof classification generically around path classes and residue detection instead of adding another brittle hard-coded allow/deny list beyond the existing contract constants.

### Gate layering between conformance and final validation
- **D-07:** Template conformance should keep enforcing baseline workspace-level proof prerequisites early: product-facing implementation exists, multilingual evidence exists, and primary surfaces do not still read like the raw template.
- **D-08:** Approved-delivery final validation should enforce the stronger end-to-end proof contract: rendered status/review must name the exact workflow surfaces, supporting logic, excluded proof paths, residue findings, and proof verdict that justified success or failure.
- **D-09:** Specialist-stage substance checks, conformance, and final pipeline validation must all consume the same proof vocabulary (`proof_verdict`, `primary_workflow_surfaces`, `supporting_logic_paths`, `excluded_proof_*`, `template_residue_*`, `failure_reasons`) so governance truth does not drift by surface.

### Operator-facing proof visibility
- **D-10:** Operator-facing status and final review must explicitly explain why a run passed or failed product proof, not just show that delivery reached handoff/GitHub/Vercel stages.
- **D-11:** Proof failure messages should stay reason-coded and human-readable, using the existing failure-reason mapping pattern so operators can see whether the problem was demo-only proof, identity-only changes, missing workflow surfaces, missing supporting logic, or template residue.
- **D-12:** Phase 20 should preserve the current authority-first model: proof verdicts and explanations are rendered from persisted structured artifacts/events, not re-derived ad hoc from markdown prose.

### the agent's Discretion
- Exact expansion of excluded-proof path constants beyond the already-observed `/demo` and identity-only seams
- Exact persistence location for any new proof snapshots, as long as status, final review, and validators read the same authoritative fields
- Exact wording and ordering of proof sections in handoffs/status markdown, as long as required proof tokens and paths remain explicit and stable

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and milestone constraints
- `.planning/ROADMAP.md` - Phase 20 goal, boundaries, and milestone risk framing for real product proof hardening
- `.planning/REQUIREMENTS.md` - `PROOF-01`, `PROOF-02`, and `PROOF-03`
- `.planning/PROJECT.md` - v1.1.2 governance-hardening objective and the explicit decision to remove `/demo` and identity-only proof
- `.planning/STATE.md` - current milestone position and pending Phase 20 work

### Prior phase decisions that must carry forward
- `.planning/phases/10-approved-project-delivery-pipeline/10-CONTEXT.md` - authority-first delivery state model, block/resume semantics, and approved-project pipeline layering
- `.planning/phases/18-handoff-contract-and-authority-alignment/18-CONTEXT.md` - latest-governance-truth model, shared machine-readable contract expectations, and operator-surface convergence requirements

### Existing contracts and proof surfaces
- `docs/platform/standalone-saas-template-contract.md` - canonical template rules, proof prerequisites, multilingual expectations, and conformance gate obligations
- `docs/OPERATIONS.md` - operator command flow and the expectation that validation proves the approval-to-handoff chain before success is declared
- `docs/skill-governance/templates/stage-handoff-template-v0.2.md` - specialist handoff contract that downstream proof explanations must remain compatible with

### Existing code and tests
- `scripts/product_proof_contract.py` - canonical proof classification rules for identity-only paths, `/demo`, primary workflow surfaces, supporting logic, and template residue
- `scripts/check_template_conformance.py` - current baseline conformance enforcement for product-facing implementation, multilingual evidence, and template residue on primary surfaces
- `scripts/start_approved_project_delivery.py` - proof-summary generation, stage evidence persistence, and operator-facing final delivery summary integration
- `scripts/render_approved_delivery_status.py` - authority-derived status/final-review rendering, including the current Product Proof section
- `scripts/validate_approved_delivery_pipeline.py` - final cross-artifact validation for proof visibility and operator-facing explanation completeness
- `tests/test_approved_delivery_pipeline_cli.py` - validator expectations for template-only specialist output, proof sections, and rendered authority truth
- `tests/test_project_delivery_pipeline_bootstrap.py` - bootstrap/runtime fixtures showing how proof evidence, UI artifacts, and final status surfaces are expected to persist
- `tests/test_project_delivery_pipeline_resume.py` - resume-path governance truth and proof-related authority/event convergence expectations

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `scripts/product_proof_contract.py`: already centralizes the product-proof taxonomy and is the natural place to harden `/demo`, identity-only, and template-residue rules instead of scattering new logic.
- `scripts/check_template_conformance.py`: already blocks missing product-facing pages, multilingual evidence gaps, and primary-surface template residue before downstream delivery continues.
- `scripts/start_approved_project_delivery.py`: already records proof summaries into stage/workspace evidence and final delivery artifacts, giving Phase 20 an existing persistence path.
- `scripts/render_approved_delivery_status.py`: already renders a dedicated `## Product Proof` section on operator surfaces.
- `scripts/validate_approved_delivery_pipeline.py`: already validates proof visibility across status and final review, making it the natural place to harden PROOF-03.

### Established Patterns
- Governance logic in this repo prefers one reusable contract module plus multiple validators/renderers consuming the same machine-readable fields.
- Authority JSON and append-only events remain the canonical truth; markdown is derived operator-facing output.
- Blocking delivery rules are enforced early when possible, then revalidated later with stronger cross-surface checks.
- The repo already distinguishes blocking failures from warnings, which fits the primary-vs-secondary residue split.

### Integration Points
- Phase 20 will likely touch `product_proof_contract.py`, `check_template_conformance.py`, `start_approved_project_delivery.py`, `render_approved_delivery_status.py`, and `validate_approved_delivery_pipeline.py` together.
- Test coverage should extend the approved-delivery CLI/bootstrap/resume suites instead of introducing an isolated proof-only test harness.
- Phase 21 resume hardening depends on Phase 20 persisting product-proof truth in a stable machine-readable form, so proof-state fields added here should be resume-safe.

</code_context>

<specifics>
## Specific Ideas

- Auto-selected all relevant proof gray areas because `--auto` was requested.
- Auto-selected the stricter default that real delivery requires both user-facing workflow surfaces and supporting logic, rather than allowing a single surface class to pass.
- Auto-selected the existing repo seam (`scripts/product_proof_contract.py`) as the canonical proof vocabulary instead of creating a second proof classifier.

</specifics>

<deferred>
## Deferred Ideas

- Expanding UI artifact coverage rules remains Phase 19 scope, not Phase 20.
- Bootstrap/resume parity and recovered-state regression closure remain Phase 21 scope, though Phase 20 should preserve resume-safe proof fields.
- Broader cleanup of secondary template/example residue across non-primary surfaces can be tightened in a future phase once primary-surface blocking is stable.
- None from matched todos; `gsd-sdk query todo.match-phase 20` returned no relevant pending todos.

</deferred>

---

*Phase: 20-real-product-proof-and-conformance-hardening*
*Context gathered: 2026-05-04*
