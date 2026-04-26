import json
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
REGISTRY_PATH = ROOT_DIR / "assets" / "shared" / "templates" / "standalone-saas-template.json"
EXPECTED_STACK = {
    "next": "15.3.0",
    "react": "19.1.0",
    "react-dom": "19.1.0",
    "@supabase/supabase-js": "^2.49.1",
    "typescript": "^5.6.3",
}
EXPECTED_UPSTREAM = ["README.md", "ARCHITECTURE.md", "BUILDING_RULES.md"]
EXPECTED_CONTRACT_PATH = "docs/platform/standalone-saas-template-contract.md"


class TemplateRegistryTests(unittest.TestCase):
    def load_registry(self) -> dict:
        self.assertTrue(REGISTRY_PATH.exists(), "template registry file is missing")
        return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))

    def test_registry_has_single_template_identity_and_governance_scope(self) -> None:
        payload = self.load_registry()
        self.assertEqual(payload["asset_id"], "standalone-saas-template")
        self.assertEqual(payload["governance_scope"], "single-template-first")

    def test_registry_includes_required_source_stack_and_governance_fields(self) -> None:
        payload = self.load_registry()
        self.assertEqual(payload["source"]["repo_path"], "C:/Users/42236/Desktop/standalone-saas-template")
        self.assertEqual(payload["source"]["intended_use"], "Hermes-approved mini-SaaS project bootstrap")
        self.assertEqual(payload["supported_stack"], EXPECTED_STACK)
        self.assertEqual(payload["governance"]["status"], "canonical")
        self.assertEqual(payload["governance"]["owner"], "Hermes platform")
        self.assertEqual(payload["governance"]["contract_path"], EXPECTED_CONTRACT_PATH)
        self.assertEqual(payload["canonical_contract"], EXPECTED_CONTRACT_PATH)
        self.assertEqual(payload["canonical_refs"]["operational_truth"], EXPECTED_CONTRACT_PATH)

    def test_registry_has_exact_upstream_refs_and_no_multi_template_catalog_shape(self) -> None:
        payload = self.load_registry()
        self.assertEqual(payload["canonical_refs"]["upstream"], EXPECTED_UPSTREAM)
        raw = REGISTRY_PATH.read_text(encoding="utf-8")
        self.assertNotIn("catalog", raw.lower())
        self.assertNotIn("templates[]", raw)


if __name__ == "__main__":
    unittest.main()
