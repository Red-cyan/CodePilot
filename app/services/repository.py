from pathlib import Path
from uuid import uuid4

from git import Repo

from app.core.config import settings
from app.schemas import (
    ImportMode,
    ImportRepositoryRequest,
    ImportRepositoryResponse,
    RepositorySummary,
)
from app.services.models import RepositoryState
from app.services.state_store import RepositoryStateStore


class RepositoryService:
    def __init__(self, state_store: RepositoryStateStore | None = None) -> None:
        self._state_store = state_store or RepositoryStateStore()
        self._repositories: dict[str, RepositoryState] = self._state_store.load()

    def import_repository(self, payload: ImportRepositoryRequest) -> ImportRepositoryResponse:
        path = self._resolve_source(payload)
        repository_id = str(uuid4())
        state = RepositoryState(
            id=repository_id,
            name=path.name,
            path=path,
            branch=payload.branch or self._current_branch(path),
            commit_hash=self._current_commit(path),
        )
        self._repositories[repository_id] = state
        self.save()
        return ImportRepositoryResponse(repository=self._summary(state))

    def list_repositories(self) -> list[RepositorySummary]:
        return [self._summary(repo) for repo in self._repositories.values()]

    def states(self) -> list[RepositoryState]:
        return list(self._repositories.values())

    def get(self, repository_id: str) -> RepositoryState:
        if repository_id not in self._repositories:
            raise KeyError(f"Repository {repository_id} was not found.")
        return self._repositories[repository_id]

    def delete(self, repository_id: str) -> None:
        if repository_id not in self._repositories:
            raise KeyError(f"Repository {repository_id} was not found.")
        del self._repositories[repository_id]
        self.save()

    def save(self) -> None:
        self._state_store.save(self._repositories)

    def _resolve_source(self, payload: ImportRepositoryRequest) -> Path:
        if payload.mode == ImportMode.local:
            path = Path(payload.source).expanduser().resolve()
            if not path.exists() or not path.is_dir():
                raise ValueError(f"Local repository path does not exist: {payload.source}")
            return path

        settings.storage_dir.mkdir(parents=True, exist_ok=True)
        target = settings.storage_dir / "repos" / self._repo_name_from_url(payload.source)
        if target.exists():
            return target.resolve()
        if payload.branch:
            Repo.clone_from(payload.source, target, branch=payload.branch)
        else:
            Repo.clone_from(payload.source, target)
        return target.resolve()

    @staticmethod
    def _repo_name_from_url(url: str) -> str:
        name = url.rstrip("/").split("/")[-1]
        return name.removesuffix(".git") or "repository"

    @staticmethod
    def _current_branch(path: Path) -> str | None:
        try:
            return Repo(path).active_branch.name
        except Exception:
            return None

    @staticmethod
    def _current_commit(path: Path) -> str | None:
        try:
            return Repo(path).head.commit.hexsha
        except Exception:
            return None

    @staticmethod
    def _summary(state: RepositoryState) -> RepositorySummary:
        return RepositorySummary(
            id=state.id,
            name=state.name,
            path=str(state.path),
            branch=state.branch,
            commit_hash=state.commit_hash,
            files_indexed=state.files_indexed,
            chunks_indexed=state.chunks_indexed,
            languages=state.languages,
        )
