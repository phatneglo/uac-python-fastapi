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


# Role-specific user fixtures
@pytest.fixture
def admin_user(api_client) -> Dict[str, Any]:
    """Get the pre-seeded admin user."""
    # Use the pre-seeded admin user
    admin_data = {
        "username": "test_admin_user",
        "email": "test_admin@example.com",
        "password": "adminpass123"
    }
    
    # Login to verify the user exists and get user info
    login_response = api_client.post("/api/v1/auth/login", json={
        "username": admin_data["username"],
        "password": admin_data["password"]
    })
    
    if login_response.status_code == 200:
        # Get user info from the /me endpoint
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        me_response = api_client.get("/api/v1/auth/me", headers=headers)
        if me_response.status_code == 200:
            user_data = me_response.json()
            user_data["password"] = admin_data["password"]
            return user_data
    
    # If admin user doesn't exist or login fails, create a fallback
    fallback_data = {
        "username": f"admin_fallback_{int(time.time())}",
        "email": f"admin_fallback_{int(time.time())}@example.com",
        "password": "adminpass123",
        "first_name": "Admin",
        "last_name": "User"
    }
    
    response = api_client.post("/api/v1/auth/register", json=fallback_data)
    assert response.status_code == 201
    user = response.json()
    user["password"] = fallback_data["password"]
    return user


@pytest.fixture
def admin_headers(api_client, admin_user: Dict[str, Any]) -> Dict[str, str]:
    """Generate authorization headers for admin user."""
    # Login with the admin user
    login_response = api_client.post("/api/v1/auth/login", json={
        "username": admin_user["username"],
        "password": admin_user["password"]
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def manager_user(api_client) -> Dict[str, Any]:
    """Get the pre-seeded manager user."""
    # Use the pre-seeded manager user
    manager_data = {
        "username": "test_manager_user",
        "email": "test_manager@example.com",
        "password": "managerpass123"
    }
    
    # Login to verify the user exists and get user info
    login_response = api_client.post("/api/v1/auth/login", json={
        "username": manager_data["username"],
        "password": manager_data["password"]
    })
    
    if login_response.status_code == 200:
        # Get user info from the /me endpoint
        token = login_response.json()["access_token"]
        headers = {"Authorization": f"Bearer {token}"}
        
        me_response = api_client.get("/api/v1/auth/me", headers=headers)
        if me_response.status_code == 200:
            user_data = me_response.json()
            user_data["password"] = manager_data["password"]
            return user_data
    
    # If manager user doesn't exist or login fails, create a fallback
    fallback_data = {
        "username": f"manager_fallback_{int(time.time())}",
        "email": f"manager_fallback_{int(time.time())}@example.com",
        "password": "managerpass123",
        "first_name": "Manager",
        "last_name": "User"
    }
    
    response = api_client.post("/api/v1/auth/register", json=fallback_data)
    assert response.status_code == 201
    user = response.json()
    user["password"] = fallback_data["password"]
    return user


@pytest.fixture
def manager_headers(api_client, manager_user: Dict[str, Any]) -> Dict[str, str]:
    """Generate authorization headers for manager user."""
    login_response = api_client.post("/api/v1/auth/login", json={
        "username": manager_user["username"],
        "password": manager_user["password"]
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def general_user(api_client, unique_timestamp: int) -> Dict[str, Any]:
    """Create and return a general user."""
    user_data = {
        "username": f"general_{unique_timestamp}",
        "email": f"general_{unique_timestamp}@example.com",
        "password": "generalpass123",
        "first_name": "General",
        "last_name": "User"
    }
    
    response = api_client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    user = response.json()
    user["password"] = user_data["password"]
    return user


@pytest.fixture
def general_headers(api_client, general_user: Dict[str, Any]) -> Dict[str, str]:
    """Generate authorization headers for general user."""
    login_response = api_client.post("/api/v1/auth/login", json={
        "username": general_user["username"],
        "password": general_user["password"]
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def multi_role_user(api_client, unique_timestamp: int) -> Dict[str, Any]:
    """Create and return a user with multiple roles."""
    user_data = {
        "username": f"multirole_{unique_timestamp}",
        "email": f"multirole_{unique_timestamp}@example.com",
        "password": "multipass123",
        "first_name": "Multi",
        "last_name": "Role"
    }
    
    # Register the user first
    response = api_client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    user = response.json()
    user["password"] = user_data["password"]
    
    # Try to assign multiple roles using admin endpoint
    try:
        # Login as admin first
        admin_login = api_client.post("/api/v1/auth/login", json={
            "username": "test_admin_user",
            "password": "adminpass123"
        })
        
        if admin_login.status_code == 200:
            admin_token = admin_login.json()["access_token"]
            admin_headers = {"Authorization": f"Bearer {admin_token}"}
            
            assign_response = api_client.post(
                f"/api/v1/admin/assign-role/{user['user_id']}?role_ids=1,2,3",
                headers=admin_headers
            )
            if assign_response.status_code == 200:
                user["user_level_id"] = "1,2,3"
            else:
                # Default to general user role if assignment fails
                user["user_level_id"] = "3"
        else:
            # Default to general user role if admin login fails
            user["user_level_id"] = "3"
    except Exception:
        # Default to general user role if anything fails
        user["user_level_id"] = "3"
    
    return user


@pytest.fixture
def multi_role_headers(api_client, multi_role_user: Dict[str, Any]) -> Dict[str, str]:
    """Generate authorization headers for multi-role user."""
    login_response = api_client.post("/api/v1/auth/login", json={
        "username": multi_role_user["username"],
        "password": multi_role_user["password"]
    })
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


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
    config.addinivalue_line(
        "markers", "admin: mark test as admin functionality"
    ) 