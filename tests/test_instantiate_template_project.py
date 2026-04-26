import json
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


ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "instantiate_template_project.py"
REGISTRY_PATH = ROOT_DIR / "assets" / "shared" / "templates" / "standalone-saas-template.json"


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
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )

    def test_cli_placeholder(self) -> None:
        self.assertTrue(SCRIPT_PATH.exists(), "instantiate script missing")


if __name__ == "__main__":
    unittest.main()
