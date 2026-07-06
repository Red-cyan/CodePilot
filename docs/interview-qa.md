# CodePilot 面试追问速查

这份文档用于面试前快速复习高频追问。回答时优先结合当前代码和 ADR，不要夸大项目边界。

## 你这个项目解决什么问题？

它解决的是“让 AI 基于真实代码仓库回答工程问题”。普通模型不知道本地仓库内容，所以 CodePilot 先导入仓库、解析源码、建立索引，再检索相关代码片段交给模型，最后返回回答和 citations。

## 这个项目和普通 ChatGPT 套壳有什么区别？

区别在工程闭环：

- 有仓库导入和生命周期管理。
- 有源码解析、chunk、符号提取和索引策略。
- 有 semantic、keyword、symbol 三种检索。
- 有 citations、RunStore、Diagnostics、Request ID 和耗时。
- 有结构化 PR Review，而不是只返回一段自然语言。
- 有测试、CI、Docker Compose、ADR 和安全说明。

## 为什么当前不用真实 embedding？

当前阶段优先保证离线演示和 CI 稳定，所以使用确定性 embedding。这样测试结果可重复，没有 API Key 也能验证检索链路。后续生产化可以替换为真实 embedding provider，并写入 pgvector。

## 为什么保留本地回退？

因为面试演示和 CI 不能依赖外部模型服务。没有 DeepSeek Key、网络失败或模型服务异常时，系统仍然能基于检索片段返回回退回答，证明仓库导入、索引、检索和 citations 链路是可用的。

## citations 有什么价值？

citations 让回答可追溯。面试时可以强调：AI 对代码仓库的回答不能只给结论，还要说明依据来自哪个文件、哪几行、哪个代码片段，这样才能降低幻觉风险。

## PR Review 为什么要结构化？

结构化结果可以被前端、质量门禁和后续自动化流程消费。`score`、`issues`、`severity`、`category` 和 `suggestion` 比一段纯文本更适合工程系统。

## 为什么状态先用 JSON？

这是 MVP 阶段的权衡。本地 JSON 启动简单、便于调试、适合演示和测试。项目已经预留 PostgreSQL、pgvector、Redis，后续可以迁移到数据库和异步任务。

## 如果仓库很大怎么办？

当前通过最大文件大小和忽略目录限制扫描范围，并返回跳过原因。后续可以做增量索引、异步任务、任务状态、数据库分页和 pgvector 检索。

## API Key 鉴权为什么是可选的？

本地演示需要低门槛，所以默认不开启。部署时配置 `CODEPILOT_API_KEY` 后，写操作、检索和 Agent 接口都需要请求头。它不是完整账号体系，但提供了最小安全边界。

## 你怎么保证不泄露密钥？

`.env` 被 `.gitignore` 排除；`.env.example` 只保留空值；诊断接口只返回是否配置，不返回真实 Key；PR 模板和 SECURITY 都要求不提交 API Key、私有路径和本地索引数据。

## 这个项目的测试覆盖了什么？

测试覆盖健康检查、请求追踪、仓库导入、索引、重建索引、删除、文件浏览、符号解析、三模式检索、Chat、生成、Review、RunStore、Diagnostics、LLM 回退和持久化。

## 你遇到的最大难点是什么？

可以回答：

“难点不是单独调模型，而是把模型能力放进稳定工程链路里。比如没有模型 Key 时仍要能测试，回答要能追溯到代码片段，PR Review 要结构化，运行历史和诊断要能解释 Agent 做了什么。”

## 这个项目目前最大的不足是什么？

可以主动说：

“当前是后端 MVP，还没有真实 embedding + pgvector，没有异步索引任务，也没有前端工作台。我把这些作为明确后续路线，而不是在当前阶段堆不稳定功能。”

## 下一步你会怎么做？

优先顺序：

1. 将 deterministic embedding 替换为真实 embedding provider。
2. 将 repository、chunk、symbol、run 迁移到 PostgreSQL 和 pgvector。
3. 将索引改为异步任务，补任务状态和失败原因。
4. 做 Next.js 工作台，用 Monaco Editor 展示源码、citations 和运行历史。
5. 用 Tree-sitter 增强多语言符号解析。

## 30 秒总结

“CodePilot 是一个代码仓库理解 Agent 后端。它不是简单调用大模型，而是实现了仓库导入、源码解析、索引检索、上下文构造、LLM 生成、引用追踪、运行历史、诊断、鉴权和 CI。当前版本定位是可演示的工程 MVP，边界清晰，并预留了 pgvector、异步任务和前端工作台的生产化路径。”
