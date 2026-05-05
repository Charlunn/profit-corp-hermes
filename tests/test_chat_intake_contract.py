import importlib.util
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "chat_intake_common.py"


def load_module(module_name: str, script_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ChatIntakeContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module("chat_intake_common", SCRIPT_PATH)

    def addCleanupPath(self, path: Path) -> None:
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))

    def test_normalize_discord_payload_into_canonical_contract(self) -> None:
        payload = {
            "platform": "discord",
            "channel_id": "chan-123",
            "thread_id": "thr-999",
            "message_id": "msg-1",
            "content": "@Hermes start a project for abandoned cart recovery",
            "timestamp": "2026-05-04T12:00:00Z",
            "author": {"id": "user-1", "display_name": "Taylor", "username": "taylor"},
        }

        envelope = self.module.normalize_chat_payload(payload)

        self.assertEqual(envelope["platform"], "discord")
        self.assertEqual(envelope["channel_or_chat_id"], "chan-123")
        self.assertEqual(envelope["thread_or_reply_context"], "thr-999")
        self.assertEqual(envelope["message_id"], "msg-1")
        self.assertEqual(envelope["requester"]["display_name"], "Taylor")
        self.assertIn("abandoned cart recovery", envelope["intent"])
        self.assertTrue(envelope["run_id"].startswith("chat-run-20260504-"))

    def test_normalize_telegram_payload_into_same_contract(self) -> None:
        payload = {
            "platform": "telegram",
            "chat": {"id": "chat-444"},
            "message": {
                "message_id": "777",
                "text": "/hermes validate a pricing workflow idea",
                "date": "2026-05-04T13:00:00Z",
                "from": {"id": "user-7", "display_name": "Morgan", "username": "morgan"},
            },
            "from": {"id": "user-7", "display_name": "Morgan", "username": "morgan"},
            "reply_to_message": {"message_id": "700"},
        }

        envelope = self.module.normalize_chat_payload(payload)

        self.assertEqual(envelope["platform"], "telegram")
        self.assertEqual(envelope["channel_or_chat_id"], "chat-444")
        self.assertEqual(envelope["thread_or_reply_context"], "700")
        self.assertEqual(envelope["requester"]["id"], "user-7")
        self.assertEqual(envelope["message_id"], "777")

    def test_missing_provenance_blocks_for_both_platform_shapes(self) -> None:
        bad_discord = {
            "platform": "discord",
            "channel_id": "chan-123",
            "content": "@Hermes start",
            "timestamp": "2026-05-04T12:00:00Z",
            "author": {"id": "", "display_name": "", "username": ""},
        }
        bad_telegram = {
            "platform": "telegram",
            "chat": {"id": ""},
            "message": {"message_id": "", "text": "", "date": ""},
            "from": {"id": "u", "display_name": "", "username": ""},
        }
        with self.assertRaises(self.module.ChatIntakeError):
            self.module.normalize_chat_payload(bad_discord)
        with self.assertRaises(self.module.ChatIntakeError):
            self.module.normalize_chat_payload(bad_telegram)

    def test_origin_key_is_stable_for_same_source_message(self) -> None:
        payload = {
            "platform": "discord",
            "channel_id": "chan-123",
            "thread_id": "thr-999",
            "message_id": "msg-1",
            "content": "@Hermes start a project for abandoned cart recovery",
            "timestamp": "2026-05-04T12:00:00Z",
            "author": {"id": "user-1", "display_name": "Taylor", "username": "taylor"},
        }
        first = self.module.normalize_chat_payload(payload)
        second = self.module.normalize_chat_payload(payload)
        self.assertEqual(first["origin_key"], second["origin_key"])
        self.assertEqual(first["run_id"], second["run_id"])


if __name__ == "__main__":
    unittest.main()
