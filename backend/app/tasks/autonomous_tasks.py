"""
Autonomous Discovery Tasks

Background jobs for autonomous job discovery per user.
Per specs/004-improve-autonomous/tasks.md Phase 3–5.
Discovery → qualification → notification pipeline.
"""

import logging
from typing import Any, Dict, List

from app.config import settings
from app.core.database import get_db_pool
from app.services.autonomy_settings_service import (
    create_autonomous_run,
    get_autonomy_settings,
    record_autonomous_run,
)


async def run_autonomous_pipeline_and_record(user_id: str, run_id: str) -> None:
    """
    Run discovery pipeline and record results for an existing run (T041).

    Used by POST /api/autonomous/run: create run first, return run_id, then
    this runs in background.
    """
    try:
        result = await run_autonomous_discovery_for_user(user_id)
        await record_autonomous_run(
            user_id,
            run_id,
            jobs_discovered=result.get("jobs_discovered", 0),
            jobs_qualified=result.get("jobs_qualified", 0),
            proposals_generated=result.get("proposals_generated", 0),
            notifications_sent=result.get("notifications_sent", 0),
            status="success",
        )
    except Exception as e:
        logger.exception("Autonomous pipeline failed for user %s: %s", user_id, e)
        await record_autonomous_run(
            user_id,
            run_id,
            status="failed",
            errors=[str(e)],
        )
from app.services.job_service import get_jobs_by_fingerprints, upsert_jobs
from app.services.keyword_service import keyword_service
from app.services.auto_proposal_service import auto_generate_proposals
from app.services.notification_service import get_user_email, notify_qualified_jobs
from app.services.qualification_service import (
    score_and_filter_jobs,
    upsert_user_job_qualification,
)

logger = logging.getLogger(__name__)

# HF dataset for discovery (matches projects router)
HF_DATASET_ID = "jacob-hugging-face/job-descriptions"
HF_JOB_LIMIT = 20


async def run_autonomous_discovery_for_user(user_id: str) -> Dict[str, Any]:
    """
    Discover jobs for a single user, upsert to database, and run qualification.

    Fetches user's keywords, loads jobs from HuggingFace, applies domain filter,
    upserts to jobs table, then scores and persists qualification for discovered jobs.

    Args:
        user_id: User UUID

    Returns:
        Dict with jobs_discovered, jobs_qualified, proposals_generated, notifications_sent

    Raises:
        Exception: Propagates from hf_loader or job_service
    """
    # Get user keywords
    keywords: List[str] = []
    try:
        user_keywords = await keyword_service.list_keywords(
            user_id, search=None, is_active=True
        )
        keywords = [k.keyword for k in user_keywords] if user_keywords else []
    except Exception as e:
        logger.warning("Could not load keywords for user %s: %s", user_id, e)

    if not keywords:
        logger.info("User %s has no active keywords; skipping discovery", user_id)
        return {"jobs_discovered": 0, "jobs_qualified": 0, "proposals_generated": 0, "notifications_sent": 0}

    # Load and filter jobs from HuggingFace
    from app.etl.hf_loader import load_and_filter_hf_jobs

    records, _, _ = load_and_filter_hf_jobs(
        dataset_id=HF_DATASET_ID,
        limit=HF_JOB_LIMIT,
        keyword_filter=keywords,
    )

    if not records:
        logger.info("No jobs found for user %s (keywords: %s)", user_id, keywords)
        return {"jobs_discovered": 0, "jobs_qualified": 0, "proposals_generated": 0, "notifications_sent": 0}

    # Upsert to database
    inserted, updated = await upsert_jobs(records, etl_source="autonomous_discovery")
    total = inserted + updated
    logger.info(
        "User %s: discovered %d jobs (inserted=%d, updated=%d)",
        user_id,
        total,
        inserted,
        updated,
    )

    jobs_qualified = 0
    proposals_generated = 0
    notifications_sent = 0

    # T035: autonomy_level behavior - discovery_only/assisted = discovery only
    try:
        settings_obj = await get_autonomy_settings(user_id)
        level = (settings_obj.autonomy_level or "assisted").lower()
        if level in ("discovery_only", "assisted"):
            logger.info(
                "User %s: autonomy_level=%s; skipping qualification/notification/auto-gen",
                user_id,
                level,
            )
            return {
                "jobs_discovered": total,
                "jobs_qualified": 0,
                "proposals_generated": 0,
                "notifications_sent": 0,
            }

        fingerprints = [r.fingerprint_hash for r in records]
        jobs = await get_jobs_by_fingerprints(fingerprints, user_id=None)
        if jobs:
            min_score = float(settings_obj.qualification_threshold)
            qualified = await score_and_filter_jobs(user_id, jobs, min_score=min_score)
            jobs_qualified = len(qualified)
            for q in qualified:
                await upsert_user_job_qualification(
                    user_id,
                    q["id"],
                    q["qualification_score"],
                    q.get("qualification_reason"),
                )
            logger.info(
                "User %s: qualified %d/%d jobs (threshold=%.2f)",
                user_id,
                jobs_qualified,
                len(jobs),
                min_score,
            )

            # Notification (T023): email when high-quality jobs found
            if qualified and settings_obj.notifications_enabled:
                try:
                    user_email = await get_user_email(user_id)
                    if user_email:
                        notif_threshold = float(settings_obj.notification_threshold)
                        notifications_sent = await notify_qualified_jobs(
                            user_email,
                            qualified,
                            threshold=notif_threshold,
                        )
                        if notifications_sent:
                            logger.info(
                                "User %s: notification sent for %d jobs (threshold=%.2f)",
                                user_id,
                                notifications_sent,
                                notif_threshold,
                            )
                except Exception as ne:
                    logger.warning(
                        "Notification failed for user %s (qualification succeeded): %s",
                        user_id,
                        ne,
                        exc_info=True,
                    )

            # Auto-proposal (T027): generate drafts for high-confidence jobs
            if qualified and settings_obj.auto_generate_enabled:
                try:
                    gen_threshold = float(settings_obj.auto_generate_threshold)
                    proposals_generated = await auto_generate_proposals(
                        user_id,
                        qualified,
                        threshold=gen_threshold,
                    )
                    if proposals_generated:
                        logger.info(
                            "User %s: auto-generated %d proposals (threshold=%.2f)",
                            user_id,
                            proposals_generated,
                            gen_threshold,
                        )
                except Exception as ae:
                    logger.warning(
                        "Auto-generation failed for user %s (qualification succeeded): %s",
                        user_id,
                        ae,
                        exc_info=True,
                    )
    except Exception as e:
        logger.warning(
            "Qualification failed for user %s (discovery succeeded): %s",
            user_id,
            e,
            exc_info=True,
        )

    return {
        "jobs_discovered": total,
        "jobs_qualified": jobs_qualified,
        "proposals_generated": proposals_generated,
        "notifications_sent": notifications_sent,
    }


