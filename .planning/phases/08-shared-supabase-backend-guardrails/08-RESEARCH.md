# Phase 8: Shared Supabase Backend Guardrails - Research

**Researched:** 2026-04-26
**Domain:** Hermes template conformance and shared Supabase boundary enforcement
**Confidence:** HIGH

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| BACK-01 | Hermes can enforce that new SaaS projects target a single shared Supabase backend model rather than creating a separate backend by default | Reuse the existing registry+contract+conformance gate pattern and add explicit checks over `.env`, shared client/server Supabase helpers, and forbidden alternate backend bootstraps. |
| BACK-02 | Hermes can enforce that product-specific business tables use the `APP_KEY_` prefix | Extend conformance with SQL/content scans anchored to `APP_KEY`, `getBusinessTableName`, and migration rules. |
| BACK-03 | Hermes can detect and block creation of unprefixed product business tables in generated SaaS projects | Add blocking migration analysis for `create table` statements outside the shared allowlist and without the current app prefix. |
| BACK-04 | Hermes can preserve the template’s shared-table boundary so only `users`, `orders`, `payments`, and `subscriptions` are treated as global platform tables | Promote the four-table boundary from contract text into executable checks over migrations and code write targets. |
| BACK-05 | Hermes can require product implementations to reuse the shared auth, payment, and entitlement flows instead of replacing them by default | Extend protected-manifest and path-presence checks around auth/payment/entitlement helpers and server routes; optionally add import/reference checks for product wrappers. |
| BACK-06 | Hermes can validate that product code does not directly write shared payment or entitlement state from client-side code | Add static client-code scans for writes to `orders`, `payments`, `subscriptions`, `users` and direct browser-side Supabase mutation patterns. |
</phase_requirements>

## Summary

Phase 7 already created the right enforcement skeleton: a single template registry record, a canonical platform contract, a safe workspace instantiator, and a blocking conformance CLI with a stable report shape. The missing work for Phase 8 is not a new system; it is a deeper rule pack inside the existing conformance flow. [VERIFIED: codebase read `scripts/check_template_conformance.py`] [VERIFIED: codebase read `docs/platform/standalone-saas-template-contract.md`]

The shared Supabase model is currently defined in three places: the Hermes contract, the upstream template docs, and the template source itself. The strongest executable signals today are `src/lib/supabase-browser.ts`, `src/lib/supabase-server.ts`, `src/lib/db-guards.ts`, `src/lib/paypal.ts`, `src/lib/entitlement.ts`, and `supabase/migrations/20260423112500_create_shared_public_tables.sql`. Phase 8 should formalize those into deterministic checks over migrations, protected files, and client/server write paths rather than relying on documentation alone. [VERIFIED: codebase read `C:/Users/42236/Desktop/standalone-saas-template/src/lib/supabase-browser.ts`] [VERIFIED: codebase read `C:/Users/42236/Desktop/standalone-saas-template/src/lib/supabase-server.ts`] [VERIFIED: codebase read `C:/Users/42236/Desktop/standalone-saas-template/src/lib/db-guards.ts`] [VERIFIED: codebase read `C:/Users/42236/Desktop/standalone-saas-template/src/lib/paypal.ts`] [VERIFIED: codebase read `C:/Users/42236/Desktop/standalone-saas-template/supabase/migrations/20260423112500_create_shared_public_tables.sql`]

