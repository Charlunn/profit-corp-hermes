import importlib.util
import json
import shutil
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT_DIR = Path(__file__).resolve().parent.parent
START_SCRIPT_PATH = ROOT_DIR / "scripts" / "start_approved_project_delivery.py"


def load_module(module_name: str, script_path: Path):
    if not script_path.exists():
        raise AssertionError(f"expected script to exist: {script_path}")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ApprovedDeliveryResumeTests(unittest.TestCase):
    maxDiff = None

    def addCleanupPath(self, path: Path) -> None:
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))

    def create_resume_fixture(self, *, stage: str, status: str = "blocked") -> tuple[Path, Path, Path, Path]:
        root = Path(tempfile.mkdtemp(prefix="approved-delivery-resume-"))
        self.addCleanupPath(root)
        project_dir = root / "assets" / "shared" / "approved-projects" / "lead-capture-copilot"
        project_dir.mkdir(parents=True, exist_ok=True)
        workspace_root = root / "generated-workspaces"
        workspace_root.mkdir(parents=True, exist_ok=True)
        workspace = workspace_root / "lead-capture-copilot"
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
            "workspace_name": "lead-capture-copilot",
            "app_key": "lead_capture_copilot",
            "app_name": "Lead Capture Copilot",
            "app_url": "https://lead-capture.example.com",
            "template_source_path": "C:/Users/42236/Desktop/standalone-saas-template",
            "canonical_contract_path": (ROOT_DIR / "docs" / "platform" / "standalone-saas-template-contract.md").as_posix(),
        }
        (hermes_dir / "project-metadata.json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (hermes_dir / "shared-backend-guardrails.json").write_text(
            json.dumps(
                {
                    "backend_model": "shared-supabase",
                    "app_key": metadata["app_key"],
                    "canonical_contract_path": metadata["canonical_contract_path"],
                    "allowed_shared_tables": ["users", "orders", "payments", "subscriptions"],
                    "protected_paths": ["src/lib/paypal.ts"],
                    "client_write_blocked_tables": ["users", "orders", "payments", "subscriptions"],
                    "allow_independent_backend": False,
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
        (hermes_dir / "PROJECT_BRIEF_ENTRYPOINT.md").write_text("# Hermes Project Brief Entrypoint\n", encoding="utf-8")
        authority_path = project_dir / "APPROVED_PROJECT.json"
        authority = {
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
            "approved_scope": ["capture inbound lead notes"],
            "target_user": "Solo operators who need to qualify inbound leads quickly.",
            "mvp_framing": "Turn incoming lead notes into ranked follow-up actions.",
            "constraints": ["reuse shared Supabase auth and payments"],
            "acceptance_gates": ["workspace bootstrap ready"],
            "pipeline": {
                "stage": stage,
                "status": status,
                "block_reason": "resume_required" if status == "blocked" else None,
                "resume_from_stage": stage,
                "workspace_path": workspace.as_posix(),
            },
            "artifacts": {
                "project_directory": project_dir.as_posix(),
                "authority_record_path": authority_path.as_posix(),
                "delivery_brief_path": (project_dir / "PROJECT_BRIEF.md").as_posix(),
                "template_contract_path": (ROOT_DIR / "docs" / "platform" / "standalone-saas-template-contract.md").as_posix(),
                "project_metadata_path": ".hermes/project-metadata.json",
                "shared_backend_guardrails_path": ".hermes/shared-backend-guardrails.json",
                "approved_brief_entrypoint_path": ".hermes/PROJECT_BRIEF_ENTRYPOINT.md",
                "gsd_constraints_path": (ROOT_DIR / ".planning" / "phases" / "09-claude-code-delivery-team-orchestration" / "09-01-PLAN.md").as_posix(),
                "events_path": (project_dir / "approved-delivery-events.jsonl").as_posix(),
                "status_path": (project_dir / "DELIVERY_PIPELINE_STATUS.md").as_posix(),
                "workspace_path": workspace.as_posix(),
            },
        }
        authority_path.write_text(json.dumps(authority, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (project_dir / "PROJECT_BRIEF.md").write_text("# Approved Project Brief\n", encoding="utf-8")
        return root, project_dir, authority_path, workspace

    def read_json(self, path: Path) -> dict:
        return json.loads(path.read_text(encoding="utf-8"))

    def read_events(self, project_dir: Path) -> list[dict]:
        events_path = project_dir / "approved-delivery-events.jsonl"
        if not events_path.exists():
            return []
        return [json.loads(line) for line in events_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def test_resume_rebuilds_workspace_when_required_repo_level_metadata_is_missing(self) -> None:
        start_module = load_module("start_approved_project_delivery", START_SCRIPT_PATH)
        root, project_dir, authority_path, workspace = self.create_resume_fixture(stage="workspace_instantiation")
        metadata_path = workspace / ".hermes" / "project-metadata.json"
        metadata = self.read_json(metadata_path)
        metadata.pop("gsd_constraints_path", None)
        metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        with mock.patch.object(start_module, "ROOT_DIR", root), \
             mock.patch.object(start_module, "resolve_approved_template_source", return_value=({
                 "asset_id": "standalone-saas-template",
                 "canonical_contract": "docs/platform/standalone-saas-template-contract.md",
             }, root)), \
             mock.patch.object(start_module, "restore_approved_workspace") as restore_mock, \
             mock.patch.object(start_module, "instantiate_workspace") as instantiate_mock, \
             mock.patch.object(start_module, "check_template_conformance", return_value={"ok": True, "report_path": (project_dir / "conformance-report.md").as_posix()}), \
             mock.patch.object(start_module, "initialize_delivery_run", return_value={
                 "ok": True,
                 "workspace": workspace.as_posix(),
                 "manifest_path": (workspace / ".hermes" / "delivery-run-manifest.json").as_posix(),
                 "status_path": (workspace / ".hermes" / "DELIVERY_STATUS.md").as_posix(),
                 "run_id": "delivery-lead-capture-copilot-001",
             }), \
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
             mock.patch.object(start_module, "dispatch_specialist_agent", return_value={"ok": True, "transcript_path": (workspace / ".hermes" / "design-claude-code.txt").as_posix(), "stdout": "ok", "stderr": ""}), \
             mock.patch.object(start_module, "build_specialist_dispatch_prompt", return_value="stage prompt"), \
             mock.patch.object(start_module, "ensure_claude_code_available", return_value="claude"), \
             mock.patch.object(start_module, "ensure_ui_ux_preflight", return_value=(workspace / ".hermes" / "ui-ux-design-system.md").as_posix()), \
             mock.patch.object(start_module, "update_app_definition_for_delivery", return_value=(workspace / "src" / "lib" / "app-definition.ts").as_posix()), \
             mock.patch.object(start_module, "write_workspace_change_inventory", side_effect=lambda *args, **kwargs: (workspace / ".hermes" / "workspace-changes.json").as_posix()), \
             mock.patch.object(start_module, "write_stage_handoff", side_effect=lambda _workspace, artifact, _content: (workspace / artifact).as_posix()), \
             mock.patch.object(start_module, "write_final_delivery_summary", return_value=(workspace / ".hermes" / "FINAL_DELIVERY.md").as_posix()), \
             mock.patch.object(start_module, "inspect_workspace_changes", return_value={"classification": "product_only", "evidence_path": (workspace / ".hermes" / "protected-surface-classification-testing.json").as_posix()}), \
             mock.patch.object(start_module, "run_github_sync", return_value={
                 "ok": True,
                 "repository_url": "https://github.com/profit-corp/lead-capture-copilot.git",
                 "default_branch": "main",
                 "synced_commit": "abc1234",
                 "evidence_path": (workspace / ".hermes" / "github-sync.json").as_posix(),
                 "remote_action": "updated",
                 "push_transport": "ssh",
                 "push_attempts": [
                     {"transport": "https", "status": "failed"},
                     {"transport": "ssh", "status": "ok"},
                 ],
             }):
            result = start_module.resume_approved_project_delivery(authority_path)

        self.assertTrue(result["ok"], msg=result)
        restore_mock.assert_called_once()
        instantiate_mock.assert_not_called()

    def test_resume_restarts_from_workspace_instantiation_without_recreating_existing_workspace(self) -> None:
        start_module = load_module("start_approved_project_delivery", START_SCRIPT_PATH)
        root, project_dir, authority_path, workspace = self.create_resume_fixture(stage="workspace_instantiation")

        with mock.patch.object(start_module, "ROOT_DIR", root), \
             mock.patch.object(start_module, "instantiate_workspace") as instantiate_mock, \
             mock.patch.object(start_module, "workspace_instantiation_artifacts_ready", return_value=True), \
             mock.patch.object(start_module, "check_template_conformance", return_value={"ok": True, "report_path": (project_dir / "conformance-report.md").as_posix()}), \
             mock.patch.object(start_module, "initialize_delivery_run", return_value={
                 "ok": True,
                 "workspace": workspace.as_posix(),
                 "manifest_path": (workspace / ".hermes" / "delivery-run-manifest.json").as_posix(),
                 "status_path": (workspace / ".hermes" / "DELIVERY_STATUS.md").as_posix(),
                 "run_id": "delivery-lead-capture-copilot-001",
             }), \
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
             mock.patch.object(start_module, "dispatch_specialist_agent", return_value={"ok": True, "transcript_path": (workspace / ".hermes" / "design-claude-code.txt").as_posix(), "stdout": "ok", "stderr": ""}), \
             mock.patch.object(start_module, "build_specialist_dispatch_prompt", return_value="stage prompt"), \
             mock.patch.object(start_module, "ensure_claude_code_available", return_value="claude"), \
             mock.patch.object(start_module, "ensure_ui_ux_preflight", return_value=(workspace / ".hermes" / "ui-ux-design-system.md").as_posix()), \
             mock.patch.object(start_module, "update_app_definition_for_delivery", return_value=(workspace / "src" / "lib" / "app-definition.ts").as_posix()), \
             mock.patch.object(start_module, "write_workspace_change_inventory", side_effect=lambda *args, **kwargs: (workspace / ".hermes" / "workspace-changes.json").as_posix()), \
             mock.patch.object(start_module, "write_stage_handoff", side_effect=lambda _workspace, artifact, _content: (workspace / artifact).as_posix()), \
             mock.patch.object(start_module, "write_final_delivery_summary", return_value=(workspace / ".hermes" / "FINAL_DELIVERY.md").as_posix()), \
             mock.patch.object(start_module, "inspect_workspace_changes", return_value={"classification": "product_only", "evidence_path": (workspace / ".hermes" / "protected-surface-classification-testing.json").as_posix()}), \
             mock.patch.object(start_module, "run_github_sync", return_value={
                 "ok": True,
                 "repository_url": "https://github.com/profit-corp/lead-capture-copilot.git",
                 "default_branch": "main",
                 "synced_commit": "abc1234",
                 "evidence_path": (workspace / ".hermes" / "github-sync.json").as_posix(),
                 "remote_action": "updated",
                 "push_transport": "ssh",
                 "push_attempts": [
                     {"transport": "https", "status": "failed"},
                     {"transport": "ssh", "status": "ok"},
                 ],
             }):
            result = start_module.resume_approved_project_delivery(authority_path)

        self.assertTrue(result["ok"], msg=result)
        instantiate_mock.assert_not_called()
        updated = self.read_json(authority_path)
        self.assertEqual(updated["pipeline"]["workspace_path"], workspace.as_posix())
        self.assertEqual(updated["pipeline"]["delivery_run_id"], "delivery-lead-capture-copilot-001")
        self.assertEqual(updated["shipping"]["github"]["repository_owner"], "profit-corp")
        self.assertEqual(updated["shipping"]["github"]["repository_name"], "profit-corp/lead-capture-copilot")
        self.assertEqual(updated["shipping"]["github"]["repository_url"], "https://github.com/profit-corp/lead-capture-copilot.git")
        self.assertEqual(updated["shipping"]["github"]["remote_action"], "updated")
        self.assertEqual(updated["shipping"]["github"]["push_transport"], "ssh")
        self.assertEqual(updated["shipping"]["github"]["push_attempts"][0]["transport"], "https")
        self.assertEqual(updated["artifacts"]["conformance_evidence_path"], (project_dir / "conformance-report.md").as_posix())
        self.assertEqual(updated["conformance_evidence_path"], (project_dir / "conformance-report.md").as_posix())
        events = self.read_events(project_dir)
        self.assertEqual([event["stage"] for event in events], ["workspace_instantiation", "conformance", "delivery_run_bootstrap", "design", "development", "testing", "git_versioning", "release_readiness", "github_repository", "github_sync", "vercel_linkage"])

    def test_resume_restarts_from_last_incomplete_stage_without_reinstantiating_workspace(self) -> None:
        start_module = load_module("start_approved_project_delivery", START_SCRIPT_PATH)
        root, project_dir, authority_path, workspace = self.create_resume_fixture(stage="conformance")
        original_record = self.read_json(authority_path)

        with mock.patch.object(start_module, "ROOT_DIR", root), \
             mock.patch.object(start_module, "instantiate_workspace") as instantiate_mock, \
             mock.patch.object(start_module, "workspace_instantiation_artifacts_ready", return_value=True), \
             mock.patch.object(start_module, "check_template_conformance", return_value={"ok": True, "report_path": (project_dir / "conformance-report.md").as_posix()}), \
             mock.patch.object(start_module, "initialize_delivery_run", return_value={
                 "ok": True,
                 "workspace": workspace.as_posix(),
                 "manifest_path": (workspace / ".hermes" / "delivery-run-manifest.json").as_posix(),
                 "status_path": (workspace / ".hermes" / "DELIVERY_STATUS.md").as_posix(),
                 "run_id": "delivery-lead-capture-copilot-001",
             }), \
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
             mock.patch.object(start_module, "dispatch_specialist_agent", return_value={"ok": True, "transcript_path": (workspace / ".hermes" / "design-claude-code.txt").as_posix(), "stdout": "ok", "stderr": ""}), \
             mock.patch.object(start_module, "build_specialist_dispatch_prompt", return_value="stage prompt"), \
             mock.patch.object(start_module, "ensure_claude_code_available", return_value="claude"), \
             mock.patch.object(start_module, "ensure_ui_ux_preflight", return_value=(workspace / ".hermes" / "ui-ux-design-system.md").as_posix()), \
             mock.patch.object(start_module, "update_app_definition_for_delivery", return_value=(workspace / "src" / "lib" / "app-definition.ts").as_posix()), \
             mock.patch.object(start_module, "write_workspace_change_inventory", side_effect=lambda *args, **kwargs: (workspace / ".hermes" / "workspace-changes.json").as_posix()), \
             mock.patch.object(start_module, "write_stage_handoff", side_effect=lambda _workspace, artifact, _content: (workspace / artifact).as_posix()), \
             mock.patch.object(start_module, "write_final_delivery_summary", return_value=(workspace / ".hermes" / "FINAL_DELIVERY.md").as_posix()), \
             mock.patch.object(start_module, "inspect_workspace_changes", return_value={"classification": "product_only", "evidence_path": (workspace / ".hermes" / "protected-surface-classification-testing.json").as_posix()}), \
             mock.patch.object(start_module, "run_github_sync", return_value={
                 "ok": True,
                 "repository_url": "https://github.com/profit-corp/lead-capture-copilot.git",
                 "default_branch": "main",
                 "synced_commit": "abc1234",
                 "evidence_path": (workspace / ".hermes" / "github-sync.json").as_posix(),
                 "remote_action": "updated",
                 "push_transport": "ssh",
                 "push_attempts": [
                     {"transport": "https", "status": "failed"},
                     {"transport": "ssh", "status": "ok"},
                 ],
             }):
            result = start_module.resume_approved_project_delivery(authority_path)

        self.assertTrue(result["ok"], msg=result)
        instantiate_mock.assert_not_called()
        updated = self.read_json(authority_path)
        self.assertEqual(updated["pipeline"]["workspace_path"], workspace.as_posix())
        self.assertEqual(updated["approval"], original_record["approval"])
        self.assertEqual(updated["project_identity"], original_record["project_identity"])
        self.assertEqual(updated["pipeline"]["delivery_run_id"], "delivery-lead-capture-copilot-001")
        events = self.read_events(project_dir)
        self.assertEqual([event["stage"] for event in events], ["conformance", "delivery_run_bootstrap", "design", "development", "testing", "git_versioning", "release_readiness", "github_repository", "github_sync", "vercel_linkage"])

    def test_resume_from_github_sync_restarts_at_vercel_linkage_before_deploy(self) -> None:
        start_module = load_module("start_approved_project_delivery", START_SCRIPT_PATH)
        root, project_dir, authority_path, workspace = self.create_resume_fixture(stage="github_sync")
        authority = self.read_json(authority_path)
        authority["pipeline"]["delivery_run_id"] = "delivery-lead-capture-copilot-001"
        authority["pipeline"]["resume_from_stage"] = "vercel_linkage"
        authority["shipping"] = {
            "github": {
                "repository_mode": "attach",
                "repository_owner": "profit-corp",
                "repository_name": "profit-corp/lead-capture-copilot",
                "repository_url": "https://github.com/profit-corp/lead-capture-copilot.git",
                "default_branch": "main",
                "delivery_run_id": "delivery-lead-capture-copilot-001",
                "last_sync_status": "completed",
            },
            "vercel": {},
        }
        authority_path.write_text(json.dumps(authority, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        link_calls: list[str] = []
        deploy_calls: list[str] = []

        with mock.patch.object(start_module, "ROOT_DIR", root), \
             mock.patch.object(start_module, "link_vercel_project", side_effect=lambda *args, **kwargs: link_calls.append("link") or {
                 "ok": True,
                 "linked": True,
                 "project_id": "prj_current",
                 "project_name": "lead-capture-copilot-prod",
                 "project_url": "https://vercel.com/profit-corp/lead-capture-copilot-prod",
                 "team_scope": "profit-corp",
                 "auth_source": "vercel_cli_session",
                 "auth_source_details": {"username": "operator"},
                 "evidence_path": (workspace / ".hermes" / "vercel-link.json").as_posix(),
                 "audit_path": (workspace / ".hermes" / "vercel-link-audit.json").as_posix(),
                 "env_contract_path": (workspace / ".hermes" / "vercel-env-contract.json").as_posix(),
                 "env_contract": {"evidence_path": (workspace / ".hermes" / "vercel-env-contract.json").as_posix()},
                 "required_env": {"platform_managed": ["SUPABASE_SERVICE_ROLE_KEY"]},
             }), \
             mock.patch.object(start_module, "run_vercel_deploy", side_effect=lambda *args, **kwargs: deploy_calls.append("deploy") or {
                 "ok": True,
                 "deploy_url": "https://lead-capture-copilot-prod.vercel.app",
                 "deploy_status": "ready",
                 "deploy_evidence_path": (workspace / ".hermes" / "vercel-deploy.json").as_posix(),
                 "deploy_audit_path": (workspace / ".hermes" / "vercel-deploy-audit.json").as_posix(),
                 "deployment_url": "https://lead-capture-copilot-prod.vercel.app",
                 "deployment_status": "ready",
                 "deployment_evidence_path": (workspace / ".hermes" / "vercel-deploy.json").as_posix(),
                 "final_handoff_path": (workspace / ".hermes" / "FINAL_DELIVERY.md").as_posix(),
             }):
            result = start_module.resume_approved_project_delivery(authority_path)

        self.assertTrue(result["ok"], msg=result)
        self.assertEqual(link_calls, ["link"])
        self.assertEqual(deploy_calls, [])
        updated = self.read_json(authority_path)
        self.assertEqual(updated["pipeline"]["stage"], "vercel_linkage")
        self.assertEqual(updated["pipeline"]["resume_from_stage"], "vercel_deploy")
        self.assertEqual(updated["shipping"]["vercel"]["project_name"], "lead-capture-copilot-prod")

    def test_resume_replaces_stale_blocked_vercel_truth_with_successful_link_and_deploy_state(self) -> None:
        start_module = load_module("start_approved_project_delivery", START_SCRIPT_PATH)
        root, project_dir, authority_path, workspace = self.create_resume_fixture(stage="vercel_linkage")
        authority = self.read_json(authority_path)
        authority["pipeline"].update(
            {
                "delivery_run_id": "delivery-lead-capture-copilot-001",
                "status": "blocked",
                "block_reason": "vercel_linkage_failed",
                "resume_from_stage": "vercel_linkage",
                "evidence_path": (workspace / ".hermes" / "stale-vercel-link-blocked.json").as_posix(),
            }
        )
        authority["shipping"] = {
            "github": {
                "repository_mode": "attach",
                "repository_owner": "profit-corp",
                "repository_name": "profit-corp/lead-capture-copilot",
                "repository_url": "https://github.com/profit-corp/lead-capture-copilot.git",
                "default_branch": "main",
                "delivery_run_id": "delivery-lead-capture-copilot-001",
                "last_sync_status": "completed",
                "synced_commit": "abc1234",
            },
            "vercel": {
                "project_id": "stale_project",
                "project_name": "stale-project-prod",
                "project_url": "https://vercel.com/old-team/stale-project-prod",
                "team_scope": "old-team",
                "linked": False,
                "auth_source": "stale_source",
                "auth_source_details": {"username": "stale-user"},
                "link_evidence_path": (workspace / ".hermes" / "stale-vercel-link.json").as_posix(),
                "env_contract_path": (workspace / ".hermes" / "stale-vercel-env-contract.json").as_posix(),
                "env_contract": {"evidence_path": (workspace / ".hermes" / "stale-vercel-env-contract.json").as_posix()},
                "required_env": {"platform_managed": ["OLD_SECRET"]},
                "deploy_url": "https://stale-project.vercel.app",
                "deploy_status": "failed",
                "deploy_evidence_path": (workspace / ".hermes" / "stale-vercel-deploy.json").as_posix(),
                "deployment_url": "https://stale-project.vercel.app",
                "deployment_status": "failed",
                "deployment_evidence_path": (workspace / ".hermes" / "stale-vercel-deploy.json").as_posix(),
            },
        }
        authority_path.write_text(json.dumps(authority, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        stale_block_event = {
            "project_slug": "lead-capture-copilot",
            "stage": "vercel_linkage",
            "status": "blocked",
            "action": "stage_blocked",
            "timestamp": "2026-04-27T08:37:00Z",
            "outcome": "blocked",
            "authority_record_path": authority_path.as_posix(),
            "brief_path": (project_dir / "PROJECT_BRIEF.md").as_posix(),
            "workspace_path": workspace.as_posix(),
            "delivery_run_id": "delivery-lead-capture-copilot-001",
            "artifact": (workspace / ".hermes" / "stale-vercel-link-blocked.json").as_posix(),
            "block_reason": "vercel_linkage_failed",
            "evidence_path": (workspace / ".hermes" / "stale-vercel-link-blocked.json").as_posix(),
            "resume_from_stage": "vercel_linkage",
            "final_handoff_path": "",
            "shipping": authority["shipping"],
        }
        (project_dir / "approved-delivery-events.jsonl").write_text(json.dumps(stale_block_event, ensure_ascii=False) + "\n", encoding="utf-8")

        final_handoff = workspace / ".hermes" / "FINAL_DELIVERY.md"
        final_handoff.write_text("# Final Delivery\n", encoding="utf-8")

        with mock.patch.object(start_module, "ROOT_DIR", root), \
             mock.patch.object(start_module, "link_vercel_project", return_value={
                 "ok": True,
                 "linked": True,
                 "project_id": "prj_current",
                 "project_name": "lead-capture-copilot-prod",
                 "project_url": "https://vercel.com/profit-corp/lead-capture-copilot-prod",
                 "team_scope": "profit-corp",
                 "auth_source": "vercel_cli_session",
                 "auth_source_details": {"username": "operator"},
                 "evidence_path": (workspace / ".hermes" / "vercel-link.json").as_posix(),
                 "audit_path": (workspace / ".hermes" / "vercel-link-audit.json").as_posix(),
                 "env_contract_path": (workspace / ".hermes" / "vercel-env-contract.json").as_posix(),
                 "env_contract": {"evidence_path": (workspace / ".hermes" / "vercel-env-contract.json").as_posix()},
                 "required_env": {
                     "platform_managed": ["SUPABASE_SERVICE_ROLE_KEY"],
                     "identity_derived": {"APP_KEY": "lead_capture_copilot"},
                 },
             }), \
             mock.patch.object(start_module, "run_vercel_deploy", return_value={
                 "ok": True,
                 "deploy_url": "https://lead-capture-copilot-prod.vercel.app",
                 "deploy_status": "ready",
                 "deploy_evidence_path": (workspace / ".hermes" / "vercel-deploy.json").as_posix(),
                 "deploy_audit_path": (workspace / ".hermes" / "vercel-deploy-audit.json").as_posix(),
                 "deployment_url": "https://lead-capture-copilot-prod.vercel.app",
                 "deployment_status": "ready",
                 "deployment_evidence_path": (workspace / ".hermes" / "vercel-deploy.json").as_posix(),
                 "final_handoff_path": final_handoff.as_posix(),
             }):
            link_result = start_module.resume_approved_project_delivery(authority_path)
            self.assertTrue(link_result["ok"], msg=link_result)
            deploy_result = start_module.resume_approved_project_delivery(authority_path)
            self.assertTrue(deploy_result["ok"], msg=deploy_result)

        updated = self.read_json(authority_path)
        vercel = updated["shipping"]["vercel"]
        self.assertEqual(vercel["project_id"], "prj_current")
        self.assertEqual(vercel["project_name"], "lead-capture-copilot-prod")
        self.assertEqual(vercel["project_url"], "https://vercel.com/profit-corp/lead-capture-copilot-prod")
        self.assertEqual(vercel["team_scope"], "profit-corp")
        self.assertTrue(vercel["linked"])
        self.assertEqual(vercel["auth_source"], "vercel_cli_session")
        self.assertEqual(vercel["auth_source_details"]["username"], "operator")
        self.assertEqual(vercel["env_contract_path"], (workspace / ".hermes" / "vercel-env-contract.json").as_posix())
        self.assertEqual(vercel["deploy_url"], "https://lead-capture-copilot-prod.vercel.app")
        self.assertEqual(vercel["deploy_status"], "ready")
        self.assertEqual(vercel["deploy_evidence_path"], (workspace / ".hermes" / "vercel-deploy.json").as_posix())
        self.assertEqual(updated["pipeline"]["stage"], "vercel_deploy")
        self.assertEqual(updated["pipeline"]["status"], "completed")
        self.assertEqual(updated["pipeline"]["resume_from_stage"], "handoff")
        self.assertIsNone(updated["pipeline"]["block_reason"])
        self.assertEqual(updated["pipeline"]["evidence_path"], (workspace / ".hermes" / "vercel-deploy.json").as_posix())
        self.assertEqual(updated["pipeline"]["final_handoff_path"], final_handoff.as_posix())
        self.assertNotEqual(vercel["project_name"], "stale-project-prod")
        self.assertNotEqual(vercel["team_scope"], "old-team")
        self.assertNotEqual(vercel["deploy_url"], "https://stale-project.vercel.app")

        events = self.read_events(project_dir)
        self.assertEqual(events[0]["status"], "blocked")
        self.assertEqual(events[0]["block_reason"], "vercel_linkage_failed")
        self.assertEqual(events[-2]["stage"], "vercel_linkage")
        self.assertEqual(events[-2]["status"], "ready")
        self.assertEqual(events[-2]["shipping"]["vercel"]["project_name"], "lead-capture-copilot-prod")
        self.assertEqual(events[-1]["stage"], "vercel_deploy")
        self.assertEqual(events[-1]["status"], "completed")
        self.assertEqual(events[-1]["final_handoff_path"], final_handoff.as_posix())
        self.assertEqual(events[-1]["shipping"]["vercel"]["deploy_url"], "https://lead-capture-copilot-prod.vercel.app")

    def test_workspace_instantiation_refreshes_existing_workspace_without_deleting_git_history(self) -> None:
        start_module = load_module("start_approved_project_delivery", START_SCRIPT_PATH)
        root, project_dir, authority_path, workspace = self.create_resume_fixture(stage="workspace_instantiation")
        (workspace / ".git").mkdir(parents=True, exist_ok=True)
        (workspace / ".git" / "HEAD").write_text("ref: refs/heads/main\n", encoding="utf-8")
        (workspace / "src").mkdir(parents=True, exist_ok=True)
        (workspace / "src" / "lib").mkdir(parents=True, exist_ok=True)
        (workspace / "src" / "lib" / "app-definition.ts").write_text(
            'export const appDefinition = {\n  name: config.appName,\n  url: config.appUrl,\n  eyebrow: "Standalone SaaS Template",\n  headline: config.appName,\n  productId: `${config.appKey}_default_offer`,\n  description: `${config.appName} access`\n} as const;\n',
            encoding="utf-8",
        )
        authority = self.read_json(authority_path)
        authority["pipeline"].update({
            "status": "blocked",
            "block_reason": "workspace_instantiation_failed",
            "resume_from_stage": "workspace_instantiation",
        })
        authority_path.write_text(json.dumps(authority, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        with mock.patch.object(start_module, "ROOT_DIR", root), \
             mock.patch.object(start_module, "workspace_instantiation_artifacts_ready", return_value=False), \
             mock.patch.object(start_module, "resolve_approved_template_source", return_value=({"asset_id": "standalone-saas-template"}, root)), \
             mock.patch.object(start_module, "instantiate_workspace") as instantiate_mock:
            result = start_module.resume_approved_project_delivery(authority_path)

        self.assertFalse(result["ok"], msg=result)
        self.assertEqual(result["stage"], "conformance")
        self.assertEqual(result["block_reason"], "conformance_failed")
        self.assertIn("check_template_conformance.py", result["error"])
        instantiate_mock.assert_not_called()
        self.assertTrue((workspace / ".git" / "HEAD").exists())
        self.assertTrue((workspace / ".env").exists())
        self.assertTrue((workspace / "vercel.json").exists())
        self.assertIn("APP_KEY=lead_capture_copilot", (workspace / ".env").read_text(encoding="utf-8"))

        start_module = load_module("start_approved_project_delivery", START_SCRIPT_PATH)
        root, project_dir, authority_path, workspace = self.create_resume_fixture(stage="handoff", status="completed")
        final_handoff = workspace / ".hermes" / "FINAL_DELIVERY.md"
        final_handoff.write_text("# Final Delivery\n", encoding="utf-8")
        authority = self.read_json(authority_path)
        authority["pipeline"]["delivery_run_id"] = "delivery-lead-capture-copilot-001"
        authority["pipeline"]["final_handoff_path"] = final_handoff.as_posix()
        authority["artifacts"]["final_handoff_path"] = final_handoff.as_posix()
        authority_path.write_text(json.dumps(authority, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        with mock.patch.object(start_module, "ROOT_DIR", root), \
             mock.patch.object(start_module, "instantiate_workspace") as instantiate_mock, \
             mock.patch.object(start_module, "check_template_conformance") as conformance_mock, \
             mock.patch.object(start_module, "initialize_delivery_run") as start_run_mock:
            result = start_module.resume_approved_project_delivery(authority_path)

        self.assertTrue(result["ok"], msg=result)
        self.assertEqual(result["stage"], "handoff")
        self.assertEqual(result["status"], "completed")
        instantiate_mock.assert_not_called()
        conformance_mock.assert_not_called()
        start_run_mock.assert_not_called()
        events = self.read_events(project_dir)
        self.assertEqual(events, [], "post-handoff resume should not append duplicate events")


if __name__ == "__main__":
    unittest.main()
