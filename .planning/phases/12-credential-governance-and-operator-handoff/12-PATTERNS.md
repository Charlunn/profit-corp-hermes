# Phase 12: Credential Governance and Operator Handoff - Pattern Map

**Mapped:** 2026-04-27
**Files analyzed:** 11
**Analogs found:** 11 / 11

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `scripts/start_approved_project_delivery.py` | service | request-response | `scripts/start_approved_project_delivery.py` | exact |
| `scripts/render_approved_delivery_status.py` | utility | transform | `scripts/render_approved_delivery_status.py` | exact |
| `scripts/validate_approved_delivery_pipeline.py` | utility | transform | `scripts/validate_approved_delivery_pipeline.py` | exact |
| `scripts/github_delivery_common.py` | service | request-response | `scripts/github_delivery_common.py` | exact |
| `scripts/vercel_delivery_common.py` | service | request-response | `scripts/vercel_delivery_common.py` | exact |
| `scripts/approved_delivery_governance.py` | service | transform | `scripts/governance_common.py` | role-match |
| `scripts/request_platform_justification.py` | service | request-response | `scripts/request_governance_approval.py` | role-match |
| `orchestration/cron/commands.sh` | utility | request-response | `orchestration/cron/commands.sh` | exact |
| `tests/test_phase11_github_sync.py` | test | request-response | `tests/test_phase11_github_sync.py` | exact |
| `tests/test_phase11_vercel_flow.py` | test | request-response | `tests/test_phase11_vercel_flow.py` | exact |
| `tests/test_phase12_credential_governance.py` | test | transform | `tests/test_project_delivery_pipeline_resume.py` | role-match |

## Pattern Assignments

### `scripts/start_approved_project_delivery.py` (service, request-response)

**Analog:** `scripts/start_approved_project_delivery.py`

**Imports and helper alias pattern** (`scripts/start_approved_project_delivery.py:15-22`):
```python
from scripts.github_delivery_common import prepare_github_repository as github_prepare_repository
from scripts.github_delivery_common import sync_workspace_to_github
from scripts.instantiate_template_project import build_metadata, instantiate_workspace
from scripts.start_delivery_run import initialize_delivery_run
from scripts.template_contract_common import build_identity_payload
from scripts.vercel_delivery_common import apply_env_contract as vercel_apply_env_contract
from scripts.vercel_delivery_common import deploy_to_vercel
from scripts.vercel_delivery_common import link_vercel_project as vercel_link_project
```
Copy this style for Phase 12 orchestration: keep governance logic in helper modules, import them into the authority-layer pipeline, and alias helper names when local wrapper names would collide.

**Append-only event payload pattern** (`scripts/start_approved_project_delivery.py:427-464`):
```python
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
    ...
    return {
        "project_slug": str(identity.get("project_slug", "")).strip(),
        "stage": stage,
        "status": status,
        "action": action,
        "timestamp": timestamp,
        "outcome": outcome,
        ...
        "block_reason": block_reason,
        "evidence_path": evidence_path,
        "resume_from_stage": resume_from_stage,
        "final_handoff_path": final_handoff_path,
        "shipping": shipping,
    }
```
Use this exact event-shape extension pattern for credential audits: add governance/audit fields without replacing the existing append-only stage event contract.

**Blocked-state persistence pattern** (`scripts/start_approved_project_delivery.py:704-753`):
```python
def block_pipeline(...):
    ...
    update_pipeline_state(
        record,
        stage=stage,
        status="blocked",
        block_reason=block_reason,
        ...
        evidence_path=evidence_path,
        resume_from_stage=stage,
        delivery_run_id=delivery_run_id or record.get("pipeline", {}).get("delivery_run_id", ""),
    )
    append_pipeline_event(
        project_dir,
        make_event(
            ...
            status="blocked",
            action="stage_blocked",
            outcome="blocked",
            artifact=evidence_path,
            ...
            block_reason=block_reason,
            evidence_path=evidence_path,
            resume_from_stage=stage,
        ),
    )
```
Phase 12 governance blocks should reuse this exact pattern: write machine-readable evidence, persist `block_reason`, and append a blocked event with resume metadata.

