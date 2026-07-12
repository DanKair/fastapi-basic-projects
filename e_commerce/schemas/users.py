from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

from models.users import UserRole

# Public user profile data
class UserRead(BaseModel):
    username: str = Field(..., max_length=50, examples=["john_doe", "mary"])
    email: EmailStr
    role: UserRole = Field(default=UserRole.CUSTOMER, examples=[UserRole.CUSTOMER, UserRole.MANAGER, UserRole.ADMIN])


class UserResponse(UserRead):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True   


class UserInDB(UserResponse):
    """Internal use only - includes the hash for DB operations."""    
    password_hash: str         


class UserCreate(BaseModel):
    username: str = Field(..., max_length=50, examples=["john_doe", "mary"])
    email: EmailStr
    password: str = Field(min_length=8)
    password_confirm: str = Field(min_length=8)

    model_config = {"extra": "forbid"}

    @model_validator(mode="after")
    def validate_passwords(self):
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self

    @field_validator("username", mode="after")
    @classmethod
    def valid_username(cls, username: str):
        if username and username[:1].isdigit():
            raise ValueError("Username shouldn't start with digit")
        return username.strip()


class StaffUserCreate(UserCreate):
    role: UserRole = Field(..., examples=[UserRole.MANAGER, UserRole.ADMIN])

    @field_validator("role", mode="after")
    @classmethod
    def validate_staff_role(cls, role: UserRole):
        if role == UserRole.CUSTOMER:
            raise ValueError("Staff accounts must use manager or admin role")
        return role


class UserUpdate(BaseModel):
    username: str | None = Field(default=None, max_length=50)
    email: EmailStr | None = None
    old_password: str | None = Field(default=None, min_length=8)
    new_password: str | None = Field(default=None, min_length=8)

    @model_validator(mode="after")
    def validate_password_fields(self):
        if self.new_password and not self.old_password:
            raise ValueError("Old password is required to set a new password")
        return self
