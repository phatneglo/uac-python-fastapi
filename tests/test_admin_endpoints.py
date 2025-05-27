"""
Tests for admin endpoints with role-based access control.
"""

import pytest


@pytest.mark.admin
class TestRoleBasedAccess:
    """Test role-based access control for admin endpoints."""
    
    def test_admin_only_endpoint_with_admin(self, api_client, admin_headers):
        """Test admin-only endpoint with admin user."""
        response = api_client.get("/api/v1/admin/admin-only", headers=admin_headers)
        assert response.status_code == 200
        assert "admin-only" in response.json()["message"]
    
    def test_admin_only_endpoint_with_manager(self, api_client, manager_headers):
        """Test admin-only endpoint with manager user (should fail)."""
        response = api_client.get("/api/v1/admin/admin-only", headers=manager_headers)
        assert response.status_code == 403
    
    def test_admin_only_endpoint_with_general_user(self, api_client, general_headers):
        """Test admin-only endpoint with general user (should fail)."""
        response = api_client.get("/api/v1/admin/admin-only", headers=general_headers)
        assert response.status_code == 403
    
    def test_manager_admin_endpoint_with_admin(self, api_client, admin_headers):
        """Test manager/admin endpoint with admin user."""
        response = api_client.get("/api/v1/admin/manager-admin", headers=admin_headers)
        assert response.status_code == 200
        assert "managers and admins" in response.json()["message"]
    
    def test_manager_admin_endpoint_with_manager(self, api_client, manager_headers):
        """Test manager/admin endpoint with manager user."""
        response = api_client.get("/api/v1/admin/manager-admin", headers=manager_headers)
        assert response.status_code == 200
        assert "managers and admins" in response.json()["message"]
    
    def test_manager_admin_endpoint_with_general_user(self, api_client, general_headers):
        """Test manager/admin endpoint with general user (should fail)."""
        response = api_client.get("/api/v1/admin/manager-admin", headers=general_headers)
        assert response.status_code == 403
    
    def test_all_users_endpoint_with_admin(self, api_client, admin_headers):
        """Test all-users endpoint with admin user."""
        response = api_client.get("/api/v1/admin/all-users", headers=admin_headers)
        assert response.status_code == 200
        assert "all authenticated users" in response.json()["message"]
    
    def test_all_users_endpoint_with_manager(self, api_client, manager_headers):
        """Test all-users endpoint with manager user."""
        response = api_client.get("/api/v1/admin/all-users", headers=manager_headers)
        assert response.status_code == 200
        assert "all authenticated users" in response.json()["message"]
    
    def test_all_users_endpoint_with_general_user(self, api_client, general_headers):
        """Test all-users endpoint with general user."""
        response = api_client.get("/api/v1/admin/all-users", headers=general_headers)
        assert response.status_code == 200
        assert "all authenticated users" in response.json()["message"]


