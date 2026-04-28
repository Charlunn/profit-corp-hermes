# Requirements: Profit-Corp Hermes

**Defined:** 2026-04-26
**Core Value:** Turn noisy web-wide user pain signals into a clear, actionable operating view: which problems are worth pursuing, what matters most, what is risky, and what the company should build and launch next.

## v1.1 Requirements

Requirements for milestone v1.1 SaaS Delivery Factory.

### Template Platform

- [x] **TMPL-01**: Operator can register `standalone-saas-template` as a governed Hermes platform asset with its source location, supported stack, and intended use
- [x] **TMPL-02**: Development workflows can read a canonical template contract that defines which files and layers are safe to customize for a new SaaS
- [x] **TMPL-03**: Development workflows can identify protected platform layers that must not be changed without explicit platform-level justification
- [x] **TMPL-04**: Hermes can create a new SaaS project workspace from the registered template without manual copy-paste setup
- [x] **TMPL-05**: Hermes can apply project identity values such as `APP_KEY`, `APP_NAME`, and `APP_URL` to a newly instantiated SaaS project
- [x] **TMPL-06**: Hermes can verify that a generated SaaS project still conforms to the shared template rules before handoff or deployment

### Shared Backend Contract

- [x] **BACK-01**: Hermes can enforce that new SaaS projects target a single shared Supabase backend model rather than creating a separate backend by default
- [x] **BACK-02**: Hermes can enforce that product-specific business tables use the `APP_KEY_` prefix
- [x] **BACK-03**: Hermes can detect and block creation of unprefixed product business tables in generated SaaS projects
- [x] **BACK-04**: Hermes can preserve the template’s shared-table boundary so only `users`, `orders`, `payments`, and `subscriptions` are treated as global platform tables
- [x] **BACK-05**: Hermes can require product implementations to reuse the shared auth, payment, and entitlement flows instead of replacing them by default
- [x] **BACK-06**: Hermes can validate that product code does not directly write shared payment or entitlement state from client-side code

### Development Team Orchestration

- [x] **TEAM-01**: Hermes can define a specialist Claude Code-powered development team for post-approval SaaS delivery with explicit role responsibilities
- [x] **TEAM-02**: Hermes can define the required inputs, outputs, and handoff artifacts for each development role in the delivery workflow
- [x] **TEAM-03**: Hermes can give each delivery role access to the approved template rules, project brief, and GSD operating constraints before implementation starts
- [x] **TEAM-04**: Hermes can constrain delivery roles so they only operate within approved project scope unless the owner reopens scope
- [x] **TEAM-05**: Hermes can record which role performed each major delivery action for auditability
- [x] **TEAM-06**: Hermes can run a repeatable approved-project delivery workflow without requiring the owner to manually orchestrate every development step

### Approval and Delivery Pipeline

- [x] **PIPE-01**: Owner can approve a product opportunity once and mark it ready for automated delivery execution
- [x] **PIPE-02**: Hermes can convert an approved product opportunity into a delivery-ready project brief with the required implementation context
- [x] **PIPE-03**: Hermes can start a new SaaS delivery workflow automatically after approval without requiring repeated manual kickoff actions
- [x] **PIPE-04**: Hermes can instantiate a project from the shared template and attach the approved project brief to the new delivery workspace
- [x] **PIPE-05**: Hermes can track the delivery state of each approved SaaS project from initialization through handoff
- [x] **PIPE-06**: Hermes can stop or block automated delivery when a required platform rule, credential requirement, or deployment precondition is missing
- [x] **PIPE-07**: Hermes can produce a final operator-facing handoff artifact that summarizes what was built, what was deployed, and what still needs attention

### GitHub and Deployment Automation

- [x] **SHIP-01**: Hermes can use platform-managed GitHub credentials to create or prepare a repository for a newly approved SaaS project
- [x] **SHIP-02**: Hermes can sync generated project code to the target GitHub repository without manual repository setup by the owner
- [x] **SHIP-03**: Hermes can record which repository, branch, and delivery run correspond to each approved SaaS project
- [x] **SHIP-04**: Hermes can use platform-managed Vercel credentials to link a generated SaaS project to a deployable Vercel project
- [x] **SHIP-05**: Hermes can configure required deployment environment values for a generated SaaS project through the approved platform delivery flow
- [x] **SHIP-06**: Hermes can trigger a Vercel deployment for a generated SaaS project after code sync and deployment checks pass
- [x] **SHIP-07**: Hermes can report deployment success or failure back into the project handoff artifact
- [x] **SHIP-08**: Hermes can block deployment when required platform-managed credentials, project linkage, or environment configuration are incomplete

