"""
Authentication Service - User Management and JWT Handling
"""

import asyncpg
import warnings
from datetime import datetime, timedelta
from typing import Optional
from passlib.context import CryptContext
from jose import JWTError, jwt
from fastapi import HTTPException, status
import uuid

from app.config import settings

# Suppress passlib bcrypt version warning (known compatibility issue with bcrypt 4.x)
warnings.filterwarnings("ignore", message=".*trapped.*error reading bcrypt version.*")

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT settings
SECRET_KEY = settings.jwt_secret
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days


class AuthService:
    """Authentication service for user management and JWT handling."""

    def __init__(self, db_pool: asyncpg.Pool):
        """Initialize auth service with database pool."""
        self.db_pool = db_pool

    @staticmethod
    def hash_password(password: str) -> str:
        """Hash a password using bcrypt."""
        # Bcrypt has a 72-byte limit, truncate password to be safe
        # This handles multi-byte UTF-8 characters correctly
        password_bytes = password.encode('utf-8')[:72]
        password_truncated = password_bytes.decode('utf-8', errors='ignore')
        return pwd_context.hash(password_truncated)

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against a hash."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        """Create a JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def decode_access_token(token: str) -> dict:
        """Decode and verify a JWT access token."""
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

    async def create_user(self, email: str, password: str, full_name: Optional[str] = None) -> dict:
        """Create a new user."""
        try:
            # Check if user already exists
            async with self.db_pool.acquire() as conn:
                existing_user = await conn.fetchrow(
                    "SELECT id FROM users WHERE email = $1", email
                )
                
                if existing_user:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Email already registered"
                    )
                
                # Hash password
                password_hash = self.hash_password(password)
                
                # Insert user
                user = await conn.fetchrow(
                    """
                    INSERT INTO users (email, password_hash, full_name)
                    VALUES ($1, $2, $3)
                    RETURNING id, email, full_name, is_active, is_verified, 
                              last_login_at, created_at, updated_at
                    """,
                    email, password_hash, full_name
                )
                
                return dict(user)
                
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error creating user: {str(e)}"
            )

    async def authenticate_user(self, email: str, password: str) -> Optional[dict]:
        """Authenticate a user by email and password."""
        try:
            async with self.db_pool.acquire() as conn:
                user = await conn.fetchrow(
                    """
                    SELECT id, email, password_hash, full_name, is_active, 
                           is_verified, last_login_at, created_at, updated_at
                    FROM users 
                    WHERE email = $1
                    """,
                    email
                )
                
                if not user:
                    return None
                
                # Verify password
                if not self.verify_password(password, user["password_hash"]):
                    return None
                
                # Update last login
                await conn.execute(
                    "UPDATE users SET last_login_at = NOW() WHERE id = $1",
                    user["id"]
                )
                
                # Return user without password_hash
                user_dict = dict(user)
                del user_dict["password_hash"]
                return user_dict
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error authenticating user: {str(e)}"
            )

    async def get_user_by_id(self, user_id: uuid.UUID) -> Optional[dict]:
        """Get user by ID."""
        try:
            async with self.db_pool.acquire() as conn:
                user = await conn.fetchrow(
                    """
                    SELECT id, email, full_name, is_active, is_verified,
                           last_login_at, created_at, updated_at
                    FROM users
                    WHERE id = $1
                    """,
                    user_id
                )
                
                return dict(user) if user else None
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching user: {str(e)}"
            )

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email."""
        try:
            async with self.db_pool.acquire() as conn:
                user = await conn.fetchrow(
                    """
                    SELECT id, email, full_name, is_active, is_verified,
                           last_login_at, created_at, updated_at
                    FROM users
                    WHERE email = $1
                    """,
                    email
                )
                
                return dict(user) if user else None
                
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error fetching user: {str(e)}"
            )
