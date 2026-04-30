# Phase 9: Claude Code Delivery Team Orchestration - Pattern Map

**Mapped:** 2026-04-27
**Files analyzed:** 10 requested inputs + implied planning artifacts
**Analogs found:** 8 / 10 requested inputs exist; pattern coverage mapped for 7 likely target artifacts

## File Classification

| New/Modified File | Role | Data Flow | Closest Analog | Match Quality |
|---|---|---|---|---|
| `docs/skill-governance/templates/orchestrator-input-template-v0.2.md` | contract | request-response | `docs/skill-governance/templates/orchestrator-input-template-v0.2.md` | exact |
| `docs/skill-governance/templates/stage-handoff-template-v0.2.md` | contract | event-driven | `docs/skill-governance/templates/stage-handoff-template-v0.2.md` | exact |
| `docs/skill-governance/templates/final-delivery-template-v0.2.md` | contract | event-driven | `docs/skill-governance/templates/final-delivery-template-v0.2.md` | exact |
| `skills/library/normalized/orchestrator-workflow.md` | contract | batch | `skills/library/normalized/orchestrator-workflow.md` | exact |
| `scripts/start_delivery_run.py` | utility | batch | `scripts/instantiate_template_project.py` | exact |
| `scripts/append_delivery_event.py` | utility | event-driven | `scripts/governance_common.py` | exact |
| `scripts/render_delivery_status.py` | utility | event-driven | `scripts/render_governance_status.py` | exact |
| `scripts/request_scope_reopen.py` | utility | governed action | `scripts/request_governance_approval.py` | exact |
| `scripts/validate_delivery_handoff.py` | utility | validation | `scripts/check_template_conformance.py` | exact |
| `orchestration/cron/commands.sh` | utility | command entry | `orchestration/cron/commands.sh` | exact |
| `assets/workspaces/ceo/AGENTS.md` | contract | orchestration | `assets/workspaces/ceo/AGENTS.md` | exact |
| `tests/test_delivery_orchestration_contract.py` | test | contract lock | `tests/test_template_contract.py` | exact |
| `tests/test_delivery_handoff_contract.py` | test | contract lock | `tests/test_template_contract.py` | exact |
| `tests/test_start_delivery_run.py` | test | workspace fixture | `tests/test_instantiate_template_project.py` | exact |
| `tests/test_delivery_events.py` | test | event/status validation | `tests/test_check_template_conformance.py` | role-match |
| `tests/test_scope_reopen_flow.py` | test | governance integration | `tests/test_check_template_conformance.py` | role-match |
| `tests/test_delivery_run_replay.py` | test | artifact replay | `tests/test_derived_packages.py` | flow-match |

## Pattern Assignments

### `.planning/phases/09-claude-code-delivery-team-orchestration/09-PLAN.md` (config, request-response)

**Analog:** `docs/MULTI_PROFILE_COORDINATION.md`

**Delegation contract pattern** (lines 16-32):
```markdown
## Delegation Template
```python
delegate_task(
  goal="<clear target>",
  context="<input files + expected output files + acceptance criteria>",
  toolsets=["terminal", "file", "web"],
  max_iterations=50
)
```

并行模板：
```python
delegate_task(tasks=[
  {"goal": "...", "context": "...", "toolsets": ["web", "file"]},
  {"goal": "...", "context": "...", "toolsets": ["terminal", "file"]}
])
```
```

**Ownership / sequencing pattern** (lines 39-49):
```markdown
## Artifact Ownership
- Scout -> `assets/shared/PAIN_POINTS.md`
- CMO -> `assets/shared/MARKET_PLAN.md`
- Arch -> `assets/shared/TECH_SPEC.md`
- CEO -> 决策记录写入 `assets/shared/CORP_CULTURE.md`
- Accountant -> 审计输出 + `manage_finance.py` 执行结果

## Concurrency Safety
- `assets/shared/manage_finance.py` 已包含文件锁。
- 避免多个角色并发写同一业务文档；由 CEO 控制写入时序。
```

**Copy for Phase 9:** structure plan tasks as explicit `goal + context + expected output + acceptance criteria`, with CEO-owned sequencing and no concurrent writes to the same artifact.

---

### `.planning/phases/09-claude-code-delivery-team-orchestration/09-DELIVERY.md` (config, batch)

**Analog:** `orchestration/cron/daily_pipeline.prompt.md`