**Primary recommendation:** Implement Phase 8 as an extension of `scripts/check_template_conformance.py` that adds static Supabase guardrail analyzers and corresponding unittest coverage, while keeping the existing blocking report format and temp-workspace integration-test style. [VERIFIED: codebase read `tests/test_check_template_conformance.py`]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Shared-backend contract enforcement | API / Backend | Frontend Server (SSR) | Hermes enforcement runs in Python CLIs and validates generated workspaces before delivery, not at runtime in the browser. [VERIFIED: codebase read `scripts/check_template_conformance.py`] |
| Shared Supabase client/server configuration checks | Frontend Server (SSR) | Browser / Client | The template splits browser anon-key access from server service-role access via separate helpers. [VERIFIED: codebase read `src/lib/supabase-browser.ts`] [VERIFIED: codebase read `src/lib/supabase-server.ts`] |
| Shared table boundary preservation | Database / Storage | API / Backend | The authoritative shared-table set is encoded in the SQL migration and consumed by server-side payment/entitlement logic. [VERIFIED: codebase read `supabase/migrations/20260423112500_create_shared_public_tables.sql`] [VERIFIED: codebase read `src/lib/paypal.ts`] |
| APP_KEY-prefixed business-table enforcement | Database / Storage | API / Backend | Table naming is a schema concern, while guard helpers and validators enforce it from code. [VERIFIED: codebase read `src/lib/db-guards.ts`] |
| Blocking direct client-side writes to payment/entitlement state | Browser / Client | API / Backend | The violation originates in client code, but the allowed path must route writes through server APIs and helpers. [VERIFIED: codebase read `src/components/billing-template.tsx`] [VERIFIED: codebase read `src/app/api/paypal/checkout/route.ts`] [VERIFIED: codebase read `src/app/api/paypal/capture/route.ts`] |
| Shared auth/payment/entitlement reuse enforcement | API / Backend | Frontend Server (SSR) | Protected helpers and routes define the approved platform primitives to reuse. [VERIFIED: codebase read `docs/platform/standalone-saas-template-contract.md`] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| Python | 3.11.15 | Hermes validation/instantiation CLIs and unittests | Existing Phase 7 tooling is Python stdlib-first, so Phase 8 should extend the same scripts and tests. [VERIFIED: local env `python --version`] [VERIFIED: codebase read `scripts/instantiate_template_project.py`] |
| unittest | stdlib | Contract and conformance test framework | Existing test suite already locks registry, contract, instantiation, and conformance behavior with `unittest`. [VERIFIED: codebase read `tests/test_template_registry.py`] [VERIFIED: codebase read `tests/test_check_template_conformance.py`] |
| pathlib + regex/string scanning | stdlib | Static workspace analysis for migrations and source files | Current scripts already use `Path`, JSON parsing, and deterministic content checks; guardrails fit this style well. [VERIFIED: codebase read `scripts/template_contract_common.py`] [VERIFIED: codebase read `scripts/check_template_conformance.py`] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| @supabase/supabase-js | ^2.49.1 | Template runtime client for browser/server data access | Use only as a scan target in Phase 8; Hermes itself should not add a new runtime dependency just to validate source text. [VERIFIED: codebase read `assets/shared/templates/standalone-saas-template.json`] |
| Next.js | 15.3.0 | Template app/router and API route surface | Use for path conventions when detecting protected routes and client components. [VERIFIED: codebase read `assets/shared/templates/standalone-saas-template.json`] |
| React | 19.1.0 | Template client components such as billing UI | Use when scanning `"use client"` files for forbidden writes. [VERIFIED: codebase read `assets/shared/templates/standalone-saas-template.json`] [VERIFIED: codebase read `src/components/billing-template.tsx`] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Extend `scripts/check_template_conformance.py` | Create a brand-new Phase 8 validator | Worse fit: duplicates report format, CLI behavior, and test fixtures already established in Phase 7. [VERIFIED: codebase read `scripts/check_template_conformance.py`] |
| Deterministic static scans | Full SQL parser / TypeScript AST tooling | Could be more exact, but adds new dependencies and planning scope. Current repo pattern favors small stdlib-first validators. [ASSUMED] |
| Blocking conformance report | Ad hoc stdout warnings | Worse fit: later phases already depend on the blocking-report pattern with named sections. [VERIFIED: codebase read `tests/test_check_template_conformance.py`] |

**Installation:**
```bash
# No new package is required for the recommended first implementation.
# Reuse existing Python stdlib tooling and repo test infrastructure.
```

## Architecture Patterns

### System Architecture Diagram

```text
Generated workspace
  |
  +--> .hermes/project-metadata.json ------------------+
  |                                                    |
  +--> .env -------------------------------------------|--> check_template_conformance.py
  |                                                    |      |
  +--> src/lib/supabase-browser.ts --------------------|      +--> identity checks
  +--> src/lib/supabase-server.ts ---------------------|      +--> protected path checks
  +--> src/lib/db-guards.ts ---------------------------|      +--> protected fingerprint checks
  +--> src/lib/paypal.ts ------------------------------|      +--> shared invariant checks
  +--> src/lib/entitlement.ts -------------------------|      +--> NEW: migration naming checks
  +--> src/app/api/paypal/*.ts ------------------------|      +--> NEW: shared-table boundary checks
  +--> client components / product pages --------------|      +--> NEW: client-side write checks
  +--> supabase/migrations/*.sql ----------------------+      |
                                                         --> markdown report
                                                               - Status
                                                               - Blocking Violations
                                                               - Verified Paths
                                                               - Fingerprint Checks
```