**Stage progression pattern** (`scripts/start_approved_project_delivery.py:1018-1039`, `1061-1080`, `1157-1169`, `1221-1234`):
```python
if not github_result.get("ok"):
    blocked = block_pipeline(
        authority_path,
        record,
        stage="github_repository",
        block_reason=str(github_result.get("block_reason", "github_repository_failed")).strip() or "github_repository_failed",
        evidence_path=str(github_result.get("evidence_path", authority_path.as_posix())).strip() or authority_path.as_posix(),
        message=str(github_result.get("error", "github repository prepare failed")),
        ...
    )
```
Copy this wrapper pattern for each credentialed action: helper returns `{ok, block_reason, evidence_path}`, pipeline wrapper maps that into authority state + event stream.

**Where to insert Phase 12 work**: place protected-change classification before `github_sync` and before `vercel_deploy`, because Context D-07/D-08 and Research §2 call for pre-sync/pre-deploy gating.

---

### `scripts/render_approved_delivery_status.py` (utility, transform)

**Analog:** `scripts/render_approved_delivery_status.py`

**History rendering pattern** (`scripts/render_approved_delivery_status.py:46-59`):
```python
def build_status_markdown(events: list[dict[str, Any]]) -> str:
    latest = events[-1] if events else {}
    history_lines = []
    for event in events:
        history_lines.append(
            "- "
            f"stage=`{event.get('stage', 'not available')}` "
            f"status=`{event.get('status', 'not available')}` "
            f"outcome=`{event.get('outcome', 'not available')}` "
            f"block_reason=`{event.get('block_reason', 'not available')}` "
            f"artifact=`{event.get('artifact', 'not available')}` "
            f"evidence=`{event.get('evidence_path', 'not available')}` "
            f"handoff=`{event.get('final_handoff_path', 'not available')}`"
        )
```
Add credential audit and justification visibility by extending this same latest-event/history-line formatting approach, not by creating a second status document.

**Latest-view operator summary pattern** (`scripts/render_approved_delivery_status.py:63-101`):
```python
return "\n".join(
    [
        "# Delivery Pipeline Status",
        f"- **Authority Source**: `{EVENTS_FILE_NAME}`",
        ...
        f"- **GitHub Sync Evidence**: `{github.get('sync_evidence_path', 'not available')}`",
        ...
        f"- **Deploy Status**: `{vercel.get('deploy_status', vercel.get('deployment_status', 'not available'))}`",
        f"- **Deploy Evidence**: `{vercel.get('deploy_evidence_path', vercel.get('deployment_evidence_path', 'not available'))}`",
        f"- **Block Reason**: `{latest.get('block_reason', 'not available')}`",
        f"- **Evidence Path**: `{latest.get('evidence_path', 'not available')}`",
        ...
        "## Event History",
        *(history_lines or [...]),
    ]
)
```
Phase 12 final operator review should copy this markdown-first field list pattern and add exception-first sections for protected changes, justification status, and credentialed action outcomes.

---

### `scripts/validate_approved_delivery_pipeline.py` (utility, transform)

**Analog:** `scripts/validate_approved_delivery_pipeline.py`

**JSON/JSONL validation pattern** (`scripts/validate_approved_delivery_pipeline.py:57-86`):
```python
def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        payload = json.loads(load_text(path, label))
    except json.JSONDecodeError as exc:
        raise ApprovedDeliveryPipelineValidationError(...)
    if not isinstance(payload, dict):
        raise ApprovedDeliveryPipelineValidationError(...)
    return payload


def load_jsonl(path: Path, label: str) -> list[dict[str, Any]]:
    ...
    if not events:
        raise ApprovedDeliveryPipelineValidationError(f"{label} has no events: {path.as_posix()}")
```
Use this same strict loader style for new credential-audit and platform-justification artifacts.

