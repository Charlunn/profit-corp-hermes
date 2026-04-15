# skills（外置 skill 目录）

这个目录用于放你后续引入或自定义的外置 skills（不限类型）。

## 建议结构
- `skills/<skill-name>/`
  - `README.md`（用途、输入、输出、DoD）
  - `examples/`（可选）
  - `notes.md`（可选）

## 约定
- 优先使用 `kebab-case` 命名。
- 每个 skill 至少写明：适用场景、非适用场景、输入要求、输出契约。
- 与仓库规范冲突时，以 `docs/standards/engineering-playbook-v0.2.md` 为准。

## 中立化 skills
- [中立化 skills 索引](normalized/INDEX.md)
- [Orchestrator 统一入口](normalized/orchestrator-workflow.md)

### Core
- [feature-planning](normalized/feature-planning.md)
- [bugfix-safety](normalized/bugfix-safety.md)
- [release-readiness](normalized/release-readiness.md)
- [observability-check](normalized/observability-check.md)
- [migration-safety](normalized/migration-safety.md)

### Git / Version Management
- [git-safe-branch-flow](normalized/git-safe-branch-flow.md)
- [git-auto-commit-policy](normalized/git-auto-commit-policy.md)
- [cn-commit-message-writer](normalized/cn-commit-message-writer.md)
- [rollback-decision-policy](normalized/rollback-decision-policy.md)

### Testing Workflow
- [test-strategy-planner](normalized/test-strategy-planner.md)
- [regression-planner](normalized/regression-planner.md)
- [flaky-test-triage](normalized/flaky-test-triage.md)
- [release-verification](normalized/release-verification.md)

### UX / Interaction
- [ux-attention-audit](normalized/ux-attention-audit.md)
- [interaction-logic-validator](normalized/interaction-logic-validator.md)
- [accessibility-contract-check](normalized/accessibility-contract-check.md)
- [information-hierarchy-optimizer](normalized/information-hierarchy-optimizer.md)
- [usability-test-generator](normalized/usability-test-generator.md)
