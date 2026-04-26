import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.template_contract_common import (
    GENERATED_WORKSPACES_DIR,
    TemplateContractError,
    build_identity_payload,
    ensure_allowed_workspace_path,
    load_registry,
    require_asset,
    validate_identity,
)


SCRIPT_PATH = ROOT_DIR / "scripts" / "instantiate_template_project.py"
REGISTRY_PATH = ROOT_DIR / "assets" / "shared" / "templates" / "standalone-saas-template.json"
CONTRACT_PATH = ROOT_DIR / "docs" / "platform" / "standalone-saas-template-contract.md"
TEMPLATE_SOURCE = Path("C:/Users/42236/Desktop/standalone-saas-template")
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


class TemplateContractCommonTests(unittest.TestCase):
    def test_validate_identity_rejects_invalid_values(self) -> None:
        with self.assertRaises(TemplateContractError):
            validate_identity("", "Lead Capture", "https://lead.example.com")

        with self.assertRaises(TemplateContractError):
            validate_identity("LeadCapture", "Lead Capture", "https://lead.example.com")

        with self.assertRaises(TemplateContractError):
            validate_identity("lead_capture", "Lead Capture", "lead.example.com")

    def test_validate_identity_and_build_payload_return_expected_values(self) -> None:
        validated = validate_identity("lead_capture", "Lead Capture", "https://lead.example.com")
        self.assertEqual(
            validated,
            {
                "APP_KEY": "lead_capture",
                "APP_NAME": "Lead Capture",
                "APP_URL": "https://lead.example.com",
            },
        )

        payload = build_identity_payload("lead_capture", "Lead Capture", "https://lead.example.com")
        self.assertEqual(
            payload,
            {
                "APP_KEY": "lead_capture",
                "APP_NAME": "Lead Capture",
                "APP_URL": "https://lead.example.com",
                "PAYPAL_BRAND_NAME": "Lead Capture",
                "APP_DEFINITION_NAME": "Lead Capture",
                "APP_DEFINITION_URL": "https://lead.example.com",
                "APP_DEFINITION_PRODUCT_ID": "lead_capture_default_offer",
                "APP_DEFINITION_DESCRIPTION": "Lead Capture access",
            },
        )

    def test_registry_load_and_workspace_guard_follow_phase_contract(self) -> None:
        registry = load_registry(REGISTRY_PATH)
        asset = require_asset(registry)
        self.assertEqual(asset["asset_id"], "standalone-saas-template")

        allowed_path = GENERATED_WORKSPACES_DIR / "guard-check"
        ensure_allowed_workspace_path(allowed_path)

        with self.assertRaises(TemplateContractError):
            ensure_allowed_workspace_path(ROOT_DIR / "tmp" / "guard-check")


