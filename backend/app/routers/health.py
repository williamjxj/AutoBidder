"""
Health Check Router

Provides endpoints for monitoring service health and dependencies.
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import httpx
import logging

from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    version: str
    environment: str


class DependencyStatus(BaseModel):
    """Dependency status model."""

    name: str
    status: str
    message: str | None = None


class DependenciesResponse(BaseModel):
    """Dependencies health check response."""

    status: str
    dependencies: list[DependencyStatus]


@router.get("/", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Basic health check endpoint.

    Returns:
        Health status information
    """
    return HealthResponse(
        status="healthy",
        version="0.1.0",
        environment=settings.environment,
    )


@router.get("/dependencies", response_model=DependenciesResponse)
async def check_dependencies() -> DependenciesResponse:
    """
    Check health of external dependencies.

    Returns:
        Status of each dependency
    """
    dependencies = []

    # Check OpenAI API
    try:
        if settings.openai_api_key and settings.openai_api_key.startswith("sk-"):
            dependencies.append(
                DependencyStatus(
                    name="OpenAI API",
                    status="healthy",
                    message="API key configured",
                )
            )
        else:
            dependencies.append(
                DependencyStatus(
                    name="OpenAI API",
                    status="unhealthy",
                    message="Invalid API key",
                )
            )
    except Exception as e:
        dependencies.append(
            DependencyStatus(
                name="OpenAI API",
                status="unhealthy",
                message=str(e),
            )
        )

    # Check Supabase connectivity
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.supabase_url}/rest/v1/",
                headers={"apikey": settings.supabase_service_key},
                timeout=5.0,
            )
            if response.status_code == 200:
                dependencies.append(
                    DependencyStatus(
                        name="Supabase",
                        status="healthy",
                        message="Connected",
                    )
                )
            else:
                dependencies.append(
                    DependencyStatus(
                        name="Supabase",
                        status="unhealthy",
                        message=f"Status code: {response.status_code}",
                    )
                )
    except Exception as e:
        dependencies.append(
            DependencyStatus(
                name="Supabase",
                status="unhealthy",
                message=str(e),
            )
        )

    # Check ChromaDB
    try:
        import os
        from pathlib import Path

        chroma_path = Path(settings.chroma_persist_dir)
        if chroma_path.exists() and chroma_path.is_dir():
            dependencies.append(
                DependencyStatus(
                    name="ChromaDB",
                    status="healthy",
                    message=f"Storage path exists: {settings.chroma_persist_dir}",
                )
            )
        else:
            dependencies.append(
                DependencyStatus(
                    name="ChromaDB",
                    status="warning",
                    message="Storage path does not exist yet (will be created on first use)",
                )
            )
    except Exception as e:
        dependencies.append(
            DependencyStatus(
                name="ChromaDB",
                status="unhealthy",
                message=str(e),
            )
        )

    # Determine overall status
    unhealthy = any(dep.status == "unhealthy" for dep in dependencies)
    overall_status = "unhealthy" if unhealthy else "healthy"

    return DependenciesResponse(
        status=overall_status,
        dependencies=dependencies,
    )
