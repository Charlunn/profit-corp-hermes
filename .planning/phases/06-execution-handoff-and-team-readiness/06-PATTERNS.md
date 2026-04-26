# Phase 6: Execution Handoff and Team Readiness - Pattern Map

**Mapped:** 2026-04-26
**Files analyzed:** 6
**Analogs found:** 6 / 6

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `scripts/derive_execution_package.py` | service | transform | `scripts/generate_decision_package.py` | role-match |
| `assets/shared/execution_packages/EXECUTION_PACKAGE.md` | config | transform | `assets/shared/execution_packages/EXECUTION_PACKAGE.md` | exact |
| `scripts/derive_board_briefing.py` | service | transform | `scripts/derive_execution_package.py` | exact |
| `assets/shared/board_briefings/BOARD_BRIEFING.md` | config | transform | `assets/shared/board_briefings/BOARD_BRIEFING.md` | exact |
| `tests/test_derived_packages.py` | test | transform | `tests/test_generate_operating_visibility.py` | role-match |
| `scripts/generate_operating_visibility.py` | service | transform | `scripts/generate_operating_visibility.py` | exact |

## Pattern Assignments

### `scripts/derive_execution_package.py` (service, transform)

**Analog:** `scripts/generate_decision_package.py`

**Imports + path-constant pattern** (`scripts/generate_decision_package.py`, lines 0-33):
```python
#!/usr/bin/env python3
import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT_DIR = Path(__file__).resolve().parent.parent
SHARED_DIR = ROOT_DIR / "assets" / "shared"
DECISION_PACKAGES_DIR = SHARED_DIR / "decision_packages"
DECISION_HISTORY_DIR = DECISION_PACKAGES_DIR / "history"
TRACE_DIR = SHARED_DIR / "trace"
OPERATING_DECISION_PACKAGE_PATH = DECISION_PACKAGES_DIR / "OPERATING_DECISION_PACKAGE.md"
OPERATING_DECISION_HISTORY_TEMPLATE = "{date}-operating-decision-package.md"
DECISION_TRACE_PATH = TRACE_DIR / "decision_package_trace.json"
ALLOWED_WRITE_DIRS = (
    DECISION_PACKAGES_DIR,
    DECISION_HISTORY_DIR,
    TRACE_DIR,
)
```

**Write-allowlist pattern** (`scripts/derive_execution_package.py`, lines 44-57):
```python
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

**Input validation + extractor pattern** (`scripts/derive_execution_package.py`, lines 73-141):
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


def extract_value(content: str, label: str) -> str:
    pattern = re.compile(rf"^- \*\*{re.escape(label)}\*\*: (.+)$", re.MULTILINE)
    match = pattern.search(content)
    if not match:
        raise ExecutionPackageError(f"missing required value in operating package: {label}")
    return match.group(1).strip()
```

**Core render-function pattern** (`scripts/derive_execution_package.py`, lines 148-181):
```python
def render_execution_package(date_value: str, operating_package: str, trace_content: str) -> str:
    require_section(operating_package, "## Overall Conclusion / 一句话总判断")
    require_section(operating_package, "## Top 3 Ranked Opportunities")
    require_section(operating_package, "## Operating Framing")
    require_section(operating_package, "## 主要风险")
    require_section(operating_package, "## 推荐下一步")
    require_source_reference(operating_package)
    if '"judgment_links"' not in trace_content:
        raise ExecutionPackageError("decision trace missing judgment_links")

    top_row = extract_first_table_row(operating_package)
    goal = extract_value(operating_package, "Goal")
    target_user = extract_value(operating_package, "Target User")
    mvp_framing = extract_value(operating_package, "MVP Framing")
    key_risk = extract_first_risk_summary(operating_package)
    first_action = extract_first_bullet_after_heading(operating_package, "## 推荐下一步")

    return (
        f"# Execution Package - {date_value}\n"
        f"- **Derived From**: `{relative(OPERATING_DECISION_PACKAGE_PATH)}`\n"
        f"- **Source Trace**: `{relative(DECISION_TRACE_PATH)}`\n"
        ...
    )
```

