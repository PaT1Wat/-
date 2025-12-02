from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReviewBase(BaseModel):
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    is_spoiler: Optional[bool] = False


class ReviewCreate(ReviewBase):
    book_id: UUID


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    is_spoiler: Optional[bool] = None


class ReviewResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    book_id: UUID
    rating: int
    title: Optional[str] = None
    content: Optional[str] = None
    is_spoiler: Optional[bool] = False
    is_approved: Optional[bool] = True
    helpful_count: Optional[int] = 0
    username: Optional[str] = None
    display_name: Optional[str] = None
    user_avatar: Optional[str] = None
    book_title: Optional[str] = None
    book_title_th: Optional[str] = None
    cover_image_url: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


class ReviewListResponse(BaseModel):
    reviews: List[ReviewResponse]
    total: int
    page: int
    totalPages: int
