# CodePilot Demo Script

## 1. Start the API

```powershell
uv sync --group dev
uv run uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## 2. Import a Repository

Call `POST /repositories/import`:

```json
{
  "mode": "local",
  "source": "E:/PythonLearning/CodePilot"
}
```

## 3. Index the Repository

Call `POST /repositories/{repository_id}/index`.

Expected result:

- indexed file count
- indexed chunk count
- indexed symbol count

## 4. Ask a Code Question

Call `POST /chat`:

```json
{
  "repository_id": "<id>",
  "question": "How does repository import work?",
  "top_k": 5
}
```

The response should include cited files and line ranges.

## 5. Run Agent Reports

- `POST /analyze/architecture`
- `POST /analyze/bug`
- `POST /review`
- `POST /generate/readme`

Use these outputs to explain repository understanding, RAG retrieval, and software engineering workflows in interviews.
