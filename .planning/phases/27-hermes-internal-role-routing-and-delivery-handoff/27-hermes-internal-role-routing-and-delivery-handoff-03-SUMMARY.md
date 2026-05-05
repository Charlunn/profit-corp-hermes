# Phase 27-03 Summary

- Updated `scripts/render_chat_run_status.py` so Hermes owner-facing status can summarize internal workstreams and routing artifacts from durable role-routing truth.
- Healthy-path messages now explain what Hermes is doing in business terms, while blocked states can name the responsible internal role and artifact without turning roles into operator controls.
- Added role-progress and blocked-owner assertions in `tests/test_chat_run_bootstrap.py`.

Verification:
- `python -m unittest tests.test_chat_run_bootstrap`
