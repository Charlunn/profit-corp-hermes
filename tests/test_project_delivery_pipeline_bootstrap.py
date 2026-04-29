import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT_DIR = Path(__file__).resolve().parent.parent
START_SCRIPT_PATH = ROOT_DIR / "scripts" / "start_approved_project_delivery.py"
APPEND_SCRIPT_PATH = ROOT_DIR / "scripts" / "append_approved_delivery_event.py"
RENDER_SCRIPT_PATH = ROOT_DIR / "scripts" / "render_approved_delivery_status.py"
CONTRACT_PATH = ROOT_DIR / "docs" / "platform" / "standalone-saas-template-contract.md"
PLAN_09_01_PATH = ROOT_DIR / ".planning" / "phases" / "09-claude-code-delivery-team-orchestration" / "09-01-PLAN.md"
PIPELINE_STAGES = [
    "approval",
    "brief_generation",
    "workspace_instantiation",
    "conformance",
    "delivery_run_bootstrap",
    "github_repository",
    "github_sync",
    "vercel_linkage",
    "vercel_deploy",
    "handoff",
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


class ApprovedDeliveryBootstrapTests(unittest.TestCase):
    maxDiff = None

    def addCleanupPath(self, path: Path) -> None:
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))

    def create_project_fixture(self, *, custom_approved_root: bool = False) -> tuple[Path, Path, Path, Path]:
        root = Path(tempfile.mkdtemp(prefix="approved-delivery-bootstrap-"))
        self.addCleanupPath(root)
        approved_root = (root / "external-approved-projects") if custom_approved_root else (root / "assets" / "shared" / "approved-projects")
        approved_root.mkdir(parents=True, exist_ok=True)
        workspace_root = root / "generated-workspaces"
        workspace_root.mkdir(parents=True, exist_ok=True)
        project_dir = approved_root / "lead-capture-copilot"
        project_dir.mkdir(parents=True, exist_ok=True)
        authority_path = project_dir / "APPROVED_PROJECT.json"
        brief_path = project_dir / "PROJECT_BRIEF.md"
        brief_path.write_text(
            "# Approved Project Brief\n\n## Project Identity\n- App key: `lead_capture_copilot`\n",
            encoding="utf-8",
        )
        record = {
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
            "pipeline": {
                "stage": "brief_generation",
                "status": "ready",
                "block_reason": None,
                "resume_from_stage": "workspace_instantiation",
            },
            "artifacts": {
                "project_directory": project_dir.as_posix(),
                "authority_record_path": authority_path.as_posix(),
                "delivery_brief_path": brief_path.as_posix(),
                "template_contract_path": CONTRACT_PATH.as_posix(),
                "project_metadata_path": ".hermes/project-metadata.json",
                "shared_backend_guardrails_path": ".hermes/shared-backend-guardrails.json",
                "approved_brief_entrypoint_path": ".hermes/PROJECT_BRIEF_ENTRYPOINT.md",
                "gsd_constraints_path": PLAN_09_01_PATH.as_posix(),
                "events_path": (project_dir / "approved-delivery-events.jsonl").as_posix(),
                "status_path": (project_dir / "DELIVERY_PIPELINE_STATUS.md").as_posix(),
            },
        }
        authority_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return root, project_dir, authority_path, workspace_root

    def read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def read_events(self, project_dir: Path) -> list[dict]:
        events_path = project_dir / "approved-delivery-events.jsonl"
        self.assertTrue(events_path.exists(), f"expected events file to exist: {events_path}")
        lines = [line for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        return [json.loads(line) for line in lines]

    def assert_event_stages(self, events: list[dict], expected: list[str]) -> None:
        self.assertEqual([event["stage"] for event in events], expected)

    def seed_workspace_outputs(
        self,
        workspace_root: Path,
        workspace_name: str = "lead-capture-copilot",
        *,
        include_downstream_prereq_evidence: bool = False,
        include_final_handoff: bool = False,
    ) -> Path:
        workspace = workspace_root / workspace_name
        hermes_dir = workspace / ".hermes"
        hermes_dir.mkdir(parents=True, exist_ok=True)
        (workspace_root / "docs" / "platform").mkdir(parents=True, exist_ok=True)
        (workspace_root / ".planning" / "phases" / "09-claude-code-delivery-team-orchestration").mkdir(parents=True, exist_ok=True)
        (workspace_root / "docs" / "platform" / "standalone-saas-template-contract.md").write_text(
            "# Standalone SaaS Template Contract\n",
            encoding="utf-8",
        )
        (workspace_root / ".planning" / "phases" / "09-claude-code-delivery-team-orchestration" / "09-01-PLAN.md").write_text(
            "# Phase 09 Plan 01\n",
            encoding="utf-8",
        )
        metadata = {
            "asset_id": "standalone-saas-template",
            "workspace_name": workspace_name,
            "app_key": "lead_capture_copilot",
            "app_name": "Lead Capture Copilot",
            "app_url": "https://lead-capture.example.com",
            "template_source_path": "C:/Users/42236/Desktop/standalone-saas-template",
            "canonical_contract_path": CONTRACT_PATH.as_posix(),
        }
        (hermes_dir / "project-metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        guardrails = {
            "backend_model": "shared-supabase",
            "app_key": metadata["app_key"],
            "canonical_contract_path": metadata["canonical_contract_path"],
            "allowed_shared_tables": ["users", "orders", "payments", "subscriptions"],
            "protected_paths": ["src/lib/paypal.ts"],
            "client_write_blocked_tables": ["users", "orders", "payments", "subscriptions"],
            "allow_independent_backend": False,
        }
        (hermes_dir / "shared-backend-guardrails.json").write_text(json.dumps(guardrails, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (hermes_dir / "PROJECT_BRIEF_ENTRYPOINT.md").write_text(
            "# Hermes Project Brief Entrypoint\n\n- Workspace: `lead-capture-copilot`\n",
            encoding="utf-8",
        )
        if include_downstream_prereq_evidence:
            (hermes_dir / "deployment-prerequisites.md").write_text(
                "# Deployment prerequisites\n\n- Missing Vercel credential evidence.\n",
                encoding="utf-8",
            )
        if include_final_handoff:
            (hermes_dir / "FINAL_DELIVERY.md").write_text(
                "# Final Delivery\n\n- Ready for operator handoff.\n",
                encoding="utf-8",
            )
        return workspace

    def test_bundle_written_to_custom_root_bootstraps_without_brief_generation_block(self) -> None:
        start_module = load_module("start_approved_project_delivery", START_SCRIPT_PATH)
        root = Path(tempfile.mkdtemp(prefix="approved-delivery-custom-root-"))
        self.addCleanupPath(root)
        approved_root = root / "external-approved-projects"
        workspace_root = root / "generated-workspaces"
        approved_root.mkdir(parents=True, exist_ok=True)
        workspace_root.mkdir(parents=True, exist_ok=True)
        workspace = self.seed_workspace_outputs(workspace_root)

        payload = {
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
            "template_contract_path": CONTRACT_PATH.as_posix(),
            "gsd_constraints_path": PLAN_09_01_PATH.as_posix(),
        }
        bundle = start_module.write_approved_project_bundle(payload, approved_projects_root=approved_root)
        authority_path = Path(bundle["authority_record_path"])
        project_dir = authority_path.parent

        def fake_instantiate(*args, **kwargs):
            return None

        def fake_conformance(*args, **kwargs):
            return {
                "ok": True,
                "report_path": (project_dir / "conformance-report.md").as_posix(),
            }

        def fake_start_run(*args, **kwargs):
            return {
                "ok": True,
                "workspace": workspace.as_posix(),
                "manifest_path": (workspace / ".hermes" / "delivery-run-manifest.json").as_posix(),
                "status_path": (workspace / ".hermes" / "DELIVERY_STATUS.md").as_posix(),
                "run_id": "delivery-lead-capture-copilot-001",
            }

        def fake_template_source(*args, **kwargs):
            return {
                "asset_id": "standalone-saas-template",
                "canonical_contract": "docs/platform/standalone-saas-template-contract.md",
            }, root

        with mock.patch.object(start_module, "ROOT_DIR", root), \
             mock.patch.object(start_module, "workspace_instantiation_artifacts_ready", return_value=True), \
             mock.patch.object(start_module, "instantiate_workspace", side_effect=fake_instantiate), \
             mock.patch.object(start_module, "check_template_conformance", side_effect=fake_conformance), \
             mock.patch.object(start_module, "initialize_delivery_run", side_effect=fake_start_run), \
             mock.patch.object(start_module, "prepare_github_repository", return_value={
                 "ok": True,
                 "repository_mode": "attach",
                 "repository_owner": "profit-corp",
                 "repository_name": "profit-corp/lead-capture-copilot",
                 "repository_url": "https://github.com/profit-corp/lead-capture-copilot.git",
                 "default_branch": "main",
                 "remote_name": "origin",
                 "prepare_evidence_path": (workspace / ".hermes" / "github-repository-prepare.json").as_posix(),
                 "prepare_auth_source": "gh_cli",
                 "prepare_auth_source_details": {"login": "profit-corp"},
             }), \
             mock.patch.object(start_module, "run_github_sync", return_value={
                 "ok": True,
                 "repository_url": "https://github.com/profit-corp/lead-capture-copilot.git",
                 "default_branch": "main",
                 "synced_commit": "abc1234",
                 "evidence_path": (workspace / ".hermes" / "github-sync.json").as_posix(),
             }):
            result = start_module.start_approved_project_delivery(authority_path, workspace_root=workspace_root)

        self.assertTrue(result["ok"], msg=result)
        self.assertEqual(result["stage"], "vercel_linkage")
        updated = self.read_json(authority_path)
        self.assertEqual(updated["artifacts"]["project_directory"], project_dir.as_posix())
        self.assertEqual(updated["artifacts"]["authority_record_path"], authority_path.as_posix())
        self.assertEqual(updated["artifacts"]["delivery_brief_path"], (project_dir / "PROJECT_BRIEF.md").as_posix())
        self.assertEqual(updated["shipping"]["github"]["repository_owner"], "profit-corp")
        self.assertEqual(updated["shipping"]["github"]["repository_name"], "profit-corp/lead-capture-copilot")
        self.assertEqual(updated["shipping"]["github"]["repository_url"], "https://github.com/profit-corp/lead-capture-copilot.git")
        self.assertEqual(updated["shipping"]["github"]["prepare_evidence_path"], (workspace / ".hermes" / "github-repository-prepare.json").as_posix())
        self.assertEqual(updated["shipping"]["github"]["prepare_auth_source"], "gh_cli")
        self.assertEqual(updated["shipping"]["github"]["prepare_auth_source_details"]["login"], "profit-corp")
        events = self.read_events(project_dir)
        self.assert_event_stages(events, PIPELINE_STAGES[:-2])

    def test_bootstrap_success_persists_authority_events_workspace_and_delivery_run(self) -> None:
        start_module = load_module("start_approved_project_delivery", START_SCRIPT_PATH)
        root, project_dir, authority_path, workspace_root = self.create_project_fixture()
        workspace = self.seed_workspace_outputs(workspace_root)

        def fake_instantiate(*args, **kwargs):
            return None

        def fake_conformance(*args, **kwargs):
            return {
                "ok": True,
                "report_path": (project_dir / "conformance-report.md").as_posix(),
            }

        def fake_start_run(*args, **kwargs):
            return {
                "ok": True,
                "workspace": workspace.as_posix(),
                "manifest_path": (workspace / ".hermes" / "delivery-run-manifest.json").as_posix(),
                "status_path": (workspace / ".hermes" / "DELIVERY_STATUS.md").as_posix(),
                "run_id": "delivery-lead-capture-copilot-001",
            }

        with mock.patch.object(start_module, "ROOT_DIR", root), \
             mock.patch.object(start_module, "workspace_instantiation_artifacts_ready", return_value=True), \
             mock.patch.object(start_module, "instantiate_workspace", side_effect=fake_instantiate), \
             mock.patch.object(start_module, "check_template_conformance", side_effect=fake_conformance), \
             mock.patch.object(start_module, "initialize_delivery_run", side_effect=fake_start_run), \
             mock.patch.object(start_module, "prepare_github_repository", return_value={
                 "ok": True,
                 "repository_mode": "attach",
                 "repository_owner": "profit-corp",
                 "repository_name": "profit-corp/lead-capture-copilot",
                 "repository_url": "https://github.com/profit-corp/lead-capture-copilot.git",
                 "default_branch": "main",
                 "remote_name": "origin",
                 "prepare_evidence_path": (workspace / ".hermes" / "github-repository-prepare.json").as_posix(),
                 "prepare_auth_source": "gh_cli",
                 "prepare_auth_source_details": {"login": "profit-corp"},
             }), \
             mock.patch.object(start_module, "run_github_sync", return_value={
                 "ok": True,
                 "repository_url": "https://github.com/profit-corp/lead-capture-copilot.git",
                 "default_branch": "main",
                 "synced_commit": "abc1234",
                 "evidence_path": (workspace / ".hermes" / "github-sync.json").as_posix(),
             }):
            result = start_module.start_approved_project_delivery(authority_path, workspace_root=workspace_root)

        self.assertTrue(result["ok"], msg=result)
        self.assertEqual(result["stage"], "vercel_linkage")
        self.assertEqual(result["status"], "ready")
        updated = self.read_json(authority_path)
        self.assertEqual(updated["pipeline"]["stage"], "vercel_linkage")
        self.assertEqual(updated["pipeline"]["status"], "ready")
        self.assertEqual(updated["pipeline"]["workspace_path"], workspace.as_posix())
        self.assertEqual(updated["pipeline"]["delivery_run_id"], "delivery-lead-capture-copilot-001")
        self.assertEqual(updated["artifacts"]["workspace_path"], workspace.as_posix())
        self.assertEqual(updated["artifacts"]["delivery_manifest_path"], (workspace / ".hermes" / "delivery-run-manifest.json").as_posix())

        events = self.read_events(project_dir)
        self.assert_event_stages(events, PIPELINE_STAGES[:-2])
        self.assertEqual(events[0]["stage"], "approval")
        self.assertEqual(events[1]["stage"], "brief_generation")
        self.assertEqual(events[-1]["stage"], "vercel_linkage")
        self.assertEqual(events[-1]["delivery_run_id"], "delivery-lead-capture-copilot-001")
        self.assertEqual(events[-1]["workspace_path"], workspace.as_posix())
        self.assertEqual(updated["shipping"]["github"]["repository_mode"], "attach")
        self.assertEqual(updated["shipping"]["github"]["default_branch"], "main")
        self.assertEqual(updated["shipping"]["github"]["synced_commit"], "abc1234")
        self.assertEqual(updated["pipeline"]["resume_from_stage"], "vercel_deploy")

    def test_blocking_paths_persist_block_reason_evidence_and_resume_stage(self) -> None:
        start_module = load_module("start_approved_project_delivery", START_SCRIPT_PATH)
        root, project_dir, authority_path, workspace_root = self.create_project_fixture()
        blocked_workspace = self.seed_workspace_outputs(workspace_root, include_downstream_prereq_evidence=True)

        cases = [
            {
                "name": "missing approval",
                "mutate_record": lambda record: record["approval"].update({"evidence": {}}),
                "expected_reason": "missing_approval_evidence",
                "expected_stage": "approval",
                "expected_evidence": "__AUTHORITY_PATH__",
            },
            {
                "name": "missing required brief input",
                "mutate_record": lambda record: (project_dir / "PROJECT_BRIEF.md").unlink(),
                "expected_reason": "missing_required_brief_input",
                "expected_stage": "brief_generation",
                "expected_evidence": "__MISSING_BRIEF_PATH__",
            },
            {
                "name": "duplicate active bootstrap",
                "mutate_record": lambda record: record["pipeline"].update({"stage": "workspace_instantiation", "status": "running", "active_run_id": "phase10-001"}),
                "expected_reason": "duplicate_active_bootstrap",
                "expected_stage": "workspace_instantiation",
                "expected_evidence": "__AUTHORITY_PATH__",
            },
            {
                "name": "instantiation failure",
                "mutate_workspace": lambda workspace: shutil.rmtree(workspace),
                "patch": {"instantiate_workspace": RuntimeError("copy failed")},
                "expected_reason": "workspace_instantiation_failed",
                "expected_stage": "workspace_instantiation",
                "expected_evidence": "__AUTHORITY_PATH__",
            },
            {
                "name": "conformance failure",
                "patch": {"check_template_conformance": {"ok": False, "report_path": (project_dir / "conformance-report.md").as_posix()}},
                "expected_reason": "conformance_failed",
                "expected_stage": "conformance",
                "expected_evidence": (project_dir / "conformance-report.md").as_posix(),
            },
            {
                "name": "delivery bootstrap failure",
                "patch": {
                    "check_template_conformance": {"ok": True, "report_path": (project_dir / "conformance-report.md").as_posix()},
                    "initialize_delivery_run": {"ok": False, "error": "bootstrap failed", "evidence_path": (project_dir / "delivery-run-bootstrap.log").as_posix()},
                },
                "expected_reason": "delivery_run_bootstrap_failed",
                "expected_stage": "delivery_run_bootstrap",
                "expected_evidence": (project_dir / "delivery-run-bootstrap.log").as_posix(),
            },
            {
                "name": "missing downstream prerequisite evidence",
                "patch": {
                    "check_template_conformance": {"ok": True, "report_path": (project_dir / "conformance-report.md").as_posix()},
                    "initialize_delivery_run": {
                        "ok": False,
                        "error": "missing downstream prerequisite evidence",
                        "block_reason": "missing_downstream_prerequisite_evidence",
                        "evidence_path": (blocked_workspace / ".hermes" / "deployment-prerequisites.md").as_posix(),
                    },
                },
                "expected_reason": "missing_downstream_prerequisite_evidence",
                "expected_stage": "delivery_run_bootstrap",
                "expected_evidence": "__DOWNSTREAM_EVIDENCE__",
            },
        ]

        for case in cases:
            with self.subTest(case=case["name"]):
                root, project_dir, authority_path, workspace_root = self.create_project_fixture()
                workspace = self.seed_workspace_outputs(workspace_root, include_downstream_prereq_evidence=True)
                mutate_workspace = case.get("mutate_workspace")
                if mutate_workspace:
                    mutate_workspace(workspace)
                record = self.read_json(authority_path)
                mutate = case.get("mutate_record")
                if mutate:
                    mutate(record)
                    authority_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

                instantiate_side_effect = None
                conformance_return = {"ok": True, "report_path": (project_dir / "conformance-report.md").as_posix()}
                start_run_return = {
                    "ok": True,
                    "workspace": workspace.as_posix(),
                    "manifest_path": (workspace / ".hermes" / "delivery-run-manifest.json").as_posix(),
                    "status_path": (workspace / ".hermes" / "DELIVERY_STATUS.md").as_posix(),
                    "run_id": "delivery-lead-capture-copilot-001",
                }
                patch_map = dict(case.get("patch", {}))
                if case["expected_evidence"] == "__DOWNSTREAM_EVIDENCE__" and "initialize_delivery_run" in patch_map:
                    patch_map["initialize_delivery_run"] = {
                        **patch_map["initialize_delivery_run"],
                        "evidence_path": (workspace / ".hermes" / "deployment-prerequisites.md").as_posix(),
                    }
                if "instantiate_workspace" in patch_map:
                    instantiate_side_effect = patch_map["instantiate_workspace"]
                if "check_template_conformance" in patch_map:
                    conformance_return = patch_map["check_template_conformance"]
                if "initialize_delivery_run" in patch_map:
                    start_run_return = patch_map["initialize_delivery_run"]

                with mock.patch.object(start_module, "ROOT_DIR", root), \
                     mock.patch.object(start_module, "workspace_instantiation_artifacts_ready", return_value=case["expected_stage"] != "workspace_instantiation"), \
                     mock.patch.object(start_module, "instantiate_workspace", side_effect=instantiate_side_effect), \
                     mock.patch.object(start_module, "check_template_conformance", return_value=conformance_return), \
                     mock.patch.object(start_module, "initialize_delivery_run", return_value=start_run_return):
                    result = start_module.start_approved_project_delivery(authority_path, workspace_root=workspace_root)

                expected_evidence = authority_path.as_posix() if case["expected_evidence"] == "__AUTHORITY_PATH__" else (
                    (project_dir / "PROJECT_BRIEF.md").as_posix() if case["expected_evidence"] == "__MISSING_BRIEF_PATH__" else (
                        (workspace / ".hermes" / "deployment-prerequisites.md").as_posix() if case["expected_evidence"] == "__DOWNSTREAM_EVIDENCE__" else case["expected_evidence"]
                    )
                )

                self.assertFalse(result["ok"], msg=result)
                self.assertEqual(result["status"], "blocked")
                self.assertEqual(result["stage"], case["expected_stage"])
                self.assertEqual(result["block_reason"], case["expected_reason"])
                updated = self.read_json(authority_path)
                self.assertEqual(updated["pipeline"]["status"], "blocked")
                self.assertEqual(updated["pipeline"]["stage"], case["expected_stage"])
                self.assertEqual(updated["pipeline"]["block_reason"], case["expected_reason"])
                self.assertEqual(updated["pipeline"]["resume_from_stage"], case["expected_stage"])
                self.assertEqual(updated["pipeline"]["evidence_path"], expected_evidence)

                events = self.read_events(project_dir)
                self.assertEqual(events[-1]["outcome"], "blocked")
                self.assertEqual(events[-1]["stage"], case["expected_stage"])
                self.assertEqual(events[-1]["block_reason"], case["expected_reason"])
                self.assertEqual(events[-1]["evidence_path"], expected_evidence)

                status_text = (project_dir / "DELIVERY_PIPELINE_STATUS.md").read_text(encoding="utf-8")
                self.assertIn(case["expected_stage"], status_text)
                self.assertIn(case["expected_reason"], status_text)
                self.assertIn(expected_evidence, status_text)

    def test_status_renderer_derives_workspace_brief_prerequisite_run_and_handoff_links(self) -> None:
        append_module = load_module("append_approved_delivery_event", APPEND_SCRIPT_PATH)
        render_module = load_module("render_approved_delivery_status", RENDER_SCRIPT_PATH)
        root, project_dir, authority_path, workspace_root = self.create_project_fixture()
        workspace = self.seed_workspace_outputs(workspace_root, include_downstream_prereq_evidence=True)

        record = self.read_json(authority_path)
        record["shipping"] = {
            "github": {
                "repository_mode": "attach",
                "repository_owner": "profit-corp",
                "repository_name": "profit-corp/lead-capture-copilot",
                "repository_url": "https://github.com/profit-corp/lead-capture-copilot.git",
                "default_branch": "main",
                "synced_commit": "abc1234",
                "sync_evidence_path": (workspace / ".hermes" / "github-sync.json").as_posix(),
                "last_sync_status": "failed",
                "prepare_audit_path": (workspace / ".hermes" / "github-repository-audit.json").as_posix(),
                "sync_audit_path": (workspace / ".hermes" / "github-sync-audit.json").as_posix(),
            },
            "vercel": {
                "team_scope": "profit-corp",
                "project_id": "prj_123",
                "project_name": "lead-capture-copilot-prod",
                "project_url": "https://vercel.com/profit-corp/lead-capture-copilot-prod",
                "linked": True,
                "env_contract_path": (workspace / ".hermes" / "vercel-env-contract.json").as_posix(),
                "deploy_url": "https://lead-capture-copilot-prod.vercel.app",
                "deploy_status": "failed",
                "deploy_evidence_path": (workspace / ".hermes" / "vercel-deploy.json").as_posix(),
                "link_audit_path": (workspace / ".hermes" / "vercel-link-audit.json").as_posix(),
                "env_audit_path": (workspace / ".hermes" / "vercel-env-audit.json").as_posix(),
                "deploy_audit_path": (workspace / ".hermes" / "vercel-deploy-audit.json").as_posix(),
            },
        }
        record["latest_blocked_prerequisite"] = {
            "reason": "missing_downstream_prerequisite_evidence",
            "path": (workspace / ".hermes" / "deployment-prerequisites.md").as_posix(),
            "status": "open",
        }
        record["protected_change"] = {
            "classification": "protected_platform_change",
            "status": "blocked",
            "evidence_path": (workspace / ".hermes" / "protected-change-inventory.json").as_posix(),
        }
        record["platform_justification"] = {
            "status": "pending",
            "artifact_path": (project_dir / "PLATFORM_CHANGE_JUSTIFICATION.md").as_posix(),
            "governance_action_id": "gov-approval-001",
        }
        record["artifacts"]["final_review_path"] = (project_dir / "FINAL_OPERATOR_REVIEW.md").as_posix()
        authority_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        events = [
            {
                "project_slug": "lead-capture-copilot",
                "stage": "approval",
                "status": "ready",
                "action": "approval_verified",
                "timestamp": "2026-04-27T08:30:00Z",
                "outcome": "pass",
                "authority_record_path": authority_path.as_posix(),
                "brief_path": (project_dir / "PROJECT_BRIEF.md").as_posix(),
                "workspace_path": workspace.as_posix(),
                "delivery_run_id": "not_available",
                "artifact": authority_path.as_posix(),
                "block_reason": "",
                "evidence_path": "",
                "resume_from_stage": "workspace_instantiation",
                "final_handoff_path": "",
                "shipping": record["shipping"],
            },
            {
                "project_slug": "lead-capture-copilot",
                "stage": "delivery_run_bootstrap",
                "status": "blocked",
                "action": "bootstrap_blocked",
                "timestamp": "2026-04-27T08:35:00Z",
                "outcome": "blocked",
                "authority_record_path": authority_path.as_posix(),
                "brief_path": (project_dir / "PROJECT_BRIEF.md").as_posix(),
                "workspace_path": workspace.as_posix(),
                "delivery_run_id": "delivery-lead-capture-copilot-001",
                "artifact": (project_dir / "approved-delivery-events.jsonl").as_posix(),
                "block_reason": "missing_downstream_prerequisite_evidence",
                "evidence_path": (workspace / ".hermes" / "deployment-prerequisites.md").as_posix(),
                "resume_from_stage": "delivery_run_bootstrap",
                "final_handoff_path": "",
                "shipping": record["shipping"],
            },
            {
                "project_slug": "lead-capture-copilot",
                "stage": "vercel_deploy",
                "status": "blocked",
                "action": "vercel_deploy_failed",
                "timestamp": "2026-04-27T08:39:00Z",
                "outcome": "failed",
                "authority_record_path": authority_path.as_posix(),
                "brief_path": (project_dir / "PROJECT_BRIEF.md").as_posix(),
                "workspace_path": workspace.as_posix(),
                "delivery_run_id": "delivery-lead-capture-copilot-001",
                "artifact": (workspace / ".hermes" / "vercel-deploy.json").as_posix(),
                "block_reason": "vercel_deploy_failed",
                "evidence_path": (workspace / ".hermes" / "vercel-deploy.json").as_posix(),
                "resume_from_stage": "vercel_deploy",
                "final_handoff_path": "",
                "shipping": record["shipping"],
            },
            {
                "project_slug": "lead-capture-copilot",
                "stage": "handoff",
                "status": "completed",
                "action": "final_handoff_persisted",
                "timestamp": "2026-04-27T08:40:00Z",
                "outcome": "pass",
                "authority_record_path": authority_path.as_posix(),
                "brief_path": (project_dir / "PROJECT_BRIEF.md").as_posix(),
                "workspace_path": workspace.as_posix(),
                "delivery_run_id": "delivery-lead-capture-copilot-001",
                "artifact": (workspace / ".hermes" / "FINAL_DELIVERY.md").as_posix(),
                "block_reason": "",
                "evidence_path": (workspace / ".hermes" / "deployment-prerequisites.md").as_posix(),
                "resume_from_stage": "",
                "final_handoff_path": (workspace / ".hermes" / "FINAL_DELIVERY.md").as_posix(),
                "shipping": record["shipping"],
            },
        ]
        for event in events:
            append_module.append_approved_delivery_event(project_dir, event)

        render_module.render_approved_delivery_status(project_dir)
        status_text = (project_dir / "DELIVERY_PIPELINE_STATUS.md").read_text(encoding="utf-8")
        self.assertIn("## Final Operator Review", status_text)
        self.assertIn("## Action Required", status_text)
        self.assertIn("## Approval Summary", status_text)
        self.assertIn("## Blocked Prerequisites", status_text)
        self.assertIn("## Credentialed Delivery Actions", status_text)
        self.assertIn("## Protected Change Review", status_text)
        self.assertIn("## Deployment Outcome", status_text)
        self.assertIn("## Final Handoff", status_text)
        self.assertIn((project_dir / "FINAL_OPERATOR_REVIEW.md").as_posix(), status_text)
        self.assertIn("missing_downstream_prerequisite_evidence", status_text)
        self.assertIn("vercel_deploy_failed", status_text)
        self.assertIn("protected_platform_change", status_text)
        self.assertIn("gov-approval-001", status_text)
        self.assertIn((workspace / ".hermes" / "github-sync-audit.json").as_posix(), status_text)
        self.assertIn((workspace / ".hermes" / "vercel-deploy-audit.json").as_posix(), status_text)
        self.assertIn((workspace / ".hermes" / "FINAL_DELIVERY.md").as_posix(), status_text)

    def test_blocked_resume_finalize_then_validate_succeeds_with_canonical_workspace_linkage(self) -> None:
        start_module = load_module("start_approved_project_delivery", START_SCRIPT_PATH)
        validate_module = load_module("validate_approved_delivery_pipeline", ROOT_DIR / "scripts" / "validate_approved_delivery_pipeline.py")
        root, project_dir, authority_path, workspace_root = self.create_project_fixture()
        workspace = self.seed_workspace_outputs(
            workspace_root,
            include_downstream_prereq_evidence=True,
            include_final_handoff=True,
        )
        (workspace / ".hermes" / "template-conformance.json").write_text(
            json.dumps({"ok": True}, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

        blocked_result = {
            "ok": False,
            "error": "missing downstream prerequisite evidence",
            "block_reason": "missing_downstream_prerequisite_evidence",
            "evidence_path": (workspace / ".hermes" / "deployment-prerequisites.md").as_posix(),
        }
        ready_result = {
            "ok": True,
            "workspace": workspace.as_posix(),
            "manifest_path": (workspace / ".hermes" / "delivery-run-manifest.json").as_posix(),
            "status_path": (workspace / ".hermes" / "DELIVERY_STATUS.md").as_posix(),
            "run_id": "delivery-lead-capture-copilot-001",
        }

        with mock.patch.object(start_module, "ROOT_DIR", root), \
             mock.patch.object(start_module, "workspace_instantiation_artifacts_ready", return_value=True), \
             mock.patch.object(start_module, "instantiate_workspace"), \
             mock.patch.object(start_module, "check_template_conformance", return_value={"ok": True, "report_path": (project_dir / "conformance-report.md").as_posix()}), \
             mock.patch.object(start_module, "initialize_delivery_run", return_value=blocked_result), \
             mock.patch.object(start_module, "prepare_github_repository", return_value={
                 "ok": True,
                 "repository_mode": "attach",
                 "repository_owner": "profit-corp",
                 "repository_name": "profit-corp/lead-capture-copilot",
                 "repository_url": "https://github.com/profit-corp/lead-capture-copilot.git",
                 "default_branch": "main",
                 "remote_name": "origin",
                 "prepare_evidence_path": (workspace / ".hermes" / "github-repository-prepare.json").as_posix(),
             }), \
             mock.patch.object(start_module, "run_github_sync", return_value={
                 "ok": True,
                 "repository_url": "https://github.com/profit-corp/lead-capture-copilot.git",
                 "default_branch": "main",
                 "synced_commit": "abc1234",
                 "evidence_path": (workspace / ".hermes" / "github-sync.json").as_posix(),
             }):
            first_result = start_module.start_approved_project_delivery(authority_path, workspace_root=workspace_root)
            self.assertFalse(first_result["ok"], msg=first_result)
            self.assertEqual(first_result["status"], "blocked")

        events_path = project_dir / "approved-delivery-events.jsonl"
        blocked_events = [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        blocked_events[-1]["timestamp"] = "2026-04-27T08:33:30Z"
        events_path.write_text(
            "\n".join(json.dumps(event, ensure_ascii=False) for event in blocked_events) + "\n",
            encoding="utf-8",
        )

        with mock.patch.object(start_module, "ROOT_DIR", root), \
             mock.patch.object(start_module, "workspace_instantiation_artifacts_ready", return_value=True), \
             mock.patch.object(start_module, "initialize_delivery_run", return_value=ready_result), \
             mock.patch.object(start_module, "prepare_github_repository", return_value={
                 "ok": True,
                 "repository_mode": "attach",
                 "repository_owner": "profit-corp",
                 "repository_name": "profit-corp/lead-capture-copilot",
                 "repository_url": "https://github.com/profit-corp/lead-capture-copilot.git",
                 "default_branch": "main",
                 "remote_name": "origin",
                 "prepare_evidence_path": (workspace / ".hermes" / "github-repository-prepare.json").as_posix(),
             }), \
             mock.patch.object(start_module, "run_github_sync", return_value={
                 "ok": True,
                 "repository_url": "https://github.com/profit-corp/lead-capture-copilot.git",
                 "default_branch": "main",
                 "synced_commit": "abc1234",
                 "evidence_path": (workspace / ".hermes" / "github-sync.json").as_posix(),
             }):
            resumed_result = start_module.resume_approved_project_delivery(authority_path, workspace_root=workspace_root)
            self.assertTrue(resumed_result["ok"], msg=resumed_result)
            self.assertEqual(resumed_result["stage"], "vercel_linkage")

            finalized_result = start_module.finalize_delivery_handoff(authority_path)
            self.assertTrue(finalized_result["ok"], msg=finalized_result)

        updated = self.read_json(authority_path)
        final_handoff_path = (workspace / ".hermes" / "FINAL_DELIVERY.md").as_posix()
        self.assertEqual(updated["pipeline"]["workspace_path"], workspace.as_posix())
        self.assertEqual(updated["artifacts"]["workspace_path"], workspace.as_posix())
        self.assertEqual(updated["workspace_path"], workspace.as_posix())
        self.assertEqual(updated["pipeline"]["final_handoff_path"], final_handoff_path)
        self.assertEqual(updated["artifacts"]["final_handoff_path"], final_handoff_path)
        self.assertEqual(updated["final_handoff"]["path"], final_handoff_path)
        self.assertEqual(updated["final_handoff"]["link"], final_handoff_path)

        validation = validate_module.validate_approved_delivery_pipeline(project_dir)
        self.assertTrue(validation["ok"], msg=validation)
        self.assertEqual(validation["workspace_path"], workspace.as_posix())
        self.assertEqual(validation["final_handoff_path"], final_handoff_path)


if __name__ == "__main__":
    unittest.main()
