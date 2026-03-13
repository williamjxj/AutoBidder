"""
Autonomous Router

API endpoints for autonomous job discovery, qualification, and settings.
"""

import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException

from app.routers.auth import get_current_user
from app.models.auth import UserResponse
from app.models.autonomy import (
    AutonomousRunResponse,
    AutonomousSettings,
    AutonomousSettingsUpdate,
    AutonomousStatusResponse,
)
from app.services.autonomy_settings_service import (
    create_autonomous_run,
    get_autonomy_settings,
    get_last_autonomous_run,
    update_autonomy_settings,
)
from app.tasks.autonomous_tasks import run_autonomous_pipeline_and_record

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/autonomous", tags=["autonomous"])


@router.get("/settings", response_model=AutonomousSettings)
async def get_autonomous_settings(
    current_user: UserResponse = Depends(get_current_user),
) -> AutonomousSettings:
    """
    Get autonomy settings for the current user (FR-002, FR-006, FR-010).
    """
    try:
        return await get_autonomy_settings(str(current_user.id))
    except Exception as e:
        logger.error("Error getting autonomy settings: %s", e)
        raise HTTPException(status_code=500, detail="Failed to get autonomy settings")


@router.put("/settings", response_model=AutonomousSettings)
async def update_autonomous_settings(
    update: AutonomousSettingsUpdate,
    current_user: UserResponse = Depends(get_current_user),
) -> AutonomousSettings:
    """
    Update autonomy settings for the current user (FR-002, FR-006, FR-010, FR-011).
    """
    try:
        return await update_autonomy_settings(str(current_user.id), update)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Error updating autonomy settings: %s", e)
        raise HTTPException(status_code=500, detail="Failed to update autonomy settings")


@router.get("/status", response_model=AutonomousStatusResponse)
async def get_autonomous_status(
    current_user: UserResponse = Depends(get_current_user),
) -> AutonomousStatusResponse:
    """
    Get last autonomous run status for the current user (T040).
    """
    try:
        run = await get_last_autonomous_run(str(current_user.id))
        if not run:
            return AutonomousStatusResponse()
        started_at = run.get("started_at")
        last_run_at = started_at.isoformat() if started_at else None
        errors = run.get("errors")
        if errors is not None and not isinstance(errors, list):
            errors = list(errors) if hasattr(errors, "__iter__") else [str(errors)]
        return AutonomousStatusResponse(
            last_run_at=last_run_at,
            status=run.get("status"),
            jobs_discovered=int(run.get("jobs_discovered") or 0),
            proposals_auto_generated=int(run.get("proposals_generated") or 0),
            notifications_sent=int(run.get("notifications_sent") or 0),
            errors=errors,
        )
    except Exception as e:
        logger.error("Error getting autonomous status: %s", e)
        raise HTTPException(status_code=500, detail="Failed to get autonomous status")


@router.post("/run", response_model=AutonomousRunResponse)
async def trigger_autonomous_run(
    background_tasks: BackgroundTasks,
    current_user: UserResponse = Depends(get_current_user),
) -> AutonomousRunResponse:
    """
    Trigger manual autonomous run for the current user (T041).
    Returns run_id immediately; pipeline runs in background.
    """
    user_id = str(current_user.id)
    run_id = await create_autonomous_run(user_id)
    background_tasks.add_task(run_autonomous_pipeline_and_record, user_id, run_id)
    return AutonomousRunResponse(run_id=run_id, status="started")
