# CodePilot

CodePilot 是一个面向软件研发场景的 AI Software Engineering Agent。它的目标不是做一个普通聊天机器人，而是让 AI 能够理解代码仓库、检索相关代码、分析项目结构、定位 Bug、Review Pull Request，并生成工程文档。

当前版本是一个后端 MVP，重点展示后端工程能力和 AI Agent 工作流：通过 FastAPI 接口导入仓库、扫描源代码、提取符号、构建本地检索索引，并把检索上下文交给 DeepSeek Chat 生成问答、分析和文档结果。未配置模型密钥时，系统会自动使用本地回退回答，保证测试和演示流程不会中断。

## 核心能力

- 支持导入本地仓库，或从 GitHub 克隆仓库。
- 支持扫描 Python、JavaScript、TypeScript、Java、Go、C、C++ 源码文件。
- 基于 Python `ast` 提取 class、function、import 等符号信息。
- 使用确定性 embedding 构建 chunk 索引，方便离线测试和 CI 验证。
- 接入 OpenAI-compatible DeepSeek Chat API，将检索上下文交给真实模型生成回答。
- 支持基于代码仓库上下文的问答，并返回引用文件和代码片段。
- 支持基于真实模型生成架构分析、Bug 分析、PR Review 和 README 草稿。
- 预留 PostgreSQL、pgvector、Redis、DeepSeek API 等生产化扩展配置。

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

## 快速启动

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
```

启动后打开：

```text
http://127.0.0.1:8000/docs
```

## 主要 API

- `GET /health`：健康检查
- `POST /repositories/import`：导入本地仓库或 GitHub 仓库
- `POST /repositories/{repository_id}/index`：扫描仓库并建立索引
- `GET /repositories`：查看已导入仓库
- `POST /chat`：基于仓库上下文进行代码问答
- `POST /analyze/architecture`：生成项目架构分析报告
- `POST /analyze/bug`：根据错误日志分析可能原因和相关代码
- `POST /review`：根据 git diff 生成 PR Review
- `POST /generate/readme`：生成 README 草稿

## 演示流程

1. 调用 `POST /repositories/import` 导入一个代码仓库。
2. 调用 `POST /repositories/{repository_id}/index` 建立代码索引。
3. 调用 `POST /chat` 提问，例如：“这个项目的仓库导入逻辑是怎么实现的？”
4. 调用 `POST /analyze/architecture` 查看架构分析报告。
5. 调用 `POST /analyze/bug` 输入错误日志，查看相关代码定位结果。
6. 调用 `POST /review` 粘贴 git diff，生成 PR Review。
7. 调用 `POST /generate/readme` 生成 README 草稿。

## 项目亮点

- 不是单纯调用大模型，而是围绕“代码仓库理解”设计完整 Agent 工作流。
- 具备仓库导入、代码解析、索引、检索、分析、生成的完整闭环。
- 当前索引和检索逻辑可离线运行；配置 API Key 后会调用真实 DeepSeek Chat。
- 模型调用失败或未配置密钥时会自动回退，便于测试、演示和 CI。
- API、服务层、解析器、检索器和报告生成模块分层清晰，后续可以平滑替换为 pgvector 和真实 embedding 模型。
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
- DeepSeek Chat 客户端回退和响应解析
- Python 符号解析
- 确定性检索逻辑
