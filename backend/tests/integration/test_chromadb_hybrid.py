"""
Integration test for ChromaDB hybrid mode.

Verifies ChromaDB connection and configuration (HTTP/Docker vs local persist).
Run with: pytest backend/tests/integration/test_chromadb_hybrid.py -v -s

Original script refactored from backend/test_chromadb_hybrid.py.
"""

from __future__ import annotations

import pytest

from app.config import settings
from app.services.vector_store import vector_store


@pytest.mark.integration
def test_chromadb_configuration() -> None:
    """Verify ChromaDB configuration is loaded."""
    assert settings.chroma_host is not None or settings.chroma_persist_dir is not None
    assert vector_store.mode in ("http", "persist")


@pytest.mark.integration
def test_chromadb_connection() -> None:
    """
    Verify ChromaDB connection by listing collections.

    Raises:
        AssertionError: With troubleshooting tips if connection fails.
    """
    try:
        collections = vector_store.client.list_collections()
    except Exception as e:
        msg = f"ChromaDB connection failed: {e}\n"
        if vector_store.mode == "http":
            msg += "  - Is Docker ChromaDB running? docker ps | grep chromadb\n"
            msg += "  - Can you reach it? curl http://localhost:8001/api/v1/"
        else:
            msg += "  - Check if directory exists: ls -la ./chroma_db\n"
            msg += "  - Check permissions on ./chroma_db directory"
        raise AssertionError(msg) from e
    assert isinstance(collections, list)


@pytest.mark.integration
def test_chromadb_collections_have_count() -> None:
    """Verify each collection has a count method."""
    collections = vector_store.client.list_collections()
    for col in collections:
        count = col.count()
        assert isinstance(count, int)
        assert count >= 0
