"""
Role-based access control utilities.
"""

from enum import Enum
from typing import List, Union
from fastapi import HTTPException, status, Depends
from app.models.user import User
from app.dependencies import get_current_user


class UserRole(Enum):
    """User role enumeration."""
    ADMIN = "1"
    MANAGER = "2"
    GENERAL_USER = "3"


class RoleChecker:
    """Role-based access control checker."""
    
    def __init__(self, allowed_roles: List[Union[UserRole, str]]):
        self.allowed_roles = [
            role.value if isinstance(role, UserRole) else str(role) 
            for role in allowed_roles
        ]
    
    def __call__(self, current_user: User = Depends(get_current_user)):
        """Check if current user has required role."""
        if not current_user.user_level_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="User has no assigned role"
            )
        
        # Handle CSV format (e.g., "1,2,3")
        user_roles = [role.strip() for role in current_user.user_level_id.split(',')]
        
        # Check if user has any of the allowed roles
        if not any(role in self.allowed_roles for role in user_roles):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient permissions"
            )
        
        return current_user


# Predefined role checkers
require_admin = RoleChecker([UserRole.ADMIN])
require_manager_or_admin = RoleChecker([UserRole.ADMIN, UserRole.MANAGER])
require_any_role = RoleChecker([UserRole.ADMIN, UserRole.MANAGER, UserRole.GENERAL_USER])


def get_user_roles(user: User) -> List[str]:
    """Get list of user roles from CSV string."""
    if not user.user_level_id:
        return []
    return [role.strip() for role in user.user_level_id.split(',')]


def has_role(user: User, role: Union[UserRole, str]) -> bool:
    """Check if user has specific role."""
    role_value = role.value if isinstance(role, UserRole) else str(role)
    user_roles = get_user_roles(user)
    return role_value in user_roles


def has_any_role(user: User, roles: List[Union[UserRole, str]]) -> bool:
    """Check if user has any of the specified roles."""
    role_values = [role.value if isinstance(role, UserRole) else str(role) for role in roles]
    user_roles = get_user_roles(user)
    return any(role in role_values for role in user_roles) 