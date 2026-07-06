from pathlib import Path

from app.schemas import (
    FileContentResponse,
    FileTreeItem,
    FileTreeResponse,
    SymbolListResponse,
    SymbolResponse,
)
from app.services.parser import IGNORED_DIRS, LANGUAGE_BY_SUFFIX
from app.services.repository import RepositoryService


class BrowserService:
    def __init__(self, repository_service: RepositoryService) -> None:
        self._repository_service = repository_service

    def tree(self, repository_id: str) -> FileTreeResponse:
        repository = self._repository_service.get(repository_id)
        items: list[FileTreeItem] = []
        for path in sorted(repository.path.rglob("*")):
            if self._is_ignored(path, repository.path):
                continue
            relative_path = path.relative_to(repository.path).as_posix()
            if path.is_dir():
                items.append(
                    FileTreeItem(
                        path=relative_path,
                        name=path.name,
                        type="directory",
                    )
                )
                continue
            language = LANGUAGE_BY_SUFFIX.get(path.suffix.lower())
            if language is None:
                continue
            items.append(
                FileTreeItem(
                    path=relative_path,
                    name=path.name,
                    type="file",
                    language=language,
                    size=path.stat().st_size,
                )
            )
        return FileTreeResponse(repository_id=repository.id, items=items)

    def file(self, repository_id: str, relative_path: str) -> FileContentResponse:
        repository = self._repository_service.get(repository_id)
        path = self._resolve_safe_path(repository.path, relative_path)
        if not path.exists() or not path.is_file():
            raise FileNotFoundError(f"File {relative_path} was not found.")
        language = LANGUAGE_BY_SUFFIX.get(path.suffix.lower())
        if language is None:
            raise ValueError(f"File {relative_path} is not a supported source file.")
        if path.stat().st_size > 512_000:
            raise ValueError(f"File {relative_path} is too large to read.")
        try:
            content = path.read_text(encoding="utf-8")
        except UnicodeDecodeError as exc:
            raise ValueError(f"File {relative_path} is not UTF-8 text.") from exc
        return FileContentResponse(
            repository_id=repository.id,
            path=path.relative_to(repository.path).as_posix(),
            language=language,
            content=content,
            size=path.stat().st_size,
        )

    def symbols(self, repository_id: str) -> SymbolListResponse:
        repository = self._repository_service.get(repository_id)
        symbols = [
            SymbolResponse(
                name=symbol.name,
                kind=symbol.kind,
                path=symbol.path,
                line=symbol.line,
            )
            for symbol in repository.symbols
        ]
        return SymbolListResponse(repository_id=repository.id, symbols=symbols)

    @staticmethod
    def _is_ignored(path: Path, root: Path) -> bool:
        relative_parts = path.relative_to(root).parts
        return any(part in IGNORED_DIRS for part in relative_parts)

    @staticmethod
    def _resolve_safe_path(root: Path, relative_path: str) -> Path:
        target = (root / relative_path).resolve()
        root = root.resolve()
        if target != root and root not in target.parents:
            raise ValueError("File path must stay inside the repository root.")
        return target
