import importlib.util
import json
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


ROOT_DIR = Path(__file__).resolve().parent.parent
START_SCRIPT_PATH = ROOT_DIR / "scripts" / "start_approved_project_delivery.py"
VERCEL_COMMON_PATH = ROOT_DIR / "scripts" / "vercel_delivery_common.py"


def load_module(module_name: str, script_path: Path):
    if not script_path.exists():
        raise AssertionError(f"expected script to exist: {script_path}")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class VercelDeliveryCommonTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="vercel-delivery-common-")
        self.addCleanup(self.tmp.cleanup)
        self.workspace = Path(self.tmp.name) / "workspace"
        self.workspace.mkdir(parents=True)

    def test_missing_cli_and_invalid_auth_produce_distinct_blocked_states(self) -> None:
        module = load_module("vercel_delivery_common_missing", VERCEL_COMMON_PATH)

        missing_cli = module.link_vercel_project(
            workspace_path=self.workspace,
            project_name="demo-app-prod",
            team_scope="profit-corp",
            env={"VERCEL_TOKEN": "token"},
            which=lambda name: None,
        )
        self.assertFalse(missing_cli["ok"], msg=missing_cli)
        self.assertEqual(missing_cli["block_reason"], "missing_vercel_cli")

        def failed_auth_probe(command, cwd, capture_output, text, check, env):
            if command == ["vercel", "whoami"]:
                return types.SimpleNamespace(
                    returncode=1,
                    stdout="",
                    stderr="Error: Please login to Vercel before continuing.",
                )
            raise AssertionError(f"unexpected command: {command}")

        invalid_auth = module.link_vercel_project(
            workspace_path=self.workspace,
            project_name="demo-app-prod",
            team_scope="profit-corp",
            env={},
            which=lambda name: "vercel",
            runner=failed_auth_probe,
        )
        self.assertFalse(invalid_auth["ok"], msg=invalid_auth)
        self.assertEqual(invalid_auth["block_reason"], "invalid_vercel_auth")

    def test_link_uses_local_cli_session_without_vercel_token(self) -> None:
        module = load_module("vercel_delivery_common_cli_auth", VERCEL_COMMON_PATH)
        commands: list[list[str]] = []

        def fake_runner(command, cwd, capture_output, text, check, env):
            commands.append(list(command))
            if command == ["vercel", "whoami"]:
                return types.SimpleNamespace(returncode=0, stdout="operator\n", stderr="")
            if command[:3] == ["vercel", "link", "--yes"]:
                return types.SimpleNamespace(returncode=0, stdout="linked", stderr="")
            raise AssertionError(f"unexpected command: {command}")

        result = module.link_vercel_project(
            workspace_path=self.workspace,
            project_name="demo-app-prod",
            team_scope="profit-corp",
            env={},
            which=lambda name: "vercel",
            runner=fake_runner,
        )

        self.assertTrue(result["ok"], msg=result)
        self.assertEqual(result["auth_source"], "vercel_cli_session")
        self.assertEqual(result["auth_source_details"]["username"], "operator")
        self.assertEqual(commands[0], ["vercel", "whoami"])
        self.assertEqual(commands[1][:3], ["vercel", "link", "--yes"])

    def test_explicit_token_remains_first_class_auth_for_link_and_deploy(self) -> None:
        module = load_module("vercel_delivery_common_token_auth", VERCEL_COMMON_PATH)
        commands: list[list[str]] = []

        def fake_runner(command, cwd, capture_output, text, check, env):
            commands.append(list(command))
            if command[:3] == ["vercel", "link", "--yes"]:
                return types.SimpleNamespace(returncode=0, stdout="linked", stderr="")
            if command[:2] == ["vercel", "deploy"]:
                return types.SimpleNamespace(returncode=0, stdout="Preview: https://demo-app.vercel.app\n", stderr="")
            raise AssertionError(f"unexpected command: {command}")

        link_result = module.link_vercel_project(
            workspace_path=self.workspace,
            project_name="demo-app-prod",
            team_scope="profit-corp",
            env={"VERCEL_TOKEN": "token"},
            which=lambda name: "vercel",
            runner=fake_runner,
        )
        self.assertTrue(link_result["ok"], msg=link_result)
        self.assertEqual(link_result["auth_source"], "vercel_token")
        self.assertEqual(link_result["auth_source_details"]["token_supplied"], True)

        deploy_result = module.deploy_to_vercel(
            workspace_path=self.workspace,
            project_name="demo-app-prod",
            team_scope="profit-corp",
            github_sync_ok=True,
            vercel_link_ok=True,
            env_contract_ok=True,
            env={"VERCEL_TOKEN": "token"},
            which=lambda name: "vercel",
            runner=fake_runner,
        )
        self.assertTrue(deploy_result["ok"], msg=deploy_result)
        self.assertEqual(deploy_result["auth_source"], "vercel_token")
        self.assertNotIn(["vercel", "whoami"], commands)

    def test_project_linkage_records_one_linked_project(self) -> None:
        module = load_module("vercel_delivery_common_link", VERCEL_COMMON_PATH)

        def fake_runner(command, cwd, capture_output, text, check, env):
            if command[:3] == ["vercel", "link", "--yes"]:
                return types.SimpleNamespace(returncode=0, stdout="linked", stderr="")
            raise AssertionError(f"unexpected command: {command}")

        result = module.link_vercel_project(
            workspace_path=self.workspace,
            project_name="demo-app-prod",
            team_scope="profit-corp",
            project_id="prj_123",
            env={"VERCEL_TOKEN": "token"},
            which=lambda name: "vercel",
            runner=fake_runner,
        )

        self.assertTrue(result["ok"], msg=result)
        self.assertTrue(result["linked"])
        self.assertEqual(result["project_id"], "prj_123")
        self.assertEqual(result["project_name"], "demo-app-prod")
        self.assertEqual(result["team_scope"], "profit-corp")
        self.assertIn("evidence_path", result)

    def test_link_and_deploy_classify_auth_scope_and_execution_failures(self) -> None:
        module = load_module("vercel_delivery_common_failure_taxonomy", VERCEL_COMMON_PATH)

        def invalid_auth_runner(command, cwd, capture_output, text, check, env):
            if command[:3] == ["vercel", "link", "--yes"]:
                return types.SimpleNamespace(
                    returncode=1,
                    stdout="",
                    stderr="Error: Invalid token provided. Please login again.",
                )
            raise AssertionError(f"unexpected command: {command}")

        invalid_auth = module.link_vercel_project(
            workspace_path=self.workspace,
            project_name="demo-app-prod",
            team_scope="profit-corp",
            env={"VERCEL_TOKEN": "token"},
            which=lambda name: "vercel",
            runner=invalid_auth_runner,
        )
        self.assertFalse(invalid_auth["ok"], msg=invalid_auth)
        self.assertEqual(invalid_auth["block_reason"], "invalid_vercel_auth")

        def inaccessible_scope_runner(command, cwd, capture_output, text, check, env):
            if command[:3] == ["vercel", "link", "--yes"]:
                return types.SimpleNamespace(
                    returncode=1,
                    stdout="",
                    stderr="Error: You do not have access to the requested scope profit-corp.",
                )
            raise AssertionError(f"unexpected command: {command}")

        inaccessible_scope = module.link_vercel_project(
            workspace_path=self.workspace,
            project_name="demo-app-prod",
            team_scope="profit-corp",
            env={"VERCEL_TOKEN": "token"},
            which=lambda name: "vercel",
            runner=inaccessible_scope_runner,
        )
        self.assertFalse(inaccessible_scope["ok"], msg=inaccessible_scope)
        self.assertEqual(inaccessible_scope["block_reason"], "inaccessible_vercel_scope")

        def deploy_failure_runner(command, cwd, capture_output, text, check, env):
            if command[:2] == ["vercel", "deploy"]:
                return types.SimpleNamespace(
                    returncode=1,
                    stdout="",
                    stderr="Build completed, but deployment failed with an unexpected runtime error.",
                )
            raise AssertionError(f"unexpected command: {command}")

        deploy_failure = module.deploy_to_vercel(
            workspace_path=self.workspace,
            project_name="demo-app-prod",
            team_scope="profit-corp",
            github_sync_ok=True,
            vercel_link_ok=True,
            env_contract_ok=True,
            env={"VERCEL_TOKEN": "token"},
            which=lambda name: "vercel",
            runner=deploy_failure_runner,
        )
        self.assertFalse(deploy_failure["ok"], msg=deploy_failure)
        self.assertEqual(deploy_failure["block_reason"], "vercel_deploy_failed")

    def test_deploy_url_extraction_prefers_preview_or_json_output(self) -> None:
        module = load_module("vercel_delivery_common_deploy_url", VERCEL_COMMON_PATH)
        self.assertEqual(
            module._extract_vercel_deploy_url("Preview: https://demo-preview.vercel.app\n", "", "demo-app-prod"),
            "https://demo-preview.vercel.app",
        )
        self.assertEqual(
            module._extract_vercel_deploy_url("", '{"deployment":{"url":"https://demo-json.vercel.app"}}', "demo-app-prod"),
            "https://demo-json.vercel.app",
        )

        module = load_module("vercel_delivery_common_env", VERCEL_COMMON_PATH)
        commands: list[tuple[list[str], str | None]] = []

        def fake_runner(*args, **kwargs):
            commands.append((list(args[0]), kwargs.get("input")))
            return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")

        result = module.apply_env_contract(
            workspace_path=self.workspace,
            project_name="demo-app-prod",
            team_scope="profit-corp",
            platform_managed_env={
                "NEXT_PUBLIC_SUPABASE_URL": "https://demo.supabase.co",
                "NEXT_PUBLIC_SUPABASE_ANON_KEY": "anon-key",
                "SUPABASE_SERVICE_ROLE_KEY": "secret",
                "NEXT_PUBLIC_PAYPAL_CLIENT_ID": "paypal-client-id",
                "PAYPAL_CLIENT_SECRET": "another-secret",
                "PAYPAL_ENVIRONMENT": "live",
            },
            identity_derived_env={
                "APP_KEY": "demo_app",
                "APP_NAME": "Demo App",
                "APP_URL": "https://demo.example.com",
                "PAYPAL_BRAND_NAME": "Demo App",
            },
            env={"VERCEL_TOKEN": "token"},
            which=lambda name: "vercel",
            runner=fake_runner,
        )

        self.assertTrue(result["ok"], msg=result)
        contract = json.loads(Path(result["env_contract_path"]).read_text(encoding="utf-8"))
        self.assertEqual(
            contract["platform_managed"],
            [
                "NEXT_PUBLIC_SUPABASE_URL",
                "NEXT_PUBLIC_SUPABASE_ANON_KEY",
                "SUPABASE_SERVICE_ROLE_KEY",
                "NEXT_PUBLIC_PAYPAL_CLIENT_ID",
                "PAYPAL_CLIENT_SECRET",
                "PAYPAL_ENVIRONMENT",
            ],
        )
        self.assertEqual(contract["identity_derived"]["APP_KEY"], "demo_app")
        self.assertEqual(contract["identity_derived"]["PAYPAL_BRAND_NAME"], "Demo App")
        self.assertEqual(contract["platform_values"]["NEXT_PUBLIC_SUPABASE_URL"], "https://demo.supabase.co")
        self.assertIn("\"platform_managed\"", json.dumps(contract, ensure_ascii=False))
        self.assertIn("\"platform_values\"", json.dumps(contract, ensure_ascii=False))
        self.assertEqual(commands[0][0][:4], ["vercel", "env", "add", "NEXT_PUBLIC_SUPABASE_URL"])
        self.assertEqual(commands[0][1], "https://demo.supabase.co\n")

    def test_apply_env_contract_replaces_existing_env_values(self) -> None:
        module = load_module("vercel_delivery_common_env_upsert", VERCEL_COMMON_PATH)
        commands: list[tuple[list[str], str | None]] = []

        def fake_runner(*args, **kwargs):
            command = list(args[0])
            commands.append((command, kwargs.get("input")))
            if command[:4] == ["vercel", "env", "add", "NEXT_PUBLIC_SUPABASE_URL"]:
                return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")
            if command[:4] == ["vercel", "env", "add", "NEXT_PUBLIC_SUPABASE_ANON_KEY"]:
                return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")
            if command[:4] == ["vercel", "env", "add", "SUPABASE_SERVICE_ROLE_KEY"]:
                return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")
            if command[:4] == ["vercel", "env", "add", "NEXT_PUBLIC_PAYPAL_CLIENT_ID"]:
                return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")
            if command[:4] == ["vercel", "env", "add", "PAYPAL_CLIENT_SECRET"]:
                return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")
            if command[:4] == ["vercel", "env", "add", "PAYPAL_ENVIRONMENT"]:
                return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")
            if command[:4] == ["vercel", "env", "add", "APP_KEY"] and kwargs.get("input") == "demo_app\n":
                if sum(1 for c, _ in commands if c[:4] == ["vercel", "env", "add", "APP_KEY"]) == 1:
                    return types.SimpleNamespace(returncode=1, stdout="", stderr="Environment Variable already exists")
                return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")
            if command[:4] == ["vercel", "env", "rm", "APP_KEY"]:
                return types.SimpleNamespace(returncode=0, stdout="removed", stderr="")
            if command[:4] == ["vercel", "env", "add", "APP_NAME"]:
                return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")
            if command[:4] == ["vercel", "env", "add", "APP_URL"]:
                return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")
            if command[:4] == ["vercel", "env", "add", "PAYPAL_BRAND_NAME"]:
                return types.SimpleNamespace(returncode=0, stdout="ok", stderr="")
            raise AssertionError(f"unexpected command: {command}")

        result = module.apply_env_contract(
            workspace_path=self.workspace,
            project_name="demo-app-prod",
            team_scope="profit-corp",
            platform_managed_env={
                "NEXT_PUBLIC_SUPABASE_URL": "https://demo.supabase.co",
                "NEXT_PUBLIC_SUPABASE_ANON_KEY": "anon-key",
                "SUPABASE_SERVICE_ROLE_KEY": "secret",
                "NEXT_PUBLIC_PAYPAL_CLIENT_ID": "paypal-client-id",
                "PAYPAL_CLIENT_SECRET": "another-secret",
                "PAYPAL_ENVIRONMENT": "live",
            },
            identity_derived_env={
                "APP_KEY": "demo_app",
                "APP_NAME": "Demo App",
                "APP_URL": "https://demo.example.com",
                "PAYPAL_BRAND_NAME": "Demo App",
            },
            env={"VERCEL_TOKEN": "token"},
            which=lambda name: "vercel",
            runner=fake_runner,
        )

        self.assertTrue(result["ok"], msg=result)
        self.assertIn((['vercel', 'env', 'rm', 'APP_KEY', 'production', '--scope', 'profit-corp', '--yes'], None), commands)

    def test_deploy_only_runs_after_github_sync_and_env_contract_checks(self) -> None:
        module = load_module("vercel_delivery_common_deploy", VERCEL_COMMON_PATH)

        missing_sync = module.deploy_to_vercel(
            workspace_path=self.workspace,
            project_name="demo-app-prod",
            team_scope="profit-corp",
            github_sync_ok=False,
            vercel_link_ok=True,
            env_contract_ok=True,
            env={"VERCEL_TOKEN": "token"},
            which=lambda name: "vercel",
        )
        self.assertFalse(missing_sync["ok"], msg=missing_sync)
        self.assertEqual(missing_sync["block_reason"], "github_sync_incomplete")

        missing_env_contract = module.deploy_to_vercel(
            workspace_path=self.workspace,
            project_name="demo-app-prod",
            team_scope="profit-corp",
            github_sync_ok=True,
            vercel_link_ok=True,
            env_contract_ok=False,
            env={"VERCEL_TOKEN": "token"},
            which=lambda name: "vercel",
        )
        self.assertFalse(missing_env_contract["ok"], msg=missing_env_contract)
        self.assertEqual(missing_env_contract["block_reason"], "missing_vercel_env_contract")


