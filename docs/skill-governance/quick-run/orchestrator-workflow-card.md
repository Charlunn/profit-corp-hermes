# Orchestrator 快速运行卡（Quick Run）

## 1) 一句启动
“按 orchestrator-workflow 跑完整流程：设计 -> 开发 -> 测试 -> 版本管理 -> 发布准备。”

## 2) 最小输入
- goal
- task_type
- risk
- surface
- 约束条件（时间/兼容/合规）

### 模板快捷入口
- [Orchestrator 输入模板](../templates/orchestrator-input-template-v0.2.md)
- [阶段交接模板](../templates/stage-handoff-template-v0.2.md)
- [最终交付模板](../templates/final-delivery-template-v0.2.md)

## 3) 执行顺序（固定）
1. Design
2. Development
3. Testing
4. Git Versioning
5. Release Readiness

## 4) 阶段硬规则
- 每阶段都要输出 handoff。
- gate_decision=FAIL 时禁止进入下一阶段。
- 发布前必须通过发布清单硬门禁。

## 5) 最终应交付
- 全流程阶段报告
- 测试证据
- 提交记录（含中文结构化 message）
- 发布建议与回滚路径

主文档：`../../../skills/library/normalized/orchestrator-workflow.md`
