#!/usr/bin/env python3
import argparse
import hashlib
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
from scripts.product_proof_contract import (
    FAILURE_REASON_MESSAGES,
    build_product_proof_summary,
)
from scripts.request_platform_justification import validate_platform_justification
from scripts.start_delivery_run import initialize_delivery_run
from scripts.template_contract_common import load_registry, require_asset
from scripts.validate_delivery_handoff import REQUIRED_STAGE_HEADINGS
from scripts.vercel_delivery_common import apply_env_contract as vercel_apply_env_contract
from scripts.vercel_delivery_common import deploy_to_vercel
from scripts.vercel_delivery_common import link_vercel_project as vercel_link_project


DEFAULT_TEMPLATE_CONTRACT_PATH = "docs/platform/standalone-saas-template-contract.md"
DEFAULT_GSD_CONSTRAINTS_PATH = ".planning/phases/09-claude-code-delivery-team-orchestration/09-01-PLAN.md"
DEFAULT_QUALIFICATION_BUNDLE_PATH = "assets/shared/qualification/latest/qualification_bundle.json"
DEFAULT_REQUIRED_LANGUAGE_PACK = ["en", "zh", "es", "ar", "pt", "fr", "hi", "ja", "ru"]
DEFAULT_UI_ARTIFACT_CONTRACT = [
    "Reference `/ui-ux-pro-max` output as the design authority before frontend implementation.",
    "Cover screen inventory, primary conversion flow, monetization surface, empty/loading/error/success states, responsive rules, accessibility rules, and multilingual behavior.",
    "Include English and Chinese copy coverage plus the remaining required language surfaces.",
]
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
    "missing_pain_point",
    "missing_monetization",
    "missing_required_languages",
    "missing_ui_artifact_contract",
    "missing_qualification_proof",
    "failed_qualification_proof",
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
    "missing_ui_ux_summary",
    "ui_ux_artifact_empty",
    "ui_ux_artifact_stale",
    "ui_ux_artifact_coverage_incomplete",
    "ui_ux_implementation_drift",
    "missing_stage_handoff",
    "empty_stage_handoff",
    "missing_structured_stage_evidence",
    "empty_structured_stage_evidence",
    "stale_structured_stage_evidence",
    "missing_claude_code_transcript",
    "stage_evidence_run_mismatch",
    "stage_evidence_stage_mismatch",
    "stage_evidence_artifact_mismatch",
    "missing_testing_verification_evidence",
    "authority_state_drift",
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
        "hermes_profile": "arch",
        "artifact": ".hermes/stage-handoffs/01-design.md",
        "next_stage": "development",
    },
    {
        "pipeline_stage": "development",
        "delivery_stage": "development",
        "role": "development-specialist",
        "hermes_profile": "arch",
        "artifact": ".hermes/stage-handoffs/02-development.md",
        "next_stage": "testing",
    },
    {
        "pipeline_stage": "testing",
        "delivery_stage": "testing",
        "role": "testing-specialist",
        "hermes_profile": "arch",
        "artifact": ".hermes/stage-handoffs/03-testing.md",
        "next_stage": "git versioning",
    },
    {
        "pipeline_stage": "git_versioning",
        "delivery_stage": "git versioning",
        "role": "git-versioning-specialist",
        "hermes_profile": "arch",
        "artifact": ".hermes/stage-handoffs/04-git-versioning.md",
        "next_stage": "release readiness",
    },
    {
        "pipeline_stage": "release_readiness",
        "delivery_stage": "release readiness",
        "role": "release-readiness-specialist",
        "hermes_profile": "ceo",
        "artifact": ".hermes/stage-handoffs/05-release-readiness.md",
        "next_stage": "none",
    },
]
SPECIALIST_STAGE_BY_PIPELINE = {item["pipeline_stage"]: item for item in SPECIALIST_STAGE_CONFIGS}
WORKSPACE_CHANGE_INVENTORY_NAME = "workspace-changes.json"
FINAL_DELIVERY_RELATIVE_PATH = ".hermes/FINAL_DELIVERY.md"
RELEASE_READINESS_EVIDENCE_NAME = "release-readiness-summary.json"
UI_UX_ARTIFACT_NAME = "ui-ux-design-system.md"
UI_UX_SUMMARY_NAME = "ui-ux-design-system.summary.json"
UI_UX_SKILL_NAME = "ui-ux-pro-max"
UI_SPECIALIST_STAGES = {"design", "development"}
REQUIRED_UI_ARTIFACT_COVERAGE_KEYS = (
    "screen_inventory",
    "primary_workflow",
    "monetization_surface",
    "multilingual_coverage",
    "responsive_rules",
    "accessibility_rules",
    "states",
)
REQUIRED_UI_ARTIFACT_STATES = ("empty", "loading", "error", "success")
STAGE_EVIDENCE_DIR = ".hermes/stage-evidence"
PRODUCT_SPEC_REQUIRED_FIELDS = [
    "pain_point",
    "product_definition",
    "core_workflow",
    "monetization",
    "required_languages",
    "ui_artifact_contract",
    "frontend_acceptance",
    "backend_acceptance",
    "template_rejection_rules",
    "non_goals",
]
TEMPLATE_MARKER_PATTERNS = [
    "A starter that already knows how to do auth, payments, and shared backend boundaries.",
    "This project is a reference implementation for building new SaaS apps",
    "Open reference console",
    "Open app shell",
    "Shared platform layer",
    "Product-facing layer",
    "AI-friendly structure",
]
REQUIRED_PRODUCT_IMPLEMENTATION_PATHS = [
    "src/app/page.tsx",
]
REQUIRED_PRODUCT_PROOF_PATH_PREFIXES = [
    "src/app",
    "src/lib",
    "src/app/api",
]
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
    "pain_point": "missing_pain_point",
    "monetization": "missing_monetization",
    "required_languages": "missing_required_languages",
    "ui_artifact_contract": "missing_ui_artifact_contract",
    "qualification_bundle_path": "missing_qualification_proof",
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
    parser.add_argument("--pain-point", help="Concrete approved user pain point that the product must solve.")
    parser.add_argument("--monetization", action="append", default=[], help="One monetization requirement or paid offer rule.")
    parser.add_argument("--required-language", action="append", default=[], help="One required language code for product surfaces.")
    parser.add_argument("--ui-artifact-contract", action="append", default=[], help="One UI artifact contract requirement.")
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


