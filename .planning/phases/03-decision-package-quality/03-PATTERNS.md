# Phase 3: decision-package-quality - Pattern Map

**Mapped:** 2026-04-25
**Files analyzed:** 10
**Analogs found:** 10 / 10

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `scripts/generate_decision_package.py` | service | transform | `scripts/generate_role_handoffs.py` | exact |
| `scripts/derive_execution_package.py` | service | transform | `scripts/generate_role_handoffs.py` | role-match |
| `scripts/derive_board_briefing.py` | service | transform | `scripts/generate_role_handoffs.py` | role-match |
| `scripts/run_signal_analysis_loop.sh` | utility | batch | `scripts/run_signal_analysis_loop.sh` | exact-modify |
| `scripts/smoke_test_pipeline.sh` | test | batch | `scripts/smoke_test_pipeline.sh` | exact-modify |
| `orchestration/cron/daily_pipeline.prompt.md` | config | request-response | `orchestration/cron/daily_pipeline.prompt.md` | exact-modify |
| `orchestration/cron/commands.sh` | utility | request-response | `orchestration/cron/commands.sh` | exact-modify |
| `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` | config | transform | `assets/shared/CEO_RANKING.md` | partial |
| `assets/shared/execution_packages/EXECUTION_PACKAGE.md` | config | transform | `assets/shared/MARKET_PLAN.md` | partial |
| `assets/shared/board_briefings/BOARD_BRIEFING.md` | config | transform | `assets/shared/CEO_RANKING.md` | partial |

## Pattern Assignments

### `scripts/generate_decision_package.py` (service, transform)

**Analog:** `scripts/generate_role_handoffs.py`

**Why this is the closest match:** same Python generator role, same read-validate-render-write flow, same repo-local markdown artifact outputs under `assets/shared/`.

**Imports and path constants** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/generate_role_handoffs.py:1-16`):
```python
#!/usr/bin/env python3
import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
SHARED_DIR = ROOT_DIR / "assets" / "shared"
TRIAGE_PATH = SHARED_DIR / "external_intelligence" / "triage" / "prioritized_signals.json"
PAIN_POINTS_PATH = SHARED_DIR / "PAIN_POINTS.md"
MARKET_PLAN_PATH = SHARED_DIR / "MARKET_PLAN.md"
TECH_SPEC_PATH = SHARED_DIR / "TECH_SPEC.md"
CEO_RANKING_PATH = SHARED_DIR / "CEO_RANKING.md"
```
Copy this pattern for root-relative constants, adding decision-package output paths and optional history/trace paths.

**Validation pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/generate_role_handoffs.py:34-50`):
```python
def load_prioritized(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        raise RoleHandoffError(f"prioritized signal file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise RoleHandoffError(f"invalid prioritized signal JSON: {path}") from exc
    prioritized = payload.get("prioritized_signals")
    if not isinstance(prioritized, list) or not prioritized:
        raise RoleHandoffError("prioritized_signals must be a non-empty list")
```
Use the same explicit file existence + JSON shape checks for triage input and for any trace sidecar input/output.

**Render function pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/generate_role_handoffs.py:120-138`):
```python
def render_ceo_ranking(leads: list[dict[str, Any]], source_path: Path) -> str:
    header = [
        "## Top 3 Ranked Micro-SaaS Ideas (last 48h)",
        "| Rank | idea_id | Idea | TotalScore/100 | Urgency | Feasibility | Monetization | Evidence | Recency | Competition | MVP Hours |",
        "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    ...
    recommendation = (
        f"**Recommended**: {top['idea_id']} — highest shared-shortlist score with fresh evidence and the clearest bridge from pain signal to MVP.\n\n"
        f"Shared shortlist source: `{source_path.as_posix()}`\n"
    )
    return "\n".join(header + rows + ["", recommendation])
```
Follow this “small pure renderer returns markdown string” shape for decision package sections: one-line conclusion, Top 3, evidence summaries, risks, next actions, backlinks.

**Write and dry-run pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/generate_role_handoffs.py:141-173`):
```python
def write_output(path: Path, content: str) -> None:
    path.write_text(content.rstrip() + "\n", encoding="utf-8")

...
if args.dry_run:
    print("=== PAIN_POINTS.md ===")
    print(pain_points)
    ...
    return 0
write_output(PAIN_POINTS_PATH, pain_points)
...
print(f"Wrote {CEO_RANKING_PATH.relative_to(ROOT_DIR)}")
```
Keep this exact CLI contract style: `--dry-run` prints render results; normal mode writes files and prints repo-relative paths.

