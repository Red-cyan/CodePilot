from fastapi.testclient import TestClient

from app.main import create_app


def test_health():
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_import_index_and_chat(tmp_path):
    (tmp_path / "notes.txt").write_text("not source", encoding="utf-8")
    (tmp_path / "app.py").write_text(
        "class RepositoryService:\n    def import_repository(self):\n        return 'ok'\n",
        encoding="utf-8",
    )
    client = TestClient(create_app())

    imported = client.post(
        "/repositories/import",
        json={"mode": "local", "source": str(tmp_path)},
    )
    assert imported.status_code == 200
    repository_id = imported.json()["repository"]["id"]

    indexed = client.post(f"/repositories/{repository_id}/index")
    assert indexed.status_code == 200
    assert indexed.json()["files_indexed"] == 1
    assert indexed.json()["files_scanned"] == 2
    assert indexed.json()["skipped_files"] == 1
    assert indexed.json()["skip_reasons"]["unsupported_extension"] == 1

    chat = client.post(
        "/chat",
        json={"repository_id": repository_id, "question": "import repository"},
    )
    assert chat.status_code == 200
    assert chat.json()["citations"][0]["path"] == "app.py"


def test_repository_browser_endpoints(tmp_path):
    (tmp_path / "pkg").mkdir()
    (tmp_path / "pkg" / "service.py").write_text(
        "class Service:\n    def run(self):\n        return 'ok'\n",
        encoding="utf-8",
    )
    client = TestClient(create_app())

    imported = client.post(
        "/repositories/import",
        json={"mode": "local", "source": str(tmp_path)},
    )
    repository_id = imported.json()["repository"]["id"]
    client.post(f"/repositories/{repository_id}/index")

    tree = client.get(f"/repositories/{repository_id}/tree")
    assert tree.status_code == 200
    tree_paths = {item["path"] for item in tree.json()["items"]}
    assert "pkg" in tree_paths
    assert "pkg/service.py" in tree_paths

    file_response = client.get(
        f"/repositories/{repository_id}/files",
        params={"path": "pkg/service.py"},
    )
    assert file_response.status_code == 200
    assert file_response.json()["language"] == "python"
    assert "class Service" in file_response.json()["content"]

    symbols = client.get(f"/repositories/{repository_id}/symbols")
    assert symbols.status_code == 200
    symbol_names = {symbol["name"] for symbol in symbols.json()["symbols"]}
    assert {"Service", "run"} <= symbol_names

    unsafe = client.get(
        f"/repositories/{repository_id}/files",
        params={"path": "../outside.py"},
    )
    assert unsafe.status_code == 400


def test_code_search_endpoint_supports_multiple_modes(tmp_path):
    (tmp_path / "search_service.py").write_text(
        "class SearchService:\n"
        "    def find_user(self, user_id: str):\n"
        "        return {'user_id': user_id}\n",
        encoding="utf-8",
    )
    client = TestClient(create_app())

    imported = client.post(
        "/repositories/import",
        json={"mode": "local", "source": str(tmp_path)},
    )
    repository_id = imported.json()["repository"]["id"]
    client.post(f"/repositories/{repository_id}/index")

    semantic = client.post(
        "/search/code",
        json={"repository_id": repository_id, "query": "find user", "mode": "semantic"},
    )
    assert semantic.status_code == 200
    assert semantic.json()["hits"][0]["path"] == "search_service.py"

    keyword = client.post(
        "/search/code",
        json={"repository_id": repository_id, "query": "user_id", "mode": "keyword"},
    )
    assert keyword.status_code == 200
    assert keyword.json()["hits"][0]["kind"] == "chunk"

    symbol = client.post(
        "/search/code",
        json={"repository_id": repository_id, "query": "SearchService", "mode": "symbol"},
    )
    assert symbol.status_code == 200
    assert symbol.json()["hits"][0]["kind"] == "class"


def test_diagnostics_reports_index_and_model_status(tmp_path):
    (tmp_path / "service.py").write_text(
        "def handle_request():\n    return 'ok'\n",
        encoding="utf-8",
    )
    client = TestClient(create_app())

    imported = client.post(
        "/repositories/import",
        json={"mode": "local", "source": str(tmp_path)},
    )
    repository_id = imported.json()["repository"]["id"]
    client.post(f"/repositories/{repository_id}/index")

    response = client.get("/diagnostics")

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "ok"
    assert payload["repositories"]["repository_count"] >= 1
    assert payload["repositories"]["files_indexed"] >= 1
    assert payload["repositories"]["chunks_indexed"] >= 1
    assert "api_key" not in payload["llm"]
    assert payload["llm"]["configured"] is False


def test_reindex_and_delete_repository(tmp_path):
    (tmp_path / "first.py").write_text(
        "def first():\n    return 'first'\n",
        encoding="utf-8",
    )
    client = TestClient(create_app())

    imported = client.post(
        "/repositories/import",
        json={"mode": "local", "source": str(tmp_path)},
    )
    repository_id = imported.json()["repository"]["id"]
    indexed = client.post(f"/repositories/{repository_id}/index")
    assert indexed.status_code == 200
    assert indexed.json()["files_indexed"] == 1

    (tmp_path / "second.py").write_text(
        "def second():\n    return 'second'\n",
        encoding="utf-8",
    )
    reindexed = client.post(f"/repositories/{repository_id}/reindex")
    assert reindexed.status_code == 200
    assert reindexed.json()["files_indexed"] == 2

    deleted = client.delete(f"/repositories/{repository_id}")
    assert deleted.status_code == 200
    assert deleted.json()["deleted"] is True

    missing = client.post(f"/repositories/{repository_id}/reindex")
    assert missing.status_code == 404


def test_generation_endpoints(tmp_path):
    (tmp_path / "service.py").write_text(
        "def create_order(user_id: str):\n    return {'user_id': user_id}\n",
        encoding="utf-8",
    )
    client = TestClient(create_app())

    imported = client.post(
        "/repositories/import",
        json={"mode": "local", "source": str(tmp_path)},
    )
    repository_id = imported.json()["repository"]["id"]
    client.post(f"/repositories/{repository_id}/index")

    api_response = client.post(
        "/generate/api",
        json={
            "repository_id": repository_id,
            "requirement": "新增创建订单接口",
            "style": "FastAPI + pytest",
        },
    )
    assert api_response.status_code == 200
    assert api_response.json()["title"] == "API Generation Draft"
    assert api_response.json()["citations"][0]["path"] == "service.py"

    test_response = client.post(
        "/generate/test",
        json={
            "repository_id": repository_id,
            "target": "create_order",
            "framework": "pytest",
        },
    )
    assert test_response.status_code == 200
    assert test_response.json()["title"] == "Unit Test Generation Draft"
    assert test_response.json()["citations"][0]["path"] == "service.py"


def test_review_endpoint_returns_structured_issues(tmp_path):
    (tmp_path / "service.py").write_text(
        "def save_secret(value: str):\n    return value\n",
        encoding="utf-8",
    )
    client = TestClient(create_app())

    imported = client.post(
        "/repositories/import",
        json={"mode": "local", "source": str(tmp_path)},
    )
    repository_id = imported.json()["repository"]["id"]
    client.post(f"/repositories/{repository_id}/index")

    response = client.post(
        "/review",
        json={
            "repository_id": repository_id,
            "diff": (
                "+ password = '123456'\n"
                "+ print(password)\n"
                "+ try:\n"
                "+     save_secret(password)\n"
                "+ except Exception:\n"
                "+     pass\n"
            ),
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["score"] < 90
    assert payload["issues"]
    categories = {issue["category"] for issue in payload["issues"]}
    assert {"security", "style", "maintainability"} <= categories


def test_agent_runs_are_recorded(tmp_path):
    (tmp_path / "app.py").write_text(
        "def import_repository(source: str):\n    return source\n",
        encoding="utf-8",
    )
    client = TestClient(create_app())

    imported = client.post(
        "/repositories/import",
        json={"mode": "local", "source": str(tmp_path)},
    )
    repository_id = imported.json()["repository"]["id"]
    client.post(f"/repositories/{repository_id}/index")

    chat = client.post(
        "/chat",
        json={"repository_id": repository_id, "question": "import repository"},
    )
    assert chat.status_code == 200

    runs = client.get(f"/runs?repository_id={repository_id}")
    assert runs.status_code == 200
    run = runs.json()["runs"][0]
    assert run["kind"] == "chat"
    assert run["repository_id"] == repository_id
    assert run["tool_trace"] == ["retriever", "context_builder", "llm"]

    detail = client.get(f"/runs/{run['id']}")
    assert detail.status_code == 200
    assert detail.json()["content"] == chat.json()["answer"]
