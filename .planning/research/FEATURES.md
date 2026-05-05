# Feature Landscape

**Domain:** Governed brownfield SaaS delivery hardening for Profit-Corp Hermes
**Milestone:** v1.1.2 real-SaaS delivery governance hardening
**Researched:** 2026-05-03
**Confidence:** HIGH

## Scope of This Milestone

This milestone should harden the already-shipped approved-project delivery pipeline so it behaves like a mature governed factory, not a best-effort agent demo. The system already has approved-project bootstrap, specialist execution, GitHub/Vercel delivery, conformance checks, blocked-state recovery, and authority/status convergence. New work should therefore focus on tightening proof standards, making required artifacts executable gates instead of policy text, and expanding regressions around bootstrap/resume behavior.

The target behavior is simple: downstream delivery should only advance when each stage leaves verifiable evidence that the right specialist did the right work, using the right contract, with the right artifacts, and without relying on placeholder template proof.

## Table Stakes

Features a mature governed delivery system must have for this milestone. Missing any of these means Hermes still behaves like a fragile orchestrated demo rather than a trustworthy delivery pipeline.

| Feature | Why Expected | Complexity | Existing Pipeline Dependencies | Expected Behavior | Must Block |
|---------|--------------|------------|-------------------------------|------------------|------------|
| Specialist evidence gating | Specialist stages are only trustworthy if they emit stage-specific proof, not just a stage name or success flag | HIGH | Phase 9 specialist workflow, approved-delivery events, FINAL_DELIVERY/FINAL_OPERATOR_REVIEW surfaces, validator CLI | Every specialist stage must produce machine-checkable and human-readable evidence before the next stage can run. “Completed” means artifact exists, is non-empty, matches the stage contract, and links to the governed run. | Missing artifact, empty artifact, wrong specialist, wrong stage, stale artifact from prior run, freeform output without required fields |
| Mandatory `/ui-ux-pro-max` artifact enforcement | Frontend delivery should never proceed on user-facing surfaces without the required design-system artifact | MEDIUM-HIGH | CLAUDE.md policy, template conformance gate, `.hermes/project-metadata.json`, delivery stage contracts | Any project with user-facing UI scope must record the `/ui-ux-pro-max` artifact path and use that artifact as the design source of truth for implementation and review. Conformance and delivery validation should treat this as a real prerequisite. | Frontend implementation without artifact, missing artifact path, artifact generated after implementation, artifact unrelated to delivered surfaces |
| Handoff contract alignment across stages | Mature pipelines cannot rely on loosely interpreted handoffs between specialists | HIGH | Core 9 handoff model, Phase 6 delivery handoff contract, Phase 9 specialist orchestration, approved-delivery validator | Stage handoffs should share one normalized contract: inputs consumed, outputs produced, readiness status, open risks, evidence links, next-stage expectations. Final operator review must derive from the same chain. | Stage marked complete without contract fields, downstream stage consuming undocumented assumptions, final review not traceable to stage handoffs |
| Remove `/demo` and identity-only proof assumptions | A real-SaaS factory must prove product-specific implementation exists beyond template identity injection | HIGH | Template conformance, project instantiation, conformance report, approved-delivery validator | Delivery proof must require product-facing implementation and removal/replacement of template placeholder surfaces. Identity injection (`APP_KEY`, `APP_NAME`, `APP_URL`) is necessary but never sufficient proof of real work. | Shipping template demo routes as primary product surface, passing conformance because only identity values changed, final proof based only on metadata or naming |
| Stronger bootstrap and resume regression coverage | Governance is brittle if bootstrap/recovery behavior can silently drift across shells, stages, or resume paths | MEDIUM-HIGH | `bootstrap_hermes.sh`, `bootstrap_hermes.ps1`, noninteractive bootstrap, start/resume commands, Phase 17 persisted-state model, CLI validator tests | Regression coverage should prove fresh-start, blocked-state, resumed-state, recovered-final-state, and platform-path behavior all preserve authority truth and do not duplicate workspaces or skip gates. | Resume replays completed stages, bootstrap/resume diverge on artifact requirements, recovered run reports success without matching authority/status/final review |

