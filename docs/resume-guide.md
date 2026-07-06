# CodePilot 简历写法

这份文档用于把 CodePilot 写成简历项目经历。内容需要和当前仓库实际能力一致，不夸大为完整生产系统。

## 项目标题

CodePilot：面向代码仓库理解的 AI Software Engineering Agent

## 一句话项目描述

基于 FastAPI、RAG、本地索引、DeepSeek Chat 和 Docker Compose 实现的代码仓库理解 Agent，支持仓库导入、源码解析、多模式检索、代码问答、结构化 PR Review、运行历史和系统诊断。

## 简历版项目经历

可以直接放到简历中：

```text
CodePilot｜AI 软件工程 Agent｜FastAPI / RAG / DeepSeek / Docker

- 设计并实现面向代码仓库理解的 AI Agent 后端，支持本地或 Git 仓库导入、源码扫描、chunk 构建、符号解析和本地索引持久化。
- 实现 semantic、keyword、symbol 三种代码检索模式，并在 Chat、架构分析、Bug 分析和文档生成中返回 citations，提升回答可追溯性。
- 接入 OpenAI-compatible DeepSeek Chat API，并设计本地回退机制，保证无 API Key 或模型调用失败时仍可完成核心演示和 CI 验证。
- 实现结构化 PR Review，输出 score、summary、issues、category、severity 和 suggestion，便于前端展示和质量门禁扩展。
- 增加 RunStore、Diagnostics、Request ID、耗时响应头和可选 API Key 鉴权，完善运行历史、可观测性和基础安全边界。
- 使用 pytest、ruff、pyright 和 Docker Compose 配置校验构建 CI 质量门禁，并补充演示脚本、ADR、安全说明和面试讲解文档。
```

## 精简版项目经历

适合简历空间较少时使用：

```text
CodePilot｜AI 软件工程 Agent

- 基于 FastAPI + RAG 实现代码仓库理解后端，支持仓库导入、源码解析、三模式检索、代码问答和结构化 PR Review。
- 接入 DeepSeek Chat，并提供本地回退、citations、运行历史、系统诊断、请求追踪和可选 API Key 鉴权。
- 使用 pytest、ruff、pyright、Docker Compose 和 GitHub Actions 建立质量门禁，补充 ADR、安全说明和演示文档。
```

## STAR 讲法

### S：背景

普通聊天机器人无法直接理解本地代码仓库，也很难稳定回答“这个函数在哪里实现”“这段 diff 有什么风险”这类工程问题。

### T：目标

做一个能导入仓库、解析代码、检索上下文、调用模型并返回引用证据的 AI Agent 后端，同时保证没有模型 Key 时也能演示和测试。

### A：行动

- 拆分 Repository、Indexer、Search、Analysis、Review、Generation、RunStore 等服务层。
- 用本地索引和确定性 embedding 支撑离线检索。
- 接入 DeepSeek Chat，并实现本地 fallback。
- 设计结构化 PR Review 和 citations。
- 补充 diagnostics、request tracing、API Key、Docker Compose、CI 和文档体系。

### R：结果

项目形成了可演示的 AI Agent 工程闭环，并通过 `ruff`、`pyright`、`pytest` 和 `docker compose config` 校验；GitHub 文档覆盖 README、演示脚本、检查清单、面试指南、ADR、开发规范和安全说明。

## 可以量化的点

当前可在简历或面试中谨慎表达：

- 覆盖 20 个自动化测试用例。
- 覆盖健康检查、仓库生命周期、索引策略、源码浏览、检索、Agent 生成、运行历史、诊断、LLM 回退和持久化。
- CI 覆盖 ruff、pyright、pytest 和 Docker Compose 配置校验。
- 支持 Python、JavaScript、TypeScript、Java、Go、C、C++ 等源码文件扫描。
- 提供 3 种检索模式和多类 Agent 任务。

## 不建议这样写

避免写成：

- “已上线生产环境”
- “支持千万级代码库检索”
- “完整替代 GitHub Copilot”
- “实现企业级权限系统”
- “使用 pgvector 完成生产级向量检索”

当前项目更准确的定位是：可演示、可测试、边界清晰、具备生产化演进路径的后端 MVP。
