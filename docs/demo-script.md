# CodePilot 演示脚本

## 1. 启动 API

```powershell
uv sync --group dev
Copy-Item .env.example .env
uv run uvicorn app.main:app --reload
```

打开：

```text
http://127.0.0.1:8000/docs
```

## 2. 导入仓库

调用 `POST /repositories/import`：

```json
{
  "mode": "local",
  "source": "E:/PythonLearning/CodePilot"
}
```

保存返回结果中的 `repository.id`。

## 3. 建立索引

调用 `POST /repositories/{repository_id}/index`。

重点观察返回值：

- `files_indexed`
- `chunks_indexed`
- `symbols_indexed`
- `files_scanned`
- `skipped_files`
- `skip_reasons`

演示重点：

- `CODEPILOT_MAX_INDEX_FILE_SIZE` 控制单文件最大索引大小。
- `CODEPILOT_IGNORED_DIRS` 控制忽略目录，例如 `.git`、`node_modules`、`.venv`。
- `skip_reasons` 可以解释文件为什么没有进入索引，例如 `ignored_directory`、`unsupported_extension`、`empty_file`、`file_too_large`。

如果源码发生变化，调用 `POST /repositories/{repository_id}/reindex` 重新扫描并刷新索引。

如果需要清理演示环境，调用 `DELETE /repositories/{repository_id}` 删除 CodePilot 内部记录和索引状态。该接口不会删除磁盘上的源码目录。

## 4. 源码浏览

先调用源码浏览接口，确认系统已经理解仓库结构：

- `GET /repositories/{repository_id}/tree`
- `GET /repositories/{repository_id}/files?path=app/services/repository.py`
- `GET /repositories/{repository_id}/symbols`

演示重点：

- 文件读取接口会限制路径必须在仓库根目录内，避免任意文件读取。
- 符号列表来自索引阶段解析出的 class、function 和 import。

## 5. 仓库问答

先调用 `POST /search/code` 演示多模式代码检索：

语义检索：

```json
{
  "repository_id": "<id>",
  "query": "repository import workflow",
  "mode": "semantic",
  "top_k": 5
}
```

关键词检索：

```json
{
  "repository_id": "<id>",
  "query": "RepositoryService",
  "mode": "keyword",
  "top_k": 5
}
```

符号检索：

```json
{
  "repository_id": "<id>",
  "query": "RepositoryService",
  "mode": "symbol",
  "top_k": 5
}
```

演示重点：

- semantic 展示 RAG 的召回基础。
- keyword 展示确定性文本匹配。
- symbol 展示代码解析结果可以直接服务于检索。

调用 `POST /chat`：

```json
{
  "repository_id": "<id>",
  "question": "这个项目的仓库导入逻辑是怎么实现的？",
  "top_k": 5
}
```

演示重点：

- 回答由 DeepSeek Chat 生成。
- 返回结果包含引用文件、行号和代码片段。
- 未配置模型时会自动回退，不影响流程演示。

## 6. 分析类 Agent

依次调用：

- `POST /analyze/architecture`
- `POST /analyze/bug`
- `POST /review`

Bug 分析示例：

```json
{
  "repository_id": "<id>",
  "error_log": "ModuleNotFoundError: No module named 'app'"
}
```

PR Review 示例：

```json
{
  "repository_id": "<id>",
  "diff": "+ print('debug')\n+ password = '123456'"
}
```

演示重点：

- 返回 `score`，可以快速判断变更风险。
- 返回 `issues`，每个问题包含 category、severity、message、suggestion 和 line_hint。
- `content` 字段仍保留 DeepSeek 生成的中文 Review 总结。
- 这个设计体现了“确定性规则 + LLM 解释”的组合，而不是完全依赖大模型。

## 7. 生成类 Agent

调用 `POST /generate/readme` 生成 README 草稿。

调用 `POST /generate/api`：

```json
{
  "repository_id": "<id>",
  "requirement": "新增一个导出仓库架构报告的接口",
  "style": "FastAPI + service + schema + pytest"
}
```

调用 `POST /generate/test`：

```json
{
  "repository_id": "<id>",
  "target": "RepositoryService.import_repository",
  "framework": "pytest"
}
```

## 8. 查看运行历史

调用 `GET /runs?repository_id=<id>` 查看当前仓库的 Agent 调用历史。

调用 `GET /runs/{run_id}` 查看单次调用详情。

演示重点：

- 每条记录包含 `kind`，能区分 chat、architecture、bug_analysis、pr_review、readme_generation 等任务。
- 每条记录包含 `tool_trace`，可以说明本次调用经过了 retriever、context_builder、llm 等步骤。
- 每条记录保留 citations，能展示回答依据来自哪些文件和行号。
- 每条记录包含 `duration_ms`，可以体现基本可观测性。

## 9. 系统诊断

调用 `GET /diagnostics` 查看系统当前状态。

演示重点：

- `repositories` 汇总仓库数量、索引文件数、chunk 数、符号数和语言分布。
- `run_count` 展示已经记录的 Agent 调用次数。
- `llm.configured` 只说明模型是否配置，不会泄露 API Key。
- `storage` 展示本地状态文件是否存在，可以说明服务重启恢复能力。

## 10. 面试讲解重点

- CodePilot 不是普通聊天机器人，而是围绕代码仓库理解设计的工程 Agent。
- 当前闭环包括导入、解析、可解释索引、源码浏览、多模式检索、LLM 生成、运行历史、系统诊断、引用追踪和测试验证。
- 测试环境禁用真实模型调用，保证 CI 稳定；本地 `.env` 配置 API Key 后可调用真实 DeepSeek。
