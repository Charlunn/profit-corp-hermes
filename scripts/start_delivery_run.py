#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))


REQUIRED_INPUTS = {
    "approved_brief_path": ".hermes/PROJECT_BRIEF_ENTRYPOINT.md",
    "template_contract_path": "docs/platform/standalone-saas-template-contract.md",
    "shared_backend_guardrails_path": ".hermes/shared-backend-guardrails.json",
    "project_metadata_path": ".hermes/project-metadata.json",
    "gsd_constraints_path": ".planning/phases/09-claude-code-delivery-team-orchestration/09-01-PLAN.md",
}
STAGES = [
    {"stage": "design", "role": "design-specialist", "artifact": ".hermes/stage-handoffs/01-design.md"},
    {"stage": "development", "role": "development-specialist", "artifact": ".hermes/stage-handoffs/02-development.md"},
    {"stage": "testing", "role": "testing-specialist", "artifact": ".hermes/stage-handoffs/03-testing.md"},
    {"stage": "git versioning", "role": "git-versioning-specialist", "artifact": ".hermes/stage-handoffs/04-git-versioning.md"},
    {"stage": "release readiness", "role": "release-readiness-specialist", "artifact": ".hermes/stage-handoffs/05-release-readiness.md"},
]
DEFAULT_SCOPE_STATUS = "approved-brief-only"
ORCHESTRATOR_ROLE = "delivery-orchestrator"
EVENTS_PATH = ".hermes/delivery-events.jsonl"
STATUS_PATH = ".hermes/DELIVERY_STATUS.md"
MANIFEST_PATH = ".hermes/delivery-run-manifest.json"
SCOPE_PATH = ".hermes/DELIVERY_SCOPE.md"


class DeliveryRunError(Exception):
    pass


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Initialize a workspace-local Hermes delivery run.")
    parser.add_argument("--workspace-path", required=True, help="Path to the generated workspace.")
    return parser.parse_args()


def load_json(path: Path, label: str) -> dict[str, Any]:
    if not path.exists():
        raise DeliveryRunError(f"{label} not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise DeliveryRunError(f"invalid JSON in {label}: {path}") from exc
    if not isinstance(payload, dict):
        raise DeliveryRunError(f"{label} must be a JSON object: {path}")
    return payload


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def resolve_required_paths(workspace: Path) -> dict[str, Path]:
    workspace_root = workspace.parent
    resolved: dict[str, Path] = {}
    metadata_path = workspace / REQUIRED_INPUTS["project_metadata_path"]
    contract_path = None
    constraints_path = None
    if metadata_path.exists():
        metadata = load_json(metadata_path, "project metadata")
        contract_value = str(metadata.get("canonical_contract_path", "")).strip()
        if contract_value:
            contract_path = Path(contract_value)
        constraints_value = str(metadata.get("gsd_constraints_path", "")).strip()
        if constraints_value:
            constraints_path = Path(constraints_value)
    for key, relative_path in REQUIRED_INPUTS.items():
        if key == "template_contract_path" and contract_path is not None:
            resolved[key] = contract_path
        elif key == "gsd_constraints_path" and constraints_path is not None:
            resolved[key] = constraints_path
        elif relative_path.startswith(".hermes/"):
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


def build_manifest(workspace: Path, metadata: dict[str, Any]) -> dict[str, Any]:
    return {
        "run_id": f"delivery-{workspace.name}-001",
        "workspace_name": str(metadata.get("workspace_name", workspace.name)).strip() or workspace.name,
        "orchestrator_role": ORCHESTRATOR_ROLE,
        "scope_status": DEFAULT_SCOPE_STATUS,
        "required_inputs": dict(REQUIRED_INPUTS),
        "stage_order": [stage["stage"] for stage in STAGES],
        "stages": [dict(stage) for stage in STAGES],
        "authority_stream": EVENTS_PATH,
        "latest_status_path": STATUS_PATH,
    }


def build_scope_markdown(manifest: dict[str, Any]) -> str:
    return "\n".join(
        [
            "# Delivery Scope",
            "",
            f"- Workspace: `{manifest['workspace_name']}`",
            f"- Run ID: `{manifest['run_id']}`",
            f"- Scope Status: `{manifest['scope_status']}`",
            "- Change policy: approved brief only until a scope reopen is explicitly approved.",
            "- Scope reopen is required before protected platform changes or out-of-scope work may proceed.",
            "- Delivery state stays inside workspace-local `.hermes/` artifacts only.",
        ]
    )


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

    from scripts.append_delivery_event import append_delivery_event
    from scripts.render_delivery_status import render_delivery_status

    append_delivery_event(
        workspace,
        {
            "run_id": manifest["run_id"],
            "workspace_name": manifest["workspace_name"],
            "role": ORCHESTRATOR_ROLE,
            "stage": STAGES[0]["stage"],
            "action": "run_started",
            "artifact": MANIFEST_PATH,
            "timestamp": "2026-04-27T10:00:00Z",
            "outcome": "pass",
            "gate_status": "open",
            "scope_status": DEFAULT_SCOPE_STATUS,
        },
    )
    render_delivery_status(workspace)
    return {
        "ok": True,
        "workspace": workspace.as_posix(),
        "manifest_path": (workspace / MANIFEST_PATH).as_posix(),
        "status_path": (workspace / STATUS_PATH).as_posix(),
    }


def main() -> int:
    args = parse_args()
    try:
        result = initialize_delivery_run(Path(args.workspace_path))
    except DeliveryRunError as exc:
        print(f"delivery run initialization error: {exc}", file=sys.stderr)
        return 1
    if not result["ok"]:
        print(result["error"], file=sys.stderr)
        return 1
    print(f"initialized delivery run: {result['manifest_path']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
