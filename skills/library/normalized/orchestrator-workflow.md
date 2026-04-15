# Skill: orchestrator-workflow（中立版）

- 名称：orchestrator-workflow
- 版本：v0.2
- 目标：作为统一入口，串联全流程 skill：设计 -> 开发 -> 测试 -> Git 版本管理 -> 发布准备。

## 适用场景
- 新项目启动或中大型功能迭代
- 希望 AI 端到端按规范执行并输出可验收产物

## 非适用场景
- 单行修复或纯文案改动
- 不需要全流程管理的一次性临时任务

## 输入要求
- `goal`：本次目标（一句话）
- `task_type`：feature/bug/release 等
- `risk`：low/med/high
- `surface`：ui/api/db/infra/multi
- 约束：时间、兼容性、合规边界

## 阶段顺序（固定）
1. 设计阶段（Design）
2. 开发阶段（Development）
3. 测试阶段（Testing）
4. 版本管理阶段（Git Versioning）
5. 发布准备阶段（Release Readiness）

> 不允许跳过测试与版本管理阶段直接进入发布准备。

## 阶段编排与门禁
### 1) 设计阶段
- 参考：`feature-planning` + 相关 UX skill
- 产出：范围定义、影响面、风险清单、验收标准
- 门禁：范围清晰且可验证（PASS）

### 2) 开发阶段
- 参考：核心实现类 skill（feature/bug/logging）
- 产出：最小可合并变更、日志/注释符合规范
- 门禁：变更不越界，结构与分层符合规范（PASS）

### 3) 测试阶段
- 参考：`test-strategy-planner` / `regression-planner` / `flaky-test-triage`
- 产出：主路径+失败路径证据、回归结果
- 门禁：关键验证通过，失败项有处置（PASS）

### 4) 版本管理阶段
- 参考：`git-safe-branch-flow` / `git-auto-commit-policy` / `cn-commit-message-writer`
- 产出：结构化提交记录、回滚指令
- 门禁：仅在允许分支提交，提交前门禁全绿（PASS）

### 5) 发布准备阶段
- 参考：`release-readiness` / `release-verification`
- 产出：发布建议、风险等级、止血与回滚路径
- 门禁：发布清单硬门禁全部通过（PASS）

## 统一交接格式（handoff）
每阶段结束必须输出：
- `stage`:
- `inputs_received`:
- `work_completed`:
- `artifacts`:
- `risks_open`:
- `gate_decision`: PASS | FAIL
- `next_stage`:

## 失败处理
- 任一阶段 FAIL：停止进入下一阶段，返回上一阶段补齐缺口。
- 对高风险任务（risk=high）：必须追加 `release-verification`。

## 输出契约
- 全流程阶段报告
- 关键产物链接（设计、测试证据、提交记录、发布检查）
- 最终决策建议（可发布/阻断）

## DoD
- [ ] 五阶段全部执行且有 PASS/FAIL 记录
- [ ] 所有硬门禁通过或有明确阻断理由
- [ ] 产物可复盘、可回滚

## 风险与回滚
- 风险：跳步执行导致后期返工
- 回滚：回退到最近 FAIL 前阶段，修复后重跑后续阶段
