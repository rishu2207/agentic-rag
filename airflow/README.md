# Airflow — scheduled ingestion

This directory contains the Apache Airflow configuration and DAGs for the
[Agentic RAG Platform](../README.md). Airflow is an **optional** component —
the backend will happily serve queries without it — but it's how the platform
keeps the OpenSearch index fresh with new ArXiv papers on a schedule.

## DAGs

| DAG | Schedule | Purpose |
| --- | --- | --- |
| `arxiv_paper_ingestion` | Weekdays 06:00 UTC | Fetch new ArXiv cs.AI papers, parse PDFs with Docling, chunk, embed with Jina, and index into OpenSearch. |
| `smoke_test` | Manual | Heartbeat + API/Postgres reachability probe. |

```
airflow/
├── README.md
├── Dockerfile                    # Custom Airflow image with PDF / OCR deps
├── requirements-airflow.txt      # Python deps for DAGs
└── dags/
    ├── smoke_test_dag.py         # Health-check DAG
    ├── arxiv_paper_ingestion.py  # Production ingestion DAG
    └── arxiv_ingestion/          # Task modules reused across DAGs
```

## Ingestion pipeline

`arxiv_paper_ingestion` runs these tasks in order:

1. `setup_environment` — verify services and prepare caches
2. `fetch_daily_papers` — pull yesterday's cs.AI paper metadata from ArXiv
3. `store_to_postgres` — upsert papers via `backend.repositories.paper`
4. `parse_pdfs` — Docling-based PDF → structured text, with OCR off
5. `chunk_papers` — section-aware chunking (600 words / 100 overlap)
6. `generate_embeddings` — Jina v3 embeddings (1024-dim)
7. `index_hybrid` — bulk index into the OpenSearch hybrid index
8. `verify_hybrid_index` — post-index sanity check
9. `generate_daily_report` — processing statistics

Rate limiting, retries, and concurrency caps are applied to stay within
ArXiv API etiquette (3-second delays, 5 parallel downloads by default).

## Running Airflow

```bash
docker compose up airflow -d
open http://localhost:8080
```

Admin credentials are generated on first boot — check the container logs with
`docker compose logs airflow`.

## Configuration

```bash
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://rag_user:rag_password@postgres:5432/rag_db
AIRFLOW__CORE__EXECUTOR=LocalExecutor
POSTGRES_DATABASE_URL=postgresql+psycopg2://rag_user:rag_password@postgres:5432/rag_db
PYTHONPATH=/opt/airflow
```

The shared `backend/` package is mounted into the container at
`/opt/airflow/backend` so DAG tasks can reuse the same service classes as the
FastAPI app — `OpenSearchClient`, `JinaEmbeddingsClient`, `PDFParserService`,
and the `PaperRepository`.

## Dependencies

- PostgreSQL — paper metadata & content
- OpenSearch — hybrid BM25 + vector index
- Jina AI — embeddings (requires `JINA_API_KEY`)
