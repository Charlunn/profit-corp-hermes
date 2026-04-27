import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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
            if cmd[:3] == ["gh", "repo", "create"]:
                return CompletedProcessStub(
                    stdout=json.dumps(
                        {
                            "nameWithOwner": "profit-corp/demo-app",
                            "url": "https://github.com/profit-corp/demo-app",
                            "defaultBranchRef": {"name": "trunk"},
                        }
                    )
                )
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

        self.assertEqual(commands[0][:3], ["gh", "repo", "create"])
        self.assertEqual(commands[1][:3], ["gh", "repo", "view"])
        self.assertEqual(commands[2][:3], ["gh", "repo", "view"])

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
            if cmd[:3] == ["git", "add", "-A"]:
                return CompletedProcessStub()
            if cmd[:3] == ["git", "status", "--short"]:
                return CompletedProcessStub(stdout=" M README.md\n")
            if cmd[:3] == ["git", "commit", "-m"]:
                return CompletedProcessStub()
            if cmd[:3] == ["git", "push", "-u"]:
                return CompletedProcessStub()
            if cmd[:4] == ["git", "rev-parse", "HEAD", "--short"]:
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
            if cmd[:3] == ["git", "add", "-A"]:
                return CompletedProcessStub()
            if cmd[:3] == ["git", "status", "--short"]:
                return CompletedProcessStub(stdout="")
            if cmd[:3] == ["git", "push", "-u"]:
                return CompletedProcessStub()
            if cmd[:4] == ["git", "rev-parse", "HEAD", "--short"]:
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
