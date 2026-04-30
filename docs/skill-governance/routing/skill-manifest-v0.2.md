# Skill Manifest & Routing v0.2（按需导入 + 动态卸载）

> 目标：避免每次全量导入所有规范；根据任务类型按需加载 1~3 个 skill，并在任务阶段结束后主动卸载无关上下文。

## 1) Manifest 元数据字段
每个 skill 至少定义：
- `name`：skill 名称
- `version`：版本号
- `tags`：能力标签（feature/bug/logging/payment/auth/refactor/release）
- `triggers`：触发关键词或任务信号
- `inputs_required`：必需输入
- `output_contract`：输出结构
- `dependencies`：依赖 skill
- `cost_level`：low/med/high（上下文成本）
- `unload_when`：软卸载触发条件（如“阶段完成/证据落盘后”）
- `handoff_minimum`：硬卸载交接最小字段

## 2) 路由输入标签
先给任务打 3 类标签：
- `task_type`: feature | bug | payment | refactor | release
- `risk`: low | med | high
- `surface`: ui | api | db | infra | multi

## 3) 基础路由决策表
- feature + (any) -> `feature-to-pr`
- bug + (any) -> `bugfix-safety`
- (any) + logging concern -> `logging-convention`
- payment + api/db -> `feature-to-pr` + `bugfix-safety`（若为修复）+ `logging-convention`
- release -> 发布检查清单必跑

## 4) 动态加载层级
### L0（摘要加载，默认）
仅加载：
- 适用/非适用场景
- 输入要求
- 输出契约
- DoD

### L1（单 skill 全文）
触发条件：
- risk = med/high
- 任务存在边界不清或多约束冲突

### L2（跨 skill + playbook）
触发条件：
- risk = high
- surface = multi
- 涉及 payment/auth/migration/release

## 5) 动态卸载规则（控制上下文）
### 软卸载（同会话）
- 每完成一个阶段，保留“阶段摘要 + 门禁状态 + 风险项”。
- 删除阶段细节引用，不再继续携带全文 skill 细则。

### 硬卸载（新会话）
- 使用简化 handoff 开新会话，仅带：
  - 当前目标
  - 已完成项
  - 未决风险
  - 下一步动作
- 不重复注入历史全过程文本。

### handoff_minimum 建议结构
- `goal`: 当前目标（一句话）
- `done`: 已完成事项（最多 5 条）
- `open_risks`: 未决风险（最多 3 条）
- `next_action`: 下一步唯一动作
- `gates_status`: 硬门禁状态（pass/fail + 原因）

## 6) 冲突处理规则
- 同时命中多个 skill 时，最多加载 3 个
- 优先级：安全类（bugfix/logging）> 交付类（feature-to-pr）
- 超过 3 个时，输出“最小 skill 集合 + 未加载项风险说明”

## 7) 全局兜底（永远执行）
无论路由结果如何，必须执行：
- `docs/release/release-checklist-one-page.md` 中的硬门禁

## 8) 路由输出标准
每次路由结果固定输出：
1. 任务标签
2. 命中 skill 列表
3. 加载级别（L0/L1/L2）
4. 卸载策略（软卸载/硬卸载）
5. 未加载风险提醒
6. 最终验收入口（发布清单）

## 9) 版本与边界
- 当前规范版本：`v0.2`
- 当前为文档规范，不绑定具体脚本或框架
- v0.3 可将本 manifest 转为可执行配置（yaml/json + 自动校验）
