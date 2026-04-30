# 文档中心（v0.2）

这个目录是仓库的规范单一事实来源（Single Source of Truth），用于统一不同 AI 在微型 SaaS 项目中的产出风格、调试方式与交付标准。

## 快速导航（按任务）
- 首次进入或切换任务：先看 [START HERE](START-HERE.md)
- 全流程统一入口：看 [Orchestrator Workflow](../../skills/library/normalized/orchestrator-workflow.md)
- 一屏执行卡：看 [Orchestrator Quick Run](quick-run/orchestrator-workflow-card.md)
- 我在做新功能：先看 [feature-to-pr](skills/feature-to-pr.md)
- 我在修线上/测试 bug：先看 [bugfix-safety](skills/bugfix-safety.md)
- 我在补可观测性：先看 [logging-convention](skills/logging-convention.md)
- 我要合并/发布：看 [发布一页纸检查清单](release/release-checklist-one-page.md)

## 路由速查卡（10 秒决策）
| 任务类型 | 默认 skill | 加载级别 | 必跑检查 |
| --- | --- | --- | --- |
| feature | feature-to-pr | L0，必要时 L1 | 发布清单硬门禁 |
| bug | bugfix-safety | L1 起步，复杂到 L2 | 发布清单硬门禁 |
| logging | logging-convention | L0/L1 | 发布清单硬门禁 |
| payment/auth/migration | feature-to-pr + 安全类 | L2 | 发布清单硬门禁 |
| release | 以发布清单为主 | L1/L2 | 发布清单硬门禁 |

## 阅读顺序
1. [START HERE](START-HERE.md)
2. [工程总手册](standards/engineering-playbook-v0.2.md)
3. [Skill 文档模板](templates/skill-doc-template-v0.2.md)
4. 核心 skills
   - [feature-to-pr](skills/feature-to-pr.md)
   - [bugfix-safety](skills/bugfix-safety.md)
   - [logging-convention](skills/logging-convention.md)
5. [发布一页纸检查清单](release/release-checklist-one-page.md)
6. [按需导入路由与 manifest](routing/skill-manifest-v0.2.md)
7. [术语表](glossary.md)

## 规范技能入口
- [中立化 skills 目录](../../skills/library/normalized/)

## Orchestrator 模板入口
- [Orchestrator 输入模板](templates/orchestrator-input-template-v0.2.md)
- [阶段交接模板](templates/stage-handoff-template-v0.2.md)
- [最终交付模板](templates/final-delivery-template-v0.2.md)

## 上下文控制策略
- 默认 L0 摘要加载；复杂任务升级到 L1/L2。
- 阶段结束执行软卸载，仅保留阶段摘要和门禁状态。
- 长链路任务建议硬卸载（新会话 + 精简 handoff）。

## 版本与范围
- 当前版本：`v0.2`
- 范围：文档与规范（不含自动化脚本、不含 CI 强制集成）
- 目标：提升一致性、可调试性、可维护性，降低多人/多 AI 协作成本。
