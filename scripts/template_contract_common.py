#!/usr/bin/env python3
import json
import re
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
SHARED_DIR = ROOT_DIR / "assets" / "shared"
TEMPLATES_DIR = SHARED_DIR / "templates"
DEFAULT_REGISTRY_PATH = TEMPLATES_DIR / "standalone-saas-template.json"
GENERATED_WORKSPACES_DIR = ROOT_DIR / "assets" / "workspaces" / "projects"
ALLOWED_WORKSPACE_ROOTS = (
    GENERATED_WORKSPACES_DIR,
)
APP_KEY_PATTERN = re.compile(r"^[a-z0-9]+(?:_[a-z0-9]+)*$")
REQUIRED_IDENTITY_KEYS = (
    "APP_KEY",
    "APP_NAME",
    "APP_URL",
    "PAYPAL_BRAND_NAME",
    "APP_DEFINITION_NAME",
    "APP_DEFINITION_URL",
    "APP_DEFINITION_PRODUCT_ID",
    "APP_DEFINITION_DESCRIPTION",
)


class TemplateContractError(Exception):
    pass


def load_registry(path: Path) -> dict[str, Any]:
    if not path.exists():
        raise TemplateContractError(f"template registry not found: {path}")
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise TemplateContractError(f"invalid template registry JSON: {path}") from exc
    if not isinstance(payload, dict):
        raise TemplateContractError("template registry root must be an object")
    return payload


def require_asset(registry: dict[str, Any], asset_id: str = "standalone-saas-template") -> dict[str, Any]:
    current_asset_id = registry.get("asset_id")
    if current_asset_id != asset_id:
        raise TemplateContractError(f"template registry asset_id mismatch: expected {asset_id}, got {current_asset_id}")
    return registry


def ensure_allowed_workspace_path(path: Path) -> None:
    resolved = path.resolve()
    for directory in ALLOWED_WORKSPACE_ROOTS:
        try:
            resolved.relative_to(directory.resolve())
            return
        except ValueError:
            continue
    raise TemplateContractError(f"refusing to write outside allowed workspace roots: {path}")


def validate_identity(app_key: str, app_name: str, app_url: str) -> dict[str, str]:
    normalized = {
        "APP_KEY": app_key.strip(),
        "APP_NAME": app_name.strip(),
        "APP_URL": app_url.strip(),
    }
    for key, value in normalized.items():
        if not value:
            raise TemplateContractError(f"{key} must not be blank")

    if not APP_KEY_PATTERN.fullmatch(normalized["APP_KEY"]):
        raise TemplateContractError("APP_KEY must be lowercase snake_case, e.g. lead_capture")

    if not (normalized["APP_URL"].startswith("http://") or normalized["APP_URL"].startswith("https://")):
        raise TemplateContractError("APP_URL must start with http:// or https://")

    return normalized


def build_identity_payload(app_key: str, app_name: str, app_url: str) -> dict[str, str]:
    validated = validate_identity(app_key, app_name, app_url)
    payload = {
        "APP_KEY": validated["APP_KEY"],
        "APP_NAME": validated["APP_NAME"],
        "APP_URL": validated["APP_URL"],
        "PAYPAL_BRAND_NAME": validated["APP_NAME"],
        "APP_DEFINITION_NAME": validated["APP_NAME"],
        "APP_DEFINITION_URL": validated["APP_URL"],
        "APP_DEFINITION_PRODUCT_ID": f"{validated['APP_KEY']}_default_offer",
        "APP_DEFINITION_DESCRIPTION": f"{validated['APP_NAME']} access",
    }
    if tuple(payload.keys()) != REQUIRED_IDENTITY_KEYS:
        raise TemplateContractError("identity payload keys drifted from required contract")
    return payload


def relative(path: Path) -> str:
    return path.relative_to(ROOT_DIR).as_posix()


def write_text(path: Path, content: str) -> None:
    ensure_allowed_workspace_path(path)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
