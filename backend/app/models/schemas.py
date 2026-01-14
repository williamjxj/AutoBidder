from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime


class JobRequirement(BaseModel):
    """Model for job requirements."""
    title: str = Field(..., description="Job title")
    description: str = Field(..., description="Job description")
    requirements: List[str] = Field(default_factory=list, description="Job requirements")
    budget: Optional[str] = Field(None, description="Budget information")
    deadline: Optional[str] = Field(None, description="Deadline information")


class ProposalRequest(BaseModel):
    """Request model for generating proposals."""
    job_requirement: JobRequirement
    user_profile: Optional[Dict] = Field(None, description="User profile information")
    custom_instructions: Optional[str] = Field(None, description="Custom instructions")


class ProposalResponse(BaseModel):
    """Response model for generated proposals."""
    proposal: str = Field(..., description="Generated proposal text")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Confidence score")
    suggestions: List[str] = Field(default_factory=list, description="Improvement suggestions")
    sources: List[str] = Field(default_factory=list, description="Sources used for RAG")


class AnalysisRequest(BaseModel):
    """Request model for analyzing job requirements."""
    description: str = Field(..., description="Job description to analyze")


class AnalysisResponse(BaseModel):
    """Response model for job analysis."""
    key_requirements: List[str] = Field(default_factory=list)
    technologies: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    estimated_complexity: str = Field(..., description="Complexity level")
    match_score: Optional[float] = Field(None, ge=0.0, le=1.0)


class DocumentUpload(BaseModel):
    """Model for document upload."""
    filename: str
    content: str
    document_type: str = Field(default="general", description="Type of document")


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    timestamp: datetime
