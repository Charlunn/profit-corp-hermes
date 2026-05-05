import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "start_approved_project_delivery.py"
APPROVAL_SCRIPT_PATH = ROOT_DIR / "scripts" / "request_governance_approval.py"


def load_module(module_name: str, script_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ChatApprovalFlowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module("start_approved_project_delivery_chat_approval", SCRIPT_PATH)
        self.approval_module = load_module("request_governance_approval_chat", APPROVAL_SCRIPT_PATH)

    def addCleanupPath(self, path: Path) -> None:
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))

    def create_authority_record(self, root: Path) -> Path:
        project_dir = root / "assets" / "shared" / "approved-projects" / "lead-capture-copilot"
        project_dir.mkdir(parents=True, exist_ok=True)
        authority_path = project_dir / "APPROVED_PROJECT.json"
        payload = {
            "approval": {
                "approval_id": "APR-2026-04-27-01",
                "approved_at": "",
                "approver": "",
                "evidence": {
                    "decision_record": "assets/shared/CORP_CULTURE.md#greenlight-2026-04-27",
                    "summary": "Awaiting explicit chat decision.",
                },
            },
            "proposal": {
                "proposal_id": "proposal-idea-001-v1",
                "chat_origin": {
                    "run_id": "chat-run-20260505-001",
                    "platform": "discord",
                    "channel_or_chat_id": "chan-123",
                    "thread_or_reply_context": "thr-999",
                    "origin_message_id": "origin-msg-1",
                },
                "qualification_backlinks": ["assets/shared/qualification/latest/qualification_bundle.json#IDEA-001"],
            },
            "project_identity": {
                "project_slug": "lead-capture-copilot",
                "app_key": "lead_capture_copilot",
                "app_name": "Lead Capture Copilot",
                "app_url": "https://lead-capture.example.com",
            },
            "approved_scope": ["capture inbound lead notes"],
            "target_user": "Revenue operators",
            "mvp_framing": "Turn incoming lead notes into ranked follow-up actions.",
            "product_requirements": {
                "pain_point": "Operators lose revenue because inbound leads sit unqualified for too long.",
                "monetization": ["https://example.com/pricing"],
                "required_languages": ["en", "zh"],
                "ui_artifact_contract": ["Reference `/ui-ux-pro-max` output before frontend implementation."],
            },
            "constraints": ["reuse shared Supabase auth and payments"],
            "acceptance_gates": ["brief generated"],
            "pipeline": {
                "stage": "approval",
                "status": "pending",
                "block_reason": "",
                "current_stage": "approval",
                "current_status": "pending",
            },
            "artifacts": {
                "project_directory": project_dir.as_posix(),
                "authority_record_path": authority_path.as_posix(),
                "delivery_brief_path": (project_dir / "PROJECT_BRIEF.md").as_posix(),
                "events_path": (project_dir / "approved-delivery-events.jsonl").as_posix(),
                "status_path": (project_dir / "DELIVERY_PIPELINE_STATUS.md").as_posix(),
                "final_review_path": (project_dir / "FINAL_OPERATOR_REVIEW.md").as_posix(),
            },
            "shipping": {"github": {}, "vercel": {}},
        }
        authority_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return authority_path

    def test_explicit_approve_and_reject_are_governed_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.addCleanupPath(root)
            authority_path = self.create_authority_record(root)
            governance_dir = root / "assets" / "shared" / "governance"
            governance_dir.mkdir(parents=True, exist_ok=True)

            result = self.module.process_chat_approval_decision(
                authority_path,
                {
                    "platform": "discord",
                    "channel_or_chat_id": "chan-123",
                    "thread_or_reply_context": "thr-999",
                    "message_id": "reply-1",
                    "reply_text": "approve",
                    "actor": "ceo",
                },
                governance_events_path=governance_dir / "governance_events.jsonl",
                governance_status_path=governance_dir / "GOVERNANCE_STATUS.md",
            )
            self.assertTrue(result["ok"])
            self.assertEqual(result["decision"], "approved")

            duplicate = self.module.process_chat_approval_decision(
                authority_path,
                {
                    "platform": "discord",
                    "channel_or_chat_id": "chan-123",
                    "thread_or_reply_context": "thr-999",
                    "message_id": "reply-1",
                    "reply_text": "approve",
                    "actor": "ceo",
                },
                governance_events_path=governance_dir / "governance_events.jsonl",
                governance_status_path=governance_dir / "GOVERNANCE_STATUS.md",
            )
            self.assertTrue(duplicate["ok"])
            self.assertTrue(duplicate["idempotent_replay"])

    def test_ambiguous_or_unlinked_reply_blocks(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.addCleanupPath(root)
            authority_path = self.create_authority_record(root)
            governance_dir = root / "assets" / "shared" / "governance"
            governance_dir.mkdir(parents=True, exist_ok=True)

            ambiguous = self.module.process_chat_approval_decision(
                authority_path,
                {
                    "platform": "discord",
                    "channel_or_chat_id": "chan-123",
                    "thread_or_reply_context": "thr-999",
                    "message_id": "reply-2",
                    "reply_text": "sounds good",
                    "actor": "ceo",
                },
                governance_events_path=governance_dir / "governance_events.jsonl",
                governance_status_path=governance_dir / "GOVERNANCE_STATUS.md",
            )
            self.assertFalse(ambiguous["ok"])
            self.assertEqual(ambiguous["block_reason"], "ambiguous_chat_approval_reply")

            unlinked = self.module.process_chat_approval_decision(
                authority_path,
                {
                    "platform": "discord",
                    "channel_or_chat_id": "wrong-channel",
                    "thread_or_reply_context": "thr-999",
                    "message_id": "reply-3",
                    "reply_text": "reject",
                    "actor": "ceo",
                },
                governance_events_path=governance_dir / "governance_events.jsonl",
                governance_status_path=governance_dir / "GOVERNANCE_STATUS.md",
            )
            self.assertFalse(unlinked["ok"])
            self.assertEqual(unlinked["block_reason"], "unlinked_chat_approval_reply")

    def test_reply_adapter_accepts_explicit_approve_reject_and_blocks_ambiguous(self) -> None:
        proposal = {
            "proposal_id": "proposal-idea-001-v1",
            "chat_origin": {
                "run_id": "chat-run-20260505-001",
                "platform": "discord",
                "channel_or_chat_id": "chan-123",
                "thread_or_reply_context": "thr-999",
            },
        }
        approved = self.approval_module.resolve_chat_approval_reply(
            proposal,
            {
                "platform": "discord",
                "channel_or_chat_id": "chan-123",
                "thread_or_reply_context": "thr-999",
                "message_id": "reply-approve",
                "reply_text": "approve proposal",
            },
        )
        rejected = self.approval_module.resolve_chat_approval_reply(
            proposal,
            {
                "platform": "discord",
                "channel_or_chat_id": "chan-123",
                "thread_or_reply_context": "thr-999",
                "message_id": "reply-reject",
                "reply_text": "reject",
            },
        )
        ambiguous = self.approval_module.resolve_chat_approval_reply(
            proposal,
            {
                "platform": "discord",
                "channel_or_chat_id": "chan-123",
                "thread_or_reply_context": "thr-999",
                "message_id": "reply-ambiguous",
                "reply_text": "looks promising",
            },
        )
        self.assertTrue(approved["ok"])
        self.assertEqual(approved["decision"], "approved")
        self.assertTrue(rejected["ok"])
        self.assertEqual(rejected["decision"], "rejected")
        self.assertFalse(ambiguous["ok"])
        self.assertEqual(ambiguous["block_reason"], "ambiguous_chat_approval_reply")


if __name__ == "__main__":
    unittest.main()
