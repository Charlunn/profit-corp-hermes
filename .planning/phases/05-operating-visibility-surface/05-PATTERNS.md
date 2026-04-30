# Phase 5: Operating Visibility Surface - Pattern Map

**Mapped:** 2026-04-25
**Files analyzed:** 8
**Analogs found:** 8 / 8

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `assets/shared/visibility/OPERATING_VISIBILITY.md` | config | transform | `assets/shared/governance/GOVERNANCE_STATUS.md` | flow-match |
| `assets/shared/visibility/history/YYYY-MM-DD-operating-visibility.md` | config | transform | `assets/shared/execution_packages/history/2026-04-25-execution-package.md` | exact |
| `scripts/generate_operating_visibility.py` | service | transform | `scripts/derive_execution_package.py` | exact |
| `scripts/generate_operating_visibility.py` | service | request-response | `scripts/render_governance_status.py` | role-match |
| `scripts/generate_operating_visibility.py` | service | file-I/O | `scripts/generate_decision_package.py` | role-match |
| `tests/test_generate_operating_visibility.py` | test | transform | `tests/test_derived_packages.py` | exact |
| `scripts/smoke_test_pipeline.sh` | test | batch | `scripts/smoke_test_pipeline.sh` | exact |
| `orchestration/cron/commands.sh` | config | batch | `orchestration/cron/commands.sh` | exact |
| `orchestration/cron/daily_pipeline.prompt.md` | config | batch | `orchestration/cron/daily_pipeline.prompt.md` | exact |
| `docs/OPERATIONS.md` | config | request-response | `docs/OPERATIONS.md` | role-match |

## Pattern Assignments

### `scripts/generate_operating_visibility.py` (service, transform / file-I/O)

**Primary analog:** `scripts/derive_execution_package.py`
**Supporting analogs:** `scripts/derive_board_briefing.py`, `scripts/render_governance_status.py`, `scripts/generate_decision_package.py`

**Imports + root/path conventions** (`scripts/derive_execution_package.py:1-21`):
```python
#!/usr/bin/env python3
import argparse
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
SHARED_DIR = ROOT_DIR / "assets" / "shared"
DECISION_PACKAGES_DIR = SHARED_DIR / "decision_packages"
EXECUTION_PACKAGES_DIR = SHARED_DIR / "execution_packages"
EXECUTION_HISTORY_DIR = EXECUTION_PACKAGES_DIR / "history"
TRACE_DIR = SHARED_DIR / "trace"
OPERATING_DECISION_PACKAGE_PATH = DECISION_PACKAGES_DIR / "OPERATING_DECISION_PACKAGE.md"
DECISION_TRACE_PATH = TRACE_DIR / "decision_package_trace.json"
```
Reuse this shape for `VISIBILITY_DIR`, `VISIBILITY_HISTORY_DIR`, and trusted source paths.

**Allowed write directory guard** (`scripts/derive_execution_package.py:39-57`):
```python
def ensure_dirs() -> None:
    EXECUTION_PACKAGES_DIR.mkdir(parents=True, exist_ok=True)
    EXECUTION_HISTORY_DIR.mkdir(parents=True, exist_ok=True)


def ensure_allowed_write_path(path: Path) -> None:
    resolved = path.resolve()
    for directory in ALLOWED_WRITE_DIRS:
        try:
            resolved.relative_to(directory.resolve())
            return
        except ValueError:
            continue
    raise ExecutionPackageError(f"refusing to write outside allowed directories: {path}")


def write_output(path: Path, content: str) -> None:
    ensure_allowed_write_path(path)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
```
Phase 5 generator should copy this exactly for visibility latest/history writes.

**Read-only trusted artifact loading** (`scripts/derive_execution_package.py:60-66`):
```python
def load_text(path: Path, label: str) -> str:
    if not path.exists():
        raise ExecutionPackageError(f"{label} not found: {path}")
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise ExecutionPackageError(f"{label} is empty: {path}")
    return content
```
Use this same pattern for operating package, governance status, latest summary, optional derived supporting views, and trace sidecar.

**Header / derived-from / source-trace pattern** (`scripts/derive_board_briefing.py:156-169`):
```python
return (
    f"# Board Briefing - {date_value}\n"
    f"- **Derived From**: `{relative(OPERATING_DECISION_PACKAGE_PATH)}`\n"
    f"- **Source Trace**: `{relative(DECISION_TRACE_PATH)}`\n"
    f"- **Conclusion**: {conclusion}\n\n"
```
Visibility artifact should keep this exact header idiom, but expand it with explicit source hierarchy lines for governance and freshness overlays.

