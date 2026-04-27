import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
COMMANDS_SH = ROOT_DIR / "orchestration" / "cron" / "commands.sh"
VALIDATOR = ROOT_DIR / "scripts" / "validate_approved_delivery_pipeline.py"
OPERATIONS_MD = ROOT_DIR / "docs" / "OPERATIONS.md"
CEO_AGENTS_MD = ROOT_DIR / "assets" / "workspaces" / "ceo" / "AGENTS.md"
BASH_EXE = shutil.which("bash") or "bash"


class ApprovedDeliveryPipelineCliTests(unittest.TestCase):
    def test_command_wrappers_help_and_arity_guards(self) -> None:
        wrappers = [
            ("start-approved-delivery", "start_approved_project_delivery.py", "<approved-project-path>"),
            ("render-approved-delivery-status", "render_approved_delivery_status.py", "<approved-project-path>"),
            ("validate-approved-delivery-pipeline", "validate_approved_delivery_pipeline.py", "<approved-project-path>"),
            ("resume-approved-delivery", "start_approved_project_delivery.py", "resume-approved-delivery"),
        ]

        for command, expected_help_fragment, usage_fragment in wrappers:
            with self.subTest(command=command):
                help_result = self.run_shell(command, "--help")
                self.assertEqual(help_result.returncode, 0, help_result.stderr)
                self.assertIn(expected_help_fragment, help_result.stdout + help_result.stderr)

                arity_result = self.run_shell(command)
                self.assertNotEqual(arity_result.returncode, 0)
                self.assertIn("Usage:", arity_result.stdout + arity_result.stderr)
                self.assertIn(usage_fragment, arity_result.stdout + arity_result.stderr)

    def test_validator_fails_when_required_artifacts_or_cross_links_are_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            approved_project = Path(tmp) / "assets" / "shared" / "approved-projects" / "demo-project"
            approved_project.mkdir(parents=True)
            workspace = Path(tmp) / "workspace"
            workspace.mkdir()
            hermes = workspace / ".hermes"
            hermes.mkdir()

            conformance = workspace / ".hermes" / "template-conformance.json"
            self.write_text(approved_project / "PROJECT_BRIEF.md", "# Brief\n")
            self.write_json(
                approved_project / "APPROVED_PROJECT.json",
                {
                    "project_slug": "demo-project",
                    "workspace_path": workspace.as_posix(),
                    "status": "blocked",
                    "stage": "delivery_run_bootstrap",
                    "phase9_delivery_run_manifest": ".hermes/delivery-run-manifest.json",
                    "conformance_evidence_path": conformance.as_posix(),
                },
            )
            downstream = workspace / ".hermes" / "release-prerequisites.json"
            self.write_jsonl(
                approved_project / "approved-delivery-events.jsonl",
                [
                    {
                        "stage": "delivery_run_bootstrap",
                        "status": "blocked",
                        "block_reason": "missing downstream prerequisite evidence",
                        "evidence_path": downstream.as_posix(),
                    }
                ],
            )
            self.write_text(
                approved_project / "DELIVERY_PIPELINE_STATUS.md",
                "# Approved Delivery Status\n\n"
                "Blocked on prerequisite evidence.\n"
                f"Evidence: {downstream.as_posix()}\n",
            )
            self.write_json(workspace / ".hermes" / "delivery-run-manifest.json", {"run_id": "run-1"})
            self.write_json(conformance, {"ok": True})
            self.write_text(workspace / ".hermes" / "FINAL_DELIVERY.md", "# Final delivery\n")

            result = self.run_validator(approved_project)
            self.assertNotEqual(result.returncode, 0)
            output = result.stdout + result.stderr
            self.assertIn("final handoff", output)
            self.assertIn("block", output)
            self.assertIn("evidence", output)

    def test_validator_passes_only_when_authority_workspace_events_and_status_agree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            approved_project = Path(tmp) / "assets" / "shared" / "approved-projects" / "demo-project"
            approved_project.mkdir(parents=True)
            workspace = Path(tmp) / "workspace"
            workspace.mkdir()
            hermes = workspace / ".hermes"
            hermes.mkdir()

            final_delivery = workspace / ".hermes" / "FINAL_DELIVERY.md"
            manifest = workspace / ".hermes" / "delivery-run-manifest.json"
            conformance = workspace / ".hermes" / "template-conformance.json"
            downstream = workspace / ".hermes" / "release-prerequisites.json"
            self.write_text(final_delivery, "# Final delivery\n\n## 1) End-to-end Summary\n")
            self.write_json(manifest, {"run_id": "run-1", "stages": [{"stage": "design", "role": "designer", "artifact": ".hermes/stage-handoffs/01-design.md"}]})
            self.write_json(conformance, {"ok": True})
            self.write_json(downstream, {"ok": True, "evidence": ["vercel", "github"]})
            self.write_text(workspace / ".hermes" / "stage-handoffs" / "01-design.md", "placeholder")

            final_ref = final_delivery.as_posix()
            self.write_json(
                approved_project / "APPROVED_PROJECT.json",
                {
                    "project_slug": "demo-project",
                    "workspace_path": workspace.as_posix(),
                    "project_brief_path": (approved_project / "PROJECT_BRIEF.md").as_posix(),
                    "conformance_evidence_path": conformance.as_posix(),
                    "phase9_delivery_run_manifest_path": manifest.as_posix(),
                    "final_handoff": {"path": final_ref, "link": final_ref},
                    "latest_blocked_prerequisite": {"path": downstream.as_posix(), "status": "resolved"},
                },
            )
            self.write_text(approved_project / "PROJECT_BRIEF.md", "# Brief\n")
            self.write_jsonl(
                approved_project / "approved-delivery-events.jsonl",
                [
                    {
                        "stage": "approval",
                        "status": "completed",
                        "workspace_path": workspace.as_posix(),
                    },
                    {
                        "stage": "handoff",
                        "status": "completed",
                        "final_handoff": {"path": final_ref, "link": final_ref},
                        "workspace_path": workspace.as_posix(),
                    },
                ],
            )
            self.write_text(
                approved_project / "DELIVERY_PIPELINE_STATUS.md",
                "# Approved Delivery Status\n\n"
                "- Authority: approved-project\n"
                f"- Workspace: {workspace.as_posix()}\n"
                f"- Final handoff: {final_ref}\n",
            )

            result = self.run_validator(approved_project)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("validated approved delivery pipeline", result.stdout)
            self.assertIn("handoff", result.stdout)

    def test_operations_and_ceo_docs_lock_start_inspect_block_resume_flow(self) -> None:
        operations = OPERATIONS_MD.read_text(encoding="utf-8")
        ceo = CEO_AGENTS_MD.read_text(encoding="utf-8")

        for text, label in [(operations, "operations"), (ceo, "ceo")]:
            with self.subTest(label=label):
                self.assertIn("start-approved-delivery", text)
                self.assertIn("render-approved-delivery-status", text)
                self.assertIn("resume-approved-delivery", text)
                self.assertRegex(text.lower(), r"resume from persisted state|instead of restarting from scratch")
                self.assertRegex(text.lower(), r"block|blocked")
                self.assertRegex(text.lower(), r"credential|deployment|prerequisite")

    def run_shell(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [BASH_EXE, str(COMMANDS_SH), *args],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )

    def run_validator(self, approved_project: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--approved-project-path", str(approved_project)],
            cwd=ROOT_DIR,
            capture_output=True,
            text=True,
        )

    def write_json(self, path: Path, payload: dict) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    def write_jsonl(self, path: Path, events: list[dict]) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("\n".join(json.dumps(event, ensure_ascii=False) for event in events) + "\n", encoding="utf-8")

    def write_text(self, path: Path, text: str) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
