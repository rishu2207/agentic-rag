"""Agentic RAG Platform — Hugging Face Spaces Demo.

This is a standalone Gradio app that showcases the Agentic RAG Platform.
When a backend API is available, it connects to it for live responses.
Otherwise, it runs in demo mode with pre-built sample responses.
"""

import os
import json
import gradio as gr

# ── Configuration ────────────────────────────────────────────────────────────
API_BASE_URL = os.getenv("API_BASE_URL", "")
GITHUB_URL = "https://github.com/rishu2207/agentic-rag"
PORTFOLIO_URL = "https://rishu2207.github.io/agentic-rag"

# ── Pre-built demo responses (used when no live backend is available) ──────
DEMO_RESPONSES = {
    "What is retrieval-augmented generation and when is it a better choice than fine-tuning?": {
        "answer": (
            "**Retrieval-Augmented Generation (RAG)** is a framework that enhances "
            "large language models by retrieving relevant documents from an external "
            "knowledge base before generating a response.\n\n"
            "### Key Advantages over Fine-tuning:\n\n"
            "1. **No retraining needed** — RAG can access up-to-date information "
            "without expensive model retraining cycles.\n"
            "2. **Grounded answers** — Responses are anchored to retrieved source "
            "documents, reducing hallucination.\n"
            "3. **Domain adaptability** — Swap the retrieval corpus to adapt to new "
            "domains instantly.\n"
            "4. **Cost-effective** — Avoids GPU-intensive fine-tuning while maintaining "
            "high-quality outputs.\n\n"
            "### When to choose RAG over fine-tuning:\n"
            "- Your knowledge base changes frequently\n"
            "- You need traceable, citation-backed answers\n"
            "- You have limited compute for training\n"
            "- Domain coverage is broad but shallow\n\n"
            "**Sources:** Lewis et al. (2020) *\"Retrieval-Augmented Generation for "
            "Knowledge-Intensive NLP Tasks\"* [arXiv:2005.11401]"
        ),
        "reasoning_steps": [
            {"node": "guardrail", "detail": "Score: 95/100 — on-topic AI/ML research question"},
            {"node": "retrieve", "detail": "Hybrid search returned 5 chunks (BM25 + kNN with RRF)"},
            {"node": "grade_documents", "detail": "4/5 chunks graded as relevant"},
            {"node": "generate", "detail": "Generated grounded answer with 1 citation"},
        ],
        "sources": ["https://arxiv.org/abs/2005.11401", "https://arxiv.org/abs/2312.10997"],
    },
    "How does reciprocal rank fusion combine BM25 and dense-vector scores?": {
        "answer": (
            "**Reciprocal Rank Fusion (RRF)** is a simple yet effective method for "
            "combining ranked lists from different retrieval systems.\n\n"
            "### How it works:\n\n"
            "Given a document *d* appearing at rank *r* in a ranked list, the RRF "
            "score is:\n\n"
            "```\n"
            "RRF(d) = Σ 1 / (k + r_i)\n"
            "```\n\n"
            "where *k* is a constant (typically 60) and *r_i* is the rank of document "
            "*d* in the *i*-th ranking.\n\n"
            "### In this platform:\n"
            "1. **BM25** retrieves top-k by keyword relevance\n"
            "2. **k-NN** retrieves top-k by cosine similarity (Jina v3 1024-dim)\n"
            "3. **RRF pipeline** in OpenSearch merges both rankings\n"
            "4. The fused list is returned as the final retrieval result\n\n"
            "### Limitations:\n"
            "- RRF ignores the actual scores, only using ranks\n"
            "- Equal weighting may not be optimal for all query types\n"
            "- The constant *k* is a hyperparameter that needs tuning\n\n"
            "**Sources:** Cormack et al. (2009) *\"Reciprocal Rank Fusion outperforms "
            "Condorcet and individual Rank Learning Methods\"*"
        ),
        "reasoning_steps": [
            {"node": "guardrail", "detail": "Score: 92/100 — valid information retrieval question"},
            {"node": "retrieve", "detail": "Hybrid search returned 5 chunks"},
            {"node": "grade_documents", "detail": "5/5 chunks graded as relevant"},
            {"node": "generate", "detail": "Generated detailed answer with formula"},
        ],
        "sources": ["https://arxiv.org/abs/2210.11934"],
    },
}

DEFAULT_ANSWER = (
    "⚠️ **Demo Mode** — This Space is running without a live backend.\n\n"
    "In production, this query would be processed by the full Agentic RAG pipeline:\n\n"
    "1. **Guardrail** validates the query is in-scope\n"
    "2. **Hybrid search** retrieves passages via BM25 + dense vectors\n"
    "3. **Document grading** filters irrelevant chunks\n"
    "4. **Query rewriting** retries when evidence is weak\n"
    "5. **Answer generation** produces grounded responses with citations\n\n"
    "👉 Try one of the **example questions** below for a full demo response!\n\n"
    f"🔗 [View the full project on GitHub]({GITHUB_URL})"
)