**Blocked visibility validation pattern** (`scripts/validate_approved_delivery_pipeline.py:182-206`):
```python
def validate_blocked_prerequisite_visibility(record, events, status_text):
    blocked_events = [event for event in events if str(event.get("status", "")).strip() == "blocked"]
    if not blocked_events:
        return
    latest_blocked = blocked_events[-1]
    block_reason = first_nonempty(...)
    evidence_path = first_nonempty(...)
    ...
    if not block_reason:
        raise ApprovedDeliveryPipelineValidationError("blocked pipeline state missing persisted block reason")
    if not evidence_path:
        raise ApprovedDeliveryPipelineValidationError("blocked pipeline state missing persisted evidence path")
```
Phase 12 validator additions should follow this pattern exactly for governance blocks: require persisted reason, evidence path, and rendered visibility in the markdown surface.

**Cross-link validation pattern** (`scripts/validate_approved_delivery_pipeline.py:208-253`):
```python
def validate_github_linkage(record: dict[str, Any], status_text: str) -> None:
    github = get_nested(record, "shipping", "github")
    ...
    for key, label in required_fields.items():
        value = first_nonempty(github.get(key))
        if not value:
            raise ApprovedDeliveryPipelineValidationError(...)
        if value.lower() not in lowered and Path(value).name.lower() not in lowered:
            raise ApprovedDeliveryPipelineValidationError(...)
```
Reuse this for audit linkage checks: authority record must point at audit/justification files and the operator review must mention them.

---

### `scripts/github_delivery_common.py` (service, request-response)

**Analog:** `scripts/github_delivery_common.py`

**Evidence writer + blocked helper pattern** (`scripts/github_delivery_common.py:37-62`):
```python
def _evidence_path(workspace: Path, stem: str) -> Path:
    return workspace / ".hermes" / stem


def _write_evidence(path: Path, payload: dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return path.as_posix()


def _blocked(workspace: Path, evidence_name: str, block_reason: str, message: str, **extra: Any) -> dict[str, Any]:
    ...
    return {
        "ok": False,
        "block_reason": block_reason,
        "error": message,
        "evidence_path": written,
        **extra,
    }
```
New credential-audit helpers should copy this exact file-first contract: every failure/blocked outcome returns machine-readable evidence and `block_reason`.

**Credential gating pattern** (`scripts/github_delivery_common.py:117-133`):
```python
def _require_gh(workspace: Path, *, which: Which | None = None, env: Mapping[str, str] | None = None) -> dict[str, Any] | None:
    locator = which or shutil.which
    if not locator("gh"):
        return _blocked(..., "missing_gh_cli", ...)
    if not _has_github_auth(env):
        return _blocked(..., "missing_github_auth", ...)
    return None
```
Phase 12 should keep credential use constrained by wrapping this helper, not by introducing arbitrary `gh` calls elsewhere.

**Success evidence payload pattern** (`scripts/github_delivery_common.py:231-254`, `371-389`):
```python
evidence_path = _write_evidence(
    _evidence_path(workspace, "github-repository-prepare.json"),
    {
        "ok": True,
        "repository_mode": repository_mode,
        "repository_owner": owner,
        "repository_name": identity,
        "repository_url": canonical_url,
        "default_branch": default_branch,
        "remote_name": remote,
        "command": "gh repo create" if repository_mode == "create" else "gh repo view",
    },
)
```
and
```python
return {
    "ok": True,
    "block_reason": "",
    "evidence_path": evidence_path,
    "repository_url": repo_url,
    "default_branch": branch,
    "remote_name": remote,
    "synced_commit": synced_commit,
}
```
Copy this shape for credential audit records: explicit action metadata, target, evidence path, and normalized success payload.

