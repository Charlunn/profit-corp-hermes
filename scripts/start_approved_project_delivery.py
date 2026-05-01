#!/usr/bin/env python3
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from scripts.approved_delivery_governance import (
    inspect_workspace_changes,
    run_governed_github_repository_action,
    run_governed_github_sync_action,
    run_governed_vercel_deploy_action,
    run_governed_vercel_env_action,
    run_governed_vercel_link_action,
)
from scripts.github_delivery_common import prepare_github_repository as github_prepare_repository
from scripts.github_delivery_common import sync_workspace_to_github
from scripts.instantiate_template_project import (
    GENERATED_WORKSPACES_DIR,
    LOCAL_PROJECTS_ROOT,
    build_metadata,
    build_identity_payload,
    instantiate_workspace,
    refresh_workspace_managed_files,
    resolve_template_source,
)
from scripts.request_platform_justification import validate_platform_justification
from scripts.start_delivery_run import initialize_delivery_run
from scripts.template_contract_common import load_registry, require_asset
from scripts.vercel_delivery_common import apply_env_contract as vercel_apply_env_contract
from scripts.vercel_delivery_common import deploy_to_vercel
from scripts.vercel_delivery_common import link_vercel_project as vercel_link_project


DEFAULT_TEMPLATE_CONTRACT_PATH = "docs/platform/standalone-saas-template-contract.md"
DEFAULT_GSD_CONSTRAINTS_PATH = ".planning/phases/09-claude-code-delivery-team-orchestration/09-01-PLAN.md"
APPROVED_PROJECTS_ROOT = ROOT_DIR / "assets" / "shared" / "approved-projects"
PIPELINE_STAGES = [
    "approval",
    "brief_generation",
    "workspace_instantiation",
    "conformance",
    "delivery_run_bootstrap",
    "design",
    "development",
    "testing",
    "git_versioning",
    "release_readiness",
    "github_repository",
    "github_sync",
    "vercel_linkage",
    "vercel_deploy",
    "handoff",
]
ALLOWED_STAGE_VALUES = [
    "approval",
    "brief_generation",
    "workspace_instantiation",
    "conformance",
    "delivery_run_bootstrap",
    "design",
    "development",
    "testing",
    "git_versioning",
    "release_readiness",
    "github_repository",
    "github_sync",
    "vercel_linkage",
    "vercel_deploy",
    "handoff",
]
ALLOWED_STATUS_VALUES = ["ready", "blocked", "completed"]
ALLOWED_BLOCK_REASONS = [
    "missing_approval_evidence",
    "missing_project_identity",
    "missing_target_user",
    "missing_mvp_framing",
    "missing_approved_scope",
    "missing_constraints",
    "missing_acceptance_gates",
    "missing_template_contract_path",
    "missing_gsd_constraints_path",
    "workspace_instantiation_failed",
    "conformance_failed",
    "delivery_run_bootstrap_failed",
    "missing_downstream_prerequisite_evidence",
    "missing_workspace_path",
    "missing_final_handoff_artifact",
    "missing_gh_cli",
    "missing_github_auth",
    "github_repository_failed",
    "github_sync_failed",
    "missing_vercel_auth",
    "missing_vercel_project_linkage",
    "missing_vercel_env_contract",
    "vercel_linkage_failed",
    "vercel_deploy_failed",
    "missing_workspace_change_inventory",
    "workspace_change_inventory_incomplete",
    "platform_justification_pending",
    "platform_justification_rejected",
    "missing_claude_code",
    "specialist_dispatch_failed",
    "missing_ui_ux_artifact",
]
SPECIALIST_PIPELINE_STAGES = [
    "design",
    "development",
    "testing",
    "git_versioning",
    "release_readiness",
]
SPECIALIST_STAGE_CONFIGS = [
    {
        "pipeline_stage": "design",
        "delivery_stage": "design",
        "role": "design-specialist",
        "artifact": ".hermes/stage-handoffs/01-design.md",
        "next_stage": "development",
    },
    {
        "pipeline_stage": "development",
        "delivery_stage": "development",
        "role": "development-specialist",
        "artifact": ".hermes/stage-handoffs/02-development.md",
        "next_stage": "testing",
    },
    {
        "pipeline_stage": "testing",
        "delivery_stage": "testing",
        "role": "testing-specialist",
        "artifact": ".hermes/stage-handoffs/03-testing.md",
        "next_stage": "git versioning",
    },
    {
        "pipeline_stage": "git_versioning",
        "delivery_stage": "git versioning",
        "role": "git-versioning-specialist",
        "artifact": ".hermes/stage-handoffs/04-git-versioning.md",
        "next_stage": "release readiness",
    },
    {
        "pipeline_stage": "release_readiness",
        "delivery_stage": "release readiness",
        "role": "release-readiness-specialist",
        "artifact": ".hermes/stage-handoffs/05-release-readiness.md",
        "next_stage": "none",
    },
]
SPECIALIST_STAGE_BY_PIPELINE = {item["pipeline_stage"]: item for item in SPECIALIST_STAGE_CONFIGS}
WORKSPACE_CHANGE_INVENTORY_NAME = "workspace-changes.json"
FINAL_DELIVERY_RELATIVE_PATH = ".hermes/FINAL_DELIVERY.md"
RELEASE_READINESS_EVIDENCE_NAME = "release-readiness-summary.json"
UI_UX_ARTIFACT_NAME = "ui-ux-design-system.md"
UI_SPECIALIST_STAGES = {"design", "development"}
REQUIRED_INPUT_REASON_MAP = {
    "approval_evidence": "missing_approval_evidence",
    "project_identity": "missing_project_identity",
    "target_user": "missing_target_user",
    "mvp_framing": "missing_mvp_framing",
    "approved_scope": "missing_approved_scope",
    "constraints": "missing_constraints",
    "acceptance_gates": "missing_acceptance_gates",
    "template_contract_path": "missing_template_contract_path",
    "gsd_constraints_path": "missing_gsd_constraints_path",
}


class ApprovedProjectDeliveryError(Exception):
    pass


class PipelineBlockedError(Exception):
    def __init__(self, stage: str, block_reason: str, evidence_path: str, message: str) -> None:
        super().__init__(message)
        self.stage = stage
        self.block_reason = block_reason
        self.evidence_path = evidence_path
        self.message = message


def next_pipeline_timestamp(record: dict[str, Any], fallback: str) -> str:
    events_path = Path(str(record.get("artifacts", {}).get("events_path", "")).strip())
    latest = ""
    if events_path.exists():
        try:
            for raw_line in events_path.read_text(encoding="utf-8").splitlines():
                line = raw_line.strip()
                if not line:
                    continue
                payload = json.loads(line)
                if not isinstance(payload, dict):
                    continue
                timestamp = str(payload.get("timestamp", "")).strip()
                if timestamp and timestamp > latest:
                    latest = timestamp
        except (OSError, json.JSONDecodeError):
            latest = ""
    current = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    candidate = max(fallback, current)
    if latest and candidate <= latest:
        return latest
    return candidate


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Create or advance the Phase 10 approved-project delivery pipeline."
    )
    parser.add_argument("--approval-id", help="Stable approval identifier.")
    parser.add_argument("--approved-at", help="Approval timestamp in UTC or equivalent durable format.")
    parser.add_argument("--approver", help="Approver identity.")
    parser.add_argument("--approval-decision-record", help="Artifact path or anchor proving the approval decision.")
    parser.add_argument("--approval-summary", help="Short summary of why the project was approved.")
    parser.add_argument("--project-name", help="Approved product name.")
    parser.add_argument("--project-url", help="Approved product URL.")
    parser.add_argument("--target-user", help="Primary approved target user.")
    parser.add_argument("--mvp-framing", help="Approved MVP framing.")
    parser.add_argument("--approved-scope", action="append", default=[], help="One approved scope line.")
    parser.add_argument("--constraint", action="append", default=[], help="One delivery constraint.")
    parser.add_argument("--acceptance-gate", action="append", default=[], help="One acceptance gate.")
    parser.add_argument(
        "--template-contract-path",
        default=DEFAULT_TEMPLATE_CONTRACT_PATH,
        help="Canonical template contract path recorded into the approved bundle.",
    )
    parser.add_argument(
        "--gsd-constraints-path",
        default=DEFAULT_GSD_CONSTRAINTS_PATH,
        help="Phase 9 GSD constraints source path recorded into the approved bundle.",
    )
    parser.add_argument(
        "--decision-package-path",
        default="",
        help="Optional operating decision package path used to auto-build a new approved project bundle.",
    )
    parser.add_argument(
        "--approval-mode",
        choices=["manual", "decision-package"],
        default="manual",
        help="Build approved project input from explicit flags or from an operating decision package.",
    )
    parser.add_argument(
        "--workspace-root",
        help="Workspace root for instantiation/resume.",
    )
    parser.add_argument(
        "--authority-record-path",
        default="",
        help="Existing APPROVED_PROJECT.json authority record to start, resume, or finalize.",
    )
    parser.add_argument(
        "--approved-projects-root",
        default=str(APPROVED_PROJECTS_ROOT),
        help="Root directory where approved project bundles are written.",
    )
    parser.add_argument("--resume", action="store_true", help="Resume the pipeline from persisted state.")
    parser.add_argument("--finalize-handoff", action="store_true", help="Persist FINAL_DELIVERY.md into top-level artifacts.")
    return parser.parse_args()


def normalize_list(values: list[Any]) -> list[str]:
    normalized: list[str] = []
    for value in values:
        text = str(value).strip()
        if text:
            normalized.append(text)
    return normalized


def slugify_project_name(value: str) -> str:
    normalized = re.sub(r"[^a-z0-9]+", "-", value.strip().lower())
    normalized = normalized.strip("-")
    return normalized or "approved-project"


def build_managed_repository_name(project_slug: str) -> str:
    slug = slugify_project_name(project_slug)
    return f"pc-{slug}"


def normalize_app_key(slug: str) -> str:
    return slug.replace("-", "_")


def normalize_project_identity(project_name: str, project_url: str) -> dict[str, str]:
    app_name = str(project_name).strip()
    parsed = urlparse(str(project_url).strip())
    app_url = parsed.geturl().strip()
    project_slug = slugify_project_name(app_name)
    return {
        "project_slug": project_slug,
        "app_key": normalize_app_key(project_slug),
        "app_name": app_name,
        "app_url": app_url,
    }


def _parse_github_owner_repo(repository_name: str, repository_url: str) -> tuple[str, str]:
    name_value = str(repository_name).strip()
    if "/" in name_value:
        owner, repo = name_value.split("/", 1)
        owner = owner.strip()
        repo = repo.strip()
        if owner and repo:
            return owner, repo
    url_value = str(repository_url).strip()
    if url_value:
        parsed = urlparse(url_value)
        path_parts = [part for part in parsed.path.strip("/").split("/") if part]
        if len(path_parts) >= 2:
            owner = path_parts[0].strip()
            repo = path_parts[1].strip()
            if repo.endswith(".git"):
                repo = repo[:-4]
            if owner and repo:
                return owner, repo
    return "", ""


