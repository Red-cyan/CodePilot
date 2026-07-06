# CodePilot 面试讲解指南

这份文档用于面试前快速准备 CodePilot 的讲解，不替代 README，而是帮助把项目讲成一个完整的工程故事。

## 一句话介绍

CodePilot 是一个面向代码仓库理解的 AI Software Engineering Agent。它可以导入代码仓库，解析源码结构，建立本地检索索引，再结合 DeepSeek Chat 完成代码问答、架构分析、Bug 分析、PR Review 和工程文档生成。

重点不是“调用一次大模型”，而是把仓库导入、代码解析、检索召回、LLM 生成、引用证据、运行历史、诊断和部署串成一个可演示的后端系统。

## 推荐讲解顺序

1. 先讲背景：普通聊天机器人无法稳定回答仓库级问题，所以需要围绕代码仓库构建检索和 Agent 流程。
2. 再讲整体流程：导入仓库 -> 解析源码 -> 建立 chunk 和符号索引 -> 检索相关代码 -> 构造上下文 -> 调用模型或本地回退 -> 返回答案和 citations。
3. 然后讲工程化：FastAPI 分层、Pydantic schema、服务层拆分、运行历史、诊断接口、请求追踪、API Key 鉴权、Docker Compose。
4. 最后讲可扩展：当前是可离线演示的 MVP，后续可以替换真实 embedding、接入 pgvector、异步索引任务和前端编辑器。

## 系统架构

```text
Client / Swagger
    |
FastAPI Routes
    |
Service Layer
    |-- RepositoryService：导入、保存仓库元数据
    |-- IndexerService：扫描文件、解析符号、建立 chunk 索引
    |-- BrowserService：文件树、源码内容、符号浏览
    |-- CodeSearchService：semantic / keyword / symbol 检索
    |-- AnalysisService：Chat、架构分析、Bug 分析
    |-- ReviewService：结构化 PR Review
    |-- GenerationService：README、API、单元测试草稿生成
    |-- RunStore：记录 Agent 运行历史
    |
Local JSON Storage
DeepSeek Chat API / Local Fallback
```

## 核心设计点

- 可离线运行：没有模型密钥时使用本地回退，保证测试、CI 和现场演示不依赖外部服务。
- 可解释检索：答案返回 citations，能说明结果来自哪个文件和代码片段。
- 多模式检索：semantic 适合语义问题，keyword 适合精确文本，symbol 适合类名和函数名定位。
- 结构化输出：PR Review 不只返回自然语言，还返回 score、issues、category、severity、suggestion。
- 运行历史：每次 Agent 调用记录 kind、tool_trace、citations、duration_ms，方便展示可观测性。
- 系统诊断：`/diagnostics` 汇总索引规模、模型配置状态、存储状态，不泄露 API Key。
- 安全边界：配置 `CODEPILOT_API_KEY` 后，写操作和 Agent 接口需要请求头鉴权，只读诊断接口保持可访问。
- 部署意识：提供 Dockerfile 和 Docker Compose，预留 PostgreSQL、pgvector、Redis。

## 可以重点展示的接口

- `POST /repositories/import`：导入本地仓库或 Git 仓库。
- `POST /repositories/{repository_id}/index`：扫描源码并建立索引，返回跳过文件原因。
- `GET /repositories/{repository_id}/tree`：展示仓库文件树。
- `GET /repositories/{repository_id}/symbols`：展示解析出的类、函数和 import。
- `POST /search/code`：展示三种检索模式。
- `POST /chat`：基于仓库上下文问答，并返回 citations。
- `POST /review`：输入 diff，输出结构化 PR Review。
- `GET /runs`：查看 Agent 运行历史和工具链路。
- `GET /diagnostics`：展示系统状态。

## 技术难点和回答方式

### 为什么需要 RAG？

模型本身不知道本地仓库的最新代码，也不能稳定记住完整上下文。RAG 的作用是先从仓库索引中召回相关代码，再把这些代码作为事实依据交给模型，降低幻觉，并通过 citations 让回答可追溯。

### 为什么保留本地回退？

面试演示、CI 和本地测试不能完全依赖外部模型服务。回退逻辑让系统在没有 API Key 或模型调用失败时仍能返回基于检索片段的结果，保证核心链路可验证。

### 当前 embedding 为什么是确定性的？

当前阶段优先保证离线测试和演示稳定，所以用确定性 embedding 形成可重复的检索结果。它不是最终生产方案，后续可以替换成 DeepSeek 或 OpenAI-compatible embedding，再把向量写入 pgvector。

### PR Review 为什么做结构化结果？

如果只让模型输出一段文字，前端和自动化流程很难消费。结构化结果可以直接用于列表展示、风险评分、严重级别筛选和后续质量门禁，同时保留 LLM 总结用于解释。

### 为什么要有 RunStore？

Agent 系统需要可观测性。RunStore 记录每次调用的任务类型、引用证据、工具链路和耗时，既方便排查问题，也方便面试展示“这不是黑盒调用模型”。

### API Key 鉴权解决什么问题？

导入仓库、删除索引、调用模型和生成报告都属于有副作用或有成本的操作。可选 API Key 在不影响本地演示的前提下，为部署环境提供最小安全边界。

## 项目边界

当前项目是后端 MVP，不把所有生产能力一次性做完。已经实现的重点是完整闭环和工程分层；未完成但设计上预留的方向包括：

- 使用真实 embedding provider 替换确定性 embedding。
- 使用 PostgreSQL + pgvector 替换本地 JSON 状态文件。
- 把索引任务改成异步任务，并提供任务状态查询。
- 接入 Next.js 前端和 Monaco Editor。
- 使用 Tree-sitter 提升多语言符号解析质量。

面试时可以主动说明这些边界，重点强调自己知道当前方案适合演示和验证，生产化还需要哪些演进。

## 常见追问

### 如何避免路径穿越？

源码读取接口会校验请求路径必须位于仓库根目录内，非法路径返回 400，避免读取仓库外部文件。

### 如何避免泄露密钥？

`.env` 不提交到 Git；诊断接口只返回模型是否配置，不返回 API Key；README 和 `.env.example` 只保留空配置示例。

### 如何保证测试稳定？

测试默认不调用真实模型，LLM 客户端有回退路径；索引和检索使用确定性逻辑；核心 API、解析器、检索、RunStore、LLM 回退都有测试覆盖。

### 如果仓库很大怎么办？

当前通过 `CODEPILOT_MAX_INDEX_FILE_SIZE` 和 `CODEPILOT_IGNORED_DIRS` 控制扫描范围，并返回跳过原因。后续可以加入异步任务、增量索引、分页读取和数据库索引。

### 为什么选择 FastAPI？

FastAPI 的类型提示、Pydantic schema、OpenAPI 文档和测试体验适合快速构建可演示的工程后端，也方便后续接前端或其他服务。

## 面试结尾总结

可以这样收束：

“CodePilot 的重点是把 AI 能力放进一个真实后端工程闭环里。我没有只做 prompt 调用，而是实现了仓库导入、源码解析、检索召回、模型生成、引用追踪、运行历史、诊断、安全配置和 Docker 部署。当前版本适合演示核心能力，后续可以沿着真实 embedding、pgvector、异步任务和前端工作台继续生产化。”
