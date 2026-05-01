from backend.schemas.api.health import HealthResponse, ServiceStatus
from backend.schemas.api.search import SearchHit, SearchRequest, SearchResponse

# ArXiv schemas
from backend.schemas.arxiv.paper import (
    ArxivPaper,
    PaperBase,
    PaperCreate,
    PaperResponse,
    PaperSearchResponse,
)

# Database schemas
from backend.schemas.database.config import PostgreSQLSettings

# Embeddings schemas
from backend.schemas.embeddings.jina import JinaEmbeddingRequest, JinaEmbeddingResponse

# Indexing schemas (including chunking)
from backend.schemas.indexing.models import ChunkMetadata, TextChunk

# PDF Parser schemas
from backend.schemas.pdf_parser.models import (
    ArxivMetadata,
    PaperFigure,
    PaperSection,
    PaperTable,
    ParsedPaper,
    ParserType,
    PdfContent,
)

# Search schemas
from backend.schemas.search.hybrid import (
    ChunkResult,
    HybridSearchRequest,
    HybridSearchResponse,
)

__all__ = [
    # API
    "HealthResponse",
    "ServiceStatus",
    "SearchRequest",
    "SearchResponse",
    "SearchHit",
    # ArXiv
    "ArxivPaper",
    "PaperBase",
    "PaperCreate",
    "PaperResponse",
    "PaperSearchResponse",
    # Indexing
    "ChunkMetadata",
    "TextChunk",
    # Database
    "PostgreSQLSettings",
    # Embeddings
    "JinaEmbeddingRequest",
    "JinaEmbeddingResponse",
    # PDF Parser
    "ParserType",
    "PaperSection",
    "PaperFigure",
    "PaperTable",
    "PdfContent",
    "ArxivMetadata",
    "ParsedPaper",
    # Search
    "HybridSearchRequest",
    "HybridSearchResponse",
    "ChunkResult",
]
