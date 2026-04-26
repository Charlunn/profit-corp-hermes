import subprocess
import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
EXECUTION_SCRIPT = ROOT_DIR / "scripts" / "derive_execution_package.py"
BOARD_SCRIPT = ROOT_DIR / "scripts" / "derive_board_briefing.py"
EXECUTION_PATH = ROOT_DIR / "assets" / "shared" / "execution_packages" / "EXECUTION_PACKAGE.md"
BOARD_PATH = ROOT_DIR / "assets" / "shared" / "board_briefings" / "BOARD_BRIEFING.md"
EXECUTION_HISTORY_PATH = ROOT_DIR / "assets" / "shared" / "execution_packages" / "history" / "2026-04-25-execution-package.md"
BOARD_HISTORY_PATH = ROOT_DIR / "assets" / "shared" / "board_briefings" / "history" / "2026-04-25-board-briefing.md"
CURRENT_EXECUTION_SECTION_ORDER = [
    "## Goal",
    "## Scope Boundary",
    "## Target User",
    "## MVP Framing",
    "## Dependencies",
    "## Key Risks",
    "## Acceptance Gate",
    "## Recommended First Actions",
    "## Handoff Target",
]
CURRENT_BOARD_SECTION_ORDER = [
    "## Top 3",
    "## Key Numbers / Signals",
    "## Major Risk",
    "## Required Attention",
]
BANNED_TASK_BOARD_TERMS = [
    "Backlog",
    "Task Board",
    "Approval Ladder",
    "Sprint",
    "TODO",
]
BANNED_COLLABORATION_HEADINGS = [
    "## Team Queue",
    "## Assignment Matrix",
    "## Workflow Routing",
]
EXPECTED_EXECUTION_METADATA = [
    "Owner",
    "Primary Role",
    "Handoff Target",
    "Readiness Status",
]
EXPECTED_READINESS_ENUM = {"ready", "blocked", "needs-input"}


