# Domain Pitfalls

**Domain:** Brownfield real-SaaS delivery governance on top of an existing approved-delivery pipeline
**Researched:** 2026-05-03

## Critical Pitfalls

Mistakes that are especially dangerous for milestone v1.1.2, where Hermes is tightening governance on an already-shipped and recently repaired approved-project delivery path.

### Pitfall 1: Adding new gates without preserving authority/status truth convergence
**What goes wrong:**
New specialist evidence gates or design-validation checks block or pass work, but their outcome is not reflected consistently across `APPROVED_PROJECT.json`, `DELIVERY_PIPELINE_STATUS.md`, `FINAL_OPERATOR_REVIEW.md`, validator output, and workspace-local `.hermes` artifacts.

**Why it happens:**
v1.1.1 already had to repair truth convergence across authority JSON, status markdown, final review, and validation. A new gate is easy to add at one stage boundary while forgetting the downstream renderers, resume logic, or validator precedence rules.

**Consequences:**
- Operators see different truths in different artifacts
- Resume logic restarts from the wrong stage or thinks a block is cleared when it is not
- Governance becomes less trustworthy exactly when it is meant to become stricter

**Prevention:**
- Treat every new gate as a cross-surface contract change, not a local stage change
- Require one canonical machine-readable gate state that renderers and validators consume
- Extend `validate-approved-delivery-pipeline` to prove gate outcome convergence across authority, status, final review, and workspace manifest
- Keep blocked history as audit evidence only; do not let stale blocked evidence override final recovered success

**Detection / Warning signs:**
- `DELIVERY_PIPELINE_STATUS.md` says blocked while final review says complete
- Resume chooses a stage that conflicts with the latest gate evidence
- Manual explanation is needed to reconcile why the operator-visible status differs from validator results

**Later roadmap phases that should absorb mitigation:**
- Phase: Governance gate state model hardening
- Phase: Status/validator convergence extension
- Phase: Resume/recovery truth-source verification

### Pitfall 2: Converting stage handoffs into box-checks instead of enforceable contracts
**What goes wrong:**
Specialist handoffs still exist as markdown files, but stricter governance only checks file presence, not whether the next stage received the required structured inputs, explicit decisions, open risks, and blocked prerequisites.

**Why it happens:**
The current delivery model already requires stage handoffs and final delivery artifacts, but the brownfield pipeline was originally optimized to move work through stages. Tightening governance can stop at “artifact exists” instead of “artifact proves readiness and scope discipline.”

**Consequences:**
- Development starts without a validated design contract
- Testing validates implementation details but misses approved requirements
- Release readiness approves work with unresolved scope changes or undocumented exceptions

**Prevention:**
- Upgrade each handoff from free-form narrative to a minimally structured contract
- Validate required sections: input authority, accepted scope, evidence links, unresolved risks, explicit go/no-go decision, and downstream obligations
- Fail the next stage if upstream handoff fields are missing or contradictory
- Ensure protected-path and expanded-scope requests still route through `request_scope_reopen.py` rather than being buried in prose

**Detection / Warning signs:**
- Handoff files all exist, but reviewers still ask “what exactly was approved?”
- Design, development, and testing handoffs each describe a different product boundary
- Scope changes appear first in code or screenshots, not in handoff contracts

**Later roadmap phases that should absorb mitigation:**
- Phase: Stage-handoff schema formalization
- Phase: Handoff validator enforcement
- Phase: Scope-reopen workflow integration

### Pitfall 3: Treating mandatory design-artifact validation as UI polish instead of release governance
**What goes wrong:**
Design artifacts become required on paper, but the gate checks only that a file exists or a `/ui-ux-pro-max` artifact is referenced. It does not prove the implemented workspace still matches the approved design contract, required language set, or product-facing differentiation from the template.

**Why it happens:**
The template contract already requires `/ui-ux-pro-max` UI artifact coverage inside `product_requirements`, language requirements (`en`, `zh`), product-facing implementation beyond the template shell, and removal of raw template markers. Brownfield teams often add a “design artifact required” step without wiring it into conformance and release validation.

**Consequences:**
- Teams satisfy governance with screenshots or docs while shipping template-like UX
- Product surfaces drift from approved design decisions without any blocking signal
- Design review becomes ceremonial instead of controlling release readiness

**Prevention:**
- Make design validation part of conformance and release-readiness gates, not an optional pre-dev artifact
- Verify traceability: approved brief -> design artifact -> implemented surface -> final handoff evidence
- Check required languages, core user flows, and product differentiation claims in final review
- Block release if design evidence is stale relative to later implementation changes

