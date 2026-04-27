# Phase 11: GitHub and Vercel Automation - Research

**Researched:** 2026-04-27
**Domain:** GitHub repository bootstrap, code sync, Vercel project linkage, environment configuration, and deployment orchestration
**Confidence:** MEDIUM

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions
### GitHub repository authority
- **D-01:** Phase 11 should start from the existing Phase 10 approved-project authority bundle and workspace linkage, not from ad-hoc repository commands run directly against a workspace.
- **D-02:** Repository preparation should support both creating a new GitHub repository and attaching to a pre-existing approved target repository, with the authority record capturing which path was used.
- **D-03:** GitHub automation should use a constrained platform-managed CLI/token path oriented to repository bootstrap and code sync only, not a generic arbitrary GitHub operator shell.

### Code sync and branch linkage
- **D-04:** Generated project code should sync to one canonical default branch per approved project run, with the authority record persisting repository URL/name, default branch, and delivery-run linkage.
- **D-05:** Initial sync should favor deterministic full-project bootstrap semantics over PR-first or multi-branch collaboration flows, because this phase is about first deployment readiness for a newly generated SaaS.
- **D-06:** Sync failures must hard-block downstream deployment and persist explicit evidence in the approved-project status layer rather than letting Vercel steps run on stale or partial repository state.

### Vercel project linkage and environment setup
- **D-07:** Vercel automation should attach the generated workspace to one deployable Vercel project per approved SaaS and persist the Vercel project identifier/linkage in the authority record.
- **D-08:** Deployment environment values should be applied through a declared required-variable contract before deployment, not by relying on manual dashboard setup after code sync.
- **D-09:** Environment configuration should distinguish reusable platform-level variables from project-identity values derived from the approved bundle so the deploy path stays repeatable across SaaS projects.

### Deployment gating and outcome reporting
- **D-10:** Deployment should only trigger after GitHub sync, Vercel linkage, and required environment configuration all pass explicit checks.
- **D-11:** Missing credentials, missing repository linkage, missing Vercel linkage, or missing required environment values should produce durable blocked states with evidence paths and resume points instead of silent skips.
- **D-12:** Deployment success or failure should flow back into both the approved-project authority surface and the workspace-local handoff artifacts so operators can trace one run from approval through deploy result.

### Claude's Discretion
- Exact artifact names and JSON schema additions for GitHub/Vercel linkage metadata, as long as repo, branch, Vercel project, deploy status, and evidence links stay explicit.
- Exact command wrapper names and script boundaries for GitHub/Vercel helpers, as long as they remain consistent with the existing `orchestration/cron/commands.sh` pattern.
- Exact split between separate GitHub and Vercel helper scripts versus one higher-level orchestrator helper, as long as blocking/resume semantics remain stable.

### Deferred Ideas (OUT OF SCOPE)
- Fine-grained credential scoping, credential storage hardening, and broader deployment audit controls belong to Phase 12.
- Multi-environment promotion workflows such as staging/preview/prod matrices are outside this phase unless required for basic Vercel deployability.
- Team collaboration features such as PR review loops, release approvals, or branch protection orchestration are beyond this first automation boundary.
</user_constraints>

## Summary

Phase 11 should extend the existing Phase 10 authority-driven pipeline instead of introducing a separate deploy subsystem. The current codebase already has the right primitives: an approved-project authority record, append-only approved-delivery events, a latest-view renderer, validator-based cross-link checking, and durable blocked/resume semantics. The planner should treat GitHub sync and Vercel deployment as additional pipeline stages that follow `delivery_run_bootstrap`, not as ad-hoc post-processing. [VERIFIED: codebase grep] [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py] [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/render_approved_delivery_status.py] [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_approved_delivery_pipeline.py]

