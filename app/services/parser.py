import ast
import hashlib
from pathlib import Path

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


class RepositoryParser:
    def scan(
        self,
        repository_id: str,
        root: Path,
    ) -> tuple[list[CodeChunk], list[Symbol], dict[str, int]]:
        chunks: list[CodeChunk] = []
        symbols: list[Symbol] = []
        languages: dict[str, int] = {}
        for path in sorted(root.rglob("*")):
            if not path.is_file() or self._is_ignored(path, root):
                continue
            language = LANGUAGE_BY_SUFFIX.get(path.suffix.lower())
            if language is None:
                continue
            text = self._read_text(path)
            if not text:
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
        return chunks, symbols, languages

    @staticmethod
    def _is_ignored(path: Path, root: Path) -> bool:
        relative_parts = path.relative_to(root).parts
        return any(part in IGNORED_DIRS for part in relative_parts)

    @staticmethod
    def _read_text(path: Path) -> str:
        try:
            if path.stat().st_size > 512_000:
                return ""
            return path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            return ""

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