class Phase11VercelFlowTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.start_module = load_module("start_approved_project_delivery_phase11_vercel", START_SCRIPT_PATH)
        self.tmp = tempfile.TemporaryDirectory(prefix="phase11-vercel-flow-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.project_dir = self.root / "assets" / "shared" / "approved-projects" / "demo-app"
        self.project_dir.mkdir(parents=True)
        self.workspace = self.root / "generated-workspaces" / "demo-app"
        (self.workspace / ".hermes").mkdir(parents=True)
        self.authority_path = self.project_dir / "APPROVED_PROJECT.json"
        self.brief_path = self.project_dir / "PROJECT_BRIEF.md"
        self.brief_path.write_text("# Approved Project Brief\n", encoding="utf-8")

    def write_record(self, *, shipping: dict | None = None) -> None:
        record = {
            "approval": {
                "approval_id": "APR-11-01",
                "approved_at": "2026-04-27T10:00:00Z",
                "approver": "owner",
                "evidence": {
                    "decision_record": "assets/shared/CORP_CULTURE.md#phase11",
                    "summary": "Approved for shipping automation.",
                },
            },
            "project_identity": {
                "project_slug": "demo-app",
                "app_key": "demo_app",
                "app_name": "Demo App",
                "app_url": "https://demo.example.com",
            },
            "approved_scope": ["bootstrap repo and deploy to Vercel"],
            "target_user": "Operators",
            "mvp_framing": "Ship from approved authority record only.",
            "constraints": ["Use constrained CLI wrappers only"],
            "acceptance_gates": ["GitHub sync succeeded", "Vercel deploy reported"],
            "pipeline": {
                "stage": "github_sync",
                "status": "ready",
                "block_reason": None,
                "resume_from_stage": "vercel_linkage",
                "workspace_path": self.workspace.as_posix(),
                "delivery_run_id": "delivery-demo-001",
            },
            "artifacts": {
                "project_directory": self.project_dir.as_posix(),
                "authority_record_path": self.authority_path.as_posix(),
                "delivery_brief_path": self.brief_path.as_posix(),
                "events_path": (self.project_dir / "approved-delivery-events.jsonl").as_posix(),
                "status_path": (self.project_dir / "DELIVERY_PIPELINE_STATUS.md").as_posix(),
                "delivery_manifest_path": (self.workspace / ".hermes" / "delivery-run-manifest.json").as_posix(),
                "workspace_path": self.workspace.as_posix(),
            },
            "shipping": shipping or {
                "github": {
                    "repository_mode": "create",
                    "repository_name": "profit-corp/demo-app",
                    "repository_url": "https://github.com/profit-corp/demo-app.git",
                    "default_branch": "main",
                    "delivery_run_id": "delivery-demo-001",
                    "last_sync_status": "completed",
                }
            },
        }
        self.authority_path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    def read_record(self) -> dict:
        return json.loads(self.authority_path.read_text(encoding="utf-8"))

    def test_vercel_linkage_persists_auth_source_without_metadata_drift_for_both_auth_paths(self) -> None:
        for auth_source, auth_details in [
            ("vercel_cli_session", {"username": "operator"}),
            ("vercel_token", {"token_supplied": True}),
        ]:
            with self.subTest(auth_source=auth_source):
                self.write_record()
                env_evidence = self.workspace / ".hermes" / f"{auth_source}-vercel-env-contract.json"
                env_evidence.parent.mkdir(parents=True, exist_ok=True)
                env_evidence.write_text("{}\n", encoding="utf-8")

                with mock.patch.object(self.start_module, "link_vercel_project", return_value={
                    "ok": True,
                    "linked": True,
                    "project_id": "prj_123",
                    "project_name": "demo-app-prod",
                    "project_url": "https://vercel.com/profit-corp/demo-app-prod",
                    "team_scope": "profit-corp",
                    "auth_source": auth_source,
                    "auth_source_details": auth_details,
                    "env_contract_path": env_evidence.as_posix(),
                    "env_contract": {"evidence_path": env_evidence.as_posix()},
                    "required_env": {
                        "platform_managed": ["SUPABASE_SERVICE_ROLE_KEY"],
                        "identity_derived": {"APP_KEY": "demo_app"},
                    },
                }):
                    result = self.start_module.run_pipeline_from_stage(
                        self.authority_path,
                        self.read_record(),
                        start_stage="vercel_linkage",
                        workspace_root=self.root / "generated-workspaces",
                    )

                self.assertTrue(result["ok"], msg=result)
                updated = self.read_record()
                vercel = updated["shipping"]["vercel"]
                self.assertEqual(vercel["project_name"], "demo-app-prod")
                self.assertEqual(vercel["project_url"], "https://vercel.com/profit-corp/demo-app-prod")
                self.assertEqual(vercel["team_scope"], "profit-corp")
                self.assertEqual(vercel["auth_source"], auth_source)
                self.assertEqual(vercel["auth_source_details"], auth_details)
                self.assertEqual(updated["pipeline"]["resume_from_stage"], "vercel_deploy")

    def test_vercel_deploy_failure_preserves_specific_block_reason_end_to_end(self) -> None:
        self.write_record(
            shipping={
                "github": {
                    "repository_mode": "create",
                    "repository_name": "profit-corp/demo-app",
                    "repository_url": "https://github.com/profit-corp/demo-app.git",
                    "default_branch": "main",
                    "delivery_run_id": "delivery-demo-001",
                    "last_sync_status": "completed",
                },
                "vercel": {
                    "project_id": "prj_123",
                    "project_name": "demo-app-prod",
                    "project_url": "https://vercel.com/profit-corp/demo-app-prod",
                    "team_scope": "profit-corp",
                    "env_contract_path": (self.workspace / ".hermes" / "vercel-env-contract.json").as_posix(),
                    "env_contract": {
                        "platform_managed": ["SUPABASE_SERVICE_ROLE_KEY"],
                        "identity_derived": {"APP_KEY": "demo_app"},
                        "evidence_path": (self.workspace / ".hermes" / "vercel-env-contract.json").as_posix(),
                    },
                },
            }
        )

        with mock.patch.object(self.start_module, "run_vercel_deploy", return_value={
            "ok": False,
            "block_reason": "vercel_deploy_failed",
            "error": "deployment failed after build",
            "deploy_url": "",
            "deploy_status": "failed",
            "deploy_evidence_path": (self.workspace / ".hermes" / "vercel-deploy.json").as_posix(),
        }):
            result = self.start_module.run_pipeline_from_stage(
                self.authority_path,
                self.read_record(),
                start_stage="vercel_deploy",
                workspace_root=self.root / "generated-workspaces",
            )

        self.assertFalse(result["ok"], msg=result)
        self.assertEqual(result["block_reason"], "vercel_deploy_failed")
        updated = self.read_record()
        self.assertEqual(updated["pipeline"]["stage"], "vercel_deploy")
        self.assertEqual(updated["pipeline"]["status"], "blocked")
        self.assertEqual(updated["pipeline"]["block_reason"], "vercel_deploy_failed")

    def test_missing_tool_auth_env_and_linkage_map_to_distinct_blocked_states(self) -> None:
        self.write_record()
        cases = [
            ("missing_gh_cli", "github_repository"),
            ("missing_github_auth", "github_repository"),
            ("missing_vercel_auth", "vercel_linkage"),
            ("missing_vercel_project_linkage", "vercel_linkage"),
            ("missing_vercel_env_contract", "vercel_linkage"),
        ]
        for reason, stage in cases:
            with self.subTest(reason=reason):
                result = self.start_module.block_pipeline(
                    self.authority_path,
                    self.read_record(),
                    stage=stage,
                    block_reason=reason,
                    evidence_path=(self.workspace / ".hermes" / f"{reason}.md").as_posix(),
                    message=f"blocked on {reason}",
                    workspace_path=self.workspace.as_posix(),
                    delivery_run_id="delivery-demo-001",
                )
                self.assertFalse(result["ok"], msg=result)
                self.assertEqual(result["block_reason"], reason)
                updated = self.read_record()
                self.assertEqual(updated["pipeline"]["block_reason"], reason)
                self.assertEqual(updated["pipeline"]["resume_from_stage"], stage)

    def test_deploy_outcome_updates_authority_record_and_workspace_handoff_references(self) -> None:
        self.write_record(
            shipping={
                "github": {
                    "repository_mode": "create",
                    "repository_name": "profit-corp/demo-app",
                    "repository_url": "https://github.com/profit-corp/demo-app.git",
                    "default_branch": "main",
                    "delivery_run_id": "delivery-demo-001",
                    "last_sync_status": "completed",
                },
                "vercel": {
                    "project_id": "prj_123",
                    "project_name": "demo-app-prod",
                    "project_url": "https://vercel.com/profit-corp/demo-app-prod",
                    "env_contract_path": (self.workspace / ".hermes" / "vercel-env-contract.json").as_posix(),
                    "env_contract": {
                        "platform_managed": ["SUPABASE_SERVICE_ROLE_KEY", "PAYPAL_CLIENT_SECRET"],
                        "identity_derived": {
                            "APP_KEY": "demo_app",
                            "APP_NAME": "Demo App",
                            "APP_URL": "https://demo.example.com",
                            "PAYPAL_BRAND_NAME": "Demo App",
                        },
                        "evidence_path": (self.workspace / ".hermes" / "vercel-env-contract.json").as_posix(),
                    },
                    "deploy_status": "pending",
                },
            }
        )
        final_handoff = self.workspace / ".hermes" / "FINAL_DELIVERY.md"
        final_handoff.write_text("# Final delivery\n", encoding="utf-8")

        with mock.patch.object(self.start_module, "run_vercel_deploy", return_value={
            "ok": True,
            "deploy_url": "https://demo-app.vercel.app",
            "deploy_status": "ready",
            "deploy_evidence_path": (self.workspace / ".hermes" / "vercel-deploy.json").as_posix(),
            "final_handoff_path": final_handoff.as_posix(),
        }):
            result = self.start_module.run_pipeline_from_stage(
                self.authority_path,
                self.read_record(),
                start_stage="vercel_deploy",
                workspace_root=self.root / "generated-workspaces",
            )

        self.assertTrue(result["ok"], msg=result)
        updated = self.read_record()
        self.assertEqual(updated["shipping"]["vercel"]["deployment_url"], "https://demo-app.vercel.app")
        self.assertEqual(updated["shipping"]["vercel"]["deployment_status"], "ready")
        self.assertEqual(updated["shipping"]["vercel"]["deploy_url"], "https://demo-app.vercel.app")
        self.assertEqual(updated["shipping"]["vercel"]["deploy_status"], "ready")
        self.assertEqual(updated["pipeline"]["final_handoff_path"], final_handoff.as_posix())
        self.assertEqual(updated["artifacts"]["final_handoff_path"], final_handoff.as_posix())


if __name__ == "__main__":
    unittest.main()
