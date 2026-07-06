import re
from collections import Counter

from app.schemas import BugAnalysisRequest, ChatRequest, ChatResponse, ReportResponse
from app.services.llm import ChatMessage, LLMClient, default_llm_client
from app.services.repository import RepositoryService
from app.services.retriever import CodeRetriever, citation_from_chunk
from app.services.run_store import RunStore, RunTimer


class AnalysisService:
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

    def chat(self, payload: ChatRequest) -> ChatResponse:
        timer = RunTimer()
        repository = self._repository_service.get(payload.repository_id)
        results = self._retriever.search(repository, payload.question, payload.top_k)
        citations = [citation_from_chunk(chunk, score) for chunk, score in results]
        citation_context = self._format_citations(
            [citation.model_dump() for citation in citations]
        )
        answer = self._llm.complete(
            [
                ChatMessage(
                    role="system",
                    content=(
                        "你是 CodePilot，一个软件工程 Agent。请只基于给定的仓库上下文回答，"
                        "如果上下文不足，要明确说明缺少依据。回答使用中文，结构清晰，"
                        "并引用相关文件路径。"
                    ),
                ),
                ChatMessage(
                    role="user",
                    content=(
                        f"用户问题：{payload.question}\n\n"
                        f"仓库名称：{repository.name}\n\n"
                        f"检索上下文：\n{citation_context}"
                    ),
                ),
            ]
        )
        response = ChatResponse(
            repository_id=repository.id,
            answer=answer,
            citations=citations,
            tool_trace=["retriever", "context_builder", "llm"],
        )
        self._record_run(
            repository_id=repository.id,
            kind="chat",
            title=f"Chat: {payload.question[:80]}",
            content=answer,
            citations=citations,
            tool_trace=response.tool_trace,
            duration_ms=timer.elapsed_ms(),
        )
        return response

    def architecture(self, repository_id: str) -> ReportResponse:
        timer = RunTimer()
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
        citations = [
            citation_from_chunk(chunk, 1.0)
            for chunk in repository.chunks[:5]
        ]
        content = self._llm.complete(
            [
                ChatMessage(
                    role="system",
                    content=(
                        "你是资深软件架构师。请根据仓库语言分布、模块和符号信息，"
                        "生成一份中文 Markdown 架构分析报告。"
                    ),
                ),
                ChatMessage(
                    role="user",
                    content=(
                        f"仓库：{repository.name}\n\n"
                        f"语言分布：\n{language_lines or '- No indexed source files'}\n\n"
                        f"主要模块：\n{module_lines or '- No modules detected'}\n\n"
                        f"关键符号：\n{symbol_lines or '- No symbols detected'}\n\n"
                        f"引用片段：\n{self._format_citations([c.model_dump() for c in citations])}"
                    ),
                ),
            ]
        )
        response = ReportResponse(
            repository_id=repository.id,
            title=f"Architecture Report: {repository.name}",
            content=content,
            citations=citations,
        )
        self._record_report("architecture", response, timer.elapsed_ms())
        return response

    def bug(self, payload: BugAnalysisRequest) -> ReportResponse:
        timer = RunTimer()
        repository = self._repository_service.get(payload.repository_id)
        query = self._bug_query(payload.error_log)
        results = self._retriever.search(repository, query, top_k=6)
        citations = [citation_from_chunk(chunk, score) for chunk, score in results]
        cited_paths = "\n".join(
            f"- {citation.path}:{citation.start_line}" for citation in citations
        )
        content = self._llm.complete(
            [
                ChatMessage(
                    role="system",
                    content=(
                        "你是资深后端排障工程师。请基于错误日志和检索到的代码上下文，"
                        "输出中文 Markdown Bug 分析，包含可能原因、相关代码、"
                        "修复建议和回归测试建议。"
                    ),
                ),
                ChatMessage(
                    role="user",
                    content=(
                        f"错误日志：\n{payload.error_log}\n\n"
                        f"提取信号：{query}\n\n"
                        f"相关代码：\n{cited_paths or '- No matching code found'}\n\n"
                        f"引用片段：\n{self._format_citations([c.model_dump() for c in citations])}"
                    ),
                ),
            ]
        )
        response = ReportResponse(
            repository_id=repository.id,
            title="Bug Analysis",
            content=content,
            citations=citations,
        )
        self._record_report("bug_analysis", response, timer.elapsed_ms())
        return response

    @staticmethod
    def _bug_query(error_log: str) -> str:
        file_hits = re.findall(r"([\w./\\-]+\.(?:py|js|ts|tsx|java|go|cpp|c))", error_log)
        symbols = re.findall(r"in ([A-Za-z_][A-Za-z0-9_]*)", error_log)
        errors = re.findall(r"([A-Za-z_]*Error|Exception)", error_log)
        return " ".join(file_hits + symbols + errors + [error_log[:300]])

    @staticmethod
    def _format_citations(citations: list[dict[str, object]]) -> str:
        if not citations:
            return "未检索到相关代码片段。"
        blocks = []
        for citation in citations:
            blocks.append(
                f"文件：{citation['path']}:{citation['start_line']}-{citation['end_line']}\n"
                f"相关度：{citation['score']}\n"
                f"代码片段：\n{citation['preview']}"
            )
        return "\n\n---\n\n".join(blocks)

    def _record_report(self, kind: str, response: ReportResponse, duration_ms: int) -> None:
        self._record_run(
            repository_id=response.repository_id,
            kind=kind,
            title=response.title,
            content=response.content,
            citations=response.citations,
            tool_trace=["retriever", "context_builder", "llm"],
            duration_ms=duration_ms,
        )

    def _record_run(
        self,
        *,
        repository_id: str,
        kind: str,
        title: str,
        content: str,
        citations: list,
        tool_trace: list[str],
        duration_ms: int,
    ) -> None:
        if self._run_store is None:
            return
        self._run_store.record(
            repository_id=repository_id,
            kind=kind,
            title=title,
            content=content,
            citations=citations,
            tool_trace=tool_trace,
            duration_ms=duration_ms,
        )
