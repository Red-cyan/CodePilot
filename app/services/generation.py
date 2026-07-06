from collections import Counter

from app.schemas import ApiGenerationRequest, ReportResponse, UnitTestGenerationRequest
from app.services.llm import ChatMessage, LLMClient, default_llm_client
from app.services.repository import RepositoryService
from app.services.retriever import CodeRetriever, citation_from_chunk


class GenerationService:
    def __init__(
        self,
        repository_service: RepositoryService,
        llm_client: LLMClient | None = None,
    ) -> None:
        self._repository_service = repository_service
        self._llm = llm_client or default_llm_client()
        self._retriever = CodeRetriever()

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

    def api(self, payload: ApiGenerationRequest) -> ReportResponse:
        repository = self._repository_service.get(payload.repository_id)
        results = self._retriever.search(
            repository,
            f"{payload.requirement} {payload.style}",
            top_k=6,
        )
        if not results:
            results = [(chunk, 0.0) for chunk in repository.chunks[:6]]
        citations = [citation_from_chunk(chunk, score) for chunk, score in results]
        content = self._llm.complete(
            [
                ChatMessage(
                    role="system",
                    content=(
                        "你是资深后端工程师。请基于现有仓库代码风格和用户需求，"
                        "生成 API 实现方案。输出中文 Markdown，必须包含："
                        "接口设计、建议修改文件、核心代码草稿、错误处理、测试建议。"
                        "不要声称已经修改文件，只输出可供开发者应用的草稿。"
                    ),
                ),
                ChatMessage(
                    role="user",
                    content=(
                        f"仓库：{repository.name}\n"
                        f"需求：{payload.requirement}\n"
                        f"偏好风格：{payload.style}\n\n"
                        f"相关代码上下文：\n{self._format_citations(citations)}"
                    ),
                ),
            ],
            temperature=0.15,
        )
        return ReportResponse(
            repository_id=repository.id,
            title="API Generation Draft",
            content=content,
            citations=citations,
        )

    def unit_test(self, payload: UnitTestGenerationRequest) -> ReportResponse:
        repository = self._repository_service.get(payload.repository_id)
        results = self._retriever.search(repository, payload.target, top_k=6)
        if not results:
            results = [(chunk, 0.0) for chunk in repository.chunks[:6]]
        citations = [citation_from_chunk(chunk, score) for chunk, score in results]
        content = self._llm.complete(
            [
                ChatMessage(
                    role="system",
                    content=(
                        "你是测试工程师。请基于目标代码和仓库上下文生成单元测试草稿。"
                        "输出中文 Markdown，必须包含：测试文件路径建议、测试用例列表、"
                        "mock 策略、完整测试代码、运行命令。"
                    ),
                ),
                ChatMessage(
                    role="user",
                    content=(
                        f"仓库：{repository.name}\n"
                        f"测试目标：{payload.target}\n"
                        f"测试框架：{payload.framework}\n\n"
                        f"相关代码上下文：\n{self._format_citations(citations)}"
                    ),
                ),
            ],
            temperature=0.1,
        )
        return ReportResponse(
            repository_id=repository.id,
            title="Unit Test Generation Draft",
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
