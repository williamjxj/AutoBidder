"""
Proposal Quality Service

Scores proposals on multiple dimensions and provides improvement suggestions.
Per specs/004-improve-autonomous T030-T031, docs/quick-wins-autonomous.md.
"""

import logging
from typing import Any, Dict, List

from app.config import settings

logger = logging.getLogger(__name__)


def score_proposal(
    proposal_text: str,
    job_description: str,
    job_requirements: List[str],
) -> Dict[str, Any]:
    """
    Score proposal on multiple dimensions (rule-based, no LLM).

    Returns:
        Dict with overall_score (0-100), dimension_scores, suggestions, word_count
    """
    scores: Dict[str, float] = {}

    # 1. Length (400-600 words optimal)
    word_count = len(proposal_text.split())
    scores["length"] = _score_length(word_count)

    # 2. Requirement coverage
    scores["coverage"] = _score_coverage(proposal_text, job_requirements)

    # 3. Citation presence (past work, experience)
    scores["citations"] = _score_citations(proposal_text)

    # 4. Grammar (basic heuristics - no LLM for reliability)
    scores["grammar"] = _score_grammar_heuristic(proposal_text)

    # 5. Personalization (job-specific terms)
    scores["personalization"] = _score_personalization(proposal_text, job_description)

    # Weighted overall
    weights = {
        "length": 0.10,
        "coverage": 0.35,
        "citations": 0.25,
        "grammar": 0.15,
        "personalization": 0.15,
    }
    overall_score = sum(scores[k] * weights[k] for k in weights)

    suggestions = _generate_suggestions(scores, word_count)

    return {
        "overall_score": round(overall_score, 1),
        "dimension_scores": scores,
        "suggestions": suggestions,
        "word_count": word_count,
    }


def _score_length(word_count: int) -> float:
    """Score based on word count (400-600 optimal)."""
    if 400 <= word_count <= 600:
        return 100.0
    if 300 <= word_count < 400:
        return 80.0
    if 600 < word_count <= 800:
        return 85.0
    if 200 <= word_count < 300:
        return 65.0
    if 800 < word_count <= 1000:
        return 70.0
    return 50.0


def _score_coverage(proposal: str, requirements: List[str]) -> float:
    """Score how many requirements are addressed."""
    if not requirements:
        return 100.0
    proposal_lower = proposal.lower()
    covered = sum(1 for req in requirements if req.lower() in proposal_lower)
    return (covered / len(requirements)) * 100.0


def _score_citations(proposal: str) -> float:
    """Check if proposal cites past work."""
    indicators = [
        "previously worked on",
        "past project",
        "experience with",
        "similar project",
        "delivered",
        "built",
        "developed",
        "case study",
        "portfolio",
        "successfully",
        "implemented",
        "led",
    ]
    proposal_lower = proposal.lower()
    matches = sum(1 for ind in indicators if ind in proposal_lower)
    if matches >= 3:
        return 100.0
    if matches == 2:
        return 75.0
    if matches == 1:
        return 50.0
    return 25.0


def _score_grammar_heuristic(proposal: str) -> float:
    """Basic grammar heuristics (no LLM)."""
    score = 80.0  # Base
    # Penalize very short sentences (fragments)
    sentences = [s.strip() for s in proposal.replace("!", ".").replace("?", ".").split(".") if s.strip()]
    if sentences:
        avg_len = sum(len(s.split()) for s in sentences) / len(sentences)
        if avg_len < 5:
            score -= 15
        elif avg_len > 30:
            score -= 5
    # Penalize excessive caps
    if len(proposal) > 0 and sum(1 for c in proposal if c.isupper()) / max(1, len(proposal)) > 0.1:
        score -= 10
    return max(0.0, min(100.0, score))


def _score_personalization(proposal: str, job_description: str) -> float:
    """Check if proposal references job-specific terms."""
    if not job_description or len(job_description) < 50:
        return 75.0  # Neutral
    # Extract likely key terms (words > 4 chars, not common)
    common = {"the", "and", "for", "with", "this", "that", "your", "will", "have", "need", "project"}
    job_words = set(
        w.lower() for w in job_description.split()
        if len(w) > 4 and w.lower() not in common
    )
    proposal_lower = proposal.lower()
    matched = sum(1 for w in job_words if w in proposal_lower)
    if len(job_words) < 3:
        return 80.0
    ratio = matched / min(len(job_words), 15)  # Cap at 15 terms
    return min(100.0, 50.0 + ratio * 50.0)


def _generate_suggestions(scores: Dict[str, float], word_count: int) -> List[str]:
    """Generate improvement suggestions from dimension scores."""
    suggestions: List[str] = []
    if scores["length"] < 80:
        if word_count < 400:
            suggestions.append("Proposal is too short. Aim for 400-600 words.")
        else:
            suggestions.append("Proposal is too long. Keep it under 600 words.")
    if scores["coverage"] < 70:
        suggestions.append("Not all job requirements are addressed. Review the job posting.")
    if scores["citations"] < 60:
        suggestions.append("Add specific examples from your past work to build credibility.")
    if scores["grammar"] < 80:
        suggestions.append("Check for grammar and spelling errors.")
    if scores["personalization"] < 70:
        suggestions.append("Make the proposal more specific to this client's needs.")
    if not suggestions:
        suggestions.append("Great proposal! Consider submitting.")
    return suggestions