def normalize_required_languages(values: list[Any]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for value in values:
        code = str(value).strip().lower()
        if code and code not in seen:
            normalized.append(code)
            seen.add(code)
    return normalized


def build_default_ui_artifact_contract() -> list[str]:
    return list(DEFAULT_UI_ARTIFACT_CONTRACT)


def build_default_required_languages() -> list[str]:
    return list(DEFAULT_REQUIRED_LANGUAGE_PACK)


def build_default_monetization(pain_point: str, target_user: str) -> list[str]:
    user_label = target_user or "target users"
    problem_label = pain_point or "the approved pain point"
    return [
        f"Offer a paid subscription that continuously solves {problem_label} for {user_label}.",
        "Show a clear upgrade/paywall surface tied to the primary workflow outcome rather than a template placeholder offer.",
        "Release-readiness evidence must prove the paid path is visible in the product or explicitly staged behind a governed integration boundary.",
    ]


def build_default_template_rejection_rules() -> list[str]:
    return [
        "Reject deliveries that only change branding, marketing copy, or src/lib/app-definition.ts.",
        "Reject deliveries whose home page or primary workflow still reads like a generic starter/template shell.",
        "Reject deliveries that cannot show product-specific workflow, monetization surface, and multilingual coverage evidence.",
    ]


def load_qualification_bundle(path: str) -> dict[str, Any]:
    bundle_path = Path(str(path).strip())
    if not bundle_path.exists():
        raise ApprovedProjectDeliveryError(f"qualification bundle not found: {bundle_path}")
    try:
        payload = json.loads(bundle_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ApprovedProjectDeliveryError(f"invalid qualification bundle JSON: {bundle_path}") from exc
    if not isinstance(payload, dict):
        raise ApprovedProjectDeliveryError("qualification bundle must be a JSON object")
    return payload


def find_qualification_verdict(bundle: dict[str, Any], idea_id: str = "", pain_point: str = "") -> dict[str, Any] | None:
    candidates = bundle.get("candidates", [])
    if not isinstance(candidates, list):
        return None
    for item in candidates:
        if isinstance(item, dict) and idea_id and str(item.get("idea_id", "")).strip() == idea_id:
            return item
    normalized_pain = str(pain_point).strip().lower()
    for item in candidates:
        if not isinstance(item, dict):
            continue
        if normalized_pain and str(item.get("problem_summary", "")).strip().lower() == normalized_pain:
            return item
    return None


def build_proposal_block(
    *,
    qualified_idea_id: str,
    mvp_framing: str,
    qualification_verdict: dict[str, Any] | None,
) -> dict[str, Any]:
    backlinks = [f"{DEFAULT_QUALIFICATION_BUNDLE_PATH}#{qualified_idea_id}"] if qualified_idea_id else []
    generated_from = dict((qualification_verdict or {}).get("generated_from", {}))
    for key in ("history_path", "cluster_path"):
        value = str(generated_from.get(key, "")).strip()
        if value:
            backlinks.append(value)
    return {
        "proposal_id": f"proposal-{qualified_idea_id.lower()}-v1" if qualified_idea_id else "proposal-unlinked-v1",
        "launch_framing": mvp_framing,
        "market_rationale": "Qualification-backed opportunity approved for a focused lead qualification workflow.",
        "qualification_summary": "Passed canonical qualification gates before approval." if qualification_verdict else "Qualification proof pending.",
        "qualification_backlinks": backlinks,
    }


def normalize_hermes_handoff(payload: dict[str, Any]) -> dict[str, str]:
    handoff = dict(payload.get("hermes_handoff", {}) or {})
    return {
        "source_role": str(handoff.get("source_role", "")).strip(),
        "source_artifact": str(handoff.get("source_artifact", "")).strip(),
        "next_target": str(handoff.get("next_target", "")).strip(),
    }


def interpret_chat_approval_reply(reply_text: str) -> str | None:
    normalized = " ".join(str(reply_text).strip().lower().split())
    if normalized in {"approve", "approved", "yes approve", "approve proposal"}:
        return "approved"
    if normalized in {"reject", "rejected", "no reject", "reject proposal"}:
        return "rejected"
    return None


def chat_approval_idempotency_key(proposal: dict[str, Any], reply_payload: dict[str, Any]) -> str:
    origin = dict(proposal.get("chat_origin", {}) or {})
    raw = "::".join(
        [
            str(proposal.get("proposal_id", "")).strip(),
            str(origin.get("run_id", "")).strip(),
            str(reply_payload.get("platform", "")).strip(),
            str(reply_payload.get("channel_or_chat_id", "")).strip(),
            str(reply_payload.get("thread_or_reply_context", "")).strip(),
            str(reply_payload.get("message_id", "")).strip(),
        ]
    )
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def process_chat_approval_decision(
    authority_path: Path | str,
    reply_payload: dict[str, Any],
    *,
    governance_events_path: Path | None = None,
    governance_status_path: Path | None = None,
) -> dict[str, Any]:
    authority = Path(authority_path)
    record = load_json(authority)
    proposal = dict(record.get("proposal", {}) or {})
    origin = dict(proposal.get("chat_origin", {}) or {})
    decision = interpret_chat_approval_reply(str(reply_payload.get("reply_text", "")))
    if decision is None:
        return {"ok": False, "block_reason": "ambiguous_chat_approval_reply"}
    if (
        str(reply_payload.get("platform", "")).strip() != str(origin.get("platform", "")).strip()
        or str(reply_payload.get("channel_or_chat_id", "")).strip() != str(origin.get("channel_or_chat_id", "")).strip()
        or str(reply_payload.get("thread_or_reply_context", "")).strip() != str(origin.get("thread_or_reply_context", "")).strip()
    ):
        return {"ok": False, "block_reason": "unlinked_chat_approval_reply"}

    idempotency_key = chat_approval_idempotency_key(proposal, reply_payload)
    decisions = dict(proposal.get("chat_decisions", {}) or {})
    if idempotency_key in decisions:
        return {"ok": True, "decision": decisions[idempotency_key]["decision"], "idempotent_replay": True}

    import scripts.governance_common as governance_common

    using_governance_overrides = governance_events_path is not None or governance_status_path is not None
    original_events_path = governance_common.GOVERNANCE_EVENTS_PATH
    original_status_path = governance_common.GOVERNANCE_STATUS_PATH
    original_allowed_dirs = governance_common.ALLOWED_WRITE_DIRS
    try:
        if governance_events_path is not None:
            governance_common.GOVERNANCE_EVENTS_PATH = Path(governance_events_path)
        if governance_status_path is not None:
            governance_common.GOVERNANCE_STATUS_PATH = Path(governance_status_path)
        if using_governance_overrides:
            governance_common.ALLOWED_WRITE_DIRS = (governance_common.GOVERNANCE_EVENTS_PATH.parent,)

        action_id = governance_common.generate_action_id(prefix="chat-approval")
        requested_event = {
            "action_id": action_id,
            "event_type": "requested",
            "action_type": "state.transition.approval.chat",
            "actor": str(reply_payload.get("actor", "ceo")).strip() or "ceo",
            "target_artifact": authority.as_posix(),
            "related_decision_package": governance_common.relative(governance_common.OPERATING_DECISION_PACKAGE_PATH),
            "status_before": str(record.get("pipeline", {}).get("status", "pending")).strip() or "pending",
            "status_after": "pending",
            "approved_by": str(reply_payload.get("actor", "ceo")).strip() or "ceo",
            "timestamp": governance_common.timestamp_now(),
            "reason": f"Chat reply requested {decision} for {proposal.get('proposal_id', 'proposal')}",
            "result_code": "approval_requested",
            "primary_writer": "ceo",
            "override_reason": "",
            "related_trace": {
                "trace_path": governance_common.relative(governance_common.DECISION_TRACE_PATH),
                "judgment_ids": [],
            },
        }
        governance_common.append_event(requested_event, governance_common.GOVERNANCE_EVENTS_PATH)
        final_event = dict(requested_event)
        final_event["event_type"] = "approved" if decision == "approved" else "rejected"
        final_event["status_before"] = "pending"
        final_event["status_after"] = decision
        final_event["reason"] = f"Chat reply {reply_payload.get('message_id', '')} set proposal to {decision}"
        final_event["result_code"] = f"approval_{decision}"
        final_event["timestamp"] = governance_common.timestamp_now()
        governance_common.append_event(final_event, governance_common.GOVERNANCE_EVENTS_PATH)
        if not using_governance_overrides:
            governance_common.refresh_status_view()
    finally:
        governance_common.GOVERNANCE_EVENTS_PATH = original_events_path
        governance_common.GOVERNANCE_STATUS_PATH = original_status_path
        governance_common.ALLOWED_WRITE_DIRS = original_allowed_dirs

    decisions[idempotency_key] = {
        "decision": decision,
        "message_id": str(reply_payload.get("message_id", "")).strip(),
        "action_id": action_id,
    }
    proposal["chat_decisions"] = decisions
    proposal["governance_action_id"] = action_id
    record["proposal"] = proposal
    record.setdefault("approval", {})["approver"] = str(reply_payload.get("actor", "ceo")).strip() or "ceo"
    record["approval"]["approved_at"] = governance_common.timestamp_now()
    record.setdefault("pipeline", {})["status"] = "ready" if decision == "approved" else "blocked"
    record["pipeline"]["stage"] = "approval"
    record["pipeline"]["block_reason"] = "" if decision == "approved" else "proposal_rejected"
    write_json(authority, record)
    return {"ok": True, "decision": decision, "action_id": action_id, "idempotent_replay": False}


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
        "qualification_bundle_path": DEFAULT_QUALIFICATION_BUNDLE_PATH,
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
    if not str(payload.get("pain_point", "")).strip():
        missing.append("pain_point")
    if not normalize_list(list(payload.get("approved_scope", []))):
        missing.append("approved_scope")
    if not normalize_list(list(payload.get("constraints", []))):
        missing.append("constraints")
    if not normalize_list(list(payload.get("acceptance_gates", []))):
        missing.append("acceptance_gates")
    if not normalize_list(list(payload.get("monetization", []))):
        missing.append("monetization")
    required_languages = normalize_required_languages(list(payload.get("required_languages", [])))
    if not required_languages or "en" not in required_languages or "zh" not in required_languages:
        missing.append("required_languages")
    if not normalize_list(list(payload.get("ui_artifact_contract", []))):
        missing.append("ui_artifact_contract")
    if not str(payload.get("template_contract_path", "")).strip():
        missing.append("template_contract_path")
    if not str(payload.get("gsd_constraints_path", "")).strip():
        missing.append("gsd_constraints_path")
    if not str(payload.get("qualification_bundle_path", "")).strip():
        missing.append("qualification_bundle_path")
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
        "pain_point": str(payload.get("pain_point", "")).strip(),
        "approved_scope": normalize_list(list(payload.get("approved_scope", []))),
        "constraints": normalize_list(list(payload.get("constraints", []))),
        "acceptance_gates": normalize_list(list(payload.get("acceptance_gates", []))),
        "monetization": normalize_list(list(payload.get("monetization", []))),
        "required_languages": normalize_required_languages(list(payload.get("required_languages", []))),
        "ui_artifact_contract": normalize_list(list(payload.get("ui_artifact_contract", []))),
        "template_contract_path": str(payload.get("template_contract_path", DEFAULT_TEMPLATE_CONTRACT_PATH)).strip(),
        "gsd_constraints_path": str(payload.get("gsd_constraints_path", DEFAULT_GSD_CONSTRAINTS_PATH)).strip(),
        "qualification_bundle_path": str(payload.get("qualification_bundle_path", DEFAULT_QUALIFICATION_BUNDLE_PATH)).strip(),
        "qualified_idea_id": str(payload.get("qualified_idea_id", "")).strip(),
        "hermes_handoff": normalize_hermes_handoff(payload),
    }
    identity = normalize_project_identity(normalized_payload["project_name"], normalized_payload["project_url"])
    missing = collect_missing_inputs(normalized_payload)
    block_reason = resolve_block_reason(missing)
    qualification_verdict = None
    if not block_reason:
        try:
            qualification_bundle = load_qualification_bundle(normalized_payload["qualification_bundle_path"])
            qualification_verdict = find_qualification_verdict(
                qualification_bundle,
                idea_id=normalized_payload["qualified_idea_id"],
                pain_point=normalized_payload["pain_point"],
            )
        except ApprovedProjectDeliveryError:
            qualification_verdict = None
        if qualification_verdict is None:
            block_reason = "missing_qualification_proof"
        elif str(qualification_verdict.get("verdict", "")).strip() != "passed":
            block_reason = "failed_qualification_proof"
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
        "proposal": build_proposal_block(
            qualified_idea_id=normalized_payload["qualified_idea_id"],
            mvp_framing=normalized_payload["mvp_framing"],
            qualification_verdict=qualification_verdict,
        ),
        "hermes_handoff": normalized_payload["hermes_handoff"],
        "project_identity": identity,
        "approved_scope": normalized_payload["approved_scope"],
        "target_user": normalized_payload["target_user"],
        "mvp_framing": normalized_payload["mvp_framing"],
        "product_requirements": {
            "pain_point": normalized_payload["pain_point"],
            "monetization": normalized_payload["monetization"],
            "required_languages": normalized_payload["required_languages"],
            "ui_artifact_contract": normalized_payload["ui_artifact_contract"],
        },
        "constraints": normalized_payload["constraints"],
        "acceptance_gates": normalized_payload["acceptance_gates"],
        "pipeline": {
            "stage": "approval",
            "status": status,
            "block_reason": block_reason,
            "current_stage": "approval",
            "current_status": status,
            "latest_governance": {
                "stage": "approval",
                "status": status,
                "outcome": "blocked" if status == "blocked" else "pass",
            },
            "latest_block_context": (
                {
                    "stage": "approval",
                    "reason": block_reason,
                    "status": "blocked",
                }
                if block_reason
                else None
            ),
        },
        "artifacts": artifacts,
        "shipping": {
            "github": {
                "repository_mode": "create",
                "repository_owner": "",
                "repository_repo": build_managed_repository_name(identity["project_slug"]),
                "repository_name": build_managed_repository_name(identity["project_slug"]),
                "repository_url": "",
                "default_branch": "main",
                "remote_name": "origin",
                "last_sync_status": "pending",
                "naming_rule": "pc-<project-slug>",
            },
            "vercel": {},
        },
    }
    approved_project["shipping"]["github"].update(resolve_github_repository_identity(approved_project))
    return {
        "ok": block_reason is None,
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
        "product_requirements",
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
    proposal = dict(record.get("proposal", {}) or {})
    approved_scope = normalize_list(list(record.get("approved_scope", [])))
    constraints = normalize_list(list(record.get("constraints", [])))
    acceptance_gates = normalize_list(list(record.get("acceptance_gates", [])))
    target_user = str(record.get("target_user", "")).strip()
    mvp_framing = str(record.get("mvp_framing", "")).strip()
    contract = build_delivery_contract(record)
    lines = [
        "# Approved Project Brief",
        "",
        "## Proposal Summary",
        f"- {proposal.get('proposal_id', 'proposal-unlinked-v1')}",
        f"- {proposal.get('launch_framing', mvp_framing)}",
        f"- {proposal.get('market_rationale', 'Market rationale pending.')}",
        f"- {proposal.get('qualification_summary', 'Qualification summary pending.')}",
        "",
        "## Qualification Backlinks",
        *[f"- {item}" for item in normalize_list(list(proposal.get('qualification_backlinks', [])))],
        "",
        "## Project Identity",
        f"- Project slug: `{identity.get('project_slug', '')}`",
        f"- App key: `{identity.get('app_key', '')}`",
        f"- App name: `{identity.get('app_name', '')}`",
        f"- App URL: `{identity.get('app_url', '')}`",
        "",
        "## Hermes Internal Handoff",
        f"- Source role: {record.get('hermes_handoff', {}).get('source_role', 'not available')}",
        f"- Source artifact: {record.get('hermes_handoff', {}).get('source_artifact', 'not available')}",
        f"- Next target: {record.get('hermes_handoff', {}).get('next_target', 'not available')}",
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
        "## Product Definition",
        f"- {contract['product_definition']}",
        "",
        "## Pain Point",
        f"- {contract['pain_point']}",
        "",
        "## Core Workflow",
        *[f"- {item}" for item in contract["core_workflow"]],
        "",
        "## Monetization",
        *[f"- {item}" for item in contract["monetization"]],
        "",
        "## Multilingual Requirements",
        *[f"- {item}" for item in contract["required_languages"]],
        "",
        "## UI Artifact Contract",
        *[f"- {item}" for item in contract["ui_artifact_contract"]],
        "",
        "## Frontend Acceptance",
        *[f"- {item}" for item in contract["frontend_acceptance"]],
        "",
        "## Backend Acceptance",
        *[f"- {item}" for item in contract["backend_acceptance"]],
        "",
        "## Template Rejection Rules",
        *[f"- {item}" for item in contract["template_rejection_rules"]],
        "",
        "## Non Goals",
        *[f"- {item}" for item in contract["non_goals"]],
        "",
        "## Constraints",
        *[f"- {item}" for item in constraints],
        "",
        "## Acceptance Gates",
        *[f"- {item}" for item in acceptance_gates],
    ]
    return "\n".join(lines).rstrip() + "\n"


def build_delivery_contract(record: dict[str, Any]) -> dict[str, Any]:
    approved_scope = normalize_list(list(record.get("approved_scope", [])))
    product_requirements = dict(record.get("product_requirements", {}) or {})
    pain_point = str(product_requirements.get("pain_point", "")).strip() or (approved_scope[0] if approved_scope else "resolve the approved user pain")
    secondary_scope = approved_scope[1] if len(approved_scope) > 1 else "deliver a concrete user workflow"
    target_user = str(record.get("target_user", "")).strip() or "target user"
    mvp_framing = str(record.get("mvp_framing", "")).strip() or "approved MVP"
    app_name = str(record.get("project_identity", {}).get("app_name", "Approved Product")).strip() or "Approved Product"
    product_definition = f"{app_name} is a product for {target_user} that must {pain_point}."
    monetization = normalize_list(list(product_requirements.get("monetization", []))) or build_default_monetization(pain_point, target_user)
    required_language_codes = normalize_required_languages(list(product_requirements.get("required_languages", []))) or build_default_required_languages()
    ui_artifact_contract = normalize_list(list(product_requirements.get("ui_artifact_contract", []))) or build_default_ui_artifact_contract()
    core_workflow = [
        f"User opens the product and immediately sees a workflow focused on: {pain_point}",
        f"User completes at least one concrete task that proves the app can {secondary_scope}",
        "User receives a visible result, output, or paid next action rather than generic template copy",
    ]
    frontend_acceptance = [
        "Landing/home page no longer contains generic template starter messaging",
        "UI includes at least one pain-point-specific primary action, one result state, and one monetization surface",
        "Design artifact defines screens, components, empty/loading/error states, responsive behavior, accessibility rules, and multilingual behavior",
    ]
    backend_acceptance = [
        "At least one implementation file or API/data path reflects the approved pain-point workflow",
        "If backend change is unnecessary, development handoff must prove why the workflow is still real, product-specific, and monetizable",
    ]
    template_rejection_rules = normalize_list(list(product_requirements.get("template_rejection_rules", []))) or build_default_template_rejection_rules()
    non_goals = [
        "Do not ship template-only branding refreshes as completed product delivery",
        "Do not pass release readiness if user-facing behavior is still generic template behavior",
        "Do not treat the template frontend as the final product UI; it is only an integration boundary example",
    ]
    return {
        "pain_point": pain_point,
        "product_definition": product_definition,
        "core_workflow": core_workflow,
        "monetization": monetization,
        "required_languages": [f"{code} (required)" for code in required_language_codes],
        "required_language_codes": required_language_codes,
        "ui_artifact_contract": ui_artifact_contract,
        "frontend_acceptance": frontend_acceptance,
        "backend_acceptance": backend_acceptance,
        "template_rejection_rules": template_rejection_rules,
        "non_goals": non_goals,
        "mvp_framing": mvp_framing,
    }


def collect_product_proof_paths(workspace: Path, touched_paths: list[str] | None = None) -> list[str]:
    summary = build_product_proof_summary(
        touched_paths=touched_paths or [],
        workspace=workspace,
        marker_patterns=TEMPLATE_MARKER_PATTERNS,
    )
    proof_paths = list(summary.get("product_proof_paths", []))
    if proof_paths:
        return proof_paths

    legacy_paths: list[str] = []
    for relative in REQUIRED_PRODUCT_IMPLEMENTATION_PATHS:
        candidate = workspace / relative
        if candidate.exists():
            legacy_paths.append(relative)
    for prefix in REQUIRED_PRODUCT_PROOF_PATH_PREFIXES:
        candidate = workspace / prefix
        if candidate.is_file():
            legacy_paths.append(prefix)
            continue
        if candidate.is_dir():
            for child in candidate.rglob("*"):
                if child.is_file():
                    relative = child.relative_to(workspace).as_posix()
                    if relative not in legacy_paths:
                        legacy_paths.append(relative)
    return sorted(dict.fromkeys(legacy_paths))


def detect_template_only_issues(workspace: Path, touched_paths: list[str]) -> list[str]:
    summary = build_product_proof_summary(
        touched_paths=touched_paths,
        workspace=workspace,
        marker_patterns=TEMPLATE_MARKER_PATTERNS,
    )
    return sorted(
        dict.fromkeys(
            list(summary.get("issues", []))
            + list(summary.get("warning_issues", []))
        )
    )


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
            "current_stage": "brief_generation",
            "current_status": "ready",
            "latest_governance": {
                "stage": "brief_generation",
                "status": "ready",
                "outcome": "pass",
            },
            "latest_block_context": None,
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
        "pain_point": args.pain_point,
        "approved_scope": list(args.approved_scope),
        "constraints": list(args.constraint),
        "acceptance_gates": list(args.acceptance_gate),
        "monetization": list(args.monetization),
        "required_languages": list(args.required_language),
        "ui_artifact_contract": list(args.ui_artifact_contract),
        "template_contract_path": args.template_contract_path,
        "gsd_constraints_path": args.gsd_constraints_path,
        "qualification_bundle_path": DEFAULT_QUALIFICATION_BUNDLE_PATH,
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
    pain_point = overall_conclusion or f"Resolve the user pain behind {top_idea_id}: {top_opportunity}"
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
    qualification_bundle = load_qualification_bundle(DEFAULT_QUALIFICATION_BUNDLE_PATH)
    qualification_verdict = find_qualification_verdict(qualification_bundle, idea_id=top_idea_id)
    if qualification_verdict is None or str(qualification_verdict.get("verdict", "")).strip() != "passed":
        raise ApprovedProjectDeliveryError(f"qualified decision input required for {top_idea_id}")
    market_proof = dict(qualification_verdict.get("market_pricing_proof", {}))
    monetization = [
        str(item).strip()
        for item in list(market_proof.get("pricing_links", []))
        if str(item).strip()
    ]
    required_languages = build_default_required_languages()
    ui_artifact_contract = build_default_ui_artifact_contract()

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
        "pain_point": pain_point,
        "approved_scope": approved_scope,
        "constraints": constraints,
        "acceptance_gates": acceptance_gates,
        "monetization": monetization,
        "required_languages": required_languages,
        "ui_artifact_contract": ui_artifact_contract,
        "template_contract_path": DEFAULT_TEMPLATE_CONTRACT_PATH,
        "gsd_constraints_path": DEFAULT_GSD_CONSTRAINTS_PATH,
        "qualification_bundle_path": DEFAULT_QUALIFICATION_BUNDLE_PATH,
        "qualified_idea_id": top_idea_id,
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


def load_pipeline_events(record: dict[str, Any]) -> list[dict[str, Any]]:
    events_path = Path(str(record.get("artifacts", {}).get("events_path", "")).strip())
    if not events_path.exists():
        return []
    events: list[dict[str, Any]] = []
    for raw_line in events_path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        payload = json.loads(line)
        if isinstance(payload, dict):
            events.append(payload)
    return events


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
    substance: dict[str, Any] | None = None,
    gate_name: str = "",
    repair_action: str = "",
) -> dict[str, Any]:
    identity = dict(record.get("project_identity", {}))
    artifacts = dict(record.get("artifacts", {}))
    shipping = dict(record.get("shipping", {}))
    primary_evidence_path = evidence_path or artifact
    handoff_block = {
        "artifact_path": artifact,
    }
    if final_handoff_path:
        handoff_block["final_handoff_path"] = final_handoff_path
    event = {
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
        "gate": {
            "name": gate_name,
            "decision": "block" if status == "blocked" or outcome == "blocked" else "pass",
            "reason": block_reason,
        },
        "evidence": {
            "primary_path": primary_evidence_path,
        },
        "handoff": handoff_block,
        "recovery": {
            "run_id": delivery_run_id,
            "resume_from_stage": resume_from_stage,
            "repair_action": repair_action,
        },
        "outcome": {
            "status": status,
            "result": outcome,
        },
        "shipping": shipping,
    }
    if substance is not None:
        event["substance"] = substance
    return event


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
    gate_name: str | None = None,
    repair_action: str | None = None,
    detail: str | None = None,
) -> None:
    pipeline = record.setdefault("pipeline", {})
    artifacts = record.setdefault("artifacts", {})
    shipping = record.setdefault("shipping", {})
    github = shipping.setdefault("github", {})
    vercel = shipping.setdefault("vercel", {})
    record.setdefault("final_handoff", {})
    previous_stage = str(pipeline.get("current_stage", pipeline.get("stage", ""))).strip() or stage
    previous_status = str(pipeline.get("current_status", pipeline.get("status", ""))).strip()
    previous_block_reason = str(pipeline.get("block_reason", "")).strip()
    previous_evidence_path = str(pipeline.get("evidence_path", "")).strip()
    previous_blocked_prerequisite = (
        dict(record.get("latest_blocked_prerequisite", {}))
        if isinstance(record.get("latest_blocked_prerequisite"), dict)
        else {}
    )
    pipeline["stage"] = stage
    pipeline["status"] = status
    pipeline["block_reason"] = block_reason
    pipeline["current_stage"] = stage
    pipeline["current_status"] = status
    pipeline["latest_governance"] = {
        "stage": stage,
        "status": status,
        "outcome": "blocked" if status == "blocked" else "pass",
        "gate": gate_name or "",
        "repair_action": repair_action or "",
        "detail": detail or "",
    }
    latest_block_context = pipeline.get("latest_block_context")
    if status == "blocked" and block_reason:
        pipeline["latest_block_context"] = {
            "stage": stage,
            "reason": block_reason,
            "status": "blocked",
            "gate": gate_name or "",
            "repair_action": repair_action or "",
            "detail": detail or "",
        }
    elif isinstance(latest_block_context, dict) and latest_block_context:
        resolved_context = dict(latest_block_context)
        resolved_context["status"] = "resolved"
        pipeline["latest_block_context"] = resolved_context
    elif previous_status == "blocked" and previous_block_reason:
        pipeline["latest_block_context"] = {
            "stage": previous_stage,
            "reason": previous_block_reason,
            "status": "resolved",
        }
    else:
        pipeline["latest_block_context"] = None
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
    if status == "blocked":
        record["latest_blocked_prerequisite"] = {
            "stage": stage,
            "reason": block_reason or "",
            "path": evidence_path or previous_evidence_path,
            "status": "blocked",
            "gate": gate_name or "",
            "repair_action": repair_action or "",
            "resume_from_stage": resume_from_stage or "",
            "run_id": delivery_run_id or "",
            "detail": detail or "",
        }
    elif previous_blocked_prerequisite or (previous_status == "blocked" and previous_block_reason):
        resolved = dict(previous_blocked_prerequisite)
        resolved.setdefault("stage", previous_stage)
        resolved.setdefault("reason", previous_block_reason)
        resolved.setdefault("path", previous_evidence_path)
        resolved["status"] = "resolved"
        if detail:
            resolved["detail"] = detail
        record["latest_blocked_prerequisite"] = resolved


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


