import importlib.util
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
COMMON_PATH = ROOT_DIR / "scripts" / "qualification_common.py"


def load_module(module_name: str, script_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class QualificationContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module("qualification_common", COMMON_PATH)

    def test_reason_code_registry_is_locked(self) -> None:
        self.assertIn("stale_required_evidence", self.module.ALLOWED_BLOCK_REASONS)
        self.assertIn("missing_market_pricing_proof", self.module.ALLOWED_BLOCK_REASONS)
        with self.assertRaises(self.module.QualificationError):
            self.module.validate_reason("not-a-real-reason")

    def test_summary_renderer_includes_reason_coded_verdicts(self) -> None:
        markdown = self.module.render_summary(
            {
                "generated_at": "2026-05-04T12:00:00Z",
                "candidates": [
                    {"idea_id": "IDEA-001", "verdict": "blocked", "reason_codes": ["stale_required_evidence"]},
                    {"idea_id": "IDEA-002", "verdict": "passed", "reason_codes": []},
                ],
            }
        )
        self.assertIn("IDEA-001", markdown)
        self.assertIn("stale_required_evidence", markdown)
        self.assertIn("IDEA-002", markdown)
        self.assertIn("passed", markdown)


if __name__ == "__main__":
    unittest.main()