**Detection / Warning signs:**
- Design artifact date predates significant implementation changes with no refresh
- Final handoff shows product URLs but no evidence tying them back to the approved design contract
- Template markers or untranslated surfaces survive despite a “passed” design gate

**Later roadmap phases that should absorb mitigation:**
- Phase: Design-contract traceability enforcement
- Phase: Conformance gate expansion for UI evidence
- Phase: Release-readiness visual/product validation

### Pitfall 4: Over-tightening evidence gates until the repaired delivery path becomes unrecoverable again
**What goes wrong:**
New mandatory evidence steps are inserted in ways that break resume behavior, turn recoverable downstream prerequisites into dead ends, or force operators back into manual workaround loops.

**Why it happens:**
v1.1.1 explicitly moved delivery toward a recoverable, evidence-driven pipeline with resume-from-state behavior. Stricter governance often adds synchronous hard stops without designing how blocked evidence is generated, updated, and resumed.

**Consequences:**
- A missing design or specialist artifact requires restarting instead of resuming
- Operators create side-channel fixes because the official path cannot recover cleanly
- Governance work undermines the core promise of one-approval automated delivery

**Prevention:**
- Define resume semantics for every new gate before implementing the gate itself
- Persist missing-prerequisite evidence the same way credential/deployment blocks are already persisted
- Separate “hard fail forever” from “block until required evidence artifact appears”
- Test partial-progress recovery on existing workspaces, not only clean-start scenarios

**Detection / Warning signs:**
- Teams re-run `start-approved-delivery` to clear governance blocks
- A gate failure leaves no persisted artifact telling the operator what to fix
- Existing workspace refresh logic works for GitHub/Vercel issues but not for new governance failures

**Later roadmap phases that should absorb mitigation:**
- Phase: Governance-aware resume semantics
- Phase: Existing-workspace recovery testing
- Phase: Block-reason artifact standardization

### Pitfall 5: Letting stricter evidence gates drift away from the approved-project authority layer
**What goes wrong:**
Specialist evidence, design approvals, and regression decisions live only in workspace-local `.hermes` files or ad-hoc notes, while `APPROVED_PROJECT.json` and approved-project bundle metadata remain blind to the new governance state.

**Why it happens:**
The brownfield architecture explicitly keeps the approved-project authority layer above workspace-local artifacts. New milestone work may be implemented in the workspace because it is faster, but that weakens operator-safe governance and makes cross-run reasoning fragile.

**Consequences:**
- Authority bundle no longer tells the full story of what is approved, blocked, or waived
- Recreated or refreshed workspaces lose critical governance context
- Validator must infer governance truth from scattered local evidence

**Prevention:**
- Decide which new governance facts belong in authority records versus workspace execution artifacts
- Persist gate decisions, waivers, and reopen events in the approved-project bundle or linked authority-owned evidence index
- Keep workspace-local artifacts as execution evidence, not the only record of governance truth

**Detection / Warning signs:**
- You cannot answer “why was release allowed?” from the approved-project directory alone
- Rehydrating a workspace loses specialist approval history
- Final operator review links to local-only artifacts that are not represented in authority state

**Later roadmap phases that should absorb mitigation:**
- Phase: Authority schema evolution for governance evidence
- Phase: Approved-project bundle enrichment
- Phase: Cross-artifact provenance indexing

### Pitfall 6: Enforcing regression updates as a documentation ritual instead of a contract with the repaired pipeline
**What goes wrong:**
Teams add “update regressions” to the checklist, but regression coverage does not actually capture the newly tightened governance behaviors: gate persistence, handoff completeness, design validation blocking, resume after evidence arrival, and final-truth convergence.

**Why it happens:**
The repo already tightened delivery regression coverage in v1.1.1, but that coverage focused on auth, sync, deploy, restore, and status reliability defects. New governance logic can land without extending the regression model from delivery mechanics to delivery-governance mechanics.

**Consequences:**
- Future fixes reintroduce silent bypasses in evidence gates
- Validator and renderer drift returns without immediate detection
- Live operator validation becomes the first place governance defects are discovered

**Prevention:**
- Define regression obligations for every new gate: fail path, resume path, final success path, and stale-artifact path
- Add artifact-level assertions, not just command exit assertions
- Update existing delivery pipeline tests to prove brownfield compatibility with refreshed workspaces and resume flows
- Treat sample approved-project fixtures with environment-path drift as a known hazard and normalize them before relying on them for governance tests

