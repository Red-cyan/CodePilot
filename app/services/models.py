from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(slots=True)
class Symbol:
    name: str
    kind: str
    path: str
    line: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "kind": self.kind,
            "path": self.path,
            "line": self.line,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "Symbol":
        return cls(
            name=str(data["name"]),
            kind=str(data["kind"]),
            path=str(data["path"]),
            line=int(data["line"]),
        )


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

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "repository_id": self.repository_id,
            "path": self.path,
            "language": self.language,
            "text": self.text,
            "start_line": self.start_line,
            "end_line": self.end_line,
            "content_hash": self.content_hash,
            "symbols": [symbol.to_dict() for symbol in self.symbols],
            "vector": self.vector,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "CodeChunk":
        return cls(
            id=str(data["id"]),
            repository_id=str(data["repository_id"]),
            path=str(data["path"]),
            language=str(data["language"]),
            text=str(data["text"]),
            start_line=int(data["start_line"]),
            end_line=int(data["end_line"]),
            content_hash=str(data["content_hash"]),
            symbols=[
                Symbol.from_dict(symbol)
                for symbol in data.get("symbols", [])
                if isinstance(symbol, dict)
            ],
            vector={
                str(token): float(score)
                for token, score in dict(data.get("vector", {})).items()
            },
        )


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

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "path": str(self.path),
            "branch": self.branch,
            "commit_hash": self.commit_hash,
            "files_indexed": self.files_indexed,
            "chunks_indexed": self.chunks_indexed,
            "languages": self.languages,
            "chunks": [chunk.to_dict() for chunk in self.chunks],
            "symbols": [symbol.to_dict() for symbol in self.symbols],
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "RepositoryState":
        return cls(
            id=str(data["id"]),
            name=str(data["name"]),
            path=Path(str(data["path"])),
            branch=data.get("branch"),
            commit_hash=data.get("commit_hash"),
            files_indexed=int(data.get("files_indexed", 0)),
            chunks_indexed=int(data.get("chunks_indexed", 0)),
            languages={
                str(language): int(count)
                for language, count in dict(data.get("languages", {})).items()
            },
            chunks=[
                CodeChunk.from_dict(chunk)
                for chunk in data.get("chunks", [])
                if isinstance(chunk, dict)
            ],
            symbols=[
                Symbol.from_dict(symbol)
                for symbol in data.get("symbols", [])
                if isinstance(symbol, dict)
            ],
        )
