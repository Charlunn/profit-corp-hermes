# Phase 28-02 Summary

- Added shared Hermes reply-resolution helpers in `scripts/request_governance_approval.py` for explicit approve/reject parsing, strict linkage checks, and deterministic idempotency keys.
- Routed `scripts/start_approved_project_delivery.py` chat approval persistence through that shared adapter so conversational approve/reject still lands in the existing governed event model.
- Extended `tests/test_chat_approval_flow.py` to cover the reusable reply adapter in addition to the persisted approved-project approval flow.

Verification:
- `python -m unittest tests.test_chat_approval_flow`
