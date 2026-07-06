# CodePilot 当前项目状态

这份文档用于说明 CodePilot 当前已经具备哪些能力、如何验证，以及哪些内容属于后续生产化方向。

## 当前定位

CodePilot 当前是一个可演示的后端 MVP，目标是展示 AI Agent 项目中的工程闭环：

```text
仓库导入 -> 源码解析 -> 索引构建 -> 检索召回 -> LLM 生成 -> 引用追踪 -> 运行历史 -> 系统诊断 -> 容器化部署
```

它适合作为秋招面试中的 AI Agent / 后端工程项目，用来展示工程拆分、测试、配置、安全边界、可观测性和部署意识。

## 已完成能力

- 仓库导入：支持本地路径和 Git 仓库。
- 索引构建：支持源码扫描、chunk 构建、符号解析和跳过原因统计。
- 源码浏览：支持文件树、文件内容读取和符号列表。
- 代码检索：支持 semantic、keyword、symbol 三种检索模式。
- Agent 问答：基于仓库上下文回答问题，并返回 citations。
- 分析能力：支持架构分析、Bug 分析。
- PR Review：输出 score、summary、issues 和 LLM 总结。
- 生成能力：支持 README、API 实现草稿、单元测试草稿。
- 运行历史：记录 Agent 调用类型、工具链路、引用证据和耗时。
- 系统诊断：展示索引规模、模型配置状态、存储状态。
- 请求追踪：响应头返回 `X-Request-Id` 和 `X-Process-Time-Ms`。
- 安全边界：支持可选 `CODEPILOT_API_KEY`。
- 容器化：提供 Dockerfile 和 Docker Compose，包含 API、PostgreSQL/pgvector、Redis。
- CI：覆盖 ruff、pyright、pytest 和 Docker Compose 配置校验。

## 当前验证命令

```powershell
uv run ruff check .
uv run pyright
uv run pytest
docker compose config --quiet
```

当前测试重点覆盖：

- 健康检查和请求追踪。
- 仓库导入、索引、重新索引和删除。
- 可解释索引策略和跳过原因统计。
- 文件树、文件内容和符号浏览。
- 多模式代码检索。
- Chat、分析、Review、生成类 Agent。
- RunStore 运行历史。
- Diagnostics 系统诊断。
- DeepSeek 客户端回退和响应解析。

## 演示建议版本

面试演示时建议使用本地开发启动：

```powershell
uv run uvicorn app.main:app --reload
```

如果 Docker Desktop 已经启动，可以演示：

```powershell
docker compose up --build
```

如果现场网络或 Docker 环境不稳定，优先使用本地启动，并强调 Docker Compose 配置已经通过 `docker compose config --quiet` 校验。

## 明确边界

当前版本没有把所有生产化能力一次做完，主要原因是优先保证 MVP 稳定可演示。

- 当前向量检索使用确定性 embedding，便于离线测试和 CI 稳定。
- 当前持久化使用本地 JSON 文件，便于快速演示和调试。
- PostgreSQL、pgvector、Redis 已在配置和 Compose 中预留，但核心状态尚未迁移到数据库。
- 索引任务当前是同步执行，适合小型仓库演示。
- 当前没有前端工作台，主要通过 Swagger 展示 API 能力。

这些边界可以在面试中主动说明，体现对工程演进路径的判断。

相关架构取舍记录在 `docs/adr/` 中，包括离线优先、本地 JSON 状态和可选 API Key。

## 后续路线

后续不建议继续堆零散接口，优先沿着生产化方向演进：

1. 把 embedding provider 替换为真实模型，并写入 pgvector。
2. 把仓库状态、chunk、symbol、run 迁移到 PostgreSQL。
3. 将索引流程改为异步任务，增加任务状态和失败原因。
4. 增加 Next.js 工作台，集成 Monaco Editor 展示源码和 citations。
5. 使用 Tree-sitter 提升多语言符号解析质量。
6. 接入更完整的 tracing 或 metrics，展示 Agent 调用链路。

## 面试表达重点

可以把项目总结为：

“CodePilot 当前不是追求功能数量，而是把 AI Agent 落到一个可运行、可测试、可解释、可部署的工程闭环里。它的价值在于把代码仓库理解、检索召回、模型生成、引用证据、运行历史和系统诊断串起来，并且保留了清晰的生产化演进路径。”
