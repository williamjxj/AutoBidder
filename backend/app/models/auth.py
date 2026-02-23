"""
Authentication Models - User and Token Models
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from uuid import UUID


class UserBase(BaseModel):
    """Base user model."""
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=72,
        description="Password must be between 8 and 72 characters"
    )


class UserLogin(BaseModel):
    """User login model."""
    email: EmailStr
    password: str


class UserResponse(UserBase):
    """User response model (without password)."""
    id: UUID
    is_active: bool
    is_verified: bool
    last_login_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    """JWT token response."""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenData(BaseModel):
    """Token payload data."""
    user_id: str
    email: str
    exp: datetime
