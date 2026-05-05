import importlib.util
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
HANDOFF_VALIDATOR = ROOT_DIR / "scripts" / "validate_delivery_handoff.py"
DELIVERY_STARTER = ROOT_DIR / "scripts" / "start_approved_project_delivery.py"
STAGE_TEMPLATE = ROOT_DIR / "docs" / "skill-governance" / "templates" / "stage-handoff-template-v0.2.md"
OPERATIONS_MD = ROOT_DIR / "docs" / "OPERATIONS.md"
CEO_AGENTS_MD = ROOT_DIR / "assets" / "workspaces" / "ceo" / "AGENTS.md"


def resolve_bash_executable() -> str:
    candidates = [
        shutil.which("bash"),
        r"C:\Program Files\Git\bin\bash.exe",
        r"C:\Program Files\Git\usr\bin\bash.exe",
        r"C:\Program Files (x86)\Git\bin\bash.exe",
        r"C:\Program Files (x86)\Git\usr\bin\bash.exe",
    ]
    for candidate in candidates:
        if not candidate or not Path(candidate).exists():
            continue
        if Path(candidate).as_posix().lower().endswith("/system32/bash.exe"):
            continue
        return candidate
    return shutil.which("bash") or "bash"


BASH_EXE = resolve_bash_executable()


