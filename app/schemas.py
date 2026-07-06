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


class RepositoryStats(BaseModel):
    repository_count: int
    files_indexed: int
    chunks_indexed: int
    symbols_indexed: int
    languages: dict[str, int] = Field(default_factory=dict)


class LLMStatus(BaseModel):
    provider: str
    model: str
    configured: bool
    base_url: str


class StorageStatus(BaseModel):
    storage_dir: str
    repository_state_file: str
    run_state_file: str
    repository_state_exists: bool
    run_state_exists: bool


class DiagnosticsResponse(BaseModel):
    status: str
    environment: str
    repositories: RepositoryStats
    run_count: int
    llm: LLMStatus
    storage: StorageStatus


class FileTreeItem(BaseModel):
    path: str
    name: str
    type: str
    language: str | None = None
    size: int | None = None


class FileTreeResponse(BaseModel):
    repository_id: str
    items: list[FileTreeItem]


class FileContentResponse(BaseModel):
    repository_id: str
    path: str
    language: str | None = None
    content: str
    size: int


class SymbolResponse(BaseModel):
    name: str
    kind: str
    path: str
    line: int


class SymbolListResponse(BaseModel):
    repository_id: str
    symbols: list[SymbolResponse]


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


class ReviewIssue(BaseModel):
    category: str
    severity: str
    message: str
    suggestion: str
    line_hint: str | None = None


class ReviewResponse(BaseModel):
    repository_id: str
    title: str
    content: str
    score: int
    summary: str
    issues: list[ReviewIssue] = Field(default_factory=list)
    citations: list["Citation"] = Field(default_factory=list)


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


class SearchMode(StrEnum):
    semantic = "semantic"
    keyword = "keyword"
    symbol = "symbol"


class CodeSearchRequest(BaseModel):
    repository_id: str
    query: str
    mode: SearchMode = SearchMode.semantic
    top_k: int = Field(default=5, ge=1, le=20)


class CodeSearchHit(BaseModel):
    path: str
    start_line: int
    end_line: int
    score: float
    language: str | None = None
    kind: str
    preview: str


class CodeSearchResponse(BaseModel):
    repository_id: str
    query: str
    mode: SearchMode
    hits: list[CodeSearchHit]


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


class ChatResponse(BaseModel):
    repository_id: str
    answer: str
    citations: list[Citation] = Field(default_factory=list)
    tool_trace: list[str] = Field(default_factory=list)


class RunRecord(BaseModel):
    id: str
    repository_id: str
    kind: str
    title: str
    content: str
    citations: list[Citation] = Field(default_factory=list)
    tool_trace: list[str] = Field(default_factory=list)
    duration_ms: int
    created_at: str


class RunListResponse(BaseModel):
    runs: list[RunRecord]
