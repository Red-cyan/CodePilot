import re
from collections import Counter

from app.schemas import BugAnalysisRequest, ChatRequest, ReportResponse
from app.services.repository import RepositoryService
from app.services.retriever import CodeRetriever, citation_from_chunk


class AnalysisService:
    def __init__(self, repository_service: RepositoryService) -> None:
        self._repository_service = repository_service
        self._retriever = CodeRetriever()

    def chat(self, payload: ChatRequest) -> dict[str, object]:
        repository = self._repository_service.get(payload.repository_id)
        results = self._retriever.search(repository, payload.question, payload.top_k)
        citations = [citation_from_chunk(chunk, score).model_dump() for chunk, score in results]
        if not citations:
            answer = (
                "No repository evidence was found for this question. "
                "Index the repository or narrow the query."
            )
        else:
            paths = ", ".join(citation["path"] for citation in citations)
            answer = (
                "Based on the indexed repository context, the most relevant evidence is in "
                f"{paths}. Review the cited snippets before making code changes."
            )
        return {
            "answer": answer,
            "citations": citations,
            "tool_trace": ["retriever", "context_builder"],
        }

    def architecture(self, repository_id: str) -> ReportResponse:
        repository = self._repository_service.get(repository_id)
        path_counter = Counter(chunk.path.split("/")[0] for chunk in repository.chunks)
        language_lines = "\n".join(
            f"- {language}: {count} files"
            for language, count in sorted(repository.languages.items())
        )
        module_lines = "\n".join(
            f"- {module}: {count} chunks" for module, count in path_counter.most_common(10)
        )
        symbol_lines = "\n".join(
            f"- `{symbol.kind}` {symbol.name} ({symbol.path}:{symbol.line})"
            for symbol in repository.symbols[:20]
        )
        content = (
            f"# Architecture Report: {repository.name}\n\n"
            "## Language Profile\n"
            f"{language_lines or '- No indexed source files'}\n\n"
            "## Main Modules\n"
            f"{module_lines or '- No modules detected'}\n\n"
            "## Key Symbols\n"
            f"{symbol_lines or '- No symbols detected'}\n\n"
            "## Notes\n"
            "- This report is generated from repository structure and parsed symbols.\n"
            "- Use it as a first-pass architecture map before deeper manual review.\n"
        )
        citations = [
            citation_from_chunk(chunk, 1.0)
            for chunk in repository.chunks[:5]
        ]
        return ReportResponse(
            repository_id=repository.id,
            title=f"Architecture Report: {repository.name}",
            content=content,
            citations=citations,
        )

    def bug(self, payload: BugAnalysisRequest) -> ReportResponse:
        repository = self._repository_service.get(payload.repository_id)
        query = self._bug_query(payload.error_log)
        results = self._retriever.search(repository, query, top_k=6)
        citations = [citation_from_chunk(chunk, score) for chunk, score in results]
        cited_paths = "\n".join(
            f"- {citation.path}:{citation.start_line}" for citation in citations
        )
        content = (
            "# Bug Analysis\n\n"
            "## Extracted Signal\n"
            f"`{query}`\n\n"
            "## Likely Relevant Code\n"
            f"{cited_paths or '- No matching code found'}\n\n"
            "## Suggested Investigation\n"
            "- Check the first cited file for the stack frame or symbol closest to the error.\n"
            "- Confirm input validation and boundary conditions around the failing call.\n"
            "- Add a regression test that reproduces the provided error log.\n"
        )
        return ReportResponse(
            repository_id=repository.id,
            title="Bug Analysis",
            content=content,
            citations=citations,
        )

    @staticmethod
    def _bug_query(error_log: str) -> str:
        file_hits = re.findall(r"([\w./\\-]+\.(?:py|js|ts|tsx|java|go|cpp|c))", error_log)
        symbols = re.findall(r"in ([A-Za-z_][A-Za-z0-9_]*)", error_log)
        errors = re.findall(r"([A-Za-z_]*Error|Exception)", error_log)
        return " ".join(file_hits + symbols + errors + [error_log[:300]])
