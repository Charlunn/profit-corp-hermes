# Phase 21: Bootstrap/Resume Governance Regressions - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md - this log preserves the alternatives considered.

**Date:** 2026-05-04
**Phase:** 21-bootstrap-resume-governance-regressions
**Areas discussed:** bootstrap and resume gate parity, blocked-state truth, regression coverage strategy, resume recovery behavior

---

## Bootstrap and Resume Gate Parity

| Option | Description | Selected |
|--------|-------------|----------|
| Shared gate contract | Fresh start and resume both execute the same evidence, UI artifact, and product-proof validators | Yes |
| Resume-light shortcut | Resume trusts most persisted artifacts and only checks the current stage superficially | |
| Hybrid exceptions | Some gates are shared, but resume gets special bypasses for older artifacts | |

**User's choice:** `[auto] Shared gate contract`
**Notes:** Auto mode selected the stricter governance path because Phase 21 is explicitly about locking hardened behavior into recovered runs without drift.

---

## Blocked-State Truth

| Option | Description | Selected |
|--------|-------------|----------|
| Canonical authority + resolved history | Persist one authoritative block reason/evidence path, then keep it as resolved history after recovery | Yes |
| Event-led truth | Let the latest event define current block state even if authority/rendered views lag | |
| Surface-local truth | Allow status markdown or final review to carry independent current-state semantics | |

**User's choice:** `[auto] Canonical authority + resolved history`
**Notes:** This carries forward the Phase 17 and Phase 18 truth-precedence decisions and keeps authority drift itself as a blocking error.

---

## Regression Coverage Strategy

| Option | Description | Selected |
|--------|-------------|----------|
| Expand existing fixture suites | Add Phase 21 coverage to the current bootstrap, resume, and validator unit tests | Yes |
| New standalone regression harness | Build a separate test driver outside the current approved-delivery suites | |
| Renderer-only checks | Focus mainly on status/final-review snapshots and keep runtime tests shallow | |

**User's choice:** `[auto] Expand existing fixture suites`
**Notes:** The current test files already model blocked, resumed, and finalized approved-delivery flows, so extending them is the lowest-drift path.

---

## Resume Recovery Behavior

| Option | Description | Selected |
|--------|-------------|----------|
| Recover in place when safe | Refresh managed surfaces, preserve legitimate workspace state, and no-op after completed handoff | Yes |
| Always rebuild from scratch | Recreate workspace/run state on every blocked resume to avoid stale artifacts | |
| Manual operator repair | Require hand edits to authority/event artifacts before resume can continue | |

**User's choice:** `[auto] Recover in place when safe`
**Notes:** This matches existing tests that preserve `.git`, refresh managed files, and prevent duplicate post-handoff replay while still failing closed on truth drift.

---

## the agent's Discretion

- Helper extraction and code organization for shared bootstrap/resume gate evaluation.
- Final naming of resolved-block metadata fields, as long as all surfaces consume the same source of truth.
- Exact test helper refactors used to keep the expanded regression matrix readable.

## Deferred Ideas

- New specialist roles or new delivery stages.
- Reopening GitHub/Vercel transport reliability work.
- Replacing the file-backed authority/event model with a new workflow system.
