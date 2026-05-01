"""Provider-aware chat model factory.

The rest of the codebase calls :func:`get_chat_model` and receives a LangChain
``BaseChatModel`` that is either backed by Ollama (local) or an OpenAI-compatible
API. This keeps agent nodes provider-agnostic.
"""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Optional

from backend.config import Settings, get_settings

logger = logging.getLogger(__name__)


class LLMProviderError(RuntimeError):
    """Raised when no LLM provider can be initialised."""


def resolved_provider(settings: Optional[Settings] = None) -> str:
    """Return the provider name that will actually be used (``"openai"`` or ``"ollama"``)."""
    settings = settings or get_settings()

    if settings.llm_provider == "openai":
        if not settings.openai_api_key:
            raise LLMProviderError(
                "llm_provider='openai' but OPENAI_API_KEY is not set. "
                "Set OPENAI_API_KEY in your .env or switch llm_provider to 'ollama'."
            )
        return "openai"

    if settings.llm_provider == "ollama":
        return "ollama"

    # auto
    if settings.openai_api_key:
        return "openai"
    return "ollama"


def get_chat_model(
    *,
    model: Optional[str] = None,
    temperature: float = 0.0,
    settings: Optional[Settings] = None,
):
    """Return a LangChain chat model configured for the active provider.

    :param model: Override the provider's default model (e.g. ``"llama3.2:1b"``
        for Ollama or ``"gpt-4o-mini"`` for OpenAI). When ``None`` the provider's
        default from settings is used.
    :param temperature: Sampling temperature.
    :param settings: Optional pre-built Settings instance.
    :returns: A LangChain ``BaseChatModel`` subclass.
    """
    settings = settings or get_settings()
    provider = resolved_provider(settings)

    if provider == "openai":
        try:
            from langchain_openai import ChatOpenAI
        except ImportError as exc:  # pragma: no cover
            raise LLMProviderError(
                "langchain-openai is not installed. Run `uv sync` to install it."
            ) from exc

        selected_model = model or settings.openai_model
        logger.debug(
            "Initialising ChatOpenAI model=%s base_url=%s",
            selected_model,
            settings.openai_base_url,
        )
        return ChatOpenAI(
            model=selected_model,
            temperature=temperature,
            api_key=settings.openai_api_key,
            base_url=settings.openai_base_url,
            timeout=settings.openai_timeout,
        )

    # provider == "ollama"
    try:
        from langchain_ollama import ChatOllama
    except ImportError as exc:  # pragma: no cover
        raise LLMProviderError(
            "langchain-ollama is not installed. Run `uv sync` to install it."
        ) from exc

    selected_model = model or settings.ollama_model
    logger.debug(
        "Initialising ChatOllama model=%s base_url=%s",
        selected_model,
        settings.ollama_host,
    )
    return ChatOllama(
        model=selected_model,
        temperature=temperature,
        base_url=settings.ollama_host,
    )


@lru_cache(maxsize=8)
def _cached_chat_model(model: Optional[str], temperature: float):
    return get_chat_model(model=model, temperature=temperature)
