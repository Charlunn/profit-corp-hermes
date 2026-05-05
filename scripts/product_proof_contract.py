from __future__ import annotations

from pathlib import Path
from typing import Any


IDENTITY_ONLY_PATHS = {
    "src/lib/app-definition.ts",
}
PRIMARY_SURFACE_EXCLUDED_PATHS = {
    "src/app/page.tsx",
}
PRIMARY_SURFACE_EXCLUDED_PREFIXES = (
    "src/app/demo/",
    "src/app/demo",
)
SUPPORTING_LOGIC_PREFIXES = (
    "src/lib/",
    "src/app/api/",
    "supabase/",
)
PRODUCT_SOURCE_PREFIXES = (
    "src/app/",
    "src/components/",
    "src/lib/",
)

FAILURE_REASON_MESSAGES = {
    "missing_primary_workflow_surface": "no result-oriented primary workflow surface was changed",
    "missing_supporting_logic": "no supporting logic directly tied to the primary workflow was changed",
    "identity_only_changes": "workspace changes only touched identity/bootstrap files",
    "demo_only_proof": "/demo changes cannot count as primary product proof",
    "template_residue_on_primary_surfaces": "template/example residue is still present on primary product surfaces",
}


def normalize_repo_paths(paths: list[str]) -> list[str]:
    normalized: list[str] = []
    for path in paths:
        text = str(path).strip().replace("\\", "/")
        if text:
            normalized.append(text)
    return sorted(dict.fromkeys(normalized))


def is_identity_only_path(path: str) -> bool:
    return path in IDENTITY_ONLY_PATHS


def is_demo_path(path: str) -> bool:
    return path == "src/app/demo/page.tsx" or path.startswith(PRIMARY_SURFACE_EXCLUDED_PREFIXES)


def is_primary_workflow_surface_path(path: str) -> bool:
    if not path.startswith("src/app/"):
        return False
    if "/api/" in path or path.startswith("src/app/api/"):
        return False
    if path.endswith("/layout.tsx") or path == "src/app/layout.tsx":
        return False
    if not path.endswith((".tsx", ".ts", ".jsx", ".js", ".mdx")):
        return False
    if path in PRIMARY_SURFACE_EXCLUDED_PATHS or is_demo_path(path):
        return False
    return True


def is_supporting_logic_path(path: str) -> bool:
    if is_identity_only_path(path) or is_demo_path(path):
        return False
    return any(path.startswith(prefix) for prefix in SUPPORTING_LOGIC_PREFIXES)


def classify_template_residue(
    workspace: Path | None,
    marker_patterns: list[str] | tuple[str, ...],
) -> tuple[list[str], list[str]]:
    if workspace is None or not workspace.exists():
        return [], []

    primary_hits: list[str] = []
    secondary_hits: list[str] = []
    for prefix in PRODUCT_SOURCE_PREFIXES:
        root = workspace / prefix
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            if path.suffix.lower() not in {".ts", ".tsx", ".js", ".jsx", ".md", ".mdx", ".json"}:
                continue
            relative = path.relative_to(workspace).as_posix()
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            if not any(marker in text for marker in marker_patterns):
                continue
            if is_primary_workflow_surface_path(relative):
                primary_hits.append(relative)
            else:
                secondary_hits.append(relative)
    return sorted(dict.fromkeys(primary_hits)), sorted(dict.fromkeys(secondary_hits))


def build_product_proof_summary(
    *,
    touched_paths: list[str],
    workspace: Path | None = None,
    marker_patterns: list[str] | tuple[str, ...] = (),
) -> dict[str, Any]:
    normalized_paths = normalize_repo_paths(touched_paths)
    identity_only_paths = [path for path in normalized_paths if is_identity_only_path(path)]
    demo_paths = [path for path in normalized_paths if is_demo_path(path)]
    primary_surfaces = [path for path in normalized_paths if is_primary_workflow_surface_path(path)]
    supporting_logic_paths = [path for path in normalized_paths if is_supporting_logic_path(path)]
    primary_residue_paths, secondary_residue_paths = classify_template_residue(workspace, marker_patterns)

    failure_reasons: list[str] = []
    if normalized_paths and len(normalized_paths) == len(identity_only_paths):
        failure_reasons.append("identity_only_changes")
    non_identity_paths = [path for path in normalized_paths if path not in identity_only_paths]
    if non_identity_paths and all(is_demo_path(path) for path in non_identity_paths):
        failure_reasons.append("demo_only_proof")
    if not primary_surfaces:
        failure_reasons.append("missing_primary_workflow_surface")
    if not supporting_logic_paths:
        failure_reasons.append("missing_supporting_logic")
    if primary_residue_paths:
        failure_reasons.append("template_residue_on_primary_surfaces")

    excluded_proof_paths = sorted(dict.fromkeys(identity_only_paths + demo_paths))
    excluded_proof_reasons: list[str] = []
    if identity_only_paths:
        excluded_proof_reasons.append("identity/bootstrap-only files do not count as product proof")
    if demo_paths:
        excluded_proof_reasons.append("/demo surfaces never count as privileged product proof")

    blocker_messages = [FAILURE_REASON_MESSAGES[reason] for reason in failure_reasons if reason in FAILURE_REASON_MESSAGES]
    warning_messages = []
    if secondary_residue_paths:
        warning_messages.append(
            "template/example residue remains on secondary surfaces: " + ", ".join(secondary_residue_paths)
        )

    proof_paths = sorted(dict.fromkeys(primary_surfaces + supporting_logic_paths))
    return {
        "proof_verdict": "pass" if not failure_reasons else "fail",
        "template_only": bool(failure_reasons),
        "touched_paths": normalized_paths,
        "product_proof_paths": proof_paths,
        "primary_workflow_surfaces": primary_surfaces,
        "supporting_logic_paths": supporting_logic_paths,
        "excluded_proof_paths": excluded_proof_paths,
        "excluded_proof_reasons": excluded_proof_reasons,
        "template_residue_blockers": primary_residue_paths,
        "template_residue_warnings": secondary_residue_paths,
        "failure_reasons": failure_reasons,
        "issues": blocker_messages,
        "template_only_issues": blocker_messages,
        "warning_issues": warning_messages,
    }
