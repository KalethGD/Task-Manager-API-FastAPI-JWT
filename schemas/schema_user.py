from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from core.enum import UserRole


class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=255)
    role: UserRole = UserRole.USER

class UserUpdate(BaseModel):
    email: EmailStr | None = None
    username: str | None = Field(None, min_length=3, max_length=50)
    password: str | None = Field(None, min_length=8, max_length=255)
    role: UserRole | None = None

class UserResponse(UserBase):
    id: int
    is_active: bool
    role: UserRole
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class UserInDB(UserResponse):
    hashed_password: str