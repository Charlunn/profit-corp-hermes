import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "start_chat_project_run.py"


def load_module(module_name: str, script_path: Path):
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ChatRunBootstrapTests(unittest.TestCase):
    def setUp(self) -> None:
        self.module = load_module("start_chat_project_run", SCRIPT_PATH)

    def addCleanupPath(self, path: Path) -> None:
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))

    def discord_payload(self) -> dict:
        return {
            "platform": "discord",
            "channel_id": "chan-123",
            "thread_id": "thr-999",
            "message_id": "msg-1",
            "content": "@Hermes start a project for abandoned cart recovery",
            "timestamp": "2026-05-04T12:00:00Z",
            "author": {"id": "user-1", "display_name": "Taylor", "username": "taylor"},
        }

    def hermes_payload(self) -> dict:
        return {
            "platform": "hermes",
            "conversation": {"id": "owner-thread-9"},
            "request": {
                "id": "req-42",
                "text": "Start a project for abandoned cart recovery and qualify the demand.",
                "received_at": "2026-05-05T08:00:00Z",
            },
            "owner": {"id": "owner-1", "display_name": "Taylor", "username": "taylor"},
            "provenance": {"surface": "hermes-web", "session_id": "session-77"},
        }

    def test_bootstrap_writes_authority_and_events_before_dispatch(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chat_root = root / "assets" / "shared" / "chat-runs"
            with mock.patch.object(self.module, "ROOT_DIR", root), \
                 mock.patch.object(self.module, "run_dir_for", side_effect=lambda run_id: chat_root / run_id), \
                 mock.patch.object(self.module, "authority_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN.json"), \
                 mock.patch.object(self.module, "status_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN_STATUS.md"), \
                 mock.patch("scripts.chat_intake_common.CHAT_RUNS_ROOT", chat_root):
                dispatched_records: list[dict] = []

                def fake_dispatch(record: dict) -> dict:
                    authority_path = chat_root / record["run_id"] / "CHAT_RUN.json"
                    self.assertTrue(authority_path.exists())
                    dispatched_records.append(json.loads(authority_path.read_text(encoding="utf-8")))
                    return {
                        "ok": True,
                        "action": "dispatched_existing_governed_startup",
                        "command": "bash orchestration/cron/commands.sh run-analysis-loop",
                        "target": "existing-discovery-startup",
                    }

                result = self.module.bootstrap_chat_project_run(self.discord_payload(), dispatch_fn=fake_dispatch)

                self.assertTrue(result["ok"])
                authority_path = Path(result["authority_record_path"])
                status_path = Path(result["status_path"])
                events_path = chat_root / "chat-run-events.jsonl"
                self.assertTrue(authority_path.exists())
                self.assertTrue(status_path.exists())
                self.assertTrue(events_path.exists())
                record = json.loads(authority_path.read_text(encoding="utf-8"))
                self.assertEqual(record["chat_origin"]["platform"], "discord")
                self.assertEqual(record["pipeline"]["stage"], "qualification")
                self.assertEqual(record["pipeline"]["status"], "running")
                self.assertEqual(record["dispatch"]["mode"], "governed-existing-pipeline")
                self.assertEqual(record["dispatch"]["target"], "existing-discovery-startup")
                self.assertEqual(len(dispatched_records), 1)
                events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
                self.assertEqual(events[0]["action"], "chat_run_initialized")

    def test_duplicate_source_message_reuses_existing_run_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chat_root = root / "assets" / "shared" / "chat-runs"
            with mock.patch.object(self.module, "ROOT_DIR", root), \
                 mock.patch.object(self.module, "run_dir_for", side_effect=lambda run_id: chat_root / run_id), \
                 mock.patch.object(self.module, "authority_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN.json"), \
                 mock.patch.object(self.module, "status_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN_STATUS.md"), \
                 mock.patch("scripts.chat_intake_common.CHAT_RUNS_ROOT", chat_root):
                first = self.module.bootstrap_chat_project_run(self.discord_payload())
                second = self.module.bootstrap_chat_project_run(self.discord_payload())
                self.assertEqual(first["run_id"], second["run_id"])
                self.assertTrue(second["idempotent_replay"])
                run_dirs = [item for item in chat_root.iterdir() if item.is_dir()]
                self.assertEqual(len(run_dirs), 1)

    def test_dispatch_failure_persists_blocked_truth(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chat_root = root / "assets" / "shared" / "chat-runs"
            with mock.patch.object(self.module, "ROOT_DIR", root), \
                 mock.patch.object(self.module, "run_dir_for", side_effect=lambda run_id: chat_root / run_id), \
                 mock.patch.object(self.module, "authority_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN.json"), \
                 mock.patch.object(self.module, "status_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN_STATUS.md"), \
                 mock.patch("scripts.chat_intake_common.CHAT_RUNS_ROOT", chat_root):
                result = self.module.bootstrap_chat_project_run(
                    self.discord_payload(),
                    dispatch_fn=lambda _record: {
                        "ok": False,
                        "action": "dispatch_failed",
                        "error": "governed startup unavailable",
                        "command": "bash orchestration/cron/commands.sh run-analysis-loop",
                        "target": "existing-discovery-startup",
                    },
                )
                self.assertFalse(result["ok"])
                record = json.loads(Path(result["authority_record_path"]).read_text(encoding="utf-8"))
                self.assertEqual(record["pipeline"]["status"], "blocked")
                self.assertEqual(record["blocked"]["reason"], "dispatch_failed")
                self.assertIn("governed startup unavailable", record["blocked"]["detail"])

    def test_hermes_bootstrap_reuses_authoritative_run_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chat_root = root / "assets" / "shared" / "chat-runs"
            with mock.patch.object(self.module, "ROOT_DIR", root), \
                 mock.patch.object(self.module, "run_dir_for", side_effect=lambda run_id: chat_root / run_id), \
                 mock.patch.object(self.module, "authority_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN.json"), \
                 mock.patch.object(self.module, "status_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN_STATUS.md"), \
                 mock.patch("scripts.chat_intake_common.CHAT_RUNS_ROOT", chat_root):
                result = self.module.bootstrap_hermes_project_run(self.hermes_payload())
                record = json.loads(Path(result["authority_record_path"]).read_text(encoding="utf-8"))
                self.assertTrue(result["ok"])
                self.assertEqual(record["chat_origin"]["platform"], "hermes")
                self.assertEqual(record["dispatch"]["mode"], "governed-existing-pipeline")
                self.assertEqual(record["pipeline"]["status"], "running")
                self.assertEqual(record["artifacts"]["authority_record_path"], result["authority_record_path"])

    def test_hermes_bootstrap_replays_same_origin_without_duplicate_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chat_root = root / "assets" / "shared" / "chat-runs"
            with mock.patch.object(self.module, "ROOT_DIR", root), \
                 mock.patch.object(self.module, "run_dir_for", side_effect=lambda run_id: chat_root / run_id), \
                 mock.patch.object(self.module, "authority_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN.json"), \
                 mock.patch.object(self.module, "status_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN_STATUS.md"), \
                 mock.patch("scripts.chat_intake_common.CHAT_RUNS_ROOT", chat_root):
                first = self.module.bootstrap_hermes_project_run(self.hermes_payload())
                second = self.module.bootstrap_hermes_project_run(self.hermes_payload())
                self.assertEqual(first["run_id"], second["run_id"])
                self.assertTrue(second["idempotent_replay"])
                run_dirs = [item for item in chat_root.iterdir() if item.is_dir()]
                self.assertEqual(len(run_dirs), 1)

    def test_hermes_bootstrap_blocks_when_required_start_metadata_is_missing(self) -> None:
        with self.assertRaises(self.module.ChatIntakeError):
            self.module.bootstrap_hermes_project_run(
                {
                    "platform": "hermes",
                    "conversation": {"id": ""},
                    "request": {"id": "", "text": "", "received_at": ""},
                    "owner": {"id": "owner-1", "display_name": "", "username": ""},
                    "provenance": {"surface": "", "session_id": ""},
                }
            )

    def test_status_renderer_uses_hermes_language_for_healthy_start(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chat_root = root / "assets" / "shared" / "chat-runs"
            with mock.patch.object(self.module, "ROOT_DIR", root), \
                 mock.patch.object(self.module, "run_dir_for", side_effect=lambda run_id: chat_root / run_id), \
                 mock.patch.object(self.module, "authority_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN.json"), \
                 mock.patch.object(self.module, "status_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN_STATUS.md"), \
                 mock.patch("scripts.chat_intake_common.CHAT_RUNS_ROOT", chat_root):
                result = self.module.bootstrap_hermes_project_run(self.hermes_payload())
                status_text = Path(result["status_path"]).read_text(encoding="utf-8")
                self.assertIn("Request accepted", status_text)
                self.assertIn("Hermes is preparing the governed project run", status_text)
                self.assertNotIn("run-analysis-loop", status_text)
                self.assertNotIn("phase", status_text.lower())
                self.assertIn(result["authority_record_path"], status_text)

    def test_status_renderer_reports_truthful_hermes_blocker_with_artifact_paths(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chat_root = root / "assets" / "shared" / "chat-runs"
            with mock.patch.object(self.module, "ROOT_DIR", root), \
                 mock.patch.object(self.module, "run_dir_for", side_effect=lambda run_id: chat_root / run_id), \
                 mock.patch.object(self.module, "authority_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN.json"), \
                 mock.patch.object(self.module, "status_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN_STATUS.md"), \
                 mock.patch("scripts.chat_intake_common.CHAT_RUNS_ROOT", chat_root):
                result = self.module.bootstrap_hermes_project_run(
                    self.hermes_payload(),
                    dispatch_fn=lambda _record: {
                        "ok": False,
                        "action": "dispatch_failed",
                        "error": "governed startup unavailable",
                        "command": "bash orchestration/cron/commands.sh run-analysis-loop",
                        "target": "existing-discovery-startup",
                    },
                )
                status_text = Path(result["status_path"]).read_text(encoding="utf-8")
                self.assertIn("Start blocked", status_text)
                self.assertIn("governed startup unavailable", status_text)
                self.assertIn(result["authority_record_path"], status_text)
                self.assertIn(result["status_path"], status_text)

    def test_status_renderer_summarizes_internal_role_progress_without_exposing_commands(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chat_root = root / "assets" / "shared" / "chat-runs"
            with mock.patch.object(self.module, "ROOT_DIR", root), \
                 mock.patch.object(self.module, "run_dir_for", side_effect=lambda run_id: chat_root / run_id), \
                 mock.patch.object(self.module, "authority_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN.json"), \
                 mock.patch.object(self.module, "status_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN_STATUS.md"), \
                 mock.patch("scripts.chat_intake_common.CHAT_RUNS_ROOT", chat_root):
                result = self.module.bootstrap_hermes_project_run(self.hermes_payload())
                authority_path = Path(result["authority_record_path"])
                record = json.loads(authority_path.read_text(encoding="utf-8"))
                record["pipeline"]["stage"] = "qualification"
                record["pipeline"]["status"] = "running"
                record["role_routing"] = {
                    "current_role": "scout",
                    "workstream": "discovery research",
                    "artifact_path": "assets/shared/qualification/latest/scout-discovery.md",
                    "next_handoff": "cmo_market_plan",
                }
                authority_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                self.module.render_chat_run_status(result["run_id"], str(chat_root / result["run_id"]))
                status_text = Path(result["status_path"]).read_text(encoding="utf-8")
                self.assertIn("discovery research", status_text)
                self.assertNotIn("scout chat", status_text.lower())
                self.assertIn("scout-discovery.md", status_text)

    def test_status_renderer_names_responsible_role_for_blocked_internal_handoff(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            chat_root = root / "assets" / "shared" / "chat-runs"
            with mock.patch.object(self.module, "ROOT_DIR", root), \
                 mock.patch.object(self.module, "run_dir_for", side_effect=lambda run_id: chat_root / run_id), \
                 mock.patch.object(self.module, "authority_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN.json"), \
                 mock.patch.object(self.module, "status_path_for", side_effect=lambda run_id: chat_root / run_id / "CHAT_RUN_STATUS.md"), \
                 mock.patch("scripts.chat_intake_common.CHAT_RUNS_ROOT", chat_root):
                result = self.module.bootstrap_hermes_project_run(self.hermes_payload())
                authority_path = Path(result["authority_record_path"])
                record = json.loads(authority_path.read_text(encoding="utf-8"))
                record["pipeline"]["status"] = "blocked"
                record["blocked"]["detail"] = "Market proof is incomplete."
                record["role_routing"] = {
                    "current_role": "cmo",
                    "workstream": "proposal preparation",
                    "artifact_path": "assets/shared/proposals/latest/market-proof.md",
                    "next_handoff": "approval",
                }
                authority_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
                self.module.render_chat_run_status(result["run_id"], str(chat_root / result["run_id"]))
                status_text = Path(result["status_path"]).read_text(encoding="utf-8")
                self.assertIn("cmo", status_text.lower())
                self.assertIn("Market proof is incomplete.", status_text)
                self.assertIn("market-proof.md", status_text)


if __name__ == "__main__":
    unittest.main()