**Error handling pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/generate_role_handoffs.py:18-19,145-180`):
```python
class RoleHandoffError(Exception):
    pass

...
except RoleHandoffError as exc:
    print(f"role handoff error: {exc}", file=sys.stderr)
    return 1
```
Mirror with a phase-specific exception like `DecisionPackageError` and a single stderr exit path.

**Secondary analog for history/latest dual write:** `scripts/collect_external_signals.py`

**History path constants** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/collect_external_signals.py:19-27`):
```python
ROOT_DIR = Path(__file__).resolve().parent.parent
EXTERNAL_DIR = ROOT_DIR / "assets" / "shared" / "external_intelligence"
SOURCES_PATH = EXTERNAL_DIR / "SOURCES.yaml"
LATEST_SUMMARY_PATH = EXTERNAL_DIR / "LATEST_SUMMARY.md"
HISTORY_DIR = EXTERNAL_DIR / "history"
RAW_DIR = EXTERNAL_DIR / "raw"
SIGNALS_PATH = HISTORY_DIR / "signals.jsonl"
RUNS_PATH = HISTORY_DIR / "runs.jsonl"
```
Use this same constant naming split: latest alias path + history directory + sidecar/history files.

**Directory creation and write helpers** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/collect_external_signals.py:296-323`):
```python
def ensure_dirs():
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

...
def write_jsonl(path, rows):
    with path.open("a", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")
```
Reuse for decision/execution/board history folders and optional append-only trace index.

---

### `scripts/derive_execution_package.py` (service, transform)

**Analog:** `scripts/generate_role_handoffs.py`

**Closest reusable pattern:** one top-level input, one focused markdown output, minimal parsing, deterministic rendering.

**Single-source derivation pattern to copy** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/generate_role_handoffs.py:83-95`):
```python
def render_market_plan(top: dict[str, Any], source_path: Path) -> str:
    components = top["score_components"]
    return (
        f"# Market Strategy: {top['title']}\n"
        f"- **Core USP**: ...\n"
        f"- **Pricing**: ...\n"
        f"- **Distribution**: ...\n"
        f"- **Risk Level**: medium\n"
        f"- **Shared Shortlist Source**: `{source_path.as_posix()}`\n"
        f"- **Chosen Idea ID**: {top['idea_id']}\n"
        f"- **Evidence Strength (0-10)**: {fmt_score(components.get('evidence_strength', 0))}\n"
        f"- **Recency (0-10)**: {fmt_score(components.get('recency', 0))}\n"
    )
```
For execution package, keep the same compact bullet-driven markdown style, but the source should be the operating decision package path rather than triage JSON.

**Write behavior to keep identical** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/generate_role_handoffs.py:141-173`): same `write_output`, `--dry-run`, and `print(f"Wrote ...")` behavior.

---

### `scripts/derive_board_briefing.py` (service, transform)

**Analog:** `scripts/generate_role_handoffs.py`

**Closest reusable pattern:** compress richer upstream content into a short, fixed-format markdown artifact.

**Table + recommendation excerpt to mirror** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/generate_role_handoffs.py:120-138`):
```python
header = [
    "## Top 3 Ranked Micro-SaaS Ideas (last 48h)",
    "| Rank | idea_id | Idea | TotalScore/100 | Urgency | Feasibility | Monetization | Evidence | Recency | Competition | MVP Hours |",
    "|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
]
...
recommendation = (
    f"**Recommended**: {top['idea_id']} — ...\n\n"
    f"Shared shortlist source: `{source_path.as_posix()}`\n"
)
```
Board briefing should copy this compact executive-summary pattern: short heading block, very small table/list, one-line recommendation, explicit source backlink.

**Error/CLI pattern:** same as `generate_role_handoffs.py:18-19,145-180`.

---

### `scripts/run_signal_analysis_loop.sh` (utility, batch)

**Analog:** `scripts/run_signal_analysis_loop.sh`

**Current chaining pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/run_signal_analysis_loop.sh:3-6,31-68`):
```bash
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PYTHON_BIN=""
TRIAGE_ARGS=()
HANDOFF_ARGS=()
...
parse_args() {
  while [ "$#" -gt 0 ]; do
    case "$1" in
      --window-hours)
        TRIAGE_ARGS+=("$1" "$2")
        ;;
      --limit)
        TRIAGE_ARGS+=("$1" "$2")
        HANDOFF_ARGS+=("$1" "$2")
        ;;
      --date)
        HANDOFF_ARGS+=("$1" "$2")
        ;;
      --dry-run)
        TRIAGE_ARGS+=("$1")
        HANDOFF_ARGS+=("$1")
        ;;
