import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
STAGE_HANDOFF_TEMPLATE_PATH = ROOT_DIR / "docs" / "skill-governance" / "templates" / "stage-handoff-template-v0.2.md"
FINAL_DELIVERY_TEMPLATE_PATH = ROOT_DIR / "docs" / "skill-governance" / "templates" / "final-delivery-template-v0.2.md"
FORBIDDEN_CHAT_STATE_TERMS = [
    "terminal history",
    "ad-hoc owner routing",
    "freeform chat state",
]
STAGE_HEADINGS = [
    "## 1) Stage Summary",
    "## 2) Outputs Produced",
    "## 3) Evidence Links",
    "## 4) Gate Decision",
    "## 5) Open Risks",
    "## 6) Next Stage Input",
]
FINAL_HEADINGS = [
    "## 1) End-to-end Summary",
    "## 2) Impact Surface",
    "## 3) Test & Verification Evidence",
    "## 4) Gate Status Snapshot",
    "## 5) Rollback Plan",
    "## 6) Release Recommendation",
]
STAGE_METADATA_FIELDS = ["`run_id`", "`role`", "`stage`", "`scope_status`", "`next_stage`"]
FINAL_METADATA_FIELDS = ["`run_id`", "`role`", "`stage`", "`scope_status`"]


class DeliveryHandoffContractTests(unittest.TestCase):
    maxDiff = None

    def load_stage_template(self) -> str:
        self.assertTrue(STAGE_HANDOFF_TEMPLATE_PATH.exists(), "stage handoff template is missing")
        return STAGE_HANDOFF_TEMPLATE_PATH.read_text(encoding="utf-8")

    def load_final_template(self) -> str:
        self.assertTrue(FINAL_DELIVERY_TEMPLATE_PATH.exists(), "final delivery template is missing")
        return FINAL_DELIVERY_TEMPLATE_PATH.read_text(encoding="utf-8")

    def assert_heading_order(self, content: str, headings: list[str], *, msg: str) -> None:
        positions: list[int] = []
        for heading in headings:
            self.assertIn(heading, content, msg)
            positions.append(content.index(heading))
        self.assertEqual(positions, sorted(positions), msg)

    def test_d05_stage_handoff_keeps_required_sections_and_delivery_metadata(self) -> None:
        content = self.load_stage_template()
        self.assert_heading_order(content, STAGE_HEADINGS, msg="D-05: stage handoff section order drifted")
        for field in STAGE_METADATA_FIELDS:
            self.assertIn(field, content, f"D-05: stage handoff missing metadata field {field}")
        self.assertIn("`gate_decision`: PASS | FAIL", content, "D-05: stage handoff must keep Gate Decision semantics")

    def test_d06_final_delivery_keeps_required_sections_and_delivery_metadata(self) -> None:
        content = self.load_final_template()
        self.assert_heading_order(content, FINAL_HEADINGS, msg="D-06: final delivery section order drifted")
        for field in FINAL_METADATA_FIELDS:
            self.assertIn(field, content, f"D-06: final delivery missing metadata field {field}")
        self.assertIn("Release Recommendation", content, "D-06: final delivery must preserve release recommendation section")

    def test_d03_d12_handoff_templates_reject_chat_only_language(self) -> None:
        combined = (self.load_stage_template() + "\n" + self.load_final_template()).lower()
        for forbidden in FORBIDDEN_CHAT_STATE_TERMS:
            self.assertNotIn(
                forbidden,
                combined,
                f"D-03/D-12: handoff templates must not rely on {forbidden}",
            )
        self.assertIn("evidence", combined, "D-03/D-12: handoff templates must remain artifact-first")


if __name__ == "__main__":
    unittest.main()
