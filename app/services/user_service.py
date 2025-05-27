from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from sqlalchemy.sql import func
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.security import get_password_hash, verify_password


class UserService:
    """Service class for user operations."""
    
    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[User]:
        """Get user by username."""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[User]:
        """Get user by email."""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_username_or_email(db: AsyncSession, identifier: str) -> Optional[User]:
        """Get user by username or email."""
        result = await db.execute(
            select(User).where(
                or_(User.username == identifier, User.email == identifier)
            )
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def create_user(db: AsyncSession, user_data: UserCreate, default_role: str = "3") -> User:
        """Create a new user with default role."""
        # Hash the password
        hashed_password = get_password_hash(user_data.password)
        
        # Create user instance with default role (3 = general user)
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=hashed_password,
            first_name=user_data.first_name,
            middle_name=user_data.middle_name,
            last_name=user_data.last_name,
            mobile_number=user_data.mobile_number,
            user_level_id=default_role,  # Assign default role
            is_active=True
        )
        
        db.add(db_user)
        await db.flush()  # Flush to get the ID
        await db.refresh(db_user)
        return db_user
    
    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[User]:
        """Authenticate user with username/email and password."""
        user = await UserService.get_user_by_username_or_email(db, username)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        if not user.is_active:
            return None
        return user
    
    @staticmethod
    async def update_last_login(db: AsyncSession, user: User) -> None:
        """Update user's last login timestamp."""
        user.last_login = func.now()
        await db.flush()
    
    @staticmethod
    async def assign_roles(db: AsyncSession, user_id: int, role_ids: str) -> Optional[User]:
        """Assign roles to a user (CSV format)."""
        result = await db.execute(select(User).where(User.user_id == user_id))
        user = result.scalar_one_or_none()
        
        if user:
            user.user_level_id = role_ids
            await db.flush()
            await db.refresh(user)
        
        return user 