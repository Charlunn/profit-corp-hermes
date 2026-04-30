# Phase 10: Approved Project Delivery Pipeline - Pattern Map

**Mapped:** 2026-04-27
**Files analyzed:** 9
**Analogs found:** 9 / 9
**Research file present:** no `10-RESEARCH.md` found; mapping based on `10-CONTEXT.md`, Phase 9 context, and existing repo code/contracts.

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `scripts/start_approved_project_delivery.py` | controller | batch | `scripts/start_delivery_run.py` + `scripts/instantiate_template_project.py` | partial-match |
| `scripts/append_approved_delivery_event.py` | utility | event-driven | `scripts/append_delivery_event.py` | exact |
| `scripts/render_approved_delivery_status.py` | utility | transform | `scripts/render_delivery_status.py` | exact |
| `scripts/validate_approved_delivery_pipeline.py` | utility | batch | `scripts/validate_delivery_handoff.py` + `scripts/check_template_conformance.py` | role-match |
| `orchestration/cron/commands.sh` | config | request-response | `orchestration/cron/commands.sh` | exact |
| `assets/workspaces/ceo/AGENTS.md` | config | request-response | `assets/workspaces/ceo/AGENTS.md` | exact |
| `docs/OPERATIONS.md` | config | request-response | `docs/OPERATIONS.md` | exact |
| `assets/shared/approved-projects/<project>/APPROVED_PROJECT.json` | model | CRUD | `.hermes/project-metadata.json` emitted by `scripts/instantiate_template_project.py` | partial-match |
| `assets/shared/approved-projects/<project>/DELIVERY_PIPELINE_STATUS.md` | latest-view artifact | transform | workspace `.hermes/DELIVERY_STATUS.md` rendered by `scripts/render_delivery_status.py` | role-match |

## Pattern Assignments

### `scripts/start_approved_project_delivery.py` (controller, batch)

**Recommended analogs:**
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\start_delivery_run.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\instantiate_template_project.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\request_scope_reopen.py`

**Imports/bootstrap pattern** from `scripts/start_delivery_run.py` (lines 0-10):
```python
#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))
```

**CLI contract pattern** from `scripts/instantiate_template_project.py` (lines 49-60):
```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Instantiate a Hermes-managed project workspace from the registered template.")
    parser.add_argument("--asset-id", default=DEFAULT_ASSET_ID, help="Template asset identifier.")
    parser.add_argument("--registry-path", default=str(DEFAULT_REGISTRY_PATH), help="Path to the template registry JSON.")
    parser.add_argument("--workspace-name", required=True, help="Workspace folder name under the workspace root.")
    parser.add_argument("--workspace-root", default=str(GENERATED_WORKSPACES_DIR), help="Allowed Hermes workspace root.")
    parser.add_argument("--app-key", required=True, help="APP_KEY for the generated project.")
    parser.add_argument("--app-name", required=True, help="APP_NAME for the generated project.")
    parser.add_argument("--app-url", required=True, help="APP_URL for the generated project.")
    parser.add_argument("--template-source-path", default="", help="Override the registered template source path.")
    parser.add_argument("--dry-run", action="store_true", help="Print the intended actions without writing files.")
```

**Required-input/blocking pattern** from `scripts/start_delivery_run.py` (lines 62-79):
```python
def resolve_required_paths(workspace: Path) -> dict[str, Path]:
    workspace_root = workspace.parent
    resolved: dict[str, Path] = {}
    for key, relative_path in REQUIRED_INPUTS.items():
        if relative_path.startswith(".hermes/"):
            resolved[key] = workspace / relative_path
        else:
            resolved[key] = workspace_root / relative_path
    return resolved


def validate_required_inputs(workspace: Path) -> tuple[bool, str | None, dict[str, Path]]:
    resolved = resolve_required_paths(workspace)
    for key, path in resolved.items():
        if not path.exists():
            return False, f"missing required input '{key}': {REQUIRED_INPUTS[key]} ({path.as_posix()})", resolved
    return True, None, resolved
