import json
import shutil
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
import importlib.util


ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "request_scope_reopen.py"
GOVERNANCE_EVENTS_PATH = ROOT_DIR / "assets" / "shared" / "governance" / "governance_events.jsonl"
GOVERNANCE_STATUS_PATH = ROOT_DIR / "assets" / "shared" / "governance" / "GOVERNANCE_STATUS.md"
REQUESTED_TARGET = "src/lib/paypal.ts"


def load_module(module_name: str, script_path: Path):
    if not script_path.exists():
        raise AssertionError(f"expected script to exist: {script_path}")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ScopeReopenFlowTests(unittest.TestCase):
    maxDiff = None

    def addCleanupPath(self, path: Path) -> None:
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))

    def create_workspace_fixture(self) -> Path:
        workspace_root = Path(tempfile.mkdtemp(prefix="scope-reopen-workspace-"))
        self.addCleanupPath(workspace_root)
        workspace = workspace_root / "lead-capture"
        hermes_dir = workspace / ".hermes"
        handoffs_dir = hermes_dir / "stage-handoffs"
        handoffs_dir.mkdir(parents=True, exist_ok=True)

        manifest = {
            "run_id": "delivery-lead-capture-001",
            "workspace_name": "lead-capture",
            "orchestrator_role": "delivery-orchestrator",
            "scope_status": "approved-brief-only",
            "authority_stream": ".hermes/delivery-events.jsonl",
            "latest_status_path": ".hermes/DELIVERY_STATUS.md",
        }
        (hermes_dir / "delivery-run-manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        (hermes_dir / "delivery-events.jsonl").write_text(
            json.dumps(
                {
                    "run_id": manifest["run_id"],
                    "workspace_name": manifest["workspace_name"],
                    "role": "development-specialist",
                    "stage": "development",
                    "action": "stage_started",
                    "artifact": ".hermes/stage-handoffs/02-development.md",
                    "timestamp": "2026-04-27T10:15:00Z",
                    "outcome": "in_progress",
                    "gate_status": "open",
                    "scope_status": "approved-brief-only",
                }
            )
            + "\n",
            encoding="utf-8",
        )
        return workspace

    def read_jsonl(self, path: Path) -> list[dict]:
        if not path.exists():
            return []
        return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    @contextmanager
    def preserve_governance_files(self):
        snapshots: dict[Path, tuple[bool, str]] = {}
        for path in (GOVERNANCE_EVENTS_PATH, GOVERNANCE_STATUS_PATH):
            snapshots[path] = (path.exists(), path.read_text(encoding="utf-8") if path.exists() else "")
        try:
            yield
        finally:
            for path, (existed, content) in snapshots.items():
                if existed:
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(content, encoding="utf-8")
                elif path.exists():
                    path.unlink()

    def test_team04_team06_protected_change_requests_governed_scope_reopen(self) -> None:
        request_scope_reopen = load_module("request_scope_reopen", SCRIPT_PATH)
        workspace = self.create_workspace_fixture()
        with self.preserve_governance_files():
            result = request_scope_reopen.request_scope_reopen(
                workspace,
                run_id="delivery-lead-capture-001",
                stage="development",
                role="development-specialist",
                target_artifact=REQUESTED_TARGET,
                reason="Need to modify protected PayPal helper for a product-specific upsell flow.",
            )

            self.assertTrue(result["ok"], msg=result)
            self.assertEqual(result["delivery_event"]["action"], "scope_reopen_requested")
            self.assertEqual(result["delivery_event"]["gate_status"], "pending")
            self.assertEqual(result["delivery_event"]["outcome"], "pending")
            self.assertEqual(result["delivery_event"]["scope_status"], "scope-reopen-requested")
            self.assertEqual(result["delivery_event"]["artifact"], REQUESTED_TARGET)

            governance_events = self.read_jsonl(GOVERNANCE_EVENTS_PATH)
            self.assertGreaterEqual(len(governance_events), 1)
            latest_governance = governance_events[-1]
            self.assertEqual(latest_governance["event_type"], "requested")
            self.assertEqual(latest_governance["status_after"], "pending")
            self.assertEqual(latest_governance["target_artifact"], REQUESTED_TARGET)
            self.assertEqual(latest_governance["action_id"], result["action_id"])

            delivery_events = self.read_jsonl(workspace / ".hermes" / "delivery-events.jsonl")
            self.assertEqual(delivery_events[-1]["action"], "scope_reopen_requested")
            self.assertEqual(delivery_events[-1]["artifact"], REQUESTED_TARGET)
            self.assertEqual(delivery_events[-1]["scope_status"], "scope-reopen-requested")

            status_text = (workspace / ".hermes" / "DELIVERY_STATUS.md").read_text(encoding="utf-8")
            self.assertIn("scope_reopen_requested", status_text)
            self.assertIn("pending", status_text)
            self.assertIn(REQUESTED_TARGET, status_text)

    def test_team04_team05_out_of_brief_request_stops_at_pending_reopen(self) -> None:
        request_scope_reopen = load_module("request_scope_reopen", SCRIPT_PATH)
        workspace = self.create_workspace_fixture()
        with self.preserve_governance_files():
            result = request_scope_reopen.request_scope_reopen(
                workspace,
                run_id="delivery-lead-capture-001",
                stage="design",
                role="design-specialist",
                target_artifact="docs/product-expansion.md",
                reason="Add a second premium workflow that is outside the approved brief.",
            )

            self.assertTrue(result["ok"], msg=result)
            self.assertEqual(result["delivery_event"]["action"], "scope_reopen_requested")
            self.assertEqual(result["delivery_event"]["outcome"], "pending")
            self.assertEqual(result["delivery_event"]["gate_status"], "pending")
            self.assertEqual(result["delivery_event"]["scope_status"], "scope-reopen-requested")
            self.assertEqual(result["governance_event"]["status_after"], "pending")
            self.assertIn("delivery.scope_reopen", result["governance_event"]["action_type"])

            delivery_events = self.read_jsonl(workspace / ".hermes" / "delivery-events.jsonl")
            self.assertEqual(len(delivery_events), 2)
            self.assertNotEqual(delivery_events[-1]["action"], "stage_completed")


if __name__ == "__main__":
    unittest.main()
