# 阶段交接模板（v0.2）

> 每个阶段结束必须填写，供下一阶段继续执行。
> specialist handoff 必须严格使用 validator 定义的固定 9 段顺序；旧 6 段格式无效。
> `Changed Files`、`User Visible Behavior`、`Pain Point Mapping` 为必填，不能为空。

## 1) Stage Summary
- `run_id`:
- `role`:
- `stage`:
- `scope_status`: approved-brief-only | in-scope | scope-reopen-requested | blocked
- `summary`:

## 2) Outputs Produced
- 产物 1：
- 产物 2：
- 产物 3：

## 3) Evidence Links
- 链接 1：
- 链接 2：
- 链接 3：

## 4) Changed Files
- `path`: 说明本阶段实际变更的文件
- `path`: 不允许留空

## 5) User Visible Behavior
- 用户/操作员现在可以看到或完成什么
- 不允许只写“not recorded”或留空

## 6) Pain Point Mapping
- 痛点信号：
- 本阶段响应：

## 7) Gate Decision
- `gate_decision`: PASS | FAIL
- `reason`:

## 8) Open Risks
- 风险项：
- 影响范围：
- 缓解建议：

## 9) Next Stage Input
- `next_stage`: design | development | testing | git versioning | release readiness | none
- 下一阶段需要的输入：
- 注意事项：