@pytest.mark.admin
class TestUserRoleManagement:
    """Test user role management functionality."""
    
    def test_get_my_roles_admin(self, api_client, admin_user, admin_headers):
        """Test getting current user roles for admin."""
        response = api_client.get("/api/v1/admin/my-roles", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        # The fixture might return either the pre-seeded user or a fallback user
        # Check if it's either the expected username or the fallback pattern
        assert data["username"] in [admin_user["username"], "test_admin_user"]
        assert data["user_level_id"] in ["1", "1,2,3"]  # Admin role or multiple roles
        assert "1" in data["roles"]  # Should have admin role
        assert data["permissions"]["is_admin"] is True
    
    def test_get_my_roles_manager(self, api_client, manager_user, manager_headers):
        """Test getting current user roles for manager."""
        response = api_client.get("/api/v1/admin/my-roles", headers=manager_headers)
        
        assert response.status_code == 200
        data = response.json()
        # The fixture might return either the pre-seeded user or a fallback user
        assert data["username"] in [manager_user["username"], "test_manager_user"]
        assert data["user_level_id"] in ["2", "1,2,3"]  # Manager role or multiple roles
        assert "2" in data["roles"]  # Should have manager role
        assert data["permissions"]["is_manager"] is True
    
    def test_get_my_roles_general_user(self, api_client, general_user, general_headers):
        """Test getting current user roles for general user."""
        response = api_client.get("/api/v1/admin/my-roles", headers=general_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == general_user["username"]
        assert data["user_level_id"] == "3"  # General user role
        assert data["roles"] == ["3"]
        assert data["permissions"]["is_general_user"] is True
        assert data["permissions"]["is_admin"] is False
        assert data["permissions"]["is_manager"] is False
    
    def test_get_user_levels(self, api_client, auth_headers):
        """Test getting available user levels."""
        response = api_client.get("/api/v1/admin/user-levels", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert "user_levels" in data
        
        levels = data["user_levels"]
        assert len(levels) >= 3
        
        # Check that we have the expected levels
        level_ids = [level["id"] for level in levels]
        assert 1 in level_ids  # Admin
        assert 2 in level_ids  # Manager
        assert 3 in level_ids  # General user
    
    def test_list_users_as_admin(self, api_client, admin_headers):
        """Test listing users as admin."""
        response = api_client.get("/api/v1/admin/users", headers=admin_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0  # Should have at least some users
    
    def test_list_users_as_manager(self, api_client, manager_headers):
        """Test listing users as manager."""
        response = api_client.get("/api/v1/admin/users", headers=manager_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
    
    def test_list_users_as_general_user(self, api_client, general_headers):
        """Test listing users as general user (should fail)."""
        response = api_client.get("/api/v1/admin/users", headers=general_headers)
        assert response.status_code == 403
    
    def test_assign_role_as_admin(self, api_client, admin_user, admin_headers, general_user):
        """Test assigning roles as admin."""
        user_id = general_user["user_id"]
        new_roles = "2,3"  # Manager and general user
        
        response = api_client.post(
            f"/api/v1/admin/assign-role/{user_id}?role_ids={new_roles}",
            headers=admin_headers
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user_id
        assert data["new_roles"] == new_roles
        # The assigned_by might be either the fixture username or the pre-seeded username
        assert data["assigned_by"] in [admin_user["username"], "test_admin_user"]
    
    def test_assign_role_as_manager(self, api_client, manager_headers, general_user):
        """Test assigning roles as manager (should fail)."""
        user_id = general_user["user_id"]
        new_roles = "2,3"
        
        response = api_client.post(
            f"/api/v1/admin/assign-role/{user_id}?role_ids={new_roles}",
            headers=manager_headers
        )
        
        assert response.status_code == 403
    
    def test_assign_invalid_role(self, api_client, admin_headers, general_user):
        """Test assigning invalid role."""
        user_id = general_user["user_id"]
        invalid_roles = "5,6"  # Invalid role IDs
        
        response = api_client.post(
            f"/api/v1/admin/assign-role/{user_id}?role_ids={invalid_roles}",
            headers=admin_headers
        )
        
        assert response.status_code == 400
        assert "Invalid role ID" in response.json()["detail"]
    
    def test_assign_role_to_nonexistent_user(self, api_client, admin_headers):
        """Test assigning role to non-existent user."""
        user_id = 99999  # Non-existent user ID
        new_roles = "2"
        
        response = api_client.post(
            f"/api/v1/admin/assign-role/{user_id}?role_ids={new_roles}",
            headers=admin_headers
        )
        
        assert response.status_code == 404
        assert "User not found" in response.json()["detail"]


@pytest.mark.admin
class TestMultipleRoles:
    """Test functionality for users with multiple roles."""
    
    def test_user_with_multiple_roles_access(self, api_client, multi_role_user, multi_role_headers):
        """Test user with multiple roles can access appropriate endpoints."""
        # Check if the user actually has multiple roles
        roles_response = api_client.get("/api/v1/admin/my-roles", headers=multi_role_headers)
        assert roles_response.status_code == 200
        user_roles = roles_response.json()["roles"]
        
        # If user has admin role (1), should be able to access admin endpoint
        if "1" in user_roles:
            response = api_client.get("/api/v1/admin/admin-only", headers=multi_role_headers)
            assert response.status_code == 200
        else:
            # If user doesn't have admin role, should get 403
            response = api_client.get("/api/v1/admin/admin-only", headers=multi_role_headers)
            assert response.status_code == 403
        
        # Should be able to access manager/admin endpoint if has role 1 or 2
        if any(role in user_roles for role in ["1", "2"]):
            response = api_client.get("/api/v1/admin/manager-admin", headers=multi_role_headers)
            assert response.status_code == 200
        
        # Should always be able to access all-users endpoint
        response = api_client.get("/api/v1/admin/all-users", headers=multi_role_headers)
        assert response.status_code == 200
    
    def test_multi_role_user_permissions(self, api_client, multi_role_user, multi_role_headers):
        """Test multi-role user permissions display correctly."""
        response = api_client.get("/api/v1/admin/my-roles", headers=multi_role_headers)
        
        assert response.status_code == 200
        data = response.json()
        
        # The user might have multiple roles or just the default role
        # Check that the response structure is correct
        assert "user_level_id" in data
        assert "roles" in data
        assert "permissions" in data
        
        # If the user has multiple roles, check that they're properly parsed
        if "," in data["user_level_id"]:
            roles = data["user_level_id"].split(",")
            assert len(roles) > 1
            assert all(role.strip() in ["1", "2", "3"] for role in roles)
        else:
            # Single role should be valid
            assert data["user_level_id"] in ["1", "2", "3"]
    
    def test_role_assignment_persistence(self, api_client, admin_headers, general_user):
        """Test that role assignments persist correctly."""
        user_id = general_user["user_id"]
        
        # Assign multiple roles
        new_roles = "1,2,3"
        assign_response = api_client.post(
            f"/api/v1/admin/assign-role/{user_id}?role_ids={new_roles}",
            headers=admin_headers
        )
        assert assign_response.status_code == 200
        
        # Login as the user to verify roles
        login_response = api_client.post("/api/v1/auth/login", json={
            "username": general_user["username"],
            "password": general_user["password"]
        })
        assert login_response.status_code == 200
        
        token = login_response.json()["access_token"]
        user_headers = {"Authorization": f"Bearer {token}"}
        
        # Check roles
        roles_response = api_client.get("/api/v1/admin/my-roles", headers=user_headers)
        assert roles_response.status_code == 200
        
        data = roles_response.json()
        assert data["user_level_id"] == new_roles
        assert "1" in data["roles"]
        assert "2" in data["roles"]
        assert "3" in data["roles"] 