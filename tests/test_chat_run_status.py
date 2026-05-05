import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "render_chat_run_status.py"


def load_module(module_name: str, script_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ChatRunStatusTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module("render_chat_run_status", SCRIPT_PATH)

    def build_record(self) -> dict:
        return {
            "run_id": "chat-run-20260504-abcdef123456",
            "chat_origin": {
                "platform": "discord",
                "channel_or_chat_id": "chan-123",
                "thread_or_reply_context": "thr-999",
                "requester": {"id": "user-1", "display_name": "Taylor", "username": "taylor"},
                "message_id": "msg-1",
                "intent": "@Hermes start a project for abandoned cart recovery",
            },
            "pipeline": {"stage": "qualification", "status": "running"},
            "dispatch": {
                "mode": "governed-existing-pipeline",
                "target": "existing-discovery-startup",
                "command": "bash orchestration/cron/commands.sh run-analysis-loop",
            },
            "blocked": {"reason": ""},
        }

    def test_renderer_derives_operator_visible_status_from_authority_record(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            project_dir = Path(tmp)
            (project_dir / "CHAT_RUN.json").write_text(json.dumps(self.build_record(), ensure_ascii=False, indent=2), encoding="utf-8")
            markdown = self.module.render_chat_run_status("chat-run-20260504-abcdef123456", project_dir.as_posix())
            self.assertIn("discord", markdown)
            self.assertIn("chan-123", markdown)
            self.assertIn("Taylor", markdown)
            self.assertIn("qualification", markdown)
            self.assertIn("existing-discovery-startup", markdown)
            self.assertTrue((project_dir / "CHAT_RUN_STATUS.md").exists())


if __name__ == "__main__":
    unittest.main()
