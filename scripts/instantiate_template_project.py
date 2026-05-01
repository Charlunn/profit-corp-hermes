#!/usr/bin/env python3
import argparse
import json
import shutil
import sys
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.template_contract_common import (
    DEFAULT_REGISTRY_PATH,
    GENERATED_WORKSPACES_DIR,
    LOCAL_PROJECTS_ROOT,
    TemplateContractError,
    build_identity_payload,
    ensure_allowed_workspace_path,
    load_registry,
    relative,
    require_asset,
)


DEFAULT_ASSET_ID = "standalone-saas-template"
DEFAULT_CONTRACT_PATH = ROOT_DIR / "docs" / "platform" / "standalone-saas-template-contract.md"
DEFAULT_TEMPLATE_SOURCE_PATH = Path("C:/Users/42236/Desktop/standalone-saas-template")
PLACEHOLDER_ENV_KEYS = {
    "NEXT_PUBLIC_SUPABASE_URL": "__REQUIRED__",
    "NEXT_PUBLIC_SUPABASE_ANON_KEY": "__REQUIRED__",
    "SUPABASE_SERVICE_ROLE_KEY": "__REQUIRED__",
    "NEXT_PUBLIC_PAYPAL_CLIENT_ID": "__REQUIRED__",
    "PAYPAL_CLIENT_SECRET": "__REQUIRED__",
}
SHARED_BACKEND_MODEL = "shared-supabase"
SHARED_TABLES = ["users", "orders", "payments", "subscriptions"]
PROTECTED_PATHS = [
    "src/lib/auth.ts",
    "src/lib/supabase-browser.ts",
    "src/lib/supabase-server.ts",
    "src/lib/paypal.ts",
    "src/lib/entitlement.ts",
    "src/lib/db-guards.ts",
    "src/app/api/auth/session/route.ts",
    "src/app/api/paypal/checkout/route.ts",
    "src/app/api/paypal/capture/route.ts",
    "supabase/migrations/20260423112500_create_shared_public_tables.sql",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Instantiate a Hermes-managed project workspace from the registered template.")
    parser.add_argument("--asset-id", default=DEFAULT_ASSET_ID, help="Template asset identifier.")
    parser.add_argument("--registry-path", default=str(DEFAULT_REGISTRY_PATH), help="Path to the template registry JSON.")
    parser.add_argument("--workspace-name", required=True, help="Workspace folder name under the workspace root.")
    parser.add_argument("--workspace-root", default=str(LOCAL_PROJECTS_ROOT), help="Allowed Hermes workspace root.")
    parser.add_argument("--app-key", required=True, help="APP_KEY for the generated project.")
    parser.add_argument("--app-name", required=True, help="APP_NAME for the generated project.")
    parser.add_argument("--app-url", required=True, help="APP_URL for the generated project.")
    parser.add_argument("--template-source-path", default="", help="Override the registered template source path.")
    parser.add_argument("--dry-run", action="store_true", help="Print the intended actions without writing files.")
    return parser.parse_args()


def load_asset(args: argparse.Namespace) -> dict:
    registry = load_registry(Path(args.registry_path))
    return require_asset(registry, args.asset_id)


def resolve_template_source(asset: dict, override: str) -> Path:
    if override.strip():
        source = Path(override.strip())
    else:
        source = Path(str(asset.get("source", {}).get("repo_path", "")).strip())
    if not source.exists():
        raise TemplateContractError(f"template source path not found: {source}")
    return source


def resolve_workspace(args: argparse.Namespace) -> tuple[Path, Path]:
    workspace_root = Path(args.workspace_root)
    workspace = workspace_root / args.workspace_name
    ensure_allowed_workspace_path(workspace)
    if workspace.exists():
        raise TemplateContractError(f"workspace already exists: {workspace}")
    return workspace_root, workspace


def update_env_file(env_path: Path, identity: dict[str, str]) -> None:
    env_path.parent.mkdir(parents=True, exist_ok=True)

    values = dict(PLACEHOLDER_ENV_KEYS)
    values["PAYPAL_ENVIRONMENT"] = "sandbox"
    for key in ("APP_KEY", "APP_NAME", "APP_URL", "PAYPAL_BRAND_NAME"):
        values[key] = identity[key]

    lines = [f"{key}={value}" for key, value in values.items()]
    env_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def write_vercel_config(workspace: Path) -> None:
    vercel_config_path = workspace / "vercel.json"
    payload = {
        "$schema": "https://openapi.vercel.sh/vercel.json",
        "framework": "nextjs",
        "installCommand": "pnpm install",
        "buildCommand": "pnpm run build",
        "ignoreCommand": "python -c \"from pathlib import Path; import sys; sys.exit(1 if any((Path('.') / name).exists() for name in ['.hermes', '.vercel', 'node_modules']) else 0)\"",
    }
    vercel_config_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_vercelignore(workspace: Path) -> None:
    vercelignore_path = workspace / ".vercelignore"
    content = "\n".join([
        ".hermes",
        ".vercel",
        "node_modules",
        ".next",
        "coverage",
        "dist",
        "build",
    ])
    vercelignore_path.write_text(content + "\n", encoding="utf-8")


def update_app_definition(app_definition_path: Path, identity: dict[str, str]) -> None:
    if not app_definition_path.exists():
        raise TemplateContractError(f"app definition file not found: {app_definition_path}")

    content = app_definition_path.read_text(encoding="utf-8")
    replacements = {
        'name: config.appName,': f'name: "{identity["APP_DEFINITION_NAME"]}",',
        'url: config.appUrl,': f'url: "{identity["APP_DEFINITION_URL"]}",',
        'eyebrow: "Standalone SaaS Template",': f'eyebrow: "{identity["APP_NAME"]}",',
        'headline: config.appName,': f'headline: "{identity["APP_NAME"]}",',
        'productId: `${config.appKey}_default_offer`,': f'productId: "{identity["APP_DEFINITION_PRODUCT_ID"]}",',
        'description: `${config.appName} access`': f'description: "{identity["APP_DEFINITION_DESCRIPTION"]}"',
    }
    for old, new in replacements.items():
        if old not in content:
            raise TemplateContractError(f"expected app-definition pattern missing: {old}")
        content = content.replace(old, new)
    app_definition_path.write_text(content, encoding="utf-8")


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


def build_shared_backend_guardrails(metadata: dict[str, str]) -> dict[str, object]:
    return {
        "backend_model": SHARED_BACKEND_MODEL,
        "app_key": metadata["app_key"],
        "canonical_contract_path": metadata["canonical_contract_path"],
        "allowed_shared_tables": SHARED_TABLES,
        "protected_paths": PROTECTED_PATHS,
        "client_write_blocked_tables": SHARED_TABLES,
        "allow_independent_backend": False,
    }


def write_hermes_handoff(workspace: Path, metadata: dict[str, str]) -> None:
    hermes_dir = workspace / ".hermes"
    hermes_dir.mkdir(parents=True, exist_ok=True)

    metadata_path = hermes_dir / "project-metadata.json"
    metadata_path.write_text(json.dumps(metadata, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    guardrails = build_shared_backend_guardrails(metadata)
    guardrails_path = hermes_dir / "shared-backend-guardrails.json"
    guardrails_path.write_text(json.dumps(guardrails, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    brief_path = hermes_dir / "PROJECT_BRIEF_ENTRYPOINT.md"
    brief = "\n".join(
        [
            "# Hermes Project Brief Entrypoint",
            "",
            f"- Workspace: `{metadata['workspace_name']}`",
            f"- App: `{metadata['app_name']}` (`{metadata['app_key']}`)",
            f"- App URL: `{metadata['app_url']}`",
            f"- Metadata: `.hermes/project-metadata.json`",
            f"- Shared backend guardrails: `.hermes/shared-backend-guardrails.json`",
            f"- Canonical contract: `{metadata['canonical_contract_path']}`",
            f"- Template source: `{metadata['template_source_path']}`",
        ]
    )
    brief_path.write_text(brief.rstrip() + "\n", encoding="utf-8")


def refresh_workspace_managed_files(workspace: Path, identity: dict[str, str], metadata: dict[str, str]) -> None:
    update_env_file(workspace / ".env", identity)
    write_vercel_config(workspace)
    write_vercelignore(workspace)
    update_app_definition(workspace / "src" / "lib" / "app-definition.ts", identity)
    write_hermes_handoff(workspace, metadata)


def render_dry_run(workspace: Path, metadata: dict[str, str]) -> str:
    lines = [
        "DRY RUN - instantiate template project",
        f"workspace_root: {workspace.parent.as_posix()}",
        f"workspace: {workspace.as_posix()}",
        f"asset_id: {metadata['asset_id']}",
        f"app_key: {metadata['app_key']}",
        f"app_name: {metadata['app_name']}",
        f"app_url: {metadata['app_url']}",
        f"backend_model: {SHARED_BACKEND_MODEL}",
        "guardrails_path: .hermes/shared-backend-guardrails.json",
    ]
    return "\n".join(lines)


def instantiate_workspace(template_source: Path, workspace_root: Path, workspace: Path, identity: dict[str, str], metadata: dict[str, str]) -> None:
    workspace_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(
        template_source,
        workspace,
        dirs_exist_ok=False,
        ignore=shutil.ignore_patterns("node_modules", ".next", ".git", ".vercel"),
    )
    refresh_workspace_managed_files(workspace, identity, metadata)


def main() -> int:
    args = parse_args()
    try:
        asset = load_asset(args)
        template_source = resolve_template_source(asset, args.template_source_path)
        workspace_root, workspace = resolve_workspace(args)
        identity = build_identity_payload(args.app_key, args.app_name, args.app_url)
        metadata = build_metadata(asset, args.workspace_name, identity, template_source)

        if args.dry_run:
            print(render_dry_run(workspace, metadata))
            return 0

        instantiate_workspace(template_source, workspace_root, workspace, identity, metadata)
        print(f"workspace created: {workspace.as_posix()}")
        print(f"metadata: {relative(workspace / '.hermes' / 'project-metadata.json')}")
        return 0
    except TemplateContractError as exc:
        print(f"template instantiate error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