The standard automation surface is CLI-first. GitHub CLI supports headless authentication through environment tokens and supports repository creation from an existing local source directory with `--source`, `--push`, and `--remote`; GitHub also states that the created repository uses the configured repository default branch. Vercel CLI supports non-interactive linking to an existing project with `vercel link --yes --team ... --project ...`, environment variable management via `vercel env add|list|pull|remove|update`, and deploy execution via `vercel deploy` with `--prod`, `--target`, `--logs`, and `--no-wait`. [CITED: https://cli.github.com/manual/gh_auth_login] [CITED: https://cli.github.com/manual/gh_repo_create] [VERIFIED: Vercel CLI help 52.0.0]

The main planning risk is environment reality, not code structure. On this machine, `node`, `python`, and `git` are installed, but `gh` is not installed and `vercel` is not installed globally; only `npx vercel@latest` is immediately usable. `npx vercel@latest whoami` entered a device-login flow, proving credentials are not already available in the current shell context. Phase 11 therefore needs explicit blocked-state handling for missing GitHub CLI and missing authenticated Vercel access, with evidence artifacts and resume instructions. [VERIFIED: local CLI probe] [VERIFIED: /c/Users/42236/AppData/Local/Temp/claude/C--Users-42236-Desktop-dev-profit-corp-hermes/6a25ade3-2493-4c0e-b5e1-e21eb10a944a/tasks/bi7qicjjm.output]

**Primary recommendation:** Implement Phase 11 as four new approved-delivery stages: `github_repository`, `github_sync`, `vercel_linkage`, and `vercel_deploy`, each persisting explicit authority metadata, evidence paths, and resume points, and each hard-blocking downstream stages on failure. [VERIFIED: codebase grep] [CITED: https://cli.github.com/manual/gh_repo_create] [VERIFIED: Vercel CLI help 52.0.0]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Approved-project orchestration | API / Backend | Database / Storage | Python scripts already own durable pipeline state, event emission, blocking, and resume logic. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py] |
| GitHub repository creation/attachment | API / Backend | Database / Storage | This is a controlled automation action using platform credentials plus persisted authority metadata, not a browser concern. [CITED: https://cli.github.com/manual/gh_repo_create] [VERIFIED: codebase grep] |
| Code sync from workspace to canonical branch | API / Backend | Database / Storage | Sync uses git/gh subprocess execution and must persist repo URL, branch, commit, and evidence in authority artifacts. [CITED: https://cli.github.com/manual/gh_repo_create] [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py] |
| Vercel project linkage | API / Backend | Database / Storage | Linking is a CLI/API automation step that creates local linkage state and should be mirrored into authority metadata. [VERIFIED: Vercel CLI help 52.0.0] |
| Deployment environment contract enforcement | API / Backend | Database / Storage | Required env var checks are governance/pipeline logic with durable blocked states, not frontend logic. [VERIFIED: Vercel CLI help 52.0.0] [VERIFIED: codebase grep] |
| Deployment execution and result capture | API / Backend | Database / Storage | Deploy commands run off-box but orchestration, gating, and result persistence belong in the pipeline controller. [VERIFIED: Vercel CLI help 52.0.0] [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/docs/OPERATIONS.md] |
| Operator-visible status rendering | Frontend Server (SSR) | API / Backend | The current system renders markdown latest views from append-only events; that rendering layer is separate from execution. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/render_approved_delivery_status.py] |

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| GitHub CLI (`gh`) | 2.91.0 | Authenticated repository bootstrap and constrained GitHub operations from scripts. [CITED: https://cli.github.com/manual/gh_auth_login] | It gives a narrow command surface for repo creation and automation-friendly auth instead of hand-rolling GitHub REST calls. [CITED: https://cli.github.com/manual/gh_repo_create] |
| Vercel CLI (`vercel`) | 52.0.0 | Project linkage, environment variable management, and deployment execution. [VERIFIED: npm registry] | It exposes the exact link/env/deploy workflow this phase needs, including non-interactive flags and env subcommands. [VERIFIED: Vercel CLI help 52.0.0] |
| Python stdlib (`subprocess`, `json`, `pathlib`) | 3.11.15 runtime present | Durable orchestration, evidence capture, artifact writes, and CLI wrapping in existing repo style. [VERIFIED: local CLI probe] | The repo already uses Python scripts as the durable business-logic layer behind shell wrappers. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/orchestration/cron/commands.sh] [VERIFIED: codebase grep] |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| git | 2.53.0.windows.1 | Local repo initialization, remote setup, branch sync, and commit/push execution under script control. [VERIFIED: local CLI probe] | Use inside the GitHub sync stage after repo authority is resolved. [VERIFIED: codebase grep] |
| `npx vercel@latest` fallback | 52.0.0 | CLI access when `vercel` is not globally installed. [VERIFIED: local CLI probe] [VERIFIED: npm registry] | Use on this machine today because global `vercel` is absent. [VERIFIED: local CLI probe] |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `gh` CLI | Raw GitHub REST API calls | API calls would increase credential, pagination, and error-handling surface in Phase 11, while the user explicitly chose a constrained CLI/token path. [CITED: https://cli.github.com/manual/gh_auth_login] [ASSUMED] |
| Vercel CLI | Vercel REST/SDK | The SDK/API is viable, but the CLI already provides link/env/deploy commands that fit the repo’s script-wrapper pattern better for this phase. [VERIFIED: Vercel CLI help 52.0.0] [ASSUMED] |

**Installation:**
```bash
# Required on operator machine or CI host
# GitHub CLI installation path is OS-specific; verify availability with `gh --version`
npm install -g vercel@52.0.0
```

**Version verification:**
- `vercel` latest npm version is `52.0.0`, with registry modified date `2026-04-22T00:25:41.159Z`. [VERIFIED: npm registry]
- GitHub CLI latest release observed was `v2.91.0`, published `2026-04-22T10:40:12Z`. [VERIFIED: https://api.github.com/repos/cli/cli/releases/latest]

## Architecture Patterns

### System Architecture Diagram
```text
Approved Project Authority Bundle
  (APPROVED_PROJECT.json + PROJECT_BRIEF.md)
            |
            v
start-approved-delivery / resume-approved-delivery wrapper
            |
            v
Phase 10 controller (existing Python pipeline)
            |
            +--> validate approval/brief/workspace prerequisites
            |
            +--> github_repository
            |      |- check credential/tool availability
            |      |- create new repo OR attach existing repo
            |      `- persist repo identity + evidence
            |
            +--> github_sync
            |      |- init/verify local git state in workspace
            |      |- set canonical remote/default branch
            |      |- push deterministic bootstrap snapshot
            |      `- persist branch/commit/sync evidence
            |
            +--> vercel_linkage
            |      |- check Vercel auth/tool availability
            |      |- link workspace to one Vercel project
            |      |- apply required env contract
            |      `- persist project linkage + env evidence
            |
            +--> vercel_deploy
            |      |- run explicit preflight checks
            |      |- trigger deployment
            |      |- capture deployment URL/status/log evidence
            |      `- persist outcome to authority + workspace
            |
            v
approved-delivery-events.jsonl ---> DELIVERY_PIPELINE_STATUS.md
            |
            v
workspace .hermes delivery artifacts + FINAL_DELIVERY.md
```

### Recommended Project Structure
```text
scripts/
├── github_delivery_common.py        # Shared repo/auth/evidence helpers [ASSUMED]
├── vercel_delivery_common.py        # Shared link/env/deploy helpers [ASSUMED]
├── start_approved_project_delivery.py  # Extend with new stages and metadata
├── render_approved_delivery_status.py  # Extend latest-view fields
└── validate_approved_delivery_pipeline.py  # Extend cross-link checks

orchestration/cron/
└── commands.sh                      # Add stable wrappers

tests/
├── test_phase11_github_sync.py      # New stage tests [ASSUMED]
├── test_phase11_vercel_flow.py      # New stage tests [ASSUMED]
└── existing approved-delivery tests # Extend CLI/status/validator coverage
```

### Pattern 1: Extend the existing authority-first pipeline
**What:** Add Phase 11 as new approved-delivery stages after `delivery_run_bootstrap`, preserving the authority record as the source above workspace-local state. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py] [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/.planning/phases/11-github-and-vercel-automation/11-CONTEXT.md]

**When to use:** For all GitHub/Vercel actions in this phase, because D-01 and D-12 explicitly require continuing from the approved-project authority bundle. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/.planning/phases/11-github-and-vercel-automation/11-CONTEXT.md]

**Example:**
```python
# Source: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py
if start_stage == "conformance":
    result = check_template_conformance(workspace, report_path)
    if not result.get("ok"):
        return block_pipeline(...)
    append_pipeline_event(project_dir, make_event(...))
    update_pipeline_state(record, stage="conformance", status="ready", ...)
```
[VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py]

### Pattern 2: Every external action emits append-only evidence
**What:** Each stage should append a validated event and refresh the markdown latest view, rather than mutating hidden state only. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/append_approved_delivery_event.py] [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/render_approved_delivery_status.py]

**When to use:** For repo creation, repo attach, sync start/success/failure, Vercel link, env sync, deploy trigger, deploy success, and deploy failure. [VERIFIED: codebase grep] [ASSUMED]

**Example:**
```python
# Source: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/append_approved_delivery_event.py
append_approved_delivery_event(project_dir, {
    "project_slug": slug,
    "stage": "github_sync",
    "status": "ready",
    "action": "repository_synced",
    "timestamp": ts,
    "outcome": "pass",
    ...
})
```
[VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/append_approved_delivery_event.py] [ASSUMED]

### Pattern 3: Non-interactive CLI usage only
**What:** Run GitHub and Vercel flows in headless mode using environment tokens and explicit flags. [CITED: https://cli.github.com/manual/gh_auth_login] [VERIFIED: Vercel CLI help 52.0.0]

**When to use:** Always in the delivery pipeline; interactive prompts break resumability and unattended runs. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/docs/OPERATIONS.md] [ASSUMED]

**Example:**
```bash
# Source: https://cli.github.com/manual/gh_auth_login
printf '%s' "$GITHUB_TOKEN" | gh auth login --with-token

# Source: Vercel CLI help 52.0.0
npx vercel@latest link --yes --team "$VERCEL_TEAM" --project "$VERCEL_PROJECT" --cwd "$WORKSPACE"
```

### Anti-Patterns to Avoid
- **Skipping the authority layer:** Running `git remote add`, `gh repo create`, or `vercel deploy` manually against a workspace without updating approved-project artifacts violates D-01 and breaks validator-oriented traceability. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/.planning/phases/11-github-and-vercel-automation/11-CONTEXT.md] [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/docs/OPERATIONS.md]
- **Deploying after sync failure:** D-06 and D-10 require hard blocking, so stale workspace state must never continue to Vercel. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/.planning/phases/11-github-and-vercel-automation/11-CONTEXT.md]
- **Depending on interactive login:** `vercel whoami` started device login here, proving the runtime can easily fall into interactive auth. The planner should require explicit token-based or pre-authenticated execution paths. [VERIFIED: /c/Users/42236/AppData/Local/Temp/claude/C--Users-42236-Desktop-dev-profit-corp-hermes/6a25ade3-2493-4c0e-b5e1-e21eb10a944a/tasks/bi7qicjjm.output]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| GitHub repository creation flow | Custom REST client for repo bootstrap | `gh repo create` | The CLI already handles create-from-source, visibility, remote naming, and push behavior. [CITED: https://cli.github.com/manual/gh_repo_create] |
| GitHub auth bootstrapping | Homemade OAuth/device-code wrapper | `gh auth login` with token/env-based auth | Official CLI documents automation-friendly token flows and host targeting. [CITED: https://cli.github.com/manual/gh_auth_login] |
| Vercel project linkage | Writing `.vercel` linkage files by hand | `vercel link` | Official CLI exposes a direct linking command with non-interactive flags. [VERIFIED: Vercel CLI help 52.0.0] |
| Vercel environment synchronization | Editing dashboard-only values manually as the default path | `vercel env add`, `vercel env list`, `vercel env pull`, `vercel env update` | The CLI already models env values as scriptable project state. [VERIFIED: Vercel CLI help 52.0.0] |
| Deployment execution | Custom deploy-hook orchestration for first deploy | `vercel deploy` | The CLI already supports target selection, logs, runtime env injection, and URL output. [VERIFIED: /c/Users/42236/AppData/Local/Temp/claude/C--Users-42236-Desktop-dev-profit-corp-hermes/6a25ade3-2493-4c0e-b5e1-e21eb10a944a/tasks/bi7qicjjm.output] |

**Key insight:** Phase 11 is mostly about integrating existing CLIs into Hermes’ durable state machine, not inventing new platform protocols. [VERIFIED: codebase grep] [CITED: https://cli.github.com/manual/gh_repo_create] [VERIFIED: Vercel CLI help 52.0.0]

## Common Pitfalls

### Pitfall 1: Missing tool versus missing credential confusion
**What goes wrong:** A failed automation run reports “GitHub/Vercel failed” without distinguishing missing executable, missing token, expired login, or missing project/team identifiers. [VERIFIED: local CLI probe] [ASSUMED]
**Why it happens:** Both platforms are external CLIs, and current environment checks already show `gh` missing while Vercel can prompt interactively. [VERIFIED: local CLI probe] [VERIFIED: /c/Users/42236/AppData/Local/Temp/claude/C--Users-42236-Desktop-dev-profit-corp-hermes/6a25ade3-2493-4c0e-b5e1-e21eb10a944a/tasks/bi7qicjjm.output]
**How to avoid:** Persist separate block reasons such as `missing_github_cli`, `missing_github_credentials`, `missing_vercel_cli`, `missing_vercel_credentials`, and `missing_vercel_scope`. [ASSUMED]
**Warning signs:** `command not found`, device-login prompts, or empty repo/project identifiers in authority metadata. [VERIFIED: local CLI probe]

### Pitfall 2: Treating workspace-local linkage as sufficient authority state
**What goes wrong:** `.git/config` or `.vercel` contains useful linkage, but the approved-project authority record does not, so status and resume become opaque. [VERIFIED: codebase grep] [ASSUMED]
**Why it happens:** CLIs write local state, but Hermes’ operator model depends on authority artifacts and latest views. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/docs/OPERATIONS.md] [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/render_approved_delivery_status.py]
**How to avoid:** Mirror all final linkage values into `APPROVED_PROJECT.json` plus append-only events. [VERIFIED: codebase grep] [ASSUMED]
**Warning signs:** Resume logic needs to rediscover repo/project linkage from disk instead of reading it from the authority record. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_project_delivery_pipeline_resume.py] [ASSUMED]

### Pitfall 3: Deploying before env-contract completion
**What goes wrong:** Vercel link succeeds, but runtime fails because required env vars were never declared or applied. [VERIFIED: Vercel CLI help 52.0.0] [ASSUMED]
**Why it happens:** Linking and deployment are separate CLI steps, and D-08/D-10 explicitly forbid relying on later manual dashboard setup. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/.planning/phases/11-github-and-vercel-automation/11-CONTEXT.md]
**How to avoid:** Add a required-variable contract artifact and a preflight stage that compares required names against linked Vercel project env state before deploy. [VERIFIED: Vercel CLI help 52.0.0] [ASSUMED]
**Warning signs:** Deploy succeeds technically but handoff lacks env evidence or app URL health status. [ASSUMED]