**Main/write flow pattern** (`scripts/derive_execution_package.py`, lines 184-211):
```python
def main() -> int:
    args = parse_args()
    try:
        assert_derived_only_inputs()
        date_value = args.date or today_iso()
        operating_package = load_text(OPERATING_DECISION_PACKAGE_PATH, "operating decision package")
        trace_content = load_text(DECISION_TRACE_PATH, "decision trace")
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
        return 0
    except ExecutionPackageError as exc:
        print(f"execution package error: {exc}", file=sys.stderr)
        return 1
```

**What to copy for Phase 6:** Keep the same script skeleton, path constants, dry-run/write dual mode, allowlisted writes, section validation, and single `render_execution_package(...)` owner function. Replace the old top-level bullet contract with the new Core 9 section contract plus embedded ownership/readiness fields inside the render function.

---

### `assets/shared/execution_packages/EXECUTION_PACKAGE.md` (config, transform)

**Analog:** `assets/shared/execution_packages/EXECUTION_PACKAGE.md`

**Header/provenance pattern** (`assets/shared/execution_packages/EXECUTION_PACKAGE.md`, lines 0-9):
```markdown
# Execution Package - 2026-04-25
- **Derived From**: `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`
- **Source Trace**: `assets/shared/trace/decision_package_trace.json`
- **Goal**: 验证 IDEA-001 是否值得作为下一阶段 mini-SaaS 切入点，并确认用户是否愿意为该痛点付费。
- **Target User**: Developers and technical operators
- **MVP Framing**: 以 IDEA-001 为核心做一个 74 小时量级的 markdown-first operator workflow 原型，先验证最痛的检索/反馈闭环。
- **Key Risks**: MARKET_PLAN.md 标记风险等级为 medium，同时该机会预计 MVP 需 74 小时，说明直接进入完整构建的执行风险偏高。
- **Recommended Near-Term Actions**:
  - 围绕 IDEA-001 组织 3-5 个目标用户验证访谈 ...
```

**Compact section style** (`assets/shared/execution_packages/EXECUTION_PACKAGE.md`, lines 11-15):
```markdown
## Kickoff Focus
- **Primary Idea**: IDEA-001
- **Why This Opportunity**: Monetization 10/10、Urgency 5.5/10，适合先做轻量验证再决定是否深入。
- **Signal Reference**: 31 条证据，最近证据距今 0 小时，来源集中在 web-discovery-default-1。
- **MVP Boundary**: Stay within the operator workflow implied by the operating package; do not add task-board governance fields.
```

**What to copy for Phase 6:** Preserve the markdown-first compact bullet style, provenance header, and anti-bloat tone. Replace `Kickoff Focus` with the fixed Core 9 section set and embed minimal ownership metadata in a stable, concise block.

---

### `scripts/derive_board_briefing.py` (service, transform)

**Analog:** `scripts/derive_execution_package.py`

**Imports + path constant pattern** (`scripts/derive_board_briefing.py`, lines 0-21):
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
BOARD_BRIEFINGS_DIR = SHARED_DIR / "board_briefings"
BOARD_HISTORY_DIR = BOARD_BRIEFINGS_DIR / "history"
TRACE_DIR = SHARED_DIR / "trace"
OPERATING_DECISION_PACKAGE_PATH = DECISION_PACKAGES_DIR / "OPERATING_DECISION_PACKAGE.md"
DECISION_TRACE_PATH = TRACE_DIR / "decision_package_trace.json"
BOARD_BRIEFING_PATH = BOARD_BRIEFINGS_DIR / "BOARD_BRIEFING.md"
BOARD_BRIEFING_HISTORY_TEMPLATE = "{date}-board-briefing.md"
ALLOWED_WRITE_DIRS = (
    BOARD_BRIEFINGS_DIR,
    BOARD_HISTORY_DIR,
)
```

**Extractor helpers pattern** (`scripts/derive_board_briefing.py`, lines 85-133):
```python
def extract_line_after_heading(content: str, heading: str) -> str:
    lines = content.splitlines()
    for index, line in enumerate(lines):
        if line.strip() == heading:
            for candidate in lines[index + 1 :]:
                stripped = candidate.strip()
                if stripped:
                    return stripped
            break
    raise BoardBriefingError(f"content missing value after heading: {heading}")


