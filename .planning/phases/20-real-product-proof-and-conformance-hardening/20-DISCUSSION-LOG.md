# Phase 20: Real Product Proof and Conformance Hardening - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md; this log preserves the auto-selected alternatives.

**Date:** 2026-05-04
**Phase:** 20-real-product-proof-and-conformance-hardening
**Mode:** auto
**Areas discussed:** Product proof source of truth, Demo and template residue policy, Gate layering between conformance and final validation, Operator-facing proof visibility

---

## Product proof source of truth

| Option | Description | Selected |
|--------|-------------|----------|
| Reuse the existing product-proof contract | Keep one shared proof vocabulary and harden it centrally across validators/renderers | Yes |
| Rebuild proof rules separately in each validator | Faster local changes, but invites governance drift | |
| Add a brand-new proof service layer | Heavyweight for this milestone and breaks existing artifact-first patterns | |

**Auto choice:** Reuse the existing product-proof contract.
**Notes:** Recommended because `scripts/product_proof_contract.py`, `start_approved_project_delivery.py`, `render_approved_delivery_status.py`, and `validate_approved_delivery_pipeline.py` already share proof fields.

---

## Demo and template residue policy

| Option | Description | Selected |
|--------|-------------|----------|
| Fail closed on `/demo` proof and block primary-surface template residue | Removes the known loophole while preserving secondary-surface warnings | Yes |
| Allow `/demo` as fallback proof when other work is thin | Keeps the loophole open | |
| Treat all residue only as warnings | Too weak for the milestone goal | |

**Auto choice:** Fail closed on `/demo` proof and block primary-surface template residue.
**Notes:** Recommended because milestone risk framing explicitly calls out `/demo` replacement shortcuts and template-shaped output passing as delivery.

---

## Gate layering between conformance and final validation

| Option | Description | Selected |
|--------|-------------|----------|
| Keep conformance as the early baseline gate and final validation as the explicit proof explainer | Matches current repo layering and minimizes architectural churn | Yes |
| Move all proof responsibility into conformance only | Weakens operator-facing end-state explanation | |
| Move all proof responsibility into final validation only | Lets thin work flow too far downstream before failing | |

**Auto choice:** Keep conformance as the early baseline gate and final validation as the explicit proof explainer.
**Notes:** Recommended because the repo already separates early blocking checks from late cross-surface validation.

---

## Operator-facing proof visibility

| Option | Description | Selected |
|--------|-------------|----------|
| Render proof verdict, proof paths, exclusions, residue, and failure reasons explicitly on status/review surfaces | Gives operators concrete reasons for pass/fail decisions | Yes |
| Show only a pass/fail badge | Too thin for governance review and resume | |
| Leave proof details buried in specialist artifacts | Makes operator surfaces ceremonial instead of authoritative | |

**Auto choice:** Render proof verdict, proof paths, exclusions, residue, and failure reasons explicitly on status/review surfaces.
**Notes:** Recommended because `PROOF-03` requires final validation and operator review to explain what proved real SaaS delivery.

---

## the agent's Discretion

- Exact persistence path for additional proof snapshots
- Exact wording/order of the rendered proof sections
- Exact breadth of excluded-proof constants beyond the already-established `/demo` and identity-only seams

## Deferred Ideas

- Secondary-surface residue escalation beyond warnings can be reconsidered later after primary-surface blocking stabilizes.
- Resume-path proof regression closure remains Phase 21 work.
