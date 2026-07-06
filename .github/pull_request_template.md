## 变更类型

- [ ] Bug 修复
- [ ] 文档打磨
- [ ] 测试补充
- [ ] 工程配置
- [ ] 功能改动

## 变更说明

请说明本次改动解决了什么问题，以及为什么需要这样改。

## 验证结果

- [ ] `uv run ruff check .`
- [ ] `uv run pyright`
- [ ] `uv run pytest`
- [ ] `docker compose config --quiet`

如果没有运行某项检查，请说明原因。

## 演示影响

- [ ] 不影响现有演示流程
- [ ] 已同步更新 README 或 `docs/`
- [ ] 涉及接口变更，已更新演示脚本或检查清单

## 安全检查

- [ ] 未提交 `.env`、API Key、私有仓库路径或本地索引数据
- [ ] 诊断输出不会泄露密钥
- [ ] 写操作或 Agent 接口仍符合 `CODEPILOT_API_KEY` 保护策略
