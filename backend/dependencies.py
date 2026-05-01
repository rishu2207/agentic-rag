from functools import lru_cache
from typing import TYPE_CHECKING, Annotated, Generator, Optional

if TYPE_CHECKING:
    from fastapi import Depends, Request
    from sqlalchemy.orm import Session
else:
    try:
        from fastapi import Depends, Request
        from sqlalchemy.orm import Session
    except ImportError:
        pass

from backend.config import Settings
from backend.db.interfaces.base import BaseDatabase
from backend.services.arxiv.client import ArxivClient
from backend.services.cache.client import CacheClient
from backend.services.embeddings.jina_client import JinaEmbeddingsClient
from backend.services.langfuse.client import LangfuseTracer
from backend.services.ollama.client import OllamaClient
from backend.services.opensearch.client import OpenSearchClient
from backend.services.pdf_parser.parser import PDFParserService
from backend.services.telegram.bot import TelegramBot
from backend.services.agents.agentic_rag import AgenticRAGService
from backend.services.agents.factory import make_agentic_rag_service


@lru_cache
def get_settings() -> Settings:
    """Get application settings."""
    return Settings()


def get_request_settings(request: Request) -> Settings:
    """Get settings from the request state."""
    return request.app.state.settings


def get_database(request: Request) -> BaseDatabase:
    """Get database from the request state."""
    return request.app.state.database


def get_db_session(database: Annotated[BaseDatabase, Depends(get_database)]) -> Generator[Session, None, None]:
    """Get database session dependency."""
    with database.get_session() as session:
        yield session


def get_opensearch_client(request: Request) -> OpenSearchClient:
    """Get OpenSearch client from the request state."""
    return request.app.state.opensearch_client


def get_arxiv_client(request: Request) -> ArxivClient:
    """Get arXiv client from the request state."""
    return request.app.state.arxiv_client


def get_pdf_parser(request: Request) -> PDFParserService:
    """Get PDF parser service from the request state."""
    return request.app.state.pdf_parser


def get_embeddings_service(request: Request) -> JinaEmbeddingsClient:
    """Get embeddings service from the request state."""
    return request.app.state.embeddings_service


def get_ollama_client(request: Request) -> OllamaClient:
    """Get Ollama client from the request state."""
    return request.app.state.ollama_client


def get_langfuse_tracer(request: Request) -> LangfuseTracer:
    """Get Langfuse tracer from the request state."""
    return request.app.state.langfuse_tracer


def get_cache_client(request: Request) -> CacheClient | None:
    """Get cache client from the request state."""
    return getattr(request.app.state, "cache_client", None)


def get_telegram_service(request: Request) -> Optional[TelegramBot]:
    """Get Telegram service from the request state."""
    return getattr(request.app.state, "telegram_service", None)


# Dependency annotations
SettingsDep = Annotated[Settings, Depends(get_settings)]
DatabaseDep = Annotated[BaseDatabase, Depends(get_database)]
SessionDep = Annotated[Session, Depends(get_db_session)]
OpenSearchDep = Annotated[OpenSearchClient, Depends(get_opensearch_client)]
ArxivDep = Annotated[ArxivClient, Depends(get_arxiv_client)]
PDFParserDep = Annotated[PDFParserService, Depends(get_pdf_parser)]
EmbeddingsDep = Annotated[JinaEmbeddingsClient, Depends(get_embeddings_service)]
OllamaDep = Annotated[OllamaClient, Depends(get_ollama_client)]
LangfuseDep = Annotated[LangfuseTracer, Depends(get_langfuse_tracer)]
CacheDep = Annotated[CacheClient | None, Depends(get_cache_client)]
TelegramDep = Annotated[Optional[TelegramBot], Depends(get_telegram_service)]


def get_agentic_rag_service(
    opensearch: OpenSearchDep,
    ollama: OllamaDep,
    embeddings: EmbeddingsDep,
    langfuse: LangfuseDep,
    settings: Annotated[Settings, Depends(get_settings)],
) -> AgenticRAGService:
    """Get agentic RAG service."""
    return make_agentic_rag_service(
        opensearch_client=opensearch,
        ollama_client=ollama,
        embeddings_client=embeddings,
        langfuse_tracer=langfuse,
        model=settings.ollama_model,
    )


AgenticRAGDep = Annotated[AgenticRAGService, Depends(get_agentic_rag_service)]
