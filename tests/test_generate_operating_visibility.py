import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
VISIBILITY_SCRIPT = ROOT_DIR / "scripts" / "generate_operating_visibility.py"
VISIBILITY_PATH = ROOT_DIR / "assets" / "shared" / "visibility" / "OPERATING_VISIBILITY.md"
VISIBILITY_HISTORY_PATH = (
    ROOT_DIR
    / "assets"
    / "shared"
    / "visibility"
    / "history"
    / "2026-04-25-operating-visibility.md"
)
PRIMARY_ANCHOR = "assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md"
GOVERNANCE_OVERLAY = "assets/shared/governance/GOVERNANCE_STATUS.md"
FRESHNESS_OVERLAY = "assets/shared/external_intelligence/LATEST_SUMMARY.md"
EXECUTION_SUPPORT = "assets/shared/execution_packages/EXECUTION_PACKAGE.md"
BOARD_SUPPORT = "assets/shared/board_briefings/BOARD_BRIEFING.md"
TRACE_PATH = "assets/shared/trace/decision_package_trace.json"
EXPECTED_SECTION_ORDER = [
    "## Status",
    "## Top Alerts",
    "## Current Situation",
    "## Top Opportunities",
    "## Top Risks",
    "## Top 3 Next Actions",
    "## Evidence Backlinks",
]

OPERATING_SOURCE = ROOT_DIR / "assets" / "shared" / "decision_packages" / "OPERATING_DECISION_PACKAGE.md"
TRACE_SOURCE = ROOT_DIR / "assets" / "shared" / "trace" / "decision_package_trace.json"
GOVERNANCE_SOURCE = ROOT_DIR / "assets" / "shared" / "governance" / "GOVERNANCE_STATUS.md"
LATEST_SOURCE = ROOT_DIR / "assets" / "shared" / "external_intelligence" / "LATEST_SUMMARY.md"
EXECUTION_SOURCE = ROOT_DIR / "assets" / "shared" / "execution_packages" / "EXECUTION_PACKAGE.md"
BOARD_SOURCE = ROOT_DIR / "assets" / "shared" / "board_briefings" / "BOARD_BRIEFING.md"