**Latest + history twin write pattern** (`scripts/derive_execution_package.py:184-204`):
```python
latest_output = render_execution_package(date_value, operating_package, trace_content)
history_path = history_output_path(date_value)
if args.dry_run:
    print("=== EXECUTION_PACKAGE.md ===")
    print(latest_output)
    print(f"=== history/{history_path.name} ===")
    print(latest_output)
    return 0
ensure_dirs()
write_output(EXECUTION_PACKAGE_PATH, latest_output)
write_output(history_path, latest_output)
print(f"Wrote {relative(EXECUTION_PACKAGE_PATH)}")
print(f"Wrote {relative(history_path)}")
```
This is the closest analog for latest markdown artifact generation plus dated snapshot writing.

**Simple CLI entrypoint and dry-run flow** (`scripts/render_governance_status.py:19-39`):
```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Render the governance latest status view from governance_events.jsonl.")
    parser.add_argument("--dry-run", action="store_true", help="Render markdown to stdout without writing files.")
    return parser.parse_args()

...
if args.dry_run:
    print(markdown, end="")
    return 0
write_text(GOVERNANCE_STATUS_PATH, markdown)
print(f"Wrote {GOVERNANCE_STATUS_PATH}")
```
Use this exact minimal CLI style for the Phase 5 generator.

**Input validation / source contract checks** (`scripts/derive_execution_package.py:73-87`):
```python
def require_section(content: str, heading: str) -> None:
    if heading not in content:
        raise ExecutionPackageError(f"operating package missing required section: {heading}")


def require_source_reference(content: str) -> None:
    if relative(OPERATING_DECISION_PACKAGE_PATH) not in content and "CEO_RANKING.md" not in content:
        raise ExecutionPackageError("operating package missing source references")


def assert_derived_only_inputs() -> None:
    if OPERATING_DECISION_PACKAGE_PATH.name != "OPERATING_DECISION_PACKAGE.md":
        raise ExecutionPackageError("unexpected operating decision package path")
    if DECISION_TRACE_PATH.name != "decision_package_trace.json":
        raise ExecutionPackageError("unexpected decision trace path")
```
Phase 5 should add equivalent checks for exact source filenames and expected headings in source markdowns.

**Trace/evidence binding pattern** (`scripts/generate_decision_package.py:345-360`):
```python
## 推荐下一步
- 围绕 IDEA-001 组织 3-5 个目标用户验证访谈 — evidence: ... — trace: `judgment_id=action-idea-001-interviews`

## 证据回链
- prioritized shortlist: `assets/shared/external_intelligence/triage/prioritized_signals.json`
- role outputs: `assets/shared/PAIN_POINTS.md`, `assets/shared/MARKET_PLAN.md`, `assets/shared/TECH_SPEC.md`
- CEO synthesis: `assets/shared/CEO_RANKING.md`
- trace sidecar: `assets/shared/trace/decision_package_trace.json`
```
Copy this evidence-backlink style for Top 3 actions in visibility output.

**Freshness metadata extraction analog** (`assets/shared/external_intelligence/LATEST_SUMMARY.md:2-9`):
```markdown
## Run Metadata
- **run_id**: run-20260425T080119Z
- **started_at**: 2026-04-25T08:01:19Z
- **completed_at**: 2026-04-25T08:01:23Z
- **new_signal_count**: 6
- **duplicate_signal_count**: 4
- **failed_source_count**: 0
- **failed_sources**: none
```
Generator should parse these labeled bullets rather than raw intelligence sources.

**Governance exception overlay analog** (`assets/shared/governance/GOVERNANCE_STATUS.md:7-21`):
```markdown
## Pending Approvals
- `gov-20260425080047` - `finance.revenue` -> `assets/shared/LEDGER.json` - status: `pending` ...

## Active Blocks
- `gov-20260425075411` - `finance.revenue` -> `assets/shared/LEDGER.json` - status: `blocked` ...
```
Use this exact latest-view grouping as the machine-checkable source for pending/blocked overlay sections.

---

### `assets/shared/visibility/OPERATING_VISIBILITY.md` (config, transform)

