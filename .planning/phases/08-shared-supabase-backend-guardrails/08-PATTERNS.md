# Phase 8: Shared Supabase Backend Guardrails - Pattern Map

**Mapped:** 2026-04-26
**Files analyzed:** 6
**Analogs found:** 6 / 6

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|-------------------|------|-----------|----------------|---------------|
| `scripts/shared_supabase_guardrails_common.py` | utility | file-I/O, validation | `scripts/template_contract_common.py` | exact-role |
| `scripts/check_shared_supabase_guardrails.py` | script | file-I/O, validation, reporting | `scripts/check_template_conformance.py` | exact-role |
| `scripts/instantiate_template_project.py` | script | file-I/O, config injection | `scripts/instantiate_template_project.py` | modify-existing |
| `tests/test_shared_supabase_guardrails.py` | test | file-I/O, validation | `tests/test_check_template_conformance.py` | exact-role |
| `tests/test_shared_supabase_guardrails_common.py` | test | validation | `tests/test_instantiate_template_project.py` (`TemplateContractCommonTests`) | role-match |
| `docs/platform/standalone-saas-template-contract.md` or guardrail contract companion | config/doc | request-response contract for validators | `docs/platform/standalone-saas-template-contract.md` + `tests/test_template_contract.py` | exact-governance-doc |

## Pattern Assignments

### `scripts/shared_supabase_guardrails_common.py` (utility, file-I/O + validation)

**Analog:** `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/template_contract_common.py`

**Why this is the best match**
- Central shared helper module for multiple scripts.
- Defines repo-root constants, custom exception, path guards, JSON loading, validation helpers.
- Phase 8 guardrails will likely need the same shape for shared Supabase path lists, allowed locations, SQL/text parsing helpers, and standardized errors.

**Imports + root/bootstrap pattern** (`template_contract_common.py` lines 0-15):
```python
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
```
Copy this pattern for constants like `PROTECTED_SUPABASE_PATHS`, `ALLOWED_SQL_ROOTS`, `SHARED_TABLES`, and regexes for allowed table prefixes.

**Custom error + JSON load pattern** (`template_contract_common.py` lines 28-41):
```python
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
```
Phase 8 helper should mirror this with `SharedSupabaseGuardrailError`, plus loaders like `load_sql_text`, `load_metadata_json`, or `load_manifest_json`.

**Path guard pattern** (`template_contract_common.py` lines 51-60):
```python
def ensure_allowed_workspace_path(path: Path) -> None:
    resolved = path.resolve()
    for directory in ALLOWED_WORKSPACE_ROOTS:
        try:
            resolved.relative_to(directory.resolve())
            return
        except ValueError:
            continue
    raise TemplateContractError(f"refusing to write outside allowed workspace roots: {path}")
```
If Phase 8 writes any report or manifest, keep this exact allowlist-first structure.

**Validation payload pattern** (`template_contract_common.py` lines 62-95):
```python
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
```
For Supabase guardrails, reuse this normalized-input then accumulate-contract-values style for schema checks such as allowed shared table names, APP_KEY table prefix rules, or protected migration invariants.

**Reusable helper to copy** (`template_contract_common.py` lines 98-104):
```python
def relative(path: Path) -> str:
    return path.relative_to(ROOT_DIR).as_posix()


def write_text(path: Path, content: str) -> None:
    ensure_allowed_workspace_path(path)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
```
Keep the `rstrip() + "\n"` convention for any Phase 8 generated report.

---

### `scripts/check_shared_supabase_guardrails.py` (script, file-I/O + validation + reporting)

**Analog:** `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/check_template_conformance.py`

**Why this is the best match**
- Same operational role: CLI validator script that loads contract/config/workspace inputs, performs blocking checks, and emits a Markdown report.
- Phase 8 guardrail checks will likely validate protected shared Supabase assets, APP_KEY boundaries, and drift against canonical files; this script already has the full pattern.

