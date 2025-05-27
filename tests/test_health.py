"""
Tests for health check endpoints.
"""

import pytest


@pytest.mark.integration
class TestHealthEndpoints:
    """Test health check endpoints."""
    
    def test_health_endpoint_returns_healthy_status(self, api_client):
        """Test that health endpoint returns healthy status."""
        response = api_client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "UAC FastAPI"
    
    def test_health_endpoint_response_format(self, api_client):
        """Test that health endpoint returns proper JSON format."""
        response = api_client.get("/health")
        
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/json"
        
        data = response.json()
        assert isinstance(data, dict)
        assert "status" in data
        assert "service" in data 