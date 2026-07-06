# CodePilot

CodePilot 是一个面向软件研发场景的 AI Software Engineering Agent。它的目标不是做一个普通聊天机器人，而是让 AI 能够理解代码仓库、检索相关代码、分析项目结构、定位 Bug、Review Pull Request，并生成工程文档。

当前版本是一个后端 MVP，重点展示后端工程能力和 AI Agent 工作流：通过 FastAPI 接口导入仓库、扫描源代码、提取符号、构建本地检索索引，并把检索上下文交给 DeepSeek Chat 生成问答、分析和文档结果。未配置模型密钥时，系统会自动使用本地回退回答，保证测试和演示流程不会中断。

## 核心能力

- 支持导入本地仓库，或从 GitHub 克隆仓库。
- 支持仓库重新索引和仓库记录删除，方便源码变更后刷新或清理演示环境。
- 支持扫描 Python、JavaScript、TypeScript、Java、Go、C、C++ 源码文件。
- 支持可配置索引策略，可以调整最大文件大小和忽略目录，并返回跳过文件原因统计。
- 基于 Python `ast` 提取 class、function、import 等符号信息。
- 使用确定性 embedding 构建 chunk 索引，方便离线测试和 CI 验证。
- 接入 OpenAI-compatible DeepSeek Chat API，将检索上下文交给真实模型生成回答。
- 支持 semantic、keyword、symbol 三种代码检索模式。
- 支持基于代码仓库上下文的问答，并返回引用文件和代码片段。
- 支持查看仓库文件树、读取源码文件内容、查询解析出的符号列表。
- 支持基于真实模型生成架构分析、Bug 分析、结构化 PR Review、README 草稿、API 实现草稿和单元测试草稿。
- 支持将仓库元数据、代码 chunk、符号和检索向量持久化到本地 JSON 状态文件，服务重启后可恢复已索引仓库。
- 支持记录每次 Agent 调用的运行历史，包括任务类型、工具链路、引用代码、耗时和生成内容。
- 支持系统诊断接口，汇总索引规模、运行历史、模型配置和本地存储状态。
- 支持 API 请求追踪，响应中返回 `X-Request-Id` 和 `X-Process-Time-Ms`。
- 预留 PostgreSQL、pgvector、Redis、DeepSeek API 等生产化扩展配置。
- 支持 Docker Compose 启动 API、PostgreSQL/pgvector 和 Redis 组成的完整后端环境。

## 技术栈

- Python 3.13
- FastAPI
- Pydantic v2
- GitPython
- SQLAlchemy
- PostgreSQL + pgvector
- Redis
- LangChain
- httpx
- pytest
- ruff
- pyright
- Docker Compose
- Dockerfile

## 快速启动

本地开发启动：

```powershell
uv sync --group dev
Copy-Item .env.example .env
uv run uvicorn app.main:app --reload
```

在 `.env` 中配置模型：

```env
DEEPSEEK_API_KEY=你的 API Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
CODEPILOT_API_KEY=
CODEPILOT_MAX_INDEX_FILE_SIZE=512000
CODEPILOT_IGNORED_DIRS=.git,.idea,.venv,__pycache__,node_modules,dist,build,target,.pytest_cache,.ruff_cache
```

启动后打开：

```text
http://127.0.0.1:8000/docs
```

Docker Compose 启动完整后端环境：

```powershell
Copy-Item .env.example .env
docker compose up --build
```

Compose 会启动：

- `api`：CodePilot FastAPI 服务，端口 `8000`
- `postgres`：PostgreSQL + pgvector，端口 `5432`
- `redis`：Redis，端口 `6379`

API 容器会把运行状态保存到 Docker volume `api_storage`，不会写入仓库目录。

所有 API 响应都会包含：

- `X-Request-Id`：请求追踪 ID；如果客户端传入同名请求头，服务会原样透传。
- `X-Process-Time-Ms`：本次请求处理耗时，单位毫秒。

### API Key 鉴权

默认情况下 `CODEPILOT_API_KEY` 为空，所有接口都可以直接用于本地演示。

如果在 `.env` 中配置：

```env
CODEPILOT_API_KEY=your-secret-key
```

仓库导入、索引、重新索引、删除、代码检索、Chat、分析、Review 和生成类接口需要在请求头中携带：

```text
X-CodePilot-Api-Key: your-secret-key
```

健康检查、系统诊断、仓库列表、源码浏览、符号查看和运行历史查询保持公开，便于演示和排查。

## 主要 API

- `GET /health`：健康检查
- `GET /diagnostics`：系统诊断，查看索引统计、运行历史、模型配置和存储状态
- `POST /repositories/import`：导入本地仓库或 GitHub 仓库
- `POST /repositories/{repository_id}/index`：扫描仓库并建立索引，返回索引数量和跳过原因
- `POST /repositories/{repository_id}/reindex`：源码变更后重新扫描并刷新索引，返回索引数量和跳过原因
- `DELETE /repositories/{repository_id}`：删除 CodePilot 内部仓库记录和索引状态，不删除磁盘源码目录
- `GET /repositories`：查看已导入仓库
- `GET /repositories/{repository_id}/tree`：查看仓库源码文件树
- `GET /repositories/{repository_id}/files?path=...`：读取指定源码文件内容
- `GET /repositories/{repository_id}/symbols`：查看已解析符号列表
- `POST /search/code`：执行代码检索，支持 `semantic`、`keyword`、`symbol`
- `POST /chat`：基于仓库上下文进行代码问答
- `POST /analyze/architecture`：生成项目架构分析报告
- `POST /analyze/bug`：根据错误日志分析可能原因和相关代码
- `POST /review`：根据 git diff 生成结构化 PR Review，包含评分、摘要、问题列表和 LLM 总结
- `POST /generate/readme`：生成 README 草稿
- `POST /generate/api`：根据需求生成 API 实现草稿
- `POST /generate/test`：根据目标代码生成单元测试草稿
- `GET /runs`：查看 Agent 运行历史，支持按 `repository_id` 过滤
- `GET /runs/{run_id}`：查看单次 Agent 调用详情