### Pitfall 4: Using repo creation defaults without recording branch reality
**What goes wrong:** The code assumes `main`, but GitHub says repo creation uses the configured repository default branch. [CITED: https://cli.github.com/manual/gh_repo_create]
**Why it happens:** Default branch names are account/org configuration, not a universal constant. [CITED: https://cli.github.com/manual/gh_repo_create]
**How to avoid:** After repo create or attach, explicitly detect and persist the canonical branch name used for sync. [CITED: https://cli.github.com/manual/gh_repo_create] [ASSUMED]
**Warning signs:** Push/remote commands reference a branch that does not exist remotely. [ASSUMED]

## Code Examples

Verified patterns from official sources:

### Headless GitHub auth
```bash
# Source: https://cli.github.com/manual/gh_auth_login
printf '%s' "$GITHUB_TOKEN" | gh auth login --with-token
```
[CITED: https://cli.github.com/manual/gh_auth_login]

### Create remote repository from existing workspace and push it
```bash
# Source: https://cli.github.com/manual/gh_repo_create
gh repo create "$OWNER/$REPO" \
  --private \
  --source "$WORKSPACE" \
  --remote origin \
  --push
```
[CITED: https://cli.github.com/manual/gh_repo_create]

### Non-interactive Vercel project link
```bash
# Source: Vercel CLI help 52.0.0
npx vercel@latest link \
  --yes \
  --team "$VERCEL_TEAM" \
  --project "$VERCEL_PROJECT" \
  --cwd "$WORKSPACE"
```
[VERIFIED: Vercel CLI help 52.0.0]

### Non-interactive Vercel env injection
```bash
# Source: Vercel CLI help 52.0.0
npx vercel@latest env add API_TOKEN production --value "$API_TOKEN" --yes
```
[VERIFIED: Vercel CLI help 52.0.0]

### Capture deployment URL from CLI stdout
```bash
# Source: Vercel deploy help 52.0.0
npx vercel@latest deploy --prod --yes > deployment-url.txt
```
[VERIFIED: /c/Users/42236/AppData/Local/Temp/claude/C--Users-42236-Desktop-dev-profit-corp-hermes/6a25ade3-2493-4c0e-b5e1-e21eb10a944a/tasks/bi7qicjjm.output]

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Manual dashboard linking and env setup for each project [ASSUMED] | CLI-driven repository bootstrap and deploy linkage through `gh` and `vercel` commands. [CITED: https://cli.github.com/manual/gh_repo_create] [VERIFIED: Vercel CLI help 52.0.0] | Current as of docs/release data fetched 2026-04-27. [VERIFIED: npm registry] [VERIFIED: https://api.github.com/repos/cli/cli/releases/latest] | Hermes can persist machine-readable evidence instead of depending on operator memory. [VERIFIED: codebase grep] |
| Local-only delivery handoff [VERIFIED: codebase grep] | Authority-plus-workspace cross-link validation model already in repo. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_approved_delivery_pipeline.py] | Established in Phase 10 artifacts dated 2026-04-27. [VERIFIED: repository files] | Phase 11 should add external platform linkage without breaking this contract. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/.planning/phases/11-github-and-vercel-automation/11-CONTEXT.md] |

**Deprecated/outdated:**
- Assuming `main` or `master` as an unverified branch default is outdated for this phase because GitHub CLI explicitly says repository creation uses the configured repository default branch. [CITED: https://cli.github.com/manual/gh_repo_create]
- Interactive-only deployment setup is incompatible with Hermes automation because current Vercel CLI supports non-interactive flags and current runtime can fall into device login if not preconfigured. [VERIFIED: Vercel CLI help 52.0.0] [VERIFIED: /c/Users/42236/AppData/Local/Temp/claude/C--Users-42236-Desktop-dev-profit-corp-hermes/6a25ade3-2493-4c0e-b5e1-e21eb10a944a/tasks/bi7qicjjm.output]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | Raw GitHub REST/SDK integration is not worth Phase 11 complexity versus `gh`. | Standard Stack | Planner may under-consider a better API-native design. |
| A2 | Separate helper modules `github_delivery_common.py` and `vercel_delivery_common.py` are the best file split. | Architecture Patterns | Planner may overfit file structure too early. |
| A3 | New approved-delivery event stages should be named `github_repository`, `github_sync`, `vercel_linkage`, and `vercel_deploy`. | Summary / Architecture Patterns | Validator and tests may prefer different naming. |
| A4 | Required deploy env contract should be materialized as a dedicated artifact file and checked against Vercel env state. | Common Pitfalls | Could add unnecessary artifact complexity if a simpler contract already exists elsewhere. |
| A5 | Missing-tool and missing-credential block reasons should be split into the exact names proposed here. | Common Pitfalls | Planner may lock schemas that differ from later implementation preference. |

## Open Questions (RESOLVED)

1. **What exact authority schema should record GitHub/Vercel linkage?** [RESOLVED]
   - Decision: Record external delivery linkage under a new top-level `shipping` section on the approved-project authority record, with `shipping.github` and `shipping.vercel` as stable sub-objects.
   - Reason: This keeps repository/deployment state separate from `pipeline` execution status and from generic `artifacts` file pointers, while matching the Phase 11 context decision that repo, branch, Vercel project, deploy status, and evidence links must stay explicit.
   - Planning consequence: Renderer, validator, and stage helpers should all read/write the same `shipping.*` contract in the same plan slices that introduce the fields.

2. **Should Vercel linkage create projects or only attach to pre-created projects?** [RESOLVED]
   - Decision: Phase 11 should attach to a supplied/approved target Vercel project when project id or name is present; otherwise it should block with evidence instead of attempting automatic project creation.
   - Reason: The phase boundary requires one deployable Vercel project per SaaS, but does not lock automatic project provisioning; credential rights for project creation are unverified and Phase 12 is the governance phase.
   - Planning consequence: Plans should implement explicit linkage validation plus a durable blocked state for missing project linkage, not speculative project-provisioning logic.

3. **Where should required env vars come from?** [RESOLVED]
   - Decision: Required env vars should come from a declared environment-contract artifact that separates platform-managed secrets from approved-project identity-derived values.
   - Reason: The template contract already defines identity values like `APP_KEY`, `APP_NAME`, `APP_URL`, and `PAYPAL_BRAND_NAME`, while platform-managed secrets must stay external and non-persisted in raw form.
   - Planning consequence: Vercel automation should generate/persist env-contract evidence and block deploy when required secret inputs are missing, while deriving non-secret identity values from the approved bundle.

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|------------|-----------|---------|----------|
| git | GitHub sync stage | ✓ | 2.53.0.windows.1 | — |
| node | Vercel CLI via `npx` | ✓ | v24.14.0 | — |
| python | Orchestration scripts/tests | ✓ | 3.11.15 | — |
| GitHub CLI (`gh`) | GitHub auth/repo bootstrap | ✗ | — | None verified on this host |
| Vercel CLI global install | Vercel link/env/deploy | ✗ | — | `npx vercel@latest` |
| Vercel authenticated session | Vercel link/env/deploy | ✗ in current shell context | — | Token-based non-interactive auth path |

**Missing dependencies with no fallback:**
- `gh` is not installed on this host, and no verified replacement aligned with D-03 was confirmed in this session. [VERIFIED: local CLI probe]

**Missing dependencies with fallback:**
- Global `vercel` install is missing, but `npx vercel@latest` works. [VERIFIED: local CLI probe] [VERIFIED: npm registry]
- Current Vercel auth session is missing, but CLI supports token-based execution flags. [VERIFIED: Vercel CLI help 52.0.0]

## Validation Architecture

### Test Framework
| Property | Value |
|----------|-------|
| Framework | Python `unittest` on Python 3.11.15. [VERIFIED: local CLI probe] |
| Config file | none detected. [VERIFIED: repository glob] |
| Quick run command | `python -m unittest tests.test_approved_delivery_pipeline_cli tests.test_project_delivery_pipeline_resume -v` [VERIFIED: repository files] |
| Full suite command | `python -m unittest discover -s tests -p 'test_*.py' -v` [VERIFIED: repository files] [ASSUMED] |

### Phase Requirements → Test Map
| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| SHIP-01/02/03 | Repo creation/attach, code sync, persisted repo+branch+run linkage | unit/integration | `python -m unittest tests.test_phase11_github_sync -v` | ❌ Wave 0 |
| SHIP-04/05 | Vercel link and env configuration contract | unit/integration | `python -m unittest tests.test_phase11_vercel_flow -v` | ❌ Wave 0 |
| SHIP-06/07/08 | Deploy trigger, outcome reporting, blocked-state handling | unit/integration | `python -m unittest tests.test_phase11_vercel_flow tests.test_approved_delivery_pipeline_cli -v` | ❌/✅ mix |

### Sampling Rate
- **Per task commit:** `python -m unittest tests.test_approved_delivery_pipeline_cli tests.test_project_delivery_pipeline_resume -v` [VERIFIED: repository files] [ASSUMED]
- **Per wave merge:** `python -m unittest discover -s tests -p 'test_*.py' -v` [VERIFIED: repository files] [ASSUMED]
- **Phase gate:** Full suite green before `/gsd-verify-work`. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/.planning/config.json]

### Wave 0 Gaps
- [ ] `tests/test_phase11_github_sync.py` — covers SHIP-01/02/03 plus blocked/retry cases. [ASSUMED]
- [ ] `tests/test_phase11_vercel_flow.py` — covers SHIP-04/05/06/07/08 plus env/deploy evidence. [ASSUMED]
- [ ] Extend `tests/test_approved_delivery_pipeline_cli.py` — lock new wrappers and operator docs. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_approved_delivery_pipeline_cli.py]
- [ ] Extend `tests/test_project_delivery_pipeline_bootstrap.py` — assert new post-bootstrap stages and failure persistence. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_project_delivery_pipeline_bootstrap.py]
- [ ] Extend `scripts/validate_approved_delivery_pipeline.py` coverage — require repo/deploy linkage tokens in authority/status/handoff. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_approved_delivery_pipeline.py]

## Security Domain

### Applicable ASVS Categories
| ASVS Category | Applies | Standard Control |
|---------------|---------|-----------------|
| V2 Authentication | yes | Token-based CLI auth via `gh`/`vercel` and platform-managed credentials, not interactive owner credentials in normal flow. [CITED: https://cli.github.com/manual/gh_auth_login] [VERIFIED: Vercel CLI help 52.0.0] |
| V3 Session Management | no | CLI token/session lifecycle is external platform behavior for this phase. [ASSUMED] |
| V4 Access Control | yes | Constrained command wrappers and approved-project authority gating. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/docs/STATE_CONTRACT.md] [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/.planning/phases/11-github-and-vercel-automation/11-CONTEXT.md] |
| V5 Input Validation | yes | Validate authority schema, required env contract, branch/repo/project identifiers, and subprocess results before state transitions. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/append_approved_delivery_event.py] [VERIFIED: codebase grep] |
| V6 Cryptography | no | No custom cryptography should be introduced in Phase 11. Credential storage hardening is deferred to Phase 12. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/.planning/phases/11-github-and-vercel-automation/11-CONTEXT.md] |