**Primary analog:** `assets/shared/board_briefings/BOARD_BRIEFING.md`
**Supporting analogs:** `assets/shared/execution_packages/EXECUTION_PACKAGE.md`, `assets/shared/governance/GOVERNANCE_STATUS.md`, `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`

**Compact latest-view layout** (`assets/shared/board_briefings/BOARD_BRIEFING.md:0-17`):
```markdown
# Board Briefing - 2026-04-25
- **Derived From**: `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`
- **Source Trace**: `assets/shared/trace/decision_package_trace.json`
- **Conclusion**: ...

## Top 3
...

## Major Risk
...

## Required Attention
...
```
Best analog for a short operator-facing surface.

**Operator workflow framing** (`assets/shared/execution_packages/EXECUTION_PACKAGE.md:0-15`):
```markdown
# Execution Package - 2026-04-25
- **Derived From**: `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`
- **Source Trace**: `assets/shared/trace/decision_package_trace.json`
- **Goal**: ...
- **Target User**: Developers and technical operators
- **MVP Framing**: ...
- **Key Risks**: ...
- **Recommended Near-Term Actions**:
```
Reuse the bullet-heavy summary style for fast scan readability.

**Authority/source header pattern** (`assets/shared/governance/GOVERNANCE_STATUS.md:0-5`):
```markdown
# Governance Status
- **Authority Source**: `assets/shared/governance/governance_events.jsonl`
- **Decision Package Anchor**: `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`
- **Trace Anchor**: `assets/shared/trace/decision_package_trace.json`
```
Visibility should use the same top-of-file provenance pattern, adding governance/freshness/supporting-view lines.

**Primary anchor content to reuse** (`assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md:6-20`):
```markdown
## Overall Conclusion / 一句话总判断
...

## Top 3 Ranked Opportunities
...

## Operating Framing
- **Goal**: ...
- **Target User**: ...
- **MVP Framing**: ...
```
Visibility summary should derive conclusion/current state/opportunity framing from here first.

**Top 3 action cap source** (`assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md:58-66`):
```markdown
## 推荐下一步
- ... — trace: `judgment_id=action-idea-001-interviews`
- ... — trace: `judgment_id=action-idea-001-prototype`

## 证据回链
- ...
```
Closest analog for the operator Top 3 Next Actions block with trace references.

---

### `assets/shared/visibility/history/YYYY-MM-DD-operating-visibility.md` (config, transform)

**Analog:** `assets/shared/execution_packages/history/2026-04-25-execution-package.md`

**History naming/writing pattern** (`scripts/derive_execution_package.py:144-145`):
```python
def history_output_path(date_value: str) -> Path:
    return EXECUTION_HISTORY_DIR / EXECUTION_HISTORY_TEMPLATE.format(date=date_value)
```
Copy this exact templated history path style with `"{date}-operating-visibility.md"`.

**Same content for latest and dated snapshot** (`scripts/derive_board_briefing.py:179-189`):
```python
latest_output = render_board_briefing(date_value, operating_package, trace_content)
history_path = history_output_path(date_value)
...
write_output(BOARD_BRIEFING_PATH, latest_output)
write_output(history_path, latest_output)
```
Planner should assume identical content written to latest and history files.

---

### `tests/test_generate_operating_visibility.py` (test, transform)

**Primary analog:** `tests/test_derived_packages.py`
**Supporting analog:** `tests/test_generate_decision_package.py`

**Subprocess test harness** (`tests/test_derived_packages.py:15-22`):
```python
class DerivedPackagesTests(unittest.TestCase):
    def run_script(self, script: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *args],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )
```
Use this exact harness for generator dry-run/write-mode tests.

**Dry-run content assertions** (`tests/test_derived_packages.py:24-45`):
```python
result = self.run_script(BOARD_SCRIPT, "--dry-run")
self.assertEqual(result.returncode, 0, msg=result.stderr)
self.assertIn("Top 3", result.stdout)
self.assertIn("Major Risk", result.stdout)
self.assertIn("Required Attention", result.stdout)
self.assertIn("OPERATING_DECISION_PACKAGE.md", result.stdout)
self.assertNotIn("{{", result.stdout)
```
Visibility test should mirror this for source header, status block, exceptions block, Top 3 action cap, and source-path presence.

