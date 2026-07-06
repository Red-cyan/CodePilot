from app.schemas import IndexRepositoryResponse
from app.services.embedding import DeterministicEmbedding
from app.services.parser import RepositoryParser
from app.services.repository import RepositoryService


class IndexerService:
    def __init__(self, repository_service: RepositoryService) -> None:
        self._repository_service = repository_service
        self._parser = RepositoryParser()
        self._embedding = DeterministicEmbedding()

    def index_repository(self, repository_id: str) -> IndexRepositoryResponse:
        state = self._repository_service.get(repository_id)
        chunks, symbols, languages = self._parser.scan(repository_id, state.path)
        for chunk in chunks:
            symbol_text = " ".join(symbol.name for symbol in chunk.symbols)
            chunk.vector = self._embedding.embed(f"{chunk.path}\n{symbol_text}\n{chunk.text}")
        state.chunks = chunks
        state.symbols = symbols
        state.languages = languages
        state.files_indexed = sum(languages.values())
        state.chunks_indexed = len(chunks)
        return IndexRepositoryResponse(
            repository_id=repository_id,
            files_indexed=state.files_indexed,
            chunks_indexed=state.chunks_indexed,
            symbols_indexed=len(symbols),
        )
