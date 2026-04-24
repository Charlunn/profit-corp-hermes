# Codebase Concerns

**Analysis Date:** 2026-04-24

## Tech Debt

**Bootstrap duplication across shells:**
- Issue: `scripts/bootstrap_hermes.sh` and `scripts/bootstrap_hermes.ps1` implement similar provisioning flows separately
- Why: cross-platform support was added with parallel native scripts
- Impact: behavior can drift between Unix and Windows setup paths
- Fix approach: keep a shared checklist/spec section in docs or extract common invariant checks into one authoritative contract document tied to both scripts

**Command wrapper parsing depends on shell text output:**
- Issue: `orchestration/cron/commands.sh` parses `hermes -p ceo cron list` output using `grep`, `awk`, and name matching
- Why: Hermes CLI is treated as the only integration surface
- Impact: formatting changes in Hermes CLI output could break duplicate detection, pause/resume, or run targeting
- Fix approach: switch to a stable machine-readable Hermes output mode if available, or add stricter parsing tests around the wrapper

## Known Bugs

**No explicit bugs documented in repo artifacts:**
- Symptoms: none confirmed from surveyed files
- Trigger: unknown
- Workaround: use `scripts/smoke_test_pipeline.sh` and `scripts/recover_cron.sh` for detection/recovery
- Root cause: current codebase map is based on static inspection rather than issue history

## Security Considerations

**Remote installer pipe-to-shell:**
- Risk: `scripts/bootstrap_hermes.sh:76-78` downloads and pipes a remote installer directly into `bash`
- Current mitigation: HTTPS + official GitHub raw URL only
- Recommendations: pin installer version/checksum or document trust assumptions more explicitly in ops docs

**Shared state integrity depends on process discipline:**
- Risk: `assets/shared/LEDGER.json` can theoretically be edited manually despite policy forbidding it
- Current mitigation: `docs/STATE_CONTRACT.md` plus `assets/shared/manage_finance.py` locking and explicit write-path rules
- Recommendations: add automated guard checks or CI/pre-commit validation to detect unauthorized ledger edits

**Approval gates are policy-based, not hard-enforced in code:**
- Risk: `/revenue`, `/bounty`, and archive rules described in `docs/STATE_CONTRACT.md` may be bypassed by ad-hoc manual actions
- Current mitigation: skill instructions and operator process
- Recommendations: encode gate checks closer to the execution path where possible

## Performance Bottlenecks

**Cron status operations scale linearly with shell parsing:**
- Problem: repeated `cron list` scans in `orchestration/cron/commands.sh` re-run CLI commands and parse output each time
- Measurement: no timings recorded
- Cause: simplicity-first wrapper design
- Improvement path: cache command output within one invocation or use structured API output if Hermes supports it

## Fragile Areas

**Finance state mutation path:**
- Why fragile: `assets/shared/manage_finance.py` is the sole sanctioned writer for `assets/shared/LEDGER.json`; bypassing it breaks invariants and auditability
- Common failures: manual JSON edits, partial lock handling differences between Unix and Windows fallback mode
- Safe modification: change ledger schema and mutation rules together; verify with `python3 -m py_compile assets/shared/manage_finance.py` and smoke checks
- Test coverage: no dedicated automated rule-level tests detected

**Cron wrapper job identification:**
- Why fragile: named-job matching in `orchestration/cron/commands.sh` assumes stable human-readable output and exact names (`ProfitCorp Daily Pipeline`, `ProfitCorp Health Check`)
- Common failures: duplicate job naming collisions, CLI output drift, manual job tampering
- Safe modification: keep names stable, test `list`, `ensure`, `resume-all`, and `recreate` flows after any change
- Test coverage: only lightweight smoke coverage

**Profile sync workflow:**
- Why fragile: bootstrap writes into `~/.hermes/` and conditionally overwrites existing profile config/skills based on prompts
- Common failures: accidental overwrite refusal, platform-specific drift, partial sync state after interrupted bootstrap
- Safe modification: preserve the explicit prompt/overwrite flow and re-run smoke tests after changes
- Test coverage: manual/integration-oriented only

## Scaling Limits

**Operator-managed single workspace:**
- Current capacity: suitable for one repo-backed Hermes workspace with five persistent roles
- Limit: no evidence of support for many environments, tenants, or high-frequency automated workflows
- Symptoms at limit: config drift, cron duplication, larger shared artifact coordination overhead
- Scaling path: introduce more structured automation, stronger validation, and possibly machine-readable control surfaces

## Dependencies at Risk

**Hermes CLI contract:**
- Risk: core automation assumes Hermes commands and subcommands remain stable
- Impact: bootstrap, smoke tests, cron orchestration, and profile sync all degrade if CLI behavior changes
- Migration plan: isolate Hermes assumptions in docs and wrappers; add version compatibility checks if repo begins pinning supported versions

## Missing Critical Features

**Automated enforcement of governance rules:**
- Problem: many invariants live in markdown contracts only
- Current workaround: human review and skill discipline
- Blocks: stronger confidence in unattended or larger-scale operation
- Implementation complexity: medium

**Dedicated regression tests for finance logic:**
- Problem: `assets/shared/manage_finance.py` has meaningful business rules but no direct tests
- Current workaround: syntax compile and manual usage
- Blocks: safe refactors of revenue/bounty/scoring logic
- Implementation complexity: low to medium

## Test Coverage Gaps

**Bootstrap behavior across platforms:**
- What's not tested: parity between `scripts/bootstrap_hermes.sh` and `scripts/bootstrap_hermes.ps1`
- Risk: one platform path diverges silently
- Priority: High
- Difficulty to test: requires cross-platform CI or documented manual verification matrix

**Cron duplicate-handling logic:**
- What's not tested: edge cases in `orchestration/cron/commands.sh` when CLI output changes or duplicate jobs exist
- Risk: scheduler drift or accidental wrong-job manipulation
- Priority: High
- Difficulty to test: depends on controllable Hermes cron fixtures or mockable command output

**Ledger mutation invariants:**
- What's not tested: distribution math, lock behavior, and milestone transitions inside `assets/shared/manage_finance.py`
- Risk: silent state corruption or incorrect treasury/points calculations
- Priority: High
- Difficulty to test: moderate; requires adding Python-level tests and fixture ledgers

---

*Concerns audit: 2026-04-24*
*Update as issues are fixed or new ones discovered*
