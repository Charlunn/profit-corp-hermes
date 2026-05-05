# Phase 26-02 Summary

- Refactored `scripts/start_chat_project_run.py` so run creation flows through a shared `_bootstrap_envelope(...)` path and added `bootstrap_hermes_project_run(...)` as the Hermes-first startup adapter.
- Kept Hermes startup replay-safe and authority-first by reusing the existing governed bootstrap record, events, dispatch, and blocked-state lifecycle.
- Expanded `tests/test_chat_run_bootstrap.py` to cover Hermes bootstrap reuse, duplicate-request replay, and fail-closed handling for missing required start metadata.

Verification:
- `python -m unittest tests.test_chat_run_bootstrap`
