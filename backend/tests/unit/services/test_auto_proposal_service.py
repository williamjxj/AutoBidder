"""
Unit tests for auto_proposal_service.

Per specs/004-improve-autonomous/tasks.md T043.
Tests auto_generate_proposals with mocked dependencies.
"""

from __future__ import annotations

import os
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest

# Set env before importing app (avoids langchain init)
os.environ.setdefault("OPENAI_API_KEY", "sk-test-key")
os.environ.setdefault("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/test_db")

pytest.importorskip("langchain_openai")
from app.services.auto_proposal_service import auto_generate_proposals


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auto_generate_proposals_returns_zero_when_no_llm() -> None:
    """auto_generate_proposals returns 0 when chat_model not configured."""
    from app.services.ai_service import ai_service

    original = ai_service.chat_model
    ai_service.chat_model = None
    try:
        jobs = [
            {
                "id": str(uuid4()),
                "qualification_score": 0.9,
                "title": "Test Job",
                "description": "Desc",
                "skills": ["python"],
            }
        ]
        count = await auto_generate_proposals("user-1", jobs, threshold=0.85)
        assert count == 0
    finally:
        ai_service.chat_model = original


@pytest.mark.unit
@pytest.mark.asyncio
async def test_auto_generate_proposals_filters_by_threshold() -> None:
    """auto_generate_proposals only processes jobs above threshold."""
    from app.services.ai_service import ai_service

    jobs = [
        {"id": "j1", "qualification_score": 0.9, "title": "High", "description": "", "skills": []},
        {"id": "j2", "qualification_score": 0.7, "title": "Low", "description": "", "skills": []},
    ]
    ai_service.chat_model = MagicMock()
    ai_service.chat_model.ainvoke = AsyncMock(return_value=MagicMock(content="Proposal text"))

    with (
        patch("app.services.auto_proposal_service.ai_service") as mock_ai,
        patch("app.services.auto_proposal_service.create_auto_generated_proposal", new_callable=AsyncMock),
        patch("app.services.auto_proposal_service.settings_service") as mock_settings,
    ):
        mock_ai.chat_model = MagicMock()
        mock_ai.generate_proposal = AsyncMock(
            return_value=MagicMock(
                title="Proposal",
                description="Desc",
                budget="5000",
                timeline="2 weeks",
                skills=[],
                ai_model="gpt-4",
                quality_score=None,
                quality_breakdown=None,
                quality_suggestions=None,
            )
        )
        mock_settings.get_settings = AsyncMock(
            return_value=MagicMock(preferences=MagicMock(default_strategy_id=None))
        )
        count = await auto_generate_proposals("user-1", jobs, threshold=0.85)

    assert count == 1
