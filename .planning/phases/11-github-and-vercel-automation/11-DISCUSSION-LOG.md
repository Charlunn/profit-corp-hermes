# Phase 11: GitHub and Vercel Automation - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-04-27
**Phase:** 11-github-and-vercel-automation
**Areas discussed:** GitHub repository authority, Code sync and branch linkage, Vercel project linkage and environment setup, Deployment gating and outcome reporting

---

## GitHub repository authority

| Option | Description | Selected |
|--------|-------------|----------|
| Approved-project authority first | Extend the existing approved-project record and workspace linkage as the control plane for repository prep. Keeps Phase 11 aligned with Phase 10 state and resume semantics. | ✓ |
| Workspace-first repo setup | Run repository preparation directly from workspace state. Simpler locally, but weakens the authority layer and operator traceability. | |
| Repo-only manual handoff | Treat GitHub as a mostly manual follow-up after workspace generation. Lowest automation value and conflicts with phase goals. | |

**User's choice:** Approved-project authority first
**Notes:** Auto mode selected the recommended default to preserve the Phase 10 authority bundle and avoid introducing a second control plane.

---

## Code sync and branch linkage

| Option | Description | Selected |
|--------|-------------|----------|
| Single canonical default branch | Sync the generated project to one authoritative branch per approved run and record repo/branch/run linkage. Simplest bootstrap path and matches first-delivery intent. | ✓ |
| PR-first bootstrap | Open a pull request instead of syncing directly to the canonical branch. Better for team review, but adds collaboration scope beyond this phase. | |
| Multi-branch release flow | Separate bootstrap, staging, and release branches from day one. More flexible, but too heavy for the first automation boundary. | |

**User's choice:** Single canonical default branch
**Notes:** Auto mode selected the recommended default because the repo currently optimizes for deterministic artifact-first delivery rather than collaborative release workflows.

---

## Vercel project linkage and environment setup

| Option | Description | Selected |
|--------|-------------|----------|
| Required-variable contract before deploy | Declare and apply the environment-variable set before deployment, with platform/project values tracked explicitly. Best fit for repeatable automation and blocked-state visibility. | ✓ |
| Manual dashboard completion after link | Let automation link the Vercel project but rely on the operator to finish env setup. Easier short term, but undermines repeatability. | |
| Best-effort partial env sync | Push what is available and continue if some values are missing. Reduces friction but weakens deployment safety. | |

**User's choice:** Required-variable contract before deploy
**Notes:** Auto mode selected the recommended default so deployment gating can remain deterministic and operator-visible.

---

## Deployment gating and outcome reporting

| Option | Description | Selected |
|--------|-------------|----------|
| Hard gate + durable blocked state | Trigger deployment only after sync/link/env checks pass, and persist failure evidence plus resume points when they do not. Extends the existing pipeline model cleanly. | ✓ |
| Soft gate + warning only | Allow deployment to proceed with warnings when some prerequisites are missing. Faster, but inconsistent with current blocking semantics. | |
| Separate deploy tracker outside authority record | Track deploy status in a parallel subsystem. Could work, but fragments the operator story and replay path. | |

**User's choice:** Hard gate + durable blocked state
**Notes:** Auto mode selected the recommended default because Phase 10 already established explicit blocked-state persistence and resume behavior.

---

## Claude's Discretion

- Exact helper-script split between GitHub and Vercel tasks
- Exact metadata field names for persisted repository and deployment linkage
- Exact command wrapper names added under `orchestration/cron/commands.sh`

## Deferred Ideas

- PR review / branch protection orchestration
- Multi-environment promotion matrices
- Credential-governance hardening beyond constrained usage boundaries
