import json
import shutil
import tempfile
import unittest
from pathlib import Path
import importlib.util


ROOT_DIR = Path(__file__).resolve().parent.parent
APPEND_SCRIPT_PATH = ROOT_DIR / "scripts" / "append_delivery_event.py"
RENDER_SCRIPT_PATH = ROOT_DIR / "scripts" / "render_delivery_status.py"
REQUIRED_EVENT_FIELDS = [
    "run_id",
    "workspace_name",
    "role",
    "stage",
    "action",
    "artifact",
    "timestamp",
    "outcome",
]
VALID_EVENT = {
    "run_id": "delivery-20260427-001",
    "workspace_name": "lead-capture",
    "role": "testing-specialist",
    "stage": "testing",
    "action": "stage_completed",
    "artifact": ".hermes/stage-handoffs/03-testing.md",
    "timestamp": "2026-04-27T10:30:00Z",
    "outcome": "pass",
    "gate_status": "open",
    "scope_status": "approved-brief-only",
}


def load_module(module_name: str, script_path: Path):
    if not script_path.exists():
        raise AssertionError(f"expected script to exist: {script_path}")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeliveryEventsTests(unittest.TestCase):
    maxDiff = None

    def addCleanupPath(self, path: Path) -> None:
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))

    def create_workspace_fixture(self) -> Path:
        workspace_root = Path(tempfile.mkdtemp(prefix="delivery-events-workspace-"))
        self.addCleanupPath(workspace_root)
        workspace = workspace_root / "lead-capture"
        hermes_dir = workspace / ".hermes"
        handoffs_dir = hermes_dir / "stage-handoffs"
        handoffs_dir.mkdir(parents=True, exist_ok=True)
        (hermes_dir / "delivery-events.jsonl").write_text("", encoding="utf-8")
        return workspace

    def read_events(self, workspace: Path) -> list[dict]:
        events_path = workspace / ".hermes" / "delivery-events.jsonl"
        lines = [line for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        return [json.loads(line) for line in lines]

    def test_d10_event_writer_requires_explicit_role_attributed_schema(self) -> None:
        append_delivery_event = load_module("append_delivery_event", APPEND_SCRIPT_PATH)
        workspace = self.create_workspace_fixture()
        for field in REQUIRED_EVENT_FIELDS:
            event = dict(VALID_EVENT)
            event.pop(field)
            with self.assertRaises(Exception, msg=f"D-10 should reject missing field: {field}"):
                append_delivery_event.append_delivery_event(workspace, event)
        self.assertEqual(self.read_events(workspace), [], "invalid events must not be written")

    def test_d10_d12_event_writer_appends_valid_jsonl_entries_only(self) -> None:
        append_delivery_event = load_module("append_delivery_event", APPEND_SCRIPT_PATH)
        workspace = self.create_workspace_fixture()
        first = dict(VALID_EVENT)
        second = dict(VALID_EVENT)
        second.update(
            {
                "role": "release-readiness-specialist",
                "stage": "release readiness",
                "action": "status_render_requested",
                "artifact": ".hermes/DELIVERY_STATUS.md",
                "timestamp": "2026-04-27T10:45:00Z",
                "outcome": "pass",
            }
        )
        append_delivery_event.append_delivery_event(workspace, first)
        append_delivery_event.append_delivery_event(workspace, second)
        events = self.read_events(workspace)
        self.assertEqual(len(events), 2)
        self.assertEqual(events[0]["timestamp"], "2026-04-27T10:30:00Z")
        self.assertEqual(events[1]["timestamp"], "2026-04-27T10:45:00Z")
        self.assertEqual(events[0]["workspace_name"], "lead-capture")
        self.assertEqual(events[1]["artifact"], ".hermes/DELIVERY_STATUS.md")

    def test_d11_status_renderer_derives_latest_markdown_view_from_jsonl(self) -> None:
        append_delivery_event = load_module("append_delivery_event", APPEND_SCRIPT_PATH)
        render_delivery_status = load_module("render_delivery_status", RENDER_SCRIPT_PATH)
        workspace = self.create_workspace_fixture()
        append_delivery_event.append_delivery_event(
            workspace,
            {
                "run_id": "delivery-20260427-001",
                "workspace_name": "lead-capture",
                "role": "development-specialist",
                "stage": "development",
                "action": "stage_started",
                "artifact": ".hermes/stage-handoffs/02-development.md",
                "timestamp": "2026-04-27T10:15:00Z",
                "outcome": "in_progress",
                "gate_status": "open",
                "scope_status": "approved-brief-only",
            },
        )
        append_delivery_event.append_delivery_event(workspace, VALID_EVENT)
        render_delivery_status.render_delivery_status(workspace)
        status_path = workspace / ".hermes" / "DELIVERY_STATUS.md"
        self.assertTrue(status_path.exists(), "D-11 should write DELIVERY_STATUS.md")
        status_text = status_path.read_text(encoding="utf-8")
        self.assertIn("delivery-events.jsonl", status_text)
        self.assertIn("delivery-20260427-001", status_text)
        self.assertIn("lead-capture", status_text)
        self.assertIn("testing", status_text)
        self.assertIn("testing-specialist", status_text)
        self.assertIn("stage_completed", status_text)
        self.assertIn("approved-brief-only", status_text)
        self.assertIn("open", status_text)
        self.assertIn(".hermes/stage-handoffs/03-testing.md", status_text)


if __name__ == "__main__":
    unittest.main()
