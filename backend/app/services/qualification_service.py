"""
Qualification Service

Scores and filters jobs based on user profile fit.
Uses Jaccard skill match (50%), budget fit (30%), client quality (20%).
Per specs/004-improve-autonomous, docs/quick-wins-autonomous.md
"""

import logging
from typing import Any, Dict, List, Optional

from app.core.database import get_db_pool

logger = logging.getLogger(__name__)

# Weights per research.md
SKILL_WEIGHT = 0.50
BUDGET_WEIGHT = 0.30
CLIENT_WEIGHT = 0.20


def _jaccard_similarity(a: set, b: set) -> float:
    """Jaccard similarity between two sets. Returns 0-1."""
    if not a or not b:
        return 0.0
    inter = len(a & b)
    union = len(a | b)
    return inter / union if union else 0.0


def score_job(job: Dict[str, Any], user_profile: Dict[str, Any]) -> float:
    """
    Score a job against user profile. Returns 0-1.

    Weights: skill match 50%, budget fit 30%, client quality 20%.

    Args:
        job: Job dict with skills, budget_min, budget_max (and optionally client_rating)
        user_profile: Dict with skills (list), min_project_budget (optional)

    Returns:
        Score between 0 and 1
    """
    job_skills = set(
        str(s).lower().strip()
        for s in (job.get("skills") or job.get("skills_required") or [])
        if s
    )
    raw_skills = user_profile.get("skills") or []
    if not isinstance(raw_skills, list):
        raw_skills = [raw_skills] if raw_skills else []
    user_skills = set(str(s).lower().strip() for s in raw_skills if s)

    skill_score = _jaccard_similarity(job_skills, user_skills)

    budget_obj = job.get("budget") or {}
    job_min = budget_obj.get("min") if isinstance(budget_obj, dict) else None
    if job_min is None:
        job_min = job.get("budget_min")
    user_min = user_profile.get("min_project_budget") or 0
    try:
        job_min = float(job_min) if job_min is not None else None
        user_min = float(user_min) if user_min is not None else 0
    except (TypeError, ValueError):
        job_min = None
        user_min = 0

    if job_min is None:
        budget_score = 0.5
    elif user_min <= 0:
        budget_score = 0.7
    elif job_min >= user_min:
        budget_score = 1.0
    elif job_min >= user_min * 0.8:
        budget_score = 0.7
    else:
        budget_score = 0.3

    client_rating = job.get("client_rating") or job.get("client_quality")
    if client_rating is not None:
        try:
            client_score = min(1.0, float(client_rating) / 5.0)
        except (TypeError, ValueError):
            client_score = 0.7
    else:
        client_score = 0.7

    total = skill_score * SKILL_WEIGHT + budget_score * BUDGET_WEIGHT + client_score * CLIENT_WEIGHT
    return round(total, 3)


def _explain_score(score: float) -> str:
    """Human-readable score explanation."""
    if score >= 0.85:
        return "Excellent match! Highly recommended."
    if score >= 0.70:
        return "Good match - worth pursuing."
    if score >= 0.60:
        return "Moderate match - review carefully."
    return "Low match - likely not a good fit."


async def score_and_filter_jobs(
    user_id: str,
    jobs: List[Dict[str, Any]],
    min_score: float = 0.60,
) -> List[Dict[str, Any]]:
    """
    Score jobs and return only those above threshold.

    Args:
        user_id: User UUID
        jobs: List of job dicts (must have id, skills, budget)
        min_score: Minimum qualification score (0-1)

    Returns:
        Jobs with qualification_score and qualification_reason, sorted by score desc
    """
    user_profile = await _get_user_profile(user_id)
    qualified: List[Dict[str, Any]] = []

    for job in jobs:
        score = score_job(job, user_profile)
        if score >= min_score:
            qualified.append({
                **job,
                "qualification_score": score,
                "qualification_reason": _explain_score(score),
            })

    qualified.sort(key=lambda j: j["qualification_score"], reverse=True)
    return qualified


async def upsert_user_job_qualification(
    user_id: str,
    job_id: str,
    score: float,
    reason: Optional[str] = None,
) -> None:
    """
    Upsert qualification score for a user-job pair.

    Args:
        user_id: User UUID
        job_id: Job UUID
        score: Qualification score 0-1
        reason: Optional human-readable explanation
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO user_project_qualifications (user_id, project_id, qualification_score, qualification_reason)
            VALUES ($1::uuid, $2::uuid, $3, $4)
            ON CONFLICT (user_id, project_id) DO UPDATE SET
                qualification_score = EXCLUDED.qualification_score,
                qualification_reason = EXCLUDED.qualification_reason
            """,
            user_id,
            job_id,
            score,
            reason or _explain_score(score),
        )


async def _get_user_profile(user_id: str) -> Dict[str, Any]:
    """Fetch user profile with skills and budget for qualification."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT preferences, up.user_id
            FROM user_profiles up
            WHERE up.user_id = $1
            """,
            user_id,
        )
        if not row:
            return {"skills": [], "keywords": [], "min_project_budget": 0}

        prefs = row.get("preferences") or {}
        if isinstance(prefs, str):
            import json
            try:
                prefs = json.loads(prefs) if prefs else {}
            except json.JSONDecodeError:
                prefs = {}

        skills = prefs.get("skills") or []
        if not isinstance(skills, list):
            skills = [skills] if skills else []
        min_budget = prefs.get("min_project_budget") or 0

        kw_rows = await conn.fetch(
            "SELECT keyword FROM keywords WHERE user_id = $1 AND is_active = true",
            user_id,
        )
        keywords = [r["keyword"] for r in kw_rows] if kw_rows else []
        # Merge skills from preferences + keywords (keywords as fallback/supplement)
        all_skills = list(
            set(str(s).strip().lower() for s in (skills + keywords) if s)
        )

        return {
            "skills": all_skills,
            "min_project_budget": min_budget,
        }
