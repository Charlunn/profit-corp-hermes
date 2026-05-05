import importlib.util
import json
import shutil
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "qualify_project_candidates.py"


def load_module(module_name: str, script_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class QualificationGateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module("qualify_project_candidates", SCRIPT_PATH)

    def fixture_files(self, root: Path, *, stale=False, vague=False, infeasible=False, missing_market=False):
        triage_path = root / "prioritized_signals.json"
        signals_path = root / "signals.jsonl"
        observed_at = "2026-05-04T10:00:00Z"
        if stale:
            observed_at = "2026-04-29T10:00:00Z"
        triage_payload = {
            "prioritized_signals": [
                {
                    "idea_id": "IDEA-001",
                    "title": "Lead Qualification Copilot",
                    "problem_summary": "operators lose deals because lead follow-up is manual and slow" if not vague else "developer tools",
                    "target_user": "Revenue operators" if not vague else "Developers and technical operators",
                    "evidence_links": ["https://example.com/pain"],
                    "score_components": {},
                    "estimated_mvp_hours": 16,
                    "total_score": 80,
                    "rank": 1,
                    "generated_from": {"history_path": "history/signals.jsonl"},
                    "lead_signal_id": "sig-1",
                    "signal_ids": ["sig-1"],
                    "market_pricing_proof": {
                        "competitor_links": [] if missing_market else ["https://example.com/competitor"],
                        "pricing_links": [] if missing_market else ["https://example.com/pricing"],
                    },
                    "feasibility": {
                        "requires_protected_layer_change": infeasible,
                        "requires_custom_backend": False,
                    },
                }
            ]
        }
        signal_row = {
            "signal_id": "sig-1",
            "collected_at": observed_at,
            "published_at": "",
            "url": "https://example.com/pain",
        }
        triage_path.write_text(json.dumps(triage_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        signals_path.write_text(json.dumps(signal_row, ensure_ascii=False) + "\n", encoding="utf-8")
        return triage_path, signals_path

    def test_passes_when_fresh_specific_feasible_and_market_backed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            triage, signals = self.fixture_files(Path(tmp))
            bundle = self.module.evaluate_candidates_bundle(
                triage,
                signals,
                current_time=datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc),
            )
            candidate = bundle["candidates"][0]
            self.assertEqual(candidate["verdict"], "passed")
            self.assertEqual(candidate["reason_codes"], [])

    def test_blocks_stale_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            triage, signals = self.fixture_files(Path(tmp), stale=True)
            bundle = self.module.evaluate_candidates_bundle(
                triage,
                signals,
                current_time=datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc),
            )
            self.assertIn("stale_required_evidence", bundle["candidates"][0]["reason_codes"])

    def test_blocks_vague_non_user_facing_pain(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            triage, signals = self.fixture_files(Path(tmp), vague=True)
            bundle = self.module.evaluate_candidates_bundle(
                triage,
                signals,
                current_time=datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc),
            )
            reasons = bundle["candidates"][0]["reason_codes"]
            self.assertIn("pain_not_user_facing", reasons)
            self.assertIn("pain_too_vague", reasons)

    def test_blocks_infeasible_or_missing_market_proof(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            triage, signals = self.fixture_files(Path(tmp), infeasible=True, missing_market=True)
            bundle = self.module.evaluate_candidates_bundle(
                triage,
                signals,
                current_time=datetime(2026, 5, 4, 12, 0, tzinfo=timezone.utc),
            )
            reasons = bundle["candidates"][0]["reason_codes"]
            self.assertIn("template_fit_failed", reasons)
            self.assertIn("missing_market_pricing_proof", reasons)


if __name__ == "__main__":
    unittest.main()
