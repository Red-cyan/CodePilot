import json
from pathlib import Path

from app.core.config import settings
from app.services.models import RepositoryState


class RepositoryStateStore:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or settings.storage_dir / "repositories.json"

    def load(self) -> dict[str, RepositoryState]:
        if not self._path.exists():
            return {}
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        repositories = payload.get("repositories", []) if isinstance(payload, dict) else []
        states: dict[str, RepositoryState] = {}
        for repository in repositories:
            if not isinstance(repository, dict):
                continue
            state = RepositoryState.from_dict(repository)
            states[state.id] = state
        return states

    def save(self, repositories: dict[str, RepositoryState]) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "repositories": [
                repository.to_dict()
                for repository in sorted(repositories.values(), key=lambda item: item.name)
            ]
        }
        temporary_path = self._path.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary_path.replace(self._path)