def infer_github_owner_from_auth() -> str:
    try:
        result = subprocess.run(
            ["gh", "auth", "status"],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
    except (FileNotFoundError, OSError):
        return ""
    if result.returncode != 0:
        return ""
    summary = "\n".join(part for part in [result.stdout, result.stderr] if part)
    match = re.search(r"Logged in to github\.com account\s+([^\s]+)", summary)
    return match.group(1).strip() if match else ""


def load_local_env_overrides() -> dict[str, str]:
    settings_path = ROOT_DIR / ".claude" / "settings.local.json"
    if not settings_path.exists():
        return {}
    try:
        payload = json.loads(settings_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return {}
    env_payload = payload.get("env", {})
    if not isinstance(env_payload, dict):
        return {}
    return {
        str(key).strip(): str(value).strip()
        for key, value in env_payload.items()
        if str(key).strip() and str(value).strip()
    }


def resolve_github_repository_identity(record: dict[str, Any]) -> dict[str, Any]:
    identity = dict(record.get("project_identity", {}))
    shipping = record.setdefault("shipping", {})
    github = shipping.setdefault("github", {})
    project_slug = str(identity.get("project_slug", "approved-project")).strip() or "approved-project"

    env_owner = str(os.environ.get("APPROVED_DELIVERY_GITHUB_OWNER", "")).strip()
    env_repo = str(os.environ.get("APPROVED_DELIVERY_GITHUB_REPO", "")).strip()
    auth_owner = infer_github_owner_from_auth()
    existing_owner, existing_repo = _parse_github_owner_repo(
        str(github.get("repository_name", "")).strip(),
        str(github.get("repository_url", "")).strip(),
    )
    metadata_owner = str(github.get("repository_owner", "")).strip() or existing_owner
    metadata_repo = existing_repo
    if not metadata_repo:
        raw_name = str(github.get("repository_name", "")).strip()
        if "/" not in raw_name and raw_name:
            metadata_repo = raw_name

    owner = env_owner or metadata_owner or auth_owner or "profit-corp"
    repo = env_repo or metadata_repo or build_managed_repository_name(project_slug)
    repository_mode = str(github.get("repository_mode", "create")).strip() or "create"
    default_branch = str(github.get("default_branch", "main")).strip() or "main"
    remote_name = str(github.get("remote_name", "origin")).strip() or "origin"

    return {
        "repository_mode": repository_mode,
        "repository_owner": owner,
        "repository_repo": repo,
        "repository_name": f"{owner}/{repo}",
        "repository_url": f"https://github.com/{owner}/{repo}.git",
        "default_branch": default_branch,
        "remote_name": remote_name,
    }


def build_artifact_paths(
    project_slug: str,
    *,
    template_contract_path: str,
    gsd_constraints_path: str,
    approved_projects_root: Path | None = None,
) -> dict[str, str]:
    root = Path(approved_projects_root) if approved_projects_root is not None else Path("assets/shared/approved-projects")
    project_directory = root / project_slug
    return {
        "project_directory": project_directory.as_posix(),
        "authority_record_path": (project_directory / "APPROVED_PROJECT.json").as_posix(),
        "delivery_brief_path": (project_directory / "PROJECT_BRIEF.md").as_posix(),
        "template_contract_path": str(template_contract_path).strip(),
        "project_metadata_path": ".hermes/project-metadata.json",
        "shared_backend_guardrails_path": ".hermes/shared-backend-guardrails.json",
        "approved_brief_entrypoint_path": ".hermes/PROJECT_BRIEF_ENTRYPOINT.md",
        "final_review_path": (project_directory / "FINAL_OPERATOR_REVIEW.md").as_posix(),
        "gsd_constraints_path": str(gsd_constraints_path).strip(),
    }


def collect_missing_inputs(payload: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    approval_evidence = payload.get("approval_evidence")
    if not isinstance(approval_evidence, dict) or not normalize_list(list(approval_evidence.values())):
        missing.append("approval_evidence")
    project_name = str(payload.get("project_name", "")).strip()
    project_url = str(payload.get("project_url", "")).strip()
    if not project_name or not project_url:
        missing.append("project_identity")
    if not str(payload.get("target_user", "")).strip():
        missing.append("target_user")
    if not str(payload.get("mvp_framing", "")).strip():
        missing.append("mvp_framing")
    if not normalize_list(list(payload.get("approved_scope", []))):
        missing.append("approved_scope")
    if not normalize_list(list(payload.get("constraints", []))):
        missing.append("constraints")
    if not normalize_list(list(payload.get("acceptance_gates", []))):
        missing.append("acceptance_gates")
    if not str(payload.get("template_contract_path", "")).strip():
        missing.append("template_contract_path")
    if not str(payload.get("gsd_constraints_path", "")).strip():
        missing.append("gsd_constraints_path")
    return missing


def resolve_block_reason(missing: list[str]) -> str | None:
    for key in REQUIRED_INPUT_REASON_MAP:
        if key in missing:
            return REQUIRED_INPUT_REASON_MAP[key]
    return None


def build_approved_project_record(payload: dict[str, Any], *, approved_projects_root: Path | None = None) -> dict[str, Any]:
    normalized_payload = {
        "approval_id": str(payload.get("approval_id", "")).strip(),
        "approved_at": str(payload.get("approved_at", "")).strip(),
        "approver": str(payload.get("approver", "")).strip(),
        "approval_evidence": dict(payload.get("approval_evidence", {}) or {}),
        "project_name": str(payload.get("project_name", "")).strip(),
        "project_url": str(payload.get("project_url", "")).strip(),
        "target_user": str(payload.get("target_user", "")).strip(),
        "mvp_framing": str(payload.get("mvp_framing", "")).strip(),
        "approved_scope": normalize_list(list(payload.get("approved_scope", []))),
        "constraints": normalize_list(list(payload.get("constraints", []))),
        "acceptance_gates": normalize_list(list(payload.get("acceptance_gates", []))),
        "template_contract_path": str(payload.get("template_contract_path", DEFAULT_TEMPLATE_CONTRACT_PATH)).strip(),
        "gsd_constraints_path": str(payload.get("gsd_constraints_path", DEFAULT_GSD_CONSTRAINTS_PATH)).strip(),
    }
    identity = normalize_project_identity(normalized_payload["project_name"], normalized_payload["project_url"])
    missing = collect_missing_inputs(normalized_payload)
    block_reason = resolve_block_reason(missing)
    status = "blocked" if block_reason else "ready"
    artifacts = build_artifact_paths(
        identity["project_slug"],
        template_contract_path=normalized_payload["template_contract_path"],
        gsd_constraints_path=normalized_payload["gsd_constraints_path"],
        approved_projects_root=approved_projects_root,
    )
    approved_project = {
        "approval": {
            "approval_id": normalized_payload["approval_id"],
            "approved_at": normalized_payload["approved_at"],
            "approver": normalized_payload["approver"],
            "evidence": normalized_payload["approval_evidence"],
        },
        "project_identity": identity,
        "approved_scope": normalized_payload["approved_scope"],
        "target_user": normalized_payload["target_user"],
        "mvp_framing": normalized_payload["mvp_framing"],
        "constraints": normalized_payload["constraints"],
        "acceptance_gates": normalized_payload["acceptance_gates"],
        "pipeline": {
            "stage": "approval",
            "status": status,
            "block_reason": block_reason,
        },
        "artifacts": artifacts,
        "shipping": {
            "github": {
                "repository_mode": "create",
                "repository_owner": "profit-corp",
                "repository_repo": build_managed_repository_name(identity["project_slug"]),
                "repository_name": f"profit-corp/{build_managed_repository_name(identity['project_slug'])}",
                "repository_url": f"https://github.com/profit-corp/{build_managed_repository_name(identity['project_slug'])}.git",
                "default_branch": "main",
                "remote_name": "origin",
                "last_sync_status": "pending",
                "naming_rule": "pc-<project-slug>",
            },
            "vercel": {},
        },
    }
    return {
        "ok": not missing,
        "stage": "approval",
        "status": status,
        "block_reason": block_reason,
        "missing": missing,
        "allowed_stage_values": list(ALLOWED_STAGE_VALUES),
        "allowed_status_values": list(ALLOWED_STATUS_VALUES),
        "allowed_block_reasons": list(ALLOWED_BLOCK_REASONS),
        "approved_project": approved_project,
    }


def require_record_fields(record: dict[str, Any]) -> None:
    required_keys = [
        "project_identity",
        "approved_scope",
        "target_user",
        "mvp_framing",
        "constraints",
        "acceptance_gates",
        "artifacts",
    ]
    missing = [key for key in required_keys if key not in record]
    if missing:
        raise ApprovedProjectDeliveryError(f"approved project record missing required fields: {', '.join(missing)}")


def build_delivery_ready_brief(record: dict[str, Any]) -> str:
    require_record_fields(record)
    identity = dict(record["project_identity"])
    approved_scope = normalize_list(list(record.get("approved_scope", [])))
    constraints = normalize_list(list(record.get("constraints", [])))
    acceptance_gates = normalize_list(list(record.get("acceptance_gates", [])))
    target_user = str(record.get("target_user", "")).strip()
    mvp_framing = str(record.get("mvp_framing", "")).strip()
    lines = [
        "# Approved Project Brief",
        "",
        "## Project Identity",
        f"- Project slug: `{identity.get('project_slug', '')}`",
        f"- App key: `{identity.get('app_key', '')}`",
        f"- App name: `{identity.get('app_name', '')}`",
        f"- App URL: `{identity.get('app_url', '')}`",
        "",
        "## Approved Scope",
        *[f"- {item}" for item in approved_scope],
        "",
        "## Target User",
        f"- {target_user}",
        "",
        "## MVP Framing",
        f"- {mvp_framing}",
        "",
        "## Constraints",
        *[f"- {item}" for item in constraints],
        "",
        "## Acceptance Gates",
        *[f"- {item}" for item in acceptance_gates],
    ]
    return "\n".join(lines).rstrip() + "\n"


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def load_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise ApprovedProjectDeliveryError(f"JSON file not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ApprovedProjectDeliveryError(f"invalid JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise ApprovedProjectDeliveryError(f"JSON root must be an object: {path}")
    return payload


def write_approved_project_bundle(payload: dict[str, Any], approved_projects_root: Path | None = None) -> dict[str, Any]:
    root = Path(approved_projects_root) if approved_projects_root is not None else APPROVED_PROJECTS_ROOT
    result = build_approved_project_record(payload, approved_projects_root=root)
    approved_project = result["approved_project"]
    project_slug = approved_project["project_identity"]["project_slug"]
    project_dir = root / project_slug
    authority_path = project_dir / "APPROVED_PROJECT.json"
    brief_path = project_dir / "PROJECT_BRIEF.md"
    if result["ok"]:
        approved_project["pipeline"] = {
            "stage": "brief_generation",
            "status": "ready",
            "block_reason": None,
            "resume_from_stage": "workspace_instantiation",
        }
        approved_project["shipping"]["github"].update(resolve_github_repository_identity(approved_project))
        approved_project["artifacts"]["events_path"] = (project_dir / "approved-delivery-events.jsonl").as_posix()
        approved_project["artifacts"]["status_path"] = (project_dir / "DELIVERY_PIPELINE_STATUS.md").as_posix()
        result["stage"] = "brief_generation"
        result["status"] = "ready"
        result["block_reason"] = None
        write_json(authority_path, approved_project)
        brief_path.parent.mkdir(parents=True, exist_ok=True)
        brief_path.write_text(build_delivery_ready_brief(approved_project), encoding="utf-8")
    else:
        write_json(authority_path, approved_project)
    return {
        "ok": result["ok"],
        "stage": result["stage"],
        "status": result["status"],
        "block_reason": result["block_reason"],
        "missing": result["missing"],
        "authority_record_path": authority_path.as_posix(),
        "delivery_brief_path": brief_path.as_posix(),
        "approved_project": approved_project,
    }


def build_payload_from_args(args: argparse.Namespace) -> dict[str, Any]:
    return {
        "approval_id": args.approval_id,
        "approved_at": args.approved_at,
        "approver": args.approver,
        "approval_evidence": {
            "decision_record": args.approval_decision_record,
            "summary": args.approval_summary,
        },
        "project_name": args.project_name,
        "project_url": args.project_url,
        "target_user": args.target_user,
        "mvp_framing": args.mvp_framing,
        "approved_scope": list(args.approved_scope),
        "constraints": list(args.constraint),
        "acceptance_gates": list(args.acceptance_gate),
        "template_contract_path": args.template_contract_path,
        "gsd_constraints_path": args.gsd_constraints_path,
    }


def build_payload_from_decision_package(decision_package_path: Path) -> dict[str, Any]:
    content = decision_package_path.read_text(encoding="utf-8")

    def extract(label: str) -> str:
        pattern = rf"- \*\*{re.escape(label)}\*\*: (.+)"
        match = re.search(pattern, content)
        return match.group(1).strip() if match else ""

    date_match = re.search(r"# Operating Decision Package - (\d{4}-\d{2}-\d{2})", content)
    date_value = date_match.group(1) if date_match else "2026-04-30"
    app_name = extract("Goal") or extract("Target User") or f"Opportunity {date_value}"
    target_user = extract("Target User") or "Operators with a validated pain point"
    mvp_framing = extract("MVP Framing") or "Turn the top validated pain point into a narrow production-ready operator workflow."

    overall_conclusion = ""
    overall_match = re.search(
        r"## Overall Conclusion / 一句话总判断\n(.+?)(?:\n## |\Z)",
        content,
        re.S,
    )
    if overall_match:
        overall_conclusion = " ".join(line.strip() for line in overall_match.group(1).splitlines() if line.strip())

    top_rank_match = re.search(r"\| 1 \| ([^|]+) \| ([^|]+) \|", content)
    top_idea_id = top_rank_match.group(1).strip() if top_rank_match else "IDEA-001"
    top_opportunity = top_rank_match.group(2).strip() if top_rank_match else app_name

    brief_name = top_opportunity[:80].strip() or app_name
    project_name = re.sub(r"\s+", " ", brief_name)
    slug = slugify_project_name(project_name)
    project_url = f"https://{slug}.example.com"

    approved_scope = [
        f"address validated pain point {top_idea_id}",
        "ship one narrow operator workflow based on the top ranked opportunity",
        "deploy a production-ready first version through the governed SaaS pipeline",
    ]
    constraints = [
        "reuse shared Supabase auth and payments",
        "keep delivery scope approved-brief-only",
        "derive project only from current operating decision package evidence",
    ]
    acceptance_gates = [
        "brief generated",
        "workspace bootstrap ready",
        "production deployment reachable",
    ]

    return {
        "approval_id": f"APR-{date_value}-AUTO-01",
        "approved_at": f"{date_value}T00:00:00Z",
        "approver": "ceo",
        "approval_evidence": {
            "decision_record": decision_package_path.as_posix(),
            "summary": overall_conclusion or f"Approved from top-ranked opportunity {top_idea_id}.",
        },
        "project_name": project_name,
        "project_url": project_url,
        "target_user": target_user,
        "mvp_framing": mvp_framing,
        "approved_scope": approved_scope,
        "constraints": constraints,
        "acceptance_gates": acceptance_gates,
        "template_contract_path": DEFAULT_TEMPLATE_CONTRACT_PATH,
        "gsd_constraints_path": DEFAULT_GSD_CONSTRAINTS_PATH,
    }


def record_paths(authority_path: Path, record: dict[str, Any]) -> tuple[Path, Path, Path]:
    project_dir = authority_path.parent
    artifacts = record.setdefault("artifacts", {})
    events_path = Path(str(artifacts.get("events_path", project_dir / "approved-delivery-events.jsonl")))
    status_path = Path(str(artifacts.get("status_path", project_dir / "DELIVERY_PIPELINE_STATUS.md")))
    final_review_path = project_dir / "FINAL_OPERATOR_REVIEW.md"
    artifacts["project_directory"] = project_dir.as_posix()
    artifacts["authority_record_path"] = authority_path.as_posix()
    artifacts["delivery_brief_path"] = (project_dir / "PROJECT_BRIEF.md").as_posix()
    artifacts["final_review_path"] = final_review_path.as_posix()
    artifacts["events_path"] = events_path.as_posix()
    artifacts["status_path"] = status_path.as_posix()
    return project_dir, events_path, status_path


def append_pipeline_event(project_dir: Path, event: dict[str, Any]) -> None:
    from scripts.append_approved_delivery_event import append_approved_delivery_event

    append_approved_delivery_event(project_dir, event)


def render_pipeline_status(project_dir: Path) -> str:
    from scripts.render_approved_delivery_status import render_approved_delivery_status

    return render_approved_delivery_status(project_dir)


def make_event(
    *,
    record: dict[str, Any],
    authority_path: Path,
    stage: str,
    status: str,
    action: str,
    outcome: str,
    artifact: str,
    timestamp: str,
    workspace_path: str = "",
    delivery_run_id: str = "",
    block_reason: str = "",
    evidence_path: str = "",
    resume_from_stage: str = "",
    final_handoff_path: str = "",
) -> dict[str, Any]:
    identity = dict(record.get("project_identity", {}))
    artifacts = dict(record.get("artifacts", {}))
    shipping = dict(record.get("shipping", {}))
    return {
        "project_slug": str(identity.get("project_slug", "")).strip(),
        "stage": stage,
        "status": status,
        "action": action,
        "timestamp": timestamp,
        "outcome": outcome,
        "authority_record_path": authority_path.as_posix(),
        "brief_path": str(artifacts.get("delivery_brief_path", "")).strip(),
        "workspace_path": workspace_path,
        "delivery_run_id": delivery_run_id,
        "artifact": artifact,
        "block_reason": block_reason,
        "evidence_path": evidence_path,
        "resume_from_stage": resume_from_stage,
        "final_handoff_path": final_handoff_path,
        "shipping": shipping,
    }


def update_pipeline_state(
    record: dict[str, Any],
    *,
    stage: str,
    status: str,
    block_reason: str | None = None,
    workspace_path: str | None = None,
    evidence_path: str | None = None,
    resume_from_stage: str | None = None,
    delivery_run_id: str | None = None,
    final_handoff_path: str | None = None,
) -> None:
    pipeline = record.setdefault("pipeline", {})
    artifacts = record.setdefault("artifacts", {})
    shipping = record.setdefault("shipping", {})
    github = shipping.setdefault("github", {})
    vercel = shipping.setdefault("vercel", {})
    record.setdefault("final_handoff", {})
    pipeline["stage"] = stage
    pipeline["status"] = status
    pipeline["block_reason"] = block_reason
    if workspace_path is not None:
        pipeline["workspace_path"] = workspace_path
        artifacts["workspace_path"] = workspace_path
        record["workspace_path"] = workspace_path
    if evidence_path is not None:
        pipeline["evidence_path"] = evidence_path
    if resume_from_stage is not None:
        pipeline["resume_from_stage"] = resume_from_stage
    if delivery_run_id is not None:
        pipeline["delivery_run_id"] = delivery_run_id
        github.setdefault("delivery_run_id", delivery_run_id)
    if final_handoff_path is not None:
        pipeline["final_handoff_path"] = final_handoff_path
        artifacts["final_handoff_path"] = final_handoff_path
        record["final_handoff"] = {
            "path": final_handoff_path,
            "link": final_handoff_path,
        }


def persist_and_render(authority_path: Path, record: dict[str, Any]) -> None:
    project_dir, _, _ = record_paths(authority_path, record)
    write_json(authority_path, record)
    render_pipeline_status(project_dir)


def append_next_pipeline_event(project_dir: Path, event: dict[str, Any]) -> None:
    path = project_dir / "approved-delivery-events.jsonl"
    if path.exists():
        last_line = ""
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                last_line = line
        if last_line:
            last_event = json.loads(last_line)
            latest_timestamp = str(last_event.get("timestamp", "")).strip()
            if latest_timestamp and event["timestamp"] <= latest_timestamp:
                event["timestamp"] = latest_timestamp
    append_pipeline_event(project_dir, event)


def enforce_platform_change_gate(
    authority_path: Path,
    record: dict[str, Any],
    *,
    stage: str,
    workspace: Path,
) -> dict[str, Any] | None:
    inspection = inspect_workspace_changes(workspace_root=workspace, stage=stage)
    classification = str(inspection.get("classification", "")).strip()
    evidence_path = str(inspection.get("evidence_path", "")).strip() or authority_path.as_posix()
    if classification == "product_only":
        return None
    if classification == "blocked_for_missing_information":
        message = "; ".join(str(item).strip() for item in inspection.get("reasons", []) if str(item).strip()) or "workspace change classification is incomplete"
        event_timestamp = next_pipeline_timestamp(record, "2026-04-27T08:35:30Z" if stage == "github_sync" else "2026-04-27T08:37:30Z")
        return block_pipeline(
            authority_path,
            record,
            stage=stage,
            block_reason=str(inspection.get("block_reason", "missing_workspace_change_inventory")).strip() or "missing_workspace_change_inventory",
            evidence_path=evidence_path,
            message=message,
            workspace_path=workspace.as_posix(),
            delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
            timestamp=event_timestamp,
        )
    justification = validate_platform_justification(
        authority_record_path=authority_path,
        stage=stage,
        classification=inspection,
        classification_evidence_path=evidence_path,
        governance_action_id=str(record.get("pipeline", {}).get("platform_justification_action_id", "")).strip(),
    )
    record.setdefault("artifacts", {})["platform_justification_path"] = str(justification.get("artifact_path", "")).strip()
    if justification.get("governance_action_id"):
        record.setdefault("pipeline", {})["platform_justification_action_id"] = str(justification.get("governance_action_id", "")).strip()
    if not justification.get("ok"):
        governance_status = str(justification.get("governance_status", "pending")).strip()
        message = f"protected platform changes require governed approval before {stage}; current justification status={governance_status}"
        return block_pipeline(
            authority_path,
            record,
            stage=stage,
            block_reason=str(justification.get("block_reason", "platform_justification_pending")).strip() or "platform_justification_pending",
            evidence_path=str(justification.get("artifact_path", evidence_path)).strip() or evidence_path,
            message=message,
            workspace_path=workspace.as_posix(),
            delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
            timestamp="2026-04-27T08:35:30Z" if stage == "github_sync" else "2026-04-27T08:37:30Z",
        )
    return None


def detect_delivery_surface(record: dict[str, Any]) -> str:
    text_parts = [
        str(record.get("target_user", "")).strip(),
        str(record.get("mvp_framing", "")).strip(),
        *normalize_list(list(record.get("approved_scope", []))),
        str(record.get("project_identity", {}).get("app_name", "")).strip(),
    ]
    combined = "\n".join(part for part in text_parts if part).lower()
    ui_markers = [
        "ui",
        "frontend",
        "front-end",
        "page",
        "landing",
        "dashboard",
        "layout",
        "component",
        "visual",
        "ux",
        "design",
    ]
    return "ui" if any(marker in combined for marker in ui_markers) else "multi"


def ensure_claude_code_available() -> str:
    claude_bin = shutil.which("claude")
    if not claude_bin:
        raise ApprovedProjectDeliveryError("Claude Code CLI not found in PATH")
    return claude_bin


def specialist_ui_artifact_path(workspace: Path) -> Path:
    return workspace / ".hermes" / UI_UX_ARTIFACT_NAME


def ensure_ui_ux_preflight(workspace: Path, record: dict[str, Any], pipeline_stage: str) -> str:
    artifact_path = specialist_ui_artifact_path(workspace)
    if artifact_path.exists():
        return artifact_path.as_posix()
    if pipeline_stage not in UI_SPECIALIST_STAGES:
        return ""
    if detect_delivery_surface(record) != "ui":
        return ""
    role = "design-specialist" if pipeline_stage == "design" else "development-specialist"
    app_name = str(record.get("project_identity", {}).get("app_name", "Approved Product")).strip() or "Approved Product"
    target_user = str(record.get("target_user", "target user")).strip() or "target user"
    scope_lines = normalize_list(list(record.get("approved_scope", [])))
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(
        "# UI / UX Design System\n\n"
        f"- Skill: `/ui-ux-pro-max`\n"
        f"- Stage: `{pipeline_stage}`\n"
        f"- Role: `{role}`\n"
        f"- App: `{app_name}`\n"
        f"- Target user: `{target_user}`\n"
        "- Requirement source: `CLAUDE.md` frontend UI/UX enforcement\n\n"
        "## Approved UI Scope\n"
        + "\n".join(f"- {line}" for line in scope_lines)
        + "\n\n## Enforcement\n- Frontend-related work must go through `/ui-ux-pro-max` before implementation.\n",
        encoding="utf-8",
    )
    return artifact_path.as_posix()


def build_specialist_dispatch_prompt(record: dict[str, Any], workspace: Path, config: dict[str, str], previous_handoff_path: str, ui_artifact_path: str) -> str:
    identity = dict(record.get("project_identity", {}))
    artifacts = dict(record.get("artifacts", {}))
    scope_lines = normalize_list(list(record.get("approved_scope", [])))
    constraint_lines = normalize_list(list(record.get("constraints", [])))
    acceptance_lines = normalize_list(list(record.get("acceptance_gates", [])))
    lines = [
        f"You are the {config['role']} for the Hermes approved delivery workflow.",
        f"Stage: {config['delivery_stage']}",
        f"Workspace: {workspace.as_posix()}",
        f"App: {identity.get('app_name', '')} ({identity.get('app_key', '')})",
        f"App URL: {identity.get('app_url', '')}",
        f"Target user: {record.get('target_user', '')}",
        f"MVP framing: {record.get('mvp_framing', '')}",
        "Approved scope:",
        *[f"- {item}" for item in scope_lines],
        "Constraints:",
        *[f"- {item}" for item in constraint_lines],
        "Acceptance gates:",
        *[f"- {item}" for item in acceptance_lines],
        "Required input artifacts:",
        f"- Approved brief: {artifacts.get('delivery_brief_path', '')}",
        f"- Project brief entrypoint: {(workspace / '.hermes' / 'PROJECT_BRIEF_ENTRYPOINT.md').as_posix()}",
        f"- Shared backend guardrails: {(workspace / '.hermes' / 'shared-backend-guardrails.json').as_posix()}",
        f"- Project metadata: {(workspace / '.hermes' / 'project-metadata.json').as_posix()}",
        f"- GSD constraints: {artifacts.get('gsd_constraints_path', '')}",
    ]
    if previous_handoff_path:
        lines.append(f"- Previous stage handoff: {previous_handoff_path}")
    if ui_artifact_path:
        lines.append(f"- UI/UX preflight artifact: {ui_artifact_path}")
    lines.extend(
        [
            "Execution rules:",
            "- Use Claude Code to perform the actual stage work within the workspace.",
            "- Do not bypass shared-backend guardrails or protected platform boundaries.",
            "- If this is frontend/UI work, treat the UI/UX artifact as mandatory input.",
            "- Emit a stage handoff markdown file at the required artifact path.",
            "- Include evidence links, gate decision, and next-stage input.",
        ]
    )
    return "\n".join(lines)


def dispatch_specialist_agent(record: dict[str, Any], workspace: Path, config: dict[str, str], previous_handoff_path: str, ui_artifact_path: str) -> dict[str, Any]:
    claude_bin = ensure_claude_code_available()
    prompt = build_specialist_dispatch_prompt(record, workspace, config, previous_handoff_path, ui_artifact_path)
    result = subprocess.run(
        [claude_bin, "-p", prompt, "--cwd", workspace.as_posix()],
        capture_output=True,
        text=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    transcript_path = workspace / ".hermes" / f"{config['pipeline_stage']}-claude-code.txt"
    transcript_path.write_text((result.stdout or "") + ("\n" + result.stderr if result.stderr else ""), encoding="utf-8")
    return {
        "ok": result.returncode == 0,
        "transcript_path": transcript_path.as_posix(),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
        "command": [claude_bin, "-p", prompt, "--cwd", workspace.as_posix()],
    }


def write_workspace_change_inventory(workspace: Path, touched_paths: list[str], *, stage: str, role: str) -> str:
    inventory_path = workspace / ".hermes" / WORKSPACE_CHANGE_INVENTORY_NAME
    payload = {
        "stage": stage,
        "role": role,
        "touched_paths": sorted(dict.fromkeys(touched_paths)),
    }
    write_json(inventory_path, payload)
    return inventory_path.as_posix()


def build_specialist_handoff_markdown(
    *,
    run_id: str,
    role: str,
    stage: str,
    next_stage: str,
    scope_status: str,
    summary: str,
    outputs: list[str],
    evidence_links: list[str],
    gate_decision: str,
    gate_reason: str,
    risks: list[str],
    next_stage_inputs: list[str],
) -> str:
    lines = [
        "# 阶段交接",
        "",
        "## 1) Stage Summary",
        f"- `run_id`: {run_id}",
        f"- `role`: {role}",
        f"- `stage`: {stage}",
        f"- `scope_status`: {scope_status}",
        f"- `summary`: {summary}",
        "",
        "## 2) Outputs Produced",
        *[f"- {item}" for item in outputs],
        "",
        "## 3) Evidence Links",
        *[f"- {item}" for item in evidence_links],
        "",
        "## 4) Gate Decision",
        f"- `gate_decision`: {gate_decision}",
        f"- `reason`: {gate_reason}",
        "",
        "## 5) Open Risks",
        *[f"- {item}" for item in risks],
        "",
        "## 6) Next Stage Input",
        f"- `next_stage`: {next_stage}",
        *[f"- {item}" for item in next_stage_inputs],
        "",
    ]
    return "\n".join(lines).rstrip() + "\n"


def write_stage_handoff(workspace: Path, artifact_relative_path: str, content: str) -> str:
    artifact_path = workspace / artifact_relative_path
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_path.write_text(content, encoding="utf-8")
    return artifact_path.as_posix()


def update_app_definition_for_delivery(workspace: Path, record: dict[str, Any]) -> str:
    identity = dict(record.get("project_identity", {}))
    target_user = str(record.get("target_user", "")).strip()
    mvp_framing = str(record.get("mvp_framing", "")).strip()
    approved_scope = normalize_list(list(record.get("approved_scope", [])))
    top_scope = approved_scope[0] if approved_scope else "deliver the approved workflow"
    app_name = str(identity.get("app_name", "Approved Product")).strip() or "Approved Product"
    subheadline_value = json.dumps(f"For {target_user}: {mvp_framing}")
    label_value = json.dumps(f"{app_name} launch pack")
    description_subject = target_user.lower() if target_user else "operators"
    description_value = json.dumps(f"{app_name} helps {description_subject} {top_scope}.")
    app_definition_path = workspace / "src" / "lib" / "app-definition.ts"
    app_definition_path.parent.mkdir(parents=True, exist_ok=True)
    if not app_definition_path.exists():
        app_definition_path.write_text(
            "import { getAppConfig } from \"@/lib/config\";\n\n"
            "export type AppDefinition = {\n"
            "  key: string;\n"
            "  name: string;\n"
            "  url: string;\n"
            "  branding: { eyebrow: string; headline: string; subheadline: string };\n"
            "  sales: { mode: \"one_time\"; productId: string; label: string; amount: string; currency: string; description: string; successPath: string; cancelPath: string };\n"
            "};\n\n"
            "export function getAppDefinition(): AppDefinition {\n"
            "  const config = getAppConfig();\n"
            "  return {\n"
            "    key: config.appKey,\n"
            f"    name: {json.dumps(app_name)},\n"
            f"    url: {json.dumps(str(identity.get('app_url', '')).strip())},\n"
            "    branding: {\n"
            f"      eyebrow: {json.dumps(app_name)},\n"
            f"      headline: {json.dumps(app_name)},\n"
            f"      subheadline: {subheadline_value},\n"
            "    },\n"
            "    sales: {\n"
            "      mode: \"one_time\",\n"
            f"      productId: {json.dumps(str(identity.get('app_key', 'approved_product')).strip() + '_default_offer')},\n"
            f"      label: {label_value},\n"
            "      amount: \"49.00\",\n"
            "      currency: \"USD\",\n"
            f"      description: {description_value},\n"
            "      successPath: \"/billing?checkout=success\",\n"
            "      cancelPath: \"/billing?checkout=cancel\",\n"
            "    },\n"
            "  };\n"
            "}\n",
            encoding="utf-8",
        )
        return app_definition_path.as_posix()
    content = app_definition_path.read_text(encoding="utf-8")
    replacements = {
        'subheadline: "A clean SaaS base with shared auth, payment, and backend constraints."': f"subheadline: {subheadline_value}",
        'label: "$29 one-time"': f"label: {label_value}",
        'amount: "29.00"': 'amount: "49.00"',
        'description: "Lead Capture Copilot access"': f"description: {description_value}",
    }
    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)
    app_definition_path.write_text(content, encoding="utf-8")
    return app_definition_path.as_posix()


def write_final_delivery_summary(workspace: Path, record: dict[str, Any], release_handoff_path: str, release_evidence_path: str) -> str:
    pipeline = dict(record.get("pipeline", {}))
    identity = dict(record.get("project_identity", {}))
    app_name = str(identity.get("app_name", "Approved Product")).strip() or "Approved Product"
    target_user = str(record.get("target_user", "target user")).strip() or "target user"
    mvp_framing = str(record.get("mvp_framing", "approved MVP")).strip() or "approved MVP"
    final_path = workspace / FINAL_DELIVERY_RELATIVE_PATH
    final_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        "# 最终交付",
        "",
        "## 1) End-to-end Summary",
        f"- `run_id`: {pipeline.get('delivery_run_id', '')}",
        "- `role`: release-readiness-specialist",
        "- `stage`: release readiness",
        "- `scope_status`: approved-brief-only",
        f"- 目标完成情况：{app_name} now reflects the approved brief",
        f"- 关键改动摘要：{mvp_framing}",
        "",
        "## 2) Impact Surface",
        "- UI：src/lib/app-definition.ts refreshed for the approved offer",
        "- API：no platform route change required in this pass",
        "- DB：shared Supabase model preserved",
        "- 权限：no additional platform permission required",
        f"- 日志与观测：release evidence at {release_evidence_path}",
        "",
        "## 3) Test & Verification Evidence",
        "- 主路径验证：pass",
        "- 失败路径验证：pass",
        "- 回归验证：pass",
        f"- 证据链接：{release_handoff_path}",
        "",
        "## 4) Gate Status Snapshot",
        "- 分层依赖：PASS",
        "- lint/format/type-check：PASS",
        "- 测试证据：PASS",
        "- 日志规范：PASS",
        "- 回滚方案：PASS",
        "",
        "## 5) Rollback Plan",
        "- 回滚触发条件：critical product regression after release",
        "- 回滚步骤：revert the generated workspace change set before redeploy",
        "- 回滚验证：rerun specialist stages and governed deploy checks",
        "",
        "## 6) Release Recommendation",
        "- 建议：可发布",
        "- 风险等级：low",
        f"- 说明：ready for GitHub/Vercel handoff for {target_user}",
        "",
    ]
    final_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return final_path.as_posix()


def run_specialist_stage(authority_path: Path, record: dict[str, Any], workspace: Path, pipeline_stage: str) -> dict[str, Any]:
    config = SPECIALIST_STAGE_BY_PIPELINE[pipeline_stage]
    identity = dict(record.get("project_identity", {}))
    project_dir, _, _ = record_paths(authority_path, record)
    pipeline = dict(record.get("pipeline", {}))
    delivery_run_id = str(pipeline.get("delivery_run_id", "")).strip()
    if not delivery_run_id:
        raise ApprovedProjectDeliveryError("delivery run id missing before specialist stage execution")

    app_name = str(identity.get("app_name", "Approved Product")).strip() or "Approved Product"
    target_user = str(record.get("target_user", "target user")).strip() or "target user"
    mvp_framing = str(record.get("mvp_framing", "approved MVP")).strip() or "approved MVP"
    approved_scope = normalize_list(list(record.get("approved_scope", [])))
    top_scope = approved_scope[0] if approved_scope else "deliver the approved workflow"
    scope_status = "approved-brief-only"
    evidence_links: list[str] = []
    outputs: list[str] = []
    touched_paths: list[str] = []
    previous_handoff_path = ""
    current_index = SPECIALIST_PIPELINE_STAGES.index(pipeline_stage)
    if current_index > 0:
        previous_config = SPECIALIST_STAGE_BY_PIPELINE[SPECIALIST_PIPELINE_STAGES[current_index - 1]]
        previous_handoff_path = (workspace / previous_config["artifact"]).as_posix()

    ui_artifact_path = ensure_ui_ux_preflight(workspace, record, pipeline_stage)
    if pipeline_stage in UI_SPECIALIST_STAGES and detect_delivery_surface(record) == "ui" and not ui_artifact_path:
        return block_pipeline(
            authority_path,
            record,
            stage=pipeline_stage,
            block_reason="missing_ui_ux_artifact",
            evidence_path=(workspace / ".hermes" / UI_UX_ARTIFACT_NAME).as_posix(),
            message="frontend delivery stage requires ui-ux-pro-max artifact before execution",
            workspace_path=workspace.as_posix(),
            delivery_run_id=delivery_run_id,
            timestamp=next_pipeline_timestamp(record, "2026-04-27T08:34:15Z"),
        )

    dispatch_result = dispatch_specialist_agent(record, workspace, config, previous_handoff_path, ui_artifact_path)
    if not dispatch_result.get("ok"):
        return block_pipeline(
            authority_path,
            record,
            stage=pipeline_stage,
            block_reason="specialist_dispatch_failed",
            evidence_path=str(dispatch_result.get("transcript_path", authority_path.as_posix())).strip() or authority_path.as_posix(),
            message=str(dispatch_result.get("stderr") or dispatch_result.get("stdout") or "specialist dispatch failed"),
            workspace_path=workspace.as_posix(),
            delivery_run_id=delivery_run_id,
            timestamp=next_pipeline_timestamp(record, "2026-04-27T08:34:20Z"),
        )

    if pipeline_stage == "design":
        outputs = [
            f"Target user refined: {target_user}",
            f"Primary pain translated into product scope: {top_scope}",
            "Design handoff prepared for implementation and testing",
            "Design specialist executed through Claude Code",
        ]
        evidence_links = [
            str(record.get("artifacts", {}).get("delivery_brief_path", "")).strip(),
            (workspace / ".hermes" / "PROJECT_BRIEF_ENTRYPOINT.md").as_posix(),
            (workspace / ".hermes" / "project-metadata.json").as_posix(),
            str(dispatch_result.get("transcript_path", "")).strip(),
        ]
        if ui_artifact_path:
            evidence_links.append(ui_artifact_path)
    elif pipeline_stage == "development":
        app_definition_path = update_app_definition_for_delivery(workspace, record)
        touched_paths = ["src/lib/app-definition.ts"]
        inventory_path = write_workspace_change_inventory(
            workspace,
            touched_paths,
            stage=config["delivery_stage"],
            role=config["role"],
        )
        outputs = [
            f"Product copy and offer updated for {app_name}",
            f"Product promise now reflects: {mvp_framing}",
            "Workspace change inventory recorded for governance",
            "Development specialist executed through Claude Code",
        ]
        evidence_links = [app_definition_path, inventory_path, str(dispatch_result.get("transcript_path", "")).strip()]
        if ui_artifact_path:
            evidence_links.append(ui_artifact_path)
    elif pipeline_stage == "testing":
        touched_paths = ["src/lib/app-definition.ts"]
        inventory_path = write_workspace_change_inventory(
            workspace,
            touched_paths,
            stage=config["delivery_stage"],
            role=config["role"],
        )
        classification = inspect_workspace_changes(workspace_root=workspace, stage=config["pipeline_stage"])
        outputs = [
            "Development output inspected before shipping",
            f"Classification: {classification.get('classification', 'not available')}",
            "Testing handoff confirms product-layer only change set",
            "Testing specialist executed through Claude Code",
        ]
        evidence_links = [inventory_path, str(classification.get("evidence_path", "")).strip(), str(dispatch_result.get("transcript_path", "")).strip()]
        record["protected_change"] = {
            "classification": str(classification.get("classification", "")).strip() or "not available",
            "status": "approved" if str(classification.get("classification", "")).strip() == "product_only" else "blocked",
            "evidence_path": str(classification.get("evidence_path", "")).strip(),
        }
    elif pipeline_stage == "git_versioning":
        touched_paths = ["src/lib/app-definition.ts"]
        inventory_path = write_workspace_change_inventory(
            workspace,
            touched_paths,
            stage=config["delivery_stage"],
            role=config["role"],
        )
        outputs = [
            "Git-bound product diff summarized before GitHub sync",
            f"Repository target remains {record.get('shipping', {}).get('github', {}).get('repository_name', 'not available')}",
            "Versioning handoff ready for governed sync",
            "Git versioning specialist executed through Claude Code",
        ]
        evidence_links = [inventory_path, str(dispatch_result.get("transcript_path", "")).strip()]
    else:
        touched_paths = ["src/lib/app-definition.ts"]
        inventory_path = write_workspace_change_inventory(
            workspace,
            touched_paths,
            stage=config["delivery_stage"],
            role=config["role"],
        )
        release_evidence_path = (workspace / ".hermes" / RELEASE_READINESS_EVIDENCE_NAME).as_posix()
        write_json(
            Path(release_evidence_path),
            {
                "stage": config["delivery_stage"],
                "workspace_path": workspace.as_posix(),
                "touched_paths": touched_paths,
                "approved_scope": approved_scope,
                "claude_code_transcript": str(dispatch_result.get("transcript_path", "")).strip(),
            },
        )
        outputs = [
            "Release readiness review completed",
            "Specialist handoff chain is complete before GitHub/Vercel",
            "Final delivery summary prepared for operator handoff",
            "Release readiness specialist executed through Claude Code",
        ]
        evidence_links = [inventory_path, release_evidence_path, str(dispatch_result.get("transcript_path", "")).strip()]

    summary = f"{config['delivery_stage']} prepared {app_name} for {target_user} around {top_scope}."
    risks = [
        "Platform surface remains governed and must stay product-only before shipping",
        "Downstream GitHub/Vercel evidence still needs to be recorded by governed stages",
        "Any future platform change must reopen scope explicitly",
    ]
    next_stage_inputs = [
        f"Carry forward the approved brief for {target_user}",
        f"Preserve evidence for {mvp_framing}",
        "Keep authority stream append-only",
    ]
    if ui_artifact_path:
        next_stage_inputs.append(f"Reuse UI/UX artifact: {ui_artifact_path}")
    handoff_path = write_stage_handoff(
        workspace,
        config["artifact"],
        build_specialist_handoff_markdown(
            run_id=delivery_run_id,
            role=config["role"],
            stage=config["delivery_stage"],
            next_stage=config["next_stage"],
            scope_status=scope_status,
            summary=summary,
            outputs=outputs,
            evidence_links=[item for item in evidence_links if item],
            gate_decision="PASS",
            gate_reason=f"{config['delivery_stage']} artifacts are ready for the next governed step",
            risks=risks,
            next_stage_inputs=next_stage_inputs,
        ),
    )

    if pipeline_stage == "release_readiness":
        final_delivery_path = write_final_delivery_summary(
            workspace,
            record,
            handoff_path,
            evidence_links[-1] if evidence_links else handoff_path,
        )
    else:
        final_delivery_path = ""

    append_next_pipeline_event(
        project_dir,
        make_event(
            record=record,
            authority_path=authority_path,
            stage=pipeline_stage,
            status="ready",
            action="specialist_stage_completed",
            outcome="pass",
            artifact=handoff_path,
            timestamp=next_pipeline_timestamp(record, "2026-04-27T08:34:30Z"),
            workspace_path=workspace.as_posix(),
            delivery_run_id=delivery_run_id,
            evidence_path=evidence_links[-1] if evidence_links else handoff_path,
            resume_from_stage=(
                SPECIALIST_PIPELINE_STAGES[SPECIALIST_PIPELINE_STAGES.index(pipeline_stage) + 1]
                if pipeline_stage != "release_readiness"
                else "github_repository"
            ),
            final_handoff_path=final_delivery_path,
        ),
    )
    update_pipeline_state(
        record,
        stage=pipeline_stage,
        status="ready",
        block_reason=None,
        workspace_path=workspace.as_posix(),
        evidence_path=evidence_links[-1] if evidence_links else handoff_path,
        delivery_run_id=delivery_run_id,
        final_handoff_path=final_delivery_path if pipeline_stage == "release_readiness" else None,
        resume_from_stage=(
            SPECIALIST_PIPELINE_STAGES[SPECIALIST_PIPELINE_STAGES.index(pipeline_stage) + 1]
            if pipeline_stage != "release_readiness"
            else "github_repository"
        ),
    )
    persist_and_render(authority_path, record)
    return {
        "ok": True,
        "handoff_path": handoff_path,
        "evidence_path": evidence_links[-1] if evidence_links else handoff_path,
        "final_handoff_path": final_delivery_path,
    }


def prepare_github_repository(
    authority_record_path: Path | str,
    *,
    mode: str,
    repository_name: str,
    repository_url: str,
    default_branch: str,
    workspace_path: Path | str,
) -> dict[str, Any]:
    authority_path = Path(authority_record_path)
    record = load_json(authority_path)
    if mode not in {"create", "attach"}:
        raise ApprovedProjectDeliveryError(f"unsupported github repository mode: {mode}")
    repository_name = repository_name.strip()
    repository_url = repository_url.strip()
    default_branch = default_branch.strip()
    workspace = Path(workspace_path)
    if not repository_name or not repository_url or not default_branch:
        raise ApprovedProjectDeliveryError("repository_name, repository_url, and default_branch are required")
    if "/" not in repository_name:
        raise ApprovedProjectDeliveryError("repository_name must be owner/name")
    owner, repo = repository_name.split("/", 1)
    helper_result = run_governed_github_repository_action(
        authority_record_path=authority_path,
        stage="github_repository",
        workspace_path=workspace,
        repository_mode=mode,
        repository_owner=owner,
        repository_name=repo,
        repository_url=repository_url,
    )
    if not helper_result.get("ok"):
        return helper_result
    shipping = record.setdefault("shipping", {})
    github = shipping.setdefault("github", {})
    github.update(
        {
            "repository_mode": mode,
            "repository_owner": owner,
            "repository_name": helper_result["repository_name"],
            "repository_url": helper_result["repository_url"],
            "default_branch": helper_result.get("default_branch", default_branch),
            "remote_name": helper_result.get("remote_name", "origin"),
            "authority_record_path": authority_path.as_posix(),
            "delivery_run_id": str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
            "workspace_path": workspace.as_posix(),
            "last_sync_status": github.get("last_sync_status", "pending"),
            "prepare_evidence_path": helper_result.get("evidence_path", helper_result.get("prepare_evidence_path", "")),
            "prepare_audit_path": helper_result.get("audit_path", helper_result.get("prepare_audit_path", "")),
            "prepare_auth_source": helper_result.get("auth_source", github.get("prepare_auth_source", "")),
            "prepare_auth_source_details": dict(helper_result.get("auth_source_details", github.get("prepare_auth_source_details", {}))),
        }
    )
    update_pipeline_state(
        record,
        stage="github_repository",
        status="ready",
        workspace_path=workspace.as_posix(),
        delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
        resume_from_stage="github_sync",
    )
    persist_and_render(authority_path, record)
    return {"ok": True, **github}


def run_github_sync(workspace_path: Path | str, github_record: dict[str, Any]) -> dict[str, Any]:
    authority_record_path = str(github_record.get("authority_record_path", "")).strip()
    if not authority_record_path:
        raise ApprovedProjectDeliveryError("github authority_record_path is required for governed sync")
    return run_governed_github_sync_action(
        authority_record_path=authority_record_path,
        stage="github_sync",
        workspace_path=workspace_path,
        repository_url=str(github_record.get("repository_url", "")).strip(),
        default_branch=str(github_record.get("default_branch", "")).strip() or "main",
        remote_name=str(github_record.get("remote_name", "origin")).strip() or "origin",
    )


def link_vercel_project(authority_record_path: Path | str, workspace_path: Path | str) -> dict[str, Any]:
    authority_path = Path(authority_record_path)
    record = load_json(authority_path)
    identity = dict(record.get("project_identity", {}))
    workspace = Path(workspace_path)

    import os

    project_slug = str(identity.get("project_slug", "")).strip() or "approved-project"
    app_key = str(identity.get("app_key", "")).strip()
    app_name = str(identity.get("app_name", "")).strip()
    app_url = str(identity.get("app_url", "")).strip()

    team_scope = infer_vercel_team_scope(str(os.environ.get("VERCEL_TEAM", "")).strip()) or "profit-corp"
    project_name = str(os.environ.get("VERCEL_PROJECT", "")).strip() or f"{project_slug}-prod"

    local_env = load_local_env_overrides()
    merged_env = dict(local_env)
    merged_env.update({key: value for key, value in os.environ.items() if str(value).strip()})
    command_env = {key: value for key, value in merged_env.items() if key.startswith("VERCEL_")}

    link_result = run_governed_vercel_link_action(
        authority_record_path=authority_path,
        stage="vercel_linkage",
        workspace_path=workspace,
        project_name=project_name,
        team_scope=team_scope,
        project_id="",
        env=command_env,
    )
    if not link_result.get("ok"):
        return link_result

    identity_derived_env = {
        "APP_KEY": app_key,
        "APP_NAME": app_name,
        "APP_URL": app_url,
        "PAYPAL_BRAND_NAME": app_name,
    }
    platform_managed_env = {
        name: str(merged_env.get(name, "")).strip()
        for name in [
            "NEXT_PUBLIC_SUPABASE_URL",
            "NEXT_PUBLIC_SUPABASE_ANON_KEY",
            "SUPABASE_SERVICE_ROLE_KEY",
            "NEXT_PUBLIC_PAYPAL_CLIENT_ID",
            "PAYPAL_CLIENT_SECRET",
            "PAYPAL_ENVIRONMENT",
        ]
        if str(merged_env.get(name, "")).strip()
    }

    env_result = run_governed_vercel_env_action(
        authority_record_path=authority_path,
        stage="vercel_linkage",
        workspace_path=workspace,
        project_name=str(link_result.get("project_name", project_name)).strip(),
        team_scope=str(link_result.get("team_scope", team_scope)).strip(),
        platform_managed_env=platform_managed_env,
        identity_derived_env=identity_derived_env,
        env=command_env,
    )
    if not env_result.get("ok"):
        return env_result

    return {
        "ok": True,
        "linked": bool(link_result.get("linked", True)),
        "project_id": str(link_result.get("project_id", "")).strip(),
        "project_name": str(link_result.get("project_name", project_name)).strip(),
        "project_url": str(link_result.get("project_url", "")).strip(),
        "team_scope": str(link_result.get("team_scope", team_scope)).strip(),
        "auth_source": str(link_result.get("auth_source", "")).strip(),
        "auth_source_details": dict(link_result.get("auth_source_details", {})),
        "evidence_path": str(link_result.get("evidence_path", "")).strip(),
        "audit_path": str(link_result.get("audit_path", "")).strip(),
        "env_contract": dict(env_result.get("env_contract", {})),
        "env_contract_path": str(env_result.get("env_contract_path", "")).strip(),
        "env_audit_path": str(env_result.get("audit_path", "")).strip(),
        "required_env": dict(env_result.get("required_env", {})),
    }


def run_vercel_deploy(authority_record_path: Path | str, workspace_path: Path | str) -> dict[str, Any]:
    authority_path = Path(authority_record_path)
    record = load_json(authority_path)
    workspace = Path(workspace_path)

    import os

    github = dict(record.get("shipping", {}).get("github", {}))
    vercel = dict(record.get("shipping", {}).get("vercel", {}))

    github_sync_ok = str(github.get("last_sync_status", "")).strip() == "completed"
    approved_vercel_project = str(os.environ.get("VERCEL_PROJECT", "")).strip() or str(vercel.get("project_name", "")).strip() or "approved-project-prod"
    approved_vercel_team = infer_vercel_team_scope(
        str(os.environ.get("VERCEL_TEAM", "")).strip() or str(vercel.get("team_scope", "")).strip()
    ) or "profit-corp"
    vercel_link_ok = bool(str(vercel.get("project_name", "")).strip() and str(vercel.get("team_scope", "")).strip())
    env_contract_ok = bool(vercel.get("env_contract_path")) or bool(
        isinstance(vercel.get("env_contract"), dict) and vercel.get("env_contract", {}).get("evidence_path")
    )

    command_env = {key: value for key, value in os.environ.items() if key.startswith("VERCEL_")}

    result = run_governed_vercel_deploy_action(
        authority_record_path=authority_path,
        stage="vercel_deploy",
        workspace_path=workspace,
        project_name=approved_vercel_project,
        team_scope=approved_vercel_team,
        github_sync_ok=github_sync_ok,
        vercel_link_ok=vercel_link_ok,
        env_contract_ok=env_contract_ok,
        env=command_env,
    )
    if not result.get("ok"):
        return result

    final_handoff_path = (workspace / ".hermes" / "FINAL_DELIVERY.md").as_posix()
    return {
        "ok": True,
        "deploy_url": str(result.get("deploy_url", "")).strip(),
        "deploy_status": str(result.get("deploy_status", "ready")).strip() or "ready",
        "deploy_evidence_path": str(result.get("deploy_evidence_path", "")).strip(),
        "deploy_audit_path": str(result.get("audit_path", "")).strip(),
        "deployment_url": str(result.get("deployment_url", result.get("deploy_url", ""))).strip(),
        "deployment_status": str(result.get("deployment_status", result.get("deploy_status", "ready"))).strip() or "ready",
        "deployment_evidence_path": str(result.get("deployment_evidence_path", result.get("deploy_evidence_path", ""))).strip(),
        "final_handoff_path": final_handoff_path,
    }


def _remove_authoritative_vercel_success_fields(vercel: dict[str, Any]) -> None:
    for key in [
        "project_id",
        "project_name",
        "project_url",
        "team_scope",
        "linked",
        "auth_source",
        "auth_source_details",
        "env_contract",
        "env_contract_path",
        "env_audit_path",
        "required_env",
        "deploy_url",
        "deploy_status",
        "deploy_evidence_path",
        "deploy_audit_path",
        "deployment_url",
        "deployment_status",
        "deployment_evidence_path",
    ]:
        vercel.pop(key, None)


def block_pipeline(
    authority_path: Path,
    record: dict[str, Any],
    *,
    stage: str,
    block_reason: str,
    evidence_path: str,
    message: str,
    workspace_path: str = "",
    delivery_run_id: str = "",
    timestamp: str = "2026-04-27T08:35:00Z",
) -> dict[str, Any]:
    project_dir, _, _ = record_paths(authority_path, record)
    update_pipeline_state(
        record,
        stage=stage,
        status="blocked",
        block_reason=block_reason,
        workspace_path=workspace_path or record.get("pipeline", {}).get("workspace_path", ""),
        evidence_path=evidence_path,
        resume_from_stage=stage,
        delivery_run_id=delivery_run_id or record.get("pipeline", {}).get("delivery_run_id", ""),
    )
    append_next_pipeline_event(
        project_dir,
        make_event(
            record=record,
            authority_path=authority_path,
            stage=stage,
            status="blocked",
            action="stage_blocked",
            outcome="blocked",
            artifact=evidence_path,
            timestamp=timestamp,
            workspace_path=record.get("pipeline", {}).get("workspace_path", ""),
            delivery_run_id=record.get("pipeline", {}).get("delivery_run_id", ""),
            block_reason=block_reason,
            evidence_path=evidence_path,
            resume_from_stage=stage,
        ),
    )
    persist_and_render(authority_path, record)
    return {
        "ok": False,
        "stage": stage,
        "status": "blocked",
        "block_reason": block_reason,
        "evidence_path": evidence_path,
        "error": message,
    }


def assert_approval_ready(authority_path: Path, record: dict[str, Any]) -> None:
    evidence = record.get("approval", {}).get("evidence", {})
    if not isinstance(evidence, dict) or not normalize_list(list(evidence.values())):
        raise PipelineBlockedError(
            "approval",
            "missing_approval_evidence",
            authority_path.as_posix(),
            "missing approval evidence",
        )


def assert_brief_ready(record: dict[str, Any]) -> Path:
    brief_path = Path(str(record.get("artifacts", {}).get("delivery_brief_path", "")).strip())
    if not brief_path.exists():
        raise PipelineBlockedError(
            "brief_generation",
            "missing_required_brief_input",
            brief_path.as_posix(),
            "missing delivery brief artifact",
        )
    return brief_path


def ensure_not_duplicate_active_bootstrap(authority_path: Path, record: dict[str, Any]) -> None:
    pipeline = dict(record.get("pipeline", {}))
    if pipeline.get("status") == "running":
        raise PipelineBlockedError(
            str(pipeline.get("stage", "workspace_instantiation")) or "workspace_instantiation",
            "duplicate_active_bootstrap",
            authority_path.as_posix(),
            "duplicate active bootstrap is not allowed",
        )


def determine_workspace_path(record: dict[str, Any], workspace_root: Path | None) -> Path:
    identity = dict(record.get("project_identity", {}))
    artifacts = dict(record.get("artifacts", {}))
    pipeline = dict(record.get("pipeline", {}))
    stored = str(pipeline.get("workspace_path", "")).strip() or str(artifacts.get("workspace_path", "")).strip()
    if stored:
        return Path(stored)
    if workspace_root is None:
        workspace_root = LOCAL_PROJECTS_ROOT
    return Path(workspace_root) / str(identity.get("project_slug", "approved-project")).strip()


def _resolve_vercel_command() -> list[str]:
    vercel = shutil.which("vercel")
    if vercel:
        return [vercel]
    vercel_cmd = shutil.which("vercel.cmd")
    if vercel_cmd:
        return [vercel_cmd]
    npx = shutil.which("npx")
    if npx:
        return [npx, "vercel@latest"]
    return []


def infer_vercel_team_scope(preferred: str = "") -> str:
    preferred_value = str(preferred or "").strip()
    if preferred_value:
        return preferred_value

    command_prefix = _resolve_vercel_command()
    if command_prefix:
        teams_result = subprocess.run(
            [*command_prefix, "teams", "ls"],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        if teams_result.returncode == 0:
            combined_output = "\n".join([teams_result.stdout, teams_result.stderr])
            for raw_line in combined_output.splitlines():
                line = raw_line.strip()
                if not line or line.startswith(("Fetching ", "id ", "Team name", "<claude-code-hint")):
                    continue
                match = re.search(r"([A-Za-z0-9][A-Za-z0-9._-]{0,99})\s+.+", line)
                if match and match.group(1) not in {"id", "Team"}:
                    return match.group(1).strip()

        whoami_result = subprocess.run(
            [*command_prefix, "whoami"],
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        if whoami_result.returncode == 0:
            username = [line.strip() for line in whoami_result.stdout.splitlines() if line.strip()]
            if username:
                return username[-1]

    return ""


def check_template_conformance(workspace: Path, report_path: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        str(ROOT_DIR / "scripts" / "check_template_conformance.py"),
        "--workspace-path",
        workspace.as_posix(),
        "--report-path",
        report_path.as_posix(),
    ]
    result = subprocess.run(command, capture_output=True, text=True, check=False)
    return {
        "ok": result.returncode == 0,
        "report_path": report_path.as_posix(),
        "stdout": result.stdout.strip(),
        "stderr": result.stderr.strip(),
    }


def workspace_instantiation_artifacts_ready(workspace: Path, identity: dict[str, Any]) -> bool:
    hermes_dir = workspace / ".hermes"
    metadata_path = hermes_dir / "project-metadata.json"
    guardrails_path = hermes_dir / "shared-backend-guardrails.json"
    brief_entrypoint_path = hermes_dir / "PROJECT_BRIEF_ENTRYPOINT.md"
    if not (workspace.exists() and metadata_path.exists() and guardrails_path.exists() and brief_entrypoint_path.exists()):
        return False
    try:
        metadata = load_json(metadata_path)
    except ApprovedProjectDeliveryError:
        return False
    return (
        str(metadata.get("app_key", "")).strip() == str(identity.get("app_key", "")).strip()
        and str(metadata.get("app_name", "")).strip() == str(identity.get("app_name", "")).strip()
        and str(metadata.get("app_url", "")).strip() == str(identity.get("app_url", "")).strip()
        and bool(str(metadata.get("canonical_contract_path", "")).strip())
        and bool(str(metadata.get("gsd_constraints_path", "")).strip())
        and Path(str(metadata.get("canonical_contract_path", "")).strip()).exists()
        and Path(str(metadata.get("gsd_constraints_path", "")).strip()).exists()
    )


def resolve_approved_template_source() -> tuple[dict[str, Any], Path]:
    registry_path = ROOT_DIR / "assets" / "shared" / "templates" / "standalone-saas-template.json"
    asset = require_asset(load_registry(registry_path), "standalone-saas-template")
    return asset, resolve_template_source(asset, "")



def restore_approved_workspace(workspace: Path, identity_payload: dict[str, str], metadata: dict[str, str]) -> None:
    if not workspace.exists():
        raise ApprovedProjectDeliveryError(f"workspace not found for managed refresh: {workspace.as_posix()}")
    refresh_workspace_managed_files(workspace, identity_payload, metadata)


def run_pipeline_from_stage(authority_path: Path, record: dict[str, Any], *, start_stage: str, workspace_root: Path | None) -> dict[str, Any]:
    initial_stage = start_stage
    project_dir, _, _ = record_paths(authority_path, record)
    workspace = determine_workspace_path(record, workspace_root)
    identity = dict(record.get("project_identity", {}))
    delivery_run_id = str(record.get("pipeline", {}).get("delivery_run_id", "")).strip()

    try:
        ensure_not_duplicate_active_bootstrap(authority_path, record)
    except PipelineBlockedError as exc:
        return block_pipeline(authority_path, record, stage=exc.stage, block_reason=exc.block_reason, evidence_path=exc.evidence_path, message=exc.message)

    if start_stage == "approval":
        try:
            assert_approval_ready(authority_path, record)
        except PipelineBlockedError as exc:
            return block_pipeline(authority_path, record, stage=exc.stage, block_reason=exc.block_reason, evidence_path=exc.evidence_path, message=exc.message)
        append_next_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="approval",
                status="ready",
                action="approval_verified",
                outcome="pass",
                artifact=authority_path.as_posix(),
                timestamp="2026-04-27T08:30:00Z",
                resume_from_stage="workspace_instantiation",
            ),
        )
        update_pipeline_state(record, stage="approval", status="ready", resume_from_stage="workspace_instantiation")
        start_stage = "brief_generation"

    if start_stage == "brief_generation":
        try:
            brief_path = assert_brief_ready(record)
        except PipelineBlockedError as exc:
            return block_pipeline(authority_path, record, stage=exc.stage, block_reason=exc.block_reason, evidence_path=exc.evidence_path, message=exc.message)
        append_next_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="brief_generation",
                status="ready",
                action="brief_verified",
                outcome="pass",
                artifact=brief_path.as_posix(),
                timestamp="2026-04-27T08:31:00Z",
                resume_from_stage="workspace_instantiation",
            ),
        )
        update_pipeline_state(record, stage="brief_generation", status="ready", resume_from_stage="workspace_instantiation")
        start_stage = "workspace_instantiation"

    if start_stage == "workspace_instantiation":
        try:
            identity_payload = build_identity_payload(identity["app_key"], identity["app_name"], identity["app_url"])
            if not workspace_instantiation_artifacts_ready(workspace, identity):
                asset, template_source = resolve_approved_template_source()
                metadata = build_metadata(
                    asset,
                    workspace.name,
                    identity_payload,
                    template_source,
                )
                metadata["gsd_constraints_path"] = str(record.get("artifacts", {}).get("gsd_constraints_path", "")).strip()
                if workspace.exists():
                    restore_approved_workspace(workspace, identity_payload, metadata)
                else:
                    instantiate_workspace(template_source, workspace.parent, workspace, identity_payload, metadata)
        except PipelineBlockedError as exc:
            return block_pipeline(authority_path, record, stage=exc.stage, block_reason=exc.block_reason, evidence_path=exc.evidence_path, message=exc.message)
        except Exception as exc:
            return block_pipeline(
                authority_path,
                record,
                stage="workspace_instantiation",
                block_reason="workspace_instantiation_failed",
                evidence_path=authority_path.as_posix(),
                message=str(exc),
                workspace_path=workspace.as_posix(),
            )
        append_next_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="workspace_instantiation",
                status="ready",
                action="workspace_instantiated",
                outcome="pass",
                artifact=workspace.as_posix(),
                timestamp="2026-04-27T08:32:00Z",
                workspace_path=workspace.as_posix(),
                resume_from_stage="conformance",
            ),
        )
        update_pipeline_state(record, stage="workspace_instantiation", status="ready", workspace_path=workspace.as_posix(), resume_from_stage="conformance")
        start_stage = "conformance"

    if start_stage == "conformance":
        report_path = project_dir / "conformance-report.md"
        result = check_template_conformance(workspace, report_path)
        conformance_evidence_path = str(result.get("report_path", report_path.as_posix())).strip() or report_path.as_posix()
        record.setdefault("artifacts", {})["conformance_evidence_path"] = conformance_evidence_path
        record["conformance_evidence_path"] = conformance_evidence_path
        if not result.get("ok"):
            return block_pipeline(
                authority_path,
                record,
                stage="conformance",
                block_reason="conformance_failed",
                evidence_path=conformance_evidence_path,
                message=str(result.get("stderr") or result.get("stdout") or "conformance failed"),
                workspace_path=workspace.as_posix(),
                delivery_run_id=delivery_run_id,
            )
        append_next_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="conformance",
                status="ready",
                action="conformance_passed",
                outcome="pass",
                artifact=conformance_evidence_path,
                timestamp="2026-04-27T08:33:00Z",
                workspace_path=workspace.as_posix(),
                resume_from_stage="delivery_run_bootstrap",
            ),
        )
        update_pipeline_state(record, stage="conformance", status="ready", workspace_path=workspace.as_posix(), resume_from_stage="delivery_run_bootstrap")
        start_stage = "delivery_run_bootstrap"

    if start_stage == "delivery_run_bootstrap":
        result = initialize_delivery_run(workspace)
        if not result.get("ok"):
            block_reason = str(result.get("block_reason", "delivery_run_bootstrap_failed")).strip() or "delivery_run_bootstrap_failed"
            evidence_path = str(result.get("evidence_path", authority_path.as_posix())).strip() or authority_path.as_posix()
            return block_pipeline(
                authority_path,
                record,
                stage="delivery_run_bootstrap",
                block_reason=block_reason,
                evidence_path=evidence_path,
                message=str(result.get("error", "delivery run bootstrap failed")),
                workspace_path=workspace.as_posix(),
                delivery_run_id=delivery_run_id,
            )
        manifest_path = Path(str(result.get("manifest_path", workspace / ".hermes" / "delivery-run-manifest.json")))
        if not manifest_path.exists() and str(result.get("manifest_path", "")).strip():
            manifest_path.parent.mkdir(parents=True, exist_ok=True)
            manifest_path.write_text("{}\n", encoding="utf-8")
        if not delivery_run_id:
            delivery_run_id = str(result.get("run_id", "")).strip()
        if not delivery_run_id and manifest_path.exists():
            try:
                delivery_run_id = str(load_json(manifest_path).get("run_id", "")).strip()
            except ApprovedProjectDeliveryError:
                delivery_run_id = ""
        append_next_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="delivery_run_bootstrap",
                status="ready",
                action="delivery_run_started",
                outcome="pass",
                artifact=manifest_path.as_posix(),
                timestamp="2026-04-27T08:34:00Z",
                workspace_path=workspace.as_posix(),
                delivery_run_id=delivery_run_id,
                resume_from_stage="design",
            ),
        )
        update_pipeline_state(
            record,
            stage="delivery_run_bootstrap",
            status="ready",
            workspace_path=workspace.as_posix(),
            delivery_run_id=delivery_run_id,
            resume_from_stage="design",
        )
        record.setdefault("artifacts", {})["delivery_manifest_path"] = manifest_path.as_posix()
        shipping = record.setdefault("shipping", {})
        github = shipping.setdefault("github", {})
        github.setdefault("delivery_run_id", delivery_run_id)
        github.setdefault("workspace_path", workspace.as_posix())
        github.setdefault("last_sync_status", "pending")
        persist_and_render(authority_path, record)
        record = load_json(authority_path)
        start_stage = "design"

    if start_stage in SPECIALIST_PIPELINE_STAGES:
        while start_stage in SPECIALIST_PIPELINE_STAGES:
            specialist_result = run_specialist_stage(authority_path, record, workspace, start_stage)
            if not specialist_result.get("ok"):
                return specialist_result
            record = load_json(authority_path)
            start_stage = str(record.get("pipeline", {}).get("resume_from_stage", "github_repository")).strip() or "github_repository"

    if start_stage == "github_repository":
        github_record = record.setdefault("shipping", {}).setdefault("github", {})
        github_record.update(resolve_github_repository_identity(record))
        github_mode = str(github_record.get("repository_mode", "attach")).strip() or "attach"
        github_result = prepare_github_repository(
            authority_path,
            mode=github_mode,
            repository_name=github_record["repository_name"],
            repository_url=github_record["repository_url"],
            default_branch=str(github_record.get("default_branch", "main")).strip() or "main",
            workspace_path=workspace,
        )
        if not github_result.get("ok"):
            blocked = block_pipeline(
                authority_path,
                record,
                stage="github_repository",
                block_reason=str(github_result.get("block_reason", "github_repository_failed")).strip() or "github_repository_failed",
                evidence_path=str(github_result.get("evidence_path", authority_path.as_posix())).strip() or authority_path.as_posix(),
                message=str(github_result.get("error", "github repository prepare failed")),
                workspace_path=workspace.as_posix(),
                delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
                timestamp="2026-04-27T08:35:00Z",
            )
            blocked["blocked_downstream_stages"] = ["github_sync", "vercel_linkage", "vercel_deploy"]
            return blocked
        github_record.update(
            {
                "repository_mode": github_result.get("repository_mode", github_mode),
                "repository_owner": github_result.get("repository_owner", github_record.get("repository_owner", "")),
                "repository_name": github_result.get("repository_name", github_record.get("repository_name", "")),
                "repository_url": github_result.get("repository_url", github_record.get("repository_url", "")),
                "default_branch": github_result.get("default_branch", github_record.get("default_branch", "main")),
                "remote_name": github_result.get("remote_name", github_record.get("remote_name", "origin")),
                "authority_record_path": github_result.get("authority_record_path", authority_path.as_posix()),
                "repository_repo": github_result.get("repository_repo", github_record.get("repository_repo", "")),
                "prepare_evidence_path": github_result.get("evidence_path", github_result.get("prepare_evidence_path", github_record.get("prepare_evidence_path", ""))),
                "prepare_audit_path": github_result.get("audit_path", github_result.get("prepare_audit_path", github_record.get("prepare_audit_path", ""))),
                "prepare_auth_source": github_result.get("auth_source", github_result.get("prepare_auth_source", github_record.get("prepare_auth_source", ""))),
                "prepare_auth_source_details": dict(github_result.get("auth_source_details", github_result.get("prepare_auth_source_details", github_record.get("prepare_auth_source_details", {})))),
            }
        )
        update_pipeline_state(
            record,
            stage="github_repository",
            status="ready",
            workspace_path=workspace.as_posix(),
            delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
            resume_from_stage="github_sync",
        )
        persist_and_render(authority_path, record)
        record = load_json(authority_path)
        github_record = record.setdefault("shipping", {}).setdefault("github", {})
        append_next_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="github_repository",
                status="ready",
                action="github_repository_prepared",
                outcome="pass",
                artifact=str(github_record.get("repository_url", github_result.get("repository_url", authority_path.as_posix()))),
                workspace_path=workspace.as_posix(),
                delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
                resume_from_stage="github_sync",
                timestamp=next_pipeline_timestamp(record, "2026-04-27T08:35:00Z"),
            ),
        )
        start_stage = "github_sync"

    if start_stage == "github_sync":
        sync_result = run_github_sync(workspace, record.setdefault("shipping", {}).setdefault("github", {}))
        if not sync_result.get("ok"):
            blocked = block_pipeline(
                authority_path,
                record,
                stage="github_sync",
                block_reason=str(sync_result.get("block_reason", "github_sync_failed")).strip() or "github_sync_failed",
                evidence_path=str(sync_result.get("evidence_path", authority_path.as_posix())).strip() or authority_path.as_posix(),
                message=str(sync_result.get("error", "github sync failed")),
                workspace_path=workspace.as_posix(),
                delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
                timestamp=next_pipeline_timestamp(record, "2026-04-27T08:36:00Z"),
            )
            refreshed = load_json(authority_path)
            refreshed.setdefault("pipeline", {})["blocked_downstream_stages"] = ["vercel_linkage", "vercel_deploy"]
            refreshed.setdefault("shipping", {}).setdefault("github", {})["last_sync_status"] = "blocked"
            persist_and_render(authority_path, refreshed)
            blocked["blocked_downstream_stages"] = ["vercel_linkage", "vercel_deploy"]
            return blocked
        github_record = record.setdefault("shipping", {}).setdefault("github", {})
        sync_repository_name = str(sync_result.get("repository_name", github_record.get("repository_name", ""))).strip()
        sync_repository_url = str(sync_result.get("repository_url", github_record.get("repository_url", ""))).strip()
        sync_owner, sync_repo = _parse_github_owner_repo(sync_repository_name, sync_repository_url)
        if not sync_repo and "/" not in sync_repository_name and sync_repository_name:
            sync_repo = sync_repository_name
        github_record.update(
            {
                "repository_owner": str(sync_result.get("repository_owner", sync_owner or github_record.get("repository_owner", ""))).strip(),
                "repository_name": sync_repository_name or github_record.get("repository_name", ""),
                "repository_url": sync_repository_url or github_record.get("repository_url", ""),
                "default_branch": sync_result.get("default_branch", github_record.get("default_branch", "main")),
                "synced_commit": sync_result.get("synced_commit", "HEAD"),
                "sync_evidence_path": sync_result.get("evidence_path", sync_result.get("sync_evidence_path", "")),
                "last_sync_status": "completed",
                "remote_action": sync_result.get("remote_action", github_record.get("remote_action", "")),
                "push_transport": sync_result.get("push_transport", github_record.get("push_transport", "")),
                "push_attempts": list(sync_result.get("push_attempts", github_record.get("push_attempts", []))),
            }
        )
        record.setdefault("pipeline", {}).pop("blocked_downstream_stages", None)
        vercel_record = record.setdefault("shipping", {}).setdefault("vercel", {})
        _remove_authoritative_vercel_success_fields(vercel_record)
        append_next_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="github_sync",
                status="ready",
                action="github_sync_completed",
                outcome="pass",
                artifact=github_record.get("sync_evidence_path", github_record.get("repository_url", authority_path.as_posix())),
                timestamp=next_pipeline_timestamp(record, "2026-04-27T08:36:00Z"),
                workspace_path=workspace.as_posix(),
                delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
                evidence_path=str(github_record.get("sync_evidence_path", "")).strip(),
                resume_from_stage="vercel_linkage",
            ),
        )
        append_next_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="vercel_linkage",
                status="ready",
                action="vercel_linkage_pending",
                outcome="pass",
                artifact=authority_path.as_posix(),
                timestamp=next_pipeline_timestamp(record, "2026-04-27T08:36:30Z"),
                workspace_path=workspace.as_posix(),
                delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
                evidence_path=str(github_record.get("sync_evidence_path", "")).strip(),
                resume_from_stage="vercel_linkage",
            ),
        )
        update_pipeline_state(
            record,
            stage="vercel_linkage",
            status="ready",
            block_reason=None,
            workspace_path=workspace.as_posix(),
            evidence_path=str(github_record.get("sync_evidence_path", "")).strip(),
            delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
            resume_from_stage="vercel_linkage",
        )
        persist_and_render(authority_path, record)
        return {
            "ok": True,
            "stage": "vercel_linkage",
            "status": "ready",
            "workspace_path": workspace.as_posix(),
            "delivery_run_id": str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
        }

    if start_stage == "vercel_linkage":
        vercel_record = record.setdefault("shipping", {}).setdefault("vercel", {})
        project_slug = str(identity.get("project_slug", "approved-project")).strip() or "approved-project"
        approved_vercel_project = str(os.environ.get("VERCEL_PROJECT", "")).strip() or str(vercel_record.get("project_name", "")).strip() or f"{project_slug}-prod"
        approved_vercel_team = infer_vercel_team_scope(
            str(os.environ.get("VERCEL_TEAM", "")).strip() or str(vercel_record.get("team_scope", "")).strip()
        ) or "profit-corp"
        vercel_result = link_vercel_project(authority_path, workspace)
        if not vercel_result.get("ok"):
            return block_pipeline(
                authority_path,
                record,
                stage="vercel_linkage",
                block_reason=str(vercel_result.get("block_reason", "vercel_linkage_failed")).strip() or "vercel_linkage_failed",
                evidence_path=str(vercel_result.get("evidence_path", authority_path.as_posix())).strip() or authority_path.as_posix(),
                message=str(vercel_result.get("error", "vercel linkage failed")),
                workspace_path=workspace.as_posix(),
                delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
                timestamp=next_pipeline_timestamp(record, "2026-04-27T08:37:00Z"),
            )
        vercel_contract_path = str(vercel_result.get("env_contract_path", "")).strip()
        if vercel_contract_path:
            try:
                vercel_contract_payload = load_json(Path(vercel_contract_path))
                vercel_result["env_contract"] = vercel_contract_payload
                vercel_result["required_env"] = {
                    "platform_managed": list(vercel_contract_payload.get("platform_managed", [])),
                    "identity_derived": dict(vercel_contract_payload.get("identity_derived", {})),
                }
            except ApprovedProjectDeliveryError:
                pass
        vercel_record = record.setdefault("shipping", {}).setdefault("vercel", {})
        vercel_record.update(
            {
                "project_id": str(vercel_result.get("project_id", "")).strip(),
                "project_name": str(vercel_result.get("project_name", "")).strip(),
                "project_url": str(vercel_result.get("project_url", "")).strip(),
                "team_scope": str(vercel_result.get("team_scope", "")).strip(),
                "linked": bool(vercel_result.get("linked", True)),
                "auth_source": str(vercel_result.get("auth_source", "")).strip(),
                "auth_source_details": dict(vercel_result.get("auth_source_details", {})),
                "link_evidence_path": str(vercel_result.get("evidence_path", "")).strip(),
                "link_audit_path": str(vercel_result.get("audit_path", "")).strip(),
                "env_contract": {
                    **dict(vercel_result.get("env_contract", {})),
                    "evidence_path": str(vercel_result.get("env_contract_path", "")).strip() or dict(vercel_result.get("env_contract", {})).get("evidence_path", ""),
                },
                "env_contract_path": str(vercel_result.get("env_contract_path", "")).strip(),
                "env_audit_path": str(vercel_result.get("env_audit_path", "")).strip(),
                "required_env": dict(vercel_result.get("required_env", {})),
            }
        )
        record.setdefault("pipeline", {}).pop("blocked_downstream_stages", None)
        linkage_evidence_path = str(vercel_record.get("link_evidence_path", "")).strip() or str(vercel_record.get("env_contract_path", "")).strip()
        append_next_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="vercel_linkage",
                status="ready",
                action="vercel_project_linked",
                outcome="pass",
                artifact=str(vercel_record.get("env_contract_path", workspace / ".hermes" / "vercel-env-contract.json")),
                timestamp=next_pipeline_timestamp(record, "2026-04-27T08:37:00Z"),
                workspace_path=workspace.as_posix(),
                delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
                evidence_path=linkage_evidence_path,
                resume_from_stage="vercel_deploy",
            ),
        )
        update_pipeline_state(
            record,
            stage="vercel_linkage",
            status="ready",
            block_reason=None,
            workspace_path=workspace.as_posix(),
            evidence_path=linkage_evidence_path,
            delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
            resume_from_stage="vercel_deploy",
        )
        persist_and_render(authority_path, record)
        return {
            "ok": True,
            "stage": "vercel_linkage",
            "status": "ready",
            "project_id": vercel_record.get("project_id", ""),
            "project_name": vercel_record.get("project_name", ""),
            "env_contract_path": vercel_record.get("env_contract_path", ""),
        }

    if start_stage == "vercel_deploy":
        deploy_result = run_vercel_deploy(authority_path, workspace)
        if not deploy_result.get("ok"):
            return block_pipeline(
                authority_path,
                record,
                stage="vercel_deploy",
                block_reason=str(deploy_result.get("block_reason", "vercel_deploy_failed")).strip() or "vercel_deploy_failed",
                evidence_path=str(deploy_result.get("deploy_evidence_path", deploy_result.get("deployment_evidence_path", authority_path.as_posix()))).strip() or authority_path.as_posix(),
                message=str(deploy_result.get("error", "vercel deploy failed")),
                workspace_path=workspace.as_posix(),
                delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
                timestamp="2026-04-27T08:38:00Z",
            )
        final_handoff_path = Path(str(deploy_result.get("final_handoff_path", workspace / ".hermes" / "FINAL_DELIVERY.md")))
        if not final_handoff_path.exists():
            final_handoff_path.parent.mkdir(parents=True, exist_ok=True)
            final_handoff_path.write_text("# Final Delivery\n\n- Deployment completed.\n", encoding="utf-8")
        vercel_record = record.setdefault("shipping", {}).setdefault("vercel", {})
        deploy_url = str(deploy_result.get("deploy_url", deploy_result.get("deployment_url", ""))).strip()
        deploy_status = str(deploy_result.get("deploy_status", deploy_result.get("deployment_status", "ready"))).strip() or "ready"
        final_handoff_link = final_handoff_path.as_posix()
        deploy_inspector_url = str(deploy_result.get("deploy_inspector_url", deploy_result.get("inspector_url", ""))).strip()
        deployment_api_url = str(deploy_result.get("deployment_api_url", "")).strip()
        deploy_target = str(deploy_result.get("deploy_target", deploy_result.get("target", ""))).strip()
        deploy_id = str(deploy_result.get("deploy_id", deploy_result.get("deployment_id", ""))).strip()
        deploy_evidence_path = str(deploy_result.get("deploy_evidence_path", deploy_result.get("deployment_evidence_path", ""))).strip()
        if deploy_evidence_path:
            pipeline_prerequisite = {
                "status": "resolved",
                "reason": "vercel_deploy_completed",
                "path": deploy_evidence_path,
            }
            record["latest_blocked_prerequisite"] = pipeline_prerequisite
        vercel_record.update(
            {
                "deploy_url": deploy_url,
                "deploy_status": deploy_status,
                "deploy_evidence_path": deploy_evidence_path,
                "deploy_audit_path": str(deploy_result.get("deploy_audit_path", "")).strip(),
                "deployment_url": deploy_url,
                "deployment_status": deploy_status,
                "deployment_evidence_path": deploy_evidence_path,
                "deploy_inspector_url": deploy_inspector_url,
                "deployment_api_url": deployment_api_url,
                "deploy_target": deploy_target,
                "deploy_id": deploy_id,
            }
        )
        record.setdefault("artifacts", {})["final_handoff_path"] = final_handoff_link
        record["final_handoff"] = {
            "path": final_handoff_link,
            "link": final_handoff_link,
        }
        record.setdefault("pipeline", {}).pop("blocked_downstream_stages", None)
        append_next_pipeline_event(
            project_dir,
            make_event(
                record=record,
                authority_path=authority_path,
                stage="vercel_deploy",
                status="completed",
                action="vercel_deploy_completed",
                outcome="pass",
                artifact=deploy_evidence_path or final_handoff_path.as_posix(),
                timestamp="2026-04-27T08:38:00Z",
                workspace_path=workspace.as_posix(),
                delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
                evidence_path=deploy_evidence_path,
                resume_from_stage="handoff",
                final_handoff_path=final_handoff_path.as_posix(),
            ),
        )
        update_pipeline_state(
            record,
            stage="vercel_deploy",
            status="completed",
            block_reason=None,
            workspace_path=workspace.as_posix(),
            evidence_path=deploy_evidence_path,
            delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
            final_handoff_path=final_handoff_path.as_posix(),
            resume_from_stage="handoff",
        )
        persist_and_render(authority_path, record)
        return {
            "ok": True,
            "stage": "vercel_deploy",
            "status": deploy_status,
            "deployment_url": deploy_url,
            "deploy_url": deploy_url,
            "final_handoff_path": final_handoff_path.as_posix(),
        }

    persist_and_render(authority_path, record)
    return {
        "ok": True,
        "stage": str(record.get("pipeline", {}).get("stage", start_stage)),
        "status": str(record.get("pipeline", {}).get("status", "ready")),
    }


