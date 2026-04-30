import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "start_approved_project_delivery.py"
EXPECTED_STAGE_VALUES = {"approval", "brief_generation"}
EXPECTED_STATUS_VALUES = {"ready", "blocked"}
EXPECTED_BLOCK_REASONS = {
    "missing_approval_evidence",
    "missing_project_identity",
    "missing_target_user",
    "missing_mvp_framing",
    "missing_approved_scope",
    "missing_constraints",
    "missing_acceptance_gates",
    "missing_template_contract_path",
    "missing_gsd_constraints_path",
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


class ApprovedProjectRecordTests(unittest.TestCase):
    maxDiff = None

    def addCleanupPath(self, path: Path) -> None:
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))

    def build_payload(self) -> dict[str, object]:
        return {
            "approval_id": "APR-2026-04-27-01",
            "approved_at": "2026-04-27T08:30:00Z",
            "approver": "owner",
            "approval_evidence": {
                "decision_record": "assets/shared/CORP_CULTURE.md#greenlight-2026-04-27",
                "summary": "Approved after confirming market pull and template fit.",
            },
            "project_name": "Lead Capture Copilot",
            "project_url": "https://lead-capture.example.com",
            "target_user": "Solo operators who need to qualify inbound leads quickly.",
            "mvp_framing": "Turn incoming lead notes into ranked follow-up actions.",
            "approved_scope": [
                "capture inbound lead notes",
                "score urgency and intent",
                "show daily follow-up queue",
            ],
            "constraints": [
                "reuse shared Supabase auth and payments",
                "keep delivery scope approved-brief-only",
            ],
            "acceptance_gates": [
                "brief generated",
                "workspace bootstrap ready",
            ],
        }

    def test_d01_d02_d10_d11_builds_stable_authority_record(self) -> None:
        start_approved_delivery = load_module("start_approved_project_delivery", SCRIPT_PATH)
        record = start_approved_delivery.build_approved_project_record(self.build_payload())

        self.assertTrue(record["ok"])
        self.assertEqual(record["stage"], "approval")
        self.assertEqual(record["status"], "ready")
        self.assertIsNone(record["block_reason"])
        self.assertEqual(set(record["allowed_stage_values"]), EXPECTED_STAGE_VALUES)
        self.assertEqual(set(record["allowed_status_values"]), EXPECTED_STATUS_VALUES)
        self.assertEqual(set(record["allowed_block_reasons"]), EXPECTED_BLOCK_REASONS)

        approved_project = record["approved_project"]
        self.assertEqual(
            list(approved_project.keys()),
            [
                "approval",
                "project_identity",
                "approved_scope",
                "target_user",
                "mvp_framing",
                "constraints",
                "acceptance_gates",
                "pipeline",
                "artifacts",
            ],
        )

        self.assertEqual(
            approved_project["approval"],
            {
                "approval_id": "APR-2026-04-27-01",
                "approved_at": "2026-04-27T08:30:00Z",
                "approver": "owner",
                "evidence": {
                    "decision_record": "assets/shared/CORP_CULTURE.md#greenlight-2026-04-27",
                    "summary": "Approved after confirming market pull and template fit.",
                },
            },
        )
        self.assertEqual(
            approved_project["project_identity"],
            {
                "project_slug": "lead-capture-copilot",
                "app_key": "lead_capture_copilot",
                "app_name": "Lead Capture Copilot",
                "app_url": "https://lead-capture.example.com",
            },
        )
        self.assertEqual(approved_project["pipeline"], {"stage": "approval", "status": "ready", "block_reason": None})
        self.assertEqual(
            approved_project["artifacts"],
            {
                "project_directory": "assets/shared/approved-projects/lead-capture-copilot",
                "authority_record_path": "assets/shared/approved-projects/lead-capture-copilot/APPROVED_PROJECT.json",
                "delivery_brief_path": "assets/shared/approved-projects/lead-capture-copilot/PROJECT_BRIEF.md",
                "template_contract_path": "docs/platform/standalone-saas-template-contract.md",
                "project_metadata_path": ".hermes/project-metadata.json",
                "shared_backend_guardrails_path": ".hermes/shared-backend-guardrails.json",
                "approved_brief_entrypoint_path": ".hermes/PROJECT_BRIEF_ENTRYPOINT.md",
                "gsd_constraints_path": ".planning/phases/09-claude-code-delivery-team-orchestration/09-01-PLAN.md",
            },
        )

    def test_bundle_write_uses_custom_approved_projects_root_for_persisted_artifact_paths(self) -> None:
        start_approved_delivery = load_module("start_approved_project_delivery", SCRIPT_PATH)
        payload = self.build_payload()
        custom_root = Path(tempfile.mkdtemp(prefix="approved-project-root-"))
        self.addCleanupPath(custom_root)

        result = start_approved_delivery.write_approved_project_bundle(payload, approved_projects_root=custom_root)

        self.assertTrue(result["ok"], msg=result)
        project_dir = custom_root / "lead-capture-copilot"
        authority_path = project_dir / "APPROVED_PROJECT.json"
        brief_path = project_dir / "PROJECT_BRIEF.md"
        self.assertEqual(result["authority_record_path"], authority_path.as_posix())
        self.assertEqual(result["delivery_brief_path"], brief_path.as_posix())
        persisted = json.loads(authority_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted["artifacts"]["project_directory"], project_dir.as_posix())
        self.assertEqual(persisted["artifacts"]["authority_record_path"], authority_path.as_posix())
        self.assertEqual(persisted["artifacts"]["delivery_brief_path"], brief_path.as_posix())
        self.assertEqual(persisted["artifacts"]["events_path"], (project_dir / "approved-delivery-events.jsonl").as_posix())
        self.assertEqual(persisted["artifacts"]["status_path"], (project_dir / "DELIVERY_PIPELINE_STATUS.md").as_posix())

    def test_d13_d14_returns_blocked_result_for_missing_required_inputs(self) -> None:
        start_approved_delivery = load_module("start_approved_project_delivery", SCRIPT_PATH)
        payload = self.build_payload()
        payload["approval_evidence"] = {}
        payload["target_user"] = ""

        record = start_approved_delivery.build_approved_project_record(payload)

        self.assertFalse(record["ok"])
        self.assertEqual(record["stage"], "approval")
        self.assertEqual(record["status"], "blocked")
        self.assertEqual(record["block_reason"], "missing_approval_evidence")
        self.assertEqual(
            record["missing"],
            ["approval_evidence", "target_user"],
        )
        approved_project = record["approved_project"]
        self.assertEqual(approved_project["pipeline"], {"stage": "approval", "status": "blocked", "block_reason": "missing_approval_evidence"})
        self.assertEqual(approved_project["approval"]["evidence"], {})
        self.assertEqual(approved_project["target_user"], "")


if __name__ == "__main__":
    unittest.main()
