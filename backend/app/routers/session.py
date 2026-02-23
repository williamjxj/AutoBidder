"""
Session State Router

FastAPI router for session state management endpoints.
Implements API contract from contracts/session-state-api.yaml
"""

from typing import Optional
import logging
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.responses import JSONResponse

from app.routers.auth import get_current_user
from app.models.auth import UserResponse
from app.models.session_state import (
    SessionState,
    SessionStateCreate,
    SessionStateUpdate,
    SessionStateResponse,
)
from app.services.session_manager import session_manager
from app.core.errors import AutoBidderError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/session/state",
    response_model=SessionState,
    status_code=status.HTTP_200_OK,
    summary="Get session state",
    description="Retrieve the current session state for the authenticated user",
)
async def get_session_state(
    current_user: UserResponse = Depends(get_current_user),
) -> SessionState:
    """
    Get user's session state.
    
    Returns:
        SessionState object or 404 if not found
    """
    try:
        user_id = str(current_user.id)
        
        session_state = await session_manager.get_state(user_id)
        
        if not session_state:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session state not found",
            )
        
        return session_state
    except HTTPException:
        raise
    except AutoBidderError as e:
        logger.error(f"Error getting session state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": str(e),
                "message": "Failed to retrieve session state",
                "action": "Please try refreshing the page. If the problem persists, contact support.",
            },
        )
    except Exception as e:
        logger.error(f"Unexpected error getting session state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "An unexpected error occurred while retrieving session state",
                "action": "Please try again. If the problem persists, contact support.",
            },
        )


@router.put(
    "/session/state",
    response_model=SessionState,
    status_code=status.HTTP_200_OK,
    summary="Update session state",
    description="Create or update session state for the authenticated user",
)
async def update_session_state(
    session_update: SessionStateUpdate,
    current_user: UserResponse = Depends(get_current_user),
) -> SessionState:
    """
    Update user's session state.
    
    Args:
        session_update: Session state updates
        
    Returns:
        Updated SessionState object
    """
    try:
        user_id = str(current_user.id)
        
        # Validate payload size (max 100KB as per spec)
        # FastAPI already validates JSON structure
        
        updated_state = await session_manager.update_state(user_id, session_update)
        
        return updated_state
    except HTTPException:
        raise
    except AutoBidderError as e:
        logger.error(f"Error updating session state: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": str(e),
                "message": "Invalid session state data",
                "action": "Please check your input and try again. Ensure all required fields are provided.",
            },
        )
    except Exception as e:
        logger.error(f"Unexpected error updating session state: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Internal server error",
                "message": "Failed to update session state",
                "action": "Please try again. Your changes may not have been saved.",
            },
        )


@router.delete(
    "/session/state",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete session state",
    description="Delete session state for the authenticated user",
)
async def delete_session_state(
    current_user: UserResponse = Depends(get_current_user),
) -> None:
    """
    Delete user's session state.
    
    Returns:
        204 No Content on success
    """
    try:
        user_id = str(current_user.id)
        
        await session_manager.delete_state(user_id)
        
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting session state: {e}")
        # Return success even if deletion fails (idempotent)
        return JSONResponse(
            status_code=status.HTTP_204_NO_CONTENT,
            content=None,
        )


@router.post(
    "/session/cleanup",
    status_code=status.HTTP_200_OK,
    summary="Cleanup expired sessions",
    description="Clean up expired session states (admin endpoint)",
)
async def cleanup_expired_sessions(
    ttl_hours: int = 24,
) -> dict:
    """
    Clean up expired session states.
    
    Args:
        ttl_hours: Time-to-live in hours (default: 24)
        
    Returns:
        Cleanup result with count of deleted sessions
    """
    try:
        count = await session_manager.cleanup_expired(ttl_hours)
        
        return {
            "message": "Cleanup completed",
            "deleted_count": count,
            "ttl_hours": ttl_hours,
        }
    except Exception as e:
        logger.error(f"Error cleaning up expired sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Cleanup failed",
        )