## Differentiators

These are the milestone features that make Hermes better than a generic agent pipeline. They are not optional forever, but compared with the table stakes above they are more about strengthening the product’s governance edge than achieving basic legitimacy.

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| Evidence-first delivery validator | Turns delivery success from a narrative into a replayable proof chain | MEDIUM | Best implemented by extending existing validator and status rendering rather than inventing a second governance path |
| Cross-surface truth convergence | Operator-facing status, authority JSON, event log, and final handoff all tell the same story | HIGH | Strong differentiator because most agent systems drift between machine state and human summaries |
| Frontend-governance as code | Enforces `/ui-ux-pro-max` the same way backend/runtime contracts are enforced | MEDIUM-HIGH | This is how Hermes avoids “nice policy, ignored in practice” failure |
| Brownfield-safe recovery semantics | Resume continues from persisted truth instead of rebuilding from assumptions | MEDIUM | Important because this repo already operates on real operator machines with partial runs and environmental drift |
| Product-proof over template-proof | Requires evidence of shipped product specificity rather than passing renamed-template checks | HIGH | Critical for the user’s “real SaaS, not template surface” requirement |

## Anti-Features

These should be explicitly avoided in v1.1.2. They create the appearance of governance while weakening the actual system.

| Anti-Feature | Why Avoid | What to Do Instead |
|--------------|-----------|-------------------|
| Treating a stage status flag as proof | Lets pipelines pass with no verifiable work behind the label | Require artifact-backed completion with schema/contract checks |
| Policy-only `/ui-ux-pro-max` enforcement | Humans forget; agents bypass; later reviewers cannot prove compliance | Persist artifact references in metadata/handoffs and fail validation when missing |
| Identity injection counted as “implementation complete” | Renaming template variables is not product delivery | Require product-facing diff evidence and placeholder/demo removal checks |
| Manual operator interpretation as the recovery mechanism | Makes brownfield recovery non-repeatable and untestable | Persist authoritative stage, block reason, and resume point in machine-readable state |
| Creating a second handoff dialect for delivery specialists | Reintroduces drift between planning, delivery, and final review | Reuse one normalized handoff contract shape end-to-end |
| Broadening scope into new product-factory capabilities | Distracts from governance hardening and dilutes milestone proof | Keep this milestone focused on stricter gates, contracts, and regressions |

## Expected Behavior by Target Feature

### 1. Specialist evidence gating

A mature governed system should treat every specialist as a controlled producer of evidence, not as an opaque executor.

Expected behavior:
- Each specialist stage has required evidence artifacts.
- Artifacts are both human-reviewable and machine-checkable.
- Evidence is attributed to the correct specialist, stage, and delivery run.
- Validators reject stale artifacts copied from prior runs or unrelated paths.
- Final delivery success is impossible unless the evidence chain is complete from specialist stages through final handoff.

Recommended proof model:
- Stage handoff markdown for human review.
- Structured event/manifest entry for machine validation.
- Stable linkage from stage artifact -> approved project -> delivery run -> final operator review.

Complexity: High, because it touches orchestration, validator logic, status rendering, and possibly artifact schemas.

### 2. Mandatory `/ui-ux-pro-max` artifact enforcement

The system already has a policy rule and template metadata expectation. In a mature system, that becomes a gate.

Expected behavior:
- If a project includes user-facing UI work, the design specialist cannot complete without a persisted `/ui-ux-pro-max` artifact.
- Development cannot begin on user-facing implementation until that artifact is referenced in the handoff contract.
- Testing/final review must confirm delivered UI surfaces align with the artifacted design intent.
- Non-frontend-only projects may explicitly mark the requirement as not applicable, but that exception must be deliberate and recorded.

What should count as compliance:
- Artifact path exists.
- Artifact is non-empty and tied to the project.
- Artifact is referenced in project metadata and specialist handoff.
- Delivered UI scope is traceable back to the artifact.

