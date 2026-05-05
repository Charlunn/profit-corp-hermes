import subprocess
import sys
import unittest
from pathlib import Path
import json
import tempfile
import shutil


ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "generate_decision_package.py"
OPERATING_PATH = ROOT_DIR / "assets" / "shared" / "decision_packages" / "OPERATING_DECISION_PACKAGE.md"
TRACE_PATH = ROOT_DIR / "assets" / "shared" / "trace" / "decision_package_trace.json"
HISTORY_PATH = ROOT_DIR / "assets" / "shared" / "decision_packages" / "history" / "2026-04-25-operating-decision-package.md"
QUALIFICATION_BUNDLE_PATH = ROOT_DIR / "assets" / "shared" / "qualification" / "latest" / "qualification_bundle.json"


class GenerateDecisionPackageTests(unittest.TestCase):
    def addCleanupPath(self, path: Path) -> None:
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))

    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )

    def load_module(self):
        import importlib.util

        spec = importlib.util.spec_from_file_location("generate_decision_package", SCRIPT_PATH)
        if spec is None or spec.loader is None:
            raise AssertionError("unable to load generate_decision_package")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def ensure_passed_qualification_fixture(self) -> None:
        qualification_payload = {
            "generated_at": "2026-05-04T12:00:00Z",
            "candidates": [
                {"idea_id": "IDEA-001", "verdict": "passed", "reason_codes": []},
                {"idea_id": "IDEA-002", "verdict": "passed", "reason_codes": []},
            ],
        }
        QUALIFICATION_BUNDLE_PATH.parent.mkdir(parents=True, exist_ok=True)
        QUALIFICATION_BUNDLE_PATH.write_text(
            json.dumps(qualification_payload, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    def test_dry_run_renders_required_sections(self) -> None:
        self.ensure_passed_qualification_fixture()
        result = self.run_script("--dry-run")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("一句话总判断", result.stdout)
        self.assertIn("Top 3 Ranked Opportunities", result.stdout)
        self.assertIn("## 关键机会", result.stdout)
        self.assertIn("## 主要风险", result.stdout)
        self.assertIn("## 推荐下一步", result.stdout)

    def test_write_mode_updates_latest_history_and_trace(self) -> None:
        self.ensure_passed_qualification_fixture()
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

    def test_decision_package_blocks_missing_or_failed_qualification(self) -> None:
        module = self.load_module()
        prioritized = [
            {
                "idea_id": "IDEA-001",
                "title": "Lead Capture Copilot",
                "problem_summary": "Operators lose deals because lead follow-up is manual and slow.",
                "target_user": "Revenue operators",
                "evidence_links": ["https://example.com/pain"],
                "score_components": {},
                "estimated_mvp_hours": 12,
                "total_score": 81,
                "rank": 1,
                "generated_from": {"history_path": "signals.jsonl"},
            }
        ]
        with self.assertRaises(module.DecisionPackageError):
            module.filter_qualified_prioritized(prioritized, {"candidates": []})
        with self.assertRaises(module.DecisionPackageError):
            module.filter_qualified_prioritized(
                prioritized,
                {"candidates": [{"idea_id": "IDEA-001", "verdict": "blocked", "reason_codes": ["missing_market_pricing_proof"]}]},
            )

    def test_decision_package_accepts_passed_qualification(self) -> None:
        module = self.load_module()
        prioritized = [
            {
                "idea_id": "IDEA-001",
                "title": "Lead Capture Copilot",
                "problem_summary": "Operators lose deals because lead follow-up is manual and slow.",
                "target_user": "Revenue operators",
                "evidence_links": ["https://example.com/pain"],
                "score_components": {},
                "estimated_mvp_hours": 12,
                "total_score": 81,
                "rank": 1,
                "generated_from": {"history_path": "signals.jsonl"},
            }
        ]
        qualified = module.filter_qualified_prioritized(
            prioritized,
            {"candidates": [{"idea_id": "IDEA-001", "verdict": "passed", "reason_codes": []}]},
        )
        self.assertEqual(len(qualified), 1)
        self.assertEqual(qualified[0]["qualification"]["verdict"], "passed")


if __name__ == "__main__":
    unittest.main()
