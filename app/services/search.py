from app.schemas import CodeSearchHit, CodeSearchRequest, CodeSearchResponse, SearchMode
from app.services.repository import RepositoryService
from app.services.retriever import CodeRetriever, citation_from_chunk


class CodeSearchService:
    def __init__(self, repository_service: RepositoryService) -> None:
        self._repository_service = repository_service
        self._retriever = CodeRetriever()

    def search(self, payload: CodeSearchRequest) -> CodeSearchResponse:
        repository = self._repository_service.get(payload.repository_id)
        if payload.mode == SearchMode.semantic:
            hits = [
                CodeSearchHit(
                    path=citation.path,
                    start_line=citation.start_line,
                    end_line=citation.end_line,
                    score=citation.score,
                    language=chunk.language,
                    kind="chunk",
                    preview=citation.preview,
                )
                for chunk, score in self._retriever.search(
                    repository,
                    payload.query,
                    payload.top_k,
                )
                for citation in [citation_from_chunk(chunk, score)]
            ]
        elif payload.mode == SearchMode.keyword:
            hits = self._keyword_search(payload)
        else:
            hits = self._symbol_search(payload)
        return CodeSearchResponse(
            repository_id=repository.id,
            query=payload.query,
            mode=payload.mode,
            hits=hits,
        )

    def _keyword_search(self, payload: CodeSearchRequest) -> list[CodeSearchHit]:
        repository = self._repository_service.get(payload.repository_id)
        query = payload.query.lower()
        scored: list[CodeSearchHit] = []
        for chunk in repository.chunks:
            text = chunk.text.lower()
            path = chunk.path.lower()
            symbol_names = " ".join(symbol.name.lower() for symbol in chunk.symbols)
            count = text.count(query) + path.count(query) + symbol_names.count(query)
            if count == 0:
                continue
            scored.append(
                CodeSearchHit(
                    path=chunk.path,
                    start_line=chunk.start_line,
                    end_line=chunk.end_line,
                    score=float(count),
                    language=chunk.language,
                    kind="chunk",
                    preview="\n".join(chunk.text.strip().splitlines()[:8]),
                )
            )
        scored.sort(key=lambda hit: hit.score, reverse=True)
        return scored[: payload.top_k]

    def _symbol_search(self, payload: CodeSearchRequest) -> list[CodeSearchHit]:
        repository = self._repository_service.get(payload.repository_id)
        query = payload.query.lower()
        hits: list[CodeSearchHit] = []
        for symbol in repository.symbols:
            if query not in symbol.name.lower() and query not in symbol.kind.lower():
                continue
            hits.append(
                CodeSearchHit(
                    path=symbol.path,
                    start_line=symbol.line,
                    end_line=symbol.line,
                    score=1.0 if query == symbol.name.lower() else 0.5,
                    language=None,
                    kind=symbol.kind,
                    preview=f"{symbol.kind} {symbol.name}",
                )
            )
        hits.sort(key=lambda hit: (hit.score, hit.path, -hit.start_line), reverse=True)
        return hits[: payload.top_k]