**Imports + sys.path bootstrap pattern** (`check_template_conformance.py` lines 0-13):
```python
#!/usr/bin/env python3
import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any


ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.template_contract_common import DEFAULT_REGISTRY_PATH, TemplateContractError, load_registry, require_asset, relative
```
Use the same top-of-file structure. If the new script depends on a new helper module, import it from `scripts.shared_supabase_guardrails_common` in one grouped import.

**CLI contract pattern** (`check_template_conformance.py` lines 65-73):
```python
def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Check a generated workspace against the Hermes template conformance contract.")
    parser.add_argument("--workspace-path", required=True, help="Path to the generated workspace to validate.")
    parser.add_argument("--contract-path", default=str(DEFAULT_CONTRACT_PATH), help="Path to the Hermes canonical contract.")
    parser.add_argument("--registry-path", default=str(DEFAULT_REGISTRY_PATH), help="Path to the template registry JSON.")
    parser.add_argument("--report-path", default=str(DEFAULT_REPORT_PATH), help="Path to write the conformance report.")
    parser.add_argument("--asset-id", default=DEFAULT_ASSET_ID, help="Template asset identifier.")
    parser.add_argument("--dry-run", action="store_true", help="Render the report to stdout without writing files.")
    return parser.parse_args()
```
Phase 8 should follow this exact argparse style: explicit required flags, repo-default paths, `--dry-run`, and no interactive prompts.

**Text/JSON loading pattern** (`check_template_conformance.py` lines 76-93):
```python
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
```
This is the clearest reusable pattern for guardrail inputs like metadata, manifest, or structured reports.

**Blocking error aggregation pattern** (`check_template_conformance.py` lines 54-63, 117-140):
```python
class BlockingViolationError(TemplateConformanceError):
    def __init__(self, violations: list[str], *, fingerprint_checks: list[dict[str, str]] | None = None):
        super().__init__("blocking template conformance violations")
        self.violations = violations
        self.fingerprint_checks = fingerprint_checks or []
```
```python
def require_workspace_identity(env_text: str, metadata: dict[str, Any]) -> None:
    env_values = parse_env(env_text)
    violations: list[str] = []
    ...
    if violations:
        raise BlockingViolationError(violations)
```
Phase 8 should preserve this distinction:
- configuration/input errors -> base exception
- policy violations discovered during checking -> blocking violation exception containing a list

**Hash/fingerprint drift pattern** (`check_template_conformance.py` lines 179-218):
```python
def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(65536), b""):
            digest.update(chunk)
    return digest.hexdigest()
```
```python
def require_protected_fingerprints(workspace_root: Path, template_root: Path, protected_manifest: list[dict[str, str]]) -> list[dict[str, str]]:
    violations: list[str] = []
    fingerprint_checks: list[dict[str, str]] = []
    ...
    if workspace_sha != template_sha:
        status = "DRIFT"
        violations.append(
            f"fingerprint drift for {relative_path}: workspace sha256 {workspace_sha} != template sha256 {template_sha}"
        )
```
This is the strongest analog if Phase 8 must verify shared Supabase migrations, shared RLS SQL, or `src/lib/db-guards.ts` against canonical protected files.

**Report rendering pattern** (`check_template_conformance.py` lines 237-283):
```python
def build_report_lines(... ) -> list[str]:
    lines = [
        "# Template Conformance Report",
        f"- Workspace: `{workspace_path.as_posix()}`",
        ...
        "## Status",
        f"- {status}",
        ...
        "## Blocking Violations",
    ]
    ...
    return lines
```
```python
def write_report(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content.rstrip() + "\n", encoding="utf-8")
```
Phase 8 report output should stay Markdown-first, sectioned, deterministic, and newline-normalized.

**Main flow pattern** (`check_template_conformance.py` lines 286-359):
```python
def main() -> int:
    args = parse_args()
    try:
        ...
        if args.dry_run:
            print(report)
            return 0

        write_report(report_path, report)
        print(f"Wrote {report_path.as_posix()}")
        return 0
    except BlockingViolationError as exc:
        ...
        return 1
    except (TemplateConformanceError, TemplateContractError) as exc:
        print(f"template conformance error: {exc}", file=sys.stderr)
        return 1
```
Phase 8 script should keep this exact return-code contract: pass=0, blocking violations=1 with report, input/config errors=1 with stderr message.

