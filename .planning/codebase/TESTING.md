# Testing Patterns

**Analysis Date:** 2026-04-24

## Test Framework

**Runner:**
- No dedicated unit-test framework detected
- Validation is script-based, centered on `scripts/smoke_test_pipeline.sh`

**Assertion Library:**
- None beyond shell exit codes and pass/fail helpers
- Python syntax verification uses `python3 -m py_compile`

**Run Commands:**
```bash
bash scripts/smoke_test_pipeline.sh              # Run repository smoke checks
python3 -m py_compile assets/shared/manage_finance.py  # Validate finance script syntax
bash orchestration/cron/commands.sh list         # Sanity-check cron CLI wiring
hermes -p ceo cron list                          # Verify Hermes runtime visibility
```

## Test File Organization

**Location:**
- No `tests/` directory detected
- Validation logic lives in operational scripts under `scripts/`

**Naming:**
- Smoke and recovery flows are named by operational purpose (`smoke_test_pipeline.sh`, `recover_cron.sh`)
- No `*.test.*` naming convention currently used

**Structure:**
```text
scripts/
  bootstrap_hermes.sh
  bootstrap_hermes.ps1
  bootstrap_hermes_noninteractive.sh
  smoke_test_pipeline.sh
  recover_cron.sh
```

## Test Structure

**Suite Organization:**
```bash
require_cmd hermes
resolve_python
check_file_nonempty "$ROOT_DIR/assets/shared/LEDGER.json"
run_check "finance script syntax" "$PYTHON_BIN" -m py_compile "$ROOT_DIR/assets/shared/manage_finance.py"
run_check "ceo cron list command" hermes -p ceo cron list
```

**Patterns:**
- Tests are imperative smoke checks rather than isolated units
- Helpers like `require_cmd`, `check_file_nonempty`, and `run_check` centralize assertions
- Failures accumulate in a status variable (`FAILED`) so the script can report a summary at the end

## Mocking

**Framework:**
- No mocking framework detected

**Patterns:**
- Repository prefers real command availability and real file existence checks
- Validation exercises actual Hermes CLI commands where possible

**What to Mock:**
- No documented mocking strategy exists today

**What NOT to Mock:**
- Critical operator dependencies (`hermes`, `bash`, `python`) are checked directly in smoke tests
- Shared-state file presence is verified against real repository files

## Fixtures and Factories

**Test Data:**
- Real repository files serve as fixtures (`assets/shared/LEDGER.json`, cron prompt files, profile templates)
- No separate fixture library detected

**Location:**
- Inline in scripts via concrete file paths

## Coverage

**Requirements:**
- No coverage target or enforcement mechanism detected
- Current emphasis is “is the workspace operable?” rather than code coverage percentages

**Configuration:**
- None observed

**View Coverage:**
```bash
# Not available; use smoke script output instead
bash scripts/smoke_test_pipeline.sh
```

## Test Types

**Unit Tests:**
- None detected

**Integration Tests:**
- Smoke checks function as lightweight integration tests across CLI, files, and scripts
- Example: `scripts/smoke_test_pipeline.sh` validates Hermes CLI wiring, cron command access, and Python syntax in one run

**E2E Tests:**
- No browser/API E2E suite detected
- Cron operations can be manually exercised through `orchestration/cron/commands.sh run-daily`

## Common Patterns

**Async Testing:**
- Not applicable in current test strategy

**Error Testing:**
- Indirectly covered by command exit codes and explicit `FAIL` reporting in smoke script helpers

**Snapshot Testing:**
- Not used

## Gaps and Implications

- There are no isolated tests for `assets/shared/manage_finance.py` business rules
- Cron wrapper behavior in `orchestration/cron/commands.sh` is only lightly validated by runtime command execution
- Bootstrap flows are largely manual/integration tested rather than deterministically unit tested
- If this repo grows executable logic, adding a proper script-level or Python test suite would reduce regression risk

---

*Testing analysis: 2026-04-24*
*Update when test patterns change*
