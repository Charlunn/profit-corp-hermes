import re
import subprocess
import sys
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
ROADMAP_PATH = ROOT_DIR / ".planning" / "ROADMAP.md"
EXPECTED_PHASES = ["7", "8", "9", "10", "11", "12"]


def extract_phase_block(text: str, phase: str) -> str | None:
    pattern = re.compile(
        rf"^### Phase {phase}: .*?(?=^### Phase \d+: |^## [^#]|\Z)",
        re.MULTILINE | re.DOTALL,
    )
    match = pattern.search(text)
    return match.group(0) if match else None


class RoadmapFormatTests(unittest.TestCase):
    def test_v11_phase_details_use_parser_safe_heading_format(self) -> None:
        text = ROADMAP_PATH.read_text(encoding="utf-8")
        for phase in EXPECTED_PHASES:
            block = extract_phase_block(text, phase)
            self.assertIsNotNone(block, msg=f"Phase {phase} detail section must use a markdown heading")
            assert block is not None
            self.assertIn("**Goal:** ", block, msg=f"Phase {phase} must expose a bold Goal line under the heading")
            self.assertIn("**Requirements:** ", block, msg=f"Phase {phase} must expose a bold Requirements line under the heading")
            self.assertIn("**Success Criteria:**", block, msg=f"Phase {phase} must expose a bold Success Criteria line under the heading")

    def test_gsd_sdk_can_resolve_phase_9_from_current_roadmap(self) -> None:
        result = subprocess.run(
            ["gsd-sdk.cmd", "query", "roadmap.get-phase", "9"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            shell=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"found": true', result.stdout)
        self.assertIn('"phase_number": "9"', result.stdout)

    def test_gsd_sdk_phase_op_init_recognizes_phase_9(self) -> None:
        result = subprocess.run(
            ["gsd-sdk.cmd", "query", "init.phase-op", "9"],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
            shell=False,
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn('"phase_found": true', result.stdout)
        self.assertIn('"phase_number": "9"', result.stdout)
        self.assertIn('"padded_phase": "09"', result.stdout)


if __name__ == "__main__":
    unittest.main()