```

**Pipeline orchestration pattern** from `scripts/start_delivery_run.py` (lines 110-150):
```python
def initialize_delivery_run(workspace: Path) -> dict[str, Any]:
    workspace = Path(workspace)
    ok, error, resolved_inputs = validate_required_inputs(workspace)
    if not ok:
        return {"ok": False, "error": error}

    metadata = load_json(resolved_inputs["project_metadata_path"], "project metadata")
    manifest = build_manifest(workspace, metadata)
    hermes_dir = workspace / ".hermes"
    stage_handoffs_dir = hermes_dir / "stage-handoffs"
    stage_handoffs_dir.mkdir(parents=True, exist_ok=True)

    (hermes_dir / "delivery-events.jsonl").write_text("", encoding="utf-8")
    write_text(hermes_dir / "delivery-run-manifest.json", json.dumps(manifest, ensure_ascii=False, indent=2))
    write_text(hermes_dir / "DELIVERY_SCOPE.md", build_scope_markdown(manifest))
```

**Template/bootstrap sequencing pattern** from `scripts/instantiate_template_project.py` (lines 191-201):
```python
def instantiate_workspace(template_source: Path, workspace_root: Path, workspace: Path, identity: dict[str, str], metadata: dict[str, str]) -> None:
    workspace_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        template_source,
        workspace,
        dirs_exist_ok=False,
        ignore=shutil.ignore_patterns("node_modules", ".next", ".git"),
    )
    update_env_file(workspace / ".env", identity)
    update_app_definition(workspace / "src" / "lib" / "app-definition.ts", identity)
    write_hermes_handoff(workspace, metadata)
```

**Error return pattern** from `scripts/instantiate_template_project.py` (lines 221-223) and `scripts/start_delivery_run.py` (lines 157-164):
```python
except TemplateContractError as exc:
    print(f"template instantiate error: {exc}", file=sys.stderr)
    return 1
```
```python
except DeliveryRunError as exc:
    print(f"delivery run initialization error: {exc}", file=sys.stderr)
    return 1
if not result["ok"]:
    print(result["error"], file=sys.stderr)
    return 1
```

**Recommended copy target for Phase 10:**
Build this new script as a thin orchestrator that:
1. validates owner approval inputs,
2. writes approved-project bundle,
3. calls template instantiation flow,
4. runs conformance gate,
5. starts delivery run,
6. appends pipeline-level events,
7. renders latest status.

---

### `scripts/append_approved_delivery_event.py` (utility, event-driven)

**Analog:** `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\append_delivery_event.py`

**Required field contract** (lines 13-31):
```python
EVENTS_RELATIVE_PATH = ".hermes/delivery-events.jsonl"
REQUIRED_EVENT_FIELDS = (
    "run_id",
    "workspace_name",
    "role",
    "stage",
    "action",
    "artifact",
    "timestamp",
    "outcome",
)
ALLOWED_ROLE_STAGE = {
    "delivery-orchestrator": {"design"},
    "design-specialist": {"design"},
    "development-specialist": {"development"},
    "testing-specialist": {"testing"},
    "git-versioning-specialist": {"git versioning"},
    "release-readiness-specialist": {"release readiness"},
}
```

**Validation pattern** (lines 67-82):
```python
def validate_event(event: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_EVENT_FIELDS if field not in event]
    if missing:
        raise DeliveryEventError(f"delivery event missing required fields: {', '.join(missing)}")
    for field in REQUIRED_EVENT_FIELDS:
        value = event.get(field)
        if not isinstance(value, str) or not value.strip():
            raise DeliveryEventError(f"delivery event field must be a non-empty string: {field}")
    role = event["role"]
    stage = event["stage"]
    allowed_stages = ALLOWED_ROLE_STAGE.get(role)
    if allowed_stages is None:
        raise DeliveryEventError(f"unsupported delivery role: {role}")
    if stage not in allowed_stages:
        raise DeliveryEventError(f"role '{role}' is not allowed to emit stage '{stage}'")
