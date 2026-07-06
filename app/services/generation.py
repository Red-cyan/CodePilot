from collections import Counter

from app.schemas import ReportResponse
from app.services.llm import ChatMessage, LLMClient, default_llm_client
from app.services.repository import RepositoryService
from app.services.retriever import citation_from_chunk


class GenerationService:
    def __init__(
        self,
        repository_service: RepositoryService,
        llm_client: LLMClient | None = None,
    ) -> None:
        self._repository_service = repository_service
        self._llm = llm_client or default_llm_client()

    def readme(self, repository_id: str) -> ReportResponse:
        repository = self._repository_service.get(repository_id)
        modules = Counter(chunk.path.split("/")[0] for chunk in repository.chunks)
        language_badges = ", ".join(sorted(repository.languages)) or "source code"
        module_lines = "\n".join(f"- `{name}/`" for name, _ in modules.most_common(12))
        citations = [citation_from_chunk(chunk, 1.0) for chunk in repository.chunks[:5]]
        content = self._llm.complete(
            [
                ChatMessage(
                    role="system",
                    content=(
                        "你是技术文档工程师。请基于仓库元数据和代码片段，生成一份中文 README 草稿，"
                        "包含项目简介、功能、技术栈、启动方式、目录结构和测试说明。"
                    ),
                ),
                ChatMessage(
                    role="user",
                    content=(
                        f"仓库：{repository.name}\n"
                        f"语言：{language_badges}\n"
                        f"模块：\n{module_lines or '- No source modules detected'}\n"
                        f"索引文件数：{repository.files_indexed}\n"
                        f"索引 chunk 数：{repository.chunks_indexed}\n"
                        f"解析符号数：{len(repository.symbols)}\n\n"
                        f"代表代码片段：\n{self._format_citations(citations)}"
                    ),
                ),
            ]
        )
        return ReportResponse(
            repository_id=repository.id,
            title=f"README Draft: {repository.name}",
            content=content,
            citations=citations,
        )

    @staticmethod
    def _format_citations(citations: list) -> str:  # noqa: ANN401
        if not citations:
            return "未检索到相关代码片段。"
        return "\n\n".join(
            f"文件：{citation.path}:{citation.start_line}-{citation.end_line}\n"
            f"代码片段：\n{citation.preview}"
            for citation in citations
        )
