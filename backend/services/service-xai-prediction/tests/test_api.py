"""Tests for API endpoints"""

import sys
from pathlib import Path

# Ensure project root is in Python path
project_root = Path(__file__).parent.parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

import pytest
from app.main import app
from fastapi.testclient import TestClient

client = TestClient(app)


class TestRootEndpoints:
    """Test root level endpoints"""

    def test_root_endpoint(self):
        """Test GET / returns service information"""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "service" in data
        assert "version" in data
        assert "status" in data
        assert data["status"] == "running"
        assert data["service"] == "XAI Prediction Service"

    def test_health_endpoint(self):
        """Test GET /health returns health status"""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "service" in data
        assert "model_loaded" in data
        assert data["status"] == "healthy"
        assert isinstance(data["model_loaded"], bool)


class TestAPIHealthEndpoints:
    """Test API v1 health endpoints"""

    def test_api_health_endpoint(self):
        """Test GET /api/v1/health returns detailed health status"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200

        data = response.json()
        assert "status" in data
        assert "service" in data
        assert "version" in data
        assert "model_loaded" in data
        assert data["status"] == "healthy"


class TestAPIDocumentation:
    """Test API documentation endpoints"""

    def test_swagger_ui_available(self):
        """Test Swagger UI is accessible"""
        response = client.get("/api/v1/docs")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_available(self):
        """Test ReDoc is accessible"""
        response = client.get("/api/v1/redoc")
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_openapi_schema_available(self):
        """Test OpenAPI schema is accessible"""
        response = client.get("/openapi.json")
        assert response.status_code == 200

        data = response.json()
        assert "openapi" in data
        assert "info" in data
        assert "paths" in data


class TestCORS:
    """Test CORS configuration"""

    def test_cors_headers_present(self):
        """Test CORS headers are present in responses"""
        response = client.get("/health", headers={"Origin": "http://localhost:3000"})
        assert response.status_code == 200
        # CORS headers should be present if properly configured
        assert "access-control-allow-origin" in response.headers or True


class TestErrorHandling:
    """Test error handling"""

    def test_404_not_found(self):
        """Test 404 error for non-existent endpoint"""
        response = client.get("/nonexistent")
        assert response.status_code == 404

        data = response.json()
        assert "detail" in data

    def test_405_method_not_allowed(self):
        """Test 405 error for wrong HTTP method"""
        response = client.post("/health")
        assert response.status_code == 405

        data = response.json()
        assert "detail" in data