**Latest/history existence assertions** (`tests/test_generate_decision_package.py:31-45`):
```python
result = self.run_script("--date", "2026-04-25")
self.assertEqual(result.returncode, 0, msg=result.stderr)
self.assertTrue(OPERATING_PATH.exists(), "latest operating package missing")
self.assertTrue(HISTORY_PATH.exists(), "history operating package missing")
```
Reuse for visibility latest/history artifact write verification.

---

### `scripts/smoke_test_pipeline.sh` (test, batch)

**Analog:** `scripts/smoke_test_pipeline.sh`

**Required artifact existence pattern** (`scripts/smoke_test_pipeline.sh:54-80`):
```bash
check_file_nonempty "$ROOT_DIR/assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md"
check_file_nonempty "$ROOT_DIR/assets/shared/execution_packages/EXECUTION_PACKAGE.md"
check_file_nonempty "$ROOT_DIR/assets/shared/board_briefings/BOARD_BRIEFING.md"
...
check_file_nonempty "$ROOT_DIR/orchestration/cron/commands.sh"
```
Add the visibility artifact and generator script here using the same `check_file_nonempty` pattern.

**Python syntax check pattern** (`scripts/smoke_test_pipeline.sh:87-99`):
```bash
run_check "decision package generator syntax" "$PYTHON_BIN" -m py_compile "$ROOT_DIR/scripts/generate_decision_package.py"
run_check "execution package generator syntax" "$PYTHON_BIN" -m py_compile "$ROOT_DIR/scripts/derive_execution_package.py"
run_check "board briefing generator syntax" "$PYTHON_BIN" -m py_compile "$ROOT_DIR/scripts/derive_board_briefing.py"
```
Visibility generator should be added with the same syntax-check line.

**Cron action smoke pattern** (`scripts/smoke_test_pipeline.sh:108-111`):
```bash
run_check "cron helper run-intelligence action" bash "$ROOT_DIR/orchestration/cron/commands.sh" run-intelligence
run_check "cron helper run-analysis-loop action" bash "$ROOT_DIR/orchestration/cron/commands.sh" run-analysis-loop
run_check "cron helper run-decision-packages action" bash "$ROOT_DIR/orchestration/cron/commands.sh" run-decision-packages
```
If a `run-visibility` action is added, test it here using the same shape.

---

### `orchestration/cron/commands.sh` (config, batch)

**Analog:** `orchestration/cron/commands.sh`

**Thin helper action pattern** (`orchestration/cron/commands.sh:109-120`):
```bash
run_intelligence() {
  bash "$ROOT_DIR/scripts/run_external_intelligence.sh"
}

run_analysis_loop() {
  bash "$ROOT_DIR/scripts/run_signal_analysis_loop.sh"
}

run_decision_packages() {
  bash "$ROOT_DIR/scripts/run_signal_analysis_loop.sh"
}
```
Visibility wiring should follow this exact helper style: one shell function, one direct script invocation, no extra logic.

**Case dispatch pattern** (`orchestration/cron/commands.sh:138-157`):
```bash
case "$ACTION" in
  ...
  run-intelligence) run_intelligence ;;
  run-analysis-loop) run_analysis_loop ;;
  run-decision-packages) run_decision_packages ;;
  ...
```
Add `run-visibility` or fold visibility generation into `run-decision-packages` using this same dispatcher convention.

---

### `orchestration/cron/daily_pipeline.prompt.md` (config, batch)

**Analog:** `orchestration/cron/daily_pipeline.prompt.md`

**Ordered artifact-read workflow pattern** (`orchestration/cron/daily_pipeline.prompt.md:26-41`):
```markdown
6. Decision Package 产物层
   - 读取 `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`
   - 读取 `assets/shared/execution_packages/EXECUTION_PACKAGE.md`
   - 读取 `assets/shared/board_briefings/BOARD_BRIEFING.md`
   - 确认三类产物都来自同一天主包派生...
...
- 如果所有指标健康，摘要第一行写“Daily pipeline completed: HEALTHY”。
- 如果存在重大风险，摘要第一行写“Daily pipeline completed: ACTION REQUIRED”。
```
Phase 5 prompt update should add visibility as the final derived read model after these artifacts exist, preserving HEALTHY/ACTION REQUIRED semantics.

---

### `docs/OPERATIONS.md` (config, request-response)

**Analog:** repo pattern inferred from artifact-first operator flow; closest concrete hooks are `orchestration/cron/daily_pipeline.prompt.md` and `assets/shared/governance/GOVERNANCE_STATUS.md`.

