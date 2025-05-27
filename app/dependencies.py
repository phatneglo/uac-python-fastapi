from typing import Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.services.user_service import UserService
from app.utils.security import verify_token

# Security scheme
security = HTTPBearer()

# Type aliases for dependency injection
DatabaseDep = Annotated[AsyncSession, Depends(get_db)]


async def get_current_user(
    db: DatabaseDep,
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> User:
    """Get current authenticated user."""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Verify token
    username = verify_token(credentials.credentials)
    if username is None:
        raise credentials_exception
    
    # Get user from database
    user = await UserService.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    
    return user


# Type alias for current user dependency
CurrentUserDep = Annotated[User, Depends(get_current_user)] 