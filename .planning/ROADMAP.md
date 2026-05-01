# Profit-Corp Hermes

## Milestones

- ✅ **v1.1.1 Delivery Pipeline Reliability Fixes** — Phases 14-17 (shipped 2026-04-30)
- ✅ **v1.1 SaaS Delivery Factory** — Phases 7-13 (shipped 2026-04-28)
- ✅ **v1.0 milestone** — Phases 1-6 (shipped 2026-04-26)

## Phases

<details>
<summary>✅ v1.1.1 Delivery Pipeline Reliability Fixes (Phases 14-17) — SHIPPED 2026-04-30</summary>

- [x] Phase 14: GitHub Auth and Repo Target Reliability (2/2 plans) — completed 2026-04-29
- [x] Phase 15: GitHub Sync Reliability on Real Workspaces (3/3 plans) — completed 2026-04-29
- [x] Phase 16: Vercel Auth and Deploy Reliability (3/3 plans) — completed 2026-04-29
- [x] Phase 17: Authority and Status Convergence (3/3 plans) — completed 2026-04-29

</details>

## Progress

| Milestone | Phases | Plans Complete | Status | Shipped |
|-----------|--------|----------------|--------|---------|
| v1.1.1 | 14-17 | 10/10 | Shipped | 2026-04-30 |
| v1.1 | 7-13 | 20/20 | Shipped | 2026-04-28 |
| v1.0 | 1-6 | 18/18 | Shipped | 2026-04-26 |

## Milestone Summary

**Key Decisions:**
- Treat the live Hermes instance test as authoritative evidence for v1.1.1 scope instead of reopening broad product-factory exploration
- Keep the approved-project delivery architecture and repair its broken auth, sync, deploy, and status boundaries in place
- Prioritize real operator-environment compatibility over idealized token-only automation assumptions

**Issues Targeted:**
- `missing_github_auth` despite valid `gh` login
- GitHub owner fallback to project slug
- Windows long-path / dependency snapshot failures during `github_sync`
- HTTPS push assumptions that fail while SSH is healthy
- Vercel token-only gating that ignores a valid local CLI login path
- Authority/status artifacts remaining blocked after a successful recovered live deploy

**Deferred:**
- DNS/domain automation
