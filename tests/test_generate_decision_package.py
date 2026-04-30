import subprocess
import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "generate_decision_package.py"
OPERATING_PATH = ROOT_DIR / "assets" / "shared" / "decision_packages" / "OPERATING_DECISION_PACKAGE.md"
TRACE_PATH = ROOT_DIR / "assets" / "shared" / "trace" / "decision_package_trace.json"
HISTORY_PATH = ROOT_DIR / "assets" / "shared" / "decision_packages" / "history" / "2026-04-25-operating-decision-package.md"


class GenerateDecisionPackageTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )

    def test_dry_run_renders_required_sections(self) -> None:
        result = self.run_script("--dry-run")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("一句话总判断", result.stdout)
        self.assertIn("Top 3 Ranked Opportunities", result.stdout)
        self.assertIn("## 关键机会", result.stdout)
        self.assertIn("## 主要风险", result.stdout)
        self.assertIn("## 推荐下一步", result.stdout)

    def test_write_mode_updates_latest_history_and_trace(self) -> None:
        result = self.run_script("--date", "2026-04-25")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertTrue(OPERATING_PATH.exists(), "latest operating package missing")
        self.assertTrue(HISTORY_PATH.exists(), "history operating package missing")
        self.assertTrue(TRACE_PATH.exists(), "trace sidecar missing")

        package_text = OPERATING_PATH.read_text(encoding="utf-8")
        trace_text = TRACE_PATH.read_text(encoding="utf-8")
        self.assertIn("prioritized_signals.json", package_text)
        self.assertIn("CEO_RANKING.md", package_text)
        self.assertIn('"judgment_links"', trace_text)
        self.assertIn('"idea_id"', trace_text)
        self.assertIn('"role_artifacts"', trace_text)


if __name__ == "__main__":
    unittest.main()
