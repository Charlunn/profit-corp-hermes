#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.product_proof_contract import classify_template_residue
from scripts.template_contract_common import DEFAULT_REGISTRY_PATH, TemplateContractError, load_registry, require_asset, relative


DEFAULT_ASSET_ID = "standalone-saas-template"
DEFAULT_CONTRACT_PATH = ROOT_DIR / "docs" / "platform" / "standalone-saas-template-contract.md"
DEFAULT_REPORT_PATH = ROOT_DIR / "assets" / "shared" / "templates" / "latest-template-conformance-report.md"
REQUIRED_CONTRACT_SECTIONS = (
    "operational source of truth",
    "Protected Platform Layer",
    "Safe Extension Layer",
    "## 5. Identity injection contract",
    "## 7. Conformance gate expectations",
)
REQUIRED_WORKSPACE_ARTIFACTS = (
    ".hermes/project-metadata.json",
    ".hermes/shared-backend-guardrails.json",
    ".hermes/PROJECT_BRIEF_ENTRYPOINT.md",
)
PROTECTED_PATHS = (
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
)
PROTECTED_MANIFEST_PATHS = (
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
)
VERIFIED_PATHS = (
    ".hermes/project-metadata.json",
    ".hermes/shared-backend-guardrails.json",
    ".hermes/PROJECT_BRIEF_ENTRYPOINT.md",
    "src/lib/auth.ts",
    "src/lib/supabase-browser.ts",
    "src/lib/supabase-server.ts",
    "src/lib/paypal.ts",
    "src/lib/entitlement.ts",
    "src/lib/db-guards.ts",
    "src/app/api/auth/session/route.ts",
    "src/app/api/paypal/checkout/route.ts",
    "src/app/api/paypal/capture/route.ts",
    "src/lib/app-definition.ts",
    "supabase/migrations/20260423112500_create_shared_public_tables.sql",
)
REQUIRED_IDENTITY_KEYS = ("APP_KEY", "APP_NAME", "APP_URL")
ALLOWED_SHARED_TABLES = {"users", "orders", "payments", "subscriptions"}
MUTATION_METHODS = ("insert", "update", "upsert", "delete")
CLIENT_SCAN_DIRS = ("src/app", "src/components")
TEMPLATE_MARKERS = (
    "Standalone SaaS Template",
    "template starter",
    "starter template",
    "generic starter",
)
REQUIRED_PRODUCT_REQUIREMENT_KEYS = (
    "pain_point",
    "monetization",
    "required_languages",
    "ui_artifact_contract",
)
TEMPLATE_SCAN_DIRS = ("src/app", "src/components")
PRODUCT_SOURCE_DIRS = ("src/app", "src/components", "src/lib")
LANGUAGE_EVIDENCE_FILES = (".hermes/PROJECT_BRIEF_ENTRYPOINT.md",)
LANGUAGE_CODE_PATTERN = re.compile(r"(?<![a-z0-9])(en|zh)(?![a-z0-9])")
LANGUAGE_EVIDENCE_SUFFIXES = (".ts", ".tsx", ".js", ".jsx", ".json", ".md")


class TemplateConformanceError(Exception):
    pass


class BlockingViolationError(TemplateConformanceError):
    def __init__(self, violations: list[str], *, fingerprint_checks: list[dict[str, str]] | None = None):
        super().__init__("blocking template conformance violations")
        self.violations = violations
        self.fingerprint_checks = fingerprint_checks or []


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check a generated workspace against the Hermes template conformance contract.")
    parser.add_argument("--workspace-path", required=True, help="Path to the generated workspace to validate.")
    parser.add_argument("--contract-path", default=str(DEFAULT_CONTRACT_PATH), help="Path to the Hermes canonical contract.")
    parser.add_argument("--registry-path", default=str(DEFAULT_REGISTRY_PATH), help="Path to the template registry JSON.")
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT_PATH), help="Path to write the conformance report.")
    parser.add_argument("--asset-id", default=DEFAULT_ASSET_ID, help="Template asset identifier.")
    parser.add_argument("--dry-run", action="store_true", help="Render the report to stdout without writing files.")
    return parser.parse_args()


