import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
CONTRACT_PATH = ROOT_DIR / "docs" / "platform" / "standalone-saas-template-contract.md"
EXPECTED_HEADINGS = [
    "## 1. Authority and source hierarchy",
    "## 2. Registered template summary",
    "## 3. Protected platform layer",
    "## 4. Safe extension layer",
    "## 5. Identity injection contract",
    "## 6. Required runtime and artifact paths",
    "## 7. Conformance gate expectations",
    "## 8. Verification checklist",
]


class TemplateContractTests(unittest.TestCase):
    maxDiff = None

    def load_contract(self) -> str:
        self.assertTrue(CONTRACT_PATH.exists(), "template contract file is missing")
        return CONTRACT_PATH.read_text(encoding="utf-8")

    def assert_heading_order(self, content: str) -> None:
        positions: list[int] = []
        for heading in EXPECTED_HEADINGS:
            self.assertIn(heading, content)
            positions.append(content.index(heading))
        self.assertEqual(positions, sorted(positions), "contract heading order drifted")

    def test_contract_contains_required_headings_in_stable_order(self) -> None:
        self.assert_heading_order(self.load_contract())

    def test_authority_section_states_operational_truth_and_upstream_refs(self) -> None:
        content = self.load_contract()
        self.assertIn("operational source of truth", content)
        self.assertIn("../standalone-saas-template/README.md", content)
        self.assertIn("../standalone-saas-template/ARCHITECTURE.md", content)
        self.assertIn("../standalone-saas-template/BUILDING_RULES.md", content)

    def test_protected_and_safe_layers_and_verification_commands_are_explicit(self) -> None:
        content = self.load_contract()
        self.assertIn("Protected Platform Layer", content)
        self.assertIn("Safe Extension Layer", content)
        self.assertIn("/api/auth/session", content)
        self.assertIn("/api/paypal/checkout", content)
        self.assertIn("/api/paypal/capture", content)
        self.assertIn("src/lib/auth.ts", content)
        self.assertIn("src/lib/paypal.ts", content)
        self.assertIn("src/lib/entitlement.ts", content)
        self.assertIn("src/lib/db-guards.ts", content)
        self.assertIn("supabase/migrations/20260423112500_create_shared_public_tables.sql", content)
        self.assertIn("APP_KEY", content)
        self.assertIn("APP_NAME", content)
        self.assertIn("APP_URL", content)
        self.assertIn("APP_KEY_", content)
        self.assertIn("python -m unittest tests.test_template_registry tests.test_template_contract", content)
        self.assertIn("python scripts/instantiate_template_project.py --help", content)
        self.assertIn("python scripts/check_template_conformance.py --help", content)


if __name__ == "__main__":
    unittest.main()