```
Extend this same arg-fanout pattern with a third/fourth/fifth arg array for decision package and its derivatives.

**Sequential generator execution pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/run_signal_analysis_loop.sh:64-68`):
```bash
resolve_python
parse_args "$@"

run_python "$ROOT_DIR/scripts/triage_external_signals.py" "${TRIAGE_ARGS[@]}"
run_python "$ROOT_DIR/scripts/generate_role_handoffs.py" "${HANDOFF_ARGS[@]}"
```
Append new generator calls in-order after role handoffs so all downstream packages share the same freshly generated evidence base.

---

### `scripts/smoke_test_pipeline.sh` (test, batch)

**Analog:** `scripts/smoke_test_pipeline.sh`

**Existence-check pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/smoke_test_pipeline.sh:30-37,54-71`):
```bash
check_file_nonempty() {
  local f="$1"
  if [ -s "$f" ]; then
    ok "file exists and non-empty: $f"
  else
    fail "file missing or empty: $f"
  fi
}
...
check_file_nonempty "$ROOT_DIR/assets/shared/CEO_RANKING.md"
check_file_nonempty "$ROOT_DIR/scripts/collect_external_signals.py"
check_file_nonempty "$ROOT_DIR/scripts/triage_external_signals.py"
check_file_nonempty "$ROOT_DIR/scripts/generate_role_handoffs.py"
```
Add decision/execution/board package latest files and new generator scripts with the same function.

**Python syntax-check pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/smoke_test_pipeline.sh:78-83`):
```bash
if [ -n "$PYTHON_BIN" ]; then
  run_check "finance script syntax" "$PYTHON_BIN" -m py_compile "$ROOT_DIR/assets/shared/manage_finance.py"
  run_check "external intelligence collector syntax" "$PYTHON_BIN" -m py_compile "$ROOT_DIR/scripts/collect_external_signals.py"
  run_check "signal triage syntax" "$PYTHON_BIN" -m py_compile "$ROOT_DIR/scripts/triage_external_signals.py"
  run_check "role handoff generator syntax" "$PYTHON_BIN" -m py_compile "$ROOT_DIR/scripts/generate_role_handoffs.py"
fi
```
Copy this exact structure for `generate_decision_package.py`, `derive_execution_package.py`, and `derive_board_briefing.py`.

**Smoke command pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/smoke_test_pipeline.sh:84-90`):
```bash
run_check "external intelligence dry run" bash "$ROOT_DIR/scripts/run_external_intelligence.sh" --dry-run
run_check "signal analysis loop run" bash "$ROOT_DIR/scripts/run_signal_analysis_loop.sh" --window-hours 48 --limit 3
run_check "cron helper run-intelligence action" bash "$ROOT_DIR/orchestration/cron/commands.sh" run-intelligence
run_check "cron helper run-analysis-loop action" bash "$ROOT_DIR/orchestration/cron/commands.sh" run-analysis-loop
```
Prefer adding dry-run checks for new generators and a full loop check that proves latest artifacts are produced.

---

### `orchestration/cron/daily_pipeline.prompt.md` (config, request-response)

**Analog:** `orchestration/cron/daily_pipeline.prompt.md`

**Ordered stage-list pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/orchestration/cron/daily_pipeline.prompt.md:4-28`):
```markdown
执行顺序：
0. External Intelligence 阶段
   - 运行 `bash scripts/run_external_intelligence.sh`
   - 读取 `assets/shared/external_intelligence/LATEST_SUMMARY.md`
...
5. CEO 决策阶段
   - 读取 `assets/shared/LEDGER.json`、`assets/shared/MARKET_PLAN.md`、`assets/shared/TECH_SPEC.md`、`assets/shared/CEO_RANKING.md`
   - 基于 CEO ranking 做 GO/NO-GO，并写入 `assets/shared/CORP_CULTURE.md`
6. Accountant 审计阶段
   - 运行 `python3 assets/shared/manage_finance.py audit`
```
Insert a new numbered step immediately after CEO ranking generation that explicitly reads the operating decision package and derived artifacts. Keep the same imperative bullet style.