### Recommended Project Structure
```text
scripts/
├── template_contract_common.py        # shared constants/helpers for Phase 7/8 validators
├── instantiate_template_project.py    # workspace generation
└── check_template_conformance.py      # extend here with backend guardrail analyzers

tests/
├── test_template_registry.py
├── test_template_contract.py
├── test_instantiate_template_project.py
└── test_check_template_conformance.py # add Phase 8 pass/fail fixtures here
```

### Pattern 1: Registry + contract + blocking validator
**What:** Phase 7 established a three-part authority chain: registry JSON, contract markdown, then a Python conformance gate that blocks drift. [VERIFIED: codebase read `assets/shared/templates/standalone-saas-template.json`] [VERIFIED: codebase read `docs/platform/standalone-saas-template-contract.md`] [VERIFIED: codebase read `scripts/check_template_conformance.py`]
**When to use:** Any rule that must stop handoff or deployment when violated.
**Example:**
```python
# Source: scripts/check_template_conformance.py
registry = load_registry(registry_path)
asset = require_asset(registry, args.asset_id)
require_contract_file(contract_path)
require_contract_sections(contract_text)
```

### Pattern 2: Protected-manifest fingerprinting for platform primitives
**What:** Protected files are explicitly enumerated and compared by `sha256` against the registered template source. [VERIFIED: codebase read `scripts/check_template_conformance.py`]
**When to use:** Auth, payment, entitlement, server Supabase helpers, and migration files that product work should not silently fork.
**Example:**
```python
# Source: scripts/check_template_conformance.py
PROTECTED_MANIFEST_PATHS = (
    "src/app/api/auth/session/route.ts",
    "src/app/api/paypal/checkout/route.ts",
    "src/app/api/paypal/capture/route.ts",
    "supabase/migrations/20260423112500_create_shared_public_tables.sql",
    "src/lib/db-guards.ts",
)
```

### Pattern 3: Temp-workspace integration tests
**What:** Tests instantiate a fresh workspace from the real template, then mutate a single file to prove a blocking failure. [VERIFIED: codebase read `tests/test_check_template_conformance.py`]
**When to use:** New Phase 8 rules for SQL naming, boundary violations, and client-write violations.
**Example:**
```python
# Source: tests/test_check_template_conformance.py
result = self.run_instantiate(...)
self.assertEqual(result.returncode, 0, msg=result.stderr)
protected_path.write_text(protected_path.read_text(encoding="utf-8") + "\n// drift\n", encoding="utf-8")
result = self.run_conformance(*self.base_args(registry_path, workspace))
self.assertEqual(result.returncode, 1)
```

### Pattern 4: Server-owned shared payment/entitlement writes
**What:** The browser calls API routes; server helpers write `orders`, `payments`, and `subscriptions`. [VERIFIED: codebase read `src/components/billing-template.tsx`] [VERIFIED: codebase read `src/app/api/paypal/checkout/route.ts`] [VERIFIED: codebase read `src/app/api/paypal/capture/route.ts`] [VERIFIED: codebase read `src/lib/paypal.ts`]
**When to use:** BACK-05 and BACK-06 enforcement design.
**Example:**
```typescript
// Source: C:/Users/42236/Desktop/standalone-saas-template/src/components/billing-template.tsx
const response = await fetch("/api/paypal/checkout", { method: "POST" });
...
const response = await fetch("/api/paypal/capture", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ orderId })
});
```

