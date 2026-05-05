---
phase: 20
slug: real-product-proof-and-conformance-hardening
status: complete
nyquist_compliant: true
wave_0_complete: true
created: 2026-05-04
updated: 2026-05-04
---

# Phase 20 - Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 8.4.2 running unittest-style tests |
| **Config file** | none |
| **Quick run command** | `pytest tests/test_approved_delivery_pipeline_cli.py::ApprovedDeliveryPipelineCliTests::test_rendered_product_proof_explains_exact_surfaces_and_exclusions -q` |
| **Full suite command** | `pytest tests/test_approved_delivery_pipeline_cli.py tests/test_project_delivery_pipeline_bootstrap.py tests/test_project_delivery_pipeline_resume.py -q` |
| **Estimated runtime** | ~20 seconds |

---

## Sampling Rate

- **After every task commit:** Run `pytest tests/test_approved_delivery_pipeline_cli.py::ApprovedDeliveryPipelineCliTests::test_rendered_product_proof_explains_exact_surfaces_and_exclusions -q`
- **After every plan wave:** Run `pytest tests/test_project_delivery_pipeline_bootstrap.py tests/test_project_delivery_pipeline_resume.py -q`
- **Before `$gsd-verify-work`:** Full suite must be green
- **Max feedback latency:** 25 seconds

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 20-01-01 | 01 | 1 | PROOF-01 / PROOF-02 | T-20-01 / T-20-02 | Identity-only and `/demo`-only changes fail proof and remain excluded from acceptable proof paths | integration | `pytest tests/test_project_delivery_pipeline_bootstrap.py::ApprovedDeliveryBootstrapTests::test_product_proof_contract_requires_primary_surface_and_supporting_logic -q` | yes | green |
| 20-01-02 | 01 | 1 | PROOF-01 / PROOF-02 | T-20-03 / T-20-04 | Conformance and stage persistence consume the same canonical proof vocabulary, including residue blockers and warnings | integration | `pytest tests/test_project_delivery_pipeline_bootstrap.py::ApprovedDeliveryBootstrapTests::test_product_proof_contract_requires_primary_surface_and_supporting_logic tests/test_project_delivery_pipeline_resume.py::ApprovedDeliveryResumeTests::test_resume_persists_canonical_product_proof_payload_without_demo_or_identity_loopholes -q` | yes | green |
| 20-02-01 | 02 | 2 | PROOF-03 | T-20-05 / T-20-06 | Status and final review render exact workflow surfaces, supporting logic, exclusions, residue findings, and mapped failure reasons | integration | `pytest tests/test_approved_delivery_pipeline_cli.py::ApprovedDeliveryPipelineCliTests::test_rendered_product_proof_explains_exact_surfaces_and_exclusions -q` | yes | green |
| 20-02-02 | 02 | 2 | PROOF-01 / PROOF-02 / PROOF-03 | T-20-07 / T-20-08 | Validator rejects stale fixture or event payload truth that still treats `/demo` or identity-only paths as acceptable product proof | integration | `pytest tests/test_approved_delivery_pipeline_cli.py::ApprovedDeliveryPipelineCliTests::test_rendered_product_proof_explains_exact_surfaces_and_exclusions tests/test_project_delivery_pipeline_resume.py::ApprovedDeliveryResumeTests::test_resume_persists_canonical_product_proof_payload_without_demo_or_identity_loopholes -q` | yes | green |

*Status: pending / green / red / flaky*

---

## Wave 0 Requirements

- [x] `tests/test_project_delivery_pipeline_bootstrap.py` - Phase 20 proof-contract nodeids added for identity-only, `/demo`, and supporting-logic failures
- [x] `tests/test_project_delivery_pipeline_resume.py` - resume-safe proof-payload nodeids added to reject demo and identity loopholes
- [x] `tests/test_approved_delivery_pipeline_cli.py` - exact rendered-proof visibility nodeids added for status, final review, and validator enforcement

---

## Manual-Only Verifications

All phase behaviors have automated verification.

---

## Validation Sign-Off

- [x] All tasks have `<automated>` verify or Wave 0 dependencies
- [x] Sampling continuity: no 3 consecutive tasks without automated verify
- [x] Wave 0 covers all missing references
- [x] No watch-mode flags
- [x] Feedback latency < 25s
- [x] `nyquist_compliant: true` set in frontmatter

**Approval:** complete
