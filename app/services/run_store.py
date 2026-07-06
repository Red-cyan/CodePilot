import json
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from uuid import uuid4

from app.core.config import settings
from app.schemas import Citation, RunRecord


class RunTimer:
    def __init__(self) -> None:
        self._started_at = perf_counter()

    def elapsed_ms(self) -> int:
        return int((perf_counter() - self._started_at) * 1000)


class RunStore:
    def __init__(self, path: Path | None = None) -> None:
        self._path = path or settings.storage_dir / "runs.json"
        self._runs: dict[str, RunRecord] = self._load()

    def record(
        self,
        *,
        repository_id: str,
        kind: str,
        title: str,
        content: str,
        citations: list[Citation],
        tool_trace: list[str],
        duration_ms: int,
    ) -> RunRecord:
        run = RunRecord(
            id=str(uuid4()),
            repository_id=repository_id,
            kind=kind,
            title=title,
            content=content,
            citations=citations,
            tool_trace=tool_trace,
            duration_ms=duration_ms,
            created_at=datetime.now(UTC).isoformat(),
        )
        self._runs[run.id] = run
        self._save()
        return run

    def list(self, repository_id: str | None = None) -> list[RunRecord]:
        runs = sorted(self._runs.values(), key=lambda run: run.created_at, reverse=True)
        if repository_id is None:
            return runs
        return [run for run in runs if run.repository_id == repository_id]

    def get(self, run_id: str) -> RunRecord:
        if run_id not in self._runs:
            raise KeyError(f"Run {run_id} was not found.")
        return self._runs[run_id]

    def _load(self) -> dict[str, RunRecord]:
        if not self._path.exists():
            return {}
        try:
            payload = json.loads(self._path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}
        runs = payload.get("runs", []) if isinstance(payload, dict) else []
        records: dict[str, RunRecord] = {}
        for run in runs:
            if not isinstance(run, dict):
                continue
            record = RunRecord.model_validate(run)
            records[record.id] = record
        return records

    def _save(self) -> None:
        self._path.parent.mkdir(parents=True, exist_ok=True)
        payload = {"runs": [run.model_dump() for run in self.list()]}
        temporary_path = self._path.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        temporary_path.replace(self._path)
