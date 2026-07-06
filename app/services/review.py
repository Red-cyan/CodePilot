from app.schemas import ReportResponse, ReviewRequest
from app.services.repository import RepositoryService
from app.services.retriever import CodeRetriever, citation_from_chunk


class ReviewService:
    def __init__(self, repository_service: RepositoryService) -> None:
        self._repository_service = repository_service
        self._retriever = CodeRetriever()

    def review(self, payload: ReviewRequest) -> ReportResponse:
        repository = self._repository_service.get(payload.repository_id)
        changed_terms = " ".join(
            line[1:].strip()
            for line in payload.diff.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )
        results = self._retriever.search(repository, changed_terms or payload.diff, top_k=5)
        citations = [citation_from_chunk(chunk, score) for chunk, score in results]
        findings = self._findings(payload.diff)
        content = (
            "# Pull Request Review\n\n"
            "## Findings\n"
            f"{findings}\n\n"
            "## Score\n"
            f"{self._score(payload.diff)}/100\n\n"
            "## Review Guidance\n"
            "- Verify behavior changes with focused tests.\n"
            "- Check cited files for related existing patterns before merging.\n"
            "- Keep generated or broad formatting changes out of feature diffs.\n"
        )
        return ReportResponse(
            repository_id=repository.id,
            title="Pull Request Review",
            content=content,
            citations=citations,
        )

    @staticmethod
    def _findings(diff: str) -> str:
        findings: list[str] = []
        if "password" in diff.lower() or "secret" in diff.lower():
            findings.append(
                "- Security: diff contains credential-like words; verify no secrets are committed."
            )
        if "except Exception" in diff:
            findings.append(
                "- Maintainability: broad exception handling may hide actionable failures."
            )
        if "TODO" in diff or "FIXME" in diff:
            findings.append(
                "- Maintainability: unresolved TODO/FIXME comments should be tracked or resolved."
            )
        if "print(" in diff:
            findings.append("- Style: replace debug prints with structured logging.")
        return (
            "\n".join(findings)
            if findings
            else "- No deterministic issues detected in the diff."
        )

    @staticmethod
    def _score(diff: str) -> int:
        score = 90
        for marker in ("password", "secret", "except Exception", "TODO", "FIXME", "print("):
            if marker.lower() in diff.lower():
                score -= 8
        return max(score, 50)
