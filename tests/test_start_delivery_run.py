import json
import shutil
import tempfile
import unittest
from pathlib import Path
import importlib.util


ROOT_DIR = Path(__file__).resolve().parent.parent
START_SCRIPT_PATH = ROOT_DIR / "scripts" / "start_delivery_run.py"
CONTRACT_PATH = ROOT_DIR / "docs" / "platform" / "standalone-saas-template-contract.md"
PLAN_09_01_PATH = ROOT_DIR / ".planning" / "phases" / "09-claude-code-delivery-team-orchestration" / "09-01-PLAN.md"
STAGE_ORDER = [
    "design",
    "development",
    "testing",
    "git versioning",
    "release readiness",
]
ROLE_ORDER = [
    "design-specialist",
    "development-specialist",
    "testing-specialist",
    "git-versioning-specialist",
    "release-readiness-specialist",
]
REQUIRED_INPUT_KEYS = [
    "approved_brief_path",
    "template_contract_path",
    "shared_backend_guardrails_path",
    "project_metadata_path",
    "gsd_constraints_path",
]
REQUIRED_INPUT_FILES = {
    "approved_brief_path": ".hermes/PROJECT_BRIEF_ENTRYPOINT.md",
    "template_contract_path": "docs/platform/standalone-saas-template-contract.md",
    "shared_backend_guardrails_path": ".hermes/shared-backend-guardrails.json",
    "project_metadata_path": ".hermes/project-metadata.json",
    "gsd_constraints_path": ".planning/phases/09-claude-code-delivery-team-orchestration/09-01-PLAN.md",
}
EXPECTED_ARTIFACTS = [
    ".hermes/delivery-run-manifest.json",
    ".hermes/DELIVERY_SCOPE.md",
    ".hermes/delivery-events.jsonl",
    ".hermes/DELIVERY_STATUS.md",
]


def load_module(module_name: str, script_path: Path):
    if not script_path.exists():
        raise AssertionError(f"expected script to exist: {script_path}")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class StartDeliveryRunTests(unittest.TestCase):
    maxDiff = None

    def addCleanupPath(self, path: Path) -> None:
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))

    def create_workspace_fixture(self) -> Path:
        workspace_root = Path(tempfile.mkdtemp(prefix="delivery-run-workspace-"))
        self.addCleanupPath(workspace_root)
        workspace = workspace_root / "lead-capture"
        hermes_dir = workspace / ".hermes"
        hermes_dir.mkdir(parents=True, exist_ok=True)
        (workspace_root / "docs" / "platform").mkdir(parents=True, exist_ok=True)
        (workspace_root / ".planning" / "phases" / "09-claude-code-delivery-team-orchestration").mkdir(parents=True, exist_ok=True)
        (workspace_root / REQUIRED_INPUT_FILES["template_contract_path"]).write_text(
            "# Standalone SaaS Template Contract\n",
            encoding="utf-8",
        )
        (workspace_root / REQUIRED_INPUT_FILES["gsd_constraints_path"]).write_text(
            "# Phase 09 Plan 01\n",
            encoding="utf-8",
        )

        metadata = {
            "asset_id": "standalone-saas-template",
            "workspace_name": "lead-capture",
            "app_key": "lead_capture",
            "app_name": "Lead Capture",
            "app_url": "https://lead.example.com",
            "template_source_path": "C:/Users/42236/Desktop/standalone-saas-template",
            "canonical_contract_path": CONTRACT_PATH.as_posix(),
        }
        (hermes_dir / "project-metadata.json").write_text(
            json.dumps(metadata, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        guardrails = {
            "backend_model": "shared-supabase",
            "app_key": metadata["app_key"],
            "canonical_contract_path": metadata["canonical_contract_path"],
            "allowed_shared_tables": ["users", "orders", "payments", "subscriptions"],
            "protected_paths": ["src/lib/paypal.ts"],
            "client_write_blocked_tables": ["users", "orders", "payments", "subscriptions"],
            "allow_independent_backend": False,
        }
        (hermes_dir / "shared-backend-guardrails.json").write_text(
            json.dumps(guardrails, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        (hermes_dir / "PROJECT_BRIEF_ENTRYPOINT.md").write_text(
            "# Hermes Project Brief Entrypoint\n\n"
            "- Workspace: `lead-capture`\n"
            "- Canonical contract: `docs/platform/standalone-saas-template-contract.md`\n"
            "- Delivery contract: `.planning/phases/09-claude-code-delivery-team-orchestration/09-01-PLAN.md`\n",
            encoding="utf-8",
        )
        return workspace

    def test_d04_blocks_when_any_required_input_is_missing(self) -> None:
        start_delivery_run = load_module("start_delivery_run", START_SCRIPT_PATH)
        for input_key, relative_path in REQUIRED_INPUT_FILES.items():
            workspace = self.create_workspace_fixture()
            target = workspace / relative_path if relative_path.startswith(".hermes/") else workspace.parent / relative_path
            target.unlink()
            result = start_delivery_run.initialize_delivery_run(workspace)
            self.assertEqual(result["ok"], False, f"D-04 should block when {input_key} is missing")
            self.assertIn(input_key, result["error"])
            self.assertIn(relative_path, result["error"])
            for artifact in EXPECTED_ARTIFACTS:
                self.assertFalse((workspace / artifact).exists(), f"artifact should not exist after blocking: {artifact}")

    def test_d04_d08_successful_bootstrap_creates_workspace_local_artifacts_and_manifest(self) -> None:
        start_delivery_run = load_module("start_delivery_run", START_SCRIPT_PATH)
        workspace = self.create_workspace_fixture()
        result = start_delivery_run.initialize_delivery_run(workspace)
        self.assertTrue(result["ok"], msg=result)

        for artifact in EXPECTED_ARTIFACTS:
            self.assertTrue((workspace / artifact).exists(), f"missing bootstrap artifact: {artifact}")

        manifest = json.loads((workspace / ".hermes" / "delivery-run-manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(manifest["orchestrator_role"], "delivery-orchestrator")
        self.assertEqual(manifest["workspace_name"], "lead-capture")
        self.assertEqual(manifest["scope_status"], "approved-brief-only")
        self.assertEqual(manifest["stage_order"], STAGE_ORDER)
        self.assertEqual([stage["role"] for stage in manifest["stages"]], ROLE_ORDER)
        self.assertEqual(sorted(manifest["required_inputs"].keys()), sorted(REQUIRED_INPUT_KEYS))
        for key, relative_path in REQUIRED_INPUT_FILES.items():
            self.assertEqual(manifest["required_inputs"][key], relative_path)

        scope_text = (workspace / ".hermes" / "DELIVERY_SCOPE.md").read_text(encoding="utf-8")
        self.assertIn("approved-brief-only", scope_text)
        self.assertIn("scope reopen", scope_text.lower())
        self.assertNotIn("assets/shared/", scope_text)

        events = (workspace / ".hermes" / "delivery-events.jsonl").read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(events), 1, "bootstrap should seed exactly one run_started event")

        status_text = (workspace / ".hermes" / "DELIVERY_STATUS.md").read_text(encoding="utf-8")
        self.assertIn("delivery-events.jsonl", status_text)
        self.assertIn("delivery-orchestrator", status_text)


if __name__ == "__main__":
    unittest.main()