### Anti-Patterns to Avoid
- **New standalone validator script for the same workspace contract:** It would fork report shape and fixture setup instead of extending the existing gate. [VERIFIED: codebase read `scripts/check_template_conformance.py`]
- **Relying only on docs text for backend rules:** BACK-02 through BACK-06 require executable checks, not more prose. [VERIFIED: codebase read `.planning/REQUIREMENTS.md`]
- **Trying to prove all semantics with file hashes alone:** Fingerprints catch platform drift, but they do not detect new unprefixed SQL tables or forbidden client writes. [VERIFIED: codebase read `scripts/check_template_conformance.py`]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Product table naming | Per-project manual review | Static validator over migration SQL + `APP_KEY` | Humans will miss drift across generated workspaces. [VERIFIED: codebase read `docs/platform/standalone-saas-template-contract.md`] |
| Shared layer integrity | Loose checklist | Existing protected-manifest fingerprinting | Already implemented and tested. [VERIFIED: codebase read `scripts/check_template_conformance.py`] |
| Payment/entitlement mutation policy | Browser-side exceptions list in product code | Server-route/server-helper ownership model already used by template | Shared state is already written centrally in `src/lib/paypal.ts`. [VERIFIED: codebase read `src/lib/paypal.ts`] |
| Workspace validation output | Custom ad hoc text per rule | Existing stable markdown report sections | Downstream readers can parse one consistent artifact. [VERIFIED: codebase read `tests/test_check_template_conformance.py`] |

**Key insight:** Phase 8 should extend the governance mechanism that already exists instead of inventing a second policy engine. [VERIFIED: codebase read `.planning/phases/07-template-assetization-and-platform-contract/07-03-SUMMARY.md`]

## Common Pitfalls

### Pitfall 1: Hashing only the protected files
**What goes wrong:** A workspace can keep all protected files intact yet still add a bad migration with unprefixed business tables. [VERIFIED: codebase read `scripts/check_template_conformance.py`]
**Why it happens:** Current conformance checks presence, identity, shared invariants, and fingerprint drift, but not general SQL migration content. [VERIFIED: codebase read `scripts/check_template_conformance.py`]
**How to avoid:** Add a separate migration scanner over all workspace `supabase/migrations/*.sql` files.
**Warning signs:** Conformance PASS while new migrations contain `create table public.leads` or similar. [ASSUMED]

### Pitfall 2: Treating all unprefixed tables as forbidden
**What goes wrong:** The validator may incorrectly fail the canonical shared migration. [VERIFIED: codebase read `supabase/migrations/20260423112500_create_shared_public_tables.sql`]
**Why it happens:** Four global shared tables are explicitly allowed: `users`, `orders`, `payments`, `subscriptions`. [VERIFIED: codebase read `docs/platform/standalone-saas-template-contract.md`]
**How to avoid:** Implement an allowlist for exactly those four names and only for shared/global semantics.
**Warning signs:** The first generated workspace fails Phase 8 without any product migrations.

### Pitfall 3: Scanning only page files for forbidden writes
**What goes wrong:** A client component under `src/components` could directly mutate shared tables and evade detection. [VERIFIED: codebase read `src/components/billing-template.tsx`] [CITED: C:/Users/42236/Desktop/standalone-saas-template/BUILDING_RULES.md]
**Why it happens:** The rule applies to product pages and client components, not only routes. [CITED: C:/Users/42236/Desktop/standalone-saas-template/BUILDING_RULES.md]
**How to avoid:** Scan all `"use client"` `.ts`/`.tsx` files in `src/app` and `src/components`.
**Warning signs:** A client file imports Supabase browser client and calls `.from("payments").update(...)`.

### Pitfall 4: Blocking read-only access by mistake
**What goes wrong:** Validators may reject legitimate reads of `subscriptions` for entitlement-aware UI. [VERIFIED: codebase read `src/lib/entitlement.ts`] [CITED: C:/Users/42236/Desktop/standalone-saas-template/ARCHITECTURE.md]
**Why it happens:** BACK-06 is specifically about direct client-side writes, not reads. [VERIFIED: codebase read `.planning/REQUIREMENTS.md`]
**How to avoid:** Only block mutation patterns such as `.insert(`, `.update(`, `.upsert(`, `.delete(` when paired with shared tables from client files.
**Warning signs:** Validator flags simple `.select()` or display-only entitlement checks.

