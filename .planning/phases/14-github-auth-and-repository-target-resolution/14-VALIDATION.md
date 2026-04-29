# Phase 14 Validation

**Verdict:** PASS

## Why this plan passes

The plan is tightly scoped to the Phase 14 goal: GitHub auth detection and repository targeting before downstream sync/deploy reliability work. It does not drag in Phase 15 snapshot/path/transport repairs or Phase 16 Vercel auth work except where those later phases are referenced as out-of-scope boundaries.

### Requirement coverage
- **GHAUTH-01** — Covered by Task 1 red tests plus Task 2 implementation/verification for authenticated `gh` CLI sessions without exported token env.
- **GHAUTH-02** — Covered by Task 1 and Task 2 preserving explicit `GH_TOKEN` / `GITHUB_TOKEN` behavior as the first auth path.
- **GHOWN-01** — Covered by Task 1 and Task 3 with explicit assertions that owner must not fall back to `project_slug`.
- **GHOWN-02** — Covered by Task 3 with controller-side canonical owner/name/url derivation and persistence for create and attach flows.

### Fresh vs resume coverage
The plan explicitly separates these cases:
- fresh-run coverage in `tests/test_project_delivery_pipeline_bootstrap.py`
- resume-run coverage in `tests/test_project_delivery_pipeline_resume.py`

That is the right split for this repo’s authority-first pipeline and is necessary to prevent retries from reintroducing bad defaults.

### Evidence / authority validation
The plan requires visible changes in:
- `shipping.github.repository_mode`
- `shipping.github.repository_owner`
- `shipping.github.repository_name`
- `shipping.github.repository_url`
- helper evidence/auth-source details

That is enough to make the Phase 14 outcome operator-visible and testable without prematurely solving later status-render convergence work.

## What the plan gets right structurally

1. **Correct layer split**
   - helper layer handles auth-source resolution
   - controller layer handles owner/name/url policy

2. **Uses existing repo patterns**
   - blocked-result shape
   - authority-first metadata persistence
   - existing Phase 11 helper/controller tests

3. **Good sequencing**
   - red tests first
   - helper auth fix second
   - controller identity fix third

4. **Good boundary control**
   - explicitly forbids owner fallback to `project_slug`
   - does not drift into sync/path/SSH or Vercel fixes

## Minor watchouts during execution

These are execution notes, not plan blockers:
- If helper evidence adds new auth-source fields, the implementation should keep them optional enough not to break older fixtures unnecessarily.
- If authenticated CLI probing uses `gh auth status`, prefer a machine-readable/parseable command path so tests don’t become brittle around human-readable CLI output.

## Final assessment

The plan is executable, phase-scoped, and sufficiently verified for Phase 14. It should produce a clean fix for the two live failures that prevented GitHub repository preparation from starting correctly.