## 演示流程

配套文档：

- [演示脚本](docs/demo-script.md)：按接口顺序完成一次完整演示。
- [演示检查清单](docs/demo-checklist.md)：面试前检查环境、请求头、接口顺序和常见问题。
- [面试讲解指南](docs/interview-guide.md)：整理项目讲法、技术难点、边界和常见追问。
- [项目状态说明](docs/project-status.md)：汇总已完成能力、验证方式、当前边界和后续路线。
- [开发规范](docs/development-guide.md)：约束提交、编码、密钥处理和本地验证流程。
- [架构决策记录](docs/adr/README.md)：解释离线优先、本地持久化和 API Key 等核心取舍。
- [安全说明](SECURITY.md)：说明密钥、索引数据、API 鉴权和漏洞反馈边界。

1. 调用 `POST /repositories/import` 导入一个代码仓库。
2. 调用 `POST /repositories/{repository_id}/index` 建立代码索引。
3. 调用 `GET /repositories/{repository_id}/tree` 和 `/symbols` 查看仓库结构与符号。
4. 调用 `POST /search/code` 分别演示语义检索、关键词检索和符号检索。
5. 调用 `POST /chat` 提问，例如：“这个项目的仓库导入逻辑是怎么实现的？”
6. 调用 `POST /analyze/architecture` 查看架构分析报告。
7. 调用 `POST /analyze/bug` 输入错误日志，查看相关代码定位结果。
8. 调用 `POST /review` 粘贴 git diff，生成 PR Review。
9. 调用 `POST /generate/readme` 生成 README 草稿。
10. 调用 `POST /generate/api` 输入接口需求，生成 Controller / Service / Schema / Test 草稿。
11. 调用 `POST /generate/test` 输入文件或函数名，生成 pytest 单元测试草稿。
12. 调用 `GET /runs?repository_id=<id>` 查看刚才所有 Agent 调用历史。
13. 调用 `GET /diagnostics` 查看系统诊断和索引统计。

索引状态会保存到：

```text
storage/repositories.json
storage/runs.json
```

该目录已被 `.gitignore` 排除，不会提交本地索引数据、运行记录或私有仓库路径。

## 项目亮点

- 不是单纯调用大模型，而是围绕“代码仓库理解”设计完整 Agent 工作流。
- 具备仓库导入、代码解析、索引、检索、分析、生成的完整闭环。
- 仓库生命周期管理更完整，支持导入、索引、重新索引和删除内部记录。
- 索引策略可配置、可解释，能展示扫描文件数、跳过文件数和跳过原因。
- 提供源码浏览和符号查看接口，便于前端集成 Monaco Editor 或演示仓库理解能力。
- 显式提供多模式代码检索接口，可以单独展示 RAG 前的召回能力。
- PR Review 同时输出确定性规则结果和 LLM 总结，便于展示工程规则与大模型结合。
- 当前索引和检索逻辑可离线运行；配置 API Key 后会调用真实 DeepSeek Chat。
- 每次 Agent 调用都会留下可查询的运行历史，便于展示 Tool Trace、引用证据和耗时。
- 系统诊断接口可以快速说明当前索引规模、模型配置状态和本地持久化状态。
- API 层提供 request id 和耗时响应头，便于定位一次请求和展示基础可观测性。
- 模型调用失败或未配置密钥时会自动回退，便于测试、演示和 CI。
- API、服务层、解析器、检索器和报告生成模块分层清晰，后续可以平滑替换为 pgvector 和真实 embedding 模型。
- 提供 Dockerfile 和 compose app 服务，便于演示部署能力和本地一键启动。
- 适合作为 AI Agent / 大模型应用开发 / 后端工程岗位的项目展示。

## 后续规划

- 接入 DeepSeek 或 OpenAI-compatible embedding provider，替换当前确定性 embedding。
- 使用 PostgreSQL + pgvector 持久化仓库元数据、代码 chunk 和向量索引。
- 引入 Redis/Celery，将仓库索引任务改为异步任务。
- 增加 Next.js 前端，集成 Monaco Editor 展示代码和引用片段。
- 扩展 Tree-sitter 多语言解析能力，提升 Java、Go、C++ 等语言的符号提取效果。
- 增加 LangSmith tracing，展示 Agent 调用链路和工具调用过程。

## 测试

```powershell
uv run ruff check .
uv run pyright
uv run pytest
```

当前测试覆盖：

- 健康检查接口
- 仓库导入、索引和问答流程
- 仓库重新索引和删除接口
- 可配置索引策略和跳过文件原因统计
- 仓库文件树、文件内容和符号查询接口
- semantic、keyword、symbol 三种代码检索接口
- 结构化 PR Review 问题分类、严重级别和评分
- 系统诊断、索引统计和模型配置状态
- API 请求追踪响应头
- API 生成和单元测试生成接口
- 仓库索引状态持久化与服务重启恢复
- Agent 运行历史记录与查询接口
- DeepSeek Chat 客户端回退和响应解析
- Python 符号解析
- 确定性检索逻辑