def extract_top_rows(content: str) -> list[tuple[str, str, str]]:
    rows: list[tuple[str, str, str]] = []
    for line in content.splitlines():
        if line.startswith("| ") and not line.startswith("| Rank ") and not line.startswith("|---"):
            parts = [part.strip() for part in line.strip("|").split("|")]
            if len(parts) >= 6:
                rows.append((parts[0], parts[1], parts[3]))
```

**Core one-screen render pattern** (`scripts/derive_board_briefing.py`, lines 140-169):
```python
def render_board_briefing(date_value: str, operating_package: str, trace_content: str) -> str:
    require_section(operating_package, "## Overall Conclusion / 一句话总判断")
    require_section(operating_package, "## Top 3 Ranked Opportunities")
    require_section(operating_package, "## 主要风险")
    require_section(operating_package, "## 推荐下一步")
    if '"judgment_links"' not in trace_content:
        raise BoardBriefingError("decision trace missing judgment_links")

    conclusion = extract_line_after_heading(operating_package, "## Overall Conclusion / 一句话总判断")
    top_rows = extract_top_rows(operating_package)
    major_risk = extract_first_risk_summary(operating_package)
    action_bullets = extract_bullets(operating_package, "## 推荐下一步")

    top_lines = [f"{rank}. {idea_id} — {why_now}" for rank, idea_id, why_now in top_rows]
    key_signal_lines = [f"- {idea_id}: {why_now}" for _, idea_id, why_now in top_rows[:2]]

    return (
        f"# Board Briefing - {date_value}\n"
        ...
        + "\n\n## Required Attention\n"
        + f"- {action_bullets[0]}\n"
    )
```

**Main/write flow pattern** (`scripts/derive_board_briefing.py`, lines 172-199):
```python
def main() -> int:
    args = parse_args()
    try:
        assert_derived_only_inputs()
        date_value = args.date or today_iso()
        operating_package = load_text(OPERATING_DECISION_PACKAGE_PATH, "operating decision package")
        trace_content = load_text(DECISION_TRACE_PATH, "decision trace")
        latest_output = render_board_briefing(date_value, operating_package, trace_content)
        history_path = history_output_path(date_value)
        if args.dry_run:
            print("=== BOARD_BRIEFING.md ===")
            print(latest_output)
            print(f"=== history/{history_path.name} ===")
            print(latest_output)
            return 0
        ensure_dirs()
        write_output(BOARD_BRIEFING_PATH, latest_output)
        write_output(history_path, latest_output)
```

**What to copy for Phase 6:** Keep this file structurally parallel to `derive_execution_package.py`: same parser/main/error style, same provenance header, same one-screen rendering discipline. Change only the render contract so the output contains exactly one governance, one risk, one finance, and one required-attention signal.

---

### `assets/shared/board_briefings/BOARD_BRIEFING.md` (config, transform)

**Analog:** `assets/shared/board_briefings/BOARD_BRIEFING.md`

**Header + compact section pattern** (`assets/shared/board_briefings/BOARD_BRIEFING.md`, lines 0-17):
```markdown
# Board Briefing - 2026-04-25
- **Derived From**: `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`
- **Source Trace**: `assets/shared/trace/decision_package_trace.json`
- **Conclusion**: 优先围绕 IDEA-001 开启下一轮 founder/operator 验证：它仍是今天最强的机会信号，但由于当前风险等级为 medium 且预计 MVP 需要 74 小时，执行上应先做窄范围验证而不是直接全面投入。

## Top 3
1. IDEA-001 — Monetization 10/10、Urgency 5.5/10，适合先做轻量验证再决定是否深入。
2. IDEA-002 — Monetization 5/10、Urgency 7/10，适合先做轻量验证再决定是否深入。

