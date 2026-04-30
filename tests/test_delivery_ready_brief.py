import importlib.util
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "start_approved_project_delivery.py"
EXPECTED_SECTION_ORDER = [
    "# Approved Project Brief",
    "## Project Identity",
    "## Approved Scope",
    "## Target User",
    "## MVP Framing",
    "## Constraints",
    "## Acceptance Gates",
]
EXPECTED_BULLETS = [
    "- Project slug:",
    "- App key:",
    "- App name:",
    "- App URL:",
]


def load_module(module_name: str, script_path: Path):
    if not script_path.exists():
        raise AssertionError(f"expected script to exist: {script_path}")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class DeliveryReadyBriefTests(unittest.TestCase):
    maxDiff = None

    def build_record(self) -> dict[str, object]:
        return {
            "approval": {
                "approval_id": "APR-2026-04-27-01",
                "approved_at": "2026-04-27T08:30:00Z",
                "approver": "owner",
                "evidence": {
                    "decision_record": "assets/shared/CORP_CULTURE.md#greenlight-2026-04-27",
                    "summary": "Approved after confirming market pull and template fit.",
                },
            },
            "project_identity": {
                "project_slug": "lead-capture-copilot",
                "app_key": "lead_capture_copilot",
                "app_name": "Lead Capture Copilot",
                "app_url": "https://lead-capture.example.com",
            },
            "approved_scope": [
                "capture inbound lead notes",
                "score urgency and intent",
                "show daily follow-up queue",
            ],
            "target_user": "Solo operators who need to qualify inbound leads quickly.",
            "mvp_framing": "Turn incoming lead notes into ranked follow-up actions.",
            "constraints": [
                "reuse shared Supabase auth and payments",
                "keep delivery scope approved-brief-only",
            ],
            "acceptance_gates": [
                "brief generated",
                "workspace bootstrap ready",
            ],
            "pipeline": {"stage": "approval", "status": "ready", "block_reason": None},
            "artifacts": {
                "project_directory": "assets/shared/approved-projects/lead-capture-copilot",
                "authority_record_path": "assets/shared/approved-projects/lead-capture-copilot/APPROVED_PROJECT.json",
                "delivery_brief_path": "assets/shared/approved-projects/lead-capture-copilot/PROJECT_BRIEF.md",
                "template_contract_path": "docs/platform/standalone-saas-template-contract.md",
                "project_metadata_path": ".hermes/project-metadata.json",
                "shared_backend_guardrails_path": ".hermes/shared-backend-guardrails.json",
                "approved_brief_entrypoint_path": ".hermes/PROJECT_BRIEF_ENTRYPOINT.md",
                "gsd_constraints_path": ".planning/phases/09-claude-code-delivery-team-orchestration/09-01-PLAN.md",
            },
        }

    def test_d05_brief_renders_required_sections_in_stable_order(self) -> None:
        start_approved_delivery = load_module("start_approved_project_delivery", SCRIPT_PATH)
        brief = start_approved_delivery.build_delivery_ready_brief(self.build_record())

        positions = []
        for section in EXPECTED_SECTION_ORDER:
            self.assertIn(section, brief)
            positions.append(brief.index(section))
        self.assertEqual(positions, sorted(positions))

        for bullet in EXPECTED_BULLETS:
            self.assertIn(bullet, brief)

        self.assertIn("- capture inbound lead notes", brief)
        self.assertIn("- Solo operators who need to qualify inbound leads quickly.", brief)
        self.assertIn("- Turn incoming lead notes into ranked follow-up actions.", brief)
        self.assertIn("- reuse shared Supabase auth and payments", brief)
        self.assertIn("- brief generated", brief)

    def test_d06_brief_derives_only_from_record_fields(self) -> None:
        start_approved_delivery = load_module("start_approved_project_delivery", SCRIPT_PATH)
        record = self.build_record()
        brief_one = start_approved_delivery.build_delivery_ready_brief(record)
        brief_two = start_approved_delivery.build_delivery_ready_brief(record)
        self.assertEqual(brief_one, brief_two)
        self.assertNotIn("chat history", brief_one.lower())

        mutated_record = self.build_record()
        mutated_record["mvp_framing"] = "Convert raw lead notes into a ready-to-call task list."
        mutated_record["approved_scope"] = [
            "import CSV leads",
            "rank follow-up priority",
        ]
        mutated_brief = start_approved_delivery.build_delivery_ready_brief(mutated_record)
        self.assertIn("Convert raw lead notes into a ready-to-call task list.", mutated_brief)
        self.assertIn("- import CSV leads", mutated_brief)
        self.assertNotEqual(brief_one, mutated_brief)


if __name__ == "__main__":
    unittest.main()
