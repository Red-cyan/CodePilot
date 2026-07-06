from dataclasses import dataclass, field
from pathlib import Path


@dataclass(slots=True)
class Symbol:
    name: str
    kind: str
    path: str
    line: int


@dataclass(slots=True)
class CodeChunk:
    id: str
    repository_id: str
    path: str
    language: str
    text: str
    start_line: int
    end_line: int
    content_hash: str
    symbols: list[Symbol] = field(default_factory=list)
    vector: dict[str, float] = field(default_factory=dict)


@dataclass(slots=True)
class RepositoryState:
    id: str
    name: str
    path: Path
    branch: str | None = None
    commit_hash: str | None = None
    files_indexed: int = 0
    chunks_indexed: int = 0
    languages: dict[str, int] = field(default_factory=dict)
    chunks: list[CodeChunk] = field(default_factory=list)
    symbols: list[Symbol] = field(default_factory=list)