---

### `scripts/instantiate_template_project.py` (existing script modification, file-I/O + config injection)

**Analog:** `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/instantiate_template_project.py`

**Why this matters for Phase 8**
- If guardrails require extra metadata or manifest generation during workspace bootstrap, this is the place existing repo conventions already use.
- Phase 8 should not invent a separate bootstrap pattern when this script already writes `.env`, `app-definition.ts`, and `.hermes` handoff artifacts.

**Argument parsing and default constants** (`instantiate_template_project.py` lines 23-46):
```python
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
```
This is the best precedent for adding future shared-backend placeholders or guardrail metadata constants.

**Safe file mutation with explicit failure messages** (`instantiate_template_project.py` lines 73-103):
```python
def update_env_file(env_path: Path, identity: dict[str, str]) -> None:
    if not env_path.exists():
        raise TemplateContractError(f"template .env file not found: {env_path}")
    ...
    env_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
```
```python
def update_app_definition(app_definition_path: Path, identity: dict[str, str]) -> None:
    if not app_definition_path.exists():
        raise TemplateContractError(f"app definition file not found: {app_definition_path}")
    ...
    for old, new in replacements.items():
        if old not in content:
            raise TemplateContractError(f"expected app-definition pattern missing: {old}")
        content = content.replace(old, new)
```
If Phase 8 injects a new `.hermes/shared-supabase-guardrails.json` or materializes a manifest, keep the same explicit existence checks and exact-pattern failure strings.

**Metadata/handoff artifact pattern** (`instantiate_template_project.py` lines 106-142):
```python
def build_metadata(... ) -> dict[str, str]:
    ...
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
```python
def write_hermes_handoff(workspace: Path, metadata: dict[str, str]) -> None:
    hermes_dir = workspace / ".hermes"
    hermes_dir.mkdir(parents=True, exist_ok=True)
    ...
```
If Phase 8 needs a persisted guardrail manifest, write it under `.hermes/` with this same metadata-first structure.

**Top-level operation flow** (`instantiate_template_project.py` lines 158-190):
```python
def instantiate_workspace(... ) -> None:
    workspace_root.mkdir(parents=True, exist_ok=True)
    shutil.copytree(...)
    update_env_file(...)
    update_app_definition(...)
    write_hermes_handoff(...)
```
New bootstrap-time guardrail generation should be one more step in this linear, explicit sequence.

---

### `tests/test_shared_supabase_guardrails.py` (test, file-I/O + validation)

**Analog:** `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_check_template_conformance.py`

**Why this is the best match**
- Same testing shape: CLI script integration tests with subprocess, workspace fixture creation, dry-run assertion, pass/fail guardrail behavior, and report inspection.
- If Phase 8 validator checks shared Supabase boundaries, these tests should mirror this file almost exactly.

**CLI execution helper pattern** (`test_check_template_conformance.py` lines 28-42):
```python
def run_conformance(self, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT_PATH), *args],
        cwd=ROOT_DIR,
        capture_output=True,
        text=True,
    )
```
Copy this verbatim, only rename the helper to match the new script.

**Stable section-order assertion pattern** (`test_check_template_conformance.py` lines 14-19, 44-59):
```python
EXPECTED_SECTION_ORDER = [
    "## Status",
    "## Blocking Violations",
    "## Verified Paths",
    "## Fingerprint Checks",
]
```
```python
def assert_section_order(self, output: str) -> None:
    positions: list[int] = []
    for section in EXPECTED_SECTION_ORDER:
        self.assertIn(section, output)
        positions.append(output.index(section))
    self.assertEqual(positions, sorted(positions), "section order drifted")
