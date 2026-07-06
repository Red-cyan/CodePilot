from fastapi import APIRouter, HTTPException

from app.schemas import (
    ArchitectureRequest,
    BugAnalysisRequest,
    ChatRequest,
    ImportRepositoryRequest,
    ImportRepositoryResponse,
    IndexRepositoryResponse,
    ReadmeRequest,
    ReportResponse,
    ReviewRequest,
)
from app.services.analysis import AnalysisService
from app.services.generation import GenerationService
from app.services.indexer import IndexerService
from app.services.repository import RepositoryService
from app.services.review import ReviewService

router = APIRouter()
repository_service = RepositoryService()
indexer_service = IndexerService(repository_service)
analysis_service = AnalysisService(repository_service)
review_service = ReviewService(repository_service)
generation_service = GenerationService(repository_service)


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


@router.get("/repositories", tags=["repositories"])
def list_repositories() -> list[dict[str, object]]:
    return [repo.model_dump() for repo in repository_service.list_repositories()]


@router.post("/chat", tags=["agents"])
def chat(payload: ChatRequest) -> dict[str, object]:
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


@router.post("/review", response_model=ReportResponse, tags=["agents"])
def review(payload: ReviewRequest) -> ReportResponse:
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