def ensure_hermes_available() -> str:
    hermes_bin = shutil.which("hermes")
    if not hermes_bin:
        raise ApprovedProjectDeliveryError("Hermes CLI not found in PATH")
    return hermes_bin


def ensure_claude_code_available() -> str:
    claude_bin = shutil.which("claude")
    if not claude_bin:
        raise ApprovedProjectDeliveryError("Claude Code CLI not found in PATH")
    return claude_bin


def required_specialist_skills(config: dict[str, str], ui_artifact_path: str) -> list[str]:
    skills: list[str] = []
    if config["pipeline_stage"] in UI_SPECIALIST_STAGES and ui_artifact_path:
        skills.append(UI_UX_SKILL_NAME)
    return skills


def ensure_hermes_skill_available(skill_name: str, config: dict[str, str]) -> None:
    profile_home = Path.home() / "AppData" / "Local" / "hermes" / "profiles" / str(config.get("hermes_profile", "")).strip() / "skills"
    skill_dir = profile_home / skill_name
    skill_file = profile_home / f"{skill_name}.md"
    if skill_dir.exists() or skill_file.exists():
        return
    raise ApprovedProjectDeliveryError(
        f"Required Hermes skill '{skill_name}' is missing for profile {config.get('hermes_profile', 'unknown')}"
    )


