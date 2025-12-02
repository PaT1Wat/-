from datetime import datetime
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class TagBase(BaseModel):
    name: str = Field(..., max_length=100)
    name_th: Optional[str] = Field(None, max_length=100)
    category: Optional[str] = Field("genre", pattern="^(genre|theme|demographic|content_warning)$")


class TagCreate(TagBase):
    pass


class TagResponse(BaseModel):
    id: UUID
    name: str
    name_th: Optional[str] = None
    category: Optional[str] = None

    class Config:
        from_attributes = True


class TagWithCount(TagResponse):
    book_count: Optional[int] = 0


class BookBase(BaseModel):
    title: str = Field(..., max_length=500)
    title_th: Optional[str] = Field(None, max_length=500)
    original_title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    description_th: Optional[str] = None
    cover_image_url: Optional[str] = None
    type: Optional[str] = Field("manga", pattern="^(manga|novel|light_novel|manhwa|manhua)$")
    status: Optional[str] = Field("ongoing", pattern="^(ongoing|completed|hiatus|cancelled)$")
    publication_year: Optional[int] = Field(None, ge=1900, le=2100)
    total_chapters: Optional[int] = None
    total_volumes: Optional[int] = None
    author_id: Optional[UUID] = None
    publisher_id: Optional[UUID] = None


class BookCreate(BookBase):
    tags: Optional[List[UUID]] = None


class BookUpdate(BaseModel):
    title: Optional[str] = Field(None, max_length=500)
    title_th: Optional[str] = Field(None, max_length=500)
    original_title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    description_th: Optional[str] = None
    cover_image_url: Optional[str] = None
    type: Optional[str] = Field(None, pattern="^(manga|novel|light_novel|manhwa|manhua)$")
    status: Optional[str] = Field(None, pattern="^(ongoing|completed|hiatus|cancelled)$")
    publication_year: Optional[int] = Field(None, ge=1900, le=2100)
    total_chapters: Optional[int] = None
    total_volumes: Optional[int] = None
    author_id: Optional[UUID] = None
    publisher_id: Optional[UUID] = None
    tags: Optional[List[UUID]] = None


class BookResponse(BaseModel):
    id: UUID
    title: str
    title_th: Optional[str] = None
    original_title: Optional[str] = None
    description: Optional[str] = None
    description_th: Optional[str] = None
    cover_image_url: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    publication_year: Optional[int] = None
    total_chapters: Optional[int] = None
    total_volumes: Optional[int] = None
    author_id: Optional[UUID] = None
    publisher_id: Optional[UUID] = None
    average_rating: Optional[float] = 0.0
    total_ratings: Optional[int] = 0
    total_reviews: Optional[int] = 0
    view_count: Optional[int] = 0
    author_name: Optional[str] = None
    author_name_th: Optional[str] = None
    publisher_name: Optional[str] = None
    publisher_name_th: Optional[str] = None
    tags: Optional[List[Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    books: List[BookResponse]
    total: int
    page: int
    totalPages: int


class BookAutocompleteResponse(BaseModel):
    id: UUID
    title: str
    title_th: Optional[str] = None
    cover_image_url: Optional[str] = None
    type: Optional[str] = None

    class Config:
        from_attributes = True


class SearchParams(BaseModel):
    query: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    tags: Optional[List[str]] = None
    author_id: Optional[UUID] = None
    publisher_id: Optional[UUID] = None
    min_rating: Optional[float] = None
    year_from: Optional[int] = None
    year_to: Optional[int] = None
    sort_by: Optional[str] = "average_rating"
    sort_order: Optional[str] = "DESC"
    page: int = 1
    limit: int = 20
