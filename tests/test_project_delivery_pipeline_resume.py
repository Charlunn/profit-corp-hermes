import importlib.util
import hashlib
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

    def _write_json_fixture(self, path: Path, payload: dict) -> str:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return path.as_posix()

    def _fake_materialize_product_surface(self, _workspace: Path, _record: dict) -> list[str]:
        return ["src/app/page.tsx", "src/app/dashboard/page.tsx", "src/app/demo/page.tsx"]

    def _write_stage_handoff_fixture(self, workspace: Path, artifact: str, _content: str) -> str:
        path = workspace / artifact
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# Stage Handoff\n", encoding="utf-8")
        return path.as_posix()

    def _make_dispatch_result(self, workspace: Path, *, transcript_name: str = "design-claude-code.txt", skills: list[str] | None = None, hermes_profile: str = "arch") -> dict:
        transcript_path = workspace / ".hermes" / transcript_name
        transcript_path.parent.mkdir(parents=True, exist_ok=True)
        transcript_path.write_text("specialist transcript evidence\n", encoding="utf-8")
        return {
            "ok": True,
            "transcript_path": transcript_path.as_posix(),
            "stdout": "ok",
            "stderr": "",
            "skills": skills or [],
            "hermes_profile": hermes_profile,
            "command": ["hermes", "-p", hermes_profile, "chat", "-q", "stage prompt", "-Q"],
        }

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
        (hermes_dir / "ui-ux-design-system.md").write_text("# UI UX Design System\n", encoding="utf-8")
        ui_brief_contract = {
            "pain_point": "capture inbound lead notes",
            "core_workflow": [
                "User opens the product and immediately sees a workflow focused on: capture inbound lead notes",
                "User completes at least one concrete task that proves the app can deliver a concrete user workflow",
                "User receives a visible result, output, or paid next action rather than generic template copy",
            ],
            "monetization": [
                "Offer a paid subscription that continuously solves capture inbound lead notes for Solo operators who need to qualify inbound leads quickly..",
                "Show a clear upgrade/paywall surface tied to the primary workflow outcome rather than a template placeholder offer.",
                "Release-readiness evidence must prove the paid path is visible in the product or explicitly staged behind a governed integration boundary.",
            ],
            "required_languages": ["en", "zh", "es", "ar", "pt", "fr", "hi", "ja", "ru"],
            "screen_inventory": ["capture inbound lead notes"],
        }
        (hermes_dir / "ui-ux-design-system.summary.json").write_text(
            json.dumps(
                {
                    "generated_by": "/ui-ux-pro-max",
                    "artifact_path": (hermes_dir / "ui-ux-design-system.md").as_posix(),
                    "stage": "design",
                    "role": "design-specialist",
                    "app_name": "Lead Capture Copilot",
                    "target_user": "Solo operators who need to qualify inbound leads quickly.",
                    "brief_contract": ui_brief_contract,
                    "coverage": {
                        "screen_inventory": ["capture inbound lead notes"],
                        "primary_workflow": [
                            "User opens the product and immediately sees a workflow focused on: capture inbound lead notes",
                            "User completes at least one concrete task that proves the app can deliver a concrete user workflow",
                            "User receives a visible result, output, or paid next action rather than generic template copy",
                        ],
                        "monetization_surface": [
                            "Offer a paid subscription that continuously solves capture inbound lead notes for Solo operators who need to qualify inbound leads quickly..",
                            "Show a clear upgrade/paywall surface tied to the primary workflow outcome rather than a template placeholder offer.",
                            "Release-readiness evidence must prove the paid path is visible in the product or explicitly staged behind a governed integration boundary.",
                        ],
                        "multilingual_coverage": ["en", "zh", "es", "ar", "pt", "fr", "hi", "ja", "ru"],
                        "responsive_rules": [
                            "Primary workflow must remain usable on desktop and mobile widths.",
                            "Responsive behavior must preserve CTA clarity and result visibility.",
                        ],
                        "accessibility_rules": [
                            "Primary actions must keep visible labels and focus states.",
                            "Critical workflow states must remain understandable without color alone.",
                        ],
                        "states": ["empty", "loading", "error", "success"],
                    },
                    "summary_hash": hashlib.sha256(
                        json.dumps(ui_brief_contract, ensure_ascii=False, sort_keys=True).encode("utf-8")
                    ).hexdigest(),
                },
                ensure_ascii=False,
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )
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
             mock.patch.object(start_module, "dispatch_specialist_agent", return_value=self._make_dispatch_result(workspace)), \
             mock.patch.object(start_module, "build_specialist_dispatch_prompt", return_value="stage prompt"), \
             mock.patch.object(start_module, "ensure_ui_ux_preflight", return_value=(workspace / ".hermes" / "ui-ux-design-system.md").as_posix()), \
             mock.patch.object(start_module, "materialize_product_surface", side_effect=self._fake_materialize_product_surface), \
             mock.patch.object(start_module, "update_app_definition_for_delivery", return_value=(workspace / "src" / "lib" / "app-definition.ts").as_posix()), \
             mock.patch.object(start_module, "write_workspace_change_inventory", side_effect=lambda *args, **kwargs: self._write_json_fixture(workspace / ".hermes" / "workspace-changes.json", {
                 "stage": kwargs.get("stage", "development"),
                 "role": kwargs.get("role", "development-specialist"),
                 "touched_paths": ["src/lib/app-definition.ts", "src/app/page.tsx", "src/app/dashboard/page.tsx", "src/app/demo/page.tsx"],
                 "product_proof_paths": ["src/app/page.tsx", "src/app/dashboard/page.tsx", "src/app/demo/page.tsx", "src/lib/app-definition.ts"],
                 "template_only": False,
                 "template_only_issues": [],
             })), \
             mock.patch.object(start_module, "write_stage_handoff", side_effect=self._write_stage_handoff_fixture), \
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
             mock.patch.object(start_module, "dispatch_specialist_agent", return_value=self._make_dispatch_result(workspace)), \
             mock.patch.object(start_module, "build_specialist_dispatch_prompt", return_value="stage prompt"), \
             mock.patch.object(start_module, "ensure_ui_ux_preflight", return_value=(workspace / ".hermes" / "ui-ux-design-system.md").as_posix()), \
             mock.patch.object(start_module, "materialize_product_surface", side_effect=self._fake_materialize_product_surface), \
             mock.patch.object(start_module, "update_app_definition_for_delivery", return_value=(workspace / "src" / "lib" / "app-definition.ts").as_posix()), \
             mock.patch.object(start_module, "write_workspace_change_inventory", side_effect=lambda *args, **kwargs: self._write_json_fixture(workspace / ".hermes" / "workspace-changes.json", {
                 "stage": kwargs.get("stage", "development"),
                 "role": kwargs.get("role", "development-specialist"),
                 "touched_paths": ["src/lib/app-definition.ts", "src/app/page.tsx", "src/app/dashboard/page.tsx", "src/app/demo/page.tsx"],
                 "product_proof_paths": ["src/app/page.tsx", "src/app/dashboard/page.tsx", "src/app/demo/page.tsx", "src/lib/app-definition.ts"],
                 "template_only": False,
                 "template_only_issues": [],
             })), \
             mock.patch.object(start_module, "write_stage_handoff", side_effect=self._write_stage_handoff_fixture), \
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
             mock.patch.object(start_module, "dispatch_specialist_agent", return_value=self._make_dispatch_result(workspace)), \
             mock.patch.object(start_module, "build_specialist_dispatch_prompt", return_value="stage prompt"), \
             mock.patch.object(start_module, "ensure_ui_ux_preflight", return_value=(workspace / ".hermes" / "ui-ux-design-system.md").as_posix()), \
             mock.patch.object(start_module, "materialize_product_surface", side_effect=self._fake_materialize_product_surface), \
             mock.patch.object(start_module, "update_app_definition_for_delivery", return_value=(workspace / "src" / "lib" / "app-definition.ts").as_posix()), \
             mock.patch.object(start_module, "write_workspace_change_inventory", side_effect=lambda *args, **kwargs: self._write_json_fixture(workspace / ".hermes" / "workspace-changes.json", {
                 "stage": kwargs.get("stage", "development"),
                 "role": kwargs.get("role", "development-specialist"),
                 "touched_paths": ["src/lib/app-definition.ts", "src/app/page.tsx", "src/app/dashboard/page.tsx", "src/app/demo/page.tsx"],
                 "product_proof_paths": ["src/app/page.tsx", "src/app/dashboard/page.tsx", "src/app/demo/page.tsx", "src/lib/app-definition.ts"],
                 "template_only": False,
                 "template_only_issues": [],
             })), \
             mock.patch.object(start_module, "write_stage_handoff", side_effect=self._write_stage_handoff_fixture), \
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
        (workspace / ".hermes" / "stale-vercel-link-blocked.json").write_text('{"ok": false}\n', encoding="utf-8")

        stale_block_event = {
            "project_slug": "lead-capture-copilot",
            "stage": "vercel_linkage",
            "status": "blocked",
            "action": "stage_blocked",
            "timestamp": "2026-04-27T08:37:00Z",
            "outcome": {
                "status": "blocked",
                "result": "blocked",
            },
            "authority_record_path": authority_path.as_posix(),
            "brief_path": (project_dir / "PROJECT_BRIEF.md").as_posix(),
            "workspace_path": workspace.as_posix(),
            "delivery_run_id": "delivery-lead-capture-copilot-001",
            "artifact": (workspace / ".hermes" / "stale-vercel-link-blocked.json").as_posix(),
            "block_reason": "vercel_linkage_failed",
            "evidence_path": (workspace / ".hermes" / "stale-vercel-link-blocked.json").as_posix(),
            "resume_from_stage": "vercel_linkage",
            "final_handoff_path": "",
            "gate": {
                "decision": "block",
                "reason": "vercel_linkage_failed",
            },
            "evidence": {
                "primary_path": (workspace / ".hermes" / "stale-vercel-link-blocked.json").as_posix(),
            },
            "handoff": {
                "artifact_path": (workspace / ".hermes" / "stale-vercel-link-blocked.json").as_posix(),
            },
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
        self.assertEqual(updated["pipeline"]["current_stage"], "vercel_deploy")
        self.assertEqual(updated["pipeline"]["current_status"], "completed")
        self.assertEqual(updated["pipeline"]["latest_governance"]["stage"], "vercel_deploy")
        self.assertEqual(updated["pipeline"]["latest_governance"]["status"], "completed")
        self.assertEqual(updated["pipeline"]["latest_governance"]["outcome"], "pass")
        self.assertEqual(updated["pipeline"]["resume_from_stage"], "handoff")
        self.assertIsNone(updated["pipeline"]["block_reason"])
        self.assertEqual(updated["pipeline"]["evidence_path"], (workspace / ".hermes" / "vercel-deploy.json").as_posix())
        self.assertEqual(updated["pipeline"]["final_handoff_path"], final_handoff.as_posix())
        self.assertEqual(updated["pipeline"]["latest_block_context"]["stage"], "vercel_linkage")
        self.assertEqual(updated["pipeline"]["latest_block_context"]["reason"], "vercel_linkage_failed")
        self.assertEqual(updated["pipeline"]["latest_block_context"]["status"], "resolved")
        self.assertEqual(updated["latest_blocked_prerequisite"]["stage"], "vercel_linkage")
        self.assertEqual(updated["latest_blocked_prerequisite"]["reason"], "vercel_linkage_failed")
        self.assertEqual(updated["latest_blocked_prerequisite"]["path"], (workspace / ".hermes" / "stale-vercel-link-blocked.json").as_posix())
        self.assertEqual(updated["latest_blocked_prerequisite"]["status"], "resolved")
        self.assertNotEqual(vercel["project_name"], "stale-project-prod")
        self.assertNotEqual(vercel["team_scope"], "old-team")
        self.assertNotEqual(vercel["deploy_url"], "https://stale-project.vercel.app")

        events = self.read_events(project_dir)
        self.assertEqual(events[0]["status"], "blocked")
        self.assertEqual(events[0]["block_reason"], "vercel_linkage_failed")
        self.assertEqual(events[0]["gate"]["decision"], "block")
        self.assertEqual(events[0]["evidence"]["primary_path"], (workspace / ".hermes" / "stale-vercel-link-blocked.json").as_posix())
        self.assertEqual(events[0]["outcome"]["status"], "blocked")
        self.assertEqual(events[-2]["stage"], "vercel_linkage")
        self.assertEqual(events[-2]["status"], "ready")
        self.assertEqual(events[-2]["gate"]["decision"], "pass")
        self.assertEqual(events[-2]["shipping"]["vercel"]["project_name"], "lead-capture-copilot-prod")
        self.assertEqual(events[-1]["stage"], "vercel_deploy")
        self.assertEqual(events[-1]["status"], "completed")
        self.assertEqual(events[-1]["handoff"]["final_handoff_path"], final_handoff.as_posix())
        self.assertEqual(events[-1]["outcome"]["status"], "completed")
        self.assertEqual(events[-1]["shipping"]["vercel"]["deploy_url"], "https://lead-capture-copilot-prod.vercel.app")

        status_text = (project_dir / "DELIVERY_PIPELINE_STATUS.md").read_text(encoding="utf-8")
        final_review_text = (project_dir / "FINAL_OPERATOR_REVIEW.md").read_text(encoding="utf-8")
        for surface_text in [status_text, final_review_text]:
            self.assertIn("**Pipeline Status**: `completed`", surface_text)
            self.assertIn("**Current Stage**: `vercel_deploy`", surface_text)
            self.assertIn("lead-capture-copilot-prod", surface_text)
            self.assertIn((workspace / ".hermes" / "vercel-deploy.json").as_posix(), surface_text)
            self.assertIn("vercel_linkage_failed", surface_text)
            self.assertIn((workspace / ".hermes" / "stale-vercel-link-blocked.json").as_posix(), surface_text)

    def test_resume_reblocks_when_blocked_authority_truth_drifts_from_event_history(self) -> None:
        start_module = load_module("start_approved_project_delivery", START_SCRIPT_PATH)
        root, project_dir, authority_path, workspace = self.create_resume_fixture(stage="vercel_linkage")
        authority = self.read_json(authority_path)
        authority["pipeline"].update(
            {
                "status": "blocked",
                "block_reason": "vercel_linkage_failed",
                "resume_from_stage": "vercel_linkage",
                "evidence_path": (workspace / ".hermes" / "authority-blocked.json").as_posix(),
                "delivery_run_id": "delivery-lead-capture-copilot-001",
            }
        )
        authority["latest_blocked_prerequisite"] = {
            "stage": "vercel_linkage",
            "reason": "vercel_linkage_failed",
            "path": (workspace / ".hermes" / "authority-blocked.json").as_posix(),
            "status": "blocked",
        }
        authority_path.write_text(json.dumps(authority, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        (workspace / ".hermes" / "authority-blocked.json").write_text('{"ok": false}\n', encoding="utf-8")

        stale_event = {
            "project_slug": "lead-capture-copilot",
            "stage": "vercel_linkage",
            "status": "blocked",
            "action": "stage_blocked",
            "timestamp": "2026-04-27T08:37:00Z",
            "outcome": {
                "status": "blocked",
                "result": "blocked",
            },
            "authority_record_path": authority_path.as_posix(),
            "brief_path": (project_dir / "PROJECT_BRIEF.md").as_posix(),
            "workspace_path": workspace.as_posix(),
            "delivery_run_id": "delivery-lead-capture-copilot-001",
            "artifact": (workspace / ".hermes" / "event-blocked.json").as_posix(),
            "block_reason": "missing_vercel_project_linkage",
            "evidence_path": (workspace / ".hermes" / "event-blocked.json").as_posix(),
            "resume_from_stage": "vercel_linkage",
            "final_handoff_path": "",
            "gate": {
                "decision": "block",
                "reason": "missing_vercel_project_linkage",
            },
            "evidence": {
                "primary_path": (workspace / ".hermes" / "event-blocked.json").as_posix(),
            },
            "handoff": {
                "artifact_path": (workspace / ".hermes" / "event-blocked.json").as_posix(),
            },
            "shipping": authority.get("shipping", {}),
        }
        (workspace / ".hermes" / "event-blocked.json").write_text('{"ok": false}\n', encoding="utf-8")
        (project_dir / "approved-delivery-events.jsonl").write_text(json.dumps(stale_event, ensure_ascii=False) + "\n", encoding="utf-8")

        with mock.patch.object(start_module, "ROOT_DIR", root), \
             mock.patch.object(start_module, "link_vercel_project") as link_mock:
            result = start_module.resume_approved_project_delivery(authority_path)

        self.assertFalse(result["ok"], msg=result)
        self.assertEqual(result["stage"], "vercel_linkage")
        self.assertEqual(result["block_reason"], "authority_state_drift")
        self.assertEqual(result["evidence_path"], (workspace / ".hermes" / "authority-blocked.json").as_posix())
        self.assertIn("latest blocked event", result["error"])
        link_mock.assert_not_called()

        updated = self.read_json(authority_path)
        self.assertEqual(updated["pipeline"]["status"], "blocked")
        self.assertEqual(updated["pipeline"]["block_reason"], "authority_state_drift")
        self.assertEqual(updated["pipeline"]["resume_from_stage"], "vercel_linkage")
        self.assertEqual(updated["pipeline"]["evidence_path"], (workspace / ".hermes" / "authority-blocked.json").as_posix())
        self.assertEqual(updated["latest_blocked_prerequisite"]["reason"], "authority_state_drift")
        self.assertEqual(updated["latest_blocked_prerequisite"]["path"], (workspace / ".hermes" / "authority-blocked.json").as_posix())
        self.assertEqual(updated["latest_blocked_prerequisite"]["status"], "blocked")

        events = self.read_events(project_dir)
        self.assertEqual(events[-1]["stage"], "vercel_linkage")
        self.assertEqual(events[-1]["status"], "blocked")
        self.assertEqual(events[-1]["block_reason"], "authority_state_drift")
        self.assertEqual(events[-1]["evidence_path"], (workspace / ".hermes" / "authority-blocked.json").as_posix())

        status_text = (project_dir / "DELIVERY_PIPELINE_STATUS.md").read_text(encoding="utf-8")
        final_review_text = (project_dir / "FINAL_OPERATOR_REVIEW.md").read_text(encoding="utf-8")
        self.assertIn("authority_state_drift", status_text)
        self.assertIn((workspace / ".hermes" / "authority-blocked.json").as_posix(), status_text)
        self.assertIn("authority_state_drift", final_review_text)
        self.assertIn((workspace / ".hermes" / "authority-blocked.json").as_posix(), final_review_text)

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