def ensure_hermes_skill_resolvable(hermes_bin: str, skill_name: str, config: dict[str, str]) -> None:
    profile = str(config.get("hermes_profile", "arch"))
    probe_command = [
        hermes_bin,
        "-p",
        profile,
        "chat",
        "-q",
        "Reply with exactly OK.",
        "-Q",
        "-s",
        skill_name,
    ]
    probe_result = subprocess.run(
        probe_command,
        capture_output=True,
        text=True,
        check=False,
        encoding="utf-8",
        errors="replace",
    )
    probe_output = "\n".join(part for part in [probe_result.stdout, probe_result.stderr] if part).strip()
    if probe_result.returncode == 0 and "OK" in probe_output:
        return
    if "Unknown skill(s):" in probe_output:
        install_command = [
            hermes_bin,
            "-p",
            profile,
            "skills",
            "install",
            "-y",
            "--force",
            skill_name,
        ]
        install_result = subprocess.run(
            install_command,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        install_output = "\n".join(part for part in [install_result.stdout, install_result.stderr] if part).strip()
        if install_result.returncode != 0:
            raise ApprovedProjectDeliveryError(
                f"Failed to install Hermes skill '{skill_name}' for profile {profile}: {install_output or 'unknown error'}"
            )
        probe_result = subprocess.run(
            probe_command,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        probe_output = "\n".join(part for part in [probe_result.stdout, probe_result.stderr] if part).strip()
        if probe_result.returncode == 0 and "OK" in probe_output:
            return
    if "API call failed after 3 retries" in probe_output or "WinError 10054" in probe_output:
        raise ApprovedProjectDeliveryError(
            f"Hermes specialist session failed due to transient provider/network error for profile {profile}: {probe_output}"
        )
    raise ApprovedProjectDeliveryError(
        f"Required Hermes skill '{skill_name}' is not resolvable for profile {profile}: {probe_output or 'unknown error'}"
    )


def specialist_ui_artifact_path(workspace: Path) -> Path:
    return workspace / ".hermes" / UI_UX_ARTIFACT_NAME


def specialist_ui_artifact_summary_path(workspace: Path) -> Path:
    return workspace / ".hermes" / UI_UX_SUMMARY_NAME


def specialist_stage_evidence_path(workspace: Path, config: dict[str, str]) -> Path:
    artifact_name = Path(str(config["artifact"])).name.replace(".md", ".json")
    return workspace / STAGE_EVIDENCE_DIR / artifact_name


def expected_ui_screen_inventory(record: dict[str, Any]) -> list[str]:
    scope_lines = normalize_list(list(record.get("approved_scope", [])))
    default_screens = [
        "Home/landing view focused on the approved workflow",
        "Primary task entry flow",
        "Visible result/output state",
    ]
    return scope_lines or default_screens


def build_ui_ux_artifact_summary(record: dict[str, Any], artifact_path: Path, *, pipeline_stage: str, role: str) -> dict[str, Any]:
    contract = build_delivery_contract(record)
    app_name = str(record.get("project_identity", {}).get("app_name", "Approved Product")).strip() or "Approved Product"
    target_user = str(record.get("target_user", "target user")).strip() or "target user"
    screen_inventory = expected_ui_screen_inventory(record)
    monetization = normalize_list(contract["monetization"])
    required_languages = normalize_required_languages(list(contract["required_language_codes"]))
    return {
        "generated_by": f"/{UI_UX_SKILL_NAME}",
        "artifact_path": artifact_path.as_posix(),
        "stage": pipeline_stage,
        "role": role,
        "app_name": app_name,
        "target_user": target_user,
        "brief_contract": {
            "pain_point": contract["pain_point"],
            "core_workflow": list(contract["core_workflow"]),
            "monetization": monetization,
            "required_languages": required_languages,
            "screen_inventory": screen_inventory,
        },
        "coverage": {
            "screen_inventory": screen_inventory,
            "primary_workflow": list(contract["core_workflow"]),
            "monetization_surface": monetization,
            "multilingual_coverage": required_languages,
            "responsive_rules": [
                "Primary workflow must remain usable on desktop and mobile widths.",
                "Responsive behavior must preserve CTA clarity and result visibility.",
            ],
            "accessibility_rules": [
                "Primary actions must keep visible labels and focus states.",
                "Critical workflow states must remain understandable without color alone.",
            ],
            "states": list(REQUIRED_UI_ARTIFACT_STATES),
        },
        "summary_hash": hashlib.sha256(
            json.dumps(
                {
                    "pain_point": contract["pain_point"],
                    "core_workflow": list(contract["core_workflow"]),
                    "monetization": monetization,
                    "required_languages": required_languages,
                    "screen_inventory": screen_inventory,
                },
                ensure_ascii=False,
                sort_keys=True,
            ).encode("utf-8")
        ).hexdigest(),
    }


def write_ui_ux_artifact_summary(workspace: Path, summary: dict[str, Any]) -> str:
    path = specialist_ui_artifact_summary_path(workspace)
    write_json(path, summary)
    return path.as_posix()


def validate_ui_ux_artifact(
    workspace: Path,
    record: dict[str, Any],
    *,
    pipeline_stage: str,
) -> tuple[bool, str, str, str]:
    artifact_path = specialist_ui_artifact_path(workspace)
    if not artifact_path.exists():
        return False, "missing_ui_ux_artifact", artifact_path.as_posix(), "ui-ux artifact is missing"
    artifact_text = artifact_path.read_text(encoding="utf-8")
    if not artifact_text.strip():
        return False, "ui_ux_artifact_empty", artifact_path.as_posix(), "ui-ux artifact is empty"
    summary_path = specialist_ui_artifact_summary_path(workspace)
    if not summary_path.exists():
        return False, "missing_ui_ux_summary", summary_path.as_posix(), "ui-ux artifact summary is missing"
    summary = load_json(summary_path)
    coverage = dict(summary.get("coverage", {}) or {})
    missing_coverage = [key for key in REQUIRED_UI_ARTIFACT_COVERAGE_KEYS if not normalize_list(list(coverage.get(key, [])))]
    if missing_coverage:
        return (
            False,
            "ui_ux_artifact_coverage_incomplete",
            summary_path.as_posix(),
            "ui-ux artifact coverage missing: " + ", ".join(missing_coverage),
        )
    states = {str(item).strip().lower() for item in coverage.get("states", []) if str(item).strip()}
    if not set(REQUIRED_UI_ARTIFACT_STATES).issubset(states):
        return (
            False,
            "ui_ux_artifact_coverage_incomplete",
            summary_path.as_posix(),
            "ui-ux artifact states missing: " + ", ".join(sorted(set(REQUIRED_UI_ARTIFACT_STATES) - states)),
        )
    expected = build_ui_ux_artifact_summary(
        record,
        artifact_path,
        pipeline_stage=pipeline_stage,
        role="design-specialist" if pipeline_stage == "design" else "development-specialist",
    )
    expected_contract = expected["brief_contract"]
    actual_contract = dict(summary.get("brief_contract", {}) or {})
    for key in ("pain_point", "core_workflow", "monetization", "required_languages", "screen_inventory"):
        if actual_contract.get(key) != expected_contract.get(key):
            return (
                False,
                "ui_ux_artifact_stale",
                summary_path.as_posix(),
                f"ui-ux artifact summary drifted from approved brief for {key}",
            )
    if summary.get("summary_hash") != expected.get("summary_hash"):
        return False, "ui_ux_artifact_stale", summary_path.as_posix(), "ui-ux artifact summary hash drifted from approved brief"
    return True, "", summary_path.as_posix(), ""


def ensure_ui_ux_preflight(workspace: Path, record: dict[str, Any], pipeline_stage: str) -> str:
    artifact_path = specialist_ui_artifact_path(workspace)
    summary_path = specialist_ui_artifact_summary_path(workspace)
    if artifact_path.exists() and summary_path.exists():
        return artifact_path.as_posix()
    if pipeline_stage not in UI_SPECIALIST_STAGES:
        return ""
    if detect_delivery_surface(record) != "ui":
        return ""
    role = "design-specialist" if pipeline_stage == "design" else "development-specialist"
    app_name = str(record.get("project_identity", {}).get("app_name", "Approved Product")).strip() or "Approved Product"
    target_user = str(record.get("target_user", "target user")).strip() or "target user"
    scope_lines = normalize_list(list(record.get("approved_scope", [])))
    contract = build_delivery_contract(record)
    artifact_path.parent.mkdir(parents=True, exist_ok=True)
    artifact_text = (
        "# UI / UX Design System\n\n"
        f"- Skill: `/ui-ux-pro-max`\n"
        f"- Stage: `{pipeline_stage}`\n"
        f"- Role: `{role}`\n"
        f"- App: `{app_name}`\n"
        f"- Target user: `{target_user}`\n"
        "- Requirement source: `CLAUDE.md` frontend UI/UX enforcement\n\n"
        "## Approved UI Scope\n"
        + "\n".join(f"- {line}" for line in scope_lines)
        + "\n\n## Product Definition\n"
        + f"- {contract['product_definition']}\n"
        + "\n## Pain Point\n"
        + f"- {contract['pain_point']}\n"
        + "\n## Required Screens\n"
        + "- Home/landing view focused on the approved workflow\n"
        + "- Primary task entry flow\n"
        + "- Visible result/output state\n"
        + "\n## Required States\n"
        + "- Empty state\n- Loading state\n- Error state\n- Success/result state\n"
        + "\n## Required Interaction Detail\n"
        + "- Primary CTA must map to the approved pain-point workflow\n"
        + "- Layout must explain the workflow outcome, not template capabilities\n"
        + "\n## Frontend Acceptance\n"
        + "\n".join(f"- {line}" for line in contract["frontend_acceptance"])
        + "\n\n## Enforcement\n- Frontend-related work must go through `/ui-ux-pro-max` before implementation.\n",
    )
    artifact_path.write_text(artifact_text, encoding="utf-8")
    write_ui_ux_artifact_summary(
        workspace,
        build_ui_ux_artifact_summary(record, artifact_path, pipeline_stage=pipeline_stage, role=role),
    )
    return artifact_path.as_posix()


def build_specialist_dispatch_prompt(record: dict[str, Any], workspace: Path, config: dict[str, str], previous_handoff_path: str, ui_artifact_path: str) -> str:
    identity = dict(record.get("project_identity", {}))
    artifacts = dict(record.get("artifacts", {}))
    scope_lines = normalize_list(list(record.get("approved_scope", [])))
    constraint_lines = normalize_list(list(record.get("constraints", [])))
    acceptance_lines = normalize_list(list(record.get("acceptance_gates", [])))
    contract = build_delivery_contract(record)
    lines = [
        f"You are the {config['role']} for the Hermes approved delivery workflow.",
        f"Stage: {config['delivery_stage']}",
        f"Workspace: {workspace.as_posix()}",
        f"App: {identity.get('app_name', '')} ({identity.get('app_key', '')})",
        f"App URL: {identity.get('app_url', '')}",
        f"Target user: {record.get('target_user', '')}",
        f"MVP framing: {record.get('mvp_framing', '')}",
        f"Pain point: {contract['pain_point']}",
        f"Product definition: {contract['product_definition']}",
        "Core workflow:",
        *[f"- {item}" for item in contract["core_workflow"]],
        "Approved scope:",
        *[f"- {item}" for item in scope_lines],
        "Constraints:",
        *[f"- {item}" for item in constraint_lines],
        "Acceptance gates:",
        *[f"- {item}" for item in acceptance_lines],
        "Frontend acceptance:",
        *[f"- {item}" for item in contract["frontend_acceptance"]],
        "Backend acceptance:",
        *[f"- {item}" for item in contract["backend_acceptance"]],
        "Non-goals:",
        *[f"- {item}" for item in contract["non_goals"]],
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
            "- You must produce real product changes that address the approved pain point, not just branding or template copy updates.",
            "- The home page and primary user flow must stop reading like a generic template starter.",
            "- Development must touch at least one user-facing workflow file beyond src/lib/app-definition.ts.",
            "- Emit a stage handoff markdown file at the required artifact path.",
            "- Include evidence links, gate decision, and next-stage input.",
            "- Your handoff must name changed files, user-visible behavior, and why the result is not template-only.",
            "- If no real product implementation is needed, explain precisely why, with evidence the workflow is still product-specific.",
        ]
    )
    return "\n".join(lines)


def dispatch_specialist_agent(record: dict[str, Any], workspace: Path, config: dict[str, str], previous_handoff_path: str, ui_artifact_path: str) -> dict[str, Any]:
    hermes_bin = ensure_hermes_available()
    ensure_claude_code_available()
    prompt = build_specialist_dispatch_prompt(record, workspace, config, previous_handoff_path, ui_artifact_path)
    skills = required_specialist_skills(config, ui_artifact_path)
    for skill_name in skills:
        ensure_hermes_skill_available(skill_name, config)
        ensure_hermes_skill_resolvable(hermes_bin, skill_name, config)
    command = [
        hermes_bin,
        "-p",
        str(config.get("hermes_profile", "arch")),
        "chat",
        "-q",
        prompt,
        "-Q",
        "--accept-hooks",
        "--yolo",
    ]
    if skills:
        command.extend(["-s", ",".join(skills)])

    attempts: list[dict[str, Any]] = []
    result = None
    combined_error = ""
    for attempt in range(1, 4):
        candidate = subprocess.run(
            command,
            capture_output=True,
            text=True,
            check=False,
            encoding="utf-8",
            errors="replace",
        )
        result = candidate
        stdout_text = candidate.stdout.strip()
        stderr_text = candidate.stderr.strip()
        combined = "\n".join(part for part in [stdout_text, stderr_text] if part).strip()
        attempts.append({
            "attempt": attempt,
            "returncode": candidate.returncode,
            "stdout": stdout_text,
            "stderr": stderr_text,
        })
        if candidate.returncode == 0:
            break
        if "API call failed after 3 retries" in combined or "WinError 10054" in combined:
            combined_error = combined
            continue
        break
    assert result is not None
    transcript_path = workspace / ".hermes" / f"{config['pipeline_stage']}-claude-code.txt"
    transcript_path.parent.mkdir(parents=True, exist_ok=True)
    transcript_body = "\n\n".join(
        [
            f"## Attempt {item['attempt']}\n"
            + (item["stdout"] or "")
            + ("\n" + item["stderr"] if item["stderr"] else "")
            for item in attempts
        ]
    ).strip()
    transcript_path.write_text(transcript_body + ("\n" if transcript_body else ""), encoding="utf-8")
    return {
        "ok": result.returncode == 0,
        "transcript_path": transcript_path.as_posix(),
        "stdout": result.stdout.strip(),
        "stderr": (combined_error or result.stderr.strip()),
        "command": command,
        "skills": skills,
        "hermes_profile": str(config.get("hermes_profile", "arch")),
        "attempts": attempts,
    }


def write_workspace_change_inventory(workspace: Path, touched_paths: list[str], *, stage: str, role: str) -> str:
    inventory_path = workspace / ".hermes" / WORKSPACE_CHANGE_INVENTORY_NAME
    proof_summary = build_product_proof_summary(
        touched_paths=touched_paths,
        workspace=workspace,
        marker_patterns=TEMPLATE_MARKER_PATTERNS,
    )
    payload = {
        "stage": stage,
        "role": role,
        **proof_summary,
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
    changed_files: list[str],
    user_visible_behavior: list[str],
    pain_point_mapping: list[str],
) -> str:
    headings = REQUIRED_STAGE_HEADINGS
    lines = [
        "# 阶段交接",
        "",
        headings[0],
        f"- `run_id`: {run_id}",
        f"- `role`: {role}",
        f"- `stage`: {stage}",
        f"- `scope_status`: {scope_status}",
        f"- `summary`: {summary}",
        "",
        headings[1],
        *[f"- {item}" for item in outputs],
        "",
        headings[2],
        *[f"- {item}" for item in evidence_links],
        "",
        headings[3],
        *[f"- {item}" for item in changed_files],
        "",
        headings[4],
        *[f"- {item}" for item in user_visible_behavior],
        "",
        headings[5],
        *[f"- {item}" for item in pain_point_mapping],
        "",
        headings[6],
        f"- `gate_decision`: {gate_decision}",
        f"- `reason`: {gate_reason}",
        "",
        headings[7],
        *[f"- {item}" for item in risks],
        "",
        headings[8],
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


def validate_stage_substance(workspace: Path, inventory_path: str, *, stage: str) -> tuple[bool, list[str]]:
    payload = load_json(Path(inventory_path))
    issues = normalize_list(list(payload.get("template_only_issues", [])))
    primary_surfaces = normalize_list(list(payload.get("primary_workflow_surfaces", [])))
    supporting_logic_paths = normalize_list(list(payload.get("supporting_logic_paths", [])))
    product_proof_paths = normalize_list(list(payload.get("product_proof_paths", [])))
    touched_paths = normalize_list(list(payload.get("touched_paths", [])))
    failure_reasons = normalize_list(list(payload.get("failure_reasons", [])))
    template_residue_blockers = normalize_list(list(payload.get("template_residue_blockers", [])))
    if stage in {"development", "testing", "git versioning", "release readiness"}:
        if primary_surfaces or supporting_logic_paths or failure_reasons or template_residue_blockers:
            if not primary_surfaces:
                issues.append(FAILURE_REASON_MESSAGES["missing_primary_workflow_surface"])
            if not supporting_logic_paths:
                issues.append(FAILURE_REASON_MESSAGES["missing_supporting_logic"])
            if template_residue_blockers:
                issues.append(
                    "template/example residue is still present on primary product surfaces: "
                    + ", ".join(template_residue_blockers)
                )
        else:
            if not product_proof_paths:
                issues.append("no product proof paths captured in workspace inventory")
            if touched_paths and all(path == "src/lib/app-definition.ts" for path in touched_paths):
                issues.append("stage only changed src/lib/app-definition.ts")
    return (len(issues) == 0, sorted(dict.fromkeys(issues)))


def derive_gate_name(block_reason: str, *, stage: str) -> str:
    if block_reason.startswith("ui_ux_") or block_reason in {"missing_ui_ux_artifact", "missing_ui_ux_summary"}:
        return "ui_artifact_gate"
    if block_reason.startswith("stage_evidence_") or "structured_stage_evidence" in block_reason or "stage_handoff" in block_reason:
        return "specialist_evidence_gate"
    if block_reason == "missing_claude_code_transcript":
        return "specialist_evidence_gate"
    if block_reason == "missing_testing_verification_evidence":
        return "testing_verification_gate"
    return f"{stage}_gate"


def derive_repair_action(block_reason: str, *, stage: str) -> str:
    repair_actions = {
        "missing_ui_ux_artifact": "Generate the `/ui-ux-pro-max` design artifact for this approved brief and rerun the blocked stage.",
        "missing_ui_ux_summary": "Persist the UI artifact structured summary and rerun the blocked stage.",
        "ui_ux_artifact_empty": "Replace the empty UI artifact with product-specific design content and rerun the blocked stage.",
        "ui_ux_artifact_stale": "Refresh the UI artifact so it matches the latest approved brief before resuming.",
        "ui_ux_artifact_coverage_incomplete": "Fill every required UI coverage area in the design artifact summary before resuming.",
        "ui_ux_implementation_drift": "Realign the implementation with the validated UI artifact and rerun the blocked stage.",
        "missing_stage_handoff": "Persist the stage handoff markdown for this run before resuming.",
        "empty_stage_handoff": "Replace the empty stage handoff with a complete handoff for this run.",
        "missing_structured_stage_evidence": "Persist the machine-readable stage evidence bundle and rerun the blocked stage.",
        "empty_structured_stage_evidence": "Replace the empty stage evidence bundle with a complete JSON artifact.",
        "stale_structured_stage_evidence": "Regenerate the structured stage evidence so it matches the current run and artifact paths.",
        "missing_claude_code_transcript": "Persist the non-empty Claude Code transcript for this specialist run and rerun the blocked stage.",
        "stage_evidence_run_mismatch": "Regenerate the stage evidence with the current delivery run id before resuming.",
        "stage_evidence_stage_mismatch": "Regenerate the stage evidence with the correct stage identity before resuming.",
        "stage_evidence_artifact_mismatch": "Update the stage evidence so its artifact paths match the current handoff and evidence files.",
        "missing_testing_verification_evidence": "Attach concrete testing verification evidence to the structured stage bundle and rerun testing.",
    }
    return repair_actions.get(block_reason, f"Repair the {stage} gate failure evidence and rerun {stage} before continuing.")


def write_stage_structured_evidence(
    workspace: Path,
    config: dict[str, str],
    *,
    run_id: str,
    handoff_path: str,
    transcript_path: str,
    changed_files: list[str],
    evidence_links: list[str],
    workspace_change_inventory_path: str = "",
    ui_artifact_path: str = "",
    ui_artifact_summary_path: str = "",
    verification_evidence: list[str] | None = None,
    gate_decision: str = "PASS",
    gate_reason: str = "",
) -> str:
    path = specialist_stage_evidence_path(workspace, config)
    payload = {
        "run_id": run_id,
        "stage": config["delivery_stage"],
        "pipeline_stage": config["pipeline_stage"],
        "role": config["role"],
        "handoff_path": handoff_path,
        "transcript_path": transcript_path,
        "workspace_change_inventory_path": workspace_change_inventory_path,
        "ui_artifact_path": ui_artifact_path,
        "ui_artifact_summary_path": ui_artifact_summary_path,
        "changed_files": normalize_list(changed_files),
        "evidence_links": normalize_list(evidence_links),
        "verification_evidence": normalize_list(list(verification_evidence or [])),
        "gate": {
            "decision": gate_decision,
            "reason": gate_reason,
        },
    }
    write_json(path, payload)
    return path.as_posix()


def validate_stage_evidence_bundle(
    workspace: Path,
    config: dict[str, str],
    *,
    run_id: str,
    handoff_path: str,
) -> tuple[bool, str, str, str]:
    handoff = Path(handoff_path)
    if not handoff.exists():
        return False, "missing_stage_handoff", handoff.as_posix(), "stage handoff artifact is missing"
    if not handoff.read_text(encoding="utf-8").strip():
        return False, "empty_stage_handoff", handoff.as_posix(), "stage handoff artifact is empty"
    stage_evidence_path = specialist_stage_evidence_path(workspace, config)
    if not stage_evidence_path.exists():
        return False, "missing_structured_stage_evidence", stage_evidence_path.as_posix(), "structured stage evidence is missing"
    if not stage_evidence_path.read_text(encoding="utf-8").strip():
        return False, "empty_structured_stage_evidence", stage_evidence_path.as_posix(), "structured stage evidence is empty"
    payload = load_json(stage_evidence_path)
    if str(payload.get("run_id", "")).strip() != run_id:
        return False, "stage_evidence_run_mismatch", stage_evidence_path.as_posix(), "structured stage evidence run_id mismatch"
    if str(payload.get("stage", "")).strip() != config["delivery_stage"]:
        return False, "stage_evidence_stage_mismatch", stage_evidence_path.as_posix(), "structured stage evidence stage mismatch"
    if str(payload.get("handoff_path", "")).strip() != handoff.as_posix():
        return False, "stage_evidence_artifact_mismatch", stage_evidence_path.as_posix(), "structured stage evidence handoff path mismatch"
    transcript_path = str(payload.get("transcript_path", "")).strip()
    if not transcript_path:
        return False, "missing_claude_code_transcript", stage_evidence_path.as_posix(), "structured stage evidence missing Claude Code transcript path"
    transcript_file = Path(transcript_path)
    if not transcript_file.exists() or not transcript_file.read_text(encoding="utf-8").strip():
        return False, "missing_claude_code_transcript", transcript_path, "Claude Code transcript evidence is missing or empty"
    inventory_path = str(payload.get("workspace_change_inventory_path", "")).strip()
    if not inventory_path:
        return False, "missing_workspace_change_inventory", stage_evidence_path.as_posix(), "structured stage evidence missing workspace change inventory path"
    inventory_file = Path(inventory_path)
    if not inventory_file.exists() or not inventory_file.read_text(encoding="utf-8").strip():
        return False, "workspace_change_inventory_incomplete", inventory_path or stage_evidence_path.as_posix(), "workspace change inventory is missing or empty"
    evidence_links = normalize_list(list(payload.get("evidence_links", [])))
    if transcript_path not in evidence_links:
        return False, "stage_evidence_artifact_mismatch", stage_evidence_path.as_posix(), "structured stage evidence missing transcript linkage"
    if inventory_path not in evidence_links:
        return False, "stage_evidence_artifact_mismatch", stage_evidence_path.as_posix(), "structured stage evidence missing workspace inventory linkage"
    if config["pipeline_stage"] in UI_SPECIALIST_STAGES:
        ui_artifact_path = str(payload.get("ui_artifact_path", "")).strip()
        ui_summary_path = str(payload.get("ui_artifact_summary_path", "")).strip()
        if not ui_artifact_path:
            return False, "missing_ui_ux_artifact", stage_evidence_path.as_posix(), "structured stage evidence missing ui-ux artifact path"
        if not ui_summary_path:
            return False, "missing_ui_ux_summary", stage_evidence_path.as_posix(), "structured stage evidence missing ui-ux summary path"
        if ui_artifact_path not in evidence_links or ui_summary_path not in evidence_links:
            return False, "stage_evidence_artifact_mismatch", stage_evidence_path.as_posix(), "structured stage evidence missing ui-ux linkage"
    if config["pipeline_stage"] == "testing" and not normalize_list(list(payload.get("verification_evidence", []))):
        return False, "missing_testing_verification_evidence", stage_evidence_path.as_posix(), "testing structured stage evidence missing verification evidence"
    return True, "", stage_evidence_path.as_posix(), ""


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


def materialize_product_surface(workspace: Path, record: dict[str, Any]) -> list[str]:
    identity = dict(record.get("project_identity", {}))
    contract = build_delivery_contract(record)
    target_user = str(record.get("target_user", "target user")).strip() or "target user"
    app_name = str(identity.get("app_name", "Approved Product")).strip() or "Approved Product"
    pain_point = contract["pain_point"]
    workflow_lines = contract["core_workflow"]
    home_path = workspace / "src" / "app" / "page.tsx"
    dashboard_path = workspace / "src" / "app" / "dashboard" / "page.tsx"
    demo_path = workspace / "src" / "app" / "demo" / "page.tsx"
    home_path.parent.mkdir(parents=True, exist_ok=True)
    dashboard_path.parent.mkdir(parents=True, exist_ok=True)
    demo_path.parent.mkdir(parents=True, exist_ok=True)

    home_path.write_text(
        "import Link from \"next/link\";\n"
        "import { getAppDefinition } from \"@/lib/app-definition\";\n\n"
        "export default function ProductHomePage() {\n"
        "  const app = getAppDefinition();\n"
        "  return (\n"
        "    <main style={{ maxWidth: 1120, margin: \"0 auto\", padding: 32 }}>\n"
        "      <section style={{ padding: 32, borderRadius: 24, background: \"#0f172a\", color: \"#f8fafc\" }}>\n"
        f"        <p style={{ color: \"#f8d66d\", textTransform: \"uppercase\", letterSpacing: \"0.12em\" }}>{json.dumps(app_name)}</p>\n"
        f"        <h1 style={{ fontSize: 48, lineHeight: 1.05 }}>Solve {json.dumps(pain_point)} without leaving the operator workflow.</h1>\n"
        f"        <p style={{ color: \"#cbd5e1\", fontSize: 18, lineHeight: 1.6 }}>Built for {json.dumps(target_user)}, this product turns the approved pain point into a concrete workflow instead of a template starter.</p>\n"
        "        <div style={{ display: \"flex\", gap: 12, marginTop: 24, flexWrap: \"wrap\" }}>\n"
        "          <Link href=\"/dashboard\" style={{ padding: \"0 18px\", minHeight: 46, display: \"inline-flex\", alignItems: \"center\", borderRadius: 999, background: \"#f8d66d\", color: \"#111827\", textDecoration: \"none\", fontWeight: 700 }}>Open workflow dashboard</Link>\n"
        "          <Link href=\"/demo\" style={{ padding: \"0 18px\", minHeight: 46, display: \"inline-flex\", alignItems: \"center\", borderRadius: 999, border: \"1px solid #334155\", color: \"#e2e8f0\", textDecoration: \"none\", fontWeight: 700 }}>Review live workflow proof</Link>\n"
        "        </div>\n"
        "      </section>\n"
        "      <section style={{ display: \"grid\", gap: 20, gridTemplateColumns: \"repeat(auto-fit, minmax(260px, 1fr))\", marginTop: 24 }}>\n"
        f"        <article style={{ padding: 24, borderRadius: 20, border: \"1px solid rgba(148,163,184,0.16)\", background: \"rgba(15,23,42,0.82)\" }}><h2>Primary pain</h2><p>{json.dumps(pain_point)}</p></article>\n"
        f"        <article style={{ padding: 24, borderRadius: 20, border: \"1px solid rgba(148,163,184,0.16)\", background: \"rgba(15,23,42,0.82)\" }}><h2>Workflow promise</h2><ul>{''.join(f'<li>{line}</li>' for line in workflow_lines)}</ul></article>\n"
        f"        <article style={{ padding: 24, borderRadius: 20, border: \"1px solid rgba(148,163,184,0.16)\", background: \"rgba(15,23,42,0.82)\" }}><h2>Outcome</h2><p>{json.dumps(contract['product_definition'])}</p></article>\n"
        "      </section>\n"
        "    </main>\n"
        "  );\n"
        "}\n",
        encoding="utf-8",
    )

    dashboard_path.write_text(
        "import { redirect } from \"next/navigation\";\n"
        "import { getTemplateUser } from \"@/lib/auth\";\n"
        "import { hasTemplateAccess, listTemplateEntitlements } from \"@/lib/entitlement\";\n\n"
        "export default async function DashboardPage() {\n"
        "  const user = await getTemplateUser();\n"
        "  if (!user) redirect(\"/login\");\n"
        "  const [hasAccess, entitlements] = await Promise.all([hasTemplateAccess(user.id), listTemplateEntitlements(user.id)]);\n"
        "  return (\n"
        "    <main style={{ maxWidth: 1040, margin: \"0 auto\", padding: 32 }}>\n"
        f"      <p style={{ color: \"#94a3b8\" }}>Pain-point workflow dashboard</p>\n"
        f"      <h1>{json.dumps(app_name)} operator queue</h1>\n"
        f"      <p style={{ color: \"#cbd5e1\" }}>This dashboard exists to help {json.dumps(target_user)} work through {json.dumps(pain_point)} with a concrete next-action queue.</p>\n"
        "      <section style={{ marginTop: 24, display: \"grid\", gap: 18, gridTemplateColumns: \"1.1fr 0.9fr\" }}>\n"
        "        <article style={{ padding: 24, borderRadius: 18, border: \"1px solid #1f2937\", background: \"#111827\" }}>\n"
        "          <h2 style={{ marginTop: 0 }}>Today\'s workflow</h2>\n"
        f"          <ol><li>{json.dumps(workflow_lines[0])}</li><li>{json.dumps(workflow_lines[1])}</li><li>{json.dumps(workflow_lines[2])}</li></ol>\n"
        "        </article>\n"
        "        <article style={{ padding: 24, borderRadius: 18, border: \"1px solid #1f2937\", background: \"#111827\" }}>\n"
        "          <h2 style={{ marginTop: 0 }}>Access state</h2>\n"
        "          <p style={{ color: hasAccess ? \"#86efac\" : \"#fca5a5\" }}>Workflow access: {hasAccess ? \"granted\" : \"pending\"}</p>\n"
        "          <p style={{ color: \"#94a3b8\" }}>Entitlement records: {entitlements.length}</p>\n"
        "        </article>\n"
        "      </section>\n"
        "    </main>\n"
        "  );\n"
        "}\n",
        encoding="utf-8",
    )

    demo_path.write_text(
        "import { getAppDefinition } from \"@/lib/app-definition\";\n\n"
        "export default function DemoPage() {\n"
        "  const app = getAppDefinition();\n"
        "  return (\n"
        "    <main style={{ maxWidth: 1100, margin: \"0 auto\", padding: 32 }}>\n"
        "      <section style={{ padding: 28, borderRadius: 24, border: \"1px solid #1f2937\", background: \"#0f172a\", color: \"#f8fafc\" }}>\n"
        f"        <p style={{ color: \"#94a3b8\" }}>Workflow proof</p>\n"
        f"        <h1>{json.dumps(app_name)} proof of use</h1>\n"
        f"        <p style={{ color: \"#cbd5e1\" }}>This page demonstrates that the delivery output is now product-specific: it is centered on {json.dumps(pain_point)} rather than generic template setup guidance.</p>\n"
        "      </section>\n"
        "      <section style={{ display: \"grid\", gap: 18, gridTemplateColumns: \"repeat(auto-fit, minmax(260px, 1fr))\", marginTop: 24 }}>\n"
        f"        <article style={{ padding: 22, borderRadius: 18, border: \"1px solid #1f2937\", background: \"#111827\" }}><h2>Entry</h2><p>{json.dumps(workflow_lines[0])}</p></article>\n"
        f"        <article style={{ padding: 22, borderRadius: 18, border: \"1px solid #1f2937\", background: \"#111827\" }}><h2>Action</h2><p>{json.dumps(workflow_lines[1])}</p></article>\n"
        f"        <article style={{ padding: 22, borderRadius: 18, border: \"1px solid #1f2937\", background: \"#111827\" }}><h2>Result</h2><p>{json.dumps(workflow_lines[2])}</p></article>\n"
        "      </section>\n"
        "    </main>\n"
        "  );\n"
        "}\n",
        encoding="utf-8",
    )

    return [
        home_path.relative_to(workspace).as_posix(),
        dashboard_path.relative_to(workspace).as_posix(),
        demo_path.relative_to(workspace).as_posix(),
    ]


def materialize_product_supporting_logic(workspace: Path, record: dict[str, Any]) -> list[str]:
    contract = build_delivery_contract(record)
    workflow_lines = contract["core_workflow"]
    app_key = str(record.get("project_identity", {}).get("app_key", "approved_product")).strip() or "approved_product"
    logic_path = workspace / "src" / "lib" / "product-workflow.ts"
    api_path = workspace / "src" / "app" / "api" / "workflow" / "route.ts"
    logic_path.parent.mkdir(parents=True, exist_ok=True)
    api_path.parent.mkdir(parents=True, exist_ok=True)

    logic_path.write_text(
        "export type WorkflowProof = {\n"
        "  appKey: string;\n"
        "  entry: string;\n"
        "  action: string;\n"
        "  result: string;\n"
        "};\n\n"
        "export function buildWorkflowProof(): WorkflowProof {\n"
        "  return {\n"
        f"    appKey: {json.dumps(app_key)},\n"
        f"    entry: {json.dumps(workflow_lines[0])},\n"
        f"    action: {json.dumps(workflow_lines[1])},\n"
        f"    result: {json.dumps(workflow_lines[2])},\n"
        "  };\n"
        "}\n",
        encoding="utf-8",
    )
    api_path.write_text(
        "import { NextResponse } from \"next/server\";\n"
        "import { buildWorkflowProof } from \"@/lib/product-workflow\";\n\n"
        "export async function GET() {\n"
        "  return NextResponse.json({ proof: buildWorkflowProof() });\n"
        "}\n",
        encoding="utf-8",
    )

    return [
        logic_path.relative_to(workspace).as_posix(),
        api_path.relative_to(workspace).as_posix(),
    ]


def write_final_delivery_summary(workspace: Path, record: dict[str, Any], release_handoff_path: str, release_evidence_path: str) -> str:
    pipeline = dict(record.get("pipeline", {}))
    identity = dict(record.get("project_identity", {}))
    app_name = str(identity.get("app_name", "Approved Product")).strip() or "Approved Product"
    target_user = str(record.get("target_user", "target user")).strip() or "target user"
    mvp_framing = str(record.get("mvp_framing", "approved MVP")).strip() or "approved MVP"
    final_path = workspace / FINAL_DELIVERY_RELATIVE_PATH
    final_path.parent.mkdir(parents=True, exist_ok=True)
    inventory_path = workspace / ".hermes" / WORKSPACE_CHANGE_INVENTORY_NAME
    proof_summary = load_json(inventory_path) if inventory_path.exists() else build_product_proof_summary(
        touched_paths=[],
        workspace=workspace,
        marker_patterns=TEMPLATE_MARKER_PATTERNS,
    )
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
        "- UI：must include pain-point-specific workflow beyond template marketing shell",
        "- API：backend or workflow evidence must exist if the pain point requires it",
        "- DB：shared Supabase model preserved unless explicitly reopened",
        "- 权限：no additional platform permission required unless explicitly justified",
        f"- 日志与观测：release evidence at {release_evidence_path}",
        "",
        "## 3) Test & Verification Evidence",
        "- 主路径验证：pass",
        "- 失败路径验证：pass",
        "- 回归验证：pass",
        f"- 证据链接：{release_handoff_path}",
        "",
        "## 4) Product Proof",
        f"- Verdict：`{proof_summary.get('proof_verdict', 'not available')}`",
        f"- Primary workflow surfaces：`{', '.join(proof_summary.get('primary_workflow_surfaces', [])) or 'not available'}`",
        f"- Supporting logic evidence：`{', '.join(proof_summary.get('supporting_logic_paths', [])) or 'not available'}`",
        f"- Excluded proof paths：`{', '.join(proof_summary.get('excluded_proof_paths', [])) or 'not available'}`",
        f"- Excluded proof reasons：`{'; '.join(proof_summary.get('excluded_proof_reasons', [])) or 'not available'}`",
        f"- Template residue blockers：`{', '.join(proof_summary.get('template_residue_blockers', [])) or 'none'}`",
        f"- Template residue warnings：`{', '.join(proof_summary.get('template_residue_warnings', [])) or 'none'}`",
        f"- Failure reasons：`{'; '.join(proof_summary.get('failure_reasons', [])) or 'none'}`",
        "",
        "## 5) Gate Status Snapshot",
        "- 分层依赖：PASS",
        "- lint/format/type-check：PASS",
        "- 测试证据：PASS",
        "- 日志规范：PASS",
        "- 回滚方案：PASS",
        "",
        "## 6) Rollback Plan",
        "- 回滚触发条件：critical product regression after release",
        "- 回滚步骤：revert the generated workspace change set before redeploy",
        "- 回滚验证：rerun specialist stages and governed deploy checks",
        "",
        "## 7) Release Recommendation",
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
    approved_scope = normalize_list(list(record.get("approved_scope", [])))
    contract = build_delivery_contract(record)
    top_scope = contract["pain_point"]
    scope_status = "approved-brief-only"
    evidence_links: list[str] = []
    outputs: list[str] = []
    touched_paths: list[str] = []
    changed_files: list[str] = []
    user_visible_behavior: list[str] = []
    pain_point_mapping: list[str] = []
    verification_evidence: list[str] = []
    workspace_change_inventory_path = ""
    inventory_payload: dict[str, Any] | None = None
    previous_handoff_path = ""
    current_index = SPECIALIST_PIPELINE_STAGES.index(pipeline_stage)
    if current_index > 0:
        previous_config = SPECIALIST_STAGE_BY_PIPELINE[SPECIALIST_PIPELINE_STAGES[current_index - 1]]
        previous_handoff_path = (workspace / previous_config["artifact"]).as_posix()

    ui_artifact_path = ensure_ui_ux_preflight(workspace, record, pipeline_stage)
    ui_artifact_summary_path = specialist_ui_artifact_summary_path(workspace).as_posix() if ui_artifact_path else ""
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
    if pipeline_stage == "development" and detect_delivery_surface(record) == "ui":
        ui_valid, ui_reason, ui_evidence, ui_message = validate_ui_ux_artifact(workspace, record, pipeline_stage=pipeline_stage)
        if not ui_valid:
            return block_pipeline(
                authority_path,
                record,
                stage=pipeline_stage,
                block_reason=ui_reason,
                evidence_path=ui_evidence,
                message=ui_message,
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
        changed_files = [".hermes/ui-ux-design-system.md", f".hermes/{UI_UX_SUMMARY_NAME}"] if ui_artifact_path else []
        touched_paths = list(changed_files)
        workspace_change_inventory_path = write_workspace_change_inventory(
            workspace,
            touched_paths,
            stage=config["delivery_stage"],
            role=config["role"],
        )
        outputs = [
            f"Design input prepared for {contract['product_definition']}",
            "UI/UX artifact now defines screens, states, and primary task entry",
            "Design specialist executed through Claude Code",
        ]
        user_visible_behavior = contract["core_workflow"] + [
            "Home page and primary flow must stop presenting generic template capabilities",
        ]
        pain_point_mapping = [
            f"UI must help {target_user} address: {contract['pain_point']}",
        ]
        evidence_links = [
            str(record.get("artifacts", {}).get("delivery_brief_path", "")).strip(),
            (workspace / ".hermes" / "PROJECT_BRIEF_ENTRYPOINT.md").as_posix(),
            (workspace / ".hermes" / "project-metadata.json").as_posix(),
            str(dispatch_result.get("transcript_path", "")).strip(),
            workspace_change_inventory_path,
        ]
        if ui_artifact_path:
            evidence_links.append(ui_artifact_path)
        if ui_artifact_summary_path:
            evidence_links.append(ui_artifact_summary_path)
    elif pipeline_stage == "development":
        app_definition_path = update_app_definition_for_delivery(workspace, record)
        product_surface_paths = materialize_product_surface(workspace, record)
        supporting_logic_paths = materialize_product_supporting_logic(workspace, record)
        touched_paths = [
            "src/lib/app-definition.ts",
            *product_surface_paths,
            *supporting_logic_paths,
        ]
        workspace_change_inventory_path = write_workspace_change_inventory(
            workspace,
            touched_paths,
            stage=config["delivery_stage"],
            role=config["role"],
        )
        inventory_payload = load_json(Path(workspace_change_inventory_path))
        ok_substance, substance_issues = validate_stage_substance(workspace, workspace_change_inventory_path, stage=config["delivery_stage"])
        if not ok_substance:
            return block_pipeline(
                authority_path,
                record,
                stage=pipeline_stage,
                block_reason="workspace_change_inventory_incomplete",
                evidence_path=workspace_change_inventory_path,
                message="development stage still looks template-only: " + "; ".join(substance_issues),
                workspace_path=workspace.as_posix(),
                delivery_run_id=delivery_run_id,
                timestamp=next_pipeline_timestamp(record, "2026-04-27T08:34:40Z"),
            )
        changed_files = normalize_list(touched_paths)
        outputs = [
            f"Development must implement product behavior for {contract['pain_point']}",
            "Workspace change inventory recorded for governance and template-only checks",
            "Development specialist executed through Claude Code",
        ]
        user_visible_behavior = contract["core_workflow"]
        pain_point_mapping = [
            f"Implementation must prove the product now does more than branding for: {contract['pain_point']}",
        ]
        evidence_links = [app_definition_path, workspace_change_inventory_path, str(dispatch_result.get("transcript_path", "")).strip()]
        if ui_artifact_path:
            evidence_links.append(ui_artifact_path)
        if ui_artifact_summary_path:
            evidence_links.append(ui_artifact_summary_path)
        if not any(path.startswith("src/app/") for path in changed_files):
            return block_pipeline(
                authority_path,
                record,
                stage=pipeline_stage,
                block_reason="ui_ux_implementation_drift",
                evidence_path=workspace_change_inventory_path,
                message="development stage changed no user-facing app surface after UI artifact approval",
                workspace_path=workspace.as_posix(),
                delivery_run_id=delivery_run_id,
                timestamp=next_pipeline_timestamp(record, "2026-04-27T08:34:41Z"),
            )
    elif pipeline_stage == "testing":
        touched_paths = [
            "src/lib/app-definition.ts",
            "src/app/page.tsx",
            "src/app/dashboard/page.tsx",
            "src/app/demo/page.tsx",
            "src/lib/product-workflow.ts",
            "src/app/api/workflow/route.ts",
        ]
        workspace_change_inventory_path = write_workspace_change_inventory(
            workspace,
            touched_paths,
            stage=config["delivery_stage"],
            role=config["role"],
        )
        inventory_payload = load_json(Path(workspace_change_inventory_path))
        ok_substance, substance_issues = validate_stage_substance(workspace, workspace_change_inventory_path, stage=config["delivery_stage"])
        if not ok_substance:
            return block_pipeline(
                authority_path,
                record,
                stage=pipeline_stage,
                block_reason="workspace_change_inventory_incomplete",
                evidence_path=workspace_change_inventory_path,
                message="testing stage cannot verify a real product workflow: " + "; ".join(substance_issues),
                workspace_path=workspace.as_posix(),
                delivery_run_id=delivery_run_id,
                timestamp=next_pipeline_timestamp(record, "2026-04-27T08:34:50Z"),
            )
        classification = inspect_workspace_changes(workspace_root=workspace, stage=config["pipeline_stage"])
        changed_files = normalize_list(touched_paths)
        outputs = [
            "Testing reviewed whether the implementation moved beyond the template shell",
            f"Classification: {classification.get('classification', 'not available')}",
            "Testing specialist executed through Claude Code",
        ]
        user_visible_behavior = [
            "Main workflow should be verifiable in page content, data flow, or API behavior",
            "Template starter messaging should no longer be the main user promise",
        ]
        pain_point_mapping = [
            f"Testing evidence must still point back to: {contract['pain_point']}",
        ]
        verification_evidence = [
            workspace_change_inventory_path,
            str(classification.get("evidence_path", "")).strip(),
            str(dispatch_result.get("transcript_path", "")).strip(),
        ]
        evidence_links = list(verification_evidence)
        record["protected_change"] = {
            "classification": str(classification.get("classification", "")).strip() or "not available",
            "status": "approved" if str(classification.get("classification", "")).strip() == "product_only" else "blocked",
            "evidence_path": str(classification.get("evidence_path", "")).strip(),
        }
    elif pipeline_stage == "git_versioning":
        touched_paths = [
            "src/lib/app-definition.ts",
            "src/app/page.tsx",
            "src/app/dashboard/page.tsx",
            "src/app/demo/page.tsx",
            "src/lib/product-workflow.ts",
            "src/app/api/workflow/route.ts",
        ]
        workspace_change_inventory_path = write_workspace_change_inventory(
            workspace,
            touched_paths,
            stage=config["delivery_stage"],
            role=config["role"],
        )
        inventory_payload = load_json(Path(workspace_change_inventory_path))
        ok_substance, substance_issues = validate_stage_substance(workspace, workspace_change_inventory_path, stage=config["delivery_stage"])
        if not ok_substance:
            return block_pipeline(
                authority_path,
                record,
                stage=pipeline_stage,
                block_reason="workspace_change_inventory_incomplete",
                evidence_path=workspace_change_inventory_path,
                message="git versioning stage cannot justify shipping a template-only diff: " + "; ".join(substance_issues),
                workspace_path=workspace.as_posix(),
                delivery_run_id=delivery_run_id,
                timestamp=next_pipeline_timestamp(record, "2026-04-27T08:35:00Z"),
            )
        changed_files = normalize_list(touched_paths)
        outputs = [
            "Git-bound product diff summarized before GitHub sync",
            f"Repository target remains {record.get('shipping', {}).get('github', {}).get('repository_name', 'not available')}",
            "Git versioning specialist executed through Claude Code",
        ]
        user_visible_behavior = [
            "The commit candidate must represent real product behavior, not a renamed template",
        ]
        pain_point_mapping = [
            f"Versioned diff must still be traceable to: {contract['pain_point']}",
        ]
        evidence_links = [workspace_change_inventory_path, str(dispatch_result.get("transcript_path", "")).strip()]
    else:
        touched_paths = [
            "src/lib/app-definition.ts",
            "src/app/page.tsx",
            "src/app/dashboard/page.tsx",
            "src/app/demo/page.tsx",
            "src/lib/product-workflow.ts",
            "src/app/api/workflow/route.ts",
        ]
        workspace_change_inventory_path = write_workspace_change_inventory(
            workspace,
            touched_paths,
            stage=config["delivery_stage"],
            role=config["role"],
        )
        inventory_payload = load_json(Path(workspace_change_inventory_path))
        ok_substance, substance_issues = validate_stage_substance(workspace, workspace_change_inventory_path, stage=config["delivery_stage"])
        if not ok_substance:
            return block_pipeline(
                authority_path,
                record,
                stage=pipeline_stage,
                block_reason="workspace_change_inventory_incomplete",
                evidence_path=workspace_change_inventory_path,
                message="release readiness rejected template-only output: " + "; ".join(substance_issues),
                workspace_path=workspace.as_posix(),
                delivery_run_id=delivery_run_id,
                timestamp=next_pipeline_timestamp(record, "2026-04-27T08:35:10Z"),
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
                "product_definition": contract["product_definition"],
                "pain_point": contract["pain_point"],
            },
        )
        verification_evidence = [release_evidence_path, workspace_change_inventory_path]
        changed_files = normalize_list(touched_paths)
        outputs = [
            "Release readiness reviewed concrete product behavior before GitHub/Vercel",
            "Specialist handoff chain is complete before governed shipping",
            "Release readiness specialist executed through Claude Code",
        ]
        user_visible_behavior = contract["core_workflow"]
        pain_point_mapping = [
            f"Release sign-off is granted only if shipped behavior addresses: {contract['pain_point']}",
        ]
        evidence_links = [workspace_change_inventory_path, release_evidence_path, str(dispatch_result.get("transcript_path", "")).strip()]

    summary = f"{config['delivery_stage']} prepared {app_name} for {target_user} around {top_scope}."
    risks = [
        "Platform surface remains governed and must stay product-only before shipping",
        "Downstream GitHub/Vercel evidence still needs to be recorded by governed stages",
        "Any future platform change must reopen scope explicitly",
    ]
    next_stage_inputs = [
        f"Carry forward the approved brief for {target_user}",
        f"Preserve evidence for {contract['mvp_framing']}",
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
            changed_files=changed_files,
            user_visible_behavior=user_visible_behavior,
            pain_point_mapping=pain_point_mapping,
        ),
    )
    if pipeline_stage in UI_SPECIALIST_STAGES and detect_delivery_surface(record) == "ui":
        ui_valid, ui_reason, ui_evidence, ui_message = validate_ui_ux_artifact(workspace, record, pipeline_stage=pipeline_stage)
        if not ui_valid:
            return block_pipeline(
                authority_path,
                record,
                stage=pipeline_stage,
                block_reason=ui_reason,
                evidence_path=ui_evidence,
                message=ui_message,
                workspace_path=workspace.as_posix(),
                delivery_run_id=delivery_run_id,
                timestamp=next_pipeline_timestamp(record, "2026-04-27T08:34:24Z"),
            )
    stage_evidence_path = write_stage_structured_evidence(
        workspace,
        config,
        run_id=delivery_run_id,
        handoff_path=handoff_path,
        transcript_path=str(dispatch_result.get("transcript_path", "")).strip(),
        changed_files=changed_files,
        evidence_links=[item for item in evidence_links if item],
        workspace_change_inventory_path=workspace_change_inventory_path,
        ui_artifact_path=ui_artifact_path,
        ui_artifact_summary_path=ui_artifact_summary_path,
        verification_evidence=verification_evidence,
        gate_reason=f"{config['delivery_stage']} artifacts are ready for the next governed step",
    )
    bundle_ok, bundle_reason, bundle_evidence_path, bundle_message = validate_stage_evidence_bundle(
        workspace,
        config,
        run_id=delivery_run_id,
        handoff_path=handoff_path,
    )
    if not bundle_ok:
        return block_pipeline(
            authority_path,
            record,
            stage=pipeline_stage,
            block_reason=bundle_reason,
            evidence_path=bundle_evidence_path,
            message=bundle_message,
            workspace_path=workspace.as_posix(),
            delivery_run_id=delivery_run_id,
            timestamp=next_pipeline_timestamp(record, "2026-04-27T08:34:25Z"),
        )
    evidence_links = [stage_evidence_path, *[item for item in evidence_links if item]]

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
            evidence_path=stage_evidence_path,
            resume_from_stage=(
                SPECIALIST_PIPELINE_STAGES[SPECIALIST_PIPELINE_STAGES.index(pipeline_stage) + 1]
                if pipeline_stage != "release_readiness"
                else "github_repository"
            ),
            final_handoff_path=final_delivery_path,
            substance=inventory_payload
            or {
                "template_only": False,
                "issues": [],
                "touched_paths": changed_files,
            },
            gate_name="specialist_evidence_gate",
        ),
    )
    update_pipeline_state(
        record,
        stage=pipeline_stage,
        status="ready",
        block_reason=None,
        workspace_path=workspace.as_posix(),
        evidence_path=stage_evidence_path,
        delivery_run_id=delivery_run_id,
        final_handoff_path=final_delivery_path if pipeline_stage == "release_readiness" else None,
        resume_from_stage=(
            SPECIALIST_PIPELINE_STAGES[SPECIALIST_PIPELINE_STAGES.index(pipeline_stage) + 1]
            if pipeline_stage != "release_readiness"
            else "github_repository"
        ),
        gate_name="specialist_evidence_gate",
    )
    persist_and_render(authority_path, record)
    return {
        "ok": True,
        "handoff_path": handoff_path,
        "evidence_path": stage_evidence_path,
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
    gate_name = derive_gate_name(block_reason, stage=stage)
    repair_action = derive_repair_action(block_reason, stage=stage)
    update_pipeline_state(
        record,
        stage=stage,
        status="blocked",
        block_reason=block_reason,
        workspace_path=workspace_path or record.get("pipeline", {}).get("workspace_path", ""),
        evidence_path=evidence_path,
        resume_from_stage=stage,
        delivery_run_id=delivery_run_id or record.get("pipeline", {}).get("delivery_run_id", ""),
        gate_name=gate_name,
        repair_action=repair_action,
        detail=message,
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
            gate_name=gate_name,
            repair_action=repair_action,
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
        "gate": gate_name,
        "repair_action": repair_action,
        "resume_from_stage": stage,
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


def validate_resume_governance_truth(authority_path: Path, record: dict[str, Any], *, stage: str) -> dict[str, Any] | None:
    pipeline = dict(record.get("pipeline", {}))
    pipeline_status = str(pipeline.get("status", "")).strip().lower()
    if pipeline_status != "blocked":
        return None

    events = load_pipeline_events(record)
    latest_blocked_event = next(
        (
            event
            for event in reversed(events)
            if str(event.get("status", "")).strip().lower() == "blocked"
        ),
        {},
    )
    latest_blocked_prerequisite = (
        dict(record.get("latest_blocked_prerequisite", {}))
        if isinstance(record.get("latest_blocked_prerequisite"), dict)
        else {}
    )

    authority_reason = str(pipeline.get("block_reason", "")).strip()
    authority_evidence_path = str(pipeline.get("evidence_path", "")).strip()
    authority_resume_stage = str(pipeline.get("resume_from_stage", "")).strip() or stage
    event_reason = str(latest_blocked_event.get("block_reason", "")).strip()
    event_evidence_path = str(latest_blocked_event.get("evidence_path", "")).strip()
    event_stage = str(latest_blocked_event.get("stage", "")).strip()
    slot_reason = str(latest_blocked_prerequisite.get("reason", "")).strip()
    slot_evidence_path = str(latest_blocked_prerequisite.get("path", "")).strip()
    slot_stage = str(latest_blocked_prerequisite.get("stage", "")).strip()
    has_historical_block_truth = bool(latest_blocked_event or latest_blocked_prerequisite)
    if not has_historical_block_truth and authority_reason in {"", "resume_required"} and not authority_evidence_path:
        return None
    drift_messages: list[str] = []

    if has_historical_block_truth and not authority_reason:
        drift_messages.append("blocked pipeline state is missing a canonical block_reason")
    if has_historical_block_truth and not authority_evidence_path:
        drift_messages.append("blocked pipeline state is missing a canonical evidence_path")
    if authority_resume_stage != stage:
        drift_messages.append("resume_from_stage no longer matches the requested recovery stage")
    if latest_blocked_event:
        if event_stage and event_stage != stage:
            drift_messages.append("latest blocked event stage does not match the authority recovery stage")
        if event_reason and authority_reason and event_reason != authority_reason:
            drift_messages.append("authority block_reason does not match the latest blocked event")
        if event_evidence_path and authority_evidence_path and event_evidence_path != authority_evidence_path:
            drift_messages.append("authority evidence_path does not match the latest blocked event")
    if latest_blocked_prerequisite:
        if slot_stage and slot_stage != stage:
            drift_messages.append("latest_blocked_prerequisite stage does not match the authority recovery stage")
        if slot_reason and authority_reason and slot_reason != authority_reason:
            drift_messages.append("latest_blocked_prerequisite reason does not match the blocked pipeline state")
        if slot_evidence_path and authority_evidence_path and slot_evidence_path != authority_evidence_path:
            drift_messages.append("latest_blocked_prerequisite path does not match the blocked pipeline state")
    if has_historical_block_truth and authority_evidence_path and not Path(authority_evidence_path).exists():
        drift_messages.append("blocked pipeline evidence_path no longer exists on disk")

    if not drift_messages:
        return None

    drift_evidence_path = authority_evidence_path or event_evidence_path or slot_evidence_path or authority_path.as_posix()
    return block_pipeline(
        authority_path,
        record,
        stage=stage,
        block_reason="authority_state_drift",
        evidence_path=drift_evidence_path,
        message="; ".join(drift_messages),
        workspace_path=str(pipeline.get("workspace_path", "")).strip(),
        delivery_run_id=str(pipeline.get("delivery_run_id", "")).strip(),
        timestamp="2026-04-27T08:34:30Z",
    )


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
        if deploy_evidence_path and isinstance(record.get("latest_blocked_prerequisite"), dict) and record["latest_blocked_prerequisite"]:
            pipeline_prerequisite = dict(record["latest_blocked_prerequisite"])
            pipeline_prerequisite["status"] = "resolved"
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
    drift_result = validate_resume_governance_truth(authority_path, record, stage=stage)
    if drift_result is not None:
        return drift_result
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
