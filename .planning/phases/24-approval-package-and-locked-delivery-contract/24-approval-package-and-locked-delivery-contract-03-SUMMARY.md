# Phase 24-03 Summary

- Expanded governed reopen coverage to locked contract drift, not just protected paths and broad scope expansion.
- Added `request_contract_drift_reopen(...)` in `scripts/request_scope_reopen.py` to record field-specific drift for approved contract values such as `monetization` and `required_languages`.
- Updated `scripts/render_approved_delivery_status.py` to render a dedicated `Locked Contract Drift` section with exact field, approved value, proposed value, evidence, and governance action.
- Added regression coverage in `tests/test_scope_reopen_flow.py` and `tests/test_delivery_orchestration_contract.py`.

Verification:
- `pytest tests/test_scope_reopen_flow.py tests/test_delivery_orchestration_contract.py -q`