### Pitfall 5: Forgetting `src/lib/entitlement.ts` and `src/lib/supabase-server.ts` in protected coverage
**What goes wrong:** Product code could fork core entitlement or server Supabase behavior without tripping the current manifest. [VERIFIED: codebase read `docs/platform/standalone-saas-template-contract.md`] [VERIFIED: codebase read `scripts/check_template_conformance.py`]
**Why it happens:** The current protected manifest covers routes, migration, and `db-guards`, but not every protected helper listed by the contract. [VERIFIED: codebase read `scripts/check_template_conformance.py`]
**How to avoid:** Expand `PROTECTED_MANIFEST_PATHS` to include at least `src/lib/auth.ts`, `src/lib/supabase-browser.ts`, `src/lib/supabase-server.ts`, `src/lib/paypal.ts`, and `src/lib/entitlement.ts`.
**Warning signs:** Contract says a path is protected, but fingerprint report never mentions it.

## Code Examples

Verified patterns from repo and template sources:

### Shared-table allowlist lives in one helper
```typescript
// Source: C:/Users/42236/Desktop/standalone-saas-template/src/lib/db-guards.ts
export function assertSharedWriteAllowed(table: string) {
  const allowed = new Set(["orders", "payments", "subscriptions", "users"]);
  if (!allowed.has(table)) {
    throw new Error(`Direct shared-table write is not allowed for ${table}`);
  }
}
```

### Product table naming helper uses APP_KEY
```typescript
// Source: C:/Users/42236/Desktop/standalone-saas-template/src/lib/db-guards.ts
export function getBusinessTableName(suffix: string) {
  const { appKey } = getAppConfig();
  if (!/^[a-z0-9_]+$/.test(suffix)) {
    throw new Error("Business table suffix must be snake_case lowercase");
  }
  return `${appKey}_${suffix}`;
}
```

### Shared payment/subscription writes are server-owned
```typescript
// Source: C:/Users/42236/Desktop/standalone-saas-template/src/lib/paypal.ts
assertSharedWriteAllowed("orders");
assertSharedWriteAllowed("payments");
assertSharedWriteAllowed("subscriptions");

const { error } = await supabase.from("subscriptions").upsert(
  {
    user_id: userId,
    scope_type: "app",
    scope_id: appKey,
    status: "active"
  },
  { onConflict: "user_id,scope_type,scope_id" }
);
```

