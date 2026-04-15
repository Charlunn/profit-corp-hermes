# 规范变更日志（Spec Changelog）

## v0.2 (2026-04-14)
### 变更点
- 引入 AI 读写规则（MUST/SHOULD/NEVER）。
- 新增中文注释规范与注释颗粒度要求。
- 新增最小文档集要求（README/RUNBOOK/CHANGELOG/ARCHITECTURE）。
- 引入动态加载层级（L0/L1/L2）与动态卸载策略（软卸载/硬卸载）。
- 增加版本治理规则与冲突优先级规则。

### 动机
- 降低多 AI 协作时产出不一致与上下文膨胀问题。

### 影响范围
- Playbook、routing manifest、skill 模板、导航文档。

### 迁移建议
- 统一使用 v0.2 文件入口。
- 新增或更新 skill 时强制使用 v0.2 模板与链接。

## v0.1 (2026-04-14)
### 变更点
- 初始化工程规范骨架。
- 产出 3 个核心 skill 文档。
- 产出发布一页纸清单与路由 manifest 初版。