**Stage-by-stage output contract** (lines 2-20):
```markdown
你是 CEO profile 的定时调度器。目标：执行完整 Profit-Corp 日常流水线并给出最终决策摘要。

执行顺序：
1. Scout 阶段
   - 读取 `assets/shared/TEMPLATES.md`
   - 产出/更新 `assets/shared/PAIN_POINTS.md`
   - 必须给出 Top3 pain points + 推荐1
2. CMO 阶段
   - 读取 `assets/shared/PAIN_POINTS.md`
   - 产出/更新 `assets/shared/MARKET_PLAN.md`
3. Architect 阶段
   - 读取 `assets/shared/MARKET_PLAN.md`
   - 产出/更新 `assets/shared/TECH_SPEC.md`
4. CEO 决策阶段
   - 读取 `assets/shared/LEDGER.json`、`MARKET_PLAN.md`、`TECH_SPEC.md`
   - 做 GO/NO-GO，并写入 `assets/shared/CORP_CULTURE.md`
5. Accountant 审计阶段
   - 运行 `python3 assets/shared/manage_finance.py audit`
   - 输出 treasury、关键风险、下一步建议
```

**Summary status pattern** (lines 22-26):
```markdown
约束：
- 默认中文输出。
- 任何风险结论必须带证据（文件或数字）。
- 如果所有指标健康，摘要第一行写“Daily pipeline completed: HEALTHY”。
- 如果存在重大风险，摘要第一行写“Daily pipeline completed: ACTION REQUIRED”。
```

**Copy for Phase 9:** define delivery output by ordered stages, mandatory evidence, and a one-line top status for machine/human handoff.

---

### `.planning/phases/09-claude-code-delivery-team-orchestration/09-HANDOFF.md` (config, event-driven)

**Analog:** `assets/workspaces/ceo/AGENTS.md`

**Orchestration rule block** (lines 12-16):
```markdown
## Hermes-native Orchestration Rules
- 多智能体协作统一使用 `delegate_task`，禁止使用 OpenCLAW 的 `sessions_*` 语法。
- 委派时必须传完整上下文（目标、输入文件、输出文件、验收标准）。
- 允许并行委派（Scout/CMO 可并发），结果回收后再触发 Arch 与 Accountant。
```

**Parallel + single-task examples** (lines 17-39):
```python
# 并行研究
delegate_task(tasks=[
  {
    "goal": "Find 3 monetizable pain points in last 48h",
    "context": "Read assets/shared/TEMPLATES.md and write assets/shared/PAIN_POINTS.md",
    "toolsets": ["web", "file"]
  },
  {
    "goal": "Turn best lead into market case",
    "context": "Read assets/shared/PAIN_POINTS.md and draft assets/shared/MARKET_PLAN.md",
    "toolsets": ["web", "file"]
  }
])

# 单任务委派
delegate_task(
  goal="Run finance audit and summarize risks",
  context="Execute python3 assets/shared/manage_finance.py audit and report treasury/agent risks",
  toolsets=["terminal", "file"]
)
```

**Copy for Phase 9:** handoff documents should include exact delegation payloads, not prose-only guidance.

---

### `docs/CLAUDE_CODE_DELIVERY_TEAM_ORCHESTRATION.md` (config, request-response)

**Analog:** `docs/OPERATIONS.md`

**Checklist pattern** (lines 2-20):
```markdown
## Daily operator checklist
1. Ensure cron baseline is healthy:
   ```bash
   bash orchestration/cron/commands.sh ensure
   bash orchestration/cron/commands.sh status
   ```
2. Verify scheduled jobs and recent outputs:
   ```bash
   hermes -p ceo cron list
   ```
3. Run regression smoke checks:
   ```bash
   bash scripts/smoke_test_pipeline.sh
   ```
4. Verify financial state integrity:
   ```bash
   python3 -m py_compile assets/shared/manage_finance.py
   ```
```

**Incident response pattern** (lines 22-69):
```markdown
### B) Cron job missing, duplicated, or paused
- One-command recovery path:
  ```bash
  bash scripts/recover_cron.sh
  ```
- Manual controls (when needed):
  ```bash
  bash orchestration/cron/commands.sh ensure
  bash orchestration/cron/commands.sh remove-duplicates
  bash orchestration/cron/commands.sh resume-all
  bash orchestration/cron/commands.sh status
  ```
```

**Copy for Phase 9:** document orchestration as operator checklists plus incident playbooks, not only architecture notes.

---

### `skills/ceo/ceo_delivery_orchestration.md` (utility, event-driven)

