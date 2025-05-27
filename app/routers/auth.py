from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.exc import IntegrityError
from app.dependencies import DatabaseDep, CurrentUserDep
from app.schemas.user import UserCreate, UserResponse, UserLogin, Token
from app.services.user_service import UserService
from app.utils.security import create_access_token
from app.config import settings

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: DatabaseDep
) -> UserResponse:
    """Register a new user."""
    
    # Check if username already exists
    existing_user = await UserService.get_user_by_username(db, user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    existing_email = await UserService.get_user_by_email(db, user_data.email)
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    try:
        # Create user
        user = await UserService.create_user(db, user_data)
        return UserResponse.model_validate(user)
    except IntegrityError:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User registration failed due to data conflict"
        )


@router.post("/login", response_model=Token)
async def login(
    user_credentials: UserLogin,
    db: DatabaseDep
) -> Token:
    """Login user and return access token."""
    
    # Authenticate user
    user = await UserService.authenticate_user(
        db, user_credentials.username, user_credentials.password
    )
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    await UserService.update_last_login(db, user)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60  # Convert to seconds
    )


@router.post("/login/form", response_model=Token)
async def login_form(
    db: DatabaseDep,
    form_data: OAuth2PasswordRequestForm = Depends()
) -> Token:
    """Login using OAuth2 password form (for OpenAPI docs)."""
    
    # Authenticate user
    user = await UserService.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Update last login
    await UserService.update_last_login(db, user)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.access_token_expire_minutes)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    
    return Token(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.access_token_expire_minutes * 60
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: CurrentUserDep) -> UserResponse:
    """Get current user information."""
    return UserResponse.model_validate(current_user) 