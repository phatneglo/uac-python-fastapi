"""
Integration tests for authentication endpoints.

These tests run against a live FastAPI server and test the complete authentication flow.
Make sure the server is running on http://localhost:8000 before running these tests.
"""

import requests
import time
import pytest


class TestAuthIntegration:
    """Integration tests for authentication endpoints."""
    
    base_url = "http://localhost:8000"
    
    def test_health_endpoint(self):
        """Test health endpoint is accessible."""
        response = requests.get(f"{self.base_url}/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_user_registration_success(self):
        """Test successful user registration."""
        timestamp = int(time.time())
        user_data = {
            "username": f"testuser_{timestamp}",
            "email": f"test_{timestamp}@example.com",
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }
        
        response = requests.post(f"{self.base_url}/api/v1/auth/register", json=user_data)
        assert response.status_code == 201
        
        user_response = response.json()
        assert user_response["username"] == user_data["username"]
        assert user_response["email"] == user_data["email"]
        assert user_response["first_name"] == user_data["first_name"]
        assert user_response["last_name"] == user_data["last_name"]
        assert user_response["is_active"] is True
        assert "user_id" in user_response
        assert "date_created" in user_response
        assert "password" not in user_response  # Password should not be returned
    
    def test_user_registration_duplicate_username(self):
        """Test registration with duplicate username fails."""
        timestamp = int(time.time())
        user_data = {
            "username": f"duplicate_user_{timestamp}",
            "email": f"duplicate_{timestamp}@example.com",
            "password": "testpass123"
        }
        
        # First registration
        response1 = requests.post(f"{self.base_url}/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Second registration with same username but different email
        user_data["email"] = f"different_{timestamp}@example.com"
        response2 = requests.post(f"{self.base_url}/api/v1/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "Username already registered" in response2.json()["detail"]
    
    def test_user_registration_duplicate_email(self):
        """Test registration with duplicate email fails."""
        timestamp = int(time.time())
        user_data = {
            "username": f"user_email_{timestamp}",
            "email": f"duplicate_email_{timestamp}@example.com",
            "password": "testpass123"
        }
        
        # First registration
        response1 = requests.post(f"{self.base_url}/api/v1/auth/register", json=user_data)
        assert response1.status_code == 201
        
        # Second registration with same email but different username
        user_data["username"] = f"different_user_{timestamp}"
        response2 = requests.post(f"{self.base_url}/api/v1/auth/register", json=user_data)
        assert response2.status_code == 400
        assert "Email already registered" in response2.json()["detail"]
    
    def test_user_registration_invalid_data(self):
        """Test registration with invalid data fails with proper validation."""
        timestamp = int(time.time())
        
        # Test short password
        user_data = {
            "username": f"shortpass_{timestamp}",
            "email": f"shortpass_{timestamp}@example.com",
            "password": "short"
        }
        response = requests.post(f"{self.base_url}/api/v1/auth/register", json=user_data)
        assert response.status_code == 422
        
        # Test invalid email format
        user_data = {
            "username": f"invalidemail_{timestamp}",
            "email": "invalid-email-format",
            "password": "testpass123"
        }
        response = requests.post(f"{self.base_url}/api/v1/auth/register", json=user_data)
        assert response.status_code == 422
    
    def test_user_login_with_username(self):
        """Test successful login with username."""
        # First register a user
        timestamp = int(time.time())
        user_data = {
            "username": f"loginuser_{timestamp}",
            "email": f"login_{timestamp}@example.com",
            "password": "loginpass123",
            "first_name": "Login",
            "last_name": "User"
        }
        
        register_response = requests.post(f"{self.base_url}/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # Now login with username
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
        response = requests.post(f"{self.base_url}/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        login_response = response.json()
        assert "access_token" in login_response
        assert login_response["token_type"] == "bearer"
        assert "expires_in" in login_response
        assert login_response["expires_in"] == 1800  # 30 minutes in seconds
    
    def test_user_login_with_email(self):
        """Test successful login using email instead of username."""
        # First register a user
        timestamp = int(time.time())
        user_data = {
            "username": f"emaillogin_{timestamp}",
            "email": f"emaillogin_{timestamp}@example.com",
            "password": "emailpass123"
        }
        
        register_response = requests.post(f"{self.base_url}/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # Login with email instead of username
        login_data = {
            "username": user_data["email"],  # Using email as username field
            "password": user_data["password"]
        }
        
        response = requests.post(f"{self.base_url}/api/v1/auth/login", json=login_data)
        assert response.status_code == 200
        
        login_response = response.json()
        assert "access_token" in login_response
        assert login_response["token_type"] == "bearer"
    
    def test_user_login_invalid_credentials(self):
        """Test login with non-existent user fails."""
        login_data = {
            "username": "nonexistent_user",
            "password": "wrongpassword"
        }
        
        response = requests.post(f"{self.base_url}/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_user_login_wrong_password(self):
        """Test login with correct username but wrong password fails."""
        # First register a user
        timestamp = int(time.time())
        user_data = {
            "username": f"wrongpass_{timestamp}",
            "email": f"wrongpass_{timestamp}@example.com",
            "password": "correctpass123"
        }
        
        register_response = requests.post(f"{self.base_url}/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # Try to login with wrong password
        login_data = {
            "username": user_data["username"],
            "password": "wrongpass123"
        }
        
        response = requests.post(f"{self.base_url}/api/v1/auth/login", json=login_data)
        assert response.status_code == 401
        assert "Incorrect username or password" in response.json()["detail"]
    
    def test_oauth2_form_login(self):
        """Test OAuth2 form login endpoint (used by API docs)."""
        # First register a user
        timestamp = int(time.time())
        user_data = {
            "username": f"oauth2_{timestamp}",
            "email": f"oauth2_{timestamp}@example.com",
            "password": "oauth2pass123"
        }
        
        register_response = requests.post(f"{self.base_url}/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # Login using form data (OAuth2 style)
        form_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        
        response = requests.post(f"{self.base_url}/api/v1/auth/login/form", data=form_data)
        assert response.status_code == 200
        
        login_response = response.json()
        assert "access_token" in login_response
        assert login_response["token_type"] == "bearer"
    
    def test_protected_endpoint_with_valid_token(self):
        """Test accessing protected endpoint with valid JWT token."""
        # Register and login to get a token
        timestamp = int(time.time())
        user_data = {
            "username": f"protected_{timestamp}",
            "email": f"protected_{timestamp}@example.com",
            "password": "protectedpass123",
            "first_name": "Protected",
            "last_name": "User"
        }
        
        # Register
        register_response = requests.post(f"{self.base_url}/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        
        # Login
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        login_response = requests.post(f"{self.base_url}/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        
        # Access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get(f"{self.base_url}/api/v1/auth/me", headers=headers)
        
        assert response.status_code == 200
        me_response = response.json()
        assert me_response["username"] == user_data["username"]
        assert me_response["email"] == user_data["email"]
        assert me_response["first_name"] == user_data["first_name"]
        assert me_response["last_name"] == user_data["last_name"]
        assert me_response["is_active"] is True
        assert "password" not in me_response
    
    def test_protected_endpoint_without_token(self):
        """Test accessing protected endpoint without token fails."""
        response = requests.get(f"{self.base_url}/api/v1/auth/me")
        assert response.status_code == 403  # Forbidden - no Authorization header
    
    def test_protected_endpoint_with_invalid_token(self):
        """Test accessing protected endpoint with invalid token fails."""
        headers = {"Authorization": "Bearer invalid_jwt_token"}
        response = requests.get(f"{self.base_url}/api/v1/auth/me", headers=headers)
        assert response.status_code == 401  # Unauthorized - invalid token
    
    def test_complete_authentication_flow(self):
        """Test the complete authentication flow from registration to protected access."""
        timestamp = int(time.time())
        user_data = {
            "username": f"complete_flow_{timestamp}",
            "email": f"complete_{timestamp}@example.com",
            "password": "completeflow123",
            "first_name": "Complete",
            "last_name": "Flow"
        }
        
        # Step 1: Register
        register_response = requests.post(f"{self.base_url}/api/v1/auth/register", json=user_data)
        assert register_response.status_code == 201
        user_id = register_response.json()["user_id"]
        
        # Step 2: Login with username
        login_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        login_response = requests.post(f"{self.base_url}/api/v1/auth/login", json=login_data)
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # Step 3: Access protected endpoint
        headers = {"Authorization": f"Bearer {token}"}
        me_response = requests.get(f"{self.base_url}/api/v1/auth/me", headers=headers)
        assert me_response.status_code == 200
        assert me_response.json()["user_id"] == user_id
        
        # Step 4: Login with email
        login_data["username"] = user_data["email"]
        email_login_response = requests.post(f"{self.base_url}/api/v1/auth/login", json=login_data)
        assert email_login_response.status_code == 200
        
        # Step 5: OAuth2 form login
        form_data = {
            "username": user_data["username"],
            "password": user_data["password"]
        }
        oauth_response = requests.post(f"{self.base_url}/api/v1/auth/login/form", data=form_data)
        assert oauth_response.status_code == 200


if __name__ == "__main__":
    # Run tests directly for quick testing
    test = TestAuthIntegration()
    
    print("🧪 Running Authentication Integration Tests...")
    
    test.test_health_endpoint()
    print("✅ Health endpoint test passed")
    
    test.test_user_registration_success()
    print("✅ User registration test passed")
    
    test.test_user_registration_duplicate_username()
    print("✅ Duplicate username test passed")
    
    test.test_user_registration_duplicate_email()
    print("✅ Duplicate email test passed")
    
    test.test_user_registration_invalid_data()
    print("✅ Invalid registration data test passed")
    
    test.test_user_login_with_username()
    print("✅ Login with username test passed")
    
    test.test_user_login_with_email()
    print("✅ Login with email test passed")
    
    test.test_user_login_invalid_credentials()
    print("✅ Invalid credentials test passed")
    
    test.test_user_login_wrong_password()
    print("✅ Wrong password test passed")
    
    test.test_oauth2_form_login()
    print("✅ OAuth2 form login test passed")
    
    test.test_protected_endpoint_with_valid_token()
    print("✅ Protected endpoint with valid token test passed")
    
    test.test_protected_endpoint_without_token()
    print("✅ Protected endpoint without token test passed")
    
    test.test_protected_endpoint_with_invalid_token()
    print("✅ Protected endpoint with invalid token test passed")
    
    test.test_complete_authentication_flow()
    print("✅ Complete authentication flow test passed")
    
    print("\n🎉 All authentication integration tests passed!") 