```
Phase 8 report tests should use the same deterministic section-order discipline.

**Fixture creation pattern** (`test_check_template_conformance.py` lines 60-90):
```python
def create_workspace_fixture(self) -> tuple[Path, Path, Path]:
    workspace_root = ROOT_DIR / "assets" / "workspaces" / "projects"
    workspace_root.mkdir(parents=True, exist_ok=True)
    workspace_name = f"lead-capture-{next(tempfile._get_candidate_names())}"
    self.addCleanupPath(workspace_root / workspace_name)
    ...
    result = self.run_instantiate(...)
    self.assertEqual(result.returncode, 0, msg=result.stderr)
    workspace = workspace_root / workspace_name
    self.assertTrue(workspace.exists(), "workspace was not created")
    return registry_path.parent, registry_path, workspace
```
For shared Supabase tests, prefer generating a real workspace fixture via the instantiate script rather than hand-building many files.

**Pass-case assertion pattern** (`test_check_template_conformance.py` lines 113-129):
```python
result = self.run_conformance(*self.base_args(registry_path, workspace))
self.assertEqual(result.returncode, 0, msg=result.stderr)
output = result.stdout
self.assertIn("# Template Conformance Report", output)
self.assertIn("PASS", self.extract_section(output, "## Status"))
self.assertEqual(self.extract_section(output, "## Blocking Violations"), "None.")
self.assert_section_order(output)
```
Use this for healthy shared-backend workspaces.

**Targeted failure mutation pattern** (`test_check_template_conformance.py` lines 131-168):
```python
env_text = env_path.read_text(encoding="utf-8").replace("APP_KEY=lead_capture", "APP_KEY=")
env_path.write_text(env_text, encoding="utf-8")
```
```python
protected_path.unlink()
```
```python
protected_path.write_text(
    protected_path.read_text(encoding="utf-8") + "\n// drift\n",
    encoding="utf-8",
)
```
This is the right style for Phase 8 negative tests: mutate one concrete invariant at a time, then assert the exact blocking phrase.

**Likely Phase 8 test cases to structure after this analog**
- healthy workspace passes shared Supabase guardrails
- missing protected Supabase migration fails
- drift in `src/lib/db-guards.ts` fails fingerprint check
- product table missing `APP_KEY_` prefix fails boundary check
- unexpected write to shared public table DDL fails blocking violation

---

### `tests/test_shared_supabase_guardrails_common.py` (test, validation)

**Analog:** `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_instantiate_template_project.py` lines 29-76 (`TemplateContractCommonTests`)

**Why this is the best match**
- That class tests helper-level validation without shelling out.
- Phase 8 common helpers should get direct unit tests in the same style.

**Helper-level import pattern** (`test_instantiate_template_project.py` lines 9-20):
```python
ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR))

from scripts.template_contract_common import (
    GENERATED_WORKSPACES_DIR,
    TemplateContractError,
    build_identity_payload,
    ensure_allowed_workspace_path,
    load_registry,
    require_asset,
    validate_identity,
)
```
A new helper test file should import the new common module exactly this way.

**Validation failure pattern** (`test_instantiate_template_project.py` lines 29-39):
```python
with self.assertRaises(TemplateContractError):
    validate_identity("", "Lead Capture", "https://lead.example.com")
```
For Phase 8, use `assertRaises(SharedSupabaseGuardrailError)` for helpers like `validate_table_name`, `require_allowed_shared_table`, or `parse_sql_manifest`.

**Direct expected-payload assertion pattern** (`test_instantiate_template_project.py` lines 40-64):
```python
payload = build_identity_payload("lead_capture", "Lead Capture", "https://lead.example.com")
self.assertEqual(payload, {...})
```
Use the same style for deterministic helper outputs such as manifest entries or parsed guardrail summaries.

**Safety guard pattern** (`test_instantiate_template_project.py` lines 66-76):
```python
allowed_path = GENERATED_WORKSPACES_DIR / "guard-check"
ensure_allowed_workspace_path(allowed_path)

with self.assertRaises(TemplateContractError):
    ensure_allowed_workspace_path(ROOT_DIR / "tmp" / "guard-check")