async def run_autonomous_discovery_job() -> None:
    """
    Run autonomous discovery for all users with auto_discovery_enabled=true.

    Queries user_profiles, invokes run_autonomous_discovery_for_user per user.
    Per-user failures are logged and do not block other users (FR-012).
    """
    if not settings.etl_use_persistence:
        logger.debug("ETL persistence disabled; skipping autonomous discovery")
        return

    pool = await get_db_pool()
    rows = await pool.fetch(
        """
        SELECT user_id FROM user_profiles
        WHERE auto_discovery_enabled = true
        """
    )

    if not rows:
        logger.debug("No users with auto_discovery_enabled; skipping")
        return

    logger.info("Auto-discovery: starting for %d users", len(rows))
    total_jobs = 0

    for row in rows:
        user_id = str(row["user_id"])
        run_id: str | None = None
        try:
            run_id = await create_autonomous_run(user_id)
            result = await run_autonomous_discovery_for_user(user_id)
            total_jobs += result.get("jobs_discovered", 0)
            await record_autonomous_run(
                user_id,
                run_id,
                jobs_discovered=result.get("jobs_discovered", 0),
                jobs_qualified=result.get("jobs_qualified", 0),
                proposals_generated=result.get("proposals_generated", 0),
                notifications_sent=result.get("notifications_sent", 0),
                status="success",
            )
        except Exception as e:
            logger.exception(
                "Discovery failed for user %s: %s",
                user_id,
                e,
                exc_info=True,
            )
            if run_id:
                await record_autonomous_run(
                    user_id,
                    run_id,
                    status="failed",
                    errors=[str(e)],
                )
            # Continue with next user (FR-012)

    logger.info("Auto-discovery complete: %d jobs across %d users", total_jobs, len(rows))


async def run_autonomous_pipeline_for_user_with_recording(user_id: str) -> str:
    """
    Run autonomous pipeline for a single user with run recording (T039, T041).

    Creates autonomous_runs row at start, runs pipeline, updates on completion.
    Used by scheduled job and by POST /api/autonomous/run (when run in foreground).

    Args:
        user_id: User UUID

    Returns:
        run_id for the created run
    """
    run_id = await create_autonomous_run(user_id)
    await _run_pipeline_and_record(user_id, run_id)
    return run_id


async def run_autonomous_pipeline_and_record(user_id: str, run_id: str) -> None:
    """
    Run pipeline and record results for an existing run (T041 background task).

    Used when POST /api/autonomous/run creates run first, then runs in background.

    Args:
        user_id: User UUID
        run_id: Existing autonomous_runs row id
    """
    await _run_pipeline_and_record(user_id, run_id)


async def _run_pipeline_and_record(user_id: str, run_id: str) -> None:
    """Run discovery pipeline and record results to autonomous_runs."""
    try:
        result = await run_autonomous_discovery_for_user(user_id)
        await record_autonomous_run(
            user_id,
            run_id,
            jobs_discovered=result.get("jobs_discovered", 0),
            jobs_qualified=result.get("jobs_qualified", 0),
            proposals_generated=result.get("proposals_generated", 0),
            notifications_sent=result.get("notifications_sent", 0),
            status="success",
        )
    except Exception as e:
        logger.exception("Autonomous pipeline failed for user %s: %s", user_id, e)
        await record_autonomous_run(
            user_id,
            run_id,
            status="failed",
            errors=[str(e)],
        )
