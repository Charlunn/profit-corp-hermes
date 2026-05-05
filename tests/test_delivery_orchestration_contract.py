import unittest
from pathlib import Path
import importlib.util
import json
import shutil
import tempfile


ROOT_DIR = Path(__file__).resolve().parent.parent
WORKFLOW_PATH = ROOT_DIR / "skills" / "library" / "normalized" / "orchestrator-workflow.md"
INPUT_TEMPLATE_PATH = ROOT_DIR / "docs" / "skill-governance" / "templates" / "orchestrator-input-template-v0.2.md"
RENDER_SCRIPT_PATH = ROOT_DIR / "scripts" / "render_approved_delivery_status.py"
FORBIDDEN_CHAT_STATE_TERMS = [
    "terminal history",
    "ad-hoc owner routing",
    "freeform chat state",
]
EXPECTED_ROLE_NAMES = [
    "delivery-orchestrator",
    "design-specialist",
    "development-specialist",
    "testing-specialist",
    "git-versioning-specialist",
    "release-readiness-specialist",
]
EXPECTED_STAGE_ORDER = [
    "design",
    "development",
    "testing",
    "git versioning",
    "release readiness",
]
EXPECTED_BUNDLE_FIELDS = [
    "approved brief",
    "template contract",
    ".hermes/shared-backend-guardrails.json",
    ".hermes/project-metadata.json",
    "GSD constraints",
]


