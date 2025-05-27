"""
Shared test configuration and fixtures for the UAC FastAPI project.
"""

import pytest
import requests
import time
from typing import Dict, Any


@pytest.fixture(scope="session")
def base_url() -> str:
    """Base URL for the FastAPI server."""
    return "http://localhost:8000"


@pytest.fixture(scope="session")
def api_client(base_url: str):
    """Simple API client for making requests."""
    class APIClient:
        def __init__(self, base_url: str):
            self.base_url = base_url
            
        def get(self, endpoint: str, headers: Dict[str, str] = None):
            return requests.get(f"{self.base_url}{endpoint}", headers=headers)
            
        def post(self, endpoint: str, json: Dict[str, Any] = None, data: Dict[str, Any] = None, headers: Dict[str, str] = None):
            return requests.post(f"{self.base_url}{endpoint}", json=json, data=data, headers=headers)
            
        def put(self, endpoint: str, json: Dict[str, Any] = None, headers: Dict[str, str] = None):
            return requests.put(f"{self.base_url}{endpoint}", json=json, headers=headers)
            
        def delete(self, endpoint: str, headers: Dict[str, str] = None):
            return requests.delete(f"{self.base_url}{endpoint}", headers=headers)
    
    return APIClient(base_url)


@pytest.fixture
def unique_timestamp() -> int:
    """Generate a unique timestamp for test data."""
    return int(time.time())


@pytest.fixture
def test_user_data(unique_timestamp: int) -> Dict[str, str]:
    """Generate test user data with unique identifiers."""
    return {
        "username": f"testuser_{unique_timestamp}",
        "email": f"test_{unique_timestamp}@example.com",
        "password": "testpass123",
        "first_name": "Test",
        "last_name": "User"
    }


@pytest.fixture
def registered_user(api_client, test_user_data: Dict[str, str]) -> Dict[str, Any]:
    """Register a test user and return the response data."""
    response = api_client.post("/api/v1/auth/register", json=test_user_data)
    assert response.status_code == 201
    user_data = response.json()
    user_data["password"] = test_user_data["password"]  # Add password for login
    return user_data


@pytest.fixture
def authenticated_user(api_client, registered_user: Dict[str, Any]) -> Dict[str, Any]:
    """Register and login a test user, return user data with token."""
    login_data = {
        "username": registered_user["username"],
        "password": registered_user["password"]
    }
    
    response = api_client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200
    
    login_response = response.json()
    registered_user["access_token"] = login_response["access_token"]
    registered_user["token_type"] = login_response["token_type"]
    
    return registered_user


@pytest.fixture
def auth_headers(authenticated_user: Dict[str, Any]) -> Dict[str, str]:
    """Generate authorization headers for authenticated requests."""
    return {
        "Authorization": f"Bearer {authenticated_user['access_token']}"
    }


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )
    config.addinivalue_line(
        "markers", "auth: mark test as authentication related"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    ) 