What should not count:
- Merely mentioning `/ui-ux-pro-max` in prose.
- Running the skill after the UI is already built.
- Reusing a generic artifact with no project-specific mapping.

Complexity: Medium-high. Mostly governance and validator work, not new platform architecture.

### 3. Handoff contract alignment

The mature behavior is contract continuity, not stage-local improvisation.

Expected behavior:
- Every stage emits the same core handoff fields: scope, inputs, outputs, evidence, blockers, residual risks, readiness, and next step.
- Resume logic relies on persisted contract state, not markdown interpretation alone.
- Final operator review is a rendered summary of the same truth, not a separate narrative assembled by hand.
- The validator can prove that every downstream stage consumed a complete upstream handoff.

This milestone should prefer normalization over expansion. Do not add more stage concepts; make existing stages line up.

Complexity: High, because drift can exist across markdown templates, event streams, validator logic, and rendering surfaces.

### 4. Remove `/demo` and identity-only proof assumptions

The mature rule is: renamed template proof is not product proof.

Expected behavior:
- Delivery cannot pass when demo/template routes remain the primary user-facing experience.
- Conformance should require evidence of product-specific implementation beyond `src/lib/app-definition.ts` and beyond pure identity injection.
- Final review should summarize which product surfaces prove the project is no longer just the template.
- Placeholder/template markers should be treated as governance failures, not cleanup suggestions.

Recommended blocking cases:
- `src/app/demo/page.tsx` remains a primary shipped surface without explicit replacement/removal policy.
- Product content still reads as template example text.
- Artifact chain shows only config/identity changes but no user-facing product implementation.

Complexity: High because it tightens the definition of “real delivery” and may require conformance, validator, and final-review changes together.

### 5. Stronger bootstrap/resume regressions

This milestone should raise confidence in recovery behavior, not just happy-path delivery.

Expected behavior:
- Fresh bootstrap and resumed runs enforce the same governance gates.
- Resume never silently skips missing artifacts or rebuilds a second workspace unless authority explicitly requires it.
- Recovered success updates `APPROVED_PROJECT.json`, `DELIVERY_PIPELINE_STATUS.md`, and `FINAL_OPERATOR_REVIEW.md` to the same final truth.
- Tests cover blocked states at the exact stages introduced by stricter governance.
- Shell/bootstrap entrypoints behave consistently enough that the operator does not get different governance outcomes by platform path.

Priority regression areas:
1. Resume from blocked design stage with missing `/ui-ux-pro-max` artifact.
2. Resume from blocked conformance stage with lingering `/demo` or template markers.
3. Resume after specialist artifact drift where stage status says complete but evidence is missing.
4. Bootstrap parity across interactive/noninteractive and shell/platform paths for governance prerequisites.

Complexity: Medium-high. The hard part is comprehensive scenario coverage, not algorithmic novelty.

## What Must Be Blocked

These are hard blockers for a governed delivery system in this milestone.

| Block Condition | Why It Must Block | Dependency |
|----------------|-------------------|------------|
| Specialist stage reports success without required artifact evidence | Success without proof breaks governance trust | Stage orchestration + validator |
| `/ui-ux-pro-max` artifact missing for frontend scope | Violates explicit project policy and design governance | CLAUDE.md + metadata + conformance |
| Handoff missing required normalized fields | Downstream stage cannot safely rely on upstream work | Handoff templates + validator |
| Delivery proof depends only on project identity values | Confuses initialization with implementation | Conformance + final review |
| Demo/template surface remains as shipped product proof | Violates real-SaaS requirement | Template conformance + product-proof checks |
| Resume path skips required gates because prior stage status was cached | Cached state must not outrank actual evidence | Persisted-state model + resume tests |
| Authority/status/final review disagree after recovery | Operator loses a single source of truth | Convergence logic + rendering tests |

## Explicitly Out of Scope

This milestone should stay narrow. The right job is governance hardening, not expanding the factory into new product domains.

