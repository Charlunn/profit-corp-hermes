import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT_DIR = Path(__file__).resolve().parent.parent
START_SCRIPT_PATH = ROOT_DIR / "scripts" / "start_approved_project_delivery.py"


def load_module(module_name: str, script_path: Path):
    if not script_path.exists():
        raise AssertionError(f"expected script to exist: {script_path}")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Phase11VercelFlowTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.start_module = load_module("start_approved_project_delivery_phase11_vercel", START_SCRIPT_PATH)
        self.tmp = tempfile.TemporaryDirectory(prefix="phase11-vercel-flow-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project_dir = self.root / "assets" / "shared" / "approved-projects" / "demo-app"
        self.project_dir.mkdir(parents=True)
        self.workspace = self.root / "generated-workspaces" / "demo-app"
        (self.workspace / ".hermes").mkdir(parents=True)
        self.authority_path = self.project_dir / "APPROVED_PROJECT.json"
        self.brief_path = self.project_dir / "PROJECT_BRIEF.md"
        self.brief_path.write_text("# Approved Project Brief\n", encoding="utf-8")

    def write_record(self, *, shipping: dict | None = None) -> None:
        record = {
            "approval": {
                "approval_id": "APR-11-01",
                "approved_at": "2026-04-27T10:00:00Z",
                "approver": "owner",
                "evidence": {
                    "decision_record": "assets/shared/CORP_CULTURE.md#phase11",
                    "summary": "Approved for shipping automation.",
                },
            },
            "project_identity": {
                "project_slug": "demo-app",
                "app_key": "demo_app",
                "app_name": "Demo App",
                "app_url": "https://demo.example.com",
            },
            "approved_scope": ["bootstrap repo and deploy to Vercel"],
            "target_user": "Operators",
            "mvp_framing": "Ship from approved authority record only.",
            "constraints": ["Use constrained CLI wrappers only"],
            "acceptance_gates": ["GitHub sync succeeded", "Vercel deploy reported"],
            "pipeline": {
                "stage": "github_sync",
                "status": "ready",
                "block_reason": None,
                "resume_from_stage": "vercel_linkage",
                "workspace_path": self.workspace.as_posix(),
                "delivery_run_id": "delivery-demo-001",
            },
            "artifacts": {
                "project_directory": self.project_dir.as_posix(),
                "authority_record_path": self.authority_path.as_posix(),
                "delivery_brief_path": self.brief_path.as_posix(),
                "events_path": (self.project_dir / "approved-delivery-events.jsonl").as_posix(),
                "status_path": (self.project_dir / "DELIVERY_PIPELINE_STATUS.md").as_posix(),
                "delivery_manifest_path": (self.workspace / ".hermes" / "delivery-run-manifest.json").as_posix(),
                "workspace_path": self.workspace.as_posix(),
            },
            "shipping": shipping or {
                "github": {
                    "repository_mode": "create",
                    "repository_name": "profit-corp/demo-app",
                    "repository_url": "https://github.com/profit-corp/demo-app.git",
                    "default_branch": "main",
                    "delivery_run_id": "delivery-demo-001",
                    "last_sync_status": "completed",
                }
            },
        }
        self.authority_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def read_record(self) -> dict:
        return json.loads(self.authority_path.read_text(encoding="utf-8"))

    def test_vercel_linkage_requires_single_project_and_persists_env_contract_evidence(self) -> None:
        self.write_record()
        env_evidence = self.workspace / ".hermes" / "vercel-env-contract.json"
        env_evidence.parent.mkdir(parents=True, exist_ok=True)
        env_evidence.write_text("{}\n", encoding="utf-8")

        with mock.patch.object(self.start_module, "link_vercel_project", return_value={
            "ok": True,
            "project_id": "prj_123",
            "project_name": "demo-app-prod",
            "project_url": "https://vercel.com/profit-corp/demo-app-prod",
            "env_contract_path": env_evidence.as_posix(),
            "required_env": {
                "platform_managed": ["SUPABASE_SERVICE_ROLE_KEY", "PAYPAL_CLIENT_SECRET"],
                "identity_derived": {
                    "APP_KEY": "demo_app",
                    "APP_NAME": "Demo App",
                    "APP_URL": "https://demo.example.com",
                },
            },
        }):
            result = self.start_module.run_pipeline_from_stage(
                self.authority_path,
                self.read_record(),
                start_stage="vercel_linkage",
                workspace_root=self.root / "generated-workspaces",
            )

        self.assertTrue(result["ok"], msg=result)
        updated = self.read_record()
        self.assertEqual(updated["shipping"]["vercel"]["project_id"], "prj_123")
        self.assertEqual(updated["shipping"]["vercel"]["project_name"], "demo-app-prod")
        self.assertEqual(updated["shipping"]["vercel"]["env_contract_path"], env_evidence.as_posix())
        self.assertEqual(updated["shipping"]["vercel"]["required_env"]["platform_managed"], ["SUPABASE_SERVICE_ROLE_KEY", "PAYPAL_CLIENT_SECRET"])
        self.assertEqual(updated["shipping"]["vercel"]["required_env"]["identity_derived"]["APP_KEY"], "demo_app")
        self.assertEqual(updated["pipeline"]["resume_from_stage"], "vercel_deploy")

    def test_missing_tool_auth_env_and_linkage_map_to_distinct_blocked_states(self) -> None:
        self.write_record()
        cases = [
            ("missing_gh_cli", "github_repository"),
            ("missing_github_auth", "github_repository"),
            ("missing_vercel_auth", "vercel_linkage"),
            ("missing_vercel_project_linkage", "vercel_linkage"),
            ("missing_vercel_env_contract", "vercel_linkage"),
        ]
        for reason, stage in cases:
            with self.subTest(reason=reason):
                result = self.start_module.block_pipeline(
                    self.authority_path,
                    self.read_record(),
                    stage=stage,
                    block_reason=reason,
                    evidence_path=(self.workspace / ".hermes" / f"{reason}.md").as_posix(),
                    message=f"blocked on {reason}",
                    workspace_path=self.workspace.as_posix(),
                    delivery_run_id="delivery-demo-001",
                )
                self.assertFalse(result["ok"], msg=result)
                self.assertEqual(result["block_reason"], reason)
                updated = self.read_record()
                self.assertEqual(updated["pipeline"]["block_reason"], reason)
                self.assertEqual(updated["pipeline"]["resume_from_stage"], stage)

    def test_deploy_outcome_updates_authority_record_and_workspace_handoff_references(self) -> None:
        self.write_record(
            shipping={
                "github": {
                    "repository_mode": "create",
                    "repository_name": "profit-corp/demo-app",
                    "repository_url": "https://github.com/profit-corp/demo-app.git",
                    "default_branch": "main",
                    "delivery_run_id": "delivery-demo-001",
                    "last_sync_status": "completed",
                },
                "vercel": {
                    "project_id": "prj_123",
                    "project_name": "demo-app-prod",
                    "project_url": "https://vercel.com/profit-corp/demo-app-prod",
                    "env_contract_path": (self.workspace / ".hermes" / "vercel-env-contract.json").as_posix(),
                },
            }
        )
        final_handoff = self.workspace / ".hermes" / "FINAL_DELIVERY.md"
        final_handoff.write_text("# Final delivery\n", encoding="utf-8")

        with mock.patch.object(self.start_module, "run_vercel_deploy", return_value={
            "ok": True,
            "deployment_url": "https://demo-app.vercel.app",
            "deployment_status": "ready",
            "deployment_evidence_path": (self.workspace / ".hermes" / "vercel-deploy.json").as_posix(),
            "final_handoff_path": final_handoff.as_posix(),
        }):
            result = self.start_module.run_pipeline_from_stage(
                self.authority_path,
                self.read_record(),
                start_stage="vercel_deploy",
                workspace_root=self.root / "generated-workspaces",
            )

        self.assertTrue(result["ok"], msg=result)
        updated = self.read_record()
        self.assertEqual(updated["shipping"]["vercel"]["deployment_url"], "https://demo-app.vercel.app")
        self.assertEqual(updated["shipping"]["vercel"]["deployment_status"], "ready")
        self.assertEqual(updated["pipeline"]["final_handoff_path"], final_handoff.as_posix())
        self.assertEqual(updated["artifacts"]["final_handoff_path"], final_handoff.as_posix())


if __name__ == "__main__":
    unittest.main()
