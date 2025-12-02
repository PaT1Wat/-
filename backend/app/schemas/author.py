from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class AuthorBase(BaseModel):
    name: str = Field(..., max_length=255)
    name_th: Optional[str] = Field(None, max_length=255)
    biography: Optional[str] = None
    biography_th: Optional[str] = None
    avatar_url: Optional[str] = None


class AuthorCreate(AuthorBase):
    pass


class AuthorUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    name_th: Optional[str] = Field(None, max_length=255)
    biography: Optional[str] = None
    biography_th: Optional[str] = None
    avatar_url: Optional[str] = None


class AuthorResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    name: str
    name_th: Optional[str] = None
    biography: Optional[str] = None
    biography_th: Optional[str] = None
    avatar_url: Optional[str] = None
    book_count: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class AuthorListResponse(BaseModel):
    authors: List[AuthorResponse]
    total: int
    page: int
    totalPages: int