### Client code uses server routes instead of direct shared-table writes
```typescript
// Source: C:/Users/42236/Desktop/standalone-saas-template/src/components/billing-template.tsx
const response = await fetch("/api/paypal/checkout", { method: "POST" });
...
const response = await fetch("/api/paypal/capture", {
  method: "POST",
  headers: { "content-type": "application/json" },
  body: JSON.stringify({ orderId })
});
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Contract-only template guardrails | Executable instantiation + blocking conformance gate | Phase 7, 2026-04-26 | Phase 8 can add backend guardrails by extending an existing enforcement point instead of creating one. [VERIFIED: codebase read `.planning/STATE.md`] [VERIFIED: codebase read `.planning/phases/07-template-assetization-and-platform-contract/07-03-SUMMARY.md`] |
| Presence-only policy docs | Presence + fingerprint drift detection for protected paths | Phase 7, 2026-04-26 | Shared platform drift is already detectable; add semantic scans next. [VERIFIED: codebase read `scripts/check_template_conformance.py`] |

**Deprecated/outdated:**
- Manual interpretation of `APP_KEY_` and shared-table rules as planning-only guidance: insufficient for BACK-02 through BACK-06 because requirements now demand executable validation. [VERIFIED: codebase read `.planning/REQUIREMENTS.md`]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Deterministic regex/string scanning is sufficient for the first Phase 8 implementation without adding AST or SQL parser dependencies | Standard Stack / Alternatives Considered | Could under-detect edge-case syntax and require a stronger parser later |
| A2 | Example bad migration names like `public.leads` represent realistic failure cases to test | Common Pitfalls | Test fixtures might need different concrete examples |

## Open Questions (RESOLVED)

1. **Should Phase 8 scan only SQL migrations, or also TypeScript string literals that name business tables?**
   - Resolution: Phase 8 execution should enforce migration SQL first as the blocking source of truth for BACK-02 through BACK-04, and additionally scan client-side/shared-table mutation patterns in TypeScript where those patterns directly affect BACK-06. General non-client TypeScript table-name scans are deferred.
   - Why: This keeps the first implementation deterministic and aligned with the current conformance/test pattern while still covering the highest-risk write paths.

2. **How strict should “reuse shared auth/payment/entitlement flows” be?**
   - Resolution: Treat replacement or drift of protected shared files/routes as blocking, but allow additive wrappers/adapters that continue to call the protected helpers and routes.
   - Why: This matches the contract’s protected-layer model without overblocking legitimate product composition.

3. **Should direct client-side writes to `users` also be blocked under BACK-06?**
   - Resolution: Phase 8 should block direct client-side mutation patterns for `payments` and `subscriptions` as the minimum required scope, and may also cover `orders` and `users` when implemented with low false-positive string-pattern checks, as already reflected in the planning direction.
   - Why: The roadmap requirement is payment/entitlement-focused, but the broader shared-table boundary can be guarded opportunistically where safe.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| Python | Guardrail CLI and tests | ✓ | 3.11.15 | — |
| unittest | Validation tests | ✓ | stdlib | — |
| Node.js | Existing repo/tooling context | ✓ | v22.15.0 | — |
| npm | Existing repo/tooling context | ✓ | 10.9.2 | — |
| Standalone template source at `C:/Users/42236/Desktop/standalone-saas-template` | Real workspace fixture and protected fingerprint source | ✓ | current local checkout | No practical fallback for fingerprint-based tests |

**Missing dependencies with no fallback:**
- None found. [VERIFIED: local env probe and template path listing]

**Missing dependencies with fallback:**
- None found. [VERIFIED: local env probe]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Python `unittest` (stdlib) [VERIFIED: codebase read `tests/test_instantiate_template_project.py`] |
| Config file | none — direct `python -m unittest` invocation [VERIFIED: codebase read `docs/platform/standalone-saas-template-contract.md`] |
| Quick run command | `cd C:/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests/test_check_template_conformance.py` [VERIFIED: codebase pattern; command form may vary by runner] |
| Full suite command | `cd C:/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest discover -s tests -p "test_*template*.py"` [VERIFIED: local run passed] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| BACK-01 | Reject workspace/backend config that drifts from shared Supabase model | integration | `python -m unittest tests/test_check_template_conformance.py` | ✅ |
| BACK-02 | Accept APP_KEY-prefixed product table definitions | integration | `python -m unittest tests/test_check_template_conformance.py` | ✅ |
| BACK-03 | Block unprefixed product business tables | integration | `python -m unittest tests/test_check_template_conformance.py` | ✅ |
| BACK-04 | Block shared global tables outside `users/orders/payments/subscriptions` boundary | integration | `python -m unittest tests/test_check_template_conformance.py` | ✅ |
| BACK-05 | Block replacement/drift of shared auth/payment/entitlement primitives | integration | `python -m unittest tests/test_check_template_conformance.py` | ✅ |
| BACK-06 | Block client-side writes to shared payment/entitlement state | integration | `python -m unittest tests/test_check_template_conformance.py` | ✅ |

### Sampling Rate
- **Per task commit:** `cd C:/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest tests/test_check_template_conformance.py`
- **Per wave merge:** `cd C:/Users/42236/Desktop/dev/profit-corp-hermes && python -m unittest discover -s tests -p "test_*template*.py"`
- **Phase gate:** Full suite green before `/gsd-verify-work`

### Wave 0 Gaps
- [ ] `tests/test_check_template_conformance.py` — add healthy prefixed-table pass fixture for BACK-02
- [ ] `tests/test_check_template_conformance.py` — add unprefixed-table fail fixture for BACK-03
- [ ] `tests/test_check_template_conformance.py` — add forbidden extra-shared-table fail fixture for BACK-04
- [ ] `tests/test_check_template_conformance.py` — add client-side shared-write fail fixture for BACK-06
- [ ] `tests/test_check_template_conformance.py` — add protected helper drift coverage for `src/lib/entitlement.ts` and Supabase helper files if manifest is expanded for BACK-05

## Security Domain

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Reuse shared Supabase auth + `/api/auth/session` contract, block unauthorized drift. [VERIFIED: codebase read `src/app/api/auth/session/route.ts` via contract/test references] |
| V3 Session Management | yes | Browser token exchange through server-owned cookie session; do not introduce second session system. [CITED: C:/Users/42236/Desktop/standalone-saas-template/ARCHITECTURE.md] |
| V4 Access Control | yes | Shared-table writes stay server-owned; RLS enabled in shared migration; service-role access isolated to server helper. [VERIFIED: codebase read `supabase/migrations/20260423112500_create_shared_public_tables.sql`] [VERIFIED: codebase read `src/lib/supabase-server.ts`] |
| V5 Input Validation | yes | Validate `APP_KEY` shape and static table-name patterns before handoff. [VERIFIED: codebase read `scripts/template_contract_common.py`] |
| V6 Cryptography | no | No new cryptography work for Phase 8; rely on existing platform/runtime handling. [ASSUMED] |

### Known Threat Patterns for this stack

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Client-side mutation of shared payment/subscription rows | Tampering | Static conformance scan over `"use client"` files for shared-table mutation patterns; require server route path instead. |
| Silent fork of shared auth/payment helpers | Tampering | Protected-manifest fingerprint drift detection against template source. [VERIFIED: codebase read `scripts/check_template_conformance.py`] |
| Unprefixed business tables leaking product data into global namespace | Tampering | Migration allowlist + `APP_KEY_` prefix enforcement. |
| Separate backend bootstraps bypassing shared Supabase contract | Elevation of Privilege | Validate `.env`/helper paths and fail on alternate backend scaffolds or missing shared Supabase helpers. [ASSUMED] |

## Sources

### Primary (HIGH confidence)
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/REQUIREMENTS.md` - Phase 8 requirements and exact BACK-01..BACK-06 wording
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/ROADMAP.md` - Phase 8 goal and success criteria
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/STATE.md` - current phase context
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/.planning/PROJECT.md` - shared Supabase model context and constraints
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/assets/shared/templates/standalone-saas-template.json` - registered template metadata and supported stack
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/docs/platform/standalone-saas-template-contract.md` - canonical Hermes platform contract
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/template_contract_common.py` - identity validation and workspace guard helpers
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/instantiate_template_project.py` - workspace instantiation workflow
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/scripts/check_template_conformance.py` - existing blocking conformance gate and report structure
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_instantiate_template_project.py` - integration test style for generated workspaces
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_check_template_conformance.py` - existing conformance test pattern and failure cases
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_template_contract.py` - contract-locking coverage
- `C:/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_template_registry.py` - registry-locking coverage
- `C:/Users/42236/Desktop/standalone-saas-template/ARCHITECTURE.md` - upstream template architecture and allowed flows
- `C:/Users/42236/Desktop/standalone-saas-template/BUILDING_RULES.md` - upstream rules for APP_KEY prefix and no client-side shared writes
- `C:/Users/42236/Desktop/standalone-saas-template/src/lib/db-guards.ts` - business table naming helper and shared-table allowlist
- `C:/Users/42236/Desktop/standalone-saas-template/src/lib/paypal.ts` - server-owned shared payment/subscription writes
- `C:/Users/42236/Desktop/standalone-saas-template/src/lib/entitlement.ts` - entitlement read path
- `C:/Users/42236/Desktop/standalone-saas-template/src/lib/supabase-browser.ts` - browser Supabase client
- `C:/Users/42236/Desktop/standalone-saas-template/src/lib/supabase-server.ts` - server Supabase client
- `C:/Users/42236/Desktop/standalone-saas-template/src/components/billing-template.tsx` - client uses API routes instead of direct writes
- `C:/Users/42236/Desktop/standalone-saas-template/src/app/api/paypal/checkout/route.ts` - approved checkout server route
- `C:/Users/42236/Desktop/standalone-saas-template/src/app/api/paypal/capture/route.ts` - approved capture server route
- `C:/Users/42236/Desktop/standalone-saas-template/supabase/migrations/20260423112500_create_shared_public_tables.sql` - authoritative shared-table schema and RLS

### Secondary (MEDIUM confidence)
- None

### Tertiary (LOW confidence)
- None beyond claims marked `[ASSUMED]`

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - recommendations extend existing repo scripts, tests, and template files directly.
- Architecture: HIGH - based on current contract, conformance gate, and upstream template source.
- Pitfalls: MEDIUM - grounded in codebase gaps, with a few example failure shapes inferred from current enforcement boundaries.

**Research date:** 2026-04-26
**Valid until:** 2026-05-26
