# Standalone SaaS Template Contract (Hermes)

This document is the Hermes-operated contract for `standalone-saas-template`.
Downstream delivery workflows must treat this file as the operational source of truth.

## 1. Authority and source hierarchy

### Operational Source of Truth
- Hermes canonical contract: `docs/platform/standalone-saas-template-contract.md`
- This document is the operational source of truth for Hermes planners, executors, validators, and delivery workflows.

### Upstream References
- `../standalone-saas-template/README.md`
- `../standalone-saas-template/ARCHITECTURE.md`
- `../standalone-saas-template/BUILDING_RULES.md`

### Source Hierarchy Rule
1. Hermes operational automation follows this contract first.
2. Upstream template docs remain authoritative references for rationale and template-local detail.
3. If upstream wording is broader or more ambiguous, Hermes resolves the operational rule here before downstream execution continues.

## 2. Registered template summary

- **Asset ID**: `standalone-saas-template`
- **Governance Scope**: `single-template-first`
- **Registry Record**: `assets/shared/templates/standalone-saas-template.json`
- **Template Source**: `C:/Users/42236/Desktop/standalone-saas-template`
- **Intended Use**: Hermes-approved mini-SaaS project bootstrap
- **Supported Stack**:
  - `next`: `15.3.0`
  - `react`: `19.1.0`
  - `react-dom`: `19.1.0`
  - `@supabase/supabase-js`: `^2.49.1`
  - `typescript`: `^5.6.3`
- **Governance Owner**: `Hermes platform`
- **Governance Status**: `canonical`
- **Default backend model**: `single shared Supabase`
- **Independent backend bootstrap**: forbidden by default for generated SaaS workspaces

## 3. Protected platform layer

### Protected Platform Layer
The following files, routes, and data boundaries are protected platform primitives. Product delivery must not replace or casually rewrite them without explicit platform-level justification.

#### Shared auth and session layer
- `src/lib/auth.ts`
- `src/lib/supabase-browser.ts`
- `src/lib/supabase-server.ts`
- `src/app/api/auth/session/route.ts`
- `/api/auth/session`

#### Shared payment layer
- `src/lib/paypal.ts`
- `src/app/api/paypal/checkout/route.ts`
- `src/app/api/paypal/capture/route.ts`
- `src/app/api/paypal/client-token/route.ts`
- `/api/paypal/checkout`
- `/api/paypal/capture`
- `/api/paypal/client-token`

#### Shared entitlement and database guard layer
- `src/lib/entitlement.ts`
- `src/lib/db-guards.ts`

#### Shared public table boundary
- `supabase/migrations/20260423112500_create_shared_public_tables.sql`
- Shared global platform tables are limited to:
  - `users`
  - `orders`
  - `payments`
  - `subscriptions`
- Any new product business table must use the `APP_KEY_` prefix.
- No generated SaaS workspace may introduce an additional unprefixed public business table such as `public.leads`.

### Protected behavior rules
- Product code must reuse the single shared Supabase backend model instead of creating an independent backend by default.
- Product code must reuse shared auth, payment, and entitlement primitives before introducing alternatives.
- Product pages and client code must not directly write shared payment or entitlement state.
- Product pages and client code must not directly mutate `users`, `orders`, `payments`, or `subscriptions` from browser-owned code.
- Shared payment state remains server-owned.
- Shared public table semantics remain platform-governed.

## 4. Safe extension layer

### Safe Extension Layer
The following surfaces are the intended customization points for a new SaaS workspace.

#### Brand and app-definition surfaces
- `.env`
- `src/lib/app-definition.ts`
- `APP_KEY`
- `APP_NAME`
- `APP_URL`
- `PAYPAL_BRAND_NAME`

#### Product pages and product modules
- `src/app/page.tsx`
- `src/app/dashboard/page.tsx`
- `src/app/billing/page.tsx`
- `src/app/demo/page.tsx`
- new business pages under `src/app/*`
- product-specific modules under `src/components/*`

#### Product-specific data layer
- Business tables using the `APP_KEY_` prefix
- Product-specific UI, copy, pricing presentation, and workflows built on top of the protected platform layer

### Extension rule
Safe extension means adapting product identity, branding, UX, business modules, and `APP_KEY_` business tables without changing protected platform behavior by default.

## 5. Identity injection contract

Required identity values for a generated workspace:
- `APP_KEY`
- `APP_NAME`
- `APP_URL`
- `PAYPAL_BRAND_NAME`

Required identity behavior:
- `APP_KEY` must define the product namespace and drive `APP_KEY_` business-table naming.
- `APP_NAME` must drive product-facing naming and copy defaults.
- `APP_URL` must define the canonical product URL.
- Derived app-definition and brand fields must be updated so the generated workspace reflects the target product instead of the template label.
- Identity injection must update app-definition and brand-facing values that flow from the template configuration layer.

## 6. Required runtime and artifact paths

The following files and paths must exist in a conforming generated workspace:
- `.env`
- `.hermes/project-metadata.json`
- `.hermes/shared-backend-guardrails.json`
- `.hermes/PROJECT_BRIEF_ENTRYPOINT.md`
- `src/lib/config.ts`
- `src/lib/auth.ts`
- `src/lib/supabase-browser.ts`
- `src/lib/supabase-server.ts`
- `src/lib/paypal.ts`
- `src/lib/entitlement.ts`
- `src/lib/db-guards.ts`
- `src/lib/app-definition.ts`
- `src/app/api/auth/session/route.ts`
- `src/app/api/paypal/checkout/route.ts`
- `src/app/api/paypal/capture/route.ts`
- `src/app/demo/page.tsx`
- `supabase/migrations/20260423112500_create_shared_public_tables.sql`
- `README.md`
- `ARCHITECTURE.md`
- `BUILDING_RULES.md`

Required Hermes-side authority artifacts:
- `assets/shared/templates/standalone-saas-template.json`
- `docs/platform/standalone-saas-template-contract.md`

## 7. Conformance gate expectations

A generated workspace is not ready for handoff or deployment unless the conformance gate verifies all of the following:
- required identity values were injected
- required runtime and artifact paths exist
- the workspace declares `shared-supabase` as its backend model through `.hermes/shared-backend-guardrails.json`
- protected platform files and routes are still present
- protected platform layer has not drifted unexpectedly relative to the registered template source
- shared-path invariants still hold for auth, payment, entitlement, and shared public tables
- product-specific data remains inside `APP_KEY_` business-table boundaries
- `supabase/migrations/*.sql` only leave `users`, `orders`, `payments`, and `subscriptions` unprefixed; every other product business table must use the current `APP_KEY_` prefix
- `src/app/**/*.ts*` and `src/components/**/*.ts*` client files do not directly mutate `users`, `orders`, `payments`, or `subscriptions`

Blocking rule:
- Any missing protected path, missing identity value, broken authority artifact, broken shared backend declaration, unauthorized shared-table mutation path, broken table-boundary rule, or protected-layer drift must fail conformance and block downstream delivery.

## 8. Verification checklist

- `python -m unittest tests.test_template_registry tests.test_template_contract`
- `python -m unittest tests.test_instantiate_template_project`
- `python -m unittest tests.test_check_template_conformance`
- `python scripts/instantiate_template_project.py --help`
- `python scripts/check_template_conformance.py --help`
- Confirm `assets/shared/templates/standalone-saas-template.json` points to `docs/platform/standalone-saas-template-contract.md`
- Confirm this contract points back to `../standalone-saas-template/README.md`, `../standalone-saas-template/ARCHITECTURE.md`, and `../standalone-saas-template/BUILDING_RULES.md`
