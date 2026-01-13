"""
Workflow Analytics Models

Pydantic models for workflow analytics event tracking.
Matches database schema from workflow_analytics table.
"""

from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class WorkflowAnalyticsEventBase(BaseModel):
    """Base analytics event model."""
    
    event_type: str = Field(..., min_length=1, max_length=50, description="Type of workflow event")
    entity_type: Optional[str] = Field(None, max_length=50, description="Type of entity involved")
    entity_id: Optional[str] = Field(None, max_length=100, description="ID of entity involved")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional event metadata")


class WorkflowAnalyticsEventCreate(WorkflowAnalyticsEventBase):
    """Model for creating analytics event (user_id will be added from auth)."""
    
    pass


class WorkflowAnalyticsEvent(WorkflowAnalyticsEventBase):
    """
    Complete analytics event model with database fields.
    
    Matches workflow_analytics table schema.
    """
    
    id: str = Field(..., description="UUID primary key")
    user_id: str = Field(..., description="User UUID from auth.users")
    created_at: datetime = Field(..., description="Event timestamp")
    
    class Config:
        """Pydantic config."""
        from_attributes = True


class WorkflowAnalyticsResponse(BaseModel):
    """API response wrapper for single analytics event."""
    
    event: WorkflowAnalyticsEvent


class WorkflowAnalyticsListResponse(BaseModel):
    """API response wrapper for analytics event list."""
    
    events: list[WorkflowAnalyticsEvent]
    count: int


class WorkflowMetrics(BaseModel):
    """
    Aggregated workflow metrics for a user.
    
    Used for analytics dashboards and performance reporting.
    """
    
    user_id: str
    time_period: str = Field(..., description="Time period for metrics (e.g., '7d', '30d')")
    
    # Navigation metrics
    total_navigations: int = 0
    average_navigation_time_ms: float = 0
    slow_navigations: int = 0  # Count of navigations >500ms
    
    # Session metrics
    total_sessions: int = 0
    average_session_duration_minutes: float = 0
    
    # Feature usage metrics
    features_accessed: Dict[str, int] = Field(default_factory=dict)
    most_used_feature: Optional[str] = None
    
    # Draft/auto-save metrics (will be populated in Phase 4)
    drafts_saved: int = 0
    drafts_recovered: int = 0
    
    class Config:
        """Pydantic config."""
        from_attributes = True