## Key Numbers / Signals
- IDEA-001: Monetization 10/10、Urgency 5.5/10，适合先做轻量验证再决定是否深入。
- IDEA-002: Monetization 5/10、Urgency 7/10，适合先做轻量验证再决定是否深入。

## Major Risk
- MARKET_PLAN.md 标记风险等级为 medium，同时该机会预计 MVP 需 74 小时，说明直接进入完整构建的执行风险偏高。

## Required Attention
- 围绕 IDEA-001 组织 3-5 个目标用户验证访谈 ...
```

**What to copy for Phase 6:** Preserve the one-screen executive layout, top header bullets, and short signal sections. Replace `Top 3` and `Key Numbers / Signals` with the locked board signal set while keeping the artifact scannable on one screen.

---

### `tests/test_derived_packages.py` (test, transform)

**Analog:** `tests/test_generate_operating_visibility.py`

**Subprocess test harness pattern** (`tests/test_derived_packages.py`, lines 0-22):
```python
import subprocess
import sys
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
EXECUTION_SCRIPT = ROOT_DIR / "scripts" / "derive_execution_package.py"
BOARD_SCRIPT = ROOT_DIR / "scripts" / "derive_board_briefing.py"

class DerivedPackagesTests(unittest.TestCase):
    def run_script(self, script: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *args],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )
```

**Exact-string contract assertion pattern** (`tests/test_derived_packages.py`, lines 24-44):
```python
def test_execution_dry_run_renders_required_fields(self) -> None:
    result = self.run_script(EXECUTION_SCRIPT, "--dry-run")
    self.assertEqual(result.returncode, 0, msg=result.stderr)
    self.assertIn("Target User", result.stdout)
    self.assertIn("MVP", result.stdout)
    self.assertIn("OPERATING_DECISION_PACKAGE.md", result.stdout)
    self.assertIn("IDEA-001", result.stdout)
    self.assertNotIn("待主包补充", result.stdout)
    self.assertNotIn("{{", result.stdout)
    self.assertNotIn("Owner", result.stdout)
    self.assertNotIn("Dependency", result.stdout)
```

**Write-mode latest/history pattern** (`tests/test_derived_packages.py`, lines 46-74):
```python
def test_write_mode_updates_latest_and_history(self) -> None:
    execution_result = self.run_script(EXECUTION_SCRIPT, "--date", "2026-04-25")
    board_result = self.run_script(BOARD_SCRIPT, "--date", "2026-04-25")
    self.assertEqual(execution_result.returncode, 0, msg=execution_result.stderr)
    self.assertEqual(board_result.returncode, 0, msg=board_result.stderr)

    self.assertTrue(EXECUTION_PATH.exists(), "latest execution package missing")
    self.assertTrue(BOARD_PATH.exists(), "latest board briefing missing")
    self.assertTrue(EXECUTION_HISTORY_PATH.exists(), "execution history snapshot missing")
    self.assertTrue(BOARD_HISTORY_PATH.exists(), "board history snapshot missing")
```

**Richer section-order helper to copy from** (`tests/test_generate_operating_visibility.py`, lines 24-71):
```python
EXPECTED_SECTION_ORDER = [
    "## Status",
    "## Top Alerts",
    "## Current Situation",
    "## Top Opportunities",
    "## Top Risks",
    "## Top 3 Next Actions",
    "## Evidence Backlinks",
]


def assert_section_order(self, output: str) -> None:
    positions: list[int] = []
    for section in EXPECTED_SECTION_ORDER:
        self.assertIn(section, output)
        positions.append(output.index(section))
    self.assertEqual(positions, sorted(positions), "section order drifted")


def extract_section(self, output: str, heading: str) -> str:
    marker = f"\n{heading}\n"
    self.assertIn(marker, output, msg=f"missing section marker for {heading}")