def load_module(module_name: str, script_path: Path):
    if not script_path.exists():
        raise AssertionError(f"expected script to exist: {script_path}")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"unable to load module spec for {script_path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class ApprovedDeliveryPipelineCliTests(unittest.TestCase):
    def build_minimal_approved_record(self) -> dict:
        return {
            "project_identity": {
                "app_name": "Demo Product",
                "app_key": "demo_product",
                "app_url": "https://demo.example.com",
            },
            "target_user": "operations leads",
            "mvp_framing": "deliver a governed workflow",
            "approved_scope": [
                "replace template starter copy with a workflow-specific landing page",
                "deliver a concrete user workflow",
            ],
            "product_requirements": {
                "pain_point": "operators cannot move from approval to delivery with evidence they can trust",
                "monetization": ["paid team subscription"],
                "required_languages": ["en", "zh"],
            },
        }

    def minimal_product_proof_markdown(self) -> str:
        return (
            "## Product Proof\n"
            "- Proof Verdict: `pass`\n"
            "- Primary Workflow Surfaces: `src/app/dashboard/page.tsx`\n"
            "- Supporting Logic Evidence: `src/lib/product-workflow.ts`\n"
            "- Excluded Proof Paths: `src/app/demo/page.tsx, src/lib/app-definition.ts`\n"
            "- Excluded Proof Reasons: `/demo surfaces never count as privileged product proof; identity/bootstrap-only files do not count as product proof`\n"
            "- Template Residue Blockers: `none`\n"
            "- Template Residue Warnings: `none`\n"
            "- Failure Reasons: `none`\n\n"
        )

    def test_runtime_ui_gate_blocks_missing_or_stale_artifacts_for_ui_stages(self) -> None:
        starter_module = load_module("start_approved_project_delivery_ui_gate_tests", DELIVERY_STARTER)
        record = self.build_minimal_approved_record()

        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            valid, reason, evidence_path, message = starter_module.validate_ui_ux_artifact(
                workspace,
                record,
                pipeline_stage="design",
            )
            self.assertFalse(valid)
            self.assertEqual(reason, "missing_ui_ux_artifact")
            self.assertEqual(evidence_path, (workspace / ".hermes" / starter_module.UI_UX_ARTIFACT_NAME).as_posix())
            self.assertIn("missing", message)

            artifact_path = starter_module.specialist_ui_artifact_path(workspace)
            artifact_path.parent.mkdir(parents=True, exist_ok=True)
            artifact_path.write_text("# UI artifact\n", encoding="utf-8")
            summary_path = starter_module.specialist_ui_artifact_summary_path(workspace)
            stale_summary = starter_module.build_ui_ux_artifact_summary(
                record,
                artifact_path,
                pipeline_stage="development",
                role="development-specialist",
            )
            stale_summary["coverage"]["screen_inventory"] = []
            self.write_json(summary_path, stale_summary)

            valid, reason, evidence_path, message = starter_module.validate_ui_ux_artifact(
                workspace,
                record,
                pipeline_stage="development",
            )
            self.assertFalse(valid)
            self.assertEqual(reason, "ui_ux_artifact_coverage_incomplete")
            self.assertEqual(evidence_path, summary_path.as_posix())
            self.assertIn("screen_inventory", message)

            drift_summary = starter_module.build_ui_ux_artifact_summary(
                record,
                artifact_path,
                pipeline_stage="development",
                role="development-specialist",
            )
            drift_summary["brief_contract"]["pain_point"] = "drifted brief"
            self.write_json(summary_path, drift_summary)

            valid, reason, evidence_path, message = starter_module.validate_ui_ux_artifact(
                workspace,
                record,
                pipeline_stage="development",
            )
            self.assertFalse(valid)
            self.assertEqual(reason, "ui_ux_artifact_stale")
            self.assertEqual(evidence_path, summary_path.as_posix())
            self.assertIn("pain_point", message)

    def test_runtime_stage_evidence_bundle_requires_non_empty_transcript_and_linked_paths(self) -> None:
        starter_module = load_module("start_approved_project_delivery_stage_bundle_tests", DELIVERY_STARTER)
        record = self.build_minimal_approved_record()
        config = starter_module.SPECIALIST_STAGE_BY_PIPELINE["development"]

        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            handoff_path = workspace / ".hermes" / "stage-handoffs" / "02-development.md"
            handoff_path.parent.mkdir(parents=True, exist_ok=True)
            handoff_path.write_text("# development\n", encoding="utf-8")
            inventory_path = workspace / ".hermes" / starter_module.WORKSPACE_CHANGE_INVENTORY_NAME
            self.write_json(inventory_path, {"touched_paths": ["src/app/page.tsx"]})
            artifact_path = starter_module.specialist_ui_artifact_path(workspace)
            artifact_path.write_text("# UI artifact\n", encoding="utf-8")
            summary = starter_module.build_ui_ux_artifact_summary(
                record,
                artifact_path,
                pipeline_stage="development",
                role="development-specialist",
            )
            summary_path = starter_module.specialist_ui_artifact_summary_path(workspace)
            self.write_json(summary_path, summary)

            starter_module.write_stage_structured_evidence(
                workspace,
                config,
                run_id="run-1",
                handoff_path=handoff_path.as_posix(),
                transcript_path="",
                changed_files=["src/app/page.tsx"],
                evidence_links=[inventory_path.as_posix()],
                workspace_change_inventory_path=inventory_path.as_posix(),
                ui_artifact_path=artifact_path.as_posix(),
                ui_artifact_summary_path=summary_path.as_posix(),
            )
            ok, reason, evidence_path, message = starter_module.validate_stage_evidence_bundle(
                workspace,
                config,
                run_id="run-1",
                handoff_path=handoff_path.as_posix(),
            )
            self.assertFalse(ok)
            self.assertEqual(reason, "missing_claude_code_transcript")
            self.assertIn("transcript", message)

            transcript_path = workspace / ".hermes" / "development-claude-code.txt"
            transcript_path.write_text("transcript evidence\n", encoding="utf-8")
            starter_module.write_stage_structured_evidence(
                workspace,
                config,
                run_id="run-1",
                handoff_path=handoff_path.as_posix(),
                transcript_path=transcript_path.as_posix(),
                changed_files=["src/app/page.tsx"],
                evidence_links=[inventory_path.as_posix()],
                workspace_change_inventory_path=inventory_path.as_posix(),
                ui_artifact_path=artifact_path.as_posix(),
                ui_artifact_summary_path=summary_path.as_posix(),
            )
            payload = json.loads(
                starter_module.specialist_stage_evidence_path(workspace, config).read_text(encoding="utf-8")
            )
            payload["handoff_path"] = (workspace / ".hermes" / "stage-handoffs" / "other.md").as_posix()
            self.write_json(starter_module.specialist_stage_evidence_path(workspace, config), payload)

            ok, reason, evidence_path, message = starter_module.validate_stage_evidence_bundle(
                workspace,
                config,
                run_id="run-1",
                handoff_path=handoff_path.as_posix(),
            )
            self.assertFalse(ok)
            self.assertEqual(reason, "stage_evidence_artifact_mismatch")
            self.assertEqual(evidence_path, starter_module.specialist_stage_evidence_path(workspace, config).as_posix())
            self.assertIn("handoff path mismatch", message)

    def test_runtime_testing_stage_requires_verification_evidence(self) -> None:
        starter_module = load_module("start_approved_project_delivery_testing_gate_tests", DELIVERY_STARTER)
        config = starter_module.SPECIALIST_STAGE_BY_PIPELINE["testing"]

        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            handoff_path = workspace / ".hermes" / "stage-handoffs" / "03-testing.md"
            handoff_path.parent.mkdir(parents=True, exist_ok=True)
            handoff_path.write_text("# testing\n", encoding="utf-8")
            transcript_path = workspace / ".hermes" / "testing-claude-code.txt"
            transcript_path.write_text("verification transcript\n", encoding="utf-8")
            inventory_path = workspace / ".hermes" / starter_module.WORKSPACE_CHANGE_INVENTORY_NAME
            self.write_json(inventory_path, {"touched_paths": ["src/app/page.tsx"]})

            starter_module.write_stage_structured_evidence(
                workspace,
                config,
                run_id="run-1",
                handoff_path=handoff_path.as_posix(),
                transcript_path=transcript_path.as_posix(),
                changed_files=["src/app/page.tsx"],
                evidence_links=[inventory_path.as_posix(), transcript_path.as_posix()],
                workspace_change_inventory_path=inventory_path.as_posix(),
                verification_evidence=[],
            )
            ok, reason, evidence_path, message = starter_module.validate_stage_evidence_bundle(
                workspace,
                config,
                run_id="run-1",
                handoff_path=handoff_path.as_posix(),
            )
            self.assertFalse(ok)
            self.assertEqual(reason, "missing_testing_verification_evidence")
            self.assertEqual(evidence_path, starter_module.specialist_stage_evidence_path(workspace, config).as_posix())
            self.assertIn("verification evidence", message)

    def test_validator_stage_evidence_requires_transcript_and_testing_verification(self) -> None:
        validator_module = load_module("validate_delivery_handoff_stage_evidence_tests", HANDOFF_VALIDATOR)

        with tempfile.TemporaryDirectory() as tmp:
            workspace = Path(tmp)
            handoff_path = workspace / ".hermes" / "stage-handoffs" / "03-testing.md"
            handoff_path.parent.mkdir(parents=True, exist_ok=True)
            handoff_path.write_text("# testing\n", encoding="utf-8")
            evidence_path = workspace / ".hermes" / "stage-evidence" / "03-testing.json"
            self.write_json(
                evidence_path,
                {
                    "run_id": "run-1",
                    "stage": "testing",
                    "role": "testing-specialist",
                    "handoff_path": handoff_path.as_posix(),
                    "transcript_path": "",
                    "workspace_change_inventory_path": (workspace / ".hermes" / "workspace-changes.json").as_posix(),
                    "evidence_links": [handoff_path.as_posix()],
                    "verification_evidence": [],
                },
            )

            with self.assertRaisesRegex(Exception, "missing transcript path"):
                validator_module.validate_stage_evidence(
                    evidence_path,
                    expected_stage="testing",
                    expected_role="testing-specialist",
                    expected_handoff_path=handoff_path.as_posix(),
                    run_id="run-1",
                )

    def test_specialist_handoff_template_and_runtime_follow_validator_owned_nine_section_contract(self) -> None:
        validator_module = load_module("validate_delivery_handoff_for_cli_tests", HANDOFF_VALIDATOR)
        starter_module = load_module("start_approved_project_delivery_for_cli_tests", DELIVERY_STARTER)

        markdown = starter_module.build_specialist_handoff_markdown(
            run_id="run-1",
            role="design-specialist",
            stage="design",
            next_stage="development",
            scope_status="approved-brief-only",
            summary="design handoff complete",
            outputs=["ui artifact"],
            evidence_links=["evidence://design"],
            gate_decision="PASS",
            gate_reason="ready for next stage",
            risks=["monitor regressions"],
            next_stage_inputs=["continue with approved brief"],
            changed_files=["src/app/page.tsx"],
            user_visible_behavior=["users can review the approved landing structure"],
            pain_point_mapping=["signal mapped to concrete UI change"],
        )

        last_position = -1
        for heading in validator_module.REQUIRED_STAGE_HEADINGS:
            self.assertIn(heading, markdown)
            current_position = markdown.index(heading)
            self.assertGreater(current_position, last_position)
            last_position = current_position

        template_text = STAGE_TEMPLATE.read_text(encoding="utf-8")
        for heading in validator_module.REQUIRED_STAGE_HEADINGS:
            self.assertIn(heading, template_text)

        self.assertIn("User Visible Behavior", template_text)
        self.assertIn("Pain Point Mapping", template_text)
        self.assertIn("不能为空", template_text)

    def test_command_wrappers_help_and_arity_guards(self) -> None:
        wrappers = [
            ("start-approved-delivery", "start_approved_project_delivery.py", "<approved-project-path>"),
            ("render-approved-delivery-status", "render_approved_delivery_status.py", "<approved-project-path>"),
            ("validate-approved-delivery-pipeline", "validate_approved_delivery_pipeline.py", "<approved-project-path>"),
            ("resume-approved-delivery", "start_approved_project_delivery.py", "resume-approved-delivery"),
            ("prepare-approved-delivery-github", "start_approved_project_delivery.py", "prepare-approved-delivery-github"),
            ("sync-approved-delivery-github", "start_approved_project_delivery.py", "sync-approved-delivery-github"),
            ("link-approved-delivery-vercel", "start_approved_project_delivery.py", "link-approved-delivery-vercel"),
            ("deploy-approved-delivery-vercel", "start_approved_project_delivery.py", "deploy-approved-delivery-vercel"),
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
                    "artifacts": {
                        "final_review_path": (approved_project / "FINAL_OPERATOR_REVIEW.md").as_posix(),
                    },
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
            self.assertIn("final operator review", output)
            self.assertIn("block", output)
            self.assertIn("evidence", output)

    def test_validator_rejects_vercel_metadata_without_authoritative_evidence(self) -> None:
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
            final_review = approved_project / "FINAL_OPERATOR_REVIEW.md"
            self.write_text(final_delivery, "# Final delivery\n\n## 1) End-to-end Summary\n")
            self.write_json(manifest, {"run_id": "run-1"})
            self.write_json(conformance, {"ok": True})
            self.write_text(final_review, "# Final Operator Review\n\n## Credentialed Delivery Actions\nVercel Deploy Audit: ok\n\n## Protected Change Review\nProtected change: none\n")
            self.write_text(approved_project / "PROJECT_BRIEF.md", "# Brief\n")

            final_ref = final_delivery.as_posix()
            self.write_json(
                approved_project / "APPROVED_PROJECT.json",
                {
                    "project_slug": "demo-project",
                    "workspace_path": workspace.as_posix(),
                    "conformance_evidence_path": conformance.as_posix(),
                    "phase9_delivery_run_manifest_path": manifest.as_posix(),
                    "final_handoff": {"path": final_ref, "link": final_ref},
                    "shipping": {
                        "vercel": {
                            "project_name": "demo-project-prod",
                            "project_url": "https://vercel.com/profit-corp/demo-project-prod",
                            "team_scope": "profit-corp",
                        }
                    },
                    "artifacts": {
                        "final_review_path": final_review.as_posix(),
                    },
                },
            )
            self.write_jsonl(
                approved_project / "approved-delivery-events.jsonl",
                [
                    {
                        "stage": "handoff",
                        "status": "completed",
                        "final_handoff": {"path": final_ref, "link": final_ref},
                        "workspace_path": workspace.as_posix(),
                    }
                ],
            )
            self.write_text(
                approved_project / "DELIVERY_PIPELINE_STATUS.md",
                "# Approved Delivery Status\n\n"
                f"- Authority: approved-project\n"
                f"- Workspace: {workspace.as_posix()}\n"
                f"- Final handoff: {final_ref}\n"
                f"- Final operator review: {final_review.as_posix()}\n"
                f"- Protected change classification: not available\n"
                f"- Platform justification status: not available\n"
                f"- Governance action: not available\n"
                f"- Blocked prerequisite evidence: not available\n"
                f"- Vercel project name: demo-project-prod\n"
                f"- Vercel project URL: https://vercel.com/profit-corp/demo-project-prod\n"
                f"- Vercel team scope: profit-corp\n",
            )

            result = self.run_validator(approved_project)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("env contract", (result.stdout + result.stderr).lower())

    def test_validator_rejects_template_only_specialist_output(self) -> None:
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
            final_review = approved_project / "FINAL_OPERATOR_REVIEW.md"
            final_delivery.write_text("# Final delivery\n", encoding="utf-8")
            self.write_json(manifest, {"run_id": "run-1"})
            self.write_json(conformance, {"ok": True})
            self.write_text(approved_project / "PROJECT_BRIEF.md", "# Brief\n")
            self.write_text(final_review, "# Final Operator Review\n\n## Credentialed Delivery Actions\nGitHub ok\nVercel ok\n")
            design_handoff, design_evidence, design_event = self.write_specialist_stage_fixture(
                workspace,
                stage_key="design",
                stage_label="design",
                role="design-specialist",
                template_only=True,
            )
            development_handoff, development_evidence, development_event = self.write_specialist_stage_fixture(
                workspace,
                stage_key="development",
                stage_label="development",
                role="development-specialist",
            )
            testing_handoff, testing_evidence, testing_event = self.write_specialist_stage_fixture(
                workspace,
                stage_key="testing",
                stage_label="testing",
                role="testing-specialist",
                verification_evidence=[
                    (workspace / ".hermes" / "testing-workspace-changes.json").as_posix(),
                    (workspace / ".hermes" / "testing-claude-code.txt").as_posix(),
                ],
            )
            git_handoff, git_evidence, git_versioning_event = self.write_specialist_stage_fixture(
                workspace,
                stage_key="git_versioning",
                stage_label="git versioning",
                role="git-versioning-specialist",
            )
            release_handoff, release_evidence, release_readiness_event = self.write_specialist_stage_fixture(
                workspace,
                stage_key="release_readiness",
                stage_label="release readiness",
                role="release-readiness-specialist",
                verification_evidence=[
                    (workspace / ".hermes" / "release_readiness-workspace-changes.json").as_posix(),
                    (workspace / ".hermes" / "release_readiness-claude-code.txt").as_posix(),
                ],
            )
            final_ref = final_delivery.as_posix()
            self.write_json(
                approved_project / "APPROVED_PROJECT.json",
                {
                    "project_slug": "demo-project",
                    "workspace_path": workspace.as_posix(),
                    "conformance_evidence_path": conformance.as_posix(),
                    "phase9_delivery_run_manifest_path": manifest.as_posix(),
                    "final_handoff": {"path": final_ref, "link": final_ref},
                    "pipeline": {
                        "stage": "handoff",
                        "status": "completed",
                        "resume_from_stage": "handoff",
                        "workspace_path": workspace.as_posix(),
                        "final_handoff_path": final_ref,
                    },
                    "shipping": {
                        "github": {
                            "repository_mode": "attach",
                            "repository_owner": "profit-corp",
                            "repository_name": "profit-corp/demo-project",
                            "repository_url": "https://github.com/profit-corp/demo-project.git",
                            "default_branch": "main",
                            "synced_commit": "abc1234",
                            "sync_evidence_path": (workspace / ".hermes" / "github-sync.json").as_posix(),
                            "last_sync_status": "completed",
                        },
                        "vercel": {
                            "project_name": "demo-project-prod",
                            "project_url": "https://vercel.com/profit-corp/demo-project-prod",
                            "team_scope": "profit-corp",
                            "env_contract_path": (workspace / ".hermes" / "vercel-env-contract.json").as_posix(),
                            "deploy_status": "ready",
                            "deploy_url": "https://demo-project.vercel.app",
                            "deploy_evidence_path": (workspace / ".hermes" / "vercel-deploy.json").as_posix(),
                        },
                    },
                    "artifacts": {
                        "final_review_path": final_review.as_posix(),
                    },
                },
            )
            self.write_jsonl(
                approved_project / "approved-delivery-events.jsonl",
                [
                    design_event,
                    development_event,
                    testing_event,
                    git_versioning_event,
                    release_readiness_event,
                    {
                        "stage": "handoff",
                        "status": "completed",
                        "outcome": "pass",
                        "artifact": final_ref,
                        "final_handoff": {"path": final_ref, "link": final_ref},
                        "workspace_path": workspace.as_posix(),
                    },
                ],
            )
            self.write_text(
                approved_project / "DELIVERY_PIPELINE_STATUS.md",
                "# Delivery Pipeline Status\n\n"
                f"- Authority: approved-project\n"
                f"- Workspace: {workspace.as_posix()}\n"
                f"- Final handoff: {final_ref}\n"
                f"- Final operator review: {final_review.as_posix()}\n"
                f"- Blocked prerequisite evidence: not available\n"
                f"- Protected change classification: product_only\n"
                f"- Platform justification status: not available\n"
                f"- Governance action: not available\n"
                f"## Specialist Delivery Stages\n"
                f"- design: status=`ready` artifact=`{design_handoff}` evidence=`{design_evidence}` template_only=`yes`\n"
                f"- development: status=`ready` artifact=`{development_handoff}` evidence=`{development_evidence}`\n"
                f"- testing: status=`ready` artifact=`{testing_handoff}` evidence=`{testing_evidence}`\n"
                f"- git_versioning: status=`ready` artifact=`{git_handoff}` evidence=`{git_evidence}`\n"
                f"- release_readiness: status=`ready` artifact=`{release_handoff}` evidence=`{release_evidence}`\n",
            )

            result = self.run_validator(approved_project)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("template-only", (result.stdout + result.stderr).lower())

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
            github_sync = workspace / ".hermes" / "github-sync.json"
            github_sync_audit = workspace / ".hermes" / "github-sync-audit.json"
            vercel_link = workspace / ".hermes" / "vercel-link.json"
            vercel_env = workspace / ".hermes" / "vercel-env-contract.json"
            vercel_deploy = workspace / ".hermes" / "vercel-deploy.json"
            final_review = approved_project / "FINAL_OPERATOR_REVIEW.md"
            self.write_text(final_delivery, "# Final delivery\n\n## 1) End-to-end Summary\n")
            self.write_json(manifest, {"run_id": "run-1"})
            self.write_json(conformance, {"ok": True})
            self.write_json(downstream, {"ok": True})
            self.write_json(github_sync, {"ok": True})
            self.write_json(github_sync_audit, {"ok": True})
            self.write_json(vercel_link, {"ok": True})
            self.write_json(vercel_env, {"ok": True})
            self.write_json(vercel_deploy, {"ok": True})
            self.write_text(approved_project / "PROJECT_BRIEF.md", "# Brief\n")
            self.write_text(final_review, "# Final Operator Review\n\n## Credentialed Delivery Actions\nRecovered completed state\nGitHub repository url present\nVercel deploy complete\n\n## Event History\nBlocked history preserved\n")

            final_ref = final_delivery.as_posix()
            self.write_json(
                approved_project / "APPROVED_PROJECT.json",
                {
                    "project_slug": "demo-project",
                    "workspace_path": workspace.as_posix(),
                    "conformance_evidence_path": conformance.as_posix(),
                    "phase9_delivery_run_manifest_path": manifest.as_posix(),
                    "final_handoff": {"path": final_ref, "link": final_ref},
                    "pipeline": {
                        "stage": "vercel_deploy",
                        "status": "completed",
                        "block_reason": None,
                        "resume_from_stage": "handoff",
                        "workspace_path": workspace.as_posix(),
                        "evidence_path": vercel_deploy.as_posix(),
                        "final_handoff_path": final_ref,
                    },
                    "latest_blocked_prerequisite": {
                        "path": downstream.as_posix(),
                        "status": "resolved",
                        "reason": "github_sync_failed",
                    },
                    "shipping": {
                        "github": {
                            "repository_mode": "attach",
                            "repository_owner": "profit-corp",
                            "repository_name": "profit-corp/demo-project",
                            "repository_url": "https://github.com/profit-corp/demo-project.git",
                            "default_branch": "main",
                            "synced_commit": "abc1234",
                            "sync_evidence_path": github_sync.as_posix(),
                            "sync_audit_path": github_sync_audit.as_posix(),
                            "last_sync_status": "completed",
                        },
                        "vercel": {
                            "project_name": "demo-project-prod",
                            "project_url": "https://vercel.com/profit-corp/demo-project-prod",
                            "team_scope": "profit-corp",
                            "env_contract_path": vercel_env.as_posix(),
                            "linked": True,
                            "deploy_status": "ready",
                            "deploy_url": "https://demo-project.vercel.app",
                            "deploy_evidence_path": vercel_deploy.as_posix(),
                        },
                    },
                    "artifacts": {
                        "final_review_path": "assets/shared/approved-projects/demo-project/FINAL_OPERATOR_REVIEW.md",
                    },
                },
            )
            self.write_jsonl(
                approved_project / "approved-delivery-events.jsonl",
                [
                    {
                        "stage": "github_sync",
                        "status": "blocked",
                        "outcome": "blocked",
                        "block_reason": "github_sync_failed",
                        "evidence_path": downstream.as_posix(),
                        "workspace_path": workspace.as_posix(),
                    },
                    {
                        "stage": "vercel_deploy",
                        "status": "completed",
                        "outcome": "pass",
                        "artifact": vercel_deploy.as_posix(),
                        "evidence_path": vercel_deploy.as_posix(),
                        "final_handoff_path": final_ref,
                        "workspace_path": workspace.as_posix(),
                        "shipping": {
                            "github": {
                                "repository_mode": "attach",
                                "repository_owner": "profit-corp",
                                "repository_name": "profit-corp/demo-project",
                                "repository_url": "https://github.com/profit-corp/demo-project.git",
                                "default_branch": "main",
                                "synced_commit": "abc1234",
                                "sync_evidence_path": github_sync.as_posix(),
                                "sync_audit_path": github_sync_audit.as_posix(),
                                "last_sync_status": "completed",
                            },
                            "vercel": {
                                "project_name": "demo-project-prod",
                                "project_url": "https://vercel.com/profit-corp/demo-project-prod",
                                "team_scope": "profit-corp",
                                "link_evidence_path": vercel_link.as_posix(),
                                "env_contract_path": vercel_env.as_posix(),
                                "linked": True,
                                "deploy_status": "ready",
                                "deploy_url": "https://demo-project.vercel.app",
                                "deploy_evidence_path": vercel_deploy.as_posix(),
                            },
                        },
                    },
                ],
            )
            self.write_text(
                approved_project / "DELIVERY_PIPELINE_STATUS.md",
                "# Delivery Pipeline Status\n"
                f"- **Authority Source**: `APPROVED_PROJECT.json`\n"
                f"- **Authority Record**: `{(approved_project / 'APPROVED_PROJECT.json').as_posix()}`\n"
                f"- **Final Operator Review**: `{final_review.as_posix()}`\n"
                f"- **Project Slug**: `demo-project`\n"
                f"- **Current Stage**: `vercel_deploy`\n"
                f"- **Pipeline Status**: `completed`\n"
                f"- **Latest Outcome**: `pass`\n"
                f"- **Delivery Brief**: `{(approved_project / 'PROJECT_BRIEF.md').as_posix()}`\n"
                f"- **Workspace Path**: `{workspace.as_posix()}`\n"
                f"- **Delivery Run ID**: `not available`\n\n"
                "## Final Operator Review\nRecovered final truth\n\n"
                "## Action Required\n- No immediate operator action required; governed delivery surface is coherent.\n\n"
                "## Approval Summary\n- Approval ID: `not available`\n- Approved At: `not available`\n- Approver: `not available`\n- Approval Evidence: `not available`\n- Approval Summary: `not available`\n\n"
                f"## Blocked Prerequisites\n- Block Reason: `github_sync_failed`\n- Blocked Prerequisite Evidence: `{downstream.as_posix()}`\n- Resume From Stage: `handoff`\n- Blocked State Visible: `yes`\n\n"
                f"## Credentialed Delivery Actions\n- GitHub Repository Mode: `attach`\n- GitHub Repository Owner: `profit-corp`\n- GitHub Repository Name: `profit-corp/demo-project`\n- GitHub Repository URL: `https://github.com/profit-corp/demo-project.git`\n- GitHub Default Branch: `main`\n- GitHub Synced Commit: `abc1234`\n- GitHub Sync Evidence Path: `{github_sync.as_posix()}`\n- GitHub Sync Audit Path: `{github_sync_audit.as_posix()}`\n- GitHub Sync Status: `completed`\n- Vercel Team Scope: `profit-corp`\n- Vercel Project ID: `not available`\n- Vercel Project Name: `demo-project-prod`\n- Vercel Project URL: `https://vercel.com/profit-corp/demo-project-prod`\n- Vercel Link Status: `yes`\n- Vercel Env Contract Path: `{vercel_env.as_posix()}`\n- Vercel Env Audit Path: `not available`\n- Vercel Deploy URL: `https://demo-project.vercel.app`\n- Vercel Deploy Status: `ready`\n- Vercel Deploy Evidence Path: `{vercel_deploy.as_posix()}`\n- Vercel Deploy Audit Path: `not available`\n\n"
                "## Protected Change Review\n- Protected Change Classification: `not available`\n- Protected Change Status: `not available`\n- Protected Change Evidence: `not available`\n- Platform Justification Status: `not available`\n- Platform Justification Artifact: `not available`\n- Governance Action: `not available`\n\n"
                f"## Deployment Outcome\n- Latest Stage Outcome: `pass`\n- Latest Artifact: `{vercel_deploy.as_posix()}`\n- Deployment Failure Visibility: `no`\n\n"
                f"## Final Handoff\n- Final Handoff Path: `{final_ref}`\n- Handoff Status: `completed`\n\n"
                "## Event History\n"
                f"- stage=`github_sync` status=`blocked` outcome=`blocked` block_reason=`github_sync_failed` artifact=`not available` evidence=`{downstream.as_posix()}` handoff=`not available`\n"
                f"- stage=`vercel_deploy` status=`completed` outcome=`pass` block_reason=`not available` artifact=`{vercel_deploy.as_posix()}` evidence=`{vercel_deploy.as_posix()}` handoff=`{final_ref}`\n\n"
                "This latest view is derived from authority latest state with append-only approved delivery event history as audit context.\n",
            )

            result = self.run_validator(approved_project)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validator_accepts_project_prefixed_relative_conformance_path(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            approved_project = Path(tmp) / "assets" / "shared" / "approved-projects" / "demo-project"
            approved_project.mkdir(parents=True)
            workspace = Path(tmp) / "workspace"
            workspace.mkdir()
            hermes = workspace / ".hermes"
            hermes.mkdir()

            final_delivery = workspace / ".hermes" / "FINAL_DELIVERY.md"
            manifest = workspace / ".hermes" / "delivery-run-manifest.json"
            downstream = workspace / ".hermes" / "release-prerequisites.json"
            github_sync = workspace / ".hermes" / "github-sync.json"
            github_sync_audit = workspace / ".hermes" / "github-sync-audit.json"
            vercel_link = workspace / ".hermes" / "vercel-link.json"
            vercel_env = workspace / ".hermes" / "vercel-env-contract.json"
            vercel_deploy = workspace / ".hermes" / "vercel-deploy.json"
            final_review = approved_project / "FINAL_OPERATOR_REVIEW.md"
            conformance = approved_project / "conformance-report.md"
            self.write_text(final_delivery, "# Final delivery\n\n## 1) End-to-end Summary\n")
            self.write_json(manifest, {"run_id": "run-1"})
            self.write_json(downstream, {"ok": True})
            self.write_json(github_sync, {"ok": True})
            self.write_json(github_sync_audit, {"ok": True})
            self.write_json(vercel_link, {"ok": True})
            self.write_json(vercel_env, {"ok": True})
            self.write_json(vercel_deploy, {"ok": True})
            self.write_text(approved_project / "PROJECT_BRIEF.md", "# Brief\n")
            self.write_text(final_review, "# Final Operator Review\n\n## Credentialed Delivery Actions\nRecovered completed state\nGitHub repository url present\nVercel deploy complete\n\n## Event History\nBlocked history preserved\n")
            self.write_text(conformance, "# Conformance report\n\nStatus: ok\n")

            final_ref = final_delivery.as_posix()
            self.write_json(
                approved_project / "APPROVED_PROJECT.json",
                {
                    "project_slug": "demo-project",
                    "workspace_path": workspace.as_posix(),
                    "phase9_delivery_run_manifest_path": manifest.as_posix(),
                    "final_handoff": {"path": final_ref, "link": final_ref},
                    "pipeline": {
                        "stage": "vercel_deploy",
                        "status": "completed",
                        "block_reason": None,
                        "resume_from_stage": "handoff",
                        "workspace_path": workspace.as_posix(),
                        "evidence_path": vercel_deploy.as_posix(),
                        "final_handoff_path": final_ref,
                    },
                    "latest_blocked_prerequisite": {
                        "path": downstream.as_posix(),
                        "status": "resolved",
                        "reason": "github_sync_failed",
                    },
                    "shipping": {
                        "github": {
                            "repository_mode": "attach",
                            "repository_owner": "profit-corp",
                            "repository_name": "profit-corp/demo-project",
                            "repository_url": "https://github.com/profit-corp/demo-project.git",
                            "default_branch": "main",
                            "synced_commit": "abc1234",
                            "sync_evidence_path": github_sync.as_posix(),
                            "sync_audit_path": github_sync_audit.as_posix(),
                            "last_sync_status": "completed",
                        },
                        "vercel": {
                            "project_name": "demo-project-prod",
                            "project_url": "https://vercel.com/profit-corp/demo-project-prod",
                            "team_scope": "profit-corp",
                            "env_contract_path": vercel_env.as_posix(),
                            "linked": True,
                            "deploy_status": "ready",
                            "deploy_url": "https://demo-project.vercel.app",
                            "deploy_evidence_path": vercel_deploy.as_posix(),
                        },
                    },
                    "artifacts": {
                        "final_review_path": final_review.as_posix(),
                        "conformance_evidence_path": "assets/shared/approved-projects/demo-project/conformance-report.md",
                    },
                    "conformance_evidence_path": "assets/shared/approved-projects/demo-project/conformance-report.md",
                },
            )
            self.write_jsonl(
                approved_project / "approved-delivery-events.jsonl",
                [
                    {
                        "stage": "github_sync",
                        "status": "blocked",
                        "outcome": "blocked",
                        "block_reason": "github_sync_failed",
                        "evidence_path": downstream.as_posix(),
                        "workspace_path": workspace.as_posix(),
                    },
                    {
                        "stage": "vercel_deploy",
                        "status": "completed",
                        "outcome": "pass",
                        "artifact": vercel_deploy.as_posix(),
                        "evidence_path": vercel_deploy.as_posix(),
                        "final_handoff_path": final_ref,
                        "workspace_path": workspace.as_posix(),
                        "shipping": {
                            "github": {
                                "repository_mode": "attach",
                                "repository_owner": "profit-corp",
                                "repository_name": "profit-corp/demo-project",
                                "repository_url": "https://github.com/profit-corp/demo-project.git",
                                "default_branch": "main",
                                "synced_commit": "abc1234",
                                "sync_evidence_path": github_sync.as_posix(),
                                "sync_audit_path": github_sync_audit.as_posix(),
                                "last_sync_status": "completed",
                            },
                            "vercel": {
                                "project_name": "demo-project-prod",
                                "project_url": "https://vercel.com/profit-corp/demo-project-prod",
                                "team_scope": "profit-corp",
                                "link_evidence_path": vercel_link.as_posix(),
                                "env_contract_path": vercel_env.as_posix(),
                                "linked": True,
                                "deploy_status": "ready",
                                "deploy_url": "https://demo-project.vercel.app",
                                "deploy_evidence_path": vercel_deploy.as_posix(),
                            },
                        },
                    },
                ],
            )
            self.write_text(
                approved_project / "DELIVERY_PIPELINE_STATUS.md",
                "# Delivery Pipeline Status\n"
                f"- **Authority Source**: `APPROVED_PROJECT.json`\n"
                f"- **Authority Record**: `{(approved_project / 'APPROVED_PROJECT.json').as_posix()}`\n"
                f"- **Final Operator Review**: `{final_review.as_posix()}`\n"
                f"- **Project Slug**: `demo-project`\n"
                f"- **Current Stage**: `vercel_deploy`\n"
                f"- **Pipeline Status**: `completed`\n"
                f"- **Latest Outcome**: `pass`\n"
                f"- **Delivery Brief**: `{(approved_project / 'PROJECT_BRIEF.md').as_posix()}`\n"
                f"- **Workspace Path**: `{workspace.as_posix()}`\n"
                f"- **Delivery Run ID**: `not available`\n\n"
                "## Final Operator Review\nRecovered final truth\n\n"
                "## Action Required\n- No immediate operator action required; governed delivery surface is coherent.\n\n"
                "## Approval Summary\n- Approval ID: `not available`\n- Approved At: `not available`\n- Approver: `not available`\n- Approval Evidence: `not available`\n- Approval Summary: `not available`\n\n"
                f"## Blocked Prerequisites\n- Block Reason: `github_sync_failed`\n- Blocked Prerequisite Evidence: `{downstream.as_posix()}`\n- Resume From Stage: `handoff`\n- Blocked State Visible: `yes`\n\n"
                f"## Credentialed Delivery Actions\n- GitHub Repository Mode: `attach`\n- GitHub Repository Owner: `profit-corp`\n- GitHub Repository Name: `profit-corp/demo-project`\n- GitHub Repository URL: `https://github.com/profit-corp/demo-project.git`\n- GitHub Default Branch: `main`\n- GitHub Synced Commit: `abc1234`\n- GitHub Sync Evidence Path: `{github_sync.as_posix()}`\n- GitHub Sync Audit Path: `{github_sync_audit.as_posix()}`\n- GitHub Sync Status: `completed`\n- Vercel Team Scope: `profit-corp`\n- Vercel Project ID: `not available`\n- Vercel Project Name: `demo-project-prod`\n- Vercel Project URL: `https://vercel.com/profit-corp/demo-project-prod`\n- Vercel Link Status: `yes`\n- Vercel Env Contract Path: `{vercel_env.as_posix()}`\n- Vercel Env Audit Path: `not available`\n- Vercel Deploy URL: `https://demo-project.vercel.app`\n- Vercel Deploy Status: `ready`\n- Vercel Deploy Evidence Path: `{vercel_deploy.as_posix()}`\n- Vercel Deploy Audit Path: `not available`\n\n"
                "## Protected Change Review\n- Protected Change Classification: `not available`\n- Protected Change Status: `not available`\n- Protected Change Evidence: `not available`\n- Platform Justification Status: `not available`\n- Platform Justification Artifact: `not available`\n- Governance Action: `not available`\n\n"
                f"## Deployment Outcome\n- Latest Stage Outcome: `pass`\n- Latest Artifact: `{vercel_deploy.as_posix()}`\n- Deployment Failure Visibility: `no`\n\n"
                f"## Final Handoff\n- Final Handoff Path: `{final_ref}`\n- Handoff Status: `completed`\n\n"
                "## Event History\n"
                f"- stage=`github_sync` status=`blocked` outcome=`blocked` block_reason=`github_sync_failed` artifact=`not available` evidence=`{downstream.as_posix()}` handoff=`not available`\n"
                f"- stage=`vercel_deploy` status=`completed` outcome=`pass` block_reason=`not available` artifact=`{vercel_deploy.as_posix()}` evidence=`{vercel_deploy.as_posix()}` handoff=`{final_ref}`\n\n"
                "This latest view is derived from authority latest state with append-only approved delivery event history as audit context.\n",
            )

            result = self.run_validator(approved_project)
            self.assertEqual(result.returncode, 0, result.stderr)

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
            github_sync = workspace / ".hermes" / "github-sync.json"
            github_sync_audit = workspace / ".hermes" / "github-sync-audit.json"
            vercel_env = workspace / ".hermes" / "vercel-env-contract.json"
            vercel_env_audit = workspace / ".hermes" / "vercel-env-audit.json"
            vercel_deploy = workspace / ".hermes" / "vercel-deploy.json"
            vercel_deploy_audit = workspace / ".hermes" / "vercel-deploy-audit.json"
            protected_inventory = workspace / ".hermes" / "protected-change-inventory.json"
            justification = approved_project / "PLATFORM_CHANGE_JUSTIFICATION.md"
            final_review = approved_project / "FINAL_OPERATOR_REVIEW.md"
            self.write_text(final_delivery, "# Final delivery\n\n## 1) End-to-end Summary\n")
            self.write_json(manifest, {"run_id": "run-1", "stages": [
                {"stage": "design", "role": "design-specialist", "artifact": ".hermes/stage-handoffs/01-design.md"},
                {"stage": "development", "role": "development-specialist", "artifact": ".hermes/stage-handoffs/02-development.md"},
                {"stage": "testing", "role": "testing-specialist", "artifact": ".hermes/stage-handoffs/03-testing.md"},
                {"stage": "git versioning", "role": "git-versioning-specialist", "artifact": ".hermes/stage-handoffs/04-git-versioning.md"},
                {"stage": "release readiness", "role": "release-readiness-specialist", "artifact": ".hermes/stage-handoffs/05-release-readiness.md"},
            ]})
            self.write_json(conformance, {"ok": True})
            self.write_json(downstream, {"ok": True, "evidence": ["vercel", "github"]})
            self.write_json(github_sync, {"ok": True})
            self.write_json(github_sync_audit, {"ok": True})
            self.write_json(vercel_env, {"ok": True})
            self.write_json(vercel_env_audit, {"ok": True})
            self.write_json(vercel_deploy, {"ok": True})
            self.write_json(vercel_deploy_audit, {"ok": True})
            self.write_json(protected_inventory, {"classification": "protected_platform_change"})
            self.write_text(justification, "# Platform change justification\n\nStatus: approved\n")
            self.write_text(final_review, "# Final Operator Review\n\n## Credentialed Delivery Actions\nGitHub Sync Audit: ok\nVercel Deploy Audit: ok\n## Specialist Delivery Stages\nClaude Code transcript recorded\nUI/UX preflight satisfied\n")
            design_handoff, design_evidence, design_event = self.write_specialist_stage_fixture(
                workspace, stage_key="design", stage_label="design", role="design-specialist"
            )
            development_handoff, development_evidence, development_event = self.write_specialist_stage_fixture(
                workspace, stage_key="development", stage_label="development", role="development-specialist"
            )
            testing_handoff, testing_evidence, testing_event = self.write_specialist_stage_fixture(
                workspace,
                stage_key="testing",
                stage_label="testing",
                role="testing-specialist",
                verification_evidence=[
                    (workspace / ".hermes" / "testing-workspace-changes.json").as_posix(),
                    (workspace / ".hermes" / "testing-claude-code.txt").as_posix(),
                ],
            )
            git_handoff, git_evidence, git_event = self.write_specialist_stage_fixture(
                workspace, stage_key="git_versioning", stage_label="git versioning", role="git-versioning-specialist"
            )
            release_handoff, release_evidence, release_event = self.write_specialist_stage_fixture(
                workspace,
                stage_key="release_readiness",
                stage_label="release readiness",
                role="release-readiness-specialist",
                verification_evidence=[
                    (workspace / ".hermes" / "release_readiness-workspace-changes.json").as_posix(),
                    (workspace / ".hermes" / "release_readiness-claude-code.txt").as_posix(),
                ],
            )

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
                    "latest_blocked_prerequisite": {"path": downstream.as_posix(), "status": "resolved", "reason": "missing_downstream_prerequisite_evidence"},
                    "shipping": {
                        "github": {
                            "repository_mode": "attach",
                            "repository_name": "profit-corp/demo-project",
                            "repository_url": "https://github.com/profit-corp/demo-project.git",
                            "default_branch": "main",
                            "synced_commit": "abc1234",
                            "sync_evidence_path": github_sync.as_posix(),
                            "sync_audit_path": github_sync_audit.as_posix(),
                            "last_sync_status": "completed",
                        },
                        "vercel": {
                            "project_name": "demo-project-prod",
                            "project_url": "https://vercel.com/profit-corp/demo-project-prod",
                            "team_scope": "profit-corp",
                            "env_contract_path": vercel_env.as_posix(),
                            "env_audit_path": vercel_env_audit.as_posix(),
                            "deploy_status": "ready",
                            "deploy_url": "https://demo-project.vercel.app",
                            "deploy_evidence_path": vercel_deploy.as_posix(),
                            "deploy_audit_path": vercel_deploy_audit.as_posix(),
                        },
                    },
                    "protected_change": {
                        "classification": "protected_platform_change",
                        "status": "approved",
                        "evidence_path": protected_inventory.as_posix(),
                    },
                    "platform_justification": {
                        "status": "approved",
                        "artifact_path": justification.as_posix(),
                        "governance_action_id": "gov-approval-001",
                    },
                    "artifacts": {
                        "final_review_path": final_review.as_posix(),
                    },
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
                    design_event,
                    development_event,
                    testing_event,
                    git_event,
                    release_event,
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
                f"- Final handoff: {final_ref}\n"
                f"- GitHub repository mode: attach\n"
                f"- GitHub repository name: profit-corp/demo-project\n"
                f"- GitHub repository URL: https://github.com/profit-corp/demo-project.git\n"
                f"- GitHub default branch: main\n"
                f"- GitHub synced commit: abc1234\n"
                f"- GitHub sync evidence path: {github_sync.as_posix()}\n"
                f"- GitHub sync audit path: {github_sync_audit.as_posix()}\n"
                f"- Vercel project name: demo-project-prod\n"
                f"- Vercel project URL: https://vercel.com/profit-corp/demo-project-prod\n"
                f"- Vercel env contract path: {vercel_env.as_posix()}\n"
                f"- Vercel env audit path: {vercel_env_audit.as_posix()}\n"
                f"- Vercel deploy status: ready\n"
                f"- Vercel deploy URL: https://demo-project.vercel.app\n"
                f"- Vercel deploy evidence path: {vercel_deploy.as_posix()}\n"
                f"- Vercel deploy audit path: {vercel_deploy_audit.as_posix()}\n"
                f"- Protected change classification: protected_platform_change\n"
                f"- Protected change evidence: {protected_inventory.as_posix()}\n"
                f"- Platform justification status: approved\n"
                f"- Platform justification artifact: {justification.as_posix()}\n"
                f"- Governance action: gov-approval-001\n"
                f"- Blocked prerequisite evidence: {downstream.as_posix()}\n"
                "## Specialist Delivery Stages\n"
                f"- design: status=`ready` artifact=`{design_handoff}` evidence=`{design_evidence}`\n"
                f"- development: status=`ready` artifact=`{development_handoff}` evidence=`{development_evidence}`\n"
                f"- testing: status=`ready` artifact=`{testing_handoff}` evidence=`{testing_evidence}`\n"
                f"- git_versioning: status=`ready` artifact=`{git_handoff}` evidence=`{git_evidence}`\n"
                f"- release_readiness: status=`ready` artifact=`{release_handoff}` evidence=`{release_evidence}`\n"
                f"- Final operator review: {final_review.as_posix()}\n",
            )

            result = self.run_validator(approved_project)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("validated approved delivery pipeline", result.stdout)
            self.assertIn("handoff", result.stdout)

    def test_validator_accepts_resolved_block_history_when_current_handoff_truth_exists(self) -> None:
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
            github_sync = workspace / ".hermes" / "github-sync.json"
            vercel_env = workspace / ".hermes" / "vercel-env-contract.json"
            vercel_deploy = workspace / ".hermes" / "vercel-deploy.json"
            final_review = approved_project / "FINAL_OPERATOR_REVIEW.md"
            status_path = approved_project / "DELIVERY_PIPELINE_STATUS.md"
            self.write_text(final_delivery, "# Final delivery\n\n## 1) End-to-end Summary\n")
            self.write_json(manifest, {"run_id": "run-1"})
            self.write_json(conformance, {"ok": True})
            self.write_json(github_sync, {"ok": True})
            self.write_json(vercel_env, {"ok": True})
            self.write_json(vercel_deploy, {"ok": True})
            self.write_text(final_review, "# Final Operator Review\n\n## Credentialed Delivery Actions\nGitHub Sync Evidence Path: {}\nVercel Deploy Status: ready\n## Specialist Delivery Stages\nClaude Code transcript recorded\n".format(github_sync.as_posix()))
            design_handoff, design_evidence, design_event = self.write_specialist_stage_fixture(
                workspace, stage_key="design", stage_label="design", role="design-specialist"
            )
            development_handoff, development_evidence, development_event = self.write_specialist_stage_fixture(
                workspace, stage_key="development", stage_label="development", role="development-specialist"
            )
            testing_handoff, testing_evidence, testing_event = self.write_specialist_stage_fixture(
                workspace,
                stage_key="testing",
                stage_label="testing",
                role="testing-specialist",
                verification_evidence=[
                    (workspace / ".hermes" / "testing-workspace-changes.json").as_posix(),
                    (workspace / ".hermes" / "testing-claude-code.txt").as_posix(),
                ],
            )
            git_handoff, git_evidence, git_event = self.write_specialist_stage_fixture(
                workspace, stage_key="git_versioning", stage_label="git versioning", role="git-versioning-specialist"
            )
            release_handoff, release_evidence, release_event = self.write_specialist_stage_fixture(
                workspace,
                stage_key="release_readiness",
                stage_label="release readiness",
                role="release-readiness-specialist",
                verification_evidence=[
                    (workspace / ".hermes" / "release_readiness-workspace-changes.json").as_posix(),
                    (workspace / ".hermes" / "release_readiness-claude-code.txt").as_posix(),
                ],
            )

            final_ref = final_delivery.as_posix()
            self.write_json(
                approved_project / "APPROVED_PROJECT.json",
                {
                    "pipeline": {
                        "stage": "handoff",
                        "status": "completed",
                        "workspace_path": workspace.as_posix(),
                        "resume_from_stage": "",
                        "final_handoff_path": final_ref,
                    },
                    "artifacts": {
                        "final_review_path": final_review.as_posix(),
                    },
                    "final_handoff": {"path": final_ref, "link": final_ref},
                    "workspace_path": workspace.as_posix(),
                    "conformance_evidence_path": conformance.as_posix(),
                    "phase9_delivery_run_manifest_path": manifest.as_posix(),
                    "latest_blocked_prerequisite": {
                        "path": vercel_deploy.as_posix(),
                        "status": "resolved",
                        "reason": "vercel_deploy_completed",
                    },
                    "shipping": {
                        "github": {
                            "repository_mode": "attach",
                            "repository_name": "profit-corp/demo-project",
                            "repository_url": "https://github.com/profit-corp/demo-project.git",
                            "default_branch": "main",
                            "synced_commit": "abc1234",
                            "sync_evidence_path": github_sync.as_posix(),
                            "last_sync_status": "completed",
                        },
                        "vercel": {
                            "project_name": "demo-project-prod",
                            "project_url": "https://vercel.com/profit-corp/demo-project-prod",
                            "team_scope": "profit-corp",
                            "env_contract_path": vercel_env.as_posix(),
                            "deploy_status": "ready",
                            "deploy_url": "https://demo-project.vercel.app",
                            "deploy_evidence_path": vercel_deploy.as_posix(),
                        },
                    },
                },
            )
            self.write_text(approved_project / "PROJECT_BRIEF.md", "# Brief\n")
            self.write_jsonl(
                approved_project / "approved-delivery-events.jsonl",
                [
                    {
                        "stage": "vercel_deploy",
                        "status": "blocked",
                        "outcome": "blocked",
                        "block_reason": "vercel_deploy_failed",
                        "evidence_path": vercel_deploy.as_posix(),
                        "workspace_path": workspace.as_posix(),
                    },
                    design_event,
                    development_event,
                    testing_event,
                    git_event,
                    release_event,
                    {
                        "stage": "handoff",
                        "status": "completed",
                        "outcome": "pass",
                        "final_handoff_path": final_ref,
                        "workspace_path": workspace.as_posix(),
                    },
                ],
            )
            self.write_text(
                status_path,
                "# Delivery Pipeline Status\n\n"
                "- Authority: approved-project\n"
                f"- Workspace: {workspace.as_posix()}\n"
                f"- Final handoff: {final_ref}\n"
                "- Final operator review: FINAL_OPERATOR_REVIEW.md\n"
                f"- Blocked prerequisite evidence: {vercel_deploy.as_posix()}\n"
                "## Specialist Delivery Stages\n"
                f"- design: status=`ready` artifact=`{design_handoff}` evidence=`{design_evidence}`\n"
                f"- development: status=`ready` artifact=`{development_handoff}` evidence=`{development_evidence}`\n"
                f"- testing: status=`ready` artifact=`{testing_handoff}` evidence=`{testing_evidence}`\n"
                f"- git_versioning: status=`ready` artifact=`{git_handoff}` evidence=`{git_evidence}`\n"
                f"- release_readiness: status=`ready` artifact=`{release_handoff}` evidence=`{release_evidence}`\n"
                "- Protected change: not available\n"
                "- Platform justification: not available\n"
                "- GitHub repository mode: attach\n"
                "- GitHub repository name: profit-corp/demo-project\n"
                "- GitHub repository URL: https://github.com/profit-corp/demo-project.git\n"
                "- GitHub default branch: main\n"
                f"- GitHub synced commit: abc1234\n"
                f"- GitHub sync evidence path: {github_sync.as_posix()}\n"
                "- Vercel project name: demo-project-prod\n"
                "- Vercel project URL: https://vercel.com/profit-corp/demo-project-prod\n"
                "- Vercel team scope: profit-corp\n"
                f"- Vercel env contract path: {vercel_env.as_posix()}\n"
                f"- Vercel deploy status: ready\n"
                f"- Vercel deploy URL: https://demo-project.vercel.app\n"
                f"- Vercel deploy evidence path: {vercel_deploy.as_posix()}\n",
            )

            result = self.run_validator(approved_project)
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_validator_rejects_completed_current_state_with_stale_blocked_authority_fields(self) -> None:
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
            github_sync = workspace / ".hermes" / "github-sync.json"
            vercel_env = workspace / ".hermes" / "vercel-env-contract.json"
            vercel_deploy = workspace / ".hermes" / "vercel-deploy.json"
            final_review = approved_project / "FINAL_OPERATOR_REVIEW.md"
            status_path = approved_project / "DELIVERY_PIPELINE_STATUS.md"
            self.write_text(final_delivery, "# Final delivery\n\n## 1) End-to-end Summary\n")
            self.write_json(manifest, {"run_id": "run-1"})
            self.write_json(conformance, {"ok": True})
            self.write_json(github_sync, {"ok": True})
            self.write_json(vercel_env, {"ok": True})
            self.write_json(vercel_deploy, {"ok": True})

            final_ref = final_delivery.as_posix()
            self.write_json(
                approved_project / "APPROVED_PROJECT.json",
                {
                    "pipeline": {
                        "stage": "handoff",
                        "status": "completed",
                        "block_reason": "vercel_deploy_failed",
                        "workspace_path": workspace.as_posix(),
                        "resume_from_stage": "",
                        "final_handoff_path": final_ref,
                    },
                    "artifacts": {
                        "final_review_path": final_review.as_posix(),
                    },
                    "final_handoff": {"path": final_ref, "link": final_ref},
                    "workspace_path": workspace.as_posix(),
                    "conformance_evidence_path": conformance.as_posix(),
                    "phase9_delivery_run_manifest_path": manifest.as_posix(),
                    "latest_blocked_prerequisite": {
                        "stage": "vercel_deploy",
                        "path": vercel_deploy.as_posix(),
                        "status": "blocked",
                        "reason": "vercel_deploy_failed",
                    },
                    "shipping": {
                        "github": {
                            "repository_mode": "attach",
                            "repository_name": "profit-corp/demo-project",
                            "repository_url": "https://github.com/profit-corp/demo-project.git",
                            "default_branch": "main",
                            "synced_commit": "abc1234",
                            "sync_evidence_path": github_sync.as_posix(),
                            "last_sync_status": "completed",
                        },
                        "vercel": {
                            "project_name": "demo-project-prod",
                            "project_url": "https://vercel.com/profit-corp/demo-project-prod",
                            "team_scope": "profit-corp",
                            "env_contract_path": vercel_env.as_posix(),
                            "deploy_status": "ready",
                            "deploy_url": "https://demo-project.vercel.app",
                            "deploy_evidence_path": vercel_deploy.as_posix(),
                        },
                    },
                },
            )
            self.write_text(approved_project / "PROJECT_BRIEF.md", "# Brief\n")
            self.write_jsonl(
                approved_project / "approved-delivery-events.jsonl",
                [
                    {
                        "stage": "vercel_deploy",
                        "status": "blocked",
                        "outcome": "blocked",
                        "block_reason": "vercel_deploy_failed",
                        "evidence_path": vercel_deploy.as_posix(),
                        "workspace_path": workspace.as_posix(),
                    },
                    {
                        "stage": "handoff",
                        "status": "completed",
                        "outcome": "pass",
                        "final_handoff_path": final_ref,
                        "workspace_path": workspace.as_posix(),
                    },
                ],
            )
            shared_markdown = (
                "# Delivery Pipeline Status\n\n"
                "- Authority: approved-project\n"
                f"- Workspace: {workspace.as_posix()}\n"
                f"- Final handoff: {final_ref}\n"
                "- Final operator review: FINAL_OPERATOR_REVIEW.md\n"
                f"- Blocked prerequisite evidence: {vercel_deploy.as_posix()}\n"
                "- Protected change: not available\n"
                "- Platform justification: not available\n"
                "- **Current Stage**: `handoff`\n"
                "- **Pipeline Status**: `completed`\n"
                f"- Final Handoff Path: `{final_ref}`\n"
                "## Credentialed Delivery Actions\n"
                f"- GitHub Sync Evidence Path: `{github_sync.as_posix()}`\n"
                f"- Vercel Env Contract Path: `{vercel_env.as_posix()}`\n"
                f"- Vercel Deploy Evidence Path: `{vercel_deploy.as_posix()}`\n"
                "## Final Operator Review\n"
                "## Specialist Delivery Stages\n"
            )
            self.write_text(status_path, shared_markdown)
            self.write_text(final_review, shared_markdown.replace("# Delivery Pipeline Status", "# Final Operator Review"))

            result = self.run_validator(approved_project)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("completed pipeline still carries blocked current-state fields in authority", (result.stdout + result.stderr).lower())

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

    def write_specialist_stage_fixture(
        self,
        workspace: Path,
        *,
        stage_key: str,
        stage_label: str,
        role: str,
        run_id: str = "run-1",
        template_only: bool = False,
        verification_evidence: list[str] | None = None,
    ) -> tuple[str, str, dict]:
        starter_module = load_module(f"start_approved_project_delivery_fixture_{stage_key}", DELIVERY_STARTER)
        config = next(item for item in starter_module.SPECIALIST_STAGE_CONFIGS if item["pipeline_stage"] == stage_key)
        handoff_path = workspace / config["artifact"]
        transcript_path = workspace / ".hermes" / f"{stage_key}-claude-code.txt"
        inventory_path = workspace / ".hermes" / f"{stage_key}-workspace-changes.json"
        handoff_path.parent.mkdir(parents=True, exist_ok=True)
        handoff_path.write_text(f"# {stage_label}\n", encoding="utf-8")
        transcript_path.write_text(f"{stage_label} transcript evidence\n", encoding="utf-8")
        inventory_payload = {
            "touched_paths": ["src/app/page.tsx"],
            "template_only_issues": ["workspace changes only touched src/lib/app-definition.ts"] if template_only else [],
        }
        self.write_json(inventory_path, inventory_payload)

        evidence_links = [transcript_path.as_posix(), inventory_path.as_posix()]
        ui_artifact_path = ""
        ui_artifact_summary_path = ""
        if stage_key in {"design", "development"}:
            record = self.build_minimal_approved_record()
            ui_artifact = starter_module.specialist_ui_artifact_path(workspace)
            ui_artifact.write_text("# UI artifact\n", encoding="utf-8")
            summary = starter_module.build_ui_ux_artifact_summary(
                record,
                ui_artifact,
                pipeline_stage=stage_key,
                role=role,
            )
            ui_summary = starter_module.specialist_ui_artifact_summary_path(workspace)
            self.write_json(ui_summary, summary)
            ui_artifact_path = ui_artifact.as_posix()
            ui_artifact_summary_path = ui_summary.as_posix()
            evidence_links.extend([ui_artifact_path, ui_artifact_summary_path])

        stage_evidence_path = Path(
            starter_module.write_stage_structured_evidence(
                workspace,
                config,
                run_id=run_id,
                handoff_path=handoff_path.as_posix(),
                transcript_path=transcript_path.as_posix(),
                changed_files=["src/app/page.tsx"],
                evidence_links=evidence_links,
                workspace_change_inventory_path=inventory_path.as_posix(),
                ui_artifact_path=ui_artifact_path,
                ui_artifact_summary_path=ui_artifact_summary_path,
                verification_evidence=verification_evidence,
            )
        )
        event = {
            "stage": stage_key,
            "status": "ready",
            "outcome": "pass",
            "artifact": handoff_path.as_posix(),
            "evidence_path": stage_evidence_path.as_posix(),
            "workspace_path": workspace.as_posix(),
            "substance": {
                "template_only": template_only,
                "issues": inventory_payload["template_only_issues"],
            },
        }
        return handoff_path.as_posix(), stage_evidence_path.as_posix(), event


if __name__ == "__main__":
    unittest.main()
