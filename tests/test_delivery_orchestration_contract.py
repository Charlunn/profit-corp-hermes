import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = ROOT_DIR / "skills" / "library" / "normalized" / "orchestrator-workflow.md"
INPUT_TEMPLATE_PATH = ROOT_DIR / "docs" / "skill-governance" / "templates" / "orchestrator-input-template-v0.2.md"
FORBIDDEN_CHAT_STATE_TERMS = [
    "terminal history",
    "ad-hoc owner routing",
    "freeform chat state",
]
EXPECTED_ROLE_NAMES = [
    "delivery-orchestrator",
    "design-specialist",
    "development-specialist",
    "testing-specialist",
    "git-versioning-specialist",
    "release-readiness-specialist",
]
EXPECTED_STAGE_ORDER = [
    "design",
    "development",
    "testing",
    "git versioning",
    "release readiness",
]
EXPECTED_BUNDLE_FIELDS = [
    "approved brief",
    "template contract",
    ".hermes/shared-backend-guardrails.json",
    ".hermes/project-metadata.json",
    "GSD constraints",
]


class DeliveryOrchestrationContractTests(unittest.TestCase):
    maxDiff = None

    def load_workflow(self) -> str:
        self.assertTrue(WORKFLOW_PATH.exists(), "workflow contract file is missing")
        return WORKFLOW_PATH.read_text(encoding="utf-8")

    def load_input_template(self) -> str:
        self.assertTrue(INPUT_TEMPLATE_PATH.exists(), "input template file is missing")
        return INPUT_TEMPLATE_PATH.read_text(encoding="utf-8")

    def assert_contains_in_order(self, content: str, expected: list[str], *, msg: str) -> None:
        positions: list[int] = []
        for item in expected:
            self.assertIn(item, content, msg=msg)
            positions.append(content.index(item))
        self.assertEqual(positions, sorted(positions), msg)

    def test_d01_d02_single_delivery_orchestrator_and_exact_five_stage_order(self) -> None:
        content = self.load_workflow().lower()
        self.assertIn("delivery-orchestrator", content, "D-01: delivery-orchestrator role must be explicit")
        self.assertEqual(
            content.count("- `delivery-orchestrator`"),
            1,
            "D-01: workflow must define one delivery-orchestrator role entry",
        )
        for role in EXPECTED_ROLE_NAMES[1:]:
            self.assertIn(role, content, f"D-02: missing specialist role {role}")
        self.assert_contains_in_order(
            content,
            EXPECTED_STAGE_ORDER,
            msg="D-02: stage order must stay design -> development -> testing -> git versioning -> release readiness",
        )

    def test_d03_d12_workflow_rejects_chat_only_delivery_memory(self) -> None:
        content = self.load_workflow().lower()
        for forbidden in FORBIDDEN_CHAT_STATE_TERMS:
            self.assertNotIn(
                forbidden,
                content,
                f"D-03/D-12: workflow must not rely on {forbidden}",
            )
        self.assertIn("artifact", content, "D-03: workflow should require artifact-based handoff")

    def test_d04_start_input_bundle_requires_explicit_paths_and_field_names(self) -> None:
        content = self.load_input_template()
        for field in EXPECTED_BUNDLE_FIELDS:
            self.assertIn(field, content, f"D-04: missing required delivery bundle field {field}")
        self.assertIn("approved brief path", content, "D-04: approved brief path must be explicit")
        self.assertIn("template contract path", content, "D-04: template contract path must be explicit")
        self.assertIn("shared-backend guardrails path", content, "D-04: guardrails path must be explicit")
        self.assertIn("project metadata path", content, "D-04: project metadata path must be explicit")
        self.assertIn("gsd constraints source", content.lower(), "D-04: GSD constraints source must be explicit")


if __name__ == "__main__":
    unittest.main()
