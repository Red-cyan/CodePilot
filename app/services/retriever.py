from app.schemas import Citation
from app.services.embedding import DeterministicEmbedding
from app.services.models import CodeChunk, RepositoryState


class CodeRetriever:
    def __init__(self) -> None:
        self._embedding = DeterministicEmbedding()

    def search(
        self,
        repository: RepositoryState,
        query: str,
        top_k: int = 5,
    ) -> list[tuple[CodeChunk, float]]:
        query_vector = self._embedding.embed(query)
        scored = [
            (chunk, self._embedding.similarity(query_vector, chunk.vector))
            for chunk in repository.chunks
        ]
        scored.sort(key=lambda item: item[1], reverse=True)
        return [item for item in scored[:top_k] if item[1] > 0]


def citation_from_chunk(chunk: CodeChunk, score: float) -> Citation:
    preview = chunk.text.strip().splitlines()
    return Citation(
        path=chunk.path,
        start_line=chunk.start_line,
        end_line=chunk.end_line,
        score=round(score, 4),
        preview="\n".join(preview[:8]),
    )
