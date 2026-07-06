from dataclasses import dataclass
from pathlib import Path

from app.core.config import settings


@dataclass(frozen=True, slots=True)
class IndexPolicy:
    ignored_dirs: set[str]
    max_file_size: int

    @classmethod
    def from_settings(cls) -> "IndexPolicy":
        ignored_dirs = {
            item.strip()
            for item in settings.ignored_dirs.split(",")
            if item.strip()
        }
        return cls(
            ignored_dirs=ignored_dirs,
            max_file_size=settings.max_index_file_size,
        )

    def skip_reason(self, path: Path, root: Path) -> str | None:
        relative_parts = path.relative_to(root).parts
        if any(part in self.ignored_dirs for part in relative_parts):
            return "ignored_directory"
        if path.is_file() and path.stat().st_size > self.max_file_size:
            return "file_too_large"
        return None
