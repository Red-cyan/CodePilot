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

## 4. 仓库问答

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

## 5. 分析类 Agent

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

## 6. 生成类 Agent

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

## 7. 面试讲解重点

## 7. 查看运行历史

调用 `GET /runs?repository_id=<id>` 查看当前仓库的 Agent 调用历史。

调用 `GET /runs/{run_id}` 查看单次调用详情。

演示重点：

- 每条记录包含 `kind`，能区分 chat、architecture、bug_analysis、pr_review、readme_generation 等任务。
- 每条记录包含 `tool_trace`，可以说明本次调用经过了 retriever、context_builder、llm 等步骤。
- 每条记录保留 citations，能展示回答依据来自哪些文件和行号。
- 每条记录包含 `duration_ms`，可以体现基本可观测性。

## 8. 面试讲解重点

- CodePilot 不是普通聊天机器人，而是围绕代码仓库理解设计的工程 Agent。
- 当前闭环包括导入、解析、索引、检索、LLM 生成、运行历史、引用追踪和测试验证。
- 测试环境禁用真实模型调用，保证 CI 稳定；本地 `.env` 配置 API Key 后可调用真实 DeepSeek。
