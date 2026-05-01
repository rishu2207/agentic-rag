<div align="center">

# ⚡ Agentic RAG Platform

**Production-grade AI research assistant powered by self-correcting LangGraph agents,
hybrid search, and full observability.**

[![Python](https://img.shields.io/badge/Python-3.12+-3776ab.svg?style=flat&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-14-000.svg?style=flat&logo=next.js&logoColor=white)](https://nextjs.org)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2+-ff6b00.svg?style=flat)](https://langchain-ai.github.io/langgraph/)
[![OpenSearch](https://img.shields.io/badge/OpenSearch-2.19-005eb8.svg?style=flat&logo=opensearch&logoColor=white)](https://opensearch.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ed.svg?style=flat&logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![License](https://img.shields.io/badge/License-MIT-22c55e.svg?style=flat)](LICENSE)

[**Live Demo**](https://huggingface.co/spaces/ramu3405/agentic-rag-platform) · [**Portfolio**](https://rishu2207.github.io/agentic-rag) · [**API Docs**](http://localhost:8000/docs)


</div>

---

## Overview

Agentic RAG Platform is an end-to-end research assistant built on top of the ArXiv cs.AI corpus. It combines a **7-node LangGraph agent** with **hybrid retrieval** (BM25 + dense vectors via Reciprocal Rank Fusion) to deliver grounded, citation-backed answers to AI/ML research questions.

A single `docker compose up` brings up 12+ services — from the FastAPI backend and Next.js chat UI, through OpenSearch and PostgreSQL, to Langfuse tracing and Airflow-based ingestion — all production-ready with healthchecks, named volumes, and proper secrets management.

### What happens when you ask a question

1. **Guardrail** — an LLM scores the query (0–100) for relevance; off-topic questions are rejected early
2. **Hybrid retrieval** — BM25 keyword search and k-NN dense-vector search run in parallel over OpenSearch, merged via Reciprocal Rank Fusion
3. **Document grading** — each retrieved chunk is evaluated for relevance; irrelevant chunks are discarded
4. **Query rewriting** — if evidence is weak, the agent rewrites the query and retries (up to 2 attempts)
5. **Answer generation** — the LLM generates a grounded response with inline citations to source papers
6. **Caching & tracing** — the answer is cached in Redis; every step is traced to Langfuse

---

## Architecture

### System diagram

```
                       ┌───────────────────────────────────┐
                       │        Next.js 14 (frontend)      │
                       │  Chat UI · dark mode · SSE stream │
                       └──────────────┬────────────────────┘
                                      │ /api/chat  /api/stream  /api/feedback
                                      ▼
                       ┌───────────────────────────────────┐
                       │          FastAPI backend           │
                       │  /ask  /ask-agentic  /stream       │
                       │  /hybrid-search  /health           │
                       └──┬───────────┬───────────────┬────┘
                          │           │               │
             ┌────────────▼──┐   ┌────▼─────────┐   ┌─▼─────────────┐
             │   LangGraph   │   │  OpenSearch   │   │   PostgreSQL  │
             │    Agent      │   │  BM25 +       │   │  paper store  │
             │  guardrail →  │   │  vectors      │   │  Alembic ORM  │
             │  retrieve →   │   │  + RRF        │   │               │
             │  grade →      │   └──────┬────────┘   └───────────────┘
             │  rewrite? →   │         │
             │  generate     │         │
             └──┬────────────┘         │
                │                      │
  ┌─────────────▼──────┐   ┌──────────▼───────┐   ┌────────────────┐
  │   LLM provider     │   │  Jina embeddings │   │  Redis cache   │
  │  Ollama (local)     │   │  1024-dim v3     │   │  exact-match   │
  │  or OpenAI-compat.  │   │  async client    │   │  answer cache  │
  └────────┬───────────┘   └──────────────────┘   └────────────────┘
           │
           ▼
    ┌──────────────┐        ┌──────────────────────┐     ┌──────────────┐
    │   Langfuse   │        │       Airflow         │     │    ArXiv     │
    │  v3 tracing  │        │  daily ingestion DAG  │◄────┤  API + PDF   │
    │  + feedback  │        │  chunk · embed · index│     │  (Docling)   │
    └──────────────┘        └──────────────────────┘     └──────────────┘
```

### Agent workflow (LangGraph)

```
        ┌──────────┐
        │   START  │
        └────┬─────┘
             ▼
      ┌─────────────┐
      │  guardrail   │  ← scores 0-100, rejects off-topic queries
      └──┬────────┬──┘
         │ ≥ 60   │ < 60
         ▼        ▼
   ┌──────────┐  ┌──────────────┐
   │ retrieve │  │ out_of_scope │──► END
   └────┬─────┘  └──────────────┘
        ▼
 ┌──────────────┐
 │ grade docs   │  ← binary relevance per chunk
 └──┬────────┬──┘
    │ all ok │ some bad
    ▼        ▼
 ┌──────┐  ┌──────────────┐
 │ gen  │  │rewrite_query │──► retrieve (max 2 retries)
 └──┬───┘  └──────────────┘
    ▼
   END
```

---

## Tech Stack

| Layer | Technology |
| --- | --- |
| **Frontend** | Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS, shadcn-style components, Lucide icons, `react-markdown` + GFM |
| **Backend** | FastAPI, Pydantic v2, SQLAlchemy 2, Alembic migrations, `uv` package manager |
| **Agent orchestration** | LangGraph 0.2+, LangChain v0.3, custom 7-node state machine |
| **LLM providers** | Ollama (local, default `llama3.2:1b`) · OpenAI-compatible API (OpenAI, Groq, Together, OpenRouter, LM Studio, vLLM) |
| **Embeddings** | Jina AI v3 (`jina-embeddings-v3`, 1024-dim) |
| **Retrieval** | OpenSearch 2.19 — BM25 + k-NN (cosine), Reciprocal Rank Fusion pipeline |
| **Document parsing** | Docling (section-aware PDF → structured text) |
| **Data stores** | PostgreSQL 16 (paper metadata), Redis 7 (answer cache) |
| **Observability** | Langfuse v3 — full trace per request, token usage, latency, user feedback |
| **Ingestion** | Apache Airflow 2.10 — daily scheduled DAG for ArXiv fetching + indexing |
| **Runtime** | Docker Compose — single command to bring up the full stack |

---

## Key Features

- **Self-correcting agentic RAG** — the agent grades its own retrieved context and rewrites the query when evidence is weak, capped at 2 retries to prevent runaway loops
- **Hybrid search with RRF** — BM25 and dense-vector retrieval run in parallel over a single unified OpenSearch index, merged via Reciprocal Rank Fusion
- **Pluggable LLM providers** — switch between local Ollama and any OpenAI-compatible API with a single env variable; auto-detects `OPENAI_API_KEY`
- **Full observability** — every span, prompt template, token count, and latency metric is exported to Langfuse; in-app thumbs up/down writes feedback to the same trace
- **Sub-millisecond caching** — exact-match Redis cache returns repeated queries instantly, keyed by `query + model + top_k + search_mode + categories`
- **Modern chat UI** — Next.js 14 with dark mode, sample prompts, source cards with relevance scores, and an expandable "Agent Reasoning" trace
- **Automated daily ingestion** — Airflow DAG fetches new cs.AI papers, parses PDFs with Docling, chunks by section, embeds via Jina, and indexes into OpenSearch
- **Production Docker setup** — 12+ containers with healthchecks, named volumes, shared network, and proper secrets management

---

## Repository Structure

```
├── backend/                        # FastAPI application (Python 3.12)
│   ├── main.py                     # App factory, CORS, lifespan, router mounting
│   ├── config.py                   # Pydantic settings (env-driven)
│   ├── routers/                    # /ask, /stream, /ask-agentic, /hybrid-search, /health, /feedback
│   ├── services/
│   │   ├── agents/                 # LangGraph workflow, nodes, tools, prompts
│   │   ├── llm/                    # Provider abstraction (Ollama ↔ OpenAI)
│   │   ├── embeddings/             # Jina v3 async client
│   │   ├── opensearch/             # Hybrid index client + RRF pipeline
│   │   ├── indexing/               # Chunking + bulk indexer
│   │   ├── pdf_parser/             # Docling wrapper
│   │   ├── arxiv/                  # ArXiv API client + PDF downloader
│   │   ├── cache/                  # Redis answer cache
│   │   └── langfuse/               # Langfuse v3 tracer + feedback
│   ├── schemas/                    # Pydantic request/response models
│   ├── models/                     # SQLAlchemy ORM models
│   ├── repositories/               # Data-access layer
│   └── db/                         # Engine + session factory
│
├── frontend/                       # Next.js 14 (App Router)
│   ├── app/                        # Pages + API route handlers
│   │   └── api/                    # /chat, /stream, /feedback, /health
│   ├── components/
│   │   ├── chat/                   # Chat, Message, Composer, Header, SourceCard, ReasoningTrace
│   │   └── ui/                     # Button, Textarea, Badge
│   └── Dockerfile                  # Multi-stage standalone build
│
├── airflow/                        # Ingestion DAGs
│   └── dags/                       # arxiv_paper_ingestion + reusable task modules
│
├── tests/                          # pytest suite (unit + integration + API)
├── notebooks/                      # Jupyter notebooks for exploration
├── docs/                           # GitHub Pages portfolio site
├── Dockerfile                      # Backend image (uv + python:3.12-slim)
├── compose.yml                     # Full-stack orchestration (12+ services)
├── Makefile                        # Convenience targets
├── pyproject.toml                  # Python dependencies (uv-managed)
└── .env.example                    # All env variables with documentation
```

---

## Getting Started

### Prerequisites

- [Docker](https://docs.docker.com/get-docker/) + Docker Compose v2
- A [Jina AI API key](https://jina.ai/embeddings) (free tier is sufficient)
- **One of:** Ollama (bundled via Docker) **or** an `OPENAI_API_KEY`

### Quick start

```bash
git clone https://github.com/rishu2207/agentic-rag.git
cd agentic-rag
cp .env.example .env          # configure JINA_API_KEY and optionally OPENAI_API_KEY
make start                    # docker compose up --build -d
```

The first boot downloads the Ollama model and initialises all databases. Allow a few minutes for everything to become healthy.

### Services

| Service | URL |
| --- | --- |
| **Chat UI** | http://localhost:3000 |
| **API (Swagger)** | http://localhost:8000/docs |
| **Health check** | http://localhost:8000/api/v1/health |
| **OpenSearch Dashboards** | http://localhost:5601 |
| **Langfuse** | http://localhost:3001 |
| **Airflow** | http://localhost:8080 |

### Populate the index

Trigger the `arxiv_paper_ingestion` DAG from the Airflow UI at http://localhost:8080, or use the notebooks in `notebooks/` for an interactive walkthrough.

---

## Development

### Backend

```bash
make setup            # install Python deps into .venv
make backend          # uvicorn with hot-reload
make format           # ruff format
make lint             # ruff check + mypy
make test             # pytest
make test-cov         # pytest with coverage report
```

### Frontend

```bash
make frontend-install # npm install
make frontend-dev     # next dev on port 3000
make frontend-build   # production build
```

### Switching LLM providers

```bash
# OpenAI (or any compatible endpoint: Groq, Together, OpenRouter, vLLM)
LLM_PROVIDER=openai OPENAI_API_KEY=sk-... docker compose up -d api

# Local Ollama (default)
LLM_PROVIDER=ollama docker compose up -d api

# Auto-detect based on whether OPENAI_API_KEY is set
LLM_PROVIDER=auto docker compose up -d api
```

### Tests

```bash
uv sync --all-groups
uv run pytest -q
```

The test suite covers unit tests (config, schemas, services, agent nodes), integration tests (multi-service flows with `testcontainers`), and API tests (FastAPI `TestClient` with mocked services).

---

## Observability

Every request creates a Langfuse trace with dedicated spans:

| Span | Details |
| --- | --- |
| `guardrail` | Scope score (0–100) + accept/reject decision |
| `retrieve` | Tool call + top-k documents (BM25 / vector / hybrid) |
| `grade_documents` | Per-chunk relevance reasoning |
| `rewrite_query` | Triggered only when evidence is insufficient |
| `answer_generation` | Prompt tokens, completion tokens, latency |

Thumbs up/down in the chat UI writes feedback directly to the corresponding Langfuse trace.

---

## API Reference

| Method | Endpoint | Description |
| --- | --- | --- |
| `POST` | `/api/v1/ask-agentic` | Full agentic RAG with reasoning steps |
| `POST` | `/api/v1/ask` | Single-shot RAG with Redis cache |
| `POST` | `/api/v1/stream` | Streaming RAG (NDJSON/SSE) |
| `POST` | `/api/v1/hybrid-search` | Raw hybrid/BM25 chunk search |
| `POST` | `/api/v1/feedback` | Submit feedback bound to a Langfuse trace |
| `GET` | `/api/v1/health` | Per-service health status |

Full OpenAPI schema available at http://localhost:8000/docs.

---

## Screenshots

<p align="center">
  <img src="static/architecture_agentic_rag.png" alt="Agentic RAG architecture" width="800">
</p>

<p align="center">
  <img src="static/architecture_hybrid_search.png" alt="Hybrid search pipeline" width="800">
</p>

<p align="center">
  <img src="static/architecture_rag_pipeline.png" alt="RAG pipeline" width="800">
</p>

<p align="center">
  <img src="static/architecture_observability.png" alt="Observability dashboard" width="800">
</p>

---

## Roadmap

- [ ] End-to-end token streaming in the Next.js UI
- [ ] Document upload endpoint for arbitrary PDFs
- [ ] Multi-tenant workspace with per-user chat history
- [ ] Evaluation harness with RAGAS-style metrics wired to Langfuse
- [ ] Kubernetes Helm chart

---

## License

MIT — see [LICENSE](LICENSE).

---

<div align="center">

**Built by Rishabh Sharma**

[Live Demo](https://huggingface.co/spaces/ramu3405/agentic-rag-platform) · [Portfolio](https://rishu2207.github.io/agentic-rag)

</div>
