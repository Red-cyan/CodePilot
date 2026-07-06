# 更新日志

本项目遵循“可演示、可测试、边界清晰”的节奏推进。当前版本号来自 `pyproject.toml`。

## 0.1.0 - 后端 MVP

### Agent 能力

- 支持导入本地仓库或 Git 仓库。
- 支持仓库索引、重新索引和删除 CodePilot 内部仓库记录。
- 支持源码扫描、chunk 构建、Python 符号解析和索引策略解释。
- 支持 semantic、keyword、symbol 三种代码检索模式。
- 支持基于仓库上下文的 Chat，并返回 citations。
- 支持架构分析、Bug 分析、结构化 PR Review。
- 支持 README、API 实现和单元测试草稿生成。
- 支持 DeepSeek Chat 调用和本地回退回答。

### 工程化能力

- 使用 FastAPI、Pydantic 和服务层拆分组织后端代码。
- 使用本地 JSON 文件持久化仓库索引状态和 Agent 运行历史。
- 增加 RunStore，记录任务类型、tool trace、citations 和耗时。
- 增加 Diagnostics，展示仓库索引规模、模型配置状态和存储状态。
- 增加请求追踪，响应头返回 `X-Request-Id` 和 `X-Process-Time-Ms`。
- 增加可选 `CODEPILOT_API_KEY`，保护写操作、检索和 Agent 接口。
- 提供 Dockerfile 和 Docker Compose，预留 PostgreSQL/pgvector 和 Redis。
- GitHub Actions 覆盖 ruff、pyright、pytest 和 Docker Compose 配置校验。

### 测试和质量

- 覆盖健康检查、请求追踪、仓库生命周期、索引策略、源码浏览、检索、Agent 生成、结构化 Review、运行历史、诊断、LLM 回退和持久化。
- 增加 `.editorconfig` 和 `.gitattributes`，统一 UTF-8 和 LF 换行。
- 增加 PR 模板、Issue 模板、开发规范和安全说明。

### 文档和面试材料

- README 改为中文，并补充快速启动、主要 API、演示流程、项目亮点和后续规划。
- 增加演示脚本、演示检查清单、项目状态说明、面试讲解指南、面试追问速查和简历写法。
- 增加 ADR，记录离线优先、本地 JSON 状态和可选 API Key 的架构取舍。
- 增加 `SECURITY.md`，说明密钥、索引数据、API 鉴权和漏洞反馈边界。

### 当前边界

- 当前是后端 MVP，没有完整前端工作台。
- 当前使用确定性 embedding 和本地 JSON 状态，适合离线演示和 CI。
- PostgreSQL、pgvector、Redis 已预留，但还没有承载核心状态。
- 索引任务当前同步执行，适合小型仓库演示。

### 推荐下一步

- 接入真实 embedding provider，并将向量写入 pgvector。
- 将 repository、chunk、symbol、run 迁移到 PostgreSQL。
- 将索引流程改为异步任务，增加任务状态和失败原因。
- 增加 Next.js + Monaco Editor 工作台。
- 使用 Tree-sitter 提升多语言符号解析质量。
