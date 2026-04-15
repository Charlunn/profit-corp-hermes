# skill

这个仓库用于沉淀微型 SaaS 场景下的 AI 工程化规范，目标是让不同 AI 产出的应用在结构、日志、调试与交付上保持一致。

## 当前规范版本
- `v0.2`

## 文档导航
- [START HERE](docs/START-HERE.md)
- [Orchestrator Workflow](skills/normalized/orchestrator-workflow.md)
- [Orchestrator 快速运行卡](docs/quick-run/orchestrator-workflow-card.md)
- [文档总入口](docs/README.md)
- [Engineering Playbook](docs/standards/engineering-playbook-v0.2.md)
- 核心 skills
  - [feature-to-pr](docs/skills/feature-to-pr.md)
  - [bugfix-safety](docs/skills/bugfix-safety.md)
  - [logging-convention](docs/skills/logging-convention.md)
- [发布一页纸检查清单](docs/release/release-checklist-one-page.md)
- [按需导入路由与 manifest](docs/routing/skill-manifest-v0.2.md)
- [Skill 模板](docs/templates/skill-doc-template-v0.2.md)
- [术语表](docs/glossary.md)

## 规范 skills
- [skills 目录说明](skills/README.md)
- [中立化 skills](skills/normalized/)

### 快速能力覆盖
- Git 版本管理（安全分支、自动提交策略、中文 commit message、回滚决策）
- 测试流程（策略规划、回归规划、flaky 排查、发布验证）
- UX 交互（注意力审计、状态逻辑、可访问性、信息层级、可用性测试）

## 设计原则
- 文档先行：先统一标准，再做自动化
- 小步可合并：优先 small diff，降低回归
- 全局兜底：不管路由哪个 skill，最终都过硬门禁
- 动态加载与卸载：按 L0/L1/L2 加载，阶段完成后主动收缩上下文
- 中文注释规范：强调“为什么”，控制注释颗粒度，保持可维护
