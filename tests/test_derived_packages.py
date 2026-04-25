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


class DerivedPackagesTests(unittest.TestCase):
    def run_script(self, script: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *args],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )

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

    def test_board_dry_run_renders_required_fields(self) -> None:
        result = self.run_script(BOARD_SCRIPT, "--dry-run")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("Top 3", result.stdout)
        self.assertIn("Major Risk", result.stdout)
        self.assertIn("Required Attention", result.stdout)
        self.assertIn("OPERATING_DECISION_PACKAGE.md", result.stdout)
        self.assertIn("IDEA-001", result.stdout)
        self.assertNotIn("{{", result.stdout)

    def test_write_mode_updates_latest_and_history(self) -> None:
        execution_result = self.run_script(EXECUTION_SCRIPT, "--date", "2026-04-25")
        board_result = self.run_script(BOARD_SCRIPT, "--date", "2026-04-25")
        self.assertEqual(execution_result.returncode, 0, msg=execution_result.stderr)
        self.assertEqual(board_result.returncode, 0, msg=board_result.stderr)

        self.assertTrue(EXECUTION_PATH.exists(), "latest execution package missing")
        self.assertTrue(BOARD_PATH.exists(), "latest board briefing missing")
        self.assertTrue(EXECUTION_HISTORY_PATH.exists(), "execution history snapshot missing")
        self.assertTrue(BOARD_HISTORY_PATH.exists(), "board history snapshot missing")

        execution_text = EXECUTION_PATH.read_text(encoding="utf-8")
        board_text = BOARD_PATH.read_text(encoding="utf-8")
        self.assertIn("OPERATING_DECISION_PACKAGE.md", execution_text)
        self.assertIn("Target User", execution_text)
        self.assertIn("MVP", execution_text)
        self.assertIn("IDEA-001", execution_text)
        self.assertIn("medium", execution_text)
        self.assertNotIn("{{", execution_text)
        self.assertNotIn("Owner", execution_text)
        self.assertNotIn("Dependency", execution_text)
        self.assertIn("OPERATING_DECISION_PACKAGE.md", board_text)
        self.assertIn("Top 3", board_text)
        self.assertIn("Major Risk", board_text)
        self.assertIn("Required Attention", board_text)
        self.assertIn("IDEA-001", board_text)
        self.assertIn("medium", board_text)
        self.assertNotIn("{{", board_text)


if __name__ == "__main__":
    unittest.main()