**Analog:** `skills/ceo/ceo_new_project.md`

**Skill structure pattern** (lines 0-17):
```markdown
# Skill: ceo_new_project

## When to Use
- 股东发起新项目并需要完整立项流程。

## Procedure
1. 不向股东追问细碎参数，默认由 CEO 自主定义初始假设、目标用户与执行边界。
2. 并行委派 Scout + CMO（`delegate_task(tasks=[...])`），分别产出：
   - `assets/shared/PAIN_POINTS.md`
   - `assets/shared/MARKET_PLAN.md`
3. 回收结果后委派 Arch 产出 `assets/shared/TECH_SPEC.md`。
4. 委派 Accountant 执行审计并回收风险摘要。
5. 由 CEO 输出 GO/NO-GO 与理由，并写入 `assets/shared/CORP_CULTURE.md` 与 `assets/shared/KNOWLEDGE_BASE.md`。

## Verification
- 核心产物文件均更新：`PAIN_POINTS.md`、`MARKET_PLAN.md`、`TECH_SPEC.md`。
- 审计步骤被执行并输出风险摘要。
- CEO 决策记录包含结论、理由和下一步动作。
```

**Secondary analog:** `skills/ceo/ceo_daily_pipeline.md` lines 2-14
```markdown
## Procedure
1. 优先调用 `bash orchestration/cron/commands.sh run-daily`。
2. 若 cron job 不存在，先 `bash orchestration/cron/commands.sh ensure` 后再 run。
3. 回收 Scout/CMO/Arch/Accountant 输出并生成 CEO 摘要。

## Verification
- `run-daily` 成功触发或给出明确失败原因。
- 产物链路有更新或审计输出。
- CEO 摘要包含风险与下一步动作。
```

**Copy for Phase 9:** keep skill docs in `When to Use / Procedure / Verification` format with command-first steps and explicit artifact verification.

---

### `orchestration/cron/delivery_orchestration.prompt.md` (config, batch)

**Analog:** `orchestration/cron/health_check.prompt.md`

**Compact rule pattern** (lines 2-18):
```markdown
你是 Profit-Corp 健康检查任务。

检查项：
1. 读取 `assets/shared/LEDGER.json`
2. 检查 treasury 与各 agent points
3. 检查关键文件是否可访问：
   - `assets/shared/CORP_CULTURE.md`
   - `assets/shared/KNOWLEDGE_BASE.md`

输出规则：
- 若 treasury >= 300 且所有 agent points > 80：仅输出 `[SILENT]`
- 否则输出：
  - 当前 treasury
  - 低分 agent 列表
  - 1-3 条操作建议（按优先级排序）

语言：简体中文。
```

**Copy for Phase 9:** for cron-facing prompts, keep short sections: role, checks, output rules, language.

---

### `scripts/check_delivery_orchestration.sh` (utility, batch)

**Analog:** `scripts/smoke_test_pipeline.sh`

**Shell scaffolding pattern** (lines 0-17):
```bash
#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
FAILED=0
PYTHON_BIN=""

ok() { printf '[smoke] PASS: %s\n' "$*"; }
fail() { printf '[smoke] FAIL: %s\n' "$*"; FAILED=1; }
```

**Reusable checks pattern** (lines 30-47):
```bash
check_file_nonempty() {
  local f="$1"
  if [ -s "$f" ]; then
    ok "file exists and non-empty: $f"
  else
    fail "file missing or empty: $f"
  fi
}

run_check() {
  local label="$1"
  shift
  if "$@" >/dev/null 2>&1; then
    ok "$label"
  else
    fail "$label"
  fi
}
```

**End-of-run verdict pattern** (lines 72-77):
```bash
if [ "$FAILED" -eq 0 ]; then
  printf '\n[smoke] OVERALL: PASS\n'
else
  printf '\n[smoke] OVERALL: FAIL\n'
  exit 1
fi
```

**Secondary analog:** `scripts/recover_cron.sh` lines 5-14
```bash
printf '[recover] Ensuring cron jobs...\n'
bash "$ROOT_DIR/orchestration/cron/commands.sh" ensure

printf '[recover] Resuming known cron jobs...\n'
bash "$ROOT_DIR/orchestration/cron/commands.sh" resume-all || true

printf '[recover] Cron status...\n'
bash "$ROOT_DIR/orchestration/cron/commands.sh" status
```

**Copy for Phase 9:** verification helpers should use explicit PASS/FAIL operator messaging and rerunnable command wrappers.
