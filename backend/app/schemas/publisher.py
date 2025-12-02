from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, HttpUrl


class PublisherBase(BaseModel):
    name: str = Field(..., max_length=255)
    name_th: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    description_th: Optional[str] = None
    website_url: Optional[str] = None
    logo_url: Optional[str] = None


class PublisherCreate(PublisherBase):
    pass


class PublisherUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=255)
    name_th: Optional[str] = Field(None, max_length=255)
    description: Optional[str] = None
    description_th: Optional[str] = None
    website_url: Optional[str] = None
    logo_url: Optional[str] = None


class PublisherResponse(BaseModel):
    id: UUID
    name: str
    name_th: Optional[str] = None
    description: Optional[str] = None
    description_th: Optional[str] = None
    website_url: Optional[str] = None
    logo_url: Optional[str] = None
    book_count: Optional[int] = 0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PublisherListResponse(BaseModel):
    publishers: List[PublisherResponse]
    total: int
    page: int
    totalPages: int
