from pydantic import BaseModel, Field, ConfigDict, EmailStr
from datetime import datetime
from typing import Optional


class UserBase(BaseModel):
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        populate_by_name=True,
        from_attributes=True
    )
    
    username: str = Field(..., min_length=3, max_length=50, description="Username")
    email: EmailStr = Field(..., description="Email address")
    first_name: Optional[str] = Field(None, max_length=50, description="First name")
    middle_name: Optional[str] = Field(None, max_length=50, description="Middle name")
    last_name: Optional[str] = Field(None, max_length=50, description="Last name")
    mobile_number: Optional[str] = Field(None, max_length=20, description="Mobile number")


class UserCreate(UserBase):
    password: str = Field(..., min_length=8, description="Password (minimum 8 characters)")


class UserLogin(BaseModel):
    username: str = Field(..., description="Username or email")
    password: str = Field(..., description="Password")


class UserResponse(UserBase):
    user_id: int
    date_created: datetime
    last_login: Optional[datetime] = None
    is_active: bool
    user_level_id: Optional[str] = None
    department_id: Optional[int] = None


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int


class TokenData(BaseModel):
    username: Optional[str] = None 