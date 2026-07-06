# CodePilot

CodePilot is an AI software engineering agent for repository indexing, code retrieval,
architecture analysis, bug analysis, pull request review, and README generation.

The first implementation focuses on a backend MVP that is easy to demo in interviews:
FastAPI endpoints import a repository, scan source files, extract symbols, build a
deterministic local search index, and run repository-aware agent workflows.

## Features

- Import a local repository or clone a GitHub repository.
- Scan Python, JavaScript, TypeScript, Java, Go, C, and C++ source files.
- Extract Python classes, functions, and imports with `ast`.
- Build a chunk index with deterministic embeddings for offline tests.
- Ask repository-aware code questions with cited file snippets.
- Generate architecture, bug analysis, PR review, and README reports.
- Keep PostgreSQL, pgvector, Redis, and DeepSeek configuration ready for production expansion.

## Quickstart

```powershell
uv sync --group dev
Copy-Item .env.example .env
uv run uvicorn app.main:app --reload
```

Open `http://127.0.0.1:8000/docs`.

## Core API

- `GET /health`
- `POST /repositories/import`
- `POST /repositories/{repository_id}/index`
- `GET /repositories`
- `POST /chat`
- `POST /analyze/architecture`
- `POST /analyze/bug`
- `POST /review`
- `POST /generate/readme`

## Demo Flow

1. Import a repository with `POST /repositories/import`.
2. Index it with `POST /repositories/{repository_id}/index`.
3. Ask code questions with `POST /chat`.
4. Run architecture and bug analysis.
5. Paste a git diff into `POST /review`.
6. Generate a README draft.

## Roadmap

- Replace deterministic embeddings with a pluggable DeepSeek/OpenAI-compatible embedding provider.
- Persist repository metadata and vectors in PostgreSQL + pgvector.
- Add async indexing workers with Redis/Celery.
- Add a Next.js interface with Monaco Editor for code browsing.
