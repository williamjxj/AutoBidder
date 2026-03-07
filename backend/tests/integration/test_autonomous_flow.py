"""
Integration tests for autonomous discovery pipeline.

Per specs/004-improve-autonomous/tasks.md T044.
Tests discovery → qualification → notification → auto-generate flow via API.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app
from app.models.auth import UserResponse
from app.routers.auth import get_current_user


def _db_available() -> bool:
    """Check if database is reachable (for skip condition)."""

    async def _check() -> bool:
        try:
            from app.core.database import get_db_pool

            pool = await get_db_pool()
            async with pool.acquire() as conn:
                await conn.fetchval("SELECT 1")
            return True
        except Exception:
            return False

    try:
        return asyncio.run(_check())
    except Exception:
        return False


# Skip DB-dependent tests when database is not available
db_required = pytest.mark.skipif(
    not _db_available(),
    reason="Database not available (start Postgres, apply migrations)",
)


@pytest.fixture
def mock_user() -> UserResponse:
    """Fake user for dependency override."""
    now = datetime.now(timezone.utc)
    return UserResponse(
        id="00000000-0000-0000-0000-000000000001",
        email="test@example.com",
        is_active=True,
        is_verified=True,
        created_at=now,
        updated_at=now,
    )


@pytest.mark.integration
@pytest.mark.asyncio
async def test_autonomous_settings_unauthorized_returns_401() -> None:
    """Unauthenticated request to autonomous settings should return 401."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as client:
        response = await client.get("/api/autonomous/settings")
        assert response.status_code == 401


@pytest.mark.integration
@pytest.mark.asyncio
@db_required
async def test_autonomous_settings_returns_defaults_when_authenticated(
    mock_user: UserResponse,
) -> None:
    """GET /api/autonomous/settings returns default autonomy settings."""
    async def override_user() -> UserResponse:
        return mock_user

    app.dependency_overrides[get_current_user] = override_user
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/api/autonomous/settings")
            assert response.status_code == 200
            data = response.json()
            assert "auto_discovery_enabled" in data
            assert "autonomy_level" in data
            assert "qualification_threshold" in data
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.integration
@pytest.mark.asyncio
@db_required
async def test_autonomous_status_returns_shape_when_authenticated(
    mock_user: UserResponse,
) -> None:
    """GET /api/autonomous/status returns expected shape (may be empty)."""
    async def override_user() -> UserResponse:
        return mock_user

    app.dependency_overrides[get_current_user] = override_user
    try:
        async with AsyncClient(
            transport=ASGITransport(app=app),
            base_url="http://test",
        ) as client:
            response = await client.get("/api/autonomous/status")
            assert response.status_code == 200
            data = response.json()
            assert "jobs_discovered" in data
            assert "jobs_qualified" in data
            assert "proposals_auto_generated" in data
            assert "notifications_sent" in data
            assert "status" in data
    finally:
        app.dependency_overrides.pop(get_current_user, None)


@pytest.mark.integration
@pytest.mark.asyncio
@db_required
async def test_autonomous_run_returns_run_id_and_started(
    mock_user: UserResponse,
) -> None:
    """POST /api/autonomous/run returns run_id and status=started."""
    async def override_user() -> UserResponse:
        return mock_user

    app.dependency_overrides[get_current_user] = override_user
    # Mock background task to avoid connection pool conflicts during test teardown
    with patch(
        "app.routers.autonomous.run_autonomous_pipeline_and_record",
        new_callable=AsyncMock,
    ):
        try:
            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                response = await client.post("/api/autonomous/run")
                assert response.status_code == 200
                data = response.json()
                assert "run_id" in data
                assert data.get("status") == "started"
                assert len(data.get("run_id", "")) > 0
        finally:
            app.dependency_overrides.pop(get_current_user, None)
