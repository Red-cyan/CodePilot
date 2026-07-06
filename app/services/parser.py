import ast
import hashlib
from dataclasses import dataclass, field
from pathlib import Path

from app.services.index_policy import IndexPolicy
from app.services.models import CodeChunk, Symbol

LANGUAGE_BY_SUFFIX = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".java": "java",
    ".go": "go",
    ".c": "c",
    ".cc": "cpp",
    ".cpp": "cpp",
    ".h": "c",
    ".hpp": "cpp",
}

IGNORED_DIRS = {
    ".git",
    ".idea",
    ".venv",
    "__pycache__",
    "node_modules",
    "dist",
    "build",
    "target",
    ".pytest_cache",
    ".ruff_cache",
}


@dataclass(slots=True)
class ParseResult:
    chunks: list[CodeChunk]
    symbols: list[Symbol]
    languages: dict[str, int]
    files_scanned: int = 0
    skipped_files: int = 0
    skip_reasons: dict[str, int] = field(default_factory=dict)


class RepositoryParser:
    def __init__(self, policy: IndexPolicy | None = None) -> None:
        self._policy = policy or IndexPolicy.from_settings()

    def scan(
        self,
        repository_id: str,
        root: Path,
    ) -> ParseResult:
        chunks: list[CodeChunk] = []
        symbols: list[Symbol] = []
        languages: dict[str, int] = {}
        files_scanned = 0
        skipped_files = 0
        skip_reasons: dict[str, int] = {}
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            files_scanned += 1
            reason = self._policy.skip_reason(path, root)
            if reason is not None:
                skipped_files += 1
                skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
                continue
            language = LANGUAGE_BY_SUFFIX.get(path.suffix.lower())
            if language is None:
                skipped_files += 1
                skip_reasons["unsupported_extension"] = (
                    skip_reasons.get("unsupported_extension", 0) + 1
                )
                continue
            text, reason = self._read_text(path)
            if reason is not None:
                skipped_files += 1
                skip_reasons[reason] = skip_reasons.get(reason, 0) + 1
                continue
            relative_path = path.relative_to(root).as_posix()
            file_symbols = self._extract_symbols(relative_path, language, text)
            symbols.extend(file_symbols)
            file_chunks = self._chunk_file(
                repository_id,
                relative_path,
                language,
                text,
                file_symbols,
            )
            chunks.extend(file_chunks)
            languages[language] = languages.get(language, 0) + 1
        return ParseResult(
            chunks=chunks,
            symbols=symbols,
            languages=languages,
            files_scanned=files_scanned,
            skipped_files=skipped_files,
            skip_reasons=skip_reasons,
        )

    @staticmethod
    def _read_text(path: Path) -> tuple[str, str | None]:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return "", "non_utf8"
        if not text:
            return "", "empty_file"
        return text, None

    @staticmethod
    def _extract_symbols(path: str, language: str, text: str) -> list[Symbol]:
        if language != "python":
            return []
        try:
            tree = ast.parse(text)
        except SyntaxError:
            return []
        symbols: list[Symbol] = []
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                symbols.append(Symbol(name=node.name, kind="class", path=path, line=node.lineno))
            elif isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef):
                symbols.append(Symbol(name=node.name, kind="function", path=path, line=node.lineno))
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    symbols.append(
                        Symbol(name=alias.name, kind="import", path=path, line=node.lineno)
                    )
            elif isinstance(node, ast.ImportFrom) and node.module:
                symbols.append(Symbol(name=node.module, kind="import", path=path, line=node.lineno))
        return symbols

    @staticmethod
    def _chunk_file(
        repository_id: str,
        path: str,
        language: str,
        text: str,
        symbols: list[Symbol],
        max_lines: int = 80,
    ) -> list[CodeChunk]:
        lines = text.splitlines()
        chunks: list[CodeChunk] = []
        for index in range(0, len(lines), max_lines):
            start_line = index + 1
            end_line = min(index + max_lines, len(lines))
            chunk_text = "\n".join(lines[index:end_line])
            content_hash = hashlib.sha256(chunk_text.encode("utf-8")).hexdigest()
            chunk_symbols = [
                symbol for symbol in symbols if start_line <= symbol.line <= end_line
            ]
            chunks.append(
                CodeChunk(
                    id=f"{path}:{start_line}:{content_hash[:12]}",
                    repository_id=repository_id,
                    path=path,
                    language=language,
                    text=chunk_text,
                    start_line=start_line,
                    end_line=end_line,
                    content_hash=content_hash,
                    symbols=chunk_symbols,
                )
            )
        return chunks