| Out of Scope | Why |
|--------------|-----|
| Building new end-user SaaS product features inside Hermes | This milestone is about delivery governance behavior, not product application scope |
| Replacing the approved-project pipeline with a new orchestration model | Brownfield constraint: extend the existing pipeline, do not restart architecture |
| Supporting fully custom non-template stacks as the default | Contradicts current shared-template/shared-Supabase strategy |
| Expanding specialist roles beyond the existing normalized team | Current problem is proof quality and handoff rigor, not missing role count |
| Creating a real-time operator dashboard for these rules first | Existing markdown/JSON authority surfaces are sufficient if they converge correctly |
| Solving all finance or cron governance gaps unrelated to approved delivery hardening | Valuable later, but not on the critical path for this milestone |
| Broad UI redesign of generated SaaS products | Enforce artifact-first governance; do not turn this into a design-production milestone |

## Feature Dependencies

```text
Specialist evidence gating
    ├──requires──> normalized stage handoff contract
    ├──requires──> artifact attribution to specialist + run
    └──requires──> validator enforcement

Mandatory /ui-ux-pro-max artifact enforcement
    ├──requires──> frontend-scope detection
    ├──requires──> metadata persistence
    ├──requires──> handoff contract references
    └──requires──> conformance + resume gating

Remove /demo and identity-only proof assumptions
    ├──requires──> stronger conformance checks
    ├──requires──> product-proof criteria in final review
    └──requires──> validator awareness of placeholder/template markers

Stronger bootstrap/resume regressions
    ├──requires──> persisted authority truth
    ├──requires──> scenario coverage for blocked stages
    └──requires──> parity across bootstrap/resume entrypoints
```

## MVP Recommendation for v1.1.2

Prioritize in this order:
1. Specialist evidence gating
2. Mandatory `/ui-ux-pro-max` artifact enforcement
3. Handoff contract alignment
4. Remove `/demo` and identity-only proof assumptions
5. Stronger bootstrap/resume regression coverage

Why this order:
- Evidence gating is the root control. Without it, every later rule is advisory.
- `/ui-ux-pro-max` enforcement is already a declared policy and metadata contract, so it should become executable next.
- Handoff alignment is required to make stage-to-stage evidence and resume logic coherent.
- Demo/identity-proof tightening defines what counts as real-SaaS completion.
- Regression expansion should then lock the hardened behavior in place.

## Complexity and Delivery-Pipeline Impact

| Feature | Implementation Complexity | Pipeline Impact | Notes |
|---------|---------------------------|-----------------|-------|
| Specialist evidence gating | High | High | Touches stage completion semantics, validator, status, and final proof surfaces |
| Mandatory `/ui-ux-pro-max` enforcement | Medium-High | Medium-High | Mostly contract and validator work; should integrate with existing metadata/conformance path |
| Handoff contract alignment | High | High | Cross-cuts stage templates, event model, resume truth, and final rendering |
| Remove `/demo` and identity-only proof assumptions | High | High | Tightens conformance definition of “real product delivered” |
| Stronger bootstrap/resume regressions | Medium-High | Medium | Heavy test work with some controller/validator hardening |

## Recommended Acceptance Lens

The milestone should be considered successful when Hermes can prove all of the following on a fresh or resumed approved-project run:
- every specialist completion is backed by required evidence
- frontend work cannot pass without `/ui-ux-pro-max` artifacts where applicable
- stage handoffs share one coherent contract
- real product implementation is required beyond identity injection and template/demo remnants
- bootstrap/resume recovery preserves one authoritative truth across machine-readable and operator-facing artifacts

## Sources

- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/PROJECT.md`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/docs/platform/standalone-saas-template-contract.md`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/docs/OPERATIONS.md`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/codebase/CONCERNS.md`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/CLAUDE.md`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/phases/09-claude-code-delivery-team-orchestration/09-RESEARCH.md`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/phases/16-vercel-auth-and-deploy-reliability/16-RESEARCH.md`
