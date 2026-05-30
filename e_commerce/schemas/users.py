from datetime import datetime
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator

# What the world sees (Safe for anyone to view)
class UserBase(BaseModel):
    username: str = Field(..., max_length=50, examples=["john_doe", "mary"])
    email: EmailStr


# What the user sees about themselves (Private data)    
class UserResponse(UserBase):
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True   


class UserInDB(UserResponse):
    """Internal use only - includes the hash for DB operations."""    
    password_hash: str         


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