class DeliveryOrchestrationContractTests(unittest.TestCase):
    maxDiff = None

    def addCleanupPath(self, path: Path) -> None:
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))

    def load_module(self, module_name: str, script_path: Path):
        self.assertTrue(script_path.exists(), f"expected script to exist: {script_path}")
        spec = importlib.util.spec_from_file_location(module_name, script_path)
        if spec is None or spec.loader is None:
            raise AssertionError(f"unable to load module spec for {script_path}")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def load_workflow(self) -> str:
        self.assertTrue(WORKFLOW_PATH.exists(), "workflow contract file is missing")
        return WORKFLOW_PATH.read_text(encoding="utf-8")

    def load_input_template(self) -> str:
        self.assertTrue(INPUT_TEMPLATE_PATH.exists(), "input template file is missing")
        return INPUT_TEMPLATE_PATH.read_text(encoding="utf-8")

    def assert_contains_in_order(self, content: str, expected: list[str], *, msg: str) -> None:
        positions: list[int] = []
        for item in expected:
            self.assertIn(item, content, msg=msg)
            positions.append(content.index(item))
        self.assertEqual(positions, sorted(positions), msg)

    def test_d01_d02_single_delivery_orchestrator_and_exact_five_stage_order(self) -> None:
        content = self.load_workflow().lower()
        self.assertIn("delivery-orchestrator", content, "D-01: delivery-orchestrator role must be explicit")
        self.assertEqual(
            content.count("- `delivery-orchestrator`"),
            1,
            "D-01: workflow must define one delivery-orchestrator role entry",
        )
        for role in EXPECTED_ROLE_NAMES[1:]:
            self.assertIn(role, content, f"D-02: missing specialist role {role}")
        self.assert_contains_in_order(
            content,
            EXPECTED_STAGE_ORDER,
            msg="D-02: stage order must stay design -> development -> testing -> git versioning -> release readiness",
        )

    def test_d03_d12_workflow_rejects_chat_only_delivery_memory(self) -> None:
        content = self.load_workflow().lower()
        for forbidden in FORBIDDEN_CHAT_STATE_TERMS:
            self.assertNotIn(
                forbidden,
                content,
                f"D-03/D-12: workflow must not rely on {forbidden}",
            )
        self.assertIn("artifact", content, "D-03: workflow should require artifact-based handoff")

    def test_d04_start_input_bundle_requires_explicit_paths_and_field_names(self) -> None:
        content = self.load_input_template()
        for field in EXPECTED_BUNDLE_FIELDS:
            self.assertIn(field, content, f"D-04: missing required delivery bundle field {field}")
        self.assertIn("approved brief path", content, "D-04: approved brief path must be explicit")
        self.assertIn("template contract path", content, "D-04: template contract path must be explicit")
        self.assertIn("shared-backend guardrails path", content, "D-04: guardrails path must be explicit")
        self.assertIn("project metadata path", content, "D-04: project metadata path must be explicit")
        self.assertIn("gsd constraints source", content.lower(), "D-04: GSD constraints source must be explicit")

    def test_auto01_status_render_names_exact_locked_contract_drift_fields(self) -> None:
        render_module = self.load_module("render_approved_delivery_status_contract", RENDER_SCRIPT_PATH)
        root = Path(tempfile.mkdtemp(prefix="delivery-contract-drift-"))
        self.addCleanupPath(root)
        project_dir = root / "assets" / "shared" / "approved-projects" / "lead-capture-copilot"
        project_dir.mkdir(parents=True, exist_ok=True)
        authority_path = project_dir / "APPROVED_PROJECT.json"
        workspace = root / "generated-workspaces" / "lead-capture-copilot"
        workspace.mkdir(parents=True, exist_ok=True)

        record = {
            "approval": {
                "approval_id": "APR-2026-04-27-01",
                "approved_at": "2026-04-27T08:30:00Z",
                "approver": "ceo",
                "evidence": {
                    "decision_record": "assets/shared/CORP_CULTURE.md#greenlight-2026-04-27",
                    "summary": "Approved for governed delivery.",
                },
            },
            "project_identity": {"project_slug": "lead-capture-copilot"},
            "pipeline": {
                "stage": "development",
                "status": "blocked",
                "block_reason": "contract_drift_requires_reopen",
                "workspace_path": workspace.as_posix(),
                "delivery_run_id": "delivery-lead-capture-copilot-001",
                "resume_from_stage": "development",
            },
            "artifacts": {
                "authority_record_path": authority_path.as_posix(),
                "delivery_brief_path": (project_dir / "PROJECT_BRIEF.md").as_posix(),
                "final_review_path": (project_dir / "FINAL_OPERATOR_REVIEW.md").as_posix(),
            },
            "contract_drift": {
                "status": "pending_reopen",
                "field": "monetization",
                "approved_value": ["subscription"],
                "proposed_value": ["subscription", "services upsell"],
                "reason": "Pricing changed after approval.",
                "evidence_path": (workspace / ".hermes" / "contract-drift.json").as_posix(),
                "governance_action_id": "gov-drift-001",
            },
            "shipping": {"github": {}, "vercel": {}},
        }
        authority_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        events_path = project_dir / "approved-delivery-events.jsonl"
        event = {
            "project_slug": "lead-capture-copilot",
            "stage": "development",
            "status": "blocked",
            "action": "scope_reopen_requested",
            "timestamp": "2026-04-27T08:35:00Z",
            "outcome": "blocked",
            "authority_record_path": authority_path.as_posix(),
            "brief_path": (project_dir / "PROJECT_BRIEF.md").as_posix(),
            "workspace_path": workspace.as_posix(),
            "delivery_run_id": "delivery-lead-capture-copilot-001",
            "artifact": "approved_contract:monetization",
            "block_reason": "contract_drift_requires_reopen",
            "evidence_path": (workspace / ".hermes" / "contract-drift.json").as_posix(),
            "resume_from_stage": "development",
            "final_handoff_path": "",
        }
        events_path.write_text(json.dumps(event, ensure_ascii=False) + "\n", encoding="utf-8")

        markdown = render_module.build_status_markdown([event], record, project_dir)
        self.assertIn("## Locked Contract Drift", markdown)
        self.assertIn("monetization", markdown)
        self.assertIn("subscription", markdown)
        self.assertIn("services upsell", markdown)
        self.assertIn("gov-drift-001", markdown)
        self.assertIn("contract_drift_requires_reopen", markdown)


if __name__ == "__main__":
    unittest.main()
