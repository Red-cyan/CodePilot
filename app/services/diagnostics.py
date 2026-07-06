from app.core.config import settings
from app.schemas import DiagnosticsResponse, LLMStatus, RepositoryStats, StorageStatus
from app.services.repository import RepositoryService
from app.services.run_store import RunStore


class DiagnosticsService:
    def __init__(self, repository_service: RepositoryService, run_store: RunStore) -> None:
        self._repository_service = repository_service
        self._run_store = run_store

    def summary(self) -> DiagnosticsResponse:
        repositories = self._repository_service.states()
        languages: dict[str, int] = {}
        for repository in repositories:
            for language, count in repository.languages.items():
                languages[language] = languages.get(language, 0) + count
        repository_stats = RepositoryStats(
            repository_count=len(repositories),
            files_indexed=sum(repository.files_indexed for repository in repositories),
            chunks_indexed=sum(repository.chunks_indexed for repository in repositories),
            symbols_indexed=sum(len(repository.symbols) for repository in repositories),
            languages=languages,
        )
        repository_state_file = settings.storage_dir / "repositories.json"
        run_state_file = settings.storage_dir / "runs.json"
        return DiagnosticsResponse(
            status="ok",
            environment=settings.env,
            repositories=repository_stats,
            run_count=len(self._run_store.list()),
            llm=LLMStatus(
                provider="deepseek",
                model=settings.deepseek_model,
                configured=bool(settings.deepseek_api_key),
                base_url=settings.deepseek_base_url,
            ),
            storage=StorageStatus(
                storage_dir=str(settings.storage_dir),
                repository_state_file=str(repository_state_file),
                run_state_file=str(run_state_file),
                repository_state_exists=repository_state_file.exists(),
                run_state_exists=run_state_file.exists(),
            ),
        )
