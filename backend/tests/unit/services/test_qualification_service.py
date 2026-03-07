"""
Unit tests for qualification_service.

Per specs/004-improve-autonomous/tasks.md T042.
Tests score_job and score_and_filter_jobs.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.services.qualification_service import score_job, score_and_filter_jobs


@pytest.mark.unit
def test_score_job_perfect_skill_match() -> None:
    """score_job returns high score when job skills match user skills."""
    job = {
        "skills_required": ["python", "react", "postgresql"],
        "budget_min": 5000,
    }
    user_profile = {"skills": ["python", "react", "postgresql"], "min_project_budget": 3000}
    score = score_job(job, user_profile)
    assert score >= 0.9
    assert score <= 1.0


@pytest.mark.unit
def test_score_job_partial_skill_match() -> None:
    """score_job returns moderate score for partial skill overlap."""
    job = {"skills_required": ["python", "react"], "budget_min": 5000}
    user_profile = {"skills": ["python", "django"], "min_project_budget": 3000}
    score = score_job(job, user_profile)
    assert 0.3 <= score <= 0.9


@pytest.mark.unit
def test_score_job_no_skill_overlap() -> None:
    """score_job returns low score when no skills match."""
    job = {"skills_required": ["java", "kotlin"], "budget_min": 5000}
    user_profile = {"skills": ["python", "react"], "min_project_budget": 3000}
    score = score_job(job, user_profile)
    assert score < 0.5


@pytest.mark.unit
def test_score_job_budget_fit_above_user_min() -> None:
    """score_job gives high budget score when job budget >= user min."""
    job = {"skills_required": ["python"], "budget_min": 10000}
    user_profile = {"skills": ["python"], "min_project_budget": 5000}
    score = score_job(job, user_profile)
    assert score >= 0.8


@pytest.mark.unit
def test_score_job_uses_skills_key() -> None:
    """score_job accepts both skills and skills_required."""
    job = {"skills": ["python"], "budget_min": 5000}
    user_profile = {"skills": ["python"], "min_project_budget": 3000}
    score = score_job(job, user_profile)
    assert score >= 0.8


@pytest.mark.unit
@pytest.mark.asyncio
async def test_score_and_filter_jobs_returns_above_threshold() -> None:
    """score_and_filter_jobs returns only jobs above min_score."""
    jobs = [
        {"id": "j1", "skills_required": ["python"], "budget_min": 5000},
        {"id": "j2", "skills_required": ["java"], "budget_min": 5000},
    ]
    user_profile = {"skills": ["python"], "min_project_budget": 3000}

    with patch(
        "app.services.qualification_service._get_user_profile",
        new_callable=AsyncMock,
        return_value=user_profile,
    ):
        result = await score_and_filter_jobs("user-123", jobs, min_score=0.5)
        assert len(result) >= 1
        for q in result:
            assert "qualification_score" in q
            assert "qualification_reason" in q
            assert q["qualification_score"] >= 0.5
