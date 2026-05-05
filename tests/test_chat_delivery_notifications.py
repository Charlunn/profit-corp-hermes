import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "chat_final_delivery_notify.py"


def load_module(module_name: str, script_path: Path):
    if not script_path.exists():
        raise AssertionError(f"expected script to exist: {script_path}")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ChatDeliveryNotificationTests(unittest.TestCase):
    def addCleanupPath(self, path: Path) -> None:
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))

    def create_authority_fixture(self, *, platform: str, status: str, stage: str) -> tuple[Path, Path, Path]:
        root = Path(tempfile.mkdtemp(prefix="chat-delivery-notify-"))
        self.addCleanupPath(root)
        project_dir = root / "assets" / "shared" / "approved-projects" / "lead-capture-copilot"
        project_dir.mkdir(parents=True, exist_ok=True)
        authority_path = project_dir / "APPROVED_PROJECT.json"
        status_path = project_dir / "DELIVERY_PIPELINE_STATUS.md"
        final_review_path = project_dir / "FINAL_OPERATOR_REVIEW.md"
        final_handoff = project_dir / "FINAL_DELIVERY.md"
        final_handoff.write_text("# Final Delivery\n\n- Deployment shipped.\n", encoding="utf-8")
        status_path.write_text("# Delivery Pipeline Status\n", encoding="utf-8")
        final_review_path.write_text("# Final Operator Review\n\n- Product shipped with proof.\n", encoding="utf-8")
        payload = {
            "approval": {
                "approval_id": "APR-2026-04-27-01",
                "approved_at": "2026-04-27T08:30:00Z",
                "approver": "ceo",
                "evidence": {
                    "decision_record": "assets/shared/CORP_CULTURE.md#greenlight-2026-04-27",
                    "summary": "Approved for delivery.",
                },
            },
            "proposal": {
                "proposal_id": "proposal-idea-001-v1",
                "chat_origin": {
                    "run_id": "chat-run-20260505-001",
                    "platform": platform,
                    "channel_or_chat_id": "chan-123",
                    "thread_or_reply_context": "thr-999",
                },
            },
            "project_identity": {"project_slug": "lead-capture-copilot", "app_name": "Lead Capture Copilot"},
            "pipeline": {
                "stage": stage,
                "status": status,
                "block_reason": "missing_stage_handoff" if status == "blocked" else "",
                "final_handoff_path": final_handoff.as_posix() if status == "completed" else "",
            },
            "artifacts": {
                "authority_record_path": authority_path.as_posix(),
                "status_path": status_path.as_posix(),
                "final_review_path": final_review_path.as_posix(),
                "final_handoff_path": final_handoff.as_posix(),
            },
            "shipping": {
                "vercel": {
                    "deploy_url": "https://lead-capture-copilot-prod.vercel.app",
                    "deploy_status": "ready" if status == "completed" else "blocked",
                }
            },
        }
        authority_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return root, authority_path, final_handoff

    def test_success_notification_renders_from_persisted_truth_for_discord_and_telegram(self) -> None:
        module = load_module("chat_final_delivery_notify_success", SCRIPT_PATH)
        for platform in ("discord", "telegram"):
            with self.subTest(platform=platform):
                _, authority_path, final_handoff = self.create_authority_fixture(platform=platform, status="completed", stage="handoff")
                result = module.deliver_final_chat_notification(authority_path, platform=platform)
                self.assertTrue(result["ok"], msg=result)
                self.assertEqual(result["delivery_status"], "completed")
                self.assertIn("https://lead-capture-copilot-prod.vercel.app", result["message"])
                self.assertIn(final_handoff.as_posix(), result["message"])
                self.assertIn("FINAL_OPERATOR_REVIEW.md", result["message"])
                self.assertIn("Lead Capture Copilot", result["message"])

    def test_blocked_notification_includes_stage_reason_and_recovery_context(self) -> None:
        module = load_module("chat_final_delivery_notify_blocked", SCRIPT_PATH)
        _, authority_path, _ = self.create_authority_fixture(platform="discord", status="blocked", stage="development")
        result = module.deliver_final_chat_notification(authority_path, platform="discord")
        self.assertTrue(result["ok"], msg=result)
        self.assertEqual(result["delivery_status"], "blocked")
        self.assertIn("development", result["message"])
        self.assertIn("missing_stage_handoff", result["message"])
        self.assertIn("DELIVERY_PIPELINE_STATUS.md", result["message"])

    def test_duplicate_final_notification_is_suppressed_for_same_authority_truth(self) -> None:
        module = load_module("chat_final_delivery_notify_idempotent", SCRIPT_PATH)
        _, authority_path, _ = self.create_authority_fixture(platform="discord", status="completed", stage="handoff")
        first = module.deliver_final_chat_notification(authority_path, platform="discord")
        second = module.deliver_final_chat_notification(authority_path, platform="discord")
        self.assertTrue(first["ok"], msg=first)
        self.assertTrue(second["ok"], msg=second)
        self.assertFalse(first["idempotent_replay"])
        self.assertTrue(second["idempotent_replay"])

    def test_success_notification_refuses_incomplete_truth(self) -> None:
        module = load_module("chat_final_delivery_notify_incomplete", SCRIPT_PATH)
        _, authority_path, _ = self.create_authority_fixture(platform="discord", status="completed", stage="handoff")
        payload = json.loads(authority_path.read_text(encoding="utf-8"))
        payload["artifacts"]["final_review_path"] = str(Path(payload["artifacts"]["final_review_path"]).with_name("MISSING_REVIEW.md"))
        authority_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        with self.assertRaises(module.ChatDeliveryNotifyError):
            module.deliver_final_chat_notification(authority_path, platform="discord")


if __name__ == "__main__":
    unittest.main()