class GenerateOperatingVisibilityTests(unittest.TestCase):
    maxDiff = None

    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VISIBILITY_SCRIPT), *args],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )

    def assert_section_order(self, output: str) -> None:
        positions: list[int] = []
        for section in EXPECTED_SECTION_ORDER:
            self.assertIn(section, output)
            positions.append(output.index(section))
        self.assertEqual(positions, sorted(positions), "section order drifted")

    def extract_section(self, output: str, heading: str) -> str:
        marker = f"\n{heading}\n"
        self.assertIn(marker, output, msg=f"missing section marker for {heading}")
        tail = output.split(marker, 1)[1]
        next_heading = tail.find("\n## ")
        if next_heading == -1:
            return tail.strip()
        return tail[:next_heading].strip()

    def extract_bullets(self, output: str, heading: str) -> list[str]:
        section = self.extract_section(output, heading)
        return [line for line in section.splitlines() if line.startswith("- ")]

    def create_fixture(self, *, healthy: bool, stale: bool, failed_sources: bool) -> tuple[Path, Path, Path, Path, Path, Path, Path, Path, str]:
        temp_dir = Path(tempfile.mkdtemp(prefix="visibility-fixture-"))
        output_root = ROOT_DIR / "assets" / "shared" / "visibility"
        output_root.mkdir(parents=True, exist_ok=True)
        history_root = output_root / "history"
        history_root.mkdir(parents=True, exist_ok=True)
        operating_path = temp_dir / "OPERATING_DECISION_PACKAGE.md"
        trace_path = temp_dir / "decision_package_trace.json"
        governance_path = temp_dir / "GOVERNANCE_STATUS.md"
        latest_path = temp_dir / "LATEST_SUMMARY.md"
        execution_path = temp_dir / "EXECUTION_PACKAGE.md"
        board_path = temp_dir / "BOARD_BRIEFING.md"
        latest_output = output_root / "OPERATING_VISIBILITY.md"
        history_path = history_root / "2026-04-25-operating-visibility.md"

        operating_path.write_text(OPERATING_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
        trace_path.write_text(TRACE_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
        execution_path.write_text(EXECUTION_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")
        board_path.write_text(BOARD_SOURCE.read_text(encoding="utf-8"), encoding="utf-8")

        if healthy:
            governance_text = """# Governance Status
- **Authority Source**: `assets/shared/governance/governance_events.jsonl`
- **Decision Package Anchor**: `assets/shared/decision_packages/OPERATING_DECISION_PACKAGE.md`
- **Trace Anchor**: `assets/shared/trace/decision_package_trace.json`

This latest view is derived from the append-only governance JSONL stream.

## Pending Approvals
- None

## Active Blocks
- None

## Recent Approvals
- None

## Recent Rejections
- None

## Recent Overrides
- None
"""
        else:
            governance_text = GOVERNANCE_SOURCE.read_text(encoding="utf-8")
        governance_path.write_text(governance_text, encoding="utf-8")

        latest_text = LATEST_SOURCE.read_text(encoding="utf-8")
        if failed_sources:
            latest_text = latest_text.replace("- **failed_source_count**: 0", "- **failed_source_count**: 2")
            latest_text = latest_text.replace("- **failed_sources**: none", "- **failed_sources**: web-discovery-default-1, web-discovery-default-2")
        latest_path.write_text(latest_text, encoding="utf-8")

        now_value = "2026-04-27T12:00:00Z" if stale else "2026-04-25T12:00:00Z"
        return (
            operating_path,
            trace_path,
            governance_path,
            latest_path,
            execution_path,
            board_path,
            latest_output,
            history_path,
            now_value,
        )

    def script_args_for_fixture(self, fixture: tuple[Path, Path, Path, Path, Path, Path, Path, Path, str]) -> list[str]:
        operating_path, trace_path, governance_path, latest_path, execution_path, board_path, latest_output, history_path, now_value = fixture
        return [
            "--operating-package-path", str(operating_path),
            "--trace-path", str(trace_path),
            "--governance-status-path", str(governance_path),
            "--latest-summary-path", str(latest_path),
            "--now", now_value,
        ]

    def write_mode_args_for_fixture(self, fixture: tuple[Path, Path, Path, Path, Path, Path, Path, Path, str]) -> list[str]:
        operating_path, trace_path, governance_path, latest_path, execution_path, board_path, latest_output, history_path, now_value = fixture
        return [
            "--operating-package-path", str(operating_path),
            "--trace-path", str(trace_path),
            "--governance-status-path", str(governance_path),
            "--latest-summary-path", str(latest_path),
            "--execution-package-path", str(execution_path),
            "--board-briefing-path", str(board_path),
            "--output-path", str(latest_output),
            "--history-path", str(history_path),
            "--now", now_value,
        ]

    def test_d07_d08_d09_dry_run_contains_exact_provenance_header(self) -> None:
        fixture = self.create_fixture(healthy=True, stale=False, failed_sources=False)
        result = self.run_script(*self.script_args_for_fixture(fixture), "--dry-run")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout
        self.assertIn("# Operating Visibility - 2026-04-25", output)
        self.assertIn(f"- **Primary Anchor**: `{PRIMARY_ANCHOR}`", output)
        self.assertIn(f"- **Governance Overlay**: `{GOVERNANCE_OVERLAY}`", output)
        self.assertIn(f"- **Freshness Overlay**: `{FRESHNESS_OVERLAY}`", output)
        self.assertIn(f"- **Supporting Views**: `{EXECUTION_SUPPORT}`, `{BOARD_SUPPORT}`", output)
        self.assertIn(f"- **Source Trace**: `{TRACE_PATH}`", output)
        self.assert_section_order(output)

    def test_d01_d03_healthy_render_is_calm_compact_and_alert_free(self) -> None:
        fixture = self.create_fixture(healthy=True, stale=False, failed_sources=False)
        result = self.run_script(*self.script_args_for_fixture(fixture), "--dry-run")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout
        status_section = self.extract_section(output, "## Status")
        alerts_section = self.extract_section(output, "## Top Alerts")
        self.assertIn("HEALTHY", status_section)
        self.assertEqual(alerts_section, "None.")
        self.assertNotIn("ACTION REQUIRED", status_section)
        self.assertLessEqual(len(output.splitlines()), 40, "healthy render should stay compact")

    def test_d02_blocked_pending_failed_and_stale_conditions_are_promoted_to_top_alerts(self) -> None:
        fixture = self.create_fixture(healthy=False, stale=True, failed_sources=True)
        result = self.run_script(*self.script_args_for_fixture(fixture), "--dry-run")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout
        alerts = self.extract_section(output, "## Top Alerts")
        self.assertIn("blocked", alerts.lower())
        self.assertIn("pending", alerts.lower())
        self.assertIn("failed", alerts.lower())
        self.assertIn("stale", alerts.lower())
        self.assertIn("ACTION REQUIRED", self.extract_section(output, "## Status"))

    def test_d04_d05_d06_top_3_actions_are_capped_and_evidence_bound(self) -> None:
        fixture = self.create_fixture(healthy=False, stale=True, failed_sources=True)
        result = self.run_script(*self.script_args_for_fixture(fixture), "--dry-run")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout
        actions = self.extract_bullets(output, "## Top 3 Next Actions")
        self.assertLessEqual(len(actions), 3)
        self.assertGreater(len(actions), 0)
        for action in actions:
            self.assertNotIn("Owner:", action)
            self.assertNotIn("Backlog", action)
            has_trace = "trace: judgment_id=" in action
            has_governance_source = GOVERNANCE_OVERLAY in action
            has_freshness_source = FRESHNESS_OVERLAY in action
            self.assertTrue(
                has_trace or has_governance_source or has_freshness_source,
                msg=f"action missing trusted evidence binding: {action}",
            )

    def test_write_mode_creates_latest_and_history_with_identical_content(self) -> None:
        fixture = self.create_fixture(healthy=False, stale=True, failed_sources=True)
        args = self.write_mode_args_for_fixture(fixture)
        result = self.run_script(*args, "--date", "2026-04-25")
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        _, _, _, _, _, _, latest_output, history_output, _ = fixture
        self.assertTrue(latest_output.exists(), "latest visibility artifact missing")
        self.assertTrue(history_output.exists(), "visibility history snapshot missing")

        latest_text = latest_output.read_text(encoding="utf-8")
        history_text = history_output.read_text(encoding="utf-8")
        self.assertTrue(latest_text.strip(), "latest visibility artifact is empty")
        self.assertEqual(latest_text, history_text)
        self.assert_section_order(latest_text)
        self.assertIn("## Top 3 Next Actions", latest_text)


if __name__ == "__main__":
    unittest.main()
