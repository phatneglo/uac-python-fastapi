"""
Admin endpoints with role-based access control.
"""

from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.dependencies import get_db
from app.models.user import User
from app.models.user_level import UserLevel
from app.schemas.user import UserResponse
from app.utils.permissions import (
    require_admin, 
    require_manager_or_admin, 
    require_any_role,
    get_user_roles,
    has_role,
    UserRole
)

router = APIRouter()


@router.get("/admin-only", dependencies=[Depends(require_admin)])
async def admin_only_endpoint():
    """Endpoint accessible only by administrators."""
    return {
        "message": "This is an admin-only endpoint",
        "access_level": "admin",
        "description": "Only users with admin role (1) can access this"
    }


@router.get("/manager-admin", dependencies=[Depends(require_manager_or_admin)])
async def manager_admin_endpoint():
    """Endpoint accessible by managers and administrators."""
    return {
        "message": "This endpoint is for managers and admins",
        "access_level": "manager_or_admin",
        "description": "Users with manager (2) or admin (1) roles can access this"
    }


@router.get("/all-users", dependencies=[Depends(require_any_role)])
async def all_users_endpoint():
    """Endpoint accessible by all authenticated users with roles."""
    return {
        "message": "This endpoint is for all authenticated users",
        "access_level": "any_authenticated_user",
        "description": "Users with any role (1, 2, or 3) can access this"
    }


@router.get("/my-roles")
async def get_my_roles(current_user: User = Depends(require_any_role)):
    """Get current user's roles and permissions."""
    user_roles = get_user_roles(current_user)
    
    role_names = []
    for role in user_roles:
        if role == UserRole.ADMIN.value:
            role_names.append("admin")
        elif role == UserRole.MANAGER.value:
            role_names.append("manager")
        elif role == UserRole.GENERAL_USER.value:
            role_names.append("general user")
    
    return {
        "user_id": current_user.user_id,
        "username": current_user.username,
        "user_level_id": current_user.user_level_id,
        "roles": user_roles,
        "role_names": role_names,
        "permissions": {
            "is_admin": has_role(current_user, UserRole.ADMIN),
            "is_manager": has_role(current_user, UserRole.MANAGER),
            "is_general_user": has_role(current_user, UserRole.GENERAL_USER)
        }
    }


@router.get("/users", response_model=List[UserResponse])
async def list_all_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_manager_or_admin)
):
    """List all users - accessible by managers and admins."""
    result = await db.execute(select(User))
    users = result.scalars().all()
    return users


@router.get("/user-levels")
async def get_user_levels(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_any_role)
):
    """Get all available user levels."""
    result = await db.execute(select(UserLevel))
    levels = result.scalars().all()
    
    return {
        "user_levels": [
            {
                "id": level.user_level_id,
                "name": level.name,
                "description": level.description
            }
            for level in levels
        ]
    }


@router.post("/assign-role/{user_id}")
async def assign_user_role(
    user_id: int,
    role_ids: str,  # CSV format like "1,2" or "3"
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """Assign roles to a user - admin only."""
    # Get the target user
    result = await db.execute(select(User).where(User.user_id == user_id))
    target_user = result.scalar_one_or_none()
    
    if not target_user:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Validate role IDs
    valid_roles = ["1", "2", "3"]
    roles = [role.strip() for role in role_ids.split(',')]
    
    for role in roles:
        if role not in valid_roles:
            from fastapi import HTTPException
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid role ID: {role}. Valid roles are: {', '.join(valid_roles)}"
            )
    
    # Update user's roles
    target_user.user_level_id = role_ids
    await db.commit()
    await db.refresh(target_user)
    
    return {
        "message": f"Roles assigned successfully to user {target_user.username}",
        "user_id": user_id,
        "username": target_user.username,
        "new_roles": role_ids,
        "assigned_by": current_user.username
    } 