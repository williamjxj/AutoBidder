"""
Session State Models

Pydantic models for user session state management.
Matches database schema from user_session_states table.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import json


class NavigationEntry(BaseModel):
    """
    Navigation history entry.
    
    Attributes:
        path: URL path navigated to
        timestamp: When navigation occurred
        entity_type: Type of entity being viewed (optional)
        entity_id: ID of entity being viewed (optional)
    """
    
    path: str = Field(..., min_length=1, max_length=500)
    timestamp: str  # ISO 8601 datetime string
    entity_type: Optional[str] = Field(None, max_length=50)
    entity_id: Optional[str] = Field(None, max_length=100)


class SessionStateBase(BaseModel):
    """Base session state model with common fields."""
    
    current_path: str = Field(..., min_length=1, max_length=500)
    navigation_history: List[NavigationEntry] = Field(default_factory=list, max_length=50)
    active_entity_type: Optional[str] = Field(None, max_length=50)
    active_entity_id: Optional[str] = Field(None, max_length=100)
    scroll_position: Dict[str, int] = Field(default_factory=dict)
    filters: Dict[str, Any] = Field(default_factory=dict)
    ui_state: Dict[str, Any] = Field(default_factory=dict)
    
    @field_validator('navigation_history', mode='before')
    @classmethod
    def validate_navigation_history(cls, v: Any) -> List[NavigationEntry]:
        """
        Validate and convert navigation history.
        
        Handles both list of dicts and list of NavigationEntry objects.
        Also handles JSON strings from database.
        """
        if isinstance(v, str):
            # Parse JSON string from database
            try:
                v = json.loads(v)
            except json.JSONDecodeError:
                return []
        
        if not isinstance(v, list):
            return []
        
        # Convert dicts to NavigationEntry objects
        result = []
        for item in v:
            if isinstance(item, dict):
                result.append(NavigationEntry(**item))
            elif isinstance(item, NavigationEntry):
                result.append(item)
        
        return result
    
    @field_validator('scroll_position', 'filters', 'ui_state', mode='before')
    @classmethod
    def validate_json_field(cls, v: Any) -> Dict[str, Any]:
        """
        Validate and convert JSON fields.
        
        Handles both dict objects and JSON strings from database.
        """
        if isinstance(v, str):
            try:
                return json.loads(v)
            except json.JSONDecodeError:
                return {}
        
        if isinstance(v, dict):
            return v
        
        return {}


class SessionStateCreate(SessionStateBase):
    """Model for creating new session state (user_id will be added from auth)."""
    
    pass


class SessionStateUpdate(SessionStateBase):
    """Model for updating session state (all fields optional)."""
    
    current_path: Optional[str] = Field(None, min_length=1, max_length=500)
    navigation_history: Optional[List[NavigationEntry]] = None
    active_entity_type: Optional[str] = None
    active_entity_id: Optional[str] = None
    scroll_position: Optional[Dict[str, int]] = None
    filters: Optional[Dict[str, Any]] = None
    ui_state: Optional[Dict[str, Any]] = None


class SessionState(SessionStateBase):
    """
    Complete session state model with database fields.
    
    Matches user_session_states table schema.
    """
    
    id: str = Field(..., description="UUID primary key")
    user_id: str = Field(..., description="User UUID from auth.users")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        """Pydantic config."""
        from_attributes = True  # Allow creation from ORM models


class SessionStateResponse(BaseModel):
    """API response wrapper for session state."""
    
    session_state: SessionState


class SessionStateListResponse(BaseModel):
    """API response wrapper for session state list."""
    
    session_states: List[SessionState]
    count: int
