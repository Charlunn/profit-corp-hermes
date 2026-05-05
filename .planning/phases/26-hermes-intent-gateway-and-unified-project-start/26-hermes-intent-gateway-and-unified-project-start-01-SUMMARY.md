# Phase 26-01 Summary

- Extended `scripts/chat_intake_common.py` so Hermes-native project-start payloads normalize into the same canonical governed run envelope used by the existing chat transports.
- Preserved one authoritative run identity by reusing the existing origin-key and run-id derivation instead of introducing Hermes-only identifiers.
- Added regression coverage in `tests/test_chat_intake_contract.py` and `tests/test_chat_origin_contract.py` for Hermes request normalization, required provenance, and stable reread semantics.

Verification:
- `python -m unittest tests.test_chat_intake_contract tests.test_chat_origin_contract`