**Constraint block pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/orchestration/cron/daily_pipeline.prompt.md:30-35`):
```markdown
约束：
- 默认中文输出。
- 任何风险结论必须带证据（文件或数字）。
- 如果所有指标健康，摘要第一行写“Daily pipeline completed: HEALTHY”。
- 如果存在重大风险，摘要第一行写“Daily pipeline completed: ACTION REQUIRED”。
```
Add new constraints here, not elsewhere: decision/execution/board artifacts must derive from the same day’s main package, and evidence backlinks must be preserved.

---

### `orchestration/cron/commands.sh` (utility, request-response)

**Analog:** `orchestration/cron/commands.sh`

**Root path + action dispatch pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/orchestration/cron/commands.sh:3-12,127-143`):
```bash
ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
DAILY_PROMPT_FILE="$ROOT_DIR/orchestration/cron/daily_pipeline.prompt.md"
...
ACTION="${1:-list}"
...
case "$ACTION" in
  create) create_jobs ;;
  ensure) ensure_jobs ;;
  recreate) recreate_jobs ;;
  ...
  run-daily) run_daily ;;
  run-intelligence) run_intelligence ;;
  run-analysis-loop) run_analysis_loop ;;
```
If new command wiring is added, keep it as another small action function plus one extra case arm.

**Thin wrapper pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/orchestration/cron/commands.sh:110-116`):
```bash
run_intelligence() {
  bash "$ROOT_DIR/scripts/run_external_intelligence.sh"
}

run_analysis_loop() {
  bash "$ROOT_DIR/scripts/run_signal_analysis_loop.sh"
}
```
Follow this exact wrapper style for any new explicit decision-package action; do not embed large logic here.

---

### `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md` (config, transform)

**Analog:** `assets/shared/CEO_RANKING.md`

**Executive-first opening pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/assets/shared/CEO_RANKING.md:0-8`):
```markdown
## Top 3 Ranked Micro-SaaS Ideas (last 48h)
| Rank | idea_id | Idea | TotalScore/100 | Urgency | Feasibility | Monetization | Evidence | Recency | Competition | MVP Hours |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 1 | IDEA-001 | ... |
| 2 | IDEA-002 | ... |

**Recommended**: IDEA-001 — highest shared-shortlist score with fresh evidence and the clearest bridge from pain signal to MVP.

Shared shortlist source: `assets/shared/external_intelligence/triage/prioritized_signals.json`
```
Use this as the opening shape: headline conclusion and ranked Top 3 before any long analysis. Phase 3 should prepend a one-line overall decision above this block, not replace the compact ranking style.

**Template vocabulary support:** `assets/shared/TEMPLATES.md:35-47` defines the same CEO top-3 table contract and can be reused for section naming consistency.

---

### `assets/shared/execution_packages/EXECUTION_PACKAGE.md` (config, transform)

**Analog:** `assets/shared/MARKET_PLAN.md` via renderer in `scripts/generate_role_handoffs.py`

**Kickoff-pack bullet style** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/generate_role_handoffs.py:83-95`):
```python
return (
    f"# Market Strategy: {top['title']}\n"
    f"- **Core USP**: ...\n"
    f"- **Pricing**: ...\n"
    f"- **Distribution**: ...\n"
    f"- **Risk Level**: medium\n"
    f"- **Shared Shortlist Source**: `{source_path.as_posix()}`\n"
    f"- **Chosen Idea ID**: {top['idea_id']}\n"
```
Copy the compact kickoff-doc tone: title plus bullets for goal, target user, MVP framing, key risks, near-term actions, and explicit source backlink to the operating package.

**Template vocabulary support:** `assets/shared/TEMPLATES.md:49-56` already shows concise market-plan bullet formatting and should guide section density.

---

### `assets/shared/board_briefings/BOARD_BRIEFING.md` (config, transform)

**Analog:** `assets/shared/CEO_RANKING.md`

**Compact board-summary pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/assets/shared/CEO_RANKING.md:0-8`): keep a very short table/list with ranked items, one recommendation line, and one explicit source line.

**Additional compact signal-summary pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/assets/shared/external_intelligence/LATEST_SUMMARY.md:1-9,34-52`):
```markdown
## Run Metadata
- **run_id**: run-20260424T182938Z
- **started_at**: 2026-04-24T18:29:38Z
- **completed_at**: 2026-04-24T18:29:41Z
- **new_signal_count**: 6
- **duplicate_signal_count**: 1
- **failed_source_count**: 0

## Complaint Signals
- **I Cancelled Claude: Token Issues, Declining Quality, and Poor Support ...** (...) — https://news.ycombinator.com/
  - source_id: `web-discovery-default-2`
  - summary: ...