**Detection / Warning signs:**
- PRs add gate logic but no validator or artifact assertions
- Tests prove commands run, but not that authority/status/final-review artifacts agree
- Failures only appear on real operator machines or resumed runs

**Later roadmap phases that should absorb mitigation:**
- Phase: Delivery-governance regression matrix
- Phase: Fixture normalization for approved-project samples
- Phase: Live-UAT parity coverage for governance gates

## Moderate Pitfalls

### Pitfall 7: Smuggling new scope through specialist evidence requirements
**What goes wrong:**
A gate that asks for stronger design or specialist evidence becomes a backdoor for adding new product requirements to an already approved run.

**Prevention:**
- Keep default delivery scope as `approved-brief-only`
- Require explicit reopen/governance flow for scope expansion
- Distinguish missing evidence for approved scope from requests for net-new capability

**Warning signs:**
- Handoff comments introduce new pages, new integrations, or new monetization logic under “needed for validation”
- Design review keeps expanding the product brief instead of validating it

**Later roadmap phases that should absorb mitigation:**
- Phase: Scope discipline and reopen policy hardening

### Pitfall 8: Using environment-specific evidence paths in new governance checks
**What goes wrong:**
New validators or handoff links depend on operator-machine-specific absolute paths or legacy sample artifact layouts.

**Prevention:**
- Normalize evidence addressing around approved-project-relative or workspace-relative references
- Keep operator-visible files readable while machine-local paths remain derivable, not canonical
- Explicitly test legacy sample bundles for path drift handling

**Warning signs:**
- Validation passes only on one machine
- Checked-in examples contain broken links after workspace refresh or repo move

**Later roadmap phases that should absorb mitigation:**
- Phase: Artifact path normalization
- Phase: Legacy sample compatibility cleanup

### Pitfall 9: Duplicating conformance, governance, and release-readiness rules in three places
**What goes wrong:**
The same requirement is hand-coded separately in template conformance, stage handoff checks, and final validation, and then drifts.

**Prevention:**
- Define one rule source with stage-specific projections
- Reuse shared validators or rule registries where possible
- Make final validation consume the same core rule outcomes already used earlier in the pipeline

**Warning signs:**
- Design gate passes, release gate fails, and both claim to evaluate the same requirement
- Updating one rule requires touching several unrelated scripts and markdown renderers

**Later roadmap phases that should absorb mitigation:**
- Phase: Shared governance rule registry
- Phase: Validator deduplication/refactor

## Minor Pitfalls

### Pitfall 10: Making evidence requirements too opaque for the solo operator
**What goes wrong:**
Governance becomes stricter, but status artifacts do not explain exactly which evidence is missing, where it belongs, and which phase owns the fix.

**Prevention:**
- Render missing-evidence requirements directly in `DELIVERY_PIPELINE_STATUS.md`
- Name the owning stage, expected artifact, and resume command

**Warning signs:**
- The operator must inspect raw logs or source code to understand a block

**Later roadmap phases that should absorb mitigation:**
- Phase: Operator-facing governance diagnostics

## Phase-Specific Warnings

| Later roadmap phase topic | Likely pitfall | Mitigation |
|---|---|---|
| Governance state model | New gates update one artifact surface but not all others | Introduce canonical gate-state schema consumed by renderers, validators, and resume logic |
| Handoff contract enforcement | Markdown handoffs exist but remain semantically weak | Add structured sections and fail downstream stages on missing contract fields |
| Design-artifact validation | Design docs become ceremonial and detached from shipped UI | Wire design evidence into conformance and release-readiness checks |
| Resume/recovery | Governance blocks are not resumable | Persist block reasons/evidence and test resume on partial-progress workspaces |
| Authority bundle evolution | New approvals live only in local workspace files | Persist governance decisions in approved-project authority records or linked authority indexes |
| Regression expansion | New governance features land without regression coverage | Add artifact assertions for fail, resume, and final-success paths |
| Fixture/path hygiene | Tests depend on environment-specific sample paths | Normalize fixture references and verify sample bundles survive repo/workspace relocation |

## Sources

- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/PROJECT.md`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/CHANGELOG.md`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/docs/OPERATIONS.md`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/docs/platform/standalone-saas-template-contract.md`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/STATE.md`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/assets/workspaces/ceo/AGENTS.md`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/README.md`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/docs/skill-governance/README.md`
