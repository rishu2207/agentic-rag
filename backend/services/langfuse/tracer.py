"""Simple, efficient Langfuse tracing utility for RAG pipeline."""

import time
from contextlib import contextmanager
from typing import Any, Dict, List, Optional

from .client import LangfuseTracer


class RAGTracer:
    """Clean, purpose-built tracer for RAG operations."""

    def __init__(self, tracer: LangfuseTracer):
        self.tracer = tracer

    @contextmanager
    def trace_request(self, user_id: str, query: str):
        """Main request trace context manager."""
        trace = None
        if self.tracer.client:
            try:
                trace = self.tracer.client.trace(
                    name="rag_request",
                    input={"query": query},
                    user_id=user_id,
                    session_id=f"session_{user_id}",
                    metadata={"simplified_tracing": True}
                )
                yield trace
            finally:
                if trace:
                    self.tracer.client.flush()
        else:
            yield None

    @contextmanager
    def trace_embedding(self, trace, query: str):
        """Query embedding operation with timing."""
        start_time = time.time()
        span = None
        if trace and self.tracer.client:
            span = trace.span(
                name="query_embedding", input={"query": query, "query_length": len(query)}
            )
        try:
            yield span
        finally:
            duration = time.time() - start_time
            if span:
                span.update(output={"embedding_duration_ms": round(duration * 1000, 2), "success": True})
                span.end()

    @contextmanager
    def trace_search(self, trace, query: str, top_k: int):
        """Search operation with timing."""
        span = None
        if trace and self.tracer.client:
            span = trace.span(name="search_retrieval", input={"query": query, "top_k": top_k})
        try:
            yield span
        finally:
            if span:
                span.end()

    def end_search(self, span, chunks: List[Dict], arxiv_ids: List[str], total_hits: int):
        """End search span with essential results."""
        if not span:
            return

        span.update(
            output={
                "chunks_returned": len(chunks),
                "unique_papers": len(set(arxiv_ids)),
                "total_hits": total_hits,
                "arxiv_ids": list(set(arxiv_ids)),
            },
        )
        span.end()

    @contextmanager
    def trace_prompt_construction(self, trace, chunks: List[Dict]):
        """Prompt building with timing."""
        span = None
        if trace and self.tracer.client:
            span = trace.span(name="prompt_construction", input={"chunk_count": len(chunks)})
        try:
            yield span
        finally:
            if span:
                span.end()

    def end_prompt(self, span, prompt: str):
        """End prompt span with final prompt."""
        if not span:
            return

        span.update(
            output={
                "prompt_length": len(prompt),
                # Don't duplicate the full prompt here since it's in llm_generation input
                "prompt_preview": prompt[:200] + "..." if len(prompt) > 200 else prompt,
            },
        )
        span.end()

    @contextmanager
    def trace_generation(self, trace, model: str, prompt: str):
        """LLM generation with timing."""
        span = None
        if trace and self.tracer.client:
            span = trace.generation(
                name="llm_generation", input={"model": model, "prompt_length": len(prompt), "prompt": prompt}
            )
        try:
            yield span
        finally:
            if span:
                span.end()

    def end_generation(self, span, response: str, model: str):
        """End generation span with response."""
        if not span:
            return

        span.update(output={"response": response, "response_length": len(response), "model_used": model})
        span.end()

    def end_request(self, trace, response: str, total_duration: float):
        """End main request trace."""
        if not trace:
            return

        try:
            trace.update(
                output={"answer": response, "total_duration_seconds": round(total_duration, 3), "response_length": len(response)}
            )
        except Exception:
            # Silently fail - don't break the request for tracing issues
            pass