def load_text(path: Path, label: str) -> str:
    if not path.exists():
        raise TemplateConformanceError(f"{label} not found: {path}")
    content = path.read_text(encoding="utf-8").strip()
    if not content:
        raise TemplateConformanceError(f"{label} is empty: {path}")
    return content


def load_json(path: Path, label: str) -> dict[str, Any]:
    raw = load_text(path, label)
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise TemplateConformanceError(f"invalid JSON in {label}: {path}") from exc
    if not isinstance(payload, dict):
        raise TemplateConformanceError(f"{label} must be a JSON object: {path}")
    return payload


def require_contract_file(path: Path) -> None:
    load_text(path, "template contract")


def require_contract_sections(contract_text: str) -> None:
    missing = [section for section in REQUIRED_CONTRACT_SECTIONS if section not in contract_text]
    if missing:
        raise TemplateConformanceError(f"template contract missing required sections: {', '.join(missing)}")


def parse_env(env_text: str) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in env_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip()
    return values


def require_workspace_identity(env_text: str, metadata: dict[str, Any]) -> None:
    env_values = parse_env(env_text)
    violations: list[str] = []
    key_map = {
        "APP_KEY": "app_key",
        "APP_NAME": "app_name",
        "APP_URL": "app_url",
    }
    for env_key in REQUIRED_IDENTITY_KEYS:
        if f"{env_key}=" not in env_text:
            violations.append(f"missing identity line: {env_key}=")
            continue
        value = env_values.get(env_key, "")
        if not value.strip():
            violations.append(f"{env_key} missing or blank in workspace .env")
            continue
        expected = str(metadata.get(key_map[env_key], "")).strip()
        if not expected:
            violations.append(f"metadata missing required identity value for {env_key}")
            continue
        if value != expected:
            violations.append(f"{env_key} mismatch between workspace .env and .hermes/project-metadata.json")
    if violations:
        raise BlockingViolationError(violations)


def build_protected_manifest(asset: dict[str, Any], metadata: dict[str, Any]) -> list[dict[str, str]]:
    asset_id = str(asset.get("asset_id", "")).strip() or DEFAULT_ASSET_ID
    template_source_path = str(metadata.get("template_source_path", "")).strip() or str(asset.get("source", {}).get("repo_path", "")).strip()
    return [
        {
            "path": manifest_path,
            "asset_id": asset_id,
            "template_source_path": template_source_path,
            "hash_algorithm": "sha256",
        }
        for manifest_path in PROTECTED_MANIFEST_PATHS
    ]


def require_workspace_artifacts(workspace_root: Path) -> None:
    violations: list[str] = []
    for relative_path in REQUIRED_WORKSPACE_ARTIFACTS:
        if not (workspace_root / relative_path).exists():
            violations.append(f"missing required workspace artifact: {relative_path}")
    if violations:
        raise BlockingViolationError(violations)


def require_shared_backend_metadata(guardrails: dict[str, Any], metadata: dict[str, Any]) -> None:
    violations: list[str] = []
    allowed_shared_tables = {str(table).strip().lower() for table in guardrails.get("allowed_shared_tables", []) if str(table).strip()}
    blocked_tables = {str(table).strip().lower() for table in guardrails.get("client_write_blocked_tables", []) if str(table).strip()}
    if str(guardrails.get("backend_model", "")).strip() != "shared-supabase":
        violations.append("shared backend model must be shared-supabase in .hermes/shared-backend-guardrails.json")
    if str(guardrails.get("app_key", "")).strip() != str(metadata.get("app_key", "")).strip():
        violations.append("shared backend guardrails app_key mismatch with .hermes/project-metadata.json")
    if str(guardrails.get("canonical_contract_path", "")).strip() != str(metadata.get("canonical_contract_path", "")).strip():
        violations.append("shared backend guardrails canonical contract mismatch with .hermes/project-metadata.json")
    if allowed_shared_tables != ALLOWED_SHARED_TABLES:
        violations.append("shared backend guardrails allowed_shared_tables drifted from the canonical shared table boundary")
    if blocked_tables != ALLOWED_SHARED_TABLES:
        violations.append("shared backend guardrails client_write_blocked_tables drifted from the canonical shared table boundary")
    if guardrails.get("allow_independent_backend") is not False:
        violations.append("shared backend guardrails must forbid independent backend bootstrap by default")
    if violations:
        raise BlockingViolationError(violations)


