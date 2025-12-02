from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


# Base schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=50)
    display_name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = None
    preferred_language: Optional[str] = Field("th", pattern="^(th|en|ja)$")


class UserCreate(UserBase):
    firebase_uid: Optional[str] = None


class UserUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = None
    preferred_language: Optional[str] = Field(None, pattern="^(th|en|ja)$")


class UserResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    email: EmailStr
    username: str
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str = "user"
    preferred_language: Optional[str] = "th"
    created_at: Optional[datetime] = None


class UserRoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(user|admin|moderator)$")


# Auth schemas
class FirebaseLoginRequest(BaseModel):
    firebase_token: str = Field(..., min_length=1)


class RegisterRequest(UserBase):
    firebase_uid: Optional[str] = None


class AuthResponse(BaseModel):
    message: str
    user: UserResponse
    token: str


class ProfileResponse(UserResponse):
    pass


# Token schemas
class TokenData(BaseModel):
    user_id: Optional[str] = None
    email: Optional[str] = None
    role: Optional[str] = None