```

**What to copy for Phase 6:** Keep subprocess-based script tests and exact heading assertions. Extend them in the style of `test_generate_operating_visibility.py` to assert ordered Core 9 execution sections, exact ownership field names, allowed readiness enum values, per-risk acceptance pairings, and exactly one board signal per category.

---

### `scripts/generate_operating_visibility.py` (service, transform)

**Analog:** `scripts/generate_operating_visibility.py`

**Supporting-view path pattern** (`scripts/generate_operating_visibility.py`, lines 19-30):
```python
OPERATING_DECISION_PACKAGE_PATH = DECISION_PACKAGES_DIR / "OPERATING_DECISION_PACKAGE.md"
DECISION_TRACE_PATH = TRACE_DIR / "decision_package_trace.json"
GOVERNANCE_STATUS_PATH = GOVERNANCE_DIR / "GOVERNANCE_STATUS.md"
LATEST_SUMMARY_PATH = EXTERNAL_INTELLIGENCE_DIR / "LATEST_SUMMARY.md"
EXECUTION_PACKAGE_PATH = EXECUTION_PACKAGES_DIR / "EXECUTION_PACKAGE.md"
BOARD_BRIEFING_PATH = BOARD_BRIEFINGS_DIR / "BOARD_BRIEFING.md"
OPERATING_VISIBILITY_PATH = VISIBILITY_DIR / "OPERATING_VISIBILITY.md"
VISIBILITY_HISTORY_TEMPLATE = "{date}-operating-visibility.md"
ALLOWED_WRITE_DIRS = (
    VISIBILITY_DIR,
    VISIBILITY_HISTORY_DIR,
)
```

**Reader/validator pattern** (`scripts/generate_operating_visibility.py`, lines 120-179):
```python
def require_section(content: str, heading: str) -> None:
    if heading not in content:
        raise OperatingVisibilityError(f"operating package missing required section: {heading}")


def require_heading(content: str, heading: str, label: str) -> None:
    if heading not in content:
        raise OperatingVisibilityError(f"{label} missing required section: {heading}")


def extract_labeled_value(content: str, label: str) -> str:
    pattern = re.compile(rf"^- \*\*{re.escape(label)}\*\*: (.+)$", re.MULTILINE)
    match = pattern.search(content)
    if not match:
        raise OperatingVisibilityError(f"missing required labeled bullet: {label}")
    return match.group(1).strip()
```

**Cross-artifact rendering pattern** (`scripts/generate_operating_visibility.py`, lines 305-378):
```python
def render_operating_visibility(
    date_value: str,
    operating_content: str,
    trace_payload: dict,
    governance_content: str,
    latest_summary_content: str,
    execution_path: Path,
    board_path: Path,
    now: datetime,
) -> str:
    require_section(operating_content, "## Overall Conclusion / 一句话总判断")
    require_section(operating_content, "## Top 3 Ranked Opportunities")
    require_section(operating_content, "## 主要风险")
    require_section(operating_content, "## 推荐下一步")
    if "judgment_links" not in trace_payload:
        raise OperatingVisibilityError("decision trace missing judgment_links")
    ...
    return (
        f"# Operating Visibility - {date_value}\n"
        f"- **Primary Anchor**: `{relative(OPERATING_DECISION_PACKAGE_PATH)}`\n"
        f"- **Governance Overlay**: `{relative(GOVERNANCE_STATUS_PATH)}`\n"
        f"- **Freshness Overlay**: `{relative(LATEST_SUMMARY_PATH)}`\n"
        f"- **Supporting Views**: `{relative(execution_path)}`, `{relative(board_path)}`\n"
        f"- **Source Trace**: `{relative(DECISION_TRACE_PATH)}`\n\n"
        ...
    )
```

**What to copy for Phase 6:** If visibility must change, keep it as a supporting consumer of execution/board artifacts, not a primary contract owner. Preserve the existing “read trusted artifacts, render compact summary, validate required headings” pattern.

---

## Shared Patterns

### Derived-artifact purity
**Source:** `scripts/derive_execution_package.py`, lines 83-87; `scripts/derive_board_briefing.py`, lines 78-82
**Apply to:** `scripts/derive_execution_package.py`, `scripts/derive_board_briefing.py`
```python
def assert_derived_only_inputs() -> None:
    if OPERATING_DECISION_PACKAGE_PATH.name != "OPERATING_DECISION_PACKAGE.md":
        raise ...
    if DECISION_TRACE_PATH.name != "decision_package_trace.json":
        raise ...
