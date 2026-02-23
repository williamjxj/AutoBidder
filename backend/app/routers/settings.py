"""
Settings Router

API endpoints for managing user settings and platform credentials.
"""

from typing import List, Optional
import logging
from fastapi import APIRouter, Depends, HTTPException

from app.routers.auth import get_current_user
from app.models.auth import UserResponse
from app.services.settings_service import settings_service
from app.models.settings import (
    UserSettings,
    UserPreferences,
    PlatformCredential,
    CredentialUpsert,
    SubscriptionInfo,
)
from app.core.errors import AutoBidderError

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/settings", response_model=UserSettings, tags=["settings"])
async def get_settings(current_user: UserResponse = Depends(get_current_user)) -> UserSettings:
    """
    Get user settings including preferences.

    Args:
        user_id: Authenticated user ID

    Returns:
        UserSettings object
    """
    try:
        return await settings_service.get_settings(str(current_user.id))
    except AutoBidderError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting settings: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/settings/preferences", tags=["settings"])
async def update_preferences(
    preferences: UserPreferences, 
    current_user: UserResponse = Depends(get_current_user)
) -> dict:
    """
    Update user preferences.

    Args:
        preferences: UserPreferences object
        user_id: Authenticated user ID

    Returns:
        Success message
    """
    try:
        await settings_service.update_preferences(str(current_user.id), preferences)
        return {"message": "Preferences updated successfully"}
    except AutoBidderError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating preferences: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/settings/credentials", response_model=List[PlatformCredential], tags=["settings"])
async def list_credentials(current_user: UserResponse = Depends(get_current_user)) -> List[PlatformCredential]:
    """
    List all platform credentials for the authenticated user.

    Args:
        current_user: Authenticated user

    Returns:
        List of credentials
    """
    try:
        return await settings_service.list_credentials(str(current_user.id))
    except AutoBidderError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error listing credentials: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/settings/credentials", response_model=PlatformCredential, tags=["settings"])
async def create_credential(
    credential: CredentialUpsert, 
    current_user: UserResponse = Depends(get_current_user)
) -> PlatformCredential:
    """
    Create a new platform credential.

    Args:
        credential: CredentialUpsert object
        current_user: Authenticated user

    Returns:
        Created credential object
    """
    try:
        return await settings_service.upsert_credential(str(current_user.id), credential)
    except AutoBidderError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error creating credential: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.put("/settings/credentials/{credential_id}", response_model=PlatformCredential, tags=["settings"])
async def update_credential(
    credential_id: str,
    credential: CredentialUpsert,
    current_user: UserResponse = Depends(get_current_user),
) -> PlatformCredential:
    """
    Update an existing platform credential.

    Args:
        credential_id: Credential UUID
        credential: CredentialUpsert object
        current_user: Authenticated user

    Returns:
        Updated credential object
    """
    try:
        credential.id = credential_id
        return await settings_service.upsert_credential(str(current_user.id), credential)
    except AutoBidderError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error updating credential: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.delete("/settings/credentials/{credential_id}", tags=["settings"])
async def delete_credential(
    credential_id: str, 
    current_user: UserResponse = Depends(get_current_user)
) -> dict:
    """
    Delete a platform credential.

    Args:
        credential_id: Credential UUID
        current_user: Authenticated user

    Returns:
        Success message
    """
    try:
        await settings_service.delete_credential(credential_id, str(current_user.id))
        return {"message": "Credential deleted successfully"}
    except AutoBidderError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error deleting credential: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.post("/settings/credentials/{credential_id}/verify", tags=["settings"])
async def verify_credential(
    credential_id: str, 
    current_user: UserResponse = Depends(get_current_user)
) -> dict:
    """
    Verify a platform credential.

    Args:
        credential_id: Credential UUID
        current_user: Authenticated user

    Returns:
        Verification result
    """
    try:
        result = await settings_service.verify_credential(credential_id, str(current_user.id))
        return result
    except AutoBidderError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error verifying credential: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/settings/subscription", response_model=Optional[SubscriptionInfo], tags=["settings"])
async def get_subscription(
    current_user: UserResponse = Depends(get_current_user)
) -> Optional[SubscriptionInfo]:
    """
    Get user subscription information.

    Args:
        current_user: Authenticated user

    Returns:
        SubscriptionInfo or None
    """
    try:
        return await settings_service.get_subscription(str(current_user.id))
    except Exception as e:
        logger.error(f"Error getting subscription: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
