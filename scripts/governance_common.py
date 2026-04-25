#!/usr/bin/env python3
import json
from collections import OrderedDict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
SHARED_DIR = ROOT_DIR / "assets" / "shared"
GOVERNANCE_DIR = SHARED_DIR / "governance"
GOVERNANCE_EVENTS_PATH = GOVERNANCE_DIR / "governance_events.jsonl"
GOVERNANCE_STATUS_PATH = GOVERNANCE_DIR / "GOVERNANCE_STATUS.md"
OPERATING_DECISION_PACKAGE_PATH = SHARED_DIR / "decision_packages" / "OPERATING_DECISION_PACKAGE.md"
DECISION_TRACE_PATH = SHARED_DIR / "trace" / "decision_package_trace.json"
ALLOWED_WRITE_DIRS = (
    GOVERNANCE_DIR,
)
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
STATUS_GROUPS = OrderedDict(
    [
        ("pending", "Pending Approvals"),
        ("blocked", "Active Blocks"),
        ("approved", "Recent Approvals"),
        ("rejected", "Recent Rejections"),
        ("override", "Recent Overrides"),
    ]
)
ACTION_RULES = OrderedDict(
    [
        ("finance.revenue", {"high_impact": True}),
        ("finance.bounty", {"high_impact": True}),
        ("archive", {"high_impact": True}),
        ("state.transition", {"high_impact": True}),
        ("fallback.takeover", {"high_impact": True}),
        ("pipeline.failure", {"high_impact": True}),
        ("governance.bootstrap", {"high_impact": False}),
    ]
)
WRITE_RULES = OrderedDict(
    [
        (
            "assets/shared/LEDGER.json",
            {
                "primary_writer": "manage_finance.py",
                "allowed_actors": {"ceo", "accountant"},
                "fallback_actor": None,
                "requires_governance": True,
                "finance_only": True,
            },
        ),
        (
            "assets/shared/PAIN_POINTS.md",
            {
                "primary_writer": "scout",
                "allowed_actors": {"scout"},
                "fallback_actor": "ceo",
                "requires_governance": True,
                "finance_only": False,
            },
        ),
        (
            "assets/shared/MARKET_PLAN.md",
            {
                "primary_writer": "cmo",
                "allowed_actors": {"cmo"},
                "fallback_actor": "ceo",
                "requires_governance": True,
                "finance_only": False,
            },
        ),
        (
            "assets/shared/TECH_SPEC.md",
            {
                "primary_writer": "arch",
                "allowed_actors": {"arch"},
                "fallback_actor": "ceo",
                "requires_governance": True,
                "finance_only": False,
            },
        ),
        (
            "assets/shared/external_intelligence/LATEST_SUMMARY.md",
            {
                "primary_writer": "external-intelligence collector workflow",
                "allowed_actors": {"external-intelligence collector workflow"},
                "fallback_actor": "ceo",
                "requires_governance": True,
                "finance_only": False,
            },
        ),
    ]
)


class GovernanceError(Exception):
    pass


def utc_now() -> datetime:
    return datetime.now(timezone.utc).replace(microsecond=0)


def timestamp_now() -> str:
    return utc_now().isoformat().replace("+00:00", "Z")


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


def write_text(path: Path, content: str) -> None:
    ensure_allowed_write_path(path)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def relative(path: Path) -> str:
    return path.relative_to(ROOT_DIR).as_posix()


def generate_action_id(prefix: str = "gov") -> str:
    return f"{prefix}-{utc_now().strftime('%Y%m%d%H%M%S')}"


def load_jsonl(path: Path = GOVERNANCE_EVENTS_PATH) -> list[dict[str, Any]]:
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
            raise GovernanceError(f"invalid JSONL at line {line_number}: {path}") from exc
        if not isinstance(payload, dict):
            raise GovernanceError(f"governance event at line {line_number} must be an object")
        validate_event(payload)
        events.append(payload)
    return events


def validate_event(event: dict[str, Any]) -> None:
    missing = [field for field in REQUIRED_EVENT_FIELDS if field not in event]
    if missing:
        raise GovernanceError(f"governance event missing required fields: {', '.join(missing)}")
    event_type = event.get("event_type")
    if event_type not in ALLOWED_EVENT_TYPES:
        raise GovernanceError(f"unsupported governance event_type: {event_type}")
    if not isinstance(event.get("action_id"), str) or not event["action_id"].strip():
        raise GovernanceError("governance event action_id must be a non-empty string")
    related_decision_package = event.get("related_decision_package")
    if related_decision_package != relative(OPERATING_DECISION_PACKAGE_PATH):
        raise GovernanceError("governance event must bind to the operating decision package path")
    related_trace = event.get("related_trace", {})
    if related_trace:
        if not isinstance(related_trace, dict):
            raise GovernanceError("related_trace must be an object when present")
        trace_path = related_trace.get("trace_path", "")
        if trace_path and trace_path != relative(DECISION_TRACE_PATH):
            raise GovernanceError("related_trace.trace_path must point to decision_package_trace.json")
        judgment_ids = related_trace.get("judgment_ids", [])
        if judgment_ids and not isinstance(judgment_ids, list):
            raise GovernanceError("related_trace.judgment_ids must be a list when present")
    approved_by = event.get("approved_by")
    if approved_by is not None and not isinstance(approved_by, str):
        raise GovernanceError("approved_by must be a string")


def append_event(event: dict[str, Any], path: Path = GOVERNANCE_EVENTS_PATH) -> None:
    validate_event(event)
    ensure_governance_dir()
    ensure_allowed_write_path(path)
    with path.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(event, ensure_ascii=False) + "\n")


def get_action_rule(action_type: str) -> dict[str, Any]:
    for prefix, rule in ACTION_RULES.items():
        if action_type == prefix or action_type.startswith(f"{prefix}."):
            return dict(rule)
    return {"high_impact": False}


def is_high_impact_action(action_type: str) -> bool:
    return bool(get_action_rule(action_type).get("high_impact", False))


def get_write_rule(target_artifact: str) -> dict[str, Any] | None:
    return WRITE_RULES.get(target_artifact)


def validate_actor_target(actor: str, target_artifact: str, action_type: str) -> dict[str, Any]:
    rule = get_write_rule(target_artifact)
    if rule is None:
        return {
            "primary_writer": "",
            "is_fallback": False,
            "requires_governance": is_high_impact_action(action_type),
            "finance_only": False,
        }
    if actor in rule["allowed_actors"]:
        return {
            "primary_writer": rule["primary_writer"],
            "is_fallback": False,
            "requires_governance": rule["requires_governance"],
            "finance_only": rule["finance_only"],
        }
    if actor == rule.get("fallback_actor"):
        return {
            "primary_writer": rule["primary_writer"],
            "is_fallback": True,
            "requires_governance": True,
            "finance_only": rule["finance_only"],
        }
    raise GovernanceError(f"actor '{actor}' is not allowed to govern target '{target_artifact}'")


def find_latest_event(action_id: str, events: list[dict[str, Any]] | None = None) -> dict[str, Any] | None:
    haystack = events if events is not None else load_jsonl(GOVERNANCE_EVENTS_PATH)
    latest: dict[str, Any] | None = None
    for event in haystack:
        if event.get("action_id") != action_id:
            continue
        if latest is None or (event.get("timestamp", ""), event.get("action_id", "")) >= (
            latest.get("timestamp", ""),
            latest.get("action_id", ""),
        ):
            latest = event
    return latest


def refresh_status_view() -> None:
    write_text(GOVERNANCE_STATUS_PATH, render_status_markdown(load_jsonl(GOVERNANCE_EVENTS_PATH)))


def group_latest_by_action(events: list[dict[str, Any]]) -> OrderedDict[str, dict[str, Any]]:
    latest: OrderedDict[str, dict[str, Any]] = OrderedDict()
    for event in sorted(events, key=lambda item: (item.get("timestamp", ""), item.get("action_id", ""))):
        latest[event["action_id"]] = event
    return latest


def build_status_sections(events: list[dict[str, Any]]) -> OrderedDict[str, list[dict[str, Any]]]:
    grouped: OrderedDict[str, list[dict[str, Any]]] = OrderedDict((key, []) for key in STATUS_GROUPS)
    for event in group_latest_by_action(events).values():
        status = str(event.get("status_after", "")).strip().lower()
        if status in grouped:
            grouped[status].append(event)
    for section_events in grouped.values():
        section_events.sort(key=lambda item: item.get("timestamp", ""), reverse=True)
    return grouped


def format_status_line(event: dict[str, Any]) -> str:
    action_id = event["action_id"]
    action_type = event.get("action_type", "unknown")
    target = event["target_artifact"]
    current_status = event.get("status_after", "unknown")
    decision_package = event["related_decision_package"]
    reason = event.get("reason") or event.get("override_reason") or "No reason recorded"
    return (
        f"- `{action_id}` - `{action_type}` -> `{target}` - status: `{current_status}` - "
        f"decision: `{decision_package}` - reason: {reason}"
    )


def render_status_markdown(events: list[dict[str, Any]]) -> str:
    sections = build_status_sections(events)
    lines = [
        "# Governance Status",
        f"- **Authority Source**: `{relative(GOVERNANCE_EVENTS_PATH)}`",
        f"- **Decision Package Anchor**: `{relative(OPERATING_DECISION_PACKAGE_PATH)}`",
        f"- **Trace Anchor**: `{relative(DECISION_TRACE_PATH)}`",
        "",
        "This latest view is derived from the append-only governance JSONL stream.",
        "",
    ]
    for status_key, heading in STATUS_GROUPS.items():
        lines.append(f"## {heading}")
        section_events = sections[status_key]
        if section_events:
            for event in section_events:
                lines.append(format_status_line(event))
        else:
            lines.append("- None")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def bootstrap_event() -> dict[str, Any]:
    return {
        "action_id": "gov-bootstrap-20260425",
        "event_type": "requested",
        "action_type": "governance.bootstrap",
        "actor": "ceo",
        "target_artifact": "assets/shared/governance/GOVERNANCE_STATUS.md",
        "related_decision_package": relative(OPERATING_DECISION_PACKAGE_PATH),
        "status_before": "none",
        "status_after": "pending",
        "approved_by": "ceo",
        "timestamp": timestamp_now(),
        "reason": "Initialize dedicated governance event stream and latest status view for Phase 4.",
        "result_code": "bootstrap_initialized",
        "primary_writer": "ceo",
        "override_reason": "",
        "related_trace": {
            "trace_path": relative(DECISION_TRACE_PATH),
            "judgment_ids": ["action-idea-001-prototype"],
        },
    }