```
Use the operating package plus trace sidecar as the canonical upstream pair. Do not add raw-signal inputs to Phase 6 derivatives.

### Latest + history snapshot writes
**Source:** `scripts/derive_execution_package.py`, lines 192-203; `scripts/derive_board_briefing.py`, lines 180-191
**Apply to:** all derived generator changes
```python
history_path = history_output_path(date_value)
write_output(EXECUTION_PACKAGE_PATH, latest_output)
write_output(history_path, latest_output)
```
Every render writes both the latest artifact and an identically rendered dated history snapshot.

### Write-path allowlisting
**Source:** `scripts/derive_execution_package.py`, lines 44-57; `scripts/derive_board_briefing.py`, lines 44-57; `scripts/generate_operating_visibility.py`, lines 77-90
**Apply to:** all modified generator scripts
```python
resolved.relative_to(directory.resolve())
raise ...("refusing to write outside allowed directories: {path}")
```
Phase 6 changes should stay inside existing allowed output directories.

### Section-driven validation before rendering
**Source:** `scripts/derive_execution_package.py`, lines 148-156; `scripts/derive_board_briefing.py`, lines 140-146; `scripts/generate_operating_visibility.py`, lines 315-320
**Apply to:** execution and board generators, plus downstream visibility if contract changes
```python
require_section(operating_package, "## Overall Conclusion / 一句话总判断")
require_section(operating_package, "## Top 3 Ranked Opportunities")
...
if '"judgment_links"' not in trace_content:
    raise ...("decision trace missing judgment_links")
```
Add new exact heading checks for the Core 9 execution sections and the refined board signal sections.

### Exact test contracts, not loose snapshots
**Source:** `tests/test_derived_packages.py`, lines 24-44; `tests/test_generate_operating_visibility.py`, lines 53-71, 163-217
**Apply to:** `tests/test_derived_packages.py`
```python
self.assertIn("Target User", result.stdout)
self.assertNotIn("{{", result.stdout)
...
self.assertEqual(positions, sorted(positions), "section order drifted")
```
Phase 6 test updates should assert specific headings, enum values, absence of task-board drift, and section order.

### Supporting-view compatibility
**Source:** `scripts/generate_operating_visibility.py`, lines 346-353; `tests/test_generate_operating_visibility.py`, lines 163-175
**Apply to:** visibility compatibility checks if execution/board contracts change
```python
evidence_backlinks = [
    f"- primary anchor: `{relative(OPERATING_DECISION_PACKAGE_PATH)}`",
    f"- governance overlay: `{relative(GOVERNANCE_STATUS_PATH)}`",
    f"- freshness overlay: `{relative(LATEST_SUMMARY_PATH)}`",
    f"- supporting execution view: `{relative(execution_path)}`",
    f"- supporting board view: `{relative(board_path)}`",
]
```
If execution or board headings change in ways visibility reads, update visibility conservatively as a downstream consumer.

### Cron wiring stays unchanged
**Source:** `orchestration/cron/commands.sh`, lines 118-126
**Apply to:** planning/integration assumptions
```bash
run_decision_packages() {
  python "$ROOT_DIR/scripts/generate_decision_package.py"
  python "$ROOT_DIR/scripts/derive_execution_package.py"
  python "$ROOT_DIR/scripts/derive_board_briefing.py"
  python "$ROOT_DIR/scripts/generate_operating_visibility.py"
}
```
Phase 6 should extend existing scripts in place; do not introduce a new derivation entrypoint.

## No Analog Found

None. All scoped Phase 6 files have direct or strong in-repo analogs.

## Metadata

**Analog search scope:**
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/assets/shared`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/orchestration/cron`

**Files scanned:** 11
**Pattern extraction date:** 2026-04-26