def require_protected_paths_present(workspace_root: Path, protected_manifest: list[dict[str, str]]) -> None:
    violations: list[str] = []
    for relative_path in PROTECTED_PATHS:
        if not (workspace_root / relative_path).exists():
            violations.append(f"missing protected path: {relative_path}")
    for entry in protected_manifest:
        manifest_path = entry["path"]
        if not (workspace_root / manifest_path).exists() and manifest_path not in PROTECTED_PATHS:
            violations.append(f"missing protected manifest path: {manifest_path}")
    if violations:
        raise BlockingViolationError(violations)


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()


def require_protected_fingerprints(workspace_root: Path, template_root: Path, protected_manifest: list[dict[str, str]]) -> list[dict[str, str]]:
    violations: list[str] = []
    fingerprint_checks: list[dict[str, str]] = []
    for entry in protected_manifest:
        relative_path = entry["path"]
        workspace_file = workspace_root / relative_path
        template_file = template_root / relative_path
        if not workspace_file.exists():
            violations.append(f"missing protected manifest path in workspace for sha256 check: {relative_path}")
            continue
        if not template_file.exists():
            violations.append(f"missing protected manifest path in template source for sha256 check: {relative_path}")
            continue
        workspace_sha = sha256_file(workspace_file)
        template_sha = sha256_file(template_file)
        status = "MATCH"
        if workspace_sha != template_sha:
            status = "DRIFT"
            violations.append(
                f"fingerprint drift for {relative_path}: workspace sha256 {workspace_sha} != template sha256 {template_sha}"
            )
        fingerprint_checks.append(
            {
                "path": relative_path,
                "workspace_sha256": workspace_sha,
                "template_sha256": template_sha,
                "status": status,
            }
        )
    if violations:
        raise BlockingViolationError(violations, fingerprint_checks=fingerprint_checks)
    return fingerprint_checks


def require_product_requirements(metadata: dict[str, Any]) -> list[str]:
    product_requirements = metadata.get("product_requirements")
    if not isinstance(product_requirements, dict):
        raise BlockingViolationError([".hermes/project-metadata.json missing product_requirements object"])
    violations: list[str] = []
    for key in REQUIRED_PRODUCT_REQUIREMENT_KEYS:
        value = product_requirements.get(key)
        if key == "required_languages":
            normalized = [str(item).strip().lower() for item in list(value or []) if str(item).strip()]
            if not normalized:
                violations.append(f".hermes/project-metadata.json missing product_requirements.{key}")
                continue
            if "en" not in normalized or "zh" not in normalized:
                violations.append(".hermes/project-metadata.json product_requirements.required_languages must include en and zh")
            continue
        if isinstance(value, list):
            if not [str(item).strip() for item in value if str(item).strip()]:
                violations.append(f".hermes/project-metadata.json missing product_requirements.{key}")
            continue
        if not str(value or "").strip():
            violations.append(f".hermes/project-metadata.json missing product_requirements.{key}")
    if violations:
        raise BlockingViolationError(violations)
    return [str(item).strip().lower() for item in list(product_requirements.get("required_languages", [])) if str(item).strip()]