### Governance and Credential Control

- [x] **GOV-01**: Hermes can store and use platform-managed GitHub and Vercel automation credentials through a documented platform-controlled path
- [x] **GOV-02**: Hermes can restrict credential use to approved delivery actions instead of allowing open-ended arbitrary operations
- [x] **GOV-03**: Hermes can record an audit trail for repository creation, code sync, environment configuration, and deployment actions
- [x] **GOV-04**: Hermes can distinguish between platform-level changes and product-level changes so protected platform behavior is not silently altered during product delivery
- [x] **GOV-05**: Hermes can require explicit platform justification before shared template primitives or shared backend contracts are modified
- [x] **GOV-06**: Hermes can surface failed approvals, blocked deliveries, and deployment failures in an operator-visible review artifact

## Future Requirements

Deferred to a future milestone.

### Product Factory Expansion

- **FACT-01**: Hermes can provision product-specific Supabase policies or stricter tenant isolation beyond naming conventions when scaling pressure requires it
- **FACT-02**: Hermes can automatically register domains and production DNS for deployed SaaS projects
- **FACT-03**: Hermes can maintain a reusable catalog of SaaS product variants and vertical presets on top of the shared template
- **FACT-04**: Hermes can run post-deploy canary checks and rollback workflows automatically for each shipped SaaS project

## Out of Scope

| Feature | Reason |
|---------|--------|
| Building a specific end-user SaaS product inside this milestone | This milestone is for factory capability, not one customer app |
| Supporting arbitrary non-template stacks by default | The goal is repeatable fast delivery, not unlimited stack freedom |
| Allowing product agents to redesign shared auth/payment platform layers freely | Shared platform stability is required for safe repeated delivery |
| Spinning up a separate Supabase backend for every SaaS by default | The agreed model is one shared Supabase project unless explicitly changed later |

## Traceability

| Requirement | Phase | Status |
|-------------|-------|--------|
| TMPL-01 | Phase 7 | Complete |
| TMPL-02 | Phase 7 | Complete |
| TMPL-03 | Phase 7 | Complete |
| TMPL-04 | Phase 7 | Complete |
| TMPL-05 | Phase 7 | Complete |
| TMPL-06 | Phase 7 | Complete |
| BACK-01 | Phase 8 | Complete |
| BACK-02 | Phase 8 | Complete |
| BACK-03 | Phase 8 | Complete |
| BACK-04 | Phase 8 | Complete |
| BACK-05 | Phase 8 | Complete |
| BACK-06 | Phase 8 | Complete |
| TEAM-01 | Phase 9 | Complete |
| TEAM-02 | Phase 9 | Complete |
| TEAM-03 | Phase 9 | Complete |
| TEAM-04 | Phase 9 | Complete |
| TEAM-05 | Phase 9 | Complete |
| TEAM-06 | Phase 9 | Complete |
| PIPE-01 | Phase 10 | Complete |
| PIPE-02 | Phase 10 | Complete |
| PIPE-03 | Phase 10 | Complete |
| PIPE-04 | Phase 10 | Complete |
| PIPE-05 | Phase 10 | Complete |
| PIPE-06 | Phase 10 | Complete |
| PIPE-07 | Phase 10 | Complete |
| SHIP-01 | Phase 11 | Complete |
| SHIP-02 | Phase 11 | Complete |
| SHIP-03 | Phase 11 | Complete |
| SHIP-04 | Phase 11 | Complete |
| SHIP-05 | Phase 11 | Complete |
| SHIP-06 | Phase 11 | Complete |
| SHIP-07 | Phase 11 | Complete |
| SHIP-08 | Phase 11 | Complete |
| GOV-01 | Phase 12 | Complete |
| GOV-02 | Phase 12 | Complete |
| GOV-03 | Phase 12 | Complete |
| GOV-04 | Phase 12 | Complete |
| GOV-05 | Phase 12 | Complete |
| GOV-06 | Phase 12 | Complete |

**Coverage:**
- v1.1 requirements: 39 total
- Mapped to phases: 39
- Unmapped: 0

---
*Requirements defined: 2026-04-26*
*Last updated: 2026-04-28 after Phase 13 canonical reconciliation*
