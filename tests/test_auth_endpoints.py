"""
Tests for authentication endpoints using pytest fixtures.
"""

import pytest


@pytest.mark.integration
@pytest.mark.auth
class TestAuthRegistration:
    """Test user registration endpoints."""
    
    def test_user_registration_success(self, api_client, test_user_data):
        """Test successful user registration."""
        response = api_client.post("/api/v1/auth/register", json=test_user_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["username"] == test_user_data["username"]
        assert data["email"] == test_user_data["email"]
        assert data["first_name"] == test_user_data["first_name"]
        assert data["last_name"] == test_user_data["last_name"]
        assert data["is_active"] is True
        assert "user_id" in data
        assert "date_created" in data
        assert "password" not in data  # Password should not be returned
    
    def test_user_registration_duplicate_username(self, api_client, registered_user, unique_timestamp):
        """Test registration with duplicate username fails."""
        duplicate_data = {
            "username": registered_user["username"],  # Same username
            "email": f"different_{unique_timestamp}@example.com",  # Different email
            "password": "testpass123"
        }
        
        response = api_client.post("/api/v1/auth/register", json=duplicate_data)
        assert response.status_code == 400
        assert "Username already registered" in response.json()["detail"]
    
    def test_user_registration_duplicate_email(self, api_client, registered_user, unique_timestamp):
        """Test registration with duplicate email fails."""
        duplicate_data = {
            "username": f"different_user_{unique_timestamp}",  # Different username
            "email": registered_user["email"],  # Same email
            "password": "testpass123"
        }
        
        response = api_client.post("/api/v1/auth/register", json=duplicate_data)
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]
    
    def test_user_registration_invalid_password(self, api_client, unique_timestamp):
        """Test registration with invalid password fails."""
        user_data = {
            "username": f"shortpass_{unique_timestamp}",
            "email": f"shortpass_{unique_timestamp}@example.com",
            "password": "short"  # Too short
        }
        
        response = api_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_user_registration_invalid_email(self, api_client, unique_timestamp):
        """Test registration with invalid email format fails."""
        user_data = {
            "username": f"invalidemail_{unique_timestamp}",
            "email": "invalid-email-format",  # Invalid format
            "password": "testpass123"
        }
        
        response = api_client.post("/api/v1/auth/register", json=user_data)
        assert response.status_code == 422


@pytest.mark.integration
@pytest.mark.auth
class TestAuthLogin:
    """Test user login endpoints."""
    
    def test_login_with_username_success(self, api_client, registered_user):
        """Test successful login with username."""
        login_data = {
            "username": registered_user["username"],
            "password": registered_user["password"]
        }
        
        response = api_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert data["expires_in"] == 1800  # 30 minutes
    
    def test_login_with_email_success(self, api_client, registered_user):
        """Test successful login with email."""
        login_data = {
            "username": registered_user["email"],  # Using email as username
            "password": registered_user["password"]
        }
        
        response = api_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_credentials(self, api_client):
        """Test login with non-existent user fails."""
        login_data = {
            "username": "nonexistent_user",
            "password": "wrongpassword"
        }
        
        response = api_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_login_wrong_password(self, api_client, registered_user):
        """Test login with correct username but wrong password fails."""
        login_data = {
            "username": registered_user["username"],
            "password": "wrongpassword"
        }
        
        response = api_client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_oauth2_form_login_success(self, api_client, registered_user):
        """Test OAuth2 form login endpoint."""
        form_data = {
            "username": registered_user["username"],
            "password": registered_user["password"]
        }
        
        response = api_client.post("/api/v1/auth/login/form", data=form_data)
        assert response.status_code == 200
        
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"


@pytest.mark.integration
@pytest.mark.auth
class TestProtectedEndpoints:
    """Test protected endpoints that require authentication."""
    
    def test_get_current_user_success(self, api_client, authenticated_user, auth_headers):
        """Test accessing current user info with valid token."""
        response = api_client.get("/api/v1/auth/me", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == authenticated_user["username"]
        assert data["email"] == authenticated_user["email"]
        assert data["first_name"] == authenticated_user["first_name"]
        assert data["last_name"] == authenticated_user["last_name"]
        assert data["is_active"] is True
        assert "password" not in data
    
    def test_get_current_user_without_token(self, api_client):
        """Test accessing protected endpoint without token fails."""
        response = api_client.get("/api/v1/auth/me")
        assert response.status_code == 403  # Forbidden
    
    def test_get_current_user_invalid_token(self, api_client):
        """Test accessing protected endpoint with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_jwt_token"}
        response = api_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 401  # Unauthorized
    
    def test_get_current_user_malformed_header(self, api_client):
        """Test accessing protected endpoint with malformed auth header fails."""
        headers = {"Authorization": "InvalidFormat token"}
        response = api_client.get("/api/v1/auth/me", headers=headers)
        assert response.status_code == 403  # Forbidden


@pytest.mark.integration
@pytest.mark.auth
@pytest.mark.slow
class TestCompleteAuthFlow:
    """Test complete authentication flows."""
    
    def test_complete_registration_to_protected_access_flow(self, api_client, test_user_data):
        """Test the complete flow from registration to accessing protected endpoints."""
        # Step 1: Register
        register_response = api_client.post("/api/v1/auth/register", json=test_user_data)
        assert register_response.status_code == 201
        user_data = register_response.json()
        
        # Step 2: Login with username
        login_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        login_response = api_client.post("/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Step 3: Access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        me_response = api_client.get("/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["user_id"] == user_data["user_id"]
        
        # Step 4: Login with email
        login_data["username"] = test_user_data["email"]
        email_login_response = api_client.post("/api/v1/auth/login", json=login_data)
        assert email_login_response.status_code == 200
        
        # Step 5: OAuth2 form login
        form_data = {
            "username": test_user_data["username"],
            "password": test_user_data["password"]
        }
        oauth_response = api_client.post("/api/v1/auth/login/form", data=form_data)
        assert oauth_response.status_code == 200 