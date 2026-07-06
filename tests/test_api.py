from fastapi.testclient import TestClient

from app.main import create_app


def test_health():
    client = TestClient(create_app())

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_import_index_and_chat(tmp_path):
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

    chat = client.post(
        "/chat",
        json={"repository_id": repository_id, "question": "import repository"},
    )
    assert chat.status_code == 200
    assert chat.json()["citations"][0]["path"] == "app.py"