---

### `scripts/vercel_delivery_common.py` (service, request-response)

**Analog:** `scripts/vercel_delivery_common.py`

**Sensitive-output redaction pattern** (`scripts/vercel_delivery_common.py:33-37`):
```python
def _safe_summary(text: str) -> str:
    cleaned = " ".join(str(text or "").split())
    for key in ("VERCEL_TOKEN",):
        cleaned = cleaned.replace(key, f"{key}=[redacted]")
    return cleaned[:400]
```
Use the same approach in Phase 12 audit artifacts so evidence is operator-usable without leaking tokens.

**CLI/auth gating pattern** (`scripts/vercel_delivery_common.py:143-166`):
```python
def _require_vercel(...):
    command = _resolve_vercel_command(which=which)
    if not command:
        return None, _blocked(..., "missing_vercel_cli", ...)
    source = dict(env or {})
    if not source.get("VERCEL_TOKEN"):
        return None, _blocked(..., "missing_vercel_auth", ...)
    return command, None
```
Phase 12 should preserve this narrow platform-controlled path for Vercel credentials.

**Structured env-contract pattern** (`scripts/vercel_delivery_common.py:170-190`, `302-315`):
```python
def build_env_contract(...):
    ...
    contract = {
        "platform_managed": platform_names,
        "identity_derived": identity_values,
        "evidence_path": (workspace / ".hermes" / "vercel-env-contract.json").as_posix(),
    }
```
and
```python
payload = {
    "ok": True,
    "project_name": validated_project_name,
    "team_scope": validated_team_scope,
    "env_contract": contract,
    "env_contract_path": contract["evidence_path"],
    "required_env": {
        "platform_managed": contract["platform_managed"],
        "identity_derived": contract["identity_derived"],
    },
}
```
Copy this pattern for credential-action audit payloads: separate normalized machine-readable contract from execution result payload.

**Prerequisite gating pattern** (`scripts/vercel_delivery_common.py:339-359`):
```python
if not github_sync_ok:
    return _blocked(..., "github_sync_incomplete", ...)
if not vercel_link_ok:
    return _blocked(..., "missing_vercel_project_linkage", ...)
if not env_contract_ok:
    return _blocked(..., "missing_vercel_env_contract", ...)
```
Protected-change governance should use the same early-return prerequisite style before deploy proceeds.

---

### `scripts/approved_delivery_governance.py` (service, transform)

**Analog:** `scripts/governance_common.py`

**Allowed event/state contract pattern** (`scripts/governance_common.py:18-45`):
```python
REQUIRED_EVENT_FIELDS = (
    "action_id",
    "event_type",
    "actor",
    "target_artifact",
    "related_decision_package",
    "status_before",
    "status_after",
    "approved_by",
    "timestamp",
)
ALLOWED_EVENT_TYPES = {
    "requested",
    "approved",
    "rejected",
    "override",
    "failed",
    "blocked",
}
```
For a new Phase 12 governance helper, define audit/justification artifact schemas as constants first, then validate every append/write against them.

**Write-scope safety pattern** (`scripts/governance_common.py:125-143`):
```python
def ensure_governance_dir() -> None:
    GOVERNANCE_DIR.mkdir(parents=True, exist_ok=True)


def ensure_allowed_write_path(path: Path) -> None:
    resolved = path.resolve()
    for directory in ALLOWED_WRITE_DIRS:
        try:
            resolved.relative_to(directory.resolve())
            return
        except ValueError:
            continue
    raise GovernanceError(f"refusing to write outside allowed directories: {path}")
```
Use this same bounded-write pattern for authority-layer credential/audit artifacts.

**Validation-before-append pattern** (`scripts/governance_common.py:172-205`):
```python
def validate_event(event: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_EVENT_FIELDS if field not in event]
    if missing:
        raise GovernanceError(...)
    ...


def append_event(event: dict[str, Any], path: Path = GOVERNANCE_EVENTS_PATH) -> None:
    validate_event(event)
    ensure_governance_dir()
    ensure_allowed_write_path(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
```
Copy this for append-only credential audit streams or authority audit ledgers.

