# CodePilot 演示检查清单

这份清单用于面试或答辩前 10 分钟快速检查，目标是保证演示过程稳定、顺序清楚、问题可排查。

## 演示前检查

- 确认当前分支干净：

```powershell
git status --short --branch
```

- 确认依赖可用：

```powershell
uv sync --group dev
```

- 确认 `.env` 已存在：

```powershell
Copy-Item .env.example .env
```

- 如果需要真实模型效果，确认 `.env` 中配置了：

```env
DEEPSEEK_API_KEY=你的 DeepSeek Key
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-chat
```

- 如果配置了 `CODEPILOT_API_KEY`，后续写操作和 Agent 接口都要带请求头：

```text
X-CodePilot-Api-Key: your-secret-key
```

- 演示前跑一次质量检查：

```powershell
uv run ruff check .
uv run pyright
uv run pytest
```

## 启动方式

本地开发启动：

```powershell
uv run uvicorn app.main:app --reload
```

打开 Swagger：

```text
http://127.0.0.1:8000/docs
```

Docker Compose 演示启动：

```powershell
docker compose up --build
```

Docker Desktop 未启动时，优先使用本地开发启动，不要在现场浪费时间排 Docker Engine。

## 标准演示顺序

1. `GET /health`
   - 证明服务启动正常。
   - 顺带展示响应头 `X-Request-Id` 和 `X-Process-Time-Ms`。

2. `GET /diagnostics`
   - 展示系统状态。
   - 说明不会泄露 API Key，只返回模型是否配置。

3. `POST /repositories/import`
   - 导入一个小型本地仓库，优先使用当前 CodePilot 仓库。
   - 保存返回的 `repository.id`。

4. `POST /repositories/{repository_id}/index`
   - 展示 `files_indexed`、`chunks_indexed`、`symbols_indexed`。
   - 重点讲 `files_scanned`、`skipped_files`、`skip_reasons`，说明索引策略可解释。

5. `GET /repositories/{repository_id}/tree`
   - 展示源码文件树。

6. `GET /repositories/{repository_id}/symbols`
   - 展示 class、function、import 等符号解析结果。

7. `POST /search/code`
   - 依次演示 `semantic`、`keyword`、`symbol`。
   - 说明三种模式服务不同查询场景。

8. `POST /chat`
   - 提问示例：

```json
{
  "repository_id": "<id>",
  "question": "这个项目的仓库导入逻辑是怎么实现的？",
  "top_k": 5
}
```

   - 重点展示 citations，说明回答有代码依据。

9. `POST /review`
   - diff 示例：

```json
{
  "repository_id": "<id>",
  "diff": "+ password = '123456'\n+ print(password)\n+ try:\n+     save_secret(password)\n+ except Exception:\n+     pass\n"
}
```

   - 展示 score、issues、category、severity、suggestion。

10. `GET /runs?repository_id=<id>`
    - 展示刚才的 Agent 运行历史。
    - 说明 tool_trace、citations 和 duration_ms。

11. `GET /diagnostics`
    - 再次展示 run_count 和索引状态变化。

## 常用演示语句

- “这个项目不是单次 prompt 调用，而是围绕代码仓库构建了导入、解析、检索、生成和可观测的闭环。”
- “没有模型 Key 时也能演示核心链路，因为系统会走本地回退，保证 CI 和现场演示稳定。”
- “citations 是为了降低幻觉风险，让回答能追溯到具体文件和代码片段。”
- “结构化 PR Review 方便前端展示和后续质量门禁，不只是返回一段自然语言。”
- “当前使用本地 JSON 存储和确定性 embedding，是为了 MVP 稳定演示；后续可以替换成 pgvector 和真实 embedding provider。”

## 现场问题排查

### 返回 401

检查 `.env` 是否配置了 `CODEPILOT_API_KEY`。如果配置了，请求头必须带：

```text
X-CodePilot-Api-Key: your-secret-key
```

### 返回 404

检查 `repository_id` 是否复制正确。重新调用 `GET /repositories` 查看当前已导入仓库。

### 没有真实模型回答

检查 `DEEPSEEK_API_KEY` 是否配置。未配置时系统会返回本地回退结果，这是预期行为。

### 索引结果太少

检查仓库里是否有支持的源码文件；同时查看 `skip_reasons`，确认是否被忽略目录、文件大小或扩展名策略跳过。

### Docker 启动失败

先确认 Docker Desktop 是否启动。面试现场可以直接切换到：

```powershell
uv run uvicorn app.main:app --reload
```

## 演示结束前确认

- 展示 README 中的项目亮点。
- 展示 `docs/interview-guide.md`，说明自己对技术选型、边界和后续演进有明确理解。
- 展示测试结果或直接运行：

```powershell
uv run pytest
```

- 最后总结当前项目的闭环：

```text
仓库导入 -> 源码解析 -> 检索索引 -> Agent 生成 -> 引用追踪 -> 运行历史 -> 系统诊断 -> Docker 部署
```