```

**Append-only ordering pattern** (lines 84-96):
```python
def append_delivery_event(workspace: Path, event: dict[str, Any]) -> None:
    workspace = Path(workspace)
    validate_event(event)
    path = events_path_for(workspace)
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = load_events(path)
    if existing:
        latest_timestamp = str(existing[-1].get("timestamp", ""))
        if event["timestamp"] < latest_timestamp:
            raise DeliveryEventError("delivery events must append in nondecreasing timestamp order")
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")
```

**Recommended copy target for Phase 10:**
Keep the same append-only JSONL pattern, but define pipeline stages such as `approval`, `brief_generation`, `workspace_instantiation`, `conformance`, `delivery_run_bootstrap`, `handoff`, plus blocked outcomes/reasons.

---

### `scripts/render_approved_delivery_status.py` (utility, transform)

**Analog:** `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\render_delivery_status.py`

**Event-stream loader pattern** (lines 28-43):
```python
def load_events(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    events: list[dict[str, Any]] = []
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue
        try:
            payload = json.loads(line)
        except json.JSONDecodeError as exc:
            raise DeliveryStatusError(f"invalid JSONL at line {line_number}: {path}") from exc
        if not isinstance(payload, dict):
            raise DeliveryStatusError(f"delivery event at line {line_number} must be an object")
        events.append(payload)
    return events
```

**Latest-view markdown pattern** (lines 46-64):
```python
def build_status_markdown(events: list[dict[str, Any]]) -> str:
    latest = events[-1] if events else {}
    return "\n".join(
        [
            "# Delivery Status",
            f"- **Authority Source**: `{EVENTS_RELATIVE_PATH}`",
            f"- **Run ID**: `{latest.get('run_id', 'not available')}`",
            f"- **Workspace**: `{latest.get('workspace_name', 'not available')}`",
            f"- **Current Stage**: `{latest.get('stage', 'not available')}`",
            f"- **Last Role**: `{latest.get('role', 'not available')}`",
            f"- **Last Action**: `{latest.get('action', 'not available')}`",
            f"- **Latest Outcome**: `{latest.get('outcome', 'not available')}`",
            f"- **Gate Status**: `{latest.get('gate_status', 'not available')}`",
            f"- **Scope Status**: `{latest.get('scope_status', 'not available')}`",
            f"- **Latest Artifact**: `{latest.get('artifact', 'not available')}`",
            "",
            "This latest view is derived from the append-only delivery event stream.",
        ]
    ).rstrip() + "\n"
```

**Write-through renderer pattern** (lines 67-74):
```python
def render_delivery_status(workspace: Path) -> str:
    workspace = Path(workspace)
    events = load_events(workspace / EVENTS_RELATIVE_PATH)
    markdown = build_status_markdown(events)
    status_path = workspace / STATUS_RELATIVE_PATH
    status_path.parent.mkdir(parents=True, exist_ok=True)
    status_path.write_text(markdown, encoding="utf-8")
    return markdown
```

**Recommended copy target for Phase 10:**
Reuse this exact "authority stream -> concise latest view" pattern for a top-level approved-delivery pipeline status file outside the workspace, including block reason, resume hint, linked workspace path, and linked approved-project bundle path.

---

### `scripts/validate_approved_delivery_pipeline.py` (utility, batch)

**Recommended analogs:**
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\validate_delivery_handoff.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\check_template_conformance.py`

**Ordered-section validation pattern** from `scripts/validate_delivery_handoff.py` (lines 98-111):
```python
def require_in_order(text: str, headings: list[str], label: str) -> None:
    positions: list[int] = []
    for heading in headings:
        if heading not in text:
            raise DeliveryHandoffValidationError(f"{label} missing required section: {heading}")
        positions.append(text.index(heading))
    if positions != sorted(positions):
        raise DeliveryHandoffValidationError(f"{label} section order drifted")


def require_tokens(text: str, tokens: list[str], label: str) -> None:
    missing = [token for token in tokens if token not in text]
    if missing:
        raise DeliveryHandoffValidationError(f"{label} missing required metadata: {', '.join(missing)}")
```

**Replay/artifact cross-check pattern** from `scripts/validate_delivery_handoff.py` (lines 155-207):
```python
def validate_delivery_run(workspace: Path) -> dict[str, Any]:
    workspace = Path(workspace)
    manifest = load_json(workspace / MANIFEST_RELATIVE_PATH, "delivery run manifest")
    events = load_jsonl(workspace / EVENTS_RELATIVE_PATH)
    run_id = str(manifest.get("run_id", "")).strip()
    if not run_id:
        return {"ok": False, "error": "delivery run manifest missing run_id"}
```
```python
            matching_events = [event for event in events if event.get("stage") == stage and event.get("role") == role and event.get("artifact") == artifact]
            if not matching_events:
                raise DeliveryHandoffValidationError(f"missing replay event for stage {stage} and artifact {artifact}")
```

**Blocking-violation pattern** from `scripts/check_template_conformance.py` (lines 80-85):
```python
class BlockingViolationError(TemplateConformanceError):
    def __init__(self, violations: list[str], *, fingerprint_checks: list[dict[str, str]] | None = None):
        super().__init__("blocking template conformance violations")
        self.violations = violations
        self.fingerprint_checks = fingerprint_checks or []
```

**Report-building pattern** from `scripts/check_template_conformance.py` (lines 334-368):
```python
def build_report_lines(
    *,
    status: str,
    violations: list[str],
    verified_paths: list[str],
    fingerprint_checks: list[dict[str, str]],
    workspace_path: Path,
    contract_path: Path,
    registry_path: Path,
) -> list[str]:
```

**Recommended copy target for Phase 10:**
Use one validator to assert pipeline prerequisites and generated artifacts are all present and cross-linked: approved record, brief, workspace path, conformance report, delivery-run manifest, event stream, and final handoff linkage.

---

### `orchestration/cron/commands.sh` (config, request-response)

**Analog:** `C:\Users\42236\Desktop\dev\profit-corp-hermes\orchestration\cron\commands.sh`

**Wrapper function pattern** (lines 136-179):
```bash
start_delivery_run() {
  if [ "${1:-}" = "--help" ]; then
    python "$ROOT_DIR/scripts/start_delivery_run.py" --help
    return 0
  fi
  [ "$#" -ge 1 ] || { echo "Usage: bash orchestration/cron/commands.sh start-delivery-run <workspace-path>"; return 1; }
  python "$ROOT_DIR/scripts/start_delivery_run.py" --workspace-path "$1"
}
```
```bash
request_scope_reopen_cmd() {
  if [ "${1:-}" = "--help" ]; then
    python "$ROOT_DIR/scripts/request_scope_reopen.py" --help
    return 0
  fi
  [ "$#" -ge 6 ] || { echo "Usage: bash orchestration/cron/commands.sh request-scope-reopen <workspace-path> <run-id> <stage> <role> <target-artifact> <reason>"; return 1; }
  python "$ROOT_DIR/scripts/request_scope_reopen.py" --workspace-path "$1" --run-id "$2" --stage "$3" --role "$4" --target-artifact "$5" --reason "$6"
}
```

**Case dispatch pattern** (lines 190-230):
```bash
  start-delivery-run)
    shift
    start_delivery_run "$@"
    ;;
  append-delivery-event)
    shift
    append_delivery_event_cmd "$@"
    ;;
  render-delivery-status)
    shift
    render_delivery_status_cmd "$@"
    ;;
```

**Recommended copy target for Phase 10:**
Add parallel wrappers for top-level approved-delivery commands, likely:
- `start-approved-delivery`
- `append-approved-delivery-event`
- `render-approved-delivery-status`
- `validate-approved-delivery-pipeline`
- `resume-approved-delivery`

Keep the same help/usage/dispatch style.

---

### `assets/workspaces/ceo/AGENTS.md` (config, request-response)

**Analog:** `C:\Users\42236\Desktop\dev\profit-corp-hermes\assets\workspaces\ceo\AGENTS.md`

**Delegation example pattern** (lines 41-76):
```markdown
### Delivery Orchestrator Delegation Example
```python
delegate_task(
  goal="Run the approved mini-SaaS delivery workflow end to end",
  context="""
  Read these required inputs before starting:
  - .hermes/PROJECT_BRIEF_ENTRYPOINT.md
  - docs/platform/standalone-saas-template-contract.md
  - .hermes/shared-backend-guardrails.json
  - .hermes/project-metadata.json
  - .planning/phases/09-claude-code-delivery-team-orchestration/09-01-PLAN.md
```

**Scope-discipline pattern** (lines 78-82):
```markdown
### Delivery Scope Discipline
- 默认交付范围是 `approved-brief-only`，不得把新需求直接塞进当前 run。
- 触达受保护路径或出现扩 scope 时，必须先走 `request_scope_reopen.py`，等待治理结果后再继续。
- 交付编排仍复用当前 `delegate_task` 语法，不引入第二套 orchestration DSL。
```

**Recommended copy target for Phase 10:**
Add a new CEO command/delegation section for approval-to-delivery initiation. Keep the same structure: explicit required inputs, required outputs, acceptance criteria, and hard block/resume language.

---

### `docs/OPERATIONS.md` (config, request-response)

**Analog:** `C:\Users\42236\Desktop\dev\profit-corp-hermes\docs\OPERATIONS.md`

**Operator checklist pattern** (lines 2-20):
```markdown
## Daily operator checklist
1. Ensure cron baseline is healthy:
   ```bash
   bash orchestration/cron/commands.sh ensure
   bash orchestration/cron/commands.sh status
   ```
2. Verify scheduled jobs and recent outputs:
   ```bash
   hermes -p ceo cron list
   ```
```

**Incident-response pattern** (lines 60-85):
```markdown
### D) State write conflict or abnormal transition
- Pause automatic writes for investigation:
  ```bash
  bash orchestration/cron/commands.sh pause-all
  ```
- Inspect last produced artifacts and ownership chain per `docs/MULTI_PROFILE_COORDINATION.md`.
```
```markdown
### E) Governance-blocked high-impact action
- Review latest governance state:
  ```bash
  python scripts/render_governance_status.py --dry-run
  ```
```

**Visibility pattern** (lines 87-108):
```markdown
## Operating Visibility
- Read the latest operator surface first:
  ```bash
  python scripts/generate_operating_visibility.py
  ```
```

**Recommended copy target for Phase 10:**
Document the approved-delivery operator path as:
1. verify approval record,
2. start approved-delivery pipeline,
3. inspect latest pipeline status,
4. resolve block reasons,
5. resume/retry without restarting from scratch.

---

### `assets/shared/approved-projects/<project>/APPROVED_PROJECT.json` (model, CRUD)

**Recommended analogs:**
- metadata shape from `scripts/instantiate_template_project.py` lines 120-133
- required input contract from `docs/skill-governance/templates/orchestrator-input-template-v0.2.md` lines 29-35

**Metadata payload pattern** from `scripts/instantiate_template_project.py` (lines 120-133):
```python
def build_metadata(asset: dict, workspace_name: str, identity: dict[str, str], template_source_path: Path) -> dict[str, str]:
    contract_path = DEFAULT_CONTRACT_PATH
    canonical_contract = str(asset.get("canonical_contract", "")).strip()
    if canonical_contract:
        contract_path = ROOT_DIR / canonical_contract
    return {
        "asset_id": asset["asset_id"],
        "workspace_name": workspace_name,
        "app_key": identity["APP_KEY"],
        "app_name": identity["APP_NAME"],
        "app_url": identity["APP_URL"],
        "template_source_path": template_source_path.as_posix(),
        "canonical_contract_path": contract_path.as_posix(),
    }
```

**Approved-bundle field pattern** from `docs/skill-governance/templates/orchestrator-input-template-v0.2.md` (lines 29-35):
```markdown
### Approved-project Delivery Bundle
- `approved brief path`: `.hermes/PROJECT_BRIEF_ENTRYPOINT.md`
- `template contract path`: `docs/platform/standalone-saas-template-contract.md`
- `shared-backend guardrails path`: `.hermes/shared-backend-guardrails.json`
- `project metadata path`: `.hermes/project-metadata.json`
- `gsd constraints source`: `.planning/phases/09-claude-code-delivery-team-orchestration/09-01-PLAN.md`
- required bundle fields: approved brief, template contract, .hermes/shared-backend-guardrails.json, .hermes/project-metadata.json, GSD constraints
```

**Recommended copy target for Phase 10:**
Use a compact JSON record as the single source of truth for approval-to-delivery. Include stable identifiers plus all downstream bundle paths and current pipeline pointers.

---

### `assets/shared/approved-projects/<project>/DELIVERY_PIPELINE_STATUS.md` (latest-view artifact, transform)

**Recommended analogs:**
- `scripts/render_delivery_status.py` lines 46-64
- `docs/skill-governance/templates/stage-handoff-template-v0.2.md` lines 4-33
- `docs/skill-governance/templates/final-delivery-template-v0.2.md` lines 4-40

**Stage vocabulary pattern** from `docs/skill-governance/templates/stage-handoff-template-v0.2.md` (lines 4-33):
```markdown
## 1) Stage Summary
- `run_id`:
- `role`:
- `stage`:
- `scope_status`: approved-brief-only | in-scope | scope-reopen-requested | blocked
- `summary`:
```

**Final gate snapshot pattern** from `docs/skill-governance/templates/final-delivery-template-v0.2.md` (lines 25-40):
```markdown
## 4) Gate Status Snapshot
- 分层依赖：PASS | FAIL
- lint/format/type-check：PASS | FAIL
- 测试证据：PASS | FAIL
- 日志规范：PASS | FAIL
- 回滚方案：PASS | FAIL

## 6) Release Recommendation
- 建议：可发布 | 阻断
- 风险等级：low | med | high
- 说明：
```

**Recommended copy target for Phase 10:**
Render a concise operator-facing status file with current stage, last action, block reason, linked artifacts, and next action. Reuse the same gate/status vocabulary already used by delivery-run artifacts.

## Shared Patterns

### Artifact-first orchestration
**Sources:**
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\docs\MULTI_PROFILE_COORDINATION.md` lines 9-24
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\skills\library\normalized\orchestrator-workflow.md` lines 22-28, 65-76

**Apply to:** all new pipeline scripts and CEO instructions

```markdown
1. 所有跨角色任务通过 CEO 统一编排。
2. 角色只写自己的目标产物，不直接修改他人核心文档。
```
```markdown
- `delivery-orchestrator`：唯一编排角色，负责加载输入包、按顺序发起阶段、阻断跳步、回收 artifact handoff。
```

### Hard blocking with explicit evidence
**Sources:**
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\start_delivery_run.py` lines 74-79
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\check_template_conformance.py` lines 179-205
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\.planning\phases\10-approved-project-delivery-pipeline\10-CONTEXT.md` lines 35-39

**Apply to:** approval check, brief generation, workspace instantiation, conformance, downstream prerequisites

```python
for key, path in resolved.items():
    if not path.exists():
        return False, f"missing required input '{key}': {REQUIRED_INPUTS[key]} ({path.as_posix()})", resolved
```

### Dual-surface state: JSONL authority + markdown latest view
**Sources:**
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\append_delivery_event.py` lines 84-96
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\render_delivery_status.py` lines 46-74
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\.planning\phases\10-approved-project-delivery-pipeline\10-CONTEXT.md` lines 30-34

**Apply to:** top-level approved delivery pipeline record

```python
with path.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(event, ensure_ascii=False) + "\n")
```
```python
latest = events[-1] if events else {}
```

### Existing governed command-entry wrappers
**Source:** `C:\Users\42236\Desktop\dev\profit-corp-hermes\orchestration\cron\commands.sh` lines 136-179, 190-230

**Apply to:** new operator entrypoints instead of bespoke shell scripts

```bash
  [ "$#" -ge 1 ] || { echo "Usage: ..."; return 1; }
  python "$ROOT_DIR/scripts/start_delivery_run.py" --workspace-path "$1"
```

### Scope/governance escalation instead of silent expansion
**Sources:**
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\request_scope_reopen.py` lines 44-49, 93-128
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\assets\workspaces\ceo\AGENTS.md` lines 67-72, 78-82

**Apply to:** any blocked Phase 10 run that discovers missing downstream prerequisites or protected-path work

```python
if normalized in PROTECTED_PATHS:
    return "delivery.scope_reopen.protected_path"
return "delivery.scope_reopen.scope_expansion"
```

## Recommended Target Files

### High-confidence new scripts
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\start_approved_project_delivery.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\append_approved_delivery_event.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\render_approved_delivery_status.py`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\scripts\validate_approved_delivery_pipeline.py`

### High-confidence modified entrypoints/contracts
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\orchestration\cron\commands.sh`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\assets\workspaces\ceo\AGENTS.md`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\docs\OPERATIONS.md`

### High-confidence new artifacts
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\assets\shared\approved-projects\<project>\APPROVED_PROJECT.json`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\assets\shared\approved-projects\<project>\PROJECT_BRIEF.md`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\assets\shared\approved-projects\<project>\approved-delivery-events.jsonl`
- `C:\Users\42236\Desktop\dev\profit-corp-hermes\assets\shared\approved-projects\<project>\DELIVERY_PIPELINE_STATUS.md`

## No Analog Found

| File | Role | Data Flow | Reason |
|---|---|---|---|
| `assets/shared/approved-projects/<project>/APPROVED_PROJECT.json` | model | CRUD | Repo has workspace metadata and decision-package artifacts, but no existing owner-approval record as a delivery trigger. |
| `scripts/start_approved_project_delivery.py` | controller | batch | Repo has delivery-run bootstrap and template instantiation separately, but no single approval-to-delivery bridge yet. |

## Metadata

**Analog search scope:** `scripts/`, `orchestration/cron/`, `assets/workspaces/ceo/`, `docs/`, `.planning/phases/09-*`, `.planning/phases/10-*`, `skills/`
**Files scanned:** 20+
**Pattern extraction date:** 2026-04-27