---

### `scripts/request_platform_justification.py` (service, request-response)

**Analog:** `scripts/request_governance_approval.py`

**CLI subcommand pattern** (`scripts/request_governance_approval.py:26-56`):
```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Request or decide governance approval state transitions.")
    subparsers = parser.add_subparsers(dest="command", required=True)
    ...
    request_parser = subparsers.add_parser("request", help="Create a requested governance action.")
    ...
    approve_parser = subparsers.add_parser("approve", help="Approve an existing pending governance action.")
    ...
```
If Phase 12 adds a dedicated platform-justification script, follow this request/approve/reject command model instead of a one-off ad hoc CLI.

**Request event construction pattern** (`scripts/request_governance_approval.py:67-89`):
```python
def build_request_event(args: argparse.Namespace) -> dict[str, Any]:
    action_type = args.action_type or "unclassified"
    validation = validate_actor_target(args.actor, args.target_artifact or "", action_type)
    ...
    return {
        "action_id": generate_action_id(),
        "event_type": "requested",
        "action_type": action_type,
        "actor": args.actor,
        "target_artifact": args.target_artifact or "",
        ...
        "status_after": "pending",
        ...
        "reason": args.reason,
        ...
    }
```
Map protected-surface detection results into this exact “request artifact + pending state + reason” flow.

**Decision transition guard pattern** (`scripts/request_governance_approval.py:92-127`):
```python
def require_pending(action_id: str) -> dict[str, Any]:
    latest = find_latest_event(action_id, load_jsonl(GOVERNANCE_EVENTS_PATH))
    if latest is None:
        raise GovernanceApprovalError(f"action_id not found: {action_id}")
    if str(latest.get("status_after", "")).lower() != "pending":
        raise GovernanceApprovalError(f"action_id is not pending: {action_id}")
    return latest
```
Use the same state-machine guard for justification approvals so resume only happens from a valid pending approval state.

---

### `orchestration/cron/commands.sh` (utility, request-response)

**Analog:** `orchestration/cron/commands.sh`

**Wrapper help/arity guard pattern** (`orchestration/cron/commands.sh:181-250`):
```bash
resume_approved_delivery() {
  if [ "${1:-}" = "--help" ]; then
    python "$ROOT_DIR/scripts/start_approved_project_delivery.py" --help
    return 0
  fi
  [ "$#" -ge 1 ] || { echo "Usage: bash orchestration/cron/commands.sh resume-approved-delivery <approved-project-path>"; return 1; }
  python "$ROOT_DIR/scripts/start_approved_project_delivery.py" --authority-record-path "$1" --resume
}
```
Any new operator entrypoints for Phase 12 should follow this shell-wrapper convention: delegated Python script, `--help` passthrough, explicit usage string.

**Case dispatch pattern** (`orchestration/cron/commands.sh:262-336`):
```bash
case "$ACTION" in
  ...
  render-approved-delivery-status)
    shift
    render_approved_delivery_status_cmd "$@"
    ;;
  validate-approved-delivery-pipeline)
    shift
    validate_approved_delivery_pipeline_cmd "$@"
    ;;
```
Add Phase 12 wrappers here rather than inventing a separate operator command surface.

---

### `tests/test_phase11_github_sync.py` (test, request-response)

**Analog:** `tests/test_phase11_github_sync.py`

**Import-by-path test loader pattern** (`tests/test_phase11_github_sync.py:18-26`):
```python
def load_module(module_name: str, script_path: Path):
    if not script_path.exists():
        raise AssertionError(f"expected script to exist: {script_path}")
    spec = importlib.util.spec_from_file_location(module_name, script_path)
    ...
```
Use this same script-module loading pattern for new Phase 12 tests against standalone scripts.

