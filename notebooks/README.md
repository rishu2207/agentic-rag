# Notebooks

Interactive walkthroughs that accompany the [Agentic RAG Platform](../README.md).
Each notebook is self-contained and runs against the services defined in
`compose.yml`. Start the stack with `make start` before opening any of them.

| Notebook | What it covers |
| --- | --- |
| [`01_environment_setup.ipynb`](01_environment_setup.ipynb) | Install dependencies, verify Postgres / OpenSearch / Ollama are reachable, and pull a local LLM. |
| [`02_arxiv_ingestion.ipynb`](02_arxiv_ingestion.ipynb) | Fetch ArXiv metadata, download and parse PDFs with Docling, and persist papers to Postgres. |
| [`03_opensearch_bm25.ipynb`](03_opensearch_bm25.ipynb) | Create the hybrid OpenSearch index and run keyword (BM25) retrieval against indexed chunks. |
| [`04_hybrid_search.ipynb`](04_hybrid_search.ipynb) | Generate Jina embeddings, index dense vectors alongside BM25, and run hybrid search with RRF. |
| [`05_rag_pipeline.ipynb`](05_rag_pipeline.ipynb) | End-to-end retrieval-augmented generation with Ollama and citation-grounded answers. |
| [`06_caching_and_observability.ipynb`](06_caching_and_observability.ipynb) | Redis exact-match caching, Langfuse tracing, and latency / quality metrics. |
| [`07_agentic_rag.ipynb`](07_agentic_rag.ipynb) | The full LangGraph agent — guardrail, retrieval, grading, query rewriting, and answer generation. |

> 💡 The production application in `backend/` and `frontend/` is the canonical
> implementation. The notebooks exist as a guided tour through the same code —
> every cell imports from the real `backend.*` packages.