### Known Threat Patterns for this stack
| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Over-broad credential use | Elevation of Privilege | Restrict automation to wrapper-supported repo bootstrap/sync/link/deploy actions only. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/.planning/phases/11-github-and-vercel-automation/11-CONTEXT.md] |
| Command injection through project metadata | Tampering | Pass subprocess arguments as arrays and validate repo/project/env identifiers before invocation. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py] [ASSUMED] |
| Secret leakage into artifacts | Information Disclosure | Store evidence paths and statuses, not raw credential values; treat env values as secrets unless intentionally non-sensitive. [VERIFIED: Vercel CLI help 52.0.0] [ASSUMED] |
| Silent partial deployment | Repudiation | Emit append-only events and latest views for every stage transition and block reason. [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/append_approved_delivery_event.py] [VERIFIED: /c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/render_approved_delivery_status.py] |

## Sources

### Primary (HIGH confidence)
- `https://cli.github.com/manual/gh_auth_login` - GitHub CLI auth modes, `--with-token`, `GH_TOKEN`, hostname handling
- `https://cli.github.com/manual/gh_repo_create` - GitHub repo create flags, source/push/remote flow, default branch note
- `https://api.github.com/repos/cli/cli/releases/latest` - Latest GitHub CLI release version/date
- Local Vercel CLI 52.0.0 help output - `vercel`, `vercel link`, `vercel env`, `vercel env add`, `vercel env pull`, `vercel deploy`
- NPM registry (`npm view vercel version time.modified time --json`) - latest Vercel CLI package version/date
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/start_approved_project_delivery.py` - existing pipeline stages, blocking, resume, subprocess orchestration
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/render_approved_delivery_status.py` - latest-view rendering contract
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/scripts/validate_approved_delivery_pipeline.py` - cross-link validation contract
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_approved_delivery_pipeline_cli.py` - wrapper and operator-flow expectations
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_project_delivery_pipeline_bootstrap.py` - blocked-state and handoff persistence patterns
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/tests/test_project_delivery_pipeline_resume.py` - resume semantics
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/docs/OPERATIONS.md` - operator workflow requirements
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/docs/STATE_CONTRACT.md` - governance/write-boundary constraints
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/docs/platform/standalone-saas-template-contract.md` - existing deploy-related identity contract
- `/c/Users/42236/Desktop/dev/profit-corp-hermes/.planning/config.json` - nyquist validation enabled

### Secondary (MEDIUM confidence)
- Web search to official GitHub/Vercel docs domains for current 2026 documentation discovery. [VERIFIED: web search session]

### Tertiary (LOW confidence)
- Any schema naming, file-splitting, or exact block-reason naming proposals marked `[ASSUMED]`

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - GitHub CLI and Vercel CLI capabilities were verified from official/manual help and current release data. [CITED: https://cli.github.com/manual/gh_repo_create] [VERIFIED: Vercel CLI help 52.0.0]
- Architecture: MEDIUM - The repo’s Phase 10 patterns are clear, but exact Phase 11 schema/stage names still need planning decisions. [VERIFIED: codebase grep] [ASSUMED]
- Pitfalls: MEDIUM - Most pipeline risks were grounded in current environment and existing blocked-state design, but some naming recommendations are still assumptions. [VERIFIED: local CLI probe] [ASSUMED]

**Research date:** 2026-04-27
**Valid until:** 2026-05-04
