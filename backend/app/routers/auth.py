"""
Authentication Router - User Registration and Login
"""

from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Optional
import uuid

from app.models.auth import UserCreate, UserLogin, UserResponse, Token
from app.services.auth_service import AuthService
from app.core.database import get_db_pool


router = APIRouter()


async def get_auth_service() -> AuthService:
    """Dependency to get auth service."""
    pool = await get_db_pool()
    return AuthService(pool)


async def get_current_user(
    authorization: Optional[str] = Header(None),
    auth_service: AuthService = Depends(get_auth_service)
) -> UserResponse:
    """
    Dependency to get current authenticated user from JWT token.
    
    Args:
        authorization: Authorization header with Bearer token
        auth_service: Auth service instance
        
    Returns:
        Current user
        
    Raises:
        HTTPException: If token is missing or invalid
    """
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = authorization.replace("Bearer ", "")
    
    try:
        payload = AuthService.decode_access_token(token)
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        user = await auth_service.get_user_by_id(uuid.UUID(user_id))
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return UserResponse(**user)
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


@router.post("/auth/signup", response_model=Token, status_code=status.HTTP_201_CREATED)
async def signup(
    user_data: UserCreate,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        auth_service: Auth service instance
        
    Returns:
        JWT token and user data
    """
    try:
        # Create user
        user = await auth_service.create_user(
            email=user_data.email,
            password=user_data.password,
            full_name=user_data.full_name
        )
        
        # Create access token
        access_token = AuthService.create_access_token(
            data={"user_id": str(user["id"]), "email": user["email"]}
        )
        
        # Return token and user
        return Token(
            access_token=access_token,
            user=UserResponse(**user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during signup: {str(e)}"
        )


@router.post("/auth/login", response_model=Token)
async def login(
    credentials: UserLogin,
    auth_service: AuthService = Depends(get_auth_service)
):
    """
    Login with email and password.
    
    Args:
        credentials: User login credentials
        auth_service: Auth service instance
        
    Returns:
        JWT token and user data
    """
    try:
        # Authenticate user
        user = await auth_service.authenticate_user(
            email=credentials.email,
            password=credentials.password
        )
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Check if user is active
        if not user.get("is_active", True):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Account is disabled"
            )
        
        # Create access token
        access_token = AuthService.create_access_token(
            data={"user_id": str(user["id"]), "email": user["email"]}
        )
        
        # Return token and user
        return Token(
            access_token=access_token,
            user=UserResponse(**user)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error during login: {str(e)}"
        )


@router.get("/auth/me", response_model=UserResponse)
async def get_me(current_user: UserResponse = Depends(get_current_user)):
    """
    Get current authenticated user.
    
    Args:
        current_user: Current user from dependency
        
    Returns:
        Current user data
    """
    return current_user


@router.post("/auth/logout")
async def logout():
    """
    Logout endpoint (client-side token removal).
    
    Since we're using JWT tokens, actual logout happens on the client side
    by removing the token. This endpoint is mainly for consistency.
    
    Returns:
        Success message
    """
    return {"message": "Successfully logged out"}