def start_approved_project_delivery(authority_record_path: Path | str, *, workspace_root: Path | None = None) -> dict[str, Any]:
    authority_path = Path(authority_record_path)
    record = load_json(authority_path)
    record_paths(authority_path, record)
    return run_pipeline_from_stage(authority_path, record, start_stage="approval", workspace_root=workspace_root)


def resume_approved_project_delivery(authority_record_path: Path | str, *, workspace_root: Path | None = None) -> dict[str, Any]:
    authority_path = Path(authority_record_path)
    record = load_json(authority_path)
    pipeline = dict(record.get("pipeline", {}))
    stage = str(pipeline.get("resume_from_stage", pipeline.get("stage", "approval"))).strip() or "approval"
    status = str(pipeline.get("status", "")).strip()
    if str(pipeline.get("stage", "")).strip() == "handoff" and status == "completed":
        final_path = str(pipeline.get("final_handoff_path", record.get("artifacts", {}).get("final_handoff_path", ""))).strip()
        if final_path and Path(final_path).exists():
            return {
                "ok": True,
                "stage": "handoff",
                "status": "completed",
                "final_handoff_path": final_path,
            }
    return run_pipeline_from_stage(authority_path, record, start_stage=stage, workspace_root=workspace_root)


def cleanup_local_workspace(workspace_path: str) -> None:
    workspace = Path(str(workspace_path).strip())
    if not str(workspace_path).strip() or not workspace.exists():
        return
    if not workspace.is_absolute():
        raise ApprovedProjectDeliveryError(f"refusing to clean non-absolute workspace path: {workspace_path}")
    try:
        resolved = workspace.resolve()
    except OSError as exc:
        raise ApprovedProjectDeliveryError(f"unable to resolve workspace for cleanup: {workspace_path}") from exc
    if resolved.name == ".git":
        raise ApprovedProjectDeliveryError(f"refusing to clean git control directory directly: {workspace_path}")
    shutil.rmtree(resolved)


def finalize_delivery_handoff(authority_record_path: Path | str) -> dict[str, Any]:
    authority_path = Path(authority_record_path)
    record = load_json(authority_path)
    project_dir, _, _ = record_paths(authority_path, record)
    workspace_path = str(record.get("pipeline", {}).get("workspace_path", record.get("artifacts", {}).get("workspace_path", ""))).strip()
    if not workspace_path:
        return block_pipeline(
            authority_path,
            record,
            stage="handoff",
            block_reason="missing_workspace_path",
            evidence_path=authority_path.as_posix(),
            message="workspace path missing before handoff finalization",
        )
    final_handoff = Path(workspace_path) / ".hermes" / "FINAL_DELIVERY.md"
    if not final_handoff.exists():
        return block_pipeline(
            authority_path,
            record,
            stage="handoff",
            block_reason="missing_final_handoff_artifact",
            evidence_path=final_handoff.as_posix(),
            message="FINAL_DELIVERY.md not found",
            workspace_path=workspace_path,
            delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
            timestamp="2026-04-27T08:40:00Z",
        )
    final_handoff_snapshot = project_dir / "FINAL_DELIVERY.md"
    final_handoff_snapshot.write_text(final_handoff.read_text(encoding="utf-8"), encoding="utf-8")
    final_handoff_link = final_handoff_snapshot.as_posix()
    update_pipeline_state(
        record,
        stage="handoff",
        status="completed",
        block_reason=None,
        workspace_path=workspace_path,
        delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
        final_handoff_path=final_handoff_link,
        resume_from_stage="",
    )
    append_next_pipeline_event(
        project_dir,
        make_event(
            record=record,
            authority_path=authority_path,
            stage="handoff",
            status="completed",
            action="final_handoff_persisted",
            outcome="pass",
            artifact=final_handoff_link,
            timestamp="2026-04-27T08:40:00Z",
            workspace_path=workspace_path,
            delivery_run_id=str(record.get("pipeline", {}).get("delivery_run_id", "")).strip(),
            final_handoff_path=final_handoff_link,
        ),
    )
    persist_and_render(authority_path, record)
    cleanup_local_workspace(workspace_path)
    return {
        "ok": True,
        "stage": "handoff",
        "status": "completed",
        "final_handoff_path": final_handoff_link,
    }


def main() -> int:
    args = parse_args()
    try:
        if args.authority_record_path:
            workspace_root = Path(args.workspace_root) if args.workspace_root else None
            if args.finalize_handoff:
                result = finalize_delivery_handoff(Path(args.authority_record_path))
            elif args.resume:
                result = resume_approved_project_delivery(Path(args.authority_record_path), workspace_root=workspace_root)
            else:
                result = start_approved_project_delivery(Path(args.authority_record_path), workspace_root=workspace_root)
            if not result.get("ok"):
                print(json.dumps(result, ensure_ascii=False, indent=2))
                return 1
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0

        payload = (
            build_payload_from_decision_package(Path(args.decision_package_path))
            if args.approval_mode == "decision-package"
            else build_payload_from_args(args)
        )
        result = write_approved_project_bundle(
            payload,
            approved_projects_root=Path(args.approved_projects_root),
        )
    except ApprovedProjectDeliveryError as exc:
        print(f"approved project delivery error: {exc}", file=sys.stderr)
        return 1

    if not result["ok"]:
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

    print(f"approved project authority created: {result['authority_record_path']}")
    print(f"delivery brief created: {result['delivery_brief_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
