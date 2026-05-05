import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT_DIR = Path(__file__).resolve().parent.parent
INTAKE_SCRIPT = ROOT_DIR / "scripts" / "chat_intake_common.py"
START_SCRIPT = ROOT_DIR / "scripts" / "start_chat_project_run.py"


def load_module(module_name: str, script_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ChatOriginContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.intake_module = load_module("chat_intake_common_contract", INTAKE_SCRIPT)
        self.start_module = load_module("start_chat_project_run_contract", START_SCRIPT)

    def payload(self) -> dict:
        return {
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

    def test_chat_origin_fields_remain_stable_when_reread_from_disk(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chat_root = root / "assets" / "shared" / "chat-runs"
            with mock.patch.object(self.start_module, "ROOT_DIR", root), \
                 mock.patch.object(self.start_module, "run_dir_for", side_effect=lambda run_id: chat_root / run_id), \
                 mock.patch.object(self.start_module, "authority_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN.json"), \
                 mock.patch.object(self.start_module, "status_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN_STATUS.md"), \
                 mock.patch("scripts.chat_intake_common.CHAT_RUNS_ROOT", chat_root):
                result = self.start_module.bootstrap_chat_project_run(self.payload())
                record = json.loads(Path(result["authority_record_path"]).read_text(encoding="utf-8"))
                reread = json.loads(Path(result["authority_record_path"]).read_text(encoding="utf-8"))
                self.assertEqual(record["chat_origin"]["origin_key"], reread["chat_origin"]["origin_key"])
                self.assertEqual(record["chat_origin"]["run_id"], reread["chat_origin"]["run_id"])
                self.assertEqual(record["chat_origin"]["thread_or_reply_context"], "700")


if __name__ == "__main__":
    unittest.main()
