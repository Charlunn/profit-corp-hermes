# Phase 28-03 Summary

- Tightened approved-project approval persistence in `scripts/start_approved_project_delivery.py` so conversational approvals keep proposal identity, chat reply linkage, and the same downstream locked-contract prerequisites the shipped pipeline already trusts.
- Verified that scope or contract drift still reuses the governed reopen path rather than degrading into a conversation-only exception.
- Reused the existing reopen coverage in `tests/test_scope_reopen_flow.py` alongside the updated chat approval tests to confirm the Hermes surface does not weaken post-approval governance.

Verification:
- `pytest tests/test_scope_reopen_flow.py -q`
- `python -m unittest tests.test_chat_approval_flow`
