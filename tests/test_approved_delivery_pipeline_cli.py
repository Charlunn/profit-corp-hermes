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

    def test_validator_accepts_project_prefixed_relative_final_review_path(self) -> None:
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
                f"- **Authority Source**: `approved-delivery-events.jsonl`\n"
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
                "This latest view is derived from the append-only approved delivery event stream.\n",
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
                f"- **Authority Source**: `approved-delivery-events.jsonl`\n"
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
                "This latest view is derived from the append-only approved delivery event stream.\n",
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
            self.write_text(workspace / ".hermes" / "stage-handoffs" / "01-design.md", "# design\n")
            self.write_text(workspace / ".hermes" / "stage-handoffs" / "02-development.md", "# development\n")
            self.write_text(workspace / ".hermes" / "stage-handoffs" / "03-testing.md", "# testing\n")
            self.write_text(workspace / ".hermes" / "stage-handoffs" / "04-git-versioning.md", "# git versioning\n")
            self.write_text(workspace / ".hermes" / "stage-handoffs" / "05-release-readiness.md", "# release readiness\n")

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
                    {
                        "stage": "design",
                        "status": "ready",
                        "artifact": (workspace / ".hermes" / "stage-handoffs" / "01-design.md").as_posix(),
                        "evidence_path": (workspace / ".hermes" / "design-claude-code.txt").as_posix(),
                        "workspace_path": workspace.as_posix(),
                    },
                    {
                        "stage": "development",
                        "status": "ready",
                        "artifact": (workspace / ".hermes" / "stage-handoffs" / "02-development.md").as_posix(),
                        "evidence_path": (workspace / ".hermes" / "development-claude-code.txt").as_posix(),
                        "workspace_path": workspace.as_posix(),
                    },
                    {
                        "stage": "testing",
                        "status": "ready",
                        "artifact": (workspace / ".hermes" / "stage-handoffs" / "03-testing.md").as_posix(),
                        "evidence_path": (workspace / ".hermes" / "testing-claude-code.txt").as_posix(),
                        "workspace_path": workspace.as_posix(),
                    },
                    {
                        "stage": "git_versioning",
                        "status": "ready",
                        "artifact": (workspace / ".hermes" / "stage-handoffs" / "04-git-versioning.md").as_posix(),
                        "evidence_path": (workspace / ".hermes" / "git-versioning-claude-code.txt").as_posix(),
                        "workspace_path": workspace.as_posix(),
                    },
                    {
                        "stage": "release_readiness",
                        "status": "ready",
                        "artifact": (workspace / ".hermes" / "stage-handoffs" / "05-release-readiness.md").as_posix(),
                        "evidence_path": (workspace / ".hermes" / "release-readiness-claude-code.txt").as_posix(),
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
                f"- design: status=`ready` artifact=`{(workspace / '.hermes' / 'stage-handoffs' / '01-design.md').as_posix()}` evidence=`{(workspace / '.hermes' / 'design-claude-code.txt').as_posix()}`\n"
                f"- development: status=`ready` artifact=`{(workspace / '.hermes' / 'stage-handoffs' / '02-development.md').as_posix()}` evidence=`{(workspace / '.hermes' / 'development-claude-code.txt').as_posix()}`\n"
                f"- testing: status=`ready` artifact=`{(workspace / '.hermes' / 'stage-handoffs' / '03-testing.md').as_posix()}` evidence=`{(workspace / '.hermes' / 'testing-claude-code.txt').as_posix()}`\n"
                f"- git_versioning: status=`ready` artifact=`{(workspace / '.hermes' / 'stage-handoffs' / '04-git-versioning.md').as_posix()}` evidence=`{(workspace / '.hermes' / 'git-versioning-claude-code.txt').as_posix()}`\n"
                f"- release_readiness: status=`ready` artifact=`{(workspace / '.hermes' / 'stage-handoffs' / '05-release-readiness.md').as_posix()}` evidence=`{(workspace / '.hermes' / 'release-readiness-claude-code.txt').as_posix()}`\n"
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
                    {
                        "stage": "design",
                        "status": "ready",
                        "artifact": (workspace / ".hermes" / "stage-handoffs" / "01-design.md").as_posix(),
                        "evidence_path": (workspace / ".hermes" / "design-claude-code.txt").as_posix(),
                        "workspace_path": workspace.as_posix(),
                    },
                    {
                        "stage": "development",
                        "status": "ready",
                        "artifact": (workspace / ".hermes" / "stage-handoffs" / "02-development.md").as_posix(),
                        "evidence_path": (workspace / ".hermes" / "development-claude-code.txt").as_posix(),
                        "workspace_path": workspace.as_posix(),
                    },
                    {
                        "stage": "testing",
                        "status": "ready",
                        "artifact": (workspace / ".hermes" / "stage-handoffs" / "03-testing.md").as_posix(),
                        "evidence_path": (workspace / ".hermes" / "testing-claude-code.txt").as_posix(),
                        "workspace_path": workspace.as_posix(),
                    },
                    {
                        "stage": "git_versioning",
                        "status": "ready",
                        "artifact": (workspace / ".hermes" / "stage-handoffs" / "04-git-versioning.md").as_posix(),
                        "evidence_path": (workspace / ".hermes" / "git-versioning-claude-code.txt").as_posix(),
                        "workspace_path": workspace.as_posix(),
                    },
                    {
                        "stage": "release_readiness",
                        "status": "ready",
                        "artifact": (workspace / ".hermes" / "stage-handoffs" / "05-release-readiness.md").as_posix(),
                        "evidence_path": (workspace / ".hermes" / "release-readiness-claude-code.txt").as_posix(),
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
            self.write_text(
                status_path,
                "# Delivery Pipeline Status\n\n"
                "- Authority: approved-project\n"
                f"- Workspace: {workspace.as_posix()}\n"
                f"- Final handoff: {final_ref}\n"
                "- Final operator review: FINAL_OPERATOR_REVIEW.md\n"
                f"- Blocked prerequisite evidence: {vercel_deploy.as_posix()}\n"
                "## Specialist Delivery Stages\n"
                f"- design: status=`ready` artifact=`{(workspace / '.hermes' / 'stage-handoffs' / '01-design.md').as_posix()}` evidence=`{(workspace / '.hermes' / 'design-claude-code.txt').as_posix()}`\n"
                f"- development: status=`ready` artifact=`{(workspace / '.hermes' / 'stage-handoffs' / '02-development.md').as_posix()}` evidence=`{(workspace / '.hermes' / 'development-claude-code.txt').as_posix()}`\n"
                f"- testing: status=`ready` artifact=`{(workspace / '.hermes' / 'stage-handoffs' / '03-testing.md').as_posix()}` evidence=`{(workspace / '.hermes' / 'testing-claude-code.txt').as_posix()}`\n"
                f"- git_versioning: status=`ready` artifact=`{(workspace / '.hermes' / 'stage-handoffs' / '04-git-versioning.md').as_posix()}` evidence=`{(workspace / '.hermes' / 'git-versioning-claude-code.txt').as_posix()}`\n"
                f"- release_readiness: status=`ready` artifact=`{(workspace / '.hermes' / 'stage-handoffs' / '05-release-readiness.md').as_posix()}` evidence=`{(workspace / '.hermes' / 'release-readiness-claude-code.txt').as_posix()}`\n"
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
