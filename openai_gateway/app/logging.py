"""Structured logging configuration using structlog."""

import sys
from typing import Any, Dict

import structlog
from structlog.types import Processor

from .settings import settings


def setup_logging() -> None:
    """Configure structured logging with structlog."""
    
    # Configure processors
    processors: list[Processor] = [
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
    ]

    # Add JSON formatter for production
    if settings.log_format == "json":
        processors.append(structlog.processors.JSONRenderer())
    else:
        # Console formatter for development
        processors.append(
            structlog.dev.ConsoleRenderer(colors=True)
        )

    # Configure structlog
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """Get a structured logger instance."""
    return structlog.get_logger(name)


def log_request(
    logger: structlog.BoundLogger,
    method: str,
    path: str,
    org_id: str | None = None,
    **kwargs: Any,
) -> None:
    """Log HTTP request metadata."""
    logger.info(
        "HTTP request",
        method=method,
        path=path,
        org_id=org_id,
        **kwargs,
    )


def log_response(
    logger: structlog.BoundLogger,
    method: str,
    path: str,
    status_code: int,
    org_id: str | None = None,
    **kwargs: Any,
) -> None:
    """Log HTTP response metadata."""
    logger.info(
        "HTTP response",
        method=method,
        path=path,
        status_code=status_code,
        org_id=org_id,
        **kwargs,
    )


def log_openai_request(
    logger: structlog.BoundLogger,
    org_id: str,
    prompt_tokens: int,
    **kwargs: Any,
) -> None:
    """Log OpenAI request metadata (no sensitive data)."""
    logger.info(
        "OpenAI request",
        org_id=org_id,
        prompt_tokens=prompt_tokens,
        **kwargs,
    )


def log_openai_response(
    logger: structlog.BoundLogger,
    org_id: str,
    response_tokens: int,
    latency_ms: float,
    **kwargs: Any,
) -> None:
    """Log OpenAI response metadata (no sensitive data)."""
    logger.info(
        "OpenAI response",
        org_id=org_id,
        response_tokens=response_tokens,
        latency_ms=latency_ms,
        **kwargs,
    ) 