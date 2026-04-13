# Skill: check_system_health

## When to Use
- 启动后做系统健康巡检。
- 发现 cron/配置异常后做回归检查。

## Procedure
1. 执行 `bash scripts/smoke_test_pipeline.sh`。
2. 执行 `bash orchestration/cron/commands.sh status`。
3. 输出 PASS/FAIL 与失败项。

## Verification
- smoke 输出可见 `OVERALL` 结果。
- cron status 能返回当前 job 状态。
- 对失败项给出下一步恢复命令。
