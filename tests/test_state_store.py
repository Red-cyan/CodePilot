from app.schemas import ImportMode, ImportRepositoryRequest
from app.services.indexer import IndexerService
from app.services.repository import RepositoryService
from app.services.state_store import RepositoryStateStore


def test_repository_state_persists_imported_and_indexed_data(tmp_path):
    repository_path = tmp_path / "repo"
    repository_path.mkdir()
    (repository_path / "service.py").write_text(
        "class Service:\n    def run(self):\n        return 'ok'\n",
        encoding="utf-8",
    )
    store_path = tmp_path / "state" / "repositories.json"

    service = RepositoryService(RepositoryStateStore(store_path))
    imported = service.import_repository(
        ImportRepositoryRequest(source=str(repository_path), mode=ImportMode.local)
    )
    repository_id = imported.repository.id
    IndexerService(service).index_repository(repository_id)

    restored_service = RepositoryService(RepositoryStateStore(store_path))
    restored = restored_service.get(repository_id)

    assert restored.name == "repo"
    assert restored.files_indexed == 1
    assert restored.chunks_indexed == 1
    assert restored.chunks[0].path == "service.py"
    assert restored.symbols[0].name == "Service"
