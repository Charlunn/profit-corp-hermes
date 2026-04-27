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


class Phase11GithubSyncTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.start_module = load_module("start_approved_project_delivery_phase11_github", START_SCRIPT_PATH)
        self.tmp = tempfile.TemporaryDirectory(prefix="phase11-github-sync-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project_dir = self.root / "assets" / "shared" / "approved-projects" / "demo-app"
        self.project_dir.mkdir(parents=True)
        self.workspace = self.root / "generated-workspaces" / "demo-app"
        (self.workspace / ".hermes").mkdir(parents=True)
        self.authority_path = self.project_dir / "APPROVED_PROJECT.json"
        self.brief_path = self.project_dir / "PROJECT_BRIEF.md"
        self.brief_path.write_text("# Approved Project Brief\n", encoding="utf-8")

    def write_record(self, *, shipping: dict | None = None) -> dict:
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
                "stage": "delivery_run_bootstrap",
                "status": "ready",
                "block_reason": None,
                "resume_from_stage": "github_repository",
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
        }
        if shipping is not None:
            record["shipping"] = shipping
        self.authority_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return record

    def read_record(self) -> dict:
        return json.loads(self.authority_path.read_text(encoding="utf-8"))

    def test_pipeline_stage_order_includes_phase11_github_and_vercel_stages(self) -> None:
        expected = [
            "approval",
            "brief_generation",
            "workspace_instantiation",
            "conformance",
            "delivery_run_bootstrap",
            "github_repository",
            "github_sync",
            "vercel_linkage",
            "vercel_deploy",
            "handoff",
        ]
        self.assertEqual(self.start_module.PIPELINE_STAGES, expected)

    def test_prepare_github_repository_supports_create_and_attach_and_persists_repo_identity(self) -> None:
        self.write_record()

        created = self.start_module.prepare_github_repository(
            self.authority_path,
            mode="create",
            repository_name="profit-corp/demo-app",
            repository_url="https://github.com/profit-corp/demo-app.git",
            default_branch="main",
            workspace_path=self.workspace,
        )
        self.assertTrue(created["ok"], msg=created)
        created_record = self.read_record()
        self.assertEqual(created_record["shipping"]["github"]["repository_mode"], "create")
        self.assertEqual(created_record["shipping"]["github"]["repository_name"], "profit-corp/demo-app")
        self.assertEqual(created_record["shipping"]["github"]["repository_url"], "https://github.com/profit-corp/demo-app.git")
        self.assertEqual(created_record["shipping"]["github"]["default_branch"], "main")
        self.assertEqual(created_record["shipping"]["github"]["delivery_run_id"], "delivery-demo-001")
        self.assertEqual(created_record["pipeline"]["resume_from_stage"], "github_sync")

        attached = self.start_module.prepare_github_repository(
            self.authority_path,
            mode="attach",
            repository_name="profit-corp/existing-demo-app",
            repository_url="https://github.com/profit-corp/existing-demo-app.git",
            default_branch="trunk",
            workspace_path=self.workspace,
        )
        self.assertTrue(attached["ok"], msg=attached)
        attached_record = self.read_record()
        self.assertEqual(attached_record["shipping"]["github"]["repository_mode"], "attach")
        self.assertEqual(attached_record["shipping"]["github"]["repository_name"], "profit-corp/existing-demo-app")
        self.assertEqual(attached_record["shipping"]["github"]["repository_url"], "https://github.com/profit-corp/existing-demo-app.git")
        self.assertEqual(attached_record["shipping"]["github"]["default_branch"], "trunk")

    def test_sync_failure_blocks_downstream_stages_with_explicit_evidence_and_resume_stage(self) -> None:
        self.write_record(
            shipping={
                "github": {
                    "repository_mode": "attach",
                    "repository_name": "profit-corp/demo-app",
                    "repository_url": "https://github.com/profit-corp/demo-app.git",
                    "default_branch": "main",
                    "delivery_run_id": "delivery-demo-001",
                }
            }
        )
        evidence_path = self.workspace / ".hermes" / "github-sync.log"
        evidence_path.parent.mkdir(parents=True, exist_ok=True)
        evidence_path.write_text("push failed\n", encoding="utf-8")

        with mock.patch.object(self.start_module, "run_github_sync", return_value={
            "ok": False,
            "block_reason": "github_sync_failed",
            "evidence_path": evidence_path.as_posix(),
            "error": "push failed",
        }):
            result = self.start_module.run_pipeline_from_stage(
                self.authority_path,
                self.read_record(),
                start_stage="github_sync",
                workspace_root=self.root / "generated-workspaces",
            )

        self.assertFalse(result["ok"], msg=result)
        self.assertEqual(result["stage"], "github_sync")
        self.assertEqual(result["block_reason"], "github_sync_failed")
        updated = self.read_record()
        self.assertEqual(updated["pipeline"]["stage"], "github_sync")
        self.assertEqual(updated["pipeline"]["resume_from_stage"], "github_sync")
        self.assertEqual(updated["pipeline"]["evidence_path"], evidence_path.as_posix())
        self.assertEqual(updated["pipeline"]["blocked_downstream_stages"], ["vercel_linkage", "vercel_deploy"])


if __name__ == "__main__":
    unittest.main()
