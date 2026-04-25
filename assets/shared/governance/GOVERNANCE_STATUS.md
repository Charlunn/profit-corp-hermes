# Governance Status
- **Authority Source**: `assets/shared/governance/governance_events.jsonl`
- **Decision Package Anchor**: `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`
- **Trace Anchor**: `assets/shared/trace/decision_package_trace.json`

This latest view is derived from the append-only governance JSONL stream.

## Pending Approvals
- `gov-20260425080047` - `finance.revenue` -> `assets/shared/LEDGER.json` - status: `pending` - decision: `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` - reason: Verify finance request after rule enforcement
- `gov-bootstrap-20260425` - `governance.bootstrap` -> `assets/shared/governance/GOVERNANCE_STATUS.md` - status: `pending` - decision: `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` - reason: Initialize dedicated governance event stream and latest status view for Phase 4.

## Active Blocks
- `gov-20260425075411` - `finance.revenue` -> `assets/shared/LEDGER.json` - status: `blocked` - decision: `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` - reason: Governed action blocked because current approval status is pending.

## Recent Approvals
- None

## Recent Rejections
- None

## Recent Overrides
- `gov-20260425075517` - `fallback.takeover.tech_spec` -> `assets/shared/TECH_SPEC.md` - status: `override` - decision: `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` - reason: CEO override fallback takeover verification
