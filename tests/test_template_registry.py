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
EXPECTED_SHARED_TABLES = ["users", "orders", "payments", "subscriptions"]
EXPECTED_PROTECTED_PATHS = [
    "src/lib/auth.ts",
    "src/lib/supabase-browser.ts",
    "src/lib/supabase-server.ts",
    "src/lib/paypal.ts",
    "src/lib/entitlement.ts",
    "src/lib/db-guards.ts",
    "src/app/api/auth/session/route.ts",
    "src/app/api/paypal/checkout/route.ts",
    "src/app/api/paypal/capture/route.ts",
    "supabase/migrations/20260423112500_create_shared_public_tables.sql",
]


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

    def test_registry_declares_shared_backend_guardrails(self) -> None:
        payload = self.load_registry()
        shared_backend = payload["shared_backend"]
        self.assertEqual(shared_backend["mode"], "shared-supabase")
        self.assertFalse(shared_backend["allow_independent_backend"])
        self.assertEqual(shared_backend["shared_tables"], EXPECTED_SHARED_TABLES)
        self.assertEqual(shared_backend["business_table_prefix"], "APP_KEY_")
        self.assertEqual(shared_backend["protected_paths"], EXPECTED_PROTECTED_PATHS)
        self.assertEqual(shared_backend["client_write_blocked_tables"], EXPECTED_SHARED_TABLES)
        self.assertIn("shared backend", shared_backend["description"])


if __name__ == "__main__":
    unittest.main()