def require_shared_invariants(workspace_root: Path, required_languages: list[str]) -> None:
    violations: list[str] = []
    app_definition_path = workspace_root / "src" / "lib" / "app-definition.ts"
    if not app_definition_path.exists():
        violations.append("missing shared invariant path: src/lib/app-definition.ts")

    product_pages = [
        path
        for path in sorted((workspace_root / "src" / "app").rglob("page.tsx"))
        if path.is_file() and "api" not in path.relative_to(workspace_root / "src" / "app").parts
    ] if (workspace_root / "src" / "app").exists() else []
    if not product_pages:
        violations.append("workspace missing product-facing page implementation under src/app/*")

    primary_marker_paths, _secondary_marker_paths = classify_template_residue(workspace_root, TEMPLATE_MARKERS)
    if primary_marker_paths:
        violations.append(
            "template marker residue detected on primary product surfaces: " + ", ".join(primary_marker_paths)
        )

    language_hits = {code: False for code in required_languages}
    for source_dir in PRODUCT_SOURCE_DIRS:
        root = workspace_root / source_dir
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in LANGUAGE_EVIDENCE_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8").lower()
            matches = set(LANGUAGE_CODE_PATTERN.findall(text))
            for code in required_languages:
                if code in matches:
                    language_hits[code] = True
    for relative_path in LANGUAGE_EVIDENCE_FILES:
        evidence_path = workspace_root / relative_path
        if not evidence_path.exists():
            continue
        text = evidence_path.read_text(encoding="utf-8").lower()
        matches = set(LANGUAGE_CODE_PATTERN.findall(text))
        for code in required_languages:
            if code in matches:
                language_hits[code] = True
    missing_languages = [code for code, found in language_hits.items() if not found]
    if missing_languages:
        violations.append(
            "workspace missing multilingual evidence for required languages: " + ", ".join(missing_languages)
        )

    if violations:
        raise BlockingViolationError(violations)


def iter_migration_files(workspace_root: Path) -> list[Path]:
    migrations_dir = workspace_root / "supabase" / "migrations"
    if not migrations_dir.exists():
        return []
    return sorted(path for path in migrations_dir.glob("*.sql") if path.is_file())


def require_table_boundaries(workspace_root: Path, app_key: str) -> None:
    violations: list[str] = []
    prefix = f"{app_key}_"
    for migration_path in iter_migration_files(workspace_root):
        lines = migration_path.read_text(encoding="utf-8").splitlines()
        for line_number, line in enumerate(lines, start=1):
            lowered = line.lower()
            if "create table" not in lowered or "public." not in lowered:
                continue
            table_name = lowered.split("public.", 1)[1].split("(", 1)[0].strip().rstrip(";")
            if table_name in ALLOWED_SHARED_TABLES:
                continue
            if table_name.startswith(prefix):
                continue
            reason = "must use APP_KEY_ prefix"
            if not table_name.startswith(prefix) and "_" not in table_name:
                reason = "breaks shared table boundary and must use APP_KEY_ prefix"
            violations.append(
                f"{migration_path.relative_to(workspace_root).as_posix()}:{line_number} create table public.{table_name} {reason}"
            )
    if violations:
        raise BlockingViolationError(violations)


def require_no_forbidden_client_writes(workspace_root: Path) -> None:
    violations: list[str] = []
    for scan_dir in CLIENT_SCAN_DIRS:
        root = workspace_root / scan_dir
        if not root.exists():
            continue
        for path in sorted(root.rglob("*.ts*")):
            text = path.read_text(encoding="utf-8")
            if '"use client"' not in text and "'use client'" not in text:
                continue
            lowered = text.lower()
            for table in sorted(ALLOWED_SHARED_TABLES):
                if f'.from("{table}")' not in lowered and f".from('{table}')" not in lowered:
                    continue
                for method in MUTATION_METHODS:
                    if f".{method}(" in lowered:
                        violations.append(
                            f"{path.relative_to(workspace_root).as_posix()} use client file must not mutate shared table {table} via .{method}(...)"
                        )
                        break
    if violations:
        raise BlockingViolationError(violations)


