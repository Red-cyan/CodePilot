from enum import StrEnum

from pydantic import BaseModel, Field


class ImportMode(StrEnum):
    local = "local"
    git = "git"


class ImportRepositoryRequest(BaseModel):
    source: str = Field(..., description="Local repository path or Git URL.")
    mode: ImportMode = ImportMode.local
    branch: str | None = None


class RepositorySummary(BaseModel):
    id: str
    name: str
    path: str
    branch: str | None = None
    commit_hash: str | None = None
    files_indexed: int = 0
    chunks_indexed: int = 0
    languages: dict[str, int] = Field(default_factory=dict)


class ImportRepositoryResponse(BaseModel):
    repository: RepositorySummary


class IndexRepositoryResponse(BaseModel):
    repository_id: str
    files_indexed: int
    chunks_indexed: int
    symbols_indexed: int


class ChatRequest(BaseModel):
    repository_id: str
    question: str
    top_k: int = 5


class ArchitectureRequest(BaseModel):
    repository_id: str


class BugAnalysisRequest(BaseModel):
    repository_id: str
    error_log: str


class ReviewRequest(BaseModel):
    repository_id: str
    diff: str


class ReadmeRequest(BaseModel):
    repository_id: str


class ApiGenerationRequest(BaseModel):
    repository_id: str
    requirement: str = Field(..., description="API feature requirement to generate.")
    style: str = Field(
        default="FastAPI + service + schema + pytest",
        description="Preferred implementation style or framework conventions.",
    )


class UnitTestGenerationRequest(BaseModel):
    repository_id: str
    target: str = Field(..., description="File path, symbol name, or behavior to test.")
    framework: str = Field(default="pytest", description="Preferred test framework.")


class Citation(BaseModel):
    path: str
    start_line: int
    end_line: int
    score: float
    preview: str


class ReportResponse(BaseModel):
    repository_id: str
    title: str
    content: str
    citations: list[Citation] = Field(default_factory=list)
