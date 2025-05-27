"""
Database initialization and seeding service.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from app.database import engine, Base
from app.models.user_level import UserLevel
from app.models.user import User
from app.utils.security import get_password_hash
import logging

logger = logging.getLogger(__name__)


async def create_tables():
    """Create all database tables."""
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


async def seed_user_levels():
    """Seed initial user levels if they don't exist."""
    try:
        async with AsyncSession(engine) as session:
            # Check if user levels already exist
            result = await session.execute(select(UserLevel))
            existing_levels = result.scalars().all()
            
            if not existing_levels:
                # Create default user levels
                user_levels = [
                    UserLevel(user_level_id=1, name="admin", description="Administrator with full access"),
                    UserLevel(user_level_id=2, name="manager", description="Manager with limited administrative access"),
                    UserLevel(user_level_id=3, name="general user", description="General user with basic access")
                ]
                
                for level in user_levels:
                    session.add(level)
                
                await session.commit()
                logger.info("User levels seeded successfully")
            else:
                logger.info("User levels already exist, skipping seeding")
                
    except Exception as e:
        logger.error(f"Error seeding user levels: {e}")
        raise


async def seed_test_users():
    """Seed test users with different roles for testing purposes."""
    try:
        async with AsyncSession(engine) as session:
            # Check if test users already exist
            result = await session.execute(
                select(User).where(User.username.in_(["test_admin_user", "test_manager_user"]))
            )
            existing_users = result.scalars().all()
            
            if len(existing_users) < 2:  # If we don't have both test users
                test_users = [
                    {
                        "username": "test_admin_user",
                        "email": "test_admin@example.com",
                        "password": "adminpass123",
                        "first_name": "Test",
                        "last_name": "Admin",
                        "user_level_id": "1"  # Admin role
                    },
                    {
                        "username": "test_manager_user", 
                        "email": "test_manager@example.com",
                        "password": "managerpass123",
                        "first_name": "Test",
                        "last_name": "Manager",
                        "user_level_id": "2"  # Manager role
                    }
                ]
                
                for user_data in test_users:
                    # Check if this specific user exists
                    result = await session.execute(
                        select(User).where(User.username == user_data["username"])
                    )
                    existing_user = result.scalar_one_or_none()
                    
                    if not existing_user:
                        hashed_password = get_password_hash(user_data["password"])
                        
                        test_user = User(
                            username=user_data["username"],
                            email=user_data["email"],
                            password_hash=hashed_password,
                            first_name=user_data["first_name"],
                            last_name=user_data["last_name"],
                            user_level_id=user_data["user_level_id"],
                            is_active=True
                        )
                        
                        session.add(test_user)
                
                await session.commit()
                logger.info("Test users seeded successfully")
            else:
                logger.info("Test users already exist, skipping seeding")
                
    except Exception as e:
        logger.error(f"Error seeding test users: {e}")
        raise


async def initialize_database():
    """Initialize database with tables and seed data."""
    logger.info("Initializing database...")
    await create_tables()
    await seed_user_levels()
    await seed_test_users()
    logger.info("Database initialization completed") 