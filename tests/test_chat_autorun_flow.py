import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "chat_approved_delivery_autorun.py"


def load_module(module_name: str, script_path: Path):
    if not script_path.exists():
        raise AssertionError(f"expected script to exist: {script_path}")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ChatApprovedDeliveryAutorunTests(unittest.TestCase):
    def addCleanupPath(self, path: Path) -> None:
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))

    def create_authority_record(self, *, stage: str, status: str, resume_from_stage: str = "") -> tuple[Path, Path]:
        root = Path(tempfile.mkdtemp(prefix="chat-autorun-"))
        self.addCleanupPath(root)
        project_dir = root / "assets" / "shared" / "approved-projects" / "lead-capture-copilot"
        project_dir.mkdir(parents=True, exist_ok=True)
        authority_path = project_dir / "APPROVED_PROJECT.json"
        payload = {
            "approval": {
                "approval_id": "APR-2026-04-27-01",
                "approved_at": "2026-04-27T08:30:00Z",
                "approver": "ceo",
                "evidence": {
                    "decision_record": "assets/shared/CORP_CULTURE.md#greenlight-2026-04-27",
                    "summary": "Approved for autonomous delivery.",
                },
            },
            "proposal": {
                "proposal_id": "proposal-idea-001-v1",
                "chat_origin": {
                    "run_id": "chat-run-20260505-001",
                    "platform": "discord",
                    "channel_or_chat_id": "chan-123",
                    "thread_or_reply_context": "thr-999",
                },
            },
            "project_identity": {"project_slug": "lead-capture-copilot"},
            "pipeline": {
                "stage": stage,
                "status": status,
                "resume_from_stage": resume_from_stage or stage,
                "workspace_path": (root / "generated-workspaces" / "lead-capture-copilot").as_posix(),
            },
            "artifacts": {
                "authority_record_path": authority_path.as_posix(),
                "delivery_brief_path": (project_dir / "PROJECT_BRIEF.md").as_posix(),
                "status_path": (project_dir / "DELIVERY_PIPELINE_STATUS.md").as_posix(),
                "final_review_path": (project_dir / "FINAL_OPERATOR_REVIEW.md").as_posix(),
            },
            "shipping": {"github": {}, "vercel": {}},
        }
        authority_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return root, authority_path

    def test_ready_approval_autorun_starts_then_finalizes_handoff(self) -> None:
        module = load_module("chat_approved_delivery_autorun", SCRIPT_PATH)
        root, authority_path = self.create_authority_record(stage="approval", status="ready")
        final_handoff = root / "generated-workspaces" / "lead-capture-copilot" / ".hermes" / "FINAL_DELIVERY.md"
        final_handoff.parent.mkdir(parents=True, exist_ok=True)
        final_handoff.write_text("# Final Delivery\n", encoding="utf-8")

        with mock.patch.object(module, "start_approved_project_delivery", return_value={
            "ok": True,
            "stage": "vercel_deploy",
            "status": "ready",
            "final_handoff_path": final_handoff.as_posix(),
        }) as start_mock, \
             mock.patch.object(module, "resume_approved_project_delivery") as resume_mock, \
             mock.patch.object(module, "finalize_delivery_handoff", return_value={
                 "ok": True,
                 "stage": "handoff",
                 "status": "completed",
                 "final_handoff_path": final_handoff.as_posix(),
             }) as finalize_mock:
            result = module.autorun_approved_delivery(authority_path)

        self.assertTrue(result["ok"], msg=result)
        self.assertEqual(result["stage"], "handoff")
        self.assertEqual(result["status"], "completed")
        start_mock.assert_called_once()
        resume_mock.assert_not_called()
        finalize_mock.assert_called_once()

    def test_blocked_authority_reenqueue_uses_resume_and_preserves_blocked_truth(self) -> None:
        module = load_module("chat_approved_delivery_autorun_blocked", SCRIPT_PATH)
        _, authority_path = self.create_authority_record(stage="development", status="blocked")

        with mock.patch.object(module, "start_approved_project_delivery") as start_mock, \
             mock.patch.object(module, "resume_approved_project_delivery", return_value={
                 "ok": False,
                 "stage": "development",
                 "status": "blocked",
                 "block_reason": "missing_stage_handoff",
                 "evidence_path": "C:/tmp/stage-handoff.md",
                 "error": "stage handoff missing",
             }) as resume_mock, \
             mock.patch.object(module, "finalize_delivery_handoff") as finalize_mock:
            result = module.autorun_approved_delivery(authority_path)

        self.assertFalse(result["ok"], msg=result)
        self.assertEqual(result["status"], "blocked")
        self.assertEqual(result["block_reason"], "missing_stage_handoff")
        start_mock.assert_not_called()
        resume_mock.assert_called_once()
        finalize_mock.assert_not_called()

    def test_completed_handoff_reenqueue_is_idempotent_and_does_not_restart_pipeline(self) -> None:
        module = load_module("chat_approved_delivery_autorun_completed", SCRIPT_PATH)
        root, authority_path = self.create_authority_record(stage="handoff", status="completed")
        final_handoff = root / "assets" / "shared" / "approved-projects" / "lead-capture-copilot" / "FINAL_DELIVERY.md"
        final_handoff.write_text("# Final Delivery\n", encoding="utf-8")
        payload = json.loads(authority_path.read_text(encoding="utf-8"))
        payload["pipeline"]["final_handoff_path"] = final_handoff.as_posix()
        payload["artifacts"]["final_handoff_path"] = final_handoff.as_posix()
        authority_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        with mock.patch.object(module, "start_approved_project_delivery") as start_mock, \
             mock.patch.object(module, "resume_approved_project_delivery") as resume_mock, \
             mock.patch.object(module, "finalize_delivery_handoff") as finalize_mock:
            result = module.autorun_approved_delivery(authority_path)

        self.assertTrue(result["ok"], msg=result)
        self.assertTrue(result["idempotent_replay"])
        self.assertEqual(result["stage"], "handoff")
        self.assertEqual(result["status"], "completed")
        start_mock.assert_not_called()
        resume_mock.assert_not_called()
        finalize_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
