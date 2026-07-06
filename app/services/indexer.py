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
        result = self._parser.scan(repository_id, state.path)
        for chunk in result.chunks:
            symbol_text = " ".join(symbol.name for symbol in chunk.symbols)
            chunk.vector = self._embedding.embed(f"{chunk.path}\n{symbol_text}\n{chunk.text}")
        state.chunks = result.chunks
        state.symbols = result.symbols
        state.languages = result.languages
        state.files_indexed = sum(result.languages.values())
        state.chunks_indexed = len(result.chunks)
        self._repository_service.save()
        return IndexRepositoryResponse(
            repository_id=repository_id,
            files_indexed=state.files_indexed,
            chunks_indexed=state.chunks_indexed,
            symbols_indexed=len(result.symbols),
            files_scanned=result.files_scanned,
            skipped_files=result.skipped_files,
            skip_reasons=result.skip_reasons,
        )
