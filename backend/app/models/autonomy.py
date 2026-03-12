"""
Autonomy Models

Pydantic models for autonomous bidding settings.
Aligns with user_profiles autonomy columns (004-improve-autonomous).
"""

from typing import Optional
from pydantic import BaseModel, Field, field_validator


class AutonomousSettings(BaseModel):
    """Autonomy settings for a user."""

    auto_discovery_enabled: bool = Field(
        default=False,
        description="Whether background job discovery runs for this user",
    )
    discovery_interval_minutes: int = Field(
        default=15,
        ge=5,
        le=1440,
        description="Minutes between discovery runs",
    )
    notification_threshold: float = Field(
        default=0.8,
        ge=0.0,
        le=1.0,
        description="Min score to trigger notification",
    )
    notifications_enabled: bool = Field(
        default=True,
        description="Send email when high-quality jobs found",
    )
    auto_generate_enabled: bool = Field(
        default=False,
        description="Auto-generate proposals for high-confidence jobs",
    )
    auto_generate_threshold: float = Field(
        default=0.85,
        ge=0.0,
        le=1.0,
        description="Min score to auto-generate proposal",
    )
    autonomy_level: str = Field(
        default="assisted",
        description="assisted, discovery_only, semi_autonomous, full_auto_generate",
    )

    @field_validator("autonomy_level")
    @classmethod
    def validate_autonomy_level(cls, v: str) -> str:
        """Validate autonomy level."""
        allowed = {"assisted", "discovery_only", "semi_autonomous", "full_auto_generate"}
        if v not in allowed:
            raise ValueError(f"autonomy_level must be one of {allowed}")
        return v


class AutonomousStatusResponse(BaseModel):
    """Response for GET /api/autonomous/status (T040)."""

    last_run_at: Optional[str] = Field(None, description="ISO timestamp of last run started_at")
    status: Optional[str] = Field(None, description="success, running, failed")
    jobs_discovered: int = 0
    jobs_qualified: int = 0
    proposals_auto_generated: int = 0
    notifications_sent: int = 0
    errors: Optional[list] = Field(None, description="Error messages if failed")


class AutonomousRunResponse(BaseModel):
    """Response for POST /api/autonomous/run (T041)."""

    run_id: str = Field(..., description="UUID of the created run")
    status: str = Field(default="started", description="started when background task queued")


class AutonomousSettingsUpdate(BaseModel):
    """Model for updating autonomy settings (partial update)."""

    auto_discovery_enabled: Optional[bool] = None
    discovery_interval_minutes: Optional[int] = Field(None, ge=5, le=1440)
    notification_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    notifications_enabled: Optional[bool] = None
    auto_generate_enabled: Optional[bool] = None
    auto_generate_threshold: Optional[float] = Field(None, ge=0.0, le=1.0)
    autonomy_level: Optional[str] = None

    @field_validator("autonomy_level")
    @classmethod
    def validate_autonomy_level(cls, v: Optional[str]) -> Optional[str]:
        """Validate autonomy level if provided."""
        if v is not None:
            allowed = {"assisted", "discovery_only", "semi_autonomous", "full_auto_generate"}
            if v not in allowed:
                raise ValueError(f"autonomy_level must be one of {allowed}")
        return v
