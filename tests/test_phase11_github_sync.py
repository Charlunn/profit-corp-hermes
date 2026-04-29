import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
GITHUB_HELPER_PATH = ROOT_DIR / "scripts" / "github_delivery_common.py"


class CompletedProcessStub:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr


def load_module(module_name: str, script_path: Path):
    if not script_path.exists():
        raise AssertionError(f"expected script to exist: {script_path}")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Phase11GithubSyncTests(unittest.TestCase):
    maxDiff = None

    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory(prefix="phase11-github-sync-")
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.workspace = self.root / "generated-workspaces" / "demo-app"
        (self.workspace / ".hermes").mkdir(parents=True)
        (self.workspace / "README.md").write_text("# Demo App\n", encoding="utf-8")
        self.helper_module = load_module("github_delivery_common_phase11", GITHUB_HELPER_PATH)

    def test_prepare_github_repository_supports_create_and_attach_modes(self) -> None:
        commands: list[list[str]] = []

        def runner(cmd: list[str], **kwargs):
            commands.append(list(cmd))
            if cmd[:3] == ["git", "init", "-b"]:
                return CompletedProcessStub()
            if cmd[:3] == ["gh", "repo", "create"]:
                return CompletedProcessStub()
            if cmd[:3] == ["gh", "repo", "view"]:
                target = cmd[3]
                return CompletedProcessStub(
                    stdout=json.dumps(
                        {
                            "nameWithOwner": target,
                            "url": f"https://github.com/{target}",
                            "defaultBranchRef": {"name": "release" if target.endswith("existing-demo-app") else "trunk"},
                        }
                    )
                )
            raise AssertionError(f"unexpected command: {cmd}")

        create_result = self.helper_module.prepare_github_repository(
            workspace_path=self.workspace,
            repository_mode="create",
            repository_owner="profit-corp",
            repository_name="demo-app",
            runner=runner,
            which=lambda _: "/usr/bin/gh",
            env={"GH_TOKEN": "token"},
        )
        self.assertTrue(create_result["ok"], msg=create_result)
        self.assertEqual(create_result["repository_mode"], "create")
        self.assertEqual(create_result["repository_owner"], "profit-corp")
        self.assertEqual(create_result["repository_name"], "profit-corp/demo-app")
        self.assertEqual(create_result["default_branch"], "trunk")
        self.assertEqual(create_result["remote_name"], "origin")
        self.assertEqual(create_result["auth_source"], "env_token")
        self.assertEqual(create_result["auth_source_details"]["source"], "GH_TOKEN")
        self.assertEqual(create_result["block_reason"], "")

        attach_result = self.helper_module.prepare_github_repository(
            workspace_path=self.workspace,
            repository_mode="attach",
            repository_owner="profit-corp",
            repository_name="existing-demo-app",
            repository_url="https://github.com/profit-corp/existing-demo-app.git",
            runner=runner,
            which=lambda _: "/usr/bin/gh",
            env={"GITHUB_TOKEN": "token"},
        )
        self.assertTrue(attach_result["ok"], msg=attach_result)
        self.assertEqual(attach_result["repository_mode"], "attach")
        self.assertEqual(attach_result["repository_name"], "profit-corp/existing-demo-app")
        self.assertEqual(attach_result["repository_url"], "https://github.com/profit-corp/existing-demo-app.git")
        self.assertEqual(attach_result["default_branch"], "release")
        self.assertEqual(attach_result["auth_source"], "env_token")
        self.assertEqual(attach_result["auth_source_details"]["source"], "GITHUB_TOKEN")

        self.assertEqual(commands[0][:4], ["git", "init", "-b", "main"])
        self.assertEqual(commands[1][:3], ["gh", "repo", "create"])
        self.assertEqual(commands[2][:3], ["gh", "repo", "view"])
        self.assertEqual(commands[3][:3], ["gh", "repo", "view"])

    def test_missing_gh_and_missing_github_credentials_block_with_distinct_reasons(self) -> None:
        missing_cli = self.helper_module.prepare_github_repository(
            workspace_path=self.workspace,
            repository_mode="attach",
            repository_owner="profit-corp",
            repository_name="demo-app",
            which=lambda _: None,
            env={"GH_TOKEN": "token"},
        )
        self.assertFalse(missing_cli["ok"], msg=missing_cli)
        self.assertEqual(missing_cli["block_reason"], "missing_gh_cli")
        self.assertTrue(missing_cli["evidence_path"].endswith("github-repository-prepare.json"))

        original_env = dict(self.helper_module.os.environ)
        self.addCleanup(lambda: self.helper_module.os.environ.clear() or self.helper_module.os.environ.update(original_env))
        self.helper_module.os.environ.clear()
        missing_auth = self.helper_module.prepare_github_repository(
            workspace_path=self.workspace,
            repository_mode="attach",
            repository_owner="profit-corp",
            repository_name="demo-app",
            which=lambda _: "/usr/bin/gh",
            env={},
        )
        self.assertFalse(missing_auth["ok"], msg=missing_auth)
        self.assertEqual(missing_auth["block_reason"], "missing_github_auth")
        self.assertTrue(missing_auth["evidence_path"].endswith("github-repository-prepare.json"))

    def test_shell_environment_token_counts_as_github_auth(self) -> None:
        original_env = dict(self.helper_module.os.environ)
        self.addCleanup(lambda: self.helper_module.os.environ.clear() or self.helper_module.os.environ.update(original_env))
        self.helper_module.os.environ.clear()
        self.helper_module.os.environ["GH_TOKEN"] = "token-from-shell"

        def runner(cmd: list[str], **kwargs):
            if cmd[:3] == ["gh", "repo", "view"]:
                return CompletedProcessStub(
                    stdout=json.dumps(
                        {
                            "nameWithOwner": "profit-corp/demo-app",
                            "url": "https://github.com/profit-corp/demo-app",
                            "defaultBranchRef": {"name": "main"},
                        }
                    )
                )
            raise AssertionError(f"unexpected command: {cmd}")

        result = self.helper_module.prepare_github_repository(
            workspace_path=self.workspace,
            repository_mode="attach",
            repository_owner="profit-corp",
            repository_name="demo-app",
            runner=runner,
            which=lambda _: "/usr/bin/gh",
            env=None,
        )
        self.assertTrue(result["ok"], msg=result)
        self.assertEqual(result["auth_source"], "env_token")
        self.assertEqual(result["auth_source_details"]["source"], "GH_TOKEN")

    def test_authenticated_gh_cli_session_counts_as_github_auth_without_env_token(self) -> None:
        commands: list[list[str]] = []
        original_env = dict(self.helper_module.os.environ)
        self.addCleanup(lambda: self.helper_module.os.environ.clear() or self.helper_module.os.environ.update(original_env))
        self.helper_module.os.environ.clear()

        def runner(cmd: list[str], **kwargs):
            commands.append(list(cmd))
            if cmd[:3] == ["gh", "auth", "status"]:
                return CompletedProcessStub(returncode=0, stdout="github.com\n  Logged in to github.com as profit-corp\n")
            if cmd[:3] == ["gh", "repo", "view"]:
                return CompletedProcessStub(
                    stdout=json.dumps(
                        {
                            "nameWithOwner": "profit-corp/demo-app",
                            "url": "https://github.com/profit-corp/demo-app",
                            "defaultBranchRef": {"name": "main"},
                        }
                    )
                )
            raise AssertionError(f"unexpected command: {cmd}")

        result = self.helper_module.prepare_github_repository(
            workspace_path=self.workspace,
            repository_mode="attach",
            repository_owner="profit-corp",
            repository_name="demo-app",
            runner=runner,
            which=lambda _: "/usr/bin/gh",
            env={},
        )
        self.assertTrue(result["ok"], msg=result)
        self.assertEqual(result["auth_source"], "gh_cli")
        self.assertEqual(result["auth_source_details"]["command"], "gh auth status")
        self.assertEqual(commands[0][:3], ["gh", "auth", "status"])

    def test_sync_workspace_to_github_filters_generated_snapshot_paths_and_records_evidence(self) -> None:
        (self.workspace / "src").mkdir(parents=True)
        (self.workspace / "src" / "main.ts").write_text("export const demo = true;\n", encoding="utf-8")
        (self.workspace / "dist").mkdir(parents=True)
        (self.workspace / "dist" / "bundle.js").write_text("compiled\n", encoding="utf-8")
        (self.workspace / "node_modules" / "pkg").mkdir(parents=True)
        (self.workspace / "node_modules" / "pkg" / "index.js").write_text("module.exports = {}\n", encoding="utf-8")
        commands: list[list[str]] = []

        def runner(cmd: list[str], **kwargs):
            commands.append(list(cmd))
            if cmd[:3] == ["git", "rev-parse", "--is-inside-work-tree"]:
                return CompletedProcessStub(stdout="true\n")
            if cmd[:4] == ["git", "remote", "get-url", "origin"]:
                return CompletedProcessStub(stdout="https://github.com/profit-corp/demo-app.git\n")
            if cmd[:4] == ["git", "fetch", "origin", "main"]:
                return CompletedProcessStub()
            if cmd[:3] == ["git", "checkout", "-B"]:
                return CompletedProcessStub()
            if cmd[:2] == ["git", "add"]:
                return CompletedProcessStub()
            if cmd[:4] == ["git", "rev-parse", "--verify", "HEAD"]:
                return CompletedProcessStub(returncode=1, stderr="no commits yet")
            if cmd[:3] == ["git", "status", "--short"]:
                return CompletedProcessStub(stdout="A  src/main.ts\n")
            if cmd[:3] == ["git", "commit", "-m"]:
                return CompletedProcessStub()
            if cmd[:3] == ["git", "push", "-u"]:
                return CompletedProcessStub()
            if cmd[:4] == ["git", "rev-parse", "--short", "HEAD"]:
                return CompletedProcessStub(stdout="fedcba9\n")
            raise AssertionError(f"unexpected command: {cmd}")

        result = self.helper_module.sync_workspace_to_github(
            workspace_path=self.workspace,
            repository_url="https://github.com/profit-corp/demo-app.git",
            default_branch="main",
            remote_name="origin",
            runner=runner,
        )

        self.assertTrue(result["ok"], msg=result)
        add_commands = [command for command in commands if command[:2] == ["git", "add"]]
        self.assertEqual(len(add_commands), 1)
        self.assertNotEqual(add_commands[0][:3], ["git", "add", "-A"])
        self.assertEqual(add_commands[0][:3], ["git", "add", "--"])
        self.assertIn("README.md", add_commands[0])
        self.assertIn("src/main.ts", add_commands[0])
        self.assertNotIn("dist/bundle.js", add_commands[0])
        self.assertNotIn("node_modules/pkg/index.js", add_commands[0])
        self.assertEqual(result["snapshot_mode"], "explicit_paths")
        self.assertIn("dist", result["snapshot_excluded_categories"])
        self.assertIn("node_modules", result["snapshot_excluded_categories"])

        evidence = json.loads(Path(result["evidence_path"]).read_text(encoding="utf-8"))
        self.assertEqual(evidence["snapshot_mode"], "explicit_paths")
        self.assertEqual(evidence["snapshot_policy"], "exclude_generated_directories")
        self.assertIn("src/main.ts", evidence["snapshot_included_paths"])
        self.assertNotIn("dist/bundle.js", evidence["snapshot_included_paths"])

    def test_sync_workspace_to_github_retries_push_with_ssh_transport_and_restores_canonical_remote(self) -> None:
        commands: list[list[str]] = []

        def runner(cmd: list[str], **kwargs):
            commands.append(list(cmd))
            if cmd[:3] == ["git", "rev-parse", "--is-inside-work-tree"]:
                return CompletedProcessStub(stdout="true\n")
            if cmd[:4] == ["git", "remote", "get-url", "origin"]:
                return CompletedProcessStub(stdout="https://github.com/profit-corp/demo-app.git\n")
            if cmd[:4] == ["git", "fetch", "origin", "main"]:
                return CompletedProcessStub()
            if cmd[:3] == ["git", "checkout", "-B"]:
                return CompletedProcessStub()
            if cmd[:2] == ["git", "add"]:
                return CompletedProcessStub()
            if cmd[:4] == ["git", "rev-parse", "--verify", "HEAD"]:
                return CompletedProcessStub(returncode=1, stderr="no commits yet")
            if cmd[:3] == ["git", "status", "--short"]:
                return CompletedProcessStub(stdout=" M README.md\n")
            if cmd[:3] == ["git", "commit", "-m"]:
                return CompletedProcessStub()
            if cmd[:5] == ["git", "remote", "set-url", "origin", "git@github.com:profit-corp/demo-app.git"]:
                return CompletedProcessStub()
            if cmd[:5] == ["git", "remote", "set-url", "origin", "https://github.com/profit-corp/demo-app.git"]:
                return CompletedProcessStub()
            if cmd[:3] == ["git", "push", "-u"]:
                remote_url = next((entry[4] for entry in commands if entry[:3] == ["git", "remote", "set-url"]), "")
                if remote_url == "git@github.com:profit-corp/demo-app.git":
                    return CompletedProcessStub()
                return CompletedProcessStub(returncode=1, stderr="https transport unavailable")
            if cmd[:4] == ["git", "rev-parse", "--short", "HEAD"]:
                return CompletedProcessStub(stdout="abc9999\n")
            raise AssertionError(f"unexpected command: {cmd}")

        result = self.helper_module.sync_workspace_to_github(
            workspace_path=self.workspace,
            repository_url="https://github.com/profit-corp/demo-app.git",
            default_branch="main",
            remote_name="origin",
            runner=runner,
        )

        self.assertTrue(result["ok"], msg=result)
        self.assertEqual(result["push_transport"], "ssh")
        self.assertEqual(result["push_remote_url"], "git@github.com:profit-corp/demo-app.git")
        self.assertEqual([attempt["transport"] for attempt in result["push_attempts"]], ["https", "ssh"])
        self.assertEqual(result["push_attempts"][0]["status"], "failed")
        self.assertEqual(result["push_attempts"][1]["status"], "ok")
        self.assertIn(["git", "remote", "set-url", "origin", "git@github.com:profit-corp/demo-app.git"], commands)
        self.assertIn(["git", "remote", "set-url", "origin", "https://github.com/profit-corp/demo-app.git"], commands)

    def test_sync_workspace_to_github_reports_failed_step_for_commit_and_push_boundaries(self) -> None:
        def commit_runner(cmd: list[str], **kwargs):
            if cmd[:3] == ["git", "rev-parse", "--is-inside-work-tree"]:
                return CompletedProcessStub(stdout="true\n")
            if cmd[:4] == ["git", "remote", "get-url", "origin"]:
                return CompletedProcessStub(stdout="https://github.com/profit-corp/demo-app.git\n")
            if cmd[:4] == ["git", "fetch", "origin", "main"]:
                return CompletedProcessStub()
            if cmd[:3] == ["git", "checkout", "-B"]:
                return CompletedProcessStub()
            if cmd[:2] == ["git", "add"]:
                return CompletedProcessStub()
            if cmd[:4] == ["git", "rev-parse", "--verify", "HEAD"]:
                return CompletedProcessStub(returncode=1, stderr="no commits yet")
            if cmd[:3] == ["git", "status", "--short"]:
                return CompletedProcessStub(stdout=" M README.md\n")
            if cmd[:3] == ["git", "commit", "-m"]:
                return CompletedProcessStub(returncode=1, stderr="commit blocked")
            raise AssertionError(f"unexpected command: {cmd}")

        commit_result = self.helper_module.sync_workspace_to_github(
            workspace_path=self.workspace,
            repository_url="https://github.com/profit-corp/demo-app.git",
            default_branch="main",
            remote_name="origin",
            runner=commit_runner,
        )
        self.assertFalse(commit_result["ok"], msg=commit_result)
        self.assertEqual(commit_result["failed_step"], "commit")
        self.assertEqual(commit_result["attempted_command"], "git commit -m")

        def push_runner(cmd: list[str], **kwargs):
            if cmd[:3] == ["git", "rev-parse", "--is-inside-work-tree"]:
                return CompletedProcessStub(stdout="true\n")
            if cmd[:4] == ["git", "remote", "get-url", "origin"]:
                return CompletedProcessStub(stdout="https://github.com/profit-corp/demo-app.git\n")
            if cmd[:4] == ["git", "fetch", "origin", "main"]:
                return CompletedProcessStub()
            if cmd[:3] == ["git", "checkout", "-B"]:
                return CompletedProcessStub()
            if cmd[:2] == ["git", "add"]:
                return CompletedProcessStub()
            if cmd[:4] == ["git", "rev-parse", "--verify", "HEAD"]:
                return CompletedProcessStub(stdout="1234567\n")
            if cmd[:3] == ["git", "status", "--short"]:
                return CompletedProcessStub(stdout="")
            if cmd[:3] == ["git", "push", "-u"]:
                return CompletedProcessStub(returncode=1, stderr="push rejected")
            if cmd[:3] == ["git", "remote", "set-url"]:
                return CompletedProcessStub()
            raise AssertionError(f"unexpected command: {cmd}")

        push_result = self.helper_module.sync_workspace_to_github(
            workspace_path=self.workspace,
            repository_url="https://github.com/profit-corp/demo-app.git",
            default_branch="main",
            remote_name="origin",
            runner=push_runner,
        )
        self.assertFalse(push_result["ok"], msg=push_result)
        self.assertEqual(push_result["failed_step"], "push")
        self.assertEqual(push_result["attempted_command"], "git push")
        self.assertEqual([attempt["transport"] for attempt in push_result["push_attempts"]], ["https", "ssh"])

    def test_sync_workspace_to_github_persists_detected_default_branch_instead_of_assuming_main(self) -> None:
        commands: list[list[str]] = []

        def runner(cmd: list[str], **kwargs):
            commands.append(list(cmd))
            if cmd[:3] == ["git", "rev-parse", "--is-inside-work-tree"]:
                return CompletedProcessStub(stdout="true\n")
            if cmd[:4] == ["git", "remote", "get-url", "origin"]:
                return CompletedProcessStub(returncode=2, stderr="missing remote")
            if cmd[:3] == ["git", "remote", "add"]:
                return CompletedProcessStub()
            if cmd[:4] == ["git", "fetch", "origin", "release"]:
                return CompletedProcessStub()
            if cmd[:3] == ["git", "checkout", "-B"]:
                return CompletedProcessStub()
            if cmd[:2] == ["git", "add"]:
                return CompletedProcessStub()
            if cmd[:4] == ["git", "rev-parse", "--verify", "HEAD"]:
                return CompletedProcessStub(returncode=1, stderr="no commits yet")
            if cmd[:3] == ["git", "status", "--short"]:
                return CompletedProcessStub(stdout=" M README.md\n")
            if cmd[:3] == ["git", "commit", "-m"]:
                return CompletedProcessStub()
            if cmd[:3] == ["git", "push", "-u"]:
                return CompletedProcessStub()
            if cmd[:4] == ["git", "rev-parse", "--short", "HEAD"]:
                return CompletedProcessStub(stdout="abc1234\n")
            raise AssertionError(f"unexpected command: {cmd}")

        result = self.helper_module.sync_workspace_to_github(
            workspace_path=self.workspace,
            repository_url="https://github.com/profit-corp/demo-app.git",
            default_branch="release",
            remote_name="origin",
            runner=runner,
        )
        self.assertTrue(result["ok"], msg=result)
        self.assertEqual(result["default_branch"], "release")
        self.assertEqual(result["repository_url"], "https://github.com/profit-corp/demo-app.git")
        self.assertEqual(result["synced_commit"], "abc1234")
        self.assertTrue(result["evidence_path"].endswith("github-sync.json"))
        self.assertIn(["git", "checkout", "-B", "release"], commands)
        self.assertIn(["git", "push", "-u", "origin", "release"], commands)

    def test_full_project_bootstrap_sync_records_remote_url_commit_branch_and_evidence(self) -> None:
        commands: list[list[str]] = []

        def runner(cmd: list[str], **kwargs):
            commands.append(list(cmd))
            if cmd[:3] == ["git", "rev-parse", "--is-inside-work-tree"]:
                return CompletedProcessStub(stdout="true\n")
            if cmd[:4] == ["git", "remote", "get-url", "origin"]:
                return CompletedProcessStub(stdout="https://github.com/profit-corp/demo-app.git\n")
            if cmd[:4] == ["git", "fetch", "origin", "trunk"]:
                return CompletedProcessStub()
            if cmd[:3] == ["git", "checkout", "-B"]:
                return CompletedProcessStub()
            if cmd[:2] == ["git", "add"]:
                return CompletedProcessStub()
            if cmd[:4] == ["git", "rev-parse", "--verify", "HEAD"]:
                return CompletedProcessStub(returncode=1, stderr="no commits yet")
            if cmd[:3] == ["git", "status", "--short"]:
                return CompletedProcessStub(stdout="")
            if cmd[:3] == ["git", "commit", "-m"]:
                return CompletedProcessStub()
            if cmd[:3] == ["git", "push", "-u"]:
                return CompletedProcessStub()
            if cmd[:4] == ["git", "rev-parse", "--short", "HEAD"]:
                return CompletedProcessStub(stdout="def5678\n")
            raise AssertionError(f"unexpected command: {cmd}")

        result = self.helper_module.sync_workspace_to_github(
            workspace_path=self.workspace,
            repository_url="https://github.com/profit-corp/demo-app.git",
            default_branch="trunk",
            remote_name="origin",
            runner=runner,
        )
        self.assertTrue(result["ok"], msg=result)
        self.assertEqual(result["repository_url"], "https://github.com/profit-corp/demo-app.git")
        self.assertEqual(result["default_branch"], "trunk")
        self.assertEqual(result["synced_commit"], "def5678")

        evidence_path = Path(result["evidence_path"])
        self.assertTrue(evidence_path.exists(), msg=result)
        evidence = json.loads(evidence_path.read_text(encoding="utf-8"))
        self.assertEqual(evidence["repository_url"], "https://github.com/profit-corp/demo-app.git")
        self.assertEqual(evidence["default_branch"], "trunk")
        self.assertEqual(evidence["synced_commit"], "def5678")
        self.assertEqual(evidence["remote_name"], "origin")


if __name__ == "__main__":
    unittest.main()
