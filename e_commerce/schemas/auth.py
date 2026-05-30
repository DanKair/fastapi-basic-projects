from typing import Annotated

from fastapi import Form
from pydantic import BaseModel, Field, field_validator, model_validator

from schemas.users import UserBase


class UserRegister(UserBase):
    password: str = Field(min_length=8)
    password_confirm: str = Field(min_length=8)

    @model_validator(mode="after")
    def validate_passwords(self):
        if self.password != self.password_confirm:
            raise ValueError("Passwords do not match")
        return self
    

    @field_validator('username', mode='after')
    @classmethod
    def valid_username(cls, username: str):
        if username and username[:1].isdigit():
            raise ValueError("Username shouldn't start with digit")
        return username.strip()

class UserLogin(BaseModel):
    # Email or username as identifier (Originally)
    username: str = Field(max_length=50, description="Username field")
    password: str = Field(min_length=8)
    model_config = {"extra": "forbid"}

    @field_validator('username', mode='after')
    @classmethod
    def valid_username(cls, username: str):
        # Cleaning and normalizing data
        username = username.strip().lower()
        if username and username[:1].isdigit():
            raise ValueError("Username or email shouldn't start with digit")
        return username
    

class TokenResponse(BaseModel):
    """Acess token model"""
    access_token: str
    token_type: str

class TokenPairsResponse(BaseModel):
    access_token: str
    refresh_token: str


