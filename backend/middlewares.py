"""Lightweight request logging helpers.

These exist as simple building blocks for request/response logging and are
imported by modules that want uniform log formatting. The FastAPI app itself
uses structured logging via the standard ``logging`` module.
"""

import logging

logger = logging.getLogger(__name__)


def log_request(method: str, path: str) -> None:
    """Emit a single-line request log entry."""
    logger.info(f"{method} {path}")


def log_error(error: str, method: str, path: str) -> None:
    """Emit a single-line error log entry."""
    logger.error(f"Error in {method} {path}: {error}")
