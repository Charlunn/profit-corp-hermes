# Engineering Playbook v0.2

> 目标：让不同 AI 在不同微型 SaaS 项目中的代码与交付物具备一致风格、可调试性与可维护性。

## 1) 分层与依赖方向（Hard Gate）

### 强制分层
- `app`：接口层/路由层/控制层
- `domain`：业务规则与领域逻辑
- `infrastructure`：数据库、外部服务、消息、缓存

### 依赖方向
- 只允许：`app -> domain -> infrastructure`
- 禁止：`domain -> app`、`infrastructure -> domain` 反向耦合、`app` 跳过 `domain` 直连基础设施（除纯透传场景并需说明）

## 2) 命名与目录规范（Hard Gate）
- 文件统一 `kebab-case`
- 函数/变量统一 `camelCase`
- 类型/类统一 `PascalCase`
- 同一业务概念在全仓使用同一命名，不得同义混用
- 对外 API、事件名、错误码必须可预测且可检索
- 禁止使用模糊命名（如 `data2`、`tmpFinal`、`maybeFix`）

## 3) Lint / Format / Type-check（Hard Gate）
- PR 前必须通过：lint + format + type-check
- 禁止通过临时关闭规则绕过检查
- 未使用变量、无效 import、隐式 any（若技术栈支持）视为阻断项

## 4) 日志规范（Hard Gate）

### 结构化字段（最小集合）
- `timestamp`
- `level`
- `service`
- `env`
- `trace_id`
- `request_id`
- `module`
- `action`
- `result`
- `duration_ms`
- `error_code`（失败时必填）

### 等级语义
- `debug`：开发诊断信息
- `info`：关键业务流程节点
- `warn`：可恢复异常/业务失败
- `error`：系统错误或需要人工介入

### 安全要求
- 禁止输出敏感信息（密码、密钥、token、完整支付信息）

## 5) 错误处理与错误码（Hard Gate）
- 业务错误与系统错误分离
- 错误码要稳定可引用，支持排查与告警聚合
- 面向用户的提示与内部诊断信息分离

## 6) 测试与质量门禁（Hard Gate）
- 新功能至少包含：1 条主路径 + 1 条失败路径验证
- Bug 修复必须包含回归验证证据
- 高风险改动（支付、鉴权、迁移）优先要求集成级验证

## 7) PR、发布与回滚（Hard Gate）
- PR 必须包含：变更摘要、影响面、风险、验证证据、回滚步骤
- 发布前必须完成一页纸检查清单：`docs/release/release-checklist-one-page.md`
- 发生线上异常时优先止血，再做根因修复

## 8) 调试 Runbook（Soft Gate，关键路径建议 Hard）
- 关键模块应具备“先看什么日志、再看什么指标、再看什么依赖”的排查顺序
- Runbook 要能让不了解上下文的维护者快速接手

## 9) AI 读写规则（MUST / SHOULD / NEVER）
### MUST
- 先按 `routing manifest` 路由，再选择 skill。
- 默认薄加载，满足升级条件才厚加载。
- 输出必须符合 skill 的 Output Contract。
- 任务结束前必须过发布清单硬门禁。

### SHOULD
- 优先 small diff，避免不相关重构。
- 注释写“为什么”，并与实现同步更新。
- 关键变更同步更新最小文档集。

### NEVER
- 未验证就宣称“完成”。
- 通过关闭规则绕过质量门禁。
- 在日志或注释中暴露敏感信息。
- 使用模糊结论词（如“应该可以”“大概没问题”“理论上可行”）替代验证结论。

## 10) 注释规范（中文）
### 语言规则
- 业务注释统一中文。
- 外部协议/标准名可保留英文原词。

### 颗粒度规则
- **模块级**：说明职责、边界、关键依赖。
- **函数级**：说明输入/输出/副作用/约束。
- **关键逻辑点**：仅在复杂分支、边界条件、业务规则出处处写注释。

### 反模式
- 为每一行代码写重复性注释。
- 代码变更后不更新注释。
- 用注释替代清晰命名与结构。

## 11) 最小文档集要求
每个项目至少维护：
- `README`：启动、目录、常用命令、环境变量概览
- `RUNBOOK`：故障排查步骤、止血策略、回滚入口
- `CHANGELOG`：版本变更与影响摘要
- `ARCHITECTURE`：分层说明、关键链路与边界

> 对小项目可精简篇幅，但四类文档不可缺失。

## 12) Skill 对齐要求
- 所有 skill 必须遵循统一模板：`docs/templates/skill-doc-template-v0.2.md`
- 所有 skill 的 DoD 不得与本手册 Hard Gate 冲突
- 规则冲突时优先级：**Playbook Hard Gate > Skill 文档 > 任务临时约定**

## 13) 版本治理
- 当前规范版本：`v0.2`
- 版本变更策略：
  - 修订（patch）：仅措辞澄清，不改门禁语义
  - 次版本（minor）：新增规则或新增模板字段
  - 主版本（major）：门禁语义变更或流程重构
- 每次版本升级需记录：变更点、动机、影响范围、迁移建议

## 14) 范围声明
- 当前为文档规范，不绑定具体脚本或框架
- 自动化落地（v0.3+）须以本手册为基线扩展
