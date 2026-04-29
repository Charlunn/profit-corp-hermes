import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = ROOT / "scripts" / "approved_delivery_governance.py"


def load_module(module_name: str, script_path: Path):
    if not script_path.exists():
        raise AssertionError(f"expected script to exist: {script_path}")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for: {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class CredentialGovernanceContractTest(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module("approved_delivery_governance", SCRIPT_PATH)
        self.root = Path(tempfile.mkdtemp(prefix="phase12-credential-governance-"))
        self.authority = self.root / "authority"
        self.project_dir = self.authority / "projects" / "demo"
        self.project_dir.mkdir(parents=True, exist_ok=True)
        self.authority_record_path = self.project_dir / "APPROVED_PROJECT.json"
        self.workspace = self.root / "workspace"
        self.workspace.mkdir(parents=True, exist_ok=True)
        self.events_path = self.project_dir / "approved-delivery-events.jsonl"
        self.record = {
            "project_slug": "demo",
            "brief_path": (self.project_dir / "brief.md").as_posix(),
            "pipeline": {
                "delivery_run_id": "run_123",
                "workspace_path": self.workspace.as_posix(),
                "stage": "github_repository",
                "status": "running",
            },
            "shipping": {
                "github": {"repository_name": "demo-repo", "repository_url": "https://github.com/acme/demo-repo"},
                "vercel": {"project_name": "demo-web", "project_id": "prj_123"},
            },
        }
        self.authority_record_path.write_text(json.dumps(self.record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def read_events(self) -> list[dict]:
        if not self.events_path.exists():
            return []
        return [json.loads(line) for line in self.events_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def test_allowlist_matches_approved_credential_actions_only(self) -> None:
        self.assertEqual(
            set(self.module.ALLOWED_CREDENTIAL_ACTIONS),
            {
                "github_repository_prepare",
                "github_sync",
                "vercel_project_link",
                "vercel_env_apply",
                "vercel_deploy",
            },
        )

    def test_rejects_non_allowlisted_action_before_dispatch(self) -> None:
        with self.assertRaises(self.module.ApprovedDeliveryGovernanceError):
            self.module.run_governed_action(
                action="shell_out_anything",
                authority_record_path=self.authority_record_path,
                stage="github_repository",
                helper=lambda **_: {"ok": True},
            )

    def test_persists_success_audit_artifact_with_required_schema(self) -> None:
        result = self.module.run_governed_action(
            action="github_repository_prepare",
            authority_record_path=self.authority_record_path,
            stage="github_repository",
            helper=lambda **_: {
                "ok": True,
                "evidence_path": (self.workspace / ".hermes" / "github-repository-prepare.json").as_posix(),
                "repository_name": "demo-repo",
                "repository_url": "https://github.com/acme/demo-repo",
            },
        )

        self.assertTrue(result["ok"], msg=result)
        audit_path = Path(result["audit_path"])
        audit = json.loads(audit_path.read_text(encoding="utf-8"))
        self.assertEqual(audit["action"], "github_repository_prepare")
        self.assertEqual(audit["stage"], "github_repository")
        self.assertEqual(audit["outcome"], "success")
        self.assertEqual(audit["delivery_run_id"], "run_123")
        self.assertEqual(audit["target"]["repository_name"], "demo-repo")
        self.assertEqual(audit["evidence_path"], (self.workspace / ".hermes" / "github-repository-prepare.json").as_posix())
        self.assertTrue(audit["timestamp"])

        events = self.read_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["stage"], "github_repository")
        self.assertEqual(events[0]["status"], "completed")
        self.assertEqual(events[0]["outcome"], "success")
        self.assertEqual(events[0]["artifact"], audit_path.as_posix())
        self.assertEqual(events[0]["evidence_path"], audit["evidence_path"])

    def test_persists_blocked_audit_and_append_only_event_linkage(self) -> None:
        result = self.module.run_governed_action(
            action="vercel_project_link",
            authority_record_path=self.authority_record_path,
            stage="vercel_linkage",
            helper=lambda **_: {
                "ok": False,
                "block_reason": "missing_vercel_auth",
                "error": "VERCEL_TOKEN is required",
                "evidence_path": (self.workspace / ".hermes" / "vercel-project-link.json").as_posix(),
                "project_name": "demo-web",
            },
        )

        self.assertFalse(result["ok"], msg=result)
        self.assertEqual(result["block_reason"], "missing_vercel_auth")
        audit = json.loads(Path(result["audit_path"]).read_text(encoding="utf-8"))
        self.assertEqual(audit["outcome"], "blocked")
        self.assertEqual(audit["reason"], "missing_vercel_auth")
        self.assertEqual(audit["target"]["project_name"], "demo-web")
        self.assertEqual(audit["delivery_run_id"], "run_123")
        self.assertEqual(audit["evidence_path"], (self.workspace / ".hermes" / "vercel-project-link.json").as_posix())

        events = self.read_events()
        self.assertEqual(len(events), 1)
        self.assertEqual(events[0]["status"], "blocked")
        self.assertEqual(events[0]["outcome"], "blocked")
        self.assertEqual(events[0]["block_reason"], "missing_vercel_auth")
        self.assertEqual(events[0]["artifact"], result["audit_path"])

    def test_persists_failure_audit_with_explicit_reason_and_evidence(self) -> None:
        result = self.module.run_governed_action(
            action="github_sync",
            authority_record_path=self.authority_record_path,
            stage="github_sync",
            helper=lambda **_: {
                "ok": False,
                "block_reason": "github_sync_failed",
                "error": "push rejected by remote",
                "failed_step": "push",
                "attempted_command": "git push",
                "push_attempts": [
                    {"transport": "https", "status": "failed"},
                    {"transport": "ssh", "status": "failed"},
                ],
                "evidence_path": (self.workspace / ".hermes" / "github-sync.json").as_posix(),
                "repository_url": "https://github.com/acme/demo-repo",
            },
        )

        self.assertFalse(result["ok"], msg=result)
        audit = json.loads(Path(result["audit_path"]).read_text(encoding="utf-8"))
        self.assertEqual(audit["outcome"], "failed")
        self.assertEqual(audit["reason"], "github_sync_failed")
        self.assertEqual(audit["error"], "push rejected by remote")
        self.assertEqual(audit["target"]["repository_url"], "https://github.com/acme/demo-repo")
        self.assertTrue(Path(result["audit_path"]).exists())

        events = self.read_events()
        self.assertEqual(events[-1]["status"], "failed")
        self.assertEqual(events[-1]["outcome"], "failed")
        self.assertEqual(events[-1]["block_reason"], "github_sync_failed")
        self.assertEqual(events[-1]["evidence_path"], (self.workspace / ".hermes" / "github-sync.json").as_posix())


if __name__ == "__main__":
    unittest.main()