class DerivedPackagesTests(unittest.TestCase):
    maxDiff = None

    def run_script(self, script: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *args],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )

    def extract_dry_run_document(self, output: str, marker: str) -> str:
        if marker not in output:
            return output
        tail = output.split(marker, 1)[1].lstrip()
        next_marker = tail.find("\n=== ")
        if next_marker == -1:
            return tail.strip()
        return tail[:next_marker].strip()

    def assert_section_order(self, output: str, expected_sections: list[str]) -> None:
        positions: list[int] = []
        for section in expected_sections:
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

    def assert_latest_history_match(self, latest_path: Path, history_path: Path, required_section: str) -> None:
        self.assertTrue(latest_path.exists(), f"latest artifact missing: {latest_path}")
        self.assertTrue(history_path.exists(), f"history snapshot missing: {history_path}")

        latest_text = latest_path.read_text(encoding="utf-8")
        history_text = history_path.read_text(encoding="utf-8")
        self.assertTrue(latest_text.strip(), f"latest artifact is empty: {latest_path}")
        self.assertEqual(latest_text, history_text)
        self.assertIn(required_section, latest_text)

    def extract_labeled_value(self, output: str, label: str) -> str:
        marker = f"- **{label}**: "
        for line in output.splitlines():
            if line.startswith(marker):
                return line[len(marker):].strip()
        self.fail(f"missing labeled value: {label}")

    def assert_paired_sections(self, output: str, left_heading: str, right_heading: str) -> None:
        left_bullets = self.extract_bullets(output, left_heading)
        right_bullets = self.extract_bullets(output, right_heading)
        self.assertEqual(len(left_bullets), len(right_bullets))
        for index, bullet in enumerate(right_bullets, start=1):
            self.assertTrue(bullet.startswith(f"- Risk {index} gate:"), msg=f"unexpected acceptance gate format: {bullet}")

    def assert_absent_terms(self, output: str, banned_terms: list[str]) -> None:
        for term in banned_terms:
            self.assertNotIn(term, output)

    def test_execution_dry_run_renders_required_fields(self) -> None:
        result = self.run_script(EXECUTION_SCRIPT, "--dry-run")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        document = self.extract_dry_run_document(result.stdout, "=== EXECUTION_PACKAGE.md ===")
        self.assertIn("OPERATING_DECISION_PACKAGE.md", document)
        self.assertIn("decision_package_trace.json", document)
        self.assertIn("founder/operator", document)
        self.assertNotIn("待主包补充", document)
        self.assertNotIn("{{", document)
        self.assertNotIn("## Kickoff Focus", document)
        self.assert_section_order(document, CURRENT_EXECUTION_SECTION_ORDER)
        for label in EXPECTED_EXECUTION_METADATA:
            self.assertIn(f"- **{label}**:", document)
        readiness = self.extract_labeled_value(document, "Readiness Status")
        self.assertIn(readiness, EXPECTED_READINESS_ENUM)
        self.assert_paired_sections(document, "## Key Risks", "## Acceptance Gate")
        for heading in CURRENT_EXECUTION_SECTION_ORDER:
            bullets = self.extract_bullets(document, heading)
            self.assertGreaterEqual(len(bullets), 1)
            self.assertLessEqual(len(bullets), 3)
        self.assert_absent_terms(document, BANNED_TASK_BOARD_TERMS)
        self.assert_absent_terms(document, BANNED_COLLABORATION_HEADINGS)

    def test_board_dry_run_renders_required_fields(self) -> None:
        result = self.run_script(BOARD_SCRIPT, "--dry-run")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        document = self.extract_dry_run_document(result.stdout, "=== BOARD_BRIEFING.md ===")
        self.assertIn("Top 3", document)
        self.assertIn("Major Risk", document)
        self.assertIn("Required Attention", document)
        self.assertIn("OPERATING_DECISION_PACKAGE.md", document)
        self.assertIn("IDEA-001", document)
        self.assertNotIn("{{", document)
        self.assert_section_order(document, CURRENT_BOARD_SECTION_ORDER)
        required_attention_bullets = self.extract_bullets(document, "## Required Attention")
        self.assertGreaterEqual(len(required_attention_bullets), 1)
        self.assertLessEqual(len(required_attention_bullets), 1)
        self.assert_absent_terms(document, BANNED_COLLABORATION_HEADINGS)

    def test_write_mode_updates_latest_and_history(self) -> None:
        execution_result = self.run_script(EXECUTION_SCRIPT, "--date", "2026-04-25")
        board_result = self.run_script(BOARD_SCRIPT, "--date", "2026-04-25")
        self.assertEqual(execution_result.returncode, 0, msg=execution_result.stderr)
        self.assertEqual(board_result.returncode, 0, msg=board_result.stderr)

        self.assert_latest_history_match(EXECUTION_PATH, EXECUTION_HISTORY_PATH, "## Goal")
        self.assert_latest_history_match(BOARD_PATH, BOARD_HISTORY_PATH, "## Required Attention")

        execution_text = EXECUTION_PATH.read_text(encoding="utf-8")
        board_text = BOARD_PATH.read_text(encoding="utf-8")
        self.assert_section_order(execution_text, CURRENT_EXECUTION_SECTION_ORDER)
        self.assertIn("OPERATING_DECISION_PACKAGE.md", execution_text)
        self.assertIn("Readiness Status", execution_text)
        self.assertIn("founder/operator", execution_text)
        self.assertIn("IDEA-001", execution_text)
        self.assertNotIn("## Kickoff Focus", execution_text)
        self.assertNotIn("{{", execution_text)
        self.assertIn("OPERATING_DECISION_PACKAGE.md", board_text)
        self.assertIn("Top 3", board_text)
        self.assertIn("Major Risk", board_text)
        self.assertIn("Required Attention", board_text)
        self.assertIn("IDEA-001", board_text)
        self.assertIn("medium", board_text)
        self.assertNotIn("{{", board_text)
        self.assert_section_order(board_text, CURRENT_BOARD_SECTION_ORDER)


if __name__ == "__main__":
    unittest.main()
