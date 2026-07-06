from app.schemas import ReviewIssue, ReviewRequest, ReviewResponse
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

    def review(self, payload: ReviewRequest) -> ReviewResponse:
        timer = RunTimer()
        repository = self._repository_service.get(payload.repository_id)
        changed_terms = " ".join(
            line[1:].strip()
            for line in payload.diff.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        )
        results = self._retriever.search(repository, changed_terms or payload.diff, top_k=5)
        citations = [citation_from_chunk(chunk, score) for chunk, score in results]
        issues = self._issues(payload.diff)
        findings = self._format_issues(issues)
        score = self._score(issues)
        summary = self._summary(score, issues)
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
                        f"初始评分：{score}/100\n\n"
                        f"相关代码：\n{self._format_citations(citations)}"
                    ),
                ),
            ]
        )
        response = ReviewResponse(
            repository_id=repository.id,
            title="Pull Request Review",
            content=content,
            score=score,
            summary=summary,
            issues=issues,
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
    def _issues(diff: str) -> list[ReviewIssue]:
        issues: list[ReviewIssue] = []
        if "password" in diff.lower() or "secret" in diff.lower():
            issues.append(
                ReviewIssue(
                    category="security",
                    severity="high",
                    message="diff 中出现疑似凭据字段。",
                    suggestion="确认没有提交真实密钥、密码或 token，并改用环境变量或密钥管理服务。",
                    line_hint="password/secret",
                )
            )
        if "except Exception" in diff:
            issues.append(
                ReviewIssue(
                    category="maintainability",
                    severity="medium",
                    message="新增代码包含过宽的异常捕获。",
                    suggestion="捕获更具体的异常类型，并记录可定位的错误上下文。",
                    line_hint="except Exception",
                )
            )
        if "TODO" in diff or "FIXME" in diff:
            issues.append(
                ReviewIssue(
                    category="maintainability",
                    severity="low",
                    message="diff 中包含未解决的 TODO/FIXME。",
                    suggestion="在合并前解决该事项，或关联明确的 issue/task 编号。",
                    line_hint="TODO/FIXME",
                )
            )
        if "print(" in diff:
            issues.append(
                ReviewIssue(
                    category="style",
                    severity="low",
                    message="新增代码包含 print 调试输出。",
                    suggestion="替换为结构化日志，或在提交前删除调试输出。",
                    line_hint="print(",
                )
            )
        added_lines = [
            line
            for line in diff.splitlines()
            if line.startswith("+") and not line.startswith("+++")
        ]
        test_lines = [
            line for line in added_lines if "test" in line.lower() or "assert" in line.lower()
        ]
        if len(added_lines) >= 5 and not test_lines:
            issues.append(
                ReviewIssue(
                    category="test",
                    severity="medium",
                    message="diff 新增了多行实现代码，但没有明显测试变更。",
                    suggestion="补充单元测试或接口测试，覆盖主要成功路径和失败路径。",
                    line_hint="新增代码缺少测试",
                )
            )
        return issues

    @staticmethod
    def _format_issues(issues: list[ReviewIssue]) -> str:
        if not issues:
            return "- 未发现确定性规则问题。"
        return "\n".join(
            f"- {issue.severity.upper()} / {issue.category}: "
            f"{issue.message} 建议：{issue.suggestion}"
            for issue in issues
        )

    @staticmethod
    def _score(issues: list[ReviewIssue]) -> int:
        score = 90
        penalty_by_severity = {"high": 18, "medium": 10, "low": 5}
        for issue in issues:
            score -= penalty_by_severity.get(issue.severity, 6)
        return max(score, 50)

    @staticmethod
    def _summary(score: int, issues: list[ReviewIssue]) -> str:
        if not issues:
            return "未发现确定性规则问题，建议继续结合业务语义和测试结果人工确认。"
        high_count = sum(1 for issue in issues if issue.severity == "high")
        medium_count = sum(1 for issue in issues if issue.severity == "medium")
        low_count = sum(1 for issue in issues if issue.severity == "low")
        return (
            f"评分 {score}/100；发现 {len(issues)} 个确定性问题，"
            f"其中 high={high_count}，medium={medium_count}，low={low_count}。"
        )

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