```
If the new helper writes reports/manifests, include equivalent allowed-directory coverage.

---

### `docs/platform/standalone-saas-template-contract.md` or a Phase 8 guardrail contract companion (config/doc, contract)

**Analog:**
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/docs/platform/standalone-saas-template-contract.md`
- validated by `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_template_contract.py`

**Why this is the best match**
- Existing conventions treat platform rules as a canonical Markdown contract with numbered headings and explicit verification commands.
- If Phase 8 introduces stronger shared Supabase backend guardrails, they should be added here or in a sibling contract using the same structure.

**Contract structure pattern** (`standalone-saas-template-contract.md` lines 5-20, 37-75, 119-162):
- numbered sections
- protected-layer inventory
- behavior rules
- required runtime paths
- conformance expectations
- verification checklist

**Heading-order enforcement analog** (`test_template_contract.py` lines 5-33):
```python
EXPECTED_HEADINGS = [
    "## 1. Authority and source hierarchy",
    "## 2. Registered template summary",
    "## 3. Protected platform layer",
    "## 4. Safe extension layer",
    "## 5. Identity injection contract",
    "## 6. Required runtime and artifact paths",
    "## 7. Conformance gate expectations",
    "## 8. Verification checklist",
]
```
```python
def assert_heading_order(self, content: str) -> None:
    positions: list[int] = []
    for heading in EXPECTED_HEADINGS:
        self.assertIn(heading, content)
        positions.append(content.index(heading))
    self.assertEqual(positions, sorted(positions), "contract heading order drifted")
```
If Phase 8 adds a new contract section for shared Supabase backend rules, update tests in this same heading-order style.

---

### `tests/test_template_registry.py` and registry-linked metadata updates (test/config)

**Analog:** `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_template_registry.py`

**Why this matters for Phase 8**
- If shared Supabase guardrails require new registry metadata, this file is the established place to assert exact JSON shape.
- The tests are strict and prefer exact field assertions over broad schema checks.

**Exact-value assertion pattern** (`test_template_registry.py` lines 18-45):
```python
payload = self.load_registry()
self.assertEqual(payload["asset_id"], "standalone-saas-template")
self.assertEqual(payload["governance_scope"], "single-template-first")
...
self.assertEqual(payload["canonical_refs"]["upstream"], EXPECTED_UPSTREAM)
raw = REGISTRY_PATH.read_text(encoding="utf-8")
self.assertNotIn("catalog", raw.lower())
self.assertNotIn("templates[]", raw)
```
If Phase 8 adds a `guardrails` block or new canonical refs, follow this exact explicit-assertion pattern.

## Shared Patterns

### 1. CLI script shape
**Source:** `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/check_template_conformance.py` lines 65-73, 286-359
- `parse_args()` returns `argparse.Namespace`
- `main()` returns process code int
- `--dry-run` prints report to stdout
- user-facing failures print to `stderr`
- file-writing mode prints `Wrote ...`

**Apply to:** all new Phase 8 guardrail scripts

### 2. Shared helper module shape
**Source:** `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/template_contract_common.py` lines 28-41, 51-60, 98-104
- one custom exception class
- pure helper functions
- central constants at top of module
- path allowlist enforcement before writes
- small focused loaders/validators

**Apply to:** `shared_supabase_guardrails_common.py`

### 3. File-I/O safety and newline normalization
**Source:**
- `template_contract_common.py` lines 102-104
- `check_template_conformance.py` lines 281-283
- `instantiate_template_project.py` lines 82-83, 126-142

**Pattern:**
- `path.write_text(content.rstrip() + "\n", encoding="utf-8")`
- create parent directories explicitly before writes
- fail fast when expected source files are missing

**Apply to:** report output, manifest output, metadata sidecars

### 4. Blocking-violation reporting model
**Source:** `check_template_conformance.py` lines 54-63, 166-218, 336-356
- gather multiple violations into a list
- attach structured detail lists like fingerprint checks
- still emit a full Markdown report on failure
- return exit code `1` for blocking policy failures