**Stubbed command runner pattern** (`tests/test_phase11_github_sync.py:10-16`, `42-68`, `134-156`):
```python
class CompletedProcessStub:
    def __init__(self, returncode: int = 0, stdout: str = "", stderr: str = "") -> None:
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
```
and then branch on `cmd[:N]` inside fake runners. Reuse this for protected-change classification and audit helper tests whenever external commands are involved.

**Blocked-state assertions pattern** (`tests/test_phase11_github_sync.py:106-129`):
```python
self.assertFalse(missing_cli["ok"], msg=missing_cli)
self.assertEqual(missing_cli["block_reason"], "missing_gh_cli")
self.assertTrue(missing_cli["evidence_path"].endswith("github-repository-prepare.json"))
```
Phase 12 tests should assert exact `block_reason` values and artifact paths, not generic failure.

---

### `tests/test_phase11_vercel_flow.py` (test, request-response)

**Analog:** `tests/test_phase11_vercel_flow.py`

**Small unit-test contract pattern** (`tests/test_phase11_vercel_flow.py:32-54`, `80-108`, `109-137`):
```python
missing_cli = module.link_vercel_project(...)
self.assertFalse(missing_cli["ok"], msg=missing_cli)
self.assertEqual(missing_cli["block_reason"], "missing_vercel_cli")
```
and
```python
contract = json.loads(Path(result["env_contract_path"]).read_text(encoding="utf-8"))
self.assertEqual(contract["platform_managed"], [...])
self.assertNotIn("secret", json.dumps(contract, ensure_ascii=False))
```
Use this structure for credential-audit payload tests and justification artifact tests: verify exact JSON shape, and verify secrets are not present.

**Pipeline-state assertion pattern** (`tests/test_phase11_vercel_flow.py:210-247`, `275-330`):
```python
updated = self.read_record()
self.assertEqual(updated["shipping"]["vercel"]["project_id"], "prj_123")
...
self.assertEqual(updated["pipeline"]["resume_from_stage"], "vercel_deploy")
```
Copy this for governance insertion points: assert authority record fields change, resume stage updates, and evidence paths persist.

---

### `tests/test_phase12_credential_governance.py` (test, transform)

**Analog:** `tests/test_project_delivery_pipeline_resume.py`

**Fixture-heavy authority bundle pattern** (`tests/test_project_delivery_pipeline_resume.py:30-123`):
```python
def create_resume_fixture(self, *, stage: str, status: str = "blocked") -> tuple[Path, Path, Path, Path]:
    root = Path(tempfile.mkdtemp(prefix="approved-delivery-resume-"))
    ...
    authority = {
        ...
        "pipeline": {
            "stage": stage,
            "status": status,
            "block_reason": "resume_required" if status == "blocked" else None,
            "resume_from_stage": stage,
            "workspace_path": workspace.as_posix(),
        },
        ...
    }
```
Use the same style for Phase 12 governance fixtures: isolated temp root, realistic authority record, realistic workspace `.hermes` artifacts.

**Patch-heavy orchestration test pattern** (`tests/test_project_delivery_pipeline_resume.py:139-149`, `172-176`):
```python
with mock.patch.object(start_module, "ROOT_DIR", root), \
     mock.patch.object(start_module, "instantiate_workspace") as instantiate_mock, \
     mock.patch.object(start_module, "check_template_conformance", return_value={...}), \
     mock.patch.object(start_module, "initialize_delivery_run", return_value={...}):
    result = start_module.resume_approved_project_delivery(authority_path)
```
Follow this pattern to test protected-change gating and justification-resume behavior without running live GitHub/Vercel operations.

**Event-order assertions pattern** (`tests/test_project_delivery_pipeline_resume.py:158-160`, `184-185`):
```python
events = self.read_events(project_dir)
self.assertEqual([event["stage"] for event in events], ["conformance", "delivery_run_bootstrap"])
```
Phase 12 tests should assert audit/gating events append in the expected order.