Document the visibility artifact as a read-only operator entrypoint, with regeneration via cron helper/script rather than manual edits.

## Shared Patterns

### Source hierarchy / trusted read model
**Sources:**
- `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md:6-20`
- `assets/shared/governance/GOVERNANCE_STATUS.md:0-21`
- `assets/shared/external_intelligence/LATEST_SUMMARY.md:2-9`
- `assets/shared/execution_packages/EXECUTION_PACKAGE.md:0-15`
- `assets/shared/board_briefings/BOARD_BRIEFING.md:0-17`

**Apply to:** visibility generator and visibility markdown artifact

**Reuse rule:** operating decision package is primary anchor; governance and latest-summary only overlay health/freshness; execution and board artifacts are supporting references only.

### Latest + history snapshot writing
**Sources:**
- `scripts/derive_execution_package.py:144-145`
- `scripts/derive_execution_package.py:184-204`
- `scripts/derive_board_briefing.py:136-137`
- `scripts/derive_board_briefing.py:172-191`

**Apply to:** latest visibility markdown and optional history snapshot

```python
def history_output_path(date_value: str) -> Path:
    return VISIBILITY_HISTORY_DIR / VISIBILITY_HISTORY_TEMPLATE.format(date=date_value)
```

### Source header / derived-from / trace header sections
**Sources:**
- `scripts/derive_board_briefing.py:156-160`
- `scripts/derive_execution_package.py:165-175`
- `scripts/governance_common.py:297-305`

**Apply to:** top of `OPERATING_VISIBILITY.md`

```python
f"# Operating Visibility - {date_value}\n"
f"- **Primary Anchor**: `{relative(OPERATING_DECISION_PACKAGE_PATH)}`\n"
f"- **Governance Overlay**: `{relative(GOVERNANCE_STATUS_PATH)}`\n"
f"- **Freshness Overlay**: `{relative(LATEST_SUMMARY_PATH)}`\n"
f"- **Supporting Views**: `{relative(EXECUTION_PACKAGE_PATH)}`, `{relative(BOARD_BRIEFING_PATH)}`\n"
f"- **Source Trace**: `{relative(DECISION_TRACE_PATH)}`\n"
```
This exact composition is not present yet, but it should be built by combining the existing derived-from and authority-source header patterns.

### Evidence-backed action lines
**Sources:**
- `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md:58-66`
- `scripts/generate_decision_package.py:345-360`

**Apply to:** Top 3 Next Actions section

```markdown
- <action> — evidence: <reason from trusted artifact> — trace: `judgment_id=<id>`
```

### Read-only composition from trusted artifacts
**Sources:**
- `scripts/derive_execution_package.py:60-66`
- `scripts/render_governance_status.py:25-35`
- `scripts/generate_decision_package.py:425-459`

**Apply to:** generator logic

Reuse the repo’s pattern of reading already-generated authoritative files, validating expected sections/fields, and emitting a thin derived markdown latest view without mutating any source artifacts.

### Smoke-test coverage for generated artifacts
**Sources:**
- `scripts/smoke_test_pipeline.sh:30-47`
- `scripts/smoke_test_pipeline.sh:54-111`

**Apply to:** new visibility artifact and generator command wiring

Reuse `check_file_nonempty` + `run_check` rather than inventing a new smoke framework.

### Cron / commands wiring
**Sources:**
- `orchestration/cron/commands.sh:103-120`
- `orchestration/cron/commands.sh:138-157`

**Apply to:** visibility generator entrypoint

Use a single shell function and one case arm; keep cron wiring thin and script-oriented.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| `assets/shared/visibility/OPERATING_VISIBILITY.md` exact final section layout | config | transform | No existing artifact combines operating anchor, governance overlay, freshness overlay, and Top 3 actions in one file; planner should compose from board briefing + governance status + execution package patterns. |
| `scripts/generate_operating_visibility.py` stale-threshold heuristic implementation | service | transform | No existing script computes stale/healthy/watch/action-required state across multiple markdown sources; planner should reuse labeled-bullet parsing and latest-view grouping patterns. |

## Metadata

**Analog search scope:** `scripts/`, `tests/`, `assets/shared/`, `orchestration/cron/`, `skills/`
**Files scanned:** 17
**Pattern extraction date:** 2026-04-25