def build_report_lines(
    *,
    status: str,
    violations: list[str],
    warnings: list[str],
    verified_paths: list[str],
    fingerprint_checks: list[dict[str, str]],
    workspace_path: Path,
    contract_path: Path,
    registry_path: Path,
) -> list[str]:
    lines = [
        "# Template Conformance Report",
        f"- Workspace: `{workspace_path.as_posix()}`",
        f"- Contract: `{safe_display_path(contract_path)}`",
        f"- Registry: `{safe_display_path(registry_path)}`",
        "",
        "## Status",
        f"- {status}",
        "",
        "## Blocking Violations",
    ]
    if violations:
        lines.extend(f"- {violation}" for violation in violations)
    else:
        lines.append("None.")
    lines.extend(["", "## Proof Warnings"])
    if warnings:
        lines.extend(f"- {warning}" for warning in warnings)
    else:
        lines.append("None.")
    lines.extend(["", "## Verified Paths"])
    lines.extend(f"- {path}" for path in verified_paths)
    lines.extend(["", "## Fingerprint Checks"])
    for check in fingerprint_checks:
        lines.append(
            "- {path} — {status} — workspace sha256={workspace_sha256} — template sha256={template_sha256}".format(**check)
        )
    if not fingerprint_checks:
        lines.append("None.")
    return lines


def safe_display_path(path: Path) -> str:
    try:
        return relative(path)
    except ValueError:
        return path.as_posix()


def write_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")


def main() -> int:
    args = parse_args()
    try:
        workspace_path = Path(args.workspace_path)
        contract_path = Path(args.contract_path)
        registry_path = Path(args.registry_path)
        report_path = Path(args.report_path)

        registry = load_registry(registry_path)
        asset = require_asset(registry, args.asset_id)
        require_contract_file(contract_path)
        contract_text = load_text(contract_path, "template contract")
        require_contract_sections(contract_text)

        require_workspace_artifacts(workspace_path)
        metadata = load_json(workspace_path / ".hermes" / "project-metadata.json", "workspace metadata")
        guardrails = load_json(workspace_path / ".hermes" / "shared-backend-guardrails.json", "shared backend guardrails")
        env_text = load_text(workspace_path / ".env", "workspace .env")
        require_workspace_identity(env_text, metadata)
        require_shared_backend_metadata(guardrails, metadata)
        required_languages = require_product_requirements(metadata)

        protected_manifest = build_protected_manifest(asset, metadata)
        require_protected_paths_present(workspace_path, protected_manifest)

        template_source_raw = str(metadata.get("template_source_path", "")).strip() or str(asset.get("source", {}).get("repo_path", "")).strip()
        if not template_source_raw:
            raise TemplateConformanceError("template source path missing from metadata and registry")
        template_root = Path(template_source_raw)
        if not template_root.exists():
            raise TemplateConformanceError(f"template source path not found: {template_root}")

        require_shared_invariants(workspace_path, required_languages)
        _, secondary_marker_paths = classify_template_residue(workspace_path, TEMPLATE_MARKERS)
        warnings = (
            ["template marker residue remains on secondary surfaces: " + ", ".join(secondary_marker_paths)]
            if secondary_marker_paths
            else []
        )
        require_table_boundaries(workspace_path, str(metadata.get("app_key", "")).strip())
        require_no_forbidden_client_writes(workspace_path)
        fingerprint_checks = require_protected_fingerprints(workspace_path, template_root, protected_manifest)
        report = "\n".join(
            build_report_lines(
                status="PASS",
                violations=[],
                warnings=warnings,
                verified_paths=list(VERIFIED_PATHS),
                fingerprint_checks=fingerprint_checks,
                workspace_path=workspace_path,
                contract_path=contract_path,
                registry_path=registry_path,
            )
        )

        if args.dry_run:
            print(report)
            return 0

        write_report(report_path, report)
        print(f"Wrote {report_path.as_posix()}")
        return 0
    except BlockingViolationError as exc:
        workspace_path = Path(args.workspace_path)
        contract_path = Path(args.contract_path)
        registry_path = Path(args.registry_path)
        report = "\n".join(
            build_report_lines(
                status="FAIL",
                violations=exc.violations,
                warnings=[],
                verified_paths=list(VERIFIED_PATHS),
                fingerprint_checks=exc.fingerprint_checks,
                workspace_path=workspace_path,
                contract_path=contract_path,
                registry_path=registry_path,
            )
        )
        if args.dry_run:
            print(report)
        else:
            write_report(Path(args.report_path), report)
            print(f"Wrote {Path(args.report_path).as_posix()}")
        return 1
    except (TemplateConformanceError, TemplateContractError) as exc:
        print(f"template conformance error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
