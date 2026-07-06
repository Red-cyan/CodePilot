# 安全说明

这份文档说明 CodePilot 当前的安全边界和维护约定。项目当前定位是可演示的后端 MVP，不是完整生产级多租户系统。

## 支持范围

当前安全策略覆盖 `main` 分支上的最新版本。

## 密钥和配置

- `.env`、`.env.*` 不应提交到 Git。
- `.env.example` 只保留空值或示例值。
- `DEEPSEEK_API_KEY` 只应存在于本地环境或部署环境。
- `CODEPILOT_API_KEY` 用于保护写操作、代码检索和 Agent 接口，不应写入 README、Issue、PR 或日志。
- `/diagnostics` 只能展示模型是否配置，不能返回真实密钥。

## 数据边界

CodePilot 会读取并索引用户导入的代码仓库。需要注意：

- `storage/` 保存本地仓库状态、索引和运行历史，已被 `.gitignore` 排除。
- 运行历史可能包含代码片段和文件路径，不应提交到公开仓库。
- 删除仓库接口只删除 CodePilot 内部记录和索引状态，不删除磁盘上的源码目录。
- 文件读取接口必须限制在仓库根目录内，避免路径穿越。

## API 访问边界

默认情况下 `CODEPILOT_API_KEY` 为空，适合本地演示和调试。

如果配置了 `CODEPILOT_API_KEY`：

- 仓库导入、索引、重新索引、删除需要请求头 `X-CodePilot-Api-Key`。
- 代码检索、Chat、分析、Review 和生成类接口需要请求头 `X-CodePilot-Api-Key`。
- 健康检查、系统诊断、仓库列表、源码浏览、符号查看和运行历史查询保持公开，方便演示和排查。

如果部署到公网，建议在反向代理、网络访问控制或更完整的用户体系中进一步保护只读接口。

## 依赖和供应链

提交前建议运行：

```powershell
uv run ruff check .
uv run pyright
uv run pytest
docker compose config --quiet
```

不要为了演示绕过 CI。依赖升级需要关注 FastAPI、Pydantic、httpx、GitPython、SQLAlchemy 和 Docker 镜像的安全公告。

## 漏洞反馈

如果发现安全问题，请不要在公开 Issue 中粘贴真实 API Key、私有仓库路径、完整源码或敏感日志。

建议反馈内容：

- 问题描述和影响范围。
- 可复现步骤。
- 是否需要配置 `CODEPILOT_API_KEY` 或 `DEEPSEEK_API_KEY`。
- 关键响应状态码和 `X-Request-Id`。
- 脱敏后的日志或请求样例。

当前项目用于求职展示，没有公开安全响应 SLA。维护者会优先处理密钥泄露、路径穿越、任意文件读取、未授权写操作和敏感信息输出问题。