class InstantiateTemplateProjectCliTests(unittest.TestCase):
    maxDiff = None

    def addCleanupPath(self, path: Path) -> None:
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))

    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )

    def create_fixture(self) -> tuple[Path, Path, Path]:
        GENERATED_WORKSPACES_DIR.mkdir(parents=True, exist_ok=True)
        temp_dir = Path(tempfile.mkdtemp(prefix="instantiate-template-", dir=str(GENERATED_WORKSPACES_DIR)))
        self.addCleanupPath(temp_dir)
        workspace_root = temp_dir
        registry_path = temp_dir / "standalone-saas-template.json"
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        registry["source"]["repo_path"] = TEMPLATE_SOURCE.as_posix()
        registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return temp_dir, workspace_root, registry_path

    def test_cli_help_exposes_required_flags(self) -> None:
        result = self.run_script("--help")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        help_text = result.stdout
        for flag in (
            "--workspace-name",
            "--app-key",
            "--app-name",
            "--app-url",
            "--workspace-root",
            "--dry-run",
        ):
            self.assertIn(flag, help_text)

    def test_script_creates_workspace_and_injects_identity_and_hermes_handoff(self) -> None:
        temp_dir, workspace_root, registry_path = self.create_fixture()
        result = self.run_script(
            "--registry-path",
            str(registry_path),
            "--workspace-root",
            str(workspace_root),
            "--workspace-name",
            "lead-capture",
            "--app-key",
            "lead_capture",
            "--app-name",
            "Lead Capture",
            "--app-url",
            "https://lead.example.com",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)

        workspace = workspace_root / "lead-capture"
        self.assertTrue(workspace.exists(), "workspace was not created")
        self.assertIn("lead-capture", result.stdout)

        env_text = (workspace / ".env").read_text(encoding="utf-8")
        self.assertIn("APP_KEY=lead_capture", env_text)
        self.assertIn("APP_NAME=Lead Capture", env_text)
        self.assertIn("APP_URL=https://lead.example.com", env_text)
        self.assertIn("PAYPAL_BRAND_NAME=Lead Capture", env_text)
        self.assertIn("NEXT_PUBLIC_SUPABASE_URL=__REQUIRED__", env_text)
        self.assertIn("NEXT_PUBLIC_SUPABASE_ANON_KEY=__REQUIRED__", env_text)
        self.assertIn("SUPABASE_SERVICE_ROLE_KEY=__REQUIRED__", env_text)
        self.assertIn("NEXT_PUBLIC_PAYPAL_CLIENT_ID=__REQUIRED__", env_text)
        self.assertIn("PAYPAL_CLIENT_SECRET=__REQUIRED__", env_text)
        self.assertIn("PAYPAL_ENVIRONMENT=sandbox", env_text)

        app_definition = (workspace / "src" / "lib" / "app-definition.ts").read_text(encoding="utf-8")
        self.assertIn('name: "Lead Capture"', app_definition)
        self.assertIn('url: "https://lead.example.com"', app_definition)
        self.assertIn('eyebrow: "Lead Capture"', app_definition)
        self.assertIn('headline: "Lead Capture"', app_definition)
        self.assertIn('productId: "lead_capture_default_offer"', app_definition)
        self.assertIn('description: "Lead Capture access"', app_definition)

        metadata_path = workspace / ".hermes" / "project-metadata.json"
        guardrails_path = workspace / ".hermes" / "shared-backend-guardrails.json"
        brief_path = workspace / ".hermes" / "PROJECT_BRIEF_ENTRYPOINT.md"
        self.assertTrue(metadata_path.exists(), "metadata file missing")
        self.assertTrue(guardrails_path.exists(), "guardrails file missing")
        self.assertTrue(brief_path.exists(), "brief entrypoint missing")

        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        self.assertEqual(metadata["asset_id"], "standalone-saas-template")
        self.assertEqual(metadata["workspace_name"], "lead-capture")
        self.assertEqual(metadata["app_key"], "lead_capture")
        self.assertEqual(metadata["app_name"], "Lead Capture")
        self.assertEqual(metadata["app_url"], "https://lead.example.com")
        self.assertEqual(metadata["template_source_path"], TEMPLATE_SOURCE.as_posix())
        self.assertEqual(metadata["canonical_contract_path"], CONTRACT_PATH.as_posix())

        guardrails = json.loads(guardrails_path.read_text(encoding="utf-8"))
        self.assertEqual(guardrails["backend_model"], "shared-supabase")
        self.assertEqual(guardrails["app_key"], metadata["app_key"])
        self.assertEqual(guardrails["canonical_contract_path"], metadata["canonical_contract_path"])
        self.assertEqual(guardrails["allowed_shared_tables"], EXPECTED_SHARED_TABLES)
        self.assertEqual(guardrails["protected_paths"], EXPECTED_PROTECTED_PATHS)
        self.assertEqual(guardrails["client_write_blocked_tables"], EXPECTED_SHARED_TABLES)
        self.assertFalse(guardrails["allow_independent_backend"])

        brief_text = brief_path.read_text(encoding="utf-8")
        self.assertIn("project-metadata.json", brief_text)
        self.assertIn("shared-backend-guardrails.json", brief_text)
        self.assertIn("standalone-saas-template-contract.md", brief_text)
        self.assertIn("Lead Capture", brief_text)

    def test_dry_run_reports_plan_without_writing_workspace(self) -> None:
        temp_dir, workspace_root, registry_path = self.create_fixture()
        result = self.run_script(
            "--registry-path",
            str(registry_path),
            "--workspace-root",
            str(workspace_root),
            "--workspace-name",
            "lead-capture",
            "--app-key",
            "lead_capture",
            "--app-name",
            "Lead Capture",
            "--app-url",
            "https://lead.example.com",
            "--dry-run",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        self.assertIn("DRY RUN", result.stdout)
        self.assertIn("lead-capture", result.stdout)
        self.assertIn("shared-supabase", result.stdout)
        self.assertIn("shared-backend-guardrails.json", result.stdout)
        self.assertFalse((workspace_root / "lead-capture").exists(), "dry-run must not create workspace")

    def test_workspace_root_safety_rejects_outside_allowed_tree(self) -> None:
        temp_dir, workspace_root, registry_path = self.create_fixture()
        unsafe_root = Path(tempfile.mkdtemp(prefix="instantiate-template-unsafe-"))
        self.addCleanupPath(unsafe_root)
        result = self.run_script(
            "--registry-path",
            str(registry_path),
            "--workspace-root",
            str(unsafe_root),
            "--workspace-name",
            "lead-capture",
            "--app-key",
            "lead_capture",
            "--app-name",
            "Lead Capture",
            "--app-url",
            "https://lead.example.com",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("refusing to write outside allowed workspace roots", result.stderr)


if __name__ == "__main__":
    unittest.main()