```
Board brief should borrow this “tiny metadata block + short bullets” density for key numbers/signals and required attention items.

---

### `assets/shared/decision_packages/history/*.md`, `assets/shared/execution_packages/history/*.md`, `assets/shared/board_briefings/history/*.md` (config, file-I/O)

**Analog:** `assets/shared/external_intelligence/history/runs.jsonl` and latest/history split in `scripts/collect_external_signals.py`

**Appendable history precedent** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/assets/shared/external_intelligence/history/runs.jsonl:0-7`):
```json
{"run_id": "run-20260424T182938Z", "started_at": "2026-04-24T18:29:38Z", "completed_at": "2026-04-24T18:29:41Z", ...}
```

**Latest + history constant pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/collect_external_signals.py:19-27`):
```python
LATEST_SUMMARY_PATH = EXTERNAL_DIR / "LATEST_SUMMARY.md"
HISTORY_DIR = EXTERNAL_DIR / "history"
```
Implement the same dual-path convention for all three package families: one stable latest file and one dated history snapshot.

---

### `assets/shared/trace/*` (utility/config, transform)

**Analog:** `assets/shared/external_intelligence/triage/prioritized_signals.json`

**Traceable source metadata pattern** (`/c/Users/42236/Desktop/dev/profit-corp-hermes/assets/shared/external_intelligence/triage/prioritized_signals.json:1-4,48-53`):
```json
{
  "generated_at": "2026-04-24T18:29:42.587949Z",
  "window_hours": 48,
  "source_history": "assets/shared/external_intelligence/history/signals.jsonl",
  ...
  "generated_from": {
    "history_path": "assets/shared/external_intelligence/history/signals.jsonl",
    "cluster_path": "assets/shared/external_intelligence/triage/clusters.json",
    "representative_url": "https://lobste.rs/"
  }
}
```
If a trace sidecar is added, mirror this exact metadata style: generated timestamp plus concrete upstream file paths and anchorable IDs.

## Shared Patterns

### 1. Python generator structure
**Sources:**
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/generate_role_handoffs.py:1-16`
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/generate_role_handoffs.py:141-180`

**Apply to:** all three new Python generators.

**Copy pattern:**
- stdlib-only imports
- `ROOT_DIR` / `SHARED_DIR` constants at top
- custom exception class
- `parse_args()` with `--dry-run`
- pure `render_*()` helpers
- one `write_output()` helper
- one `main()` with single `try/except` and stderr error string

### 2. Explicit input validation before rendering
**Sources:**
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/generate_role_handoffs.py:34-50`
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/triage_external_signals.py:136-143`

**Apply to:** decision-package input loaders and trace/sidecar loaders.

**Copy pattern:** validate file existence, JSON decode, required keys, and non-empty lists before any markdown rendering.

### 3. latest + history dual-write storage
**Sources:**
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/collect_external_signals.py:19-27`
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/collect_external_signals.py:296-323`

**Apply to:** decision packages, execution packages, board briefings, optional trace index.

**Copy pattern:** separate constant for stable latest file and history dir; create dirs with `mkdir(parents=True, exist_ok=True)`; write deterministic files under repo-relative asset paths.

### 4. Batch wrapper fan-out in shell
**Sources:**
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/run_signal_analysis_loop.sh:31-68`
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/orchestration/cron/commands.sh:110-116`

**Apply to:** daily pipeline wiring and any new command wrappers.

**Copy pattern:** small shell functions, arg arrays per downstream script, sequential invocation, no business logic embedded in cron wrapper.

### 5. Smoke-test extension pattern
**Sources:**
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/smoke_test_pipeline.sh:30-37`
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/smoke_test_pipeline.sh:78-90`

**Apply to:** every new generator and latest artifact.

**Copy pattern:** add `check_file_nonempty`, `py_compile`, and `run_check` entries rather than inventing a new test harness.

### 6. Evidence backlink formatting
**Sources:**
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/generate_role_handoffs.py:76-80,135-137`
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/assets/shared/CEO_RANKING.md:6-8`
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/assets/shared/external_intelligence/triage/prioritized_signals.json:48-53`

**Apply to:** operating decision package body, execution package source reference, board briefing source reference, optional trace sidecar.

**Copy pattern:** always include explicit repo-relative source paths such as:
- ``Shared shortlist source: `assets/shared/external_intelligence/triage/prioritized_signals.json``` 
- generated metadata blocks with `generated_from.history_path`, `cluster_path`, or equivalent.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| None | — | — | The repo already has close analogs for generator scripts, latest/history storage, prompt wiring, and smoke-test extension. |

## Metadata

**Analog search scope:**
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts`
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/assets/shared`
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/orchestration/cron`

**Files scanned:** 11

**Pattern extraction date:** 2026-04-25
