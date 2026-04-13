# Skill: read_shareholder_announcements

## When to Use
- 会话开始时需要同步股东级公告。
- 本地策略与公告可能冲突时，需要以公告为准。

## Procedure
1. 读取 `assets/shared/SHAREHOLDER_ANNOUNCEMENTS.md`。
2. 提炼最新公告（按日期从新到旧）。
3. 标记对当前任务有影响的约束。

## Verification
- 输出包含最新公告日期。
- 输出包含至少 1 条公告约束。
- 不修改公告板文件。
