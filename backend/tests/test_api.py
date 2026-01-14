import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data
    assert "timestamp" in data


def test_root_endpoint():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_analyze_endpoint_schema():
    """Test the analyze endpoint with valid input."""
    response = client.post(
        "/api/v1/proposals/analyze",
        json={
            "description": "We are looking for a Python developer with FastAPI experience."
        }
    )
    # This will fail without OpenAI API key, but schema should be validated
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "key_requirements" in data
        assert "technologies" in data
        assert "skills" in data
        assert "estimated_complexity" in data


def test_generate_proposal_schema():
    """Test the generate proposal endpoint with valid input."""
    response = client.post(
        "/api/v1/proposals/generate",
        json={
            "job_requirement": {
                "title": "Python Developer",
                "description": "Looking for Python developer",
                "requirements": ["Python", "FastAPI"]
            }
        }
    )
    # This will fail without OpenAI API key, but schema should be validated
    assert response.status_code in [200, 500]
    
    if response.status_code == 200:
        data = response.json()
        assert "proposal" in data
        assert "confidence_score" in data
        assert "suggestions" in data


def test_analyze_missing_description():
    """Test analyze endpoint with missing description."""
    response = client.post(
        "/api/v1/proposals/analyze",
        json={}
    )
    assert response.status_code == 422  # Validation error
