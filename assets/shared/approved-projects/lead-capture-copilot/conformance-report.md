# Template Conformance Report
- Workspace: `C:/Users/42236/Desktop/dev/profit-corp-hermes/.claude/worktrees/agent-ae15860b/generated-workspaces/lead-capture-copilot`
- Contract: `docs/platform/standalone-saas-template-contract.md`
- Registry: `assets/shared/templates/standalone-saas-template.json`

## Status
- PASS

## Blocking Violations
None.

## Verified Paths
- .hermes/project-metadata.json
- .hermes/shared-backend-guardrails.json
- .hermes/PROJECT_BRIEF_ENTRYPOINT.md
- src/lib/auth.ts
- src/lib/supabase-browser.ts
- src/lib/supabase-server.ts
- src/lib/paypal.ts
- src/lib/entitlement.ts
- src/lib/db-guards.ts
- src/app/api/auth/session/route.ts
- src/app/api/paypal/checkout/route.ts
- src/app/api/paypal/capture/route.ts
- src/app/demo/page.tsx
- supabase/migrations/20260423112500_create_shared_public_tables.sql

## Fingerprint Checks
- src/lib/auth.ts — MATCH — workspace sha256=8831d69e9aaba00cc1ccceca015201061d9176160213acce6d8f2ed11eb0cabe — template sha256=8831d69e9aaba00cc1ccceca015201061d9176160213acce6d8f2ed11eb0cabe
- src/lib/supabase-browser.ts — MATCH — workspace sha256=09985846c59b4b80e4a98b7cbc2db7d0072a5fbb4316a49cfae3bba5a350dfa3 — template sha256=09985846c59b4b80e4a98b7cbc2db7d0072a5fbb4316a49cfae3bba5a350dfa3
- src/lib/supabase-server.ts — MATCH — workspace sha256=d23708005fbc4ad56a9bdf420858d67728b973bd1845645fc0cc5b98f397293f — template sha256=d23708005fbc4ad56a9bdf420858d67728b973bd1845645fc0cc5b98f397293f
- src/lib/paypal.ts — MATCH — workspace sha256=3c1c4cf9890cee6e4849d72eff229a0613741807a16b5843dcc1959e66d56a63 — template sha256=3c1c4cf9890cee6e4849d72eff229a0613741807a16b5843dcc1959e66d56a63
- src/lib/entitlement.ts — MATCH — workspace sha256=d2e025aeef7dfc1d2ec30c8c680038cee0276e862c0771486e1fc2e7107c3039 — template sha256=d2e025aeef7dfc1d2ec30c8c680038cee0276e862c0771486e1fc2e7107c3039
- src/lib/db-guards.ts — MATCH — workspace sha256=a033bcf4b8992b8c687ed6b598b61e488a8e1390ce140c085235071ad6878e35 — template sha256=a033bcf4b8992b8c687ed6b598b61e488a8e1390ce140c085235071ad6878e35
- src/app/api/auth/session/route.ts — MATCH — workspace sha256=71101bb880e7186ceeb26af902a3da76f320a9c4eed0874cacd5d56561e70f9f — template sha256=71101bb880e7186ceeb26af902a3da76f320a9c4eed0874cacd5d56561e70f9f
- src/app/api/paypal/checkout/route.ts — MATCH — workspace sha256=22d78e4f1b0b49ea96060576435221710b4f449076d537d7e23360d9bde32cc7 — template sha256=22d78e4f1b0b49ea96060576435221710b4f449076d537d7e23360d9bde32cc7
- src/app/api/paypal/capture/route.ts — MATCH — workspace sha256=0f5d4a7b2841f1080e86b37bee05ef42842d3db6c4f228669ca80e77bc622ac9 — template sha256=0f5d4a7b2841f1080e86b37bee05ef42842d3db6c4f228669ca80e77bc622ac9
- supabase/migrations/20260423112500_create_shared_public_tables.sql — MATCH — workspace sha256=bb3e1977a015422726d1e31d3ea3db7b82a4df1152d90511e4bb5b20c3b477d3 — template sha256=bb3e1977a015422726d1e31d3ea3db7b82a4df1152d90511e4bb5b20c3b477d3
