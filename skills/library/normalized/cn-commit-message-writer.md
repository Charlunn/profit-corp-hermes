# Skill: cn-commit-message-writer（中立版）

- 名称：cn-commit-message-writer
- 版本：v0.2
- 来源：Conventional Commits（中英文规范）+ 提交质量实践（重写）

## 适用场景
- 需要生成高质量、可追溯的中文 commit message

## 非适用场景
- 无实际代码变更

## 输入要求
- 变更目的（Why）
- 核心改动（What）
- 影响范围与风险（Impact/Risk）

## 执行步骤
1. 选择类型前缀：feat/fix/refactor/test/docs/chore。
2. 生成标题：`type(scope): 中文简述`。
3. 正文补充：背景原因、影响范围、风险与回滚要点。
4. 校验：避免空泛词，确保可复盘。

## 输出契约
- 标题（结构化）
- 正文（中文，含 Why/Impact/Risk）

## DoD
- [ ] 类型与范围准确
- [ ] 中文表达具体可验证
- [ ] 含风险或回滚提示（如适用）

## 风险与回滚
- 风险：消息过于笼统导致后续难追踪
- 回滚：提交后如信息错误，新增修正提交，不改共享历史
