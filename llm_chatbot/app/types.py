
"""Shared typing utilities for the chatbot application."""

from __future__ import annotations

from typing import Any, Mapping, Protocol


class SourceDocument(Protocol):
    """Protocol describing the metadata exposed by LangChain documents."""

    metadata: Mapping[str, Any]
    page_content: str