def find_closest_demo(query: str) -> dict | None:
    """Find the closest matching demo response."""
    q = query.lower().strip()
    for key, val in DEMO_RESPONSES.items():
        if any(word in q for word in key.lower().split()[:4]):
            return val
    return None


async def ask_question(
    query: str,
    top_k: int = 5,
    use_hybrid: bool = True,
):
    """Process a question — live API if available, otherwise demo mode."""
    if not query.strip():
        return "Please enter a question.", "", ""

    # Try live API first
    if API_BASE_URL:
        try:
            import httpx
            payload = {
                "query": query,
                "top_k": top_k,
                "use_hybrid": use_hybrid,
            }
            async with httpx.AsyncClient(timeout=60.0) as client:
                res = await client.post(
                    f"{API_BASE_URL}/ask-agentic", json=payload
                )
                if res.status_code == 200:
                    data = res.json()
                    answer = data.get("answer", "No answer returned.")
                    sources = "\n".join(
                        f"- [{s.split('/')[-1]}]({s})"
                        for s in data.get("sources", [])
                    ) or "No sources."
                    reasoning = "\n".join(
                        f"**{step.get('node', '?')}**: {step.get('detail', '')}"
                        for step in data.get("reasoning_steps", [])
                    ) or "No reasoning steps."
                    return answer, sources, reasoning
        except Exception:
            pass  # Fall through to demo mode

    # Demo mode
    demo = find_closest_demo(query)
    if demo:
        answer = demo["answer"]
        sources = "\n".join(
            f"- [{s.split('/')[-1]}]({s})" for s in demo.get("sources", [])
        )
        reasoning = "\n".join(
            f"**{step['node']}**: {step['detail']}"
            for step in demo.get("reasoning_steps", [])
        )
        return answer, sources, reasoning

    return DEFAULT_ANSWER, "Demo mode — no live sources", "Demo mode — pipeline not connected"


# ── Gradio Interface ─────────────────────────────────────────────────────────
DESCRIPTION = """
# 🔬 Agentic RAG Platform

**Production-grade AI research assistant** over ArXiv cs.AI papers.

This demo showcases the project architecture. Try the example questions below
for sample agentic RAG responses, or connect a live backend for real-time answers.

| Component | Technology |
|-----------|-----------|
| **Backend** | FastAPI + Python 3.12 |
| **Agent** | LangGraph (7-node state machine) |
| **Search** | OpenSearch hybrid (BM25 + kNN + RRF) |
| **LLM** | Ollama / OpenAI (pluggable) |
| **Frontend** | Next.js 14 + this Gradio demo |
| **Observability** | Langfuse v3 |

"""

ARTICLE = f"""
---
**Links:** [GitHub Repository]({GITHUB_URL}) · [Portfolio Site]({PORTFOLIO_URL}) · [LinkedIn](https://www.linkedin.com/in/rishu2207/)

Built by **Rishabh Sharma** — MIT License
"""

with gr.Blocks(
    title="Agentic RAG Platform",
    theme=gr.themes.Soft(
        primary_hue=gr.themes.colors.purple,
        secondary_hue=gr.themes.colors.teal,
        neutral_hue=gr.themes.colors.slate,
    ),
) as demo:
    gr.Markdown(DESCRIPTION)

    with gr.Row():
        with gr.Column(scale=3):
            query_input = gr.Textbox(
                label="🔍 Your Research Question",
                placeholder="Ask about AI/ML research...",
                lines=2,
                max_lines=4,
            )
        with gr.Column(scale=1):
            submit_btn = gr.Button("Ask Agent →", variant="primary", size="lg")

    with gr.Accordion("⚙️ Advanced Options", open=False):
        with gr.Row():
            top_k = gr.Slider(1, 10, value=5, step=1, label="Chunks to retrieve")
            use_hybrid = gr.Checkbox(value=True, label="Hybrid search (BM25 + vectors)")

    with gr.Row():
        with gr.Column(scale=2):
            answer_output = gr.Markdown(label="📝 Answer", value="*Ask a question to get started!*")
        with gr.Column(scale=1):
            sources_output = gr.Markdown(label="📚 Sources", value="")
            reasoning_output = gr.Markdown(label="🧠 Agent Reasoning", value="")

    gr.Examples(
        examples=[
            ["What is retrieval-augmented generation and when is it a better choice than fine-tuning?"],
            ["How does reciprocal rank fusion combine BM25 and dense-vector scores?"],
            ["What are the latest self-correcting or agentic RAG workflows?"],
            ["How do you evaluate retrieval quality and faithfulness of a RAG system?"],
        ],
        inputs=[query_input],
    )

    submit_btn.click(
        fn=ask_question,
        inputs=[query_input, top_k, use_hybrid],
        outputs=[answer_output, sources_output, reasoning_output],
    )
    query_input.submit(
        fn=ask_question,
        inputs=[query_input, top_k, use_hybrid],
        outputs=[answer_output, sources_output, reasoning_output],
    )

    gr.Markdown(ARTICLE)

if __name__ == "__main__":
    demo.launch()
