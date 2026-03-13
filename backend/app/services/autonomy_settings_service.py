"""
Autonomy Settings Service

Reads and writes user autonomy preferences from user_profiles.
Supports auto-discovery, notifications, and auto-generation settings.
"""

from typing import Optional

from app.core.database import get_db_pool
from app.models.autonomy import AutonomousSettings, AutonomousSettingsUpdate

# Default values matching data-model.md
DEFAULT_AUTO_DISCOVERY_ENABLED = False
DEFAULT_DISCOVERY_INTERVAL_MINUTES = 15
DEFAULT_NOTIFICATIONS_ENABLED = True
DEFAULT_AUTO_GENERATE_ENABLED = False
DEFAULT_AUTONOMY_LEVEL = "assisted"


async def get_autonomy_settings(user_id: str) -> AutonomousSettings:
    """
    Get autonomy settings for a user.

    Args:
        user_id: User's UUID

    Returns:
        AutonomousSettings with current or default values
    """
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT
                COALESCE(auto_discovery_enabled, $2) AS auto_discovery_enabled,
                COALESCE(discovery_interval_minutes, $3) AS discovery_interval_minutes,
                COALESCE(notifications_enabled, $4) AS notifications_enabled,
                COALESCE(auto_generate_enabled, $5) AS auto_generate_enabled,
                COALESCE(autonomy_level, $6) AS autonomy_level
            FROM user_profiles
            WHERE user_id = $1
            """,
            user_id,
            DEFAULT_AUTO_DISCOVERY_ENABLED,
            DEFAULT_DISCOVERY_INTERVAL_MINUTES,
            DEFAULT_NOTIFICATIONS_ENABLED,
            DEFAULT_AUTO_GENERATE_ENABLED,
            DEFAULT_AUTONOMY_LEVEL,
        )

    if not row:
        return AutonomousSettings(
            auto_discovery_enabled=DEFAULT_AUTO_DISCOVERY_ENABLED,
            discovery_interval_minutes=DEFAULT_DISCOVERY_INTERVAL_MINUTES,
            notifications_enabled=DEFAULT_NOTIFICATIONS_ENABLED,
            auto_generate_enabled=DEFAULT_AUTO_GENERATE_ENABLED,
            autonomy_level=DEFAULT_AUTONOMY_LEVEL,
        )

    return AutonomousSettings(
        auto_discovery_enabled=bool(row["auto_discovery_enabled"]),
        discovery_interval_minutes=int(row["discovery_interval_minutes"]),
        notifications_enabled=bool(row["notifications_enabled"]),
        auto_generate_enabled=bool(row["auto_generate_enabled"]),
        autonomy_level=str(row["autonomy_level"]),
    )


async def update_autonomy_settings(
    user_id: str, update: AutonomousSettingsUpdate
) -> AutonomousSettings:
    """
    Update autonomy settings for a user.

    Args:
        user_id: User's UUID
        update: Partial settings to update

    Returns:
        Updated AutonomousSettings
    """
    pool = await get_db_pool()

    # Build dynamic update from non-None fields
    updates: list[str] = []
    params: list[object] = []
    idx = 1

    if update.auto_discovery_enabled is not None:
        updates.append(f"auto_discovery_enabled = ${idx}")
        params.append(update.auto_discovery_enabled)
        idx += 1
    if update.discovery_interval_minutes is not None:
        updates.append(f"discovery_interval_minutes = ${idx}")
        params.append(update.discovery_interval_minutes)
        idx += 1
    if update.notifications_enabled is not None:
        updates.append(f"notifications_enabled = ${idx}")
        params.append(update.notifications_enabled)
        idx += 1
    if update.auto_generate_enabled is not None:
        updates.append(f"auto_generate_enabled = ${idx}")
        params.append(update.auto_generate_enabled)
        idx += 1
    if update.autonomy_level is not None:
        updates.append(f"autonomy_level = ${idx}")
        params.append(update.autonomy_level)
        idx += 1

    if not updates:
        return await get_autonomy_settings(user_id)

    updates.append("updated_at = NOW()")
    params.append(user_id)

    async with pool.acquire() as conn:
        await conn.execute(
            f"""
            UPDATE user_profiles
            SET {", ".join(updates)}
            WHERE user_id = ${idx}
            """,
            *params,
        )

    return await get_autonomy_settings(user_id)


async def record_autonomous_run(
    user_id: str,
    run_id: str,
    jobs_discovered: int = 0,
    proposals_generated: int = 0,
    notifications_sent: int = 0,
    status: str = "success",
    errors: Optional[list] = None,
) -> None:
    """Update autonomous_runs row on completion (T039)."""
    pool = await get_db_pool()
    import json
    async with pool.acquire() as conn:
        await conn.execute(
            """
            UPDATE autonomous_runs
            SET completed_at = NOW(), status = $2, jobs_discovered = $3,
                proposals_generated = $4, notifications_sent = $5,
                errors = $6::jsonb
            WHERE id = $1::uuid
            """,
            run_id,
            status,
            jobs_discovered,
            proposals_generated,
            notifications_sent,
            json.dumps(errors) if errors else None,
        )


async def create_autonomous_run(user_id: str) -> str:
    """Create autonomous_runs row at pipeline start. Returns run_id."""
    pool = await get_db_pool()
    from uuid import uuid4
    run_id = str(uuid4())
    async with pool.acquire() as conn:
        await conn.execute(
            """
            INSERT INTO autonomous_runs (id, user_id, status)
            VALUES ($1::uuid, $2::uuid, 'running')
            """,
            run_id,
            user_id,
        )
    return run_id


async def get_last_autonomous_run(user_id: str) -> Optional[dict]:
    """Get most recent autonomous run for user (T040)."""
    pool = await get_db_pool()
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT started_at, completed_at, status, jobs_discovered,
                     proposals_generated, notifications_sent, errors
            FROM autonomous_runs
            WHERE user_id = $1::uuid
            ORDER BY started_at DESC
            LIMIT 1
            """,
            user_id,
        )
    if not row:
        return None
    return dict(row)
