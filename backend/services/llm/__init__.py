"""LLM provider abstraction.

This module exposes a single entry point, :func:`get_chat_model`, that returns
a LangChain ``BaseChatModel`` configured according to the platform settings.
It lets the rest of the backend (agents, nodes, routers) stay agnostic of the
underlying provider — Ollama for local inference or any OpenAI-compatible API
for hosted inference.

Selection rules (driven by ``Settings.llm_provider``):

* ``"openai"``  → always uses OpenAI-compatible provider.
* ``"ollama"``  → always uses local Ollama.
* ``"auto"``    → uses OpenAI when ``openai_api_key`` is set, otherwise Ollama.
"""

from .provider import LLMProviderError, get_chat_model, resolved_provider

__all__ = ["get_chat_model", "resolved_provider", "LLMProviderError"]
