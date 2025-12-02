from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class FavoriteBase(BaseModel):
    book_id: UUID
    list_name: Optional[str] = Field(
        "favorites", 
        pattern="^(favorites|reading|completed|plan_to_read|dropped)$"
    )


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteUpdateList(BaseModel):
    old_list_name: str = Field(..., pattern="^(favorites|reading|completed|plan_to_read|dropped)$")
    new_list_name: str = Field(..., pattern="^(favorites|reading|completed|plan_to_read|dropped)$")


class FavoriteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    
    id: UUID
    user_id: UUID
    book_id: UUID
    list_name: str
    title: Optional[str] = None
    title_th: Optional[str] = None
    cover_image_url: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    average_rating: Optional[float] = None
    author_id: Optional[UUID] = None
    author_name: Optional[str] = None
    author_name_th: Optional[str] = None
    created_at: Optional[datetime] = None


class FavoriteListResponse(BaseModel):
    favorites: List[FavoriteResponse]
    total: int
    page: int
    totalPages: int


class FavoriteCheckResponse(BaseModel):
    isFavorite: bool
    lists: List[str]


class ListCountResponse(BaseModel):
    list_name: str
    count: int
