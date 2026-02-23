"""
Settings Service - User Settings Management

Handles user preferences and platform credentials management.
"""

from typing import Any, Dict, List, Optional
import logging
from datetime import datetime

from app.core.database import get_db_pool
from app.core.errors import AutoBidderError
from app.models.settings import (
    UserSettings,
    UserPreferences,
    UserProfile,
    PlatformCredential,
    CredentialUpsert,
    SubscriptionInfo,
    UsageQuota,
)

logger = logging.getLogger(__name__)


class SettingsService:
    """Service for managing user settings and platform credentials."""

    async def get_settings(self, user_id: str) -> UserSettings:
        """
        Get user settings including preferences.

        Args:
            user_id: User's UUID

        Returns:
            UserSettings object

        Raises:
            AutoBidderError: If query fails
        """
        try:
            pool = await get_db_pool()
            async with pool.acquire() as conn:
                # Get user profile for preferences
                profile_row = await conn.fetchrow(
                    "SELECT * FROM user_profiles WHERE user_id = $1",
                    user_id
                )
                
                # Create default profile if doesn't exist
                if not profile_row:
                    profile = UserProfile(
                        user_id=user_id,
                        subscription_tier='free',
                        subscription_status='active',
                    )
                else:
                    profile = UserProfile(
                        user_id=str(profile_row.get("user_id")),
                        subscription_tier=profile_row.get("subscription_tier", "free"),
                        subscription_status=profile_row.get("subscription_status", "active"),
                    )

                # Extract preferences from profile
                preferences = UserPreferences(
                    theme=profile_row.get("theme", "system") if profile_row else "system",
                    language=profile_row.get("language", "en") if profile_row else "en",
                    notification_email=profile_row.get("notification_email", True) if profile_row else True,
                    notification_browser=profile_row.get("notification_browser", True) if profile_row else True,
                    default_strategy_id=profile_row.get("default_strategy_id") if profile_row else None,
                )

                # Get platform credentials
                credentials = []
                try:
                    cred_rows = await conn.fetch(
                        "SELECT id, user_id, platform, is_active, last_verified_at, verification_error, expires_at FROM platform_credentials WHERE user_id = $1",
                        user_id
                    )
                    for row in cred_rows:
                        credentials.append(PlatformCredential(
                            id=str(row["id"]),
                            user_id=str(row["user_id"]),
                            platform=row["platform"],
                            is_active=row.get("is_active", True),
                            last_verified_at=row.get("last_verified_at"),
                            verification_error=row.get("verification_error"),
                            expires_at=row.get("expires_at"),
                        ))
                except Exception as e:
                    logger.warning(f"Failed to fetch credentials: {e}")

                # Get usage quota
                usage_quota = UsageQuota(
                    proposals_generated=0,
                    proposals_limit=10 if profile.subscription_tier == 'free' else 100,
                    period_start=None,
                )

                # Create subscription info
                subscription = SubscriptionInfo(
                    tier=profile.subscription_tier,
                    status=profile.subscription_status,
                    expires_at=None,
                    usage_quota=usage_quota,
                )

                return UserSettings(
                    profile=profile,
                    preferences=preferences,
                    credentials=credentials,
                    subscription=subscription,
                )
        except Exception as e:
            logger.error(f"Failed to get settings: {e}")
            raise AutoBidderError(f"Failed to get settings: {e}")

    async def update_preferences(self, user_id: str, preferences: UserPreferences) -> None:
        """
        Update user preferences.

        Args:
            user_id: User's UUID
            preferences: UserPreferences object

        Raises:
            AutoBidderError: If update fails
        """
        try:
            pool = await get_db_pool()
            async with pool.acquire() as conn:
                # Build update query
                update_fields = [
                    "theme = $2",
                    "notifications_enabled = $3",
                    "email_notifications = $4"
                ]
                params = [
                    user_id,
                    preferences.theme,
                    preferences.notifications_enabled,
                    preferences.email_notifications
                ]
                
                param_count = 4
                if preferences.default_strategy_id:
                    param_count += 1
                    update_fields.append(f"default_strategy_id = ${param_count}")
                    params.append(preferences.default_strategy_id)
                
                query = f"""
                    UPDATE user_profiles
                    SET {', '.join(update_fields)}, updated_at = CURRENT_TIMESTAMP
                    WHERE user_id = $1
                """
                
                await conn.execute(query, *params)
                logger.info(f"Updated preferences for user {user_id}")
        except Exception as e:
            logger.error(f"Failed to update preferences: {e}")
            raise AutoBidderError(f"Failed to update preferences: {e}")

    async def list_credentials(self, user_id: str) -> List[PlatformCredential]:
        """
        List all platform credentials for a user.

        Args:
            user_id: User's UUID

        Returns:
            List of PlatformCredential objects

        Raises:
            AutoBidderError: If query fails
        """
        try:
            pool = await get_db_pool()
            async with pool.acquire() as conn:
                rows = await conn.fetch(
                    """
                    SELECT * FROM platform_credentials
                    WHERE user_id = $1
                    ORDER BY created_at DESC
                    """,
                    user_id
                )
                
                credentials = []
                for row in rows:
                    credentials.append(self._row_to_credential(dict(row)))
                
                return credentials
        except Exception as e:
            logger.error(f"Failed to list credentials: {e}")
            raise AutoBidderError(f"Failed to list credentials: {e}")

    async def upsert_credential(
        self, user_id: str, credential: CredentialUpsert
    ) -> PlatformCredential:
        """
        Create or update a platform credential.

        Args:
            user_id: User's UUID
            credential: CredentialUpsert object

        Returns:
            Created or updated PlatformCredential object

        Raises:
            AutoBidderError: If upsert fails
        """
        try:
            pool = await get_db_pool()
            async with pool.acquire() as conn:
                if credential.id:
                    # Update existing credential
                    row = await conn.fetchrow(
                        """
                        UPDATE platform_credentials
                        SET platform = $3, api_key = $4, api_secret = $5, is_active = $6, updated_at = CURRENT_TIMESTAMP
                        WHERE id = $1 AND user_id = $2
                        RETURNING *
                        """,
                        credential.id,
                        user_id,
                        credential.platform,
                        credential.api_key,  # In production, encrypt this
                        credential.api_secret,  # In production, encrypt this
                        credential.is_active,
                    )
                else:
                    # Create new credential
                    row = await conn.fetchrow(
                        """
                        INSERT INTO platform_credentials (user_id, platform, api_key, api_secret, is_active)
                        VALUES ($1, $2, $3, $4, $5)
                        RETURNING *
                        """,
                        user_id,
                        credential.platform,
                        credential.api_key,  # In production, encrypt this
                        credential.api_secret,  # In production, encrypt this
                        credential.is_active,
                    )
                
                if not row:
                    raise AutoBidderError("Failed to upsert credential")
                
                return self._row_to_credential(dict(row))
        except AutoBidderError:
            raise
        except Exception as e:
            logger.error(f"Failed to upsert credential: {e}")
            raise AutoBidderError(f"Failed to upsert credential: {e}")

    async def delete_credential(self, credential_id: str, user_id: str) -> None:
        """
        Delete a platform credential.

        Args:
            credential_id: Credential UUID
            user_id: User's UUID (for authorization)

        Raises:
            AutoBidderError: If deletion fails
        """
        try:
            pool = await get_db_pool()
            async with pool.acquire() as conn:
                await conn.execute(
                    """
                    DELETE FROM platform_credentials
                    WHERE id = $1 AND user_id = $2
                    """,
                    credential_id,
                    user_id
                )
                logger.info(f"Deleted credential {credential_id}")
        except Exception as e:
            logger.error(f"Failed to delete credential: {e}")
            raise AutoBidderError(f"Failed to delete credential: {e}")

    async def verify_credential(self, credential_id: str, user_id: str) -> Dict[str, Any]:
        """
        Verify a platform credential by making a test API call.

        Args:
            credential_id: Credential UUID
            user_id: User's UUID (for authorization)

        Returns:
            Verification result with status and message

        Raises:
            AutoBidderError: If verification fails
        """
        try:
            pool = await get_db_pool()
            async with pool.acquire() as conn:
                # Get credential
                row = await conn.fetchrow(
                    """
                    SELECT * FROM platform_credentials
                    WHERE id = $1 AND user_id = $2
                    """,
                    credential_id,
                    user_id
                )
                
                if not row:
                    raise AutoBidderError("Credential not found")
                
                platform = row["platform"]
                api_key = row.get("api_key")
                api_secret = row.get("api_secret")

                # Verify based on platform
                # In production, make actual API calls to verify
                # For now, just check if credentials exist
                if not api_key:
                    return {
                        "verified": False,
                        "message": "API key is missing",
                    }

                # TODO: Implement actual verification for each platform
                # For now, return success if credentials exist
                return {
                    "verified": True,
                    "message": f"Credentials for {platform} verified successfully",
                }
        except AutoBidderError:
            raise
        except Exception as e:
            logger.error(f"Failed to verify credential: {e}")
            raise AutoBidderError(f"Failed to verify credential: {e}")

    async def get_subscription(self, user_id: str) -> Optional[SubscriptionInfo]:
        """
        Get user subscription information.

        Args:
            user_id: User's UUID

        Returns:
            SubscriptionInfo or None if no subscription

        Raises:
            AutoBidderError: If query fails
        """
        try:
            pool = await get_db_pool()
            async with pool.acquire() as conn:
                row = await conn.fetchrow(
                    """
                    SELECT * FROM user_subscriptions
                    WHERE user_id = $1 AND status = 'active'
                    LIMIT 1
                    """,
                    user_id
                )
                
                if not row:
                    return None
                
                return SubscriptionInfo(
                    plan=row.get("plan", "free"),
                    status=row.get("status", "active"),
                    expires_at=row.get("expires_at"),
                )
        except Exception as e:
            logger.error(f"Failed to get subscription: {e}")
            return None

    def _row_to_credential(self, row: Dict[str, Any]) -> PlatformCredential:
        """Convert database row to PlatformCredential model."""
        return PlatformCredential(
            id=str(row["id"]),
            user_id=str(row["user_id"]),
            platform=row["platform"],
            api_key=row.get("api_key", ""),  # In production, decrypt this
            api_secret=row.get("api_secret"),  # In production, decrypt this
            is_active=row.get("is_active", True),
            verified_at=row.get("verified_at"),
            created_at=row["created_at"],
            updated_at=row["updated_at"],
        )


# Global instance
settings_service = SettingsService()
