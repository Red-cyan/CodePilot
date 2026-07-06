from app.services.embedding import DeterministicEmbedding
from app.services.models import CodeChunk, RepositoryState
from app.services.retriever import CodeRetriever


def test_retriever_returns_relevant_chunk(tmp_path):
    embedding = DeterministicEmbedding()
    chunk = CodeChunk(
        id="a",
        repository_id="repo",
        path="service.py",
        language="python",
        text="def import_repository(): pass",
        start_line=1,
        end_line=1,
        content_hash="hash",
    )
    chunk.vector = embedding.embed(chunk.text)
    state = RepositoryState(id="repo", name="repo", path=tmp_path, chunks=[chunk])

    results = CodeRetriever().search(state, "repository import", top_k=1)

    assert results
    assert results[0][0].path == "service.py"