**Apply to:** shared Supabase boundary validators

### 5. Fingerprint/drift verification
**Source:** `check_template_conformance.py` lines 179-218
- use SHA-256 chunked reads
- compare workspace protected files to canonical template files
- include both hashes in report
- classify as `MATCH` or `DRIFT`

**Apply to:** protected Supabase migrations, `src/lib/db-guards.ts`, maybe shared auth/payment/server helpers if guardrails expand

### 6. Deterministic Markdown report formatting
**Source:** `check_template_conformance.py` lines 237-271 and `tests/test_check_template_conformance.py` lines 14-19, 44-59
- fixed heading order
- predictable bullet formatting
- explicit `None.` when section empty
- tests assert section order

**Apply to:** any Phase 8 report artifact

### 7. Integration test fixture strategy
**Source:** `tests/test_check_template_conformance.py` lines 60-90 and `tests/test_instantiate_template_project.py` lines 92-101
- create temp registry fixture
- point registry source to real template source
- create real workspace via CLI
- cleanup temp directories with `addCleanup`

**Apply to:** validation tests for new guardrail scripts

### 8. Contract/governance documentation style
**Source:** `docs/platform/standalone-saas-template-contract.md` lines 37-75, 142-162 and `tests/test_template_contract.py` lines 42-60
- spell out protected paths explicitly
- spell out safe extension boundaries explicitly
- include runnable verification commands
- test exact phrases and headings

**Apply to:** any new shared Supabase guardrail contract text

## Likely Phase 8 Structure Recommendations

### Recommended new script split
1. `scripts/shared_supabase_guardrails_common.py`
   - constants for protected shared backend paths
   - table/prefix validation helpers
   - SQL/text/JSON load helpers
   - custom exception class

2. `scripts/check_shared_supabase_guardrails.py`
   - CLI entrypoint
   - workspace + contract + registry loading
   - protected path existence checks
   - shared-table boundary checks
   - APP_KEY-prefixed business-table checks
   - fingerprint drift checks for protected backend files
   - Markdown report writer

3. Optional bootstrap integration in `scripts/instantiate_template_project.py`
   - only if guardrail metadata/manifest must be generated at workspace creation time
   - keep as one extra explicit function call in `instantiate_workspace(...)`

### Recommended new test split
1. `tests/test_shared_supabase_guardrails_common.py`
   - direct unit tests for parsing/validation helpers
   - no subprocess unless necessary

2. `tests/test_shared_supabase_guardrails.py`
   - subprocess CLI tests
   - healthy dry-run pass case
   - mutation-based negative cases
   - fixed report-section assertions

### Recommended likely report sections
Follow `check_template_conformance.py` unless Phase 8 needs more detail:
- `## Status`
- `## Blocking Violations`
- `## Verified Paths`
- `## Fingerprint Checks`
- optionally `## Table Boundary Checks` if there are many SQL-specific assertions

### Recommended likely guardrail checks
Based on existing contract language in `standalone-saas-template-contract.md` lines 58-75 and 142-153:
- protected shared backend files still exist
- shared public tables remain limited to `users`, `orders`, `payments`, `subscriptions`
- product-specific tables stay inside `APP_KEY_` namespace
- `src/lib/db-guards.ts` remains present and optionally fingerprint-locked
- protected shared migration file has no drift unless platform explicitly updates canonical source

## No Analog Found

| File | Role | Data Flow | Reason |
|------|------|-----------|--------|
| None | - | - | Phase 8 guardrail work fits existing template-conformance and helper/test patterns closely. |

## Metadata

**Analog search scope:**
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/assets/shared/templates`
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/docs/platform`

**Files scanned:** 10 primary artifacts plus supporting analogs in `scripts/governance_common.py`, `scripts/enforce_governed_action.py`, `tests/test_generate_operating_visibility.py`, and `tests/test_generate_decision_package.py`

**Pattern extraction date:** 2026-04-26