## Shared Patterns

### Authentication / Credential boundary
**Source:** `scripts/github_delivery_common.py:117-133`, `scripts/vercel_delivery_common.py:143-166`
**Apply to:** All credential-bearing GitHub/Vercel helpers and Phase 12 governance wrappers
```python
if not locator("gh"):
    return _blocked(..., "missing_gh_cli", ...)
if not _has_github_auth(env):
    return _blocked(..., "missing_github_auth", ...)
```
```python
if not command:
    return None, _blocked(..., "missing_vercel_cli", ...)
if not source.get("VERCEL_TOKEN"):
    return None, _blocked(..., "missing_vercel_auth", ...)
```
Keep credentials behind helper functions; do not add freeform shell calls in the pipeline.

### Append-only audit/event stream
**Source:** `scripts/append_approved_delivery_event.py:13-48`, `scripts/start_approved_project_delivery.py:415-424`, `427-464`
**Apply to:** Credential audit events, protected-change blocks, justification approvals
```python
REQUIRED_EVENT_FIELDS = (
    "project_slug", "stage", "status", "action", "timestamp", "outcome",
    "authority_record_path", "brief_path", "workspace_path", "delivery_run_id",
    "artifact", "block_reason", "evidence_path", "resume_from_stage", "final_handoff_path",
)
```
```python
append_approved_delivery_event(project_dir, event)
```
Extend the existing event stream instead of creating a second logging system.

### Protected-surface detection
**Source:** `scripts/check_template_conformance.py:30-53`, `165-176`, `208-260`
**Apply to:** Pre-sync and pre-deploy touched-path classification
```python
PROTECTED_PATHS = (
    "src/lib/auth.ts",
    "src/lib/supabase-browser.ts",
    ...
    "supabase/migrations/20260423112500_create_shared_public_tables.sql",
)
```
```python
def build_protected_manifest(...):
    return [
        {
            "path": manifest_path,
            "asset_id": asset_id,
            "template_source_path": template_source_path,
            "hash_algorithm": "sha256",
        }
        for manifest_path in PROTECTED_MANIFEST_PATHS
    ]
```
Use this deterministic manifest/path-list approach for product-vs-platform classification.

### Governance request / approval state machine
**Source:** `scripts/request_governance_approval.py:67-127`, `scripts/governance_common.py:297-317`
**Apply to:** Platform-justification artifact and approval flow
```python
return {
    "action_id": generate_action_id(),
    "event_type": "requested",
    ...
    "status_after": "pending",
    ...
}
```
```python
if str(latest.get("status_after", "")).lower() != "pending":
    raise GovernanceApprovalError(f"action_id is not pending: {action_id}")
```
```python
lines = [
    "# Governance Status",
    f"- **Authority Source**: `{relative(GOVERNANCE_EVENTS_PATH)}`",
    ...
]
```
Reuse the existing governance language and transitions for justification, not a new approval vocabulary.

### Operator-facing markdown surface
**Source:** `scripts/render_approved_delivery_status.py:63-101`, `scripts/governance_common.py:297-317`
**Apply to:** Final Phase 12 operator review artifact
```python
"# Delivery Pipeline Status",
f"- **Block Reason**: `{latest.get('block_reason', 'not available')}`",
f"- **Evidence Path**: `{latest.get('evidence_path', 'not available')}`",
"## Event History",
```
Keep the review artifact file-based, markdown-first, and explicit about blocked/failed outcomes.

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| None | - | - | Existing approved-delivery, governance, conformance, and test code already provide direct or close analogs for all implied Phase 12 files. |

## Metadata

**Analog search scope:** `scripts/`, `tests/`, `orchestration/cron/`
**Files scanned:** 12 primary analog files plus phase context/research inputs
**Pattern extraction date:** 2026-04-27
