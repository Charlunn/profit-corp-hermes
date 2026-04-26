import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
SCRIPT_PATH = ROOT_DIR / "scripts" / "check_template_conformance.py"
INSTANTIATE_SCRIPT = ROOT_DIR / "scripts" / "instantiate_template_project.py"
REGISTRY_PATH = ROOT_DIR / "assets" / "shared" / "templates" / "standalone-saas-template.json"
TEMPLATE_SOURCE = Path("C:/Users/42236/Desktop/standalone-saas-template")
EXPECTED_SECTION_ORDER = [
    "## Status",
    "## Blocking Violations",
    "## Verified Paths",
    "## Fingerprint Checks",
]


class CheckTemplateConformanceTests(unittest.TestCase):
    maxDiff = None

    def addCleanupPath(self, path: Path) -> None:
        self.addCleanup(lambda: shutil.rmtree(path, ignore_errors=True))

    def run_conformance(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT_PATH), *args],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )

    def run_instantiate(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(INSTANTIATE_SCRIPT), *args],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )

    def assert_section_order(self, output: str) -> None:
        positions: list[int] = []
        for section in EXPECTED_SECTION_ORDER:
            self.assertIn(section, output)
            positions.append(output.index(section))
        self.assertEqual(positions, sorted(positions), "section order drifted")

    def extract_section(self, output: str, heading: str) -> str:
        marker = f"\n{heading}\n"
        self.assertIn(marker, output, msg=f"missing section marker for {heading}")
        tail = output.split(marker, 1)[1]
        next_heading = tail.find("\n## ")
        if next_heading == -1:
            return tail.strip()
        return tail[:next_heading].strip()

    def create_workspace_fixture(self) -> tuple[Path, Path, Path]:
        assets_root = Path(tempfile.mkdtemp(prefix="conformance-assets-"))
        self.addCleanupPath(assets_root)
        workspace_root = assets_root / "assets" / "workspaces" / "projects"
        workspace_root.mkdir(parents=True, exist_ok=True)

        registry_path = assets_root / "standalone-saas-template.json"
        registry = json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))
        registry["source"]["repo_path"] = TEMPLATE_SOURCE.as_posix()
        registry_path.write_text(json.dumps(registry, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

        result = self.run_instantiate(
            "--registry-path",
            str(registry_path),
            "--workspace-root",
            str(workspace_root),
            "--workspace-name",
            "lead-capture",
            "--app-key",
            "lead_capture",
            "--app-name",
            "Lead Capture",
            "--app-url",
            "https://lead.example.com",
        )
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        workspace = workspace_root / "lead-capture"
        self.assertTrue(workspace.exists(), "workspace was not created")
        return assets_root, registry_path, workspace

    def base_args(self, registry_path: Path, workspace: Path) -> list[str]:
        return [
            "--workspace-path",
            str(workspace),
            "--registry-path",
            str(registry_path),
            "--dry-run",
        ]

    def test_cli_help_exposes_required_flags(self) -> None:
        result = self.run_conformance("--help")
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        help_text = result.stdout
        for flag in (
            "--workspace-path",
            "--contract-path",
            "--registry-path",
            "--report-path",
            "--dry-run",
        ):
            self.assertIn(flag, help_text)

    def test_healthy_workspace_passes_conformance_and_lists_verified_paths(self) -> None:
        _, registry_path, workspace = self.create_workspace_fixture()
        result = self.run_conformance(*self.base_args(registry_path, workspace))
        self.assertEqual(result.returncode, 0, msg=result.stderr)
        output = result.stdout
        self.assertIn("# Template Conformance Report", output)
        self.assertIn("PASS", self.extract_section(output, "## Status"))
        self.assertIn("src/app/demo/page.tsx", self.extract_section(output, "## Verified Paths"))
        self.assertIn(
            "supabase/migrations/20260423112500_create_shared_public_tables.sql",
            self.extract_section(output, "## Verified Paths"),
        )
        fingerprint_section = self.extract_section(output, "## Fingerprint Checks")
        self.assertIn("src/app/api/auth/session/route.ts", fingerprint_section)
        self.assertIn("src/app/api/paypal/capture/route.ts", fingerprint_section)
        self.assertEqual(self.extract_section(output, "## Blocking Violations"), "None.")
        self.assert_section_order(output)

    def test_missing_app_key_fails_with_blocking_violation(self) -> None:
        _, registry_path, workspace = self.create_workspace_fixture()
        env_path = workspace / ".env"
        env_text = env_path.read_text(encoding="utf-8").replace("APP_KEY=lead_capture", "APP_KEY=")
        env_path.write_text(env_text, encoding="utf-8")

        result = self.run_conformance(*self.base_args(registry_path, workspace))
        self.assertEqual(result.returncode, 1)
        violations = self.extract_section(result.stdout, "## Blocking Violations")
        self.assertIn("APP_KEY", violations)
        self.assertIn("missing or blank", violations)

    def test_missing_protected_path_fails_with_blocking_violation(self) -> None:
        _, registry_path, workspace = self.create_workspace_fixture()
        protected_path = workspace / "src" / "app" / "api" / "paypal" / "capture" / "route.ts"
        protected_path.unlink()

        result = self.run_conformance(*self.base_args(registry_path, workspace))
        self.assertEqual(result.returncode, 1)
        violations = self.extract_section(result.stdout, "## Blocking Violations")
        self.assertIn("src/app/api/paypal/capture/route.ts", violations)
        self.assertIn("missing protected path", violations)

    def test_fingerprint_drifted_protected_path_fails_with_blocking_violation(self) -> None:
        _, registry_path, workspace = self.create_workspace_fixture()
        protected_path = workspace / "src" / "app" / "api" / "auth" / "session" / "route.ts"
        protected_path.write_text(
            protected_path.read_text(encoding="utf-8") + "\n// drift\n",
            encoding="utf-8",
        )

        result = self.run_conformance(*self.base_args(registry_path, workspace))
        self.assertEqual(result.returncode, 1)
        violations = self.extract_section(result.stdout, "## Blocking Violations")
        self.assertIn("src/app/api/auth/session/route.ts", violations)
        self.assertIn("fingerprint drift", violations)
        self.assertIn("sha256", self.extract_section(result.stdout, "## Fingerprint Checks"))


if __name__ == "__main__":
    unittest.main()
