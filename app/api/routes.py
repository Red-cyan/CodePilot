from fastapi import APIRouter, HTTPException

from app.schemas import (
    ApiGenerationRequest,
    ArchitectureRequest,
    BugAnalysisRequest,
    ChatRequest,
    ChatResponse,
    CodeSearchRequest,
    CodeSearchResponse,
    DeleteRepositoryResponse,
    DiagnosticsResponse,
    FileContentResponse,
    FileTreeResponse,
    ImportRepositoryRequest,
    ImportRepositoryResponse,
    IndexRepositoryResponse,
    ReadmeRequest,
    ReportResponse,
    ReviewRequest,
    ReviewResponse,
    RunListResponse,
    RunRecord,
    SymbolListResponse,
    UnitTestGenerationRequest,
)
from app.services.analysis import AnalysisService
from app.services.browser import BrowserService
from app.services.diagnostics import DiagnosticsService
from app.services.generation import GenerationService
from app.services.indexer import IndexerService
from app.services.repository import RepositoryService
from app.services.review import ReviewService
from app.services.run_store import RunStore
from app.services.search import CodeSearchService

router = APIRouter()
repository_service = RepositoryService()
indexer_service = IndexerService(repository_service)
browser_service = BrowserService(repository_service)
search_service = CodeSearchService(repository_service)
run_store = RunStore()
diagnostics_service = DiagnosticsService(repository_service, run_store)
analysis_service = AnalysisService(repository_service, run_store=run_store)
review_service = ReviewService(repository_service, run_store=run_store)
generation_service = GenerationService(repository_service, run_store=run_store)


@router.post("/repositories/import", response_model=ImportRepositoryResponse, tags=["repositories"])
def import_repository(payload: ImportRepositoryRequest) -> ImportRepositoryResponse:
    try:
        return repository_service.import_repository(payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post(
    "/repositories/{repository_id}/index",
    response_model=IndexRepositoryResponse,
    tags=["repositories"],
)
def index_repository(repository_id: str) -> IndexRepositoryResponse:
    try:
        return indexer_service.index_repository(repository_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post(
    "/repositories/{repository_id}/reindex",
    response_model=IndexRepositoryResponse,
    tags=["repositories"],
)
def reindex_repository(repository_id: str) -> IndexRepositoryResponse:
    try:
        return indexer_service.index_repository(repository_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.delete(
    "/repositories/{repository_id}",
    response_model=DeleteRepositoryResponse,
    tags=["repositories"],
)
def delete_repository(repository_id: str) -> DeleteRepositoryResponse:
    try:
        repository_service.delete(repository_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return DeleteRepositoryResponse(
        repository_id=repository_id,
        deleted=True,
        message="已删除 CodePilot 中的仓库记录和索引状态，未删除磁盘源码目录。",
    )


@router.get("/repositories", tags=["repositories"])
def list_repositories() -> list[dict[str, object]]:
    return [repo.model_dump() for repo in repository_service.list_repositories()]


@router.get("/diagnostics", response_model=DiagnosticsResponse, tags=["system"])
def diagnostics() -> DiagnosticsResponse:
    return diagnostics_service.summary()


@router.get(
    "/repositories/{repository_id}/tree",
    response_model=FileTreeResponse,
    tags=["repositories"],
)
def get_repository_tree(repository_id: str) -> FileTreeResponse:
    try:
        return browser_service.tree(repository_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get(
    "/repositories/{repository_id}/files",
    response_model=FileContentResponse,
    tags=["repositories"],
)
def get_repository_file(repository_id: str, path: str) -> FileContentResponse:
    try:
        return browser_service.file(repository_id, path)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get(
    "/repositories/{repository_id}/symbols",
    response_model=SymbolListResponse,
    tags=["repositories"],
)
def get_repository_symbols(repository_id: str) -> SymbolListResponse:
    try:
        return browser_service.symbols(repository_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.get("/runs", response_model=RunListResponse, tags=["runs"])
def list_runs(repository_id: str | None = None) -> RunListResponse:
    return RunListResponse(runs=run_store.list(repository_id))


@router.get("/runs/{run_id}", response_model=RunRecord, tags=["runs"])
def get_run(run_id: str) -> RunRecord:
    try:
        return run_store.get(run_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/search/code", response_model=CodeSearchResponse, tags=["search"])
def search_code(payload: CodeSearchRequest) -> CodeSearchResponse:
    try:
        return search_service.search(payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/chat", response_model=ChatResponse, tags=["agents"])
def chat(payload: ChatRequest) -> ChatResponse:
    try:
        return analysis_service.chat(payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/analyze/architecture", response_model=ReportResponse, tags=["agents"])
def analyze_architecture(payload: ArchitectureRequest) -> ReportResponse:
    try:
        return analysis_service.architecture(payload.repository_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/analyze/bug", response_model=ReportResponse, tags=["agents"])
def analyze_bug(payload: BugAnalysisRequest) -> ReportResponse:
    try:
        return analysis_service.bug(payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/review", response_model=ReviewResponse, tags=["agents"])
def review(payload: ReviewRequest) -> ReviewResponse:
    try:
        return review_service.review(payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/generate/readme", response_model=ReportResponse, tags=["agents"])
def generate_readme(payload: ReadmeRequest) -> ReportResponse:
    try:
        return generation_service.readme(payload.repository_id)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/generate/api", response_model=ReportResponse, tags=["agents"])
def generate_api(payload: ApiGenerationRequest) -> ReportResponse:
    try:
        return generation_service.api(payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/generate/test", response_model=ReportResponse, tags=["agents"])
def generate_unit_test(payload: UnitTestGenerationRequest) -> ReportResponse:
    try:
        return generation_service.unit_test(payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
