import logging
import os
from contextlib import asynccontextmanager

import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.config import get_settings
from backend.db.factory import make_database
from backend.routers import agentic_ask, hybrid_search, ping
from backend.routers.ask import ask_router, stream_router
from backend.services.arxiv.factory import make_arxiv_client
from backend.services.cache.factory import make_cache_client
from backend.services.embeddings.factory import make_embeddings_service
from backend.services.langfuse.factory import make_langfuse_tracer
from backend.services.ollama.factory import make_ollama_client
from backend.services.opensearch.factory import make_opensearch_client
from backend.services.pdf_parser.factory import make_pdf_parser_service
from backend.services.telegram.factory import make_telegram_service

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan for the API.
    """
    logger.info("Starting RAG API...")

    settings = get_settings()
    app.state.settings = settings

    database = make_database()
    app.state.database = database
    logger.info("Database connected")

    # Initialize search service
    opensearch_client = make_opensearch_client()
    app.state.opensearch_client = opensearch_client

    # Verify OpenSearch connectivity and create index if needed
    if opensearch_client.health_check():
        logger.info("OpenSearch connected successfully")

        # Setup hybrid index (supports all search types)
        setup_results = opensearch_client.setup_indices(force=False)
        if setup_results.get("hybrid_index"):
            logger.info("Hybrid index created")
        else:
            logger.info("Hybrid index already exists")

        # Get simple statistics
        try:
            stats = opensearch_client.client.count(index=opensearch_client.index_name)
            logger.info(f"OpenSearch ready: {stats['count']} documents indexed")
        except Exception:
            logger.info("OpenSearch index ready (stats unavailable)")
    else:
        logger.warning("OpenSearch connection failed - search features will be limited")

    # Initialize other services (kept for future endpoints and notebook demos)
    app.state.arxiv_client = make_arxiv_client()
    app.state.pdf_parser = make_pdf_parser_service()
    app.state.embeddings_service = make_embeddings_service()
    app.state.ollama_client = make_ollama_client()
    app.state.langfuse_tracer = make_langfuse_tracer()
    app.state.cache_client = make_cache_client(settings)
    logger.info("Services initialized: arXiv API client, PDF parser, OpenSearch, Embeddings, Ollama, Langfuse, Cache")

    # Optional Telegram bot (disabled unless TELEGRAM__ENABLED=true)
    telegram_service = make_telegram_service(
        opensearch_client=app.state.opensearch_client,
        embeddings_client=app.state.embeddings_service,
        ollama_client=app.state.ollama_client,
        cache_client=app.state.cache_client,
        langfuse_tracer=app.state.langfuse_tracer,
    )

    if telegram_service:
        app.state.telegram_service = telegram_service
        try:
            await telegram_service.start()
            logger.info("Telegram bot started successfully")
        except Exception as e:
            logger.error(f"Failed to start Telegram bot: {e}")
    else:
        logger.info("Telegram bot not configured - skipping initialization")

    logger.info("API ready")
    yield

    # Cleanup
    if hasattr(app.state, "telegram_service") and app.state.telegram_service:
        await app.state.telegram_service.stop()
        logger.info("Telegram bot stopped")

    database.teardown()
    logger.info("API shutdown complete")


app = FastAPI(
    title="Agentic RAG Platform API",
    description=(
        "Production-grade agentic retrieval-augmented generation over ArXiv "
        "research papers. Hybrid BM25 + dense-vector retrieval, a LangGraph "
        "agent with guardrail, grading and query-rewrite nodes, and a pluggable "
        "LLM provider (Ollama or OpenAI-compatible)."
    ),
    version=os.getenv("APP_VERSION", "1.0.0"),
    lifespan=lifespan,
)

# CORS — allow the Next.js frontend (port 3000) and the legacy Gradio UI.
# For production deployments set ALLOWED_ORIGINS and tighten this list.
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://0.0.0.0:3000",
        "http://frontend:3000",
        "http://localhost:7861",
        "http://0.0.0.0:7861",
        "http://gradio:7861",
        "*",  # permissive for dev; override via settings in production
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(ping.router, prefix="/api/v1")  # Health check endpoint
app.include_router(hybrid_search.router, prefix="/api/v1")  # Search chunks with BM25/hybrid
app.include_router(ask_router, prefix="/api/v1")  # RAG question answering with LLM
app.include_router(stream_router, prefix="/api/v1")  # Streaming RAG responses
app.include_router(agentic_ask.router)  # Agentic RAG with intelligent retrieval


if __name__ == "__main__":
    uvicorn.run(app, port=8000, host="0.0.0.0")
