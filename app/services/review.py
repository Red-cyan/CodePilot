from app.schemas import ReportResponse, ReviewRequest
from app.services.llm import ChatMessage, LLMClient, default_llm_client
from app.services.repository import RepositoryService
from app.services.retriever import CodeRetriever, citation_from_chunk
from app.services.run_store import RunStore, RunTimer


class ReviewService:
    def __init__(
        self,
        repository_service: RepositoryService,
        llm_client: LLMClient | None = None,
        run_store: RunStore | None = None,
    ) -> None:
        self._repository_service = repository_service
        self._retriever = CodeRetriever()
        self._llm = llm_client or default_llm_client()
        self._run_store = run_store

    def review(self, payload: ReviewRequest) -> ReportResponse:
        timer = RunTimer()
        repository = self._repository_service.get(payload.repository_id)
        changed_terms = " ".join(
            line[1:].strip()
            for line in payload.diff.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )
        results = self._retriever.search(repository, changed_terms or payload.diff, top_k=5)
        citations = [citation_from_chunk(chunk, score) for chunk, score in results]
        findings = self._findings(payload.diff)
        content = self._llm.complete(
            [
                ChatMessage(
                    role="system",
                    content=(
                        "你是严格的软件工程代码审查 Agent。请基于 git diff、"
                        "确定性检查结果和相关仓库代码，用中文输出 PR Review。"
                        "优先指出 bug、安全、性能、可维护性和测试缺口。"
                    ),
                ),
                ChatMessage(
                    role="user",
                    content=(
                        f"仓库：{repository.name}\n\n"
                        f"git diff：\n{payload.diff}\n\n"
                        f"确定性检查：\n{findings}\n\n"
                        f"初始评分：{self._score(payload.diff)}/100\n\n"
                        f"相关代码：\n{self._format_citations(citations)}"
                    ),
                ),
            ]
        )
        response = ReportResponse(
            repository_id=repository.id,
            title="Pull Request Review",
            content=content,
            citations=citations,
        )
        if self._run_store is not None:
            self._run_store.record(
                repository_id=response.repository_id,
                kind="pr_review",
                title=response.title,
                content=response.content,
                citations=response.citations,
                tool_trace=["diff_parser", "retriever", "llm"],
                duration_ms=timer.elapsed_ms(),
            )
        return response

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

    @staticmethod
    def _format_citations(citations: list) -> str:  # noqa: ANN401
        if not citations:
            return "未检索到相关代码片段。"
        return "\n\n".join(
            f"文件：{citation.path}:{citation.start_line}-{citation.end_line}\n"
            f"相关度：{citation.score}\n"
            f"代码片段：\n{citation.preview}"
            for citation in citations
        )
