# Changelog

## v1.1.1 — Delivery Pipeline Reliability Fixes

### What changed
- restored governed GitHub auth so approved delivery can use either exported tokens or an already-authenticated `gh` CLI session
- repaired canonical GitHub repository owner/name/url targeting so approved projects stop falling back to slug-based identities
- hardened GitHub sync for real Windows + pnpm workspaces through source-only snapshots, remote convergence, transport fallback, and granular sync evidence
- restored governed Vercel auth and deploy reliability with explicit-token plus local-CLI auth paths and authoritative deploy metadata persistence
- reworked authority, status rendering, and validator precedence so recovered successful runs now present the true final completed state while preserving blocked history as audit evidence
- improved workspace restore/config materialization behavior and tightened delivery regression coverage

### Architecture impact
- delivery moved from “best effort live rerun” toward a recoverable, evidence-driven pipeline
- operator-visible truth is now expected to converge across authority JSON, status markdown, final review, and handoff artifacts
- existing workspaces can be refreshed instead of being blindly deleted and recreated

### Why it matters
- real operator machines can recover from GitHub/Vercel failures without manual repo surgery
- delivery validation now proves what actually succeeded, rather than just replaying commands
- the system is much closer to supporting a true first-product production launch as a repeatable path

---

## v1.1 — SaaS Delivery Factory

### What changed
- promoted `standalone-saas-template` into a governed Hermes platform asset with a canonical contract and conformance enforcement
- standardized approved-project bundles as the bridge from company-level decision making to product execution
- introduced a specialist delivery team / delivery orchestrator flow with staged handoffs:
  - design
  - development
  - testing
  - git versioning
  - release readiness
- added governed GitHub sync, Vercel deploy, and final handoff automation
- reconciled roadmap / requirements / state docs to the live delivery evidence set at milestone close

### Architecture impact
- the system stopped being only an intelligence-and-decision company core
- product execution became a governed pipeline instead of relying on a single technical role to manually carry a build to the finish line
- approved opportunities gained a repeatable path to deployable SaaS workspaces

### Why it matters
- the repo now contains both the company judgment layer and the product delivery layer
- `arch` remains a core company role, but product execution is now handled by a delivery team abstraction rather than one role doing everything
- this milestone is what turned Hermes into a real mini-SaaS factory candidate

---

## v1.0 — Operating Intelligence Core

### What changed
- established the Hermes-native multi-role company core:
  - `ceo`
  - `scout`
  - `cmo`
  - `arch`
  - `accountant`
- built web-wide signal intake, triage, and ranked shortlist generation
- added role-specific operating artifacts:
  - `PAIN_POINTS.md`
  - `MARKET_PLAN.md`
  - `TECH_SPEC.md`
  - `CEO_RANKING.md`
- shipped operating decision packages plus execution-pack and board-brief derivatives
- added governance controls, operator visibility, and recurring cron-oriented operation

### Architecture impact
- this milestone created the company decision layer
- it defined how Hermes finds pain points, evaluates them, and turns them into operating decisions
- it established the governance and observability base that later delivery automation builds on

### Why it matters
- without v1.0, there is no reliable way to know what to build
- this milestone gave Hermes a repeatable way to move from noisy public signals to structured internal judgment
- later delivery milestones depend on this foundation to ensure the product factory starts from real pain instead of arbitrary ideas
