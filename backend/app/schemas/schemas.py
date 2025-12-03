from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    username: str = Field(..., min_length=3, max_length=100)
    display_name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = None
    preferred_language: Optional[str] = Field(default="th", pattern="^(th|en|ja)$")


class UserCreate(UserBase):
    firebase_uid: Optional[str] = None


class UserUpdate(BaseModel):
    display_name: Optional[str] = Field(None, max_length=255)
    avatar_url: Optional[str] = None
    preferred_language: Optional[str] = Field(None, pattern="^(th|en|ja)$")


class UserRoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(user|admin|moderator)$")


class UserResponse(UserBase):
    id: UUID
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    users: List[UserResponse]
    total: int
    page: int
    total_pages: int


# Auth Schemas
class FirebaseLoginRequest(BaseModel):
    firebase_token: str


class SupabaseLoginRequest(BaseModel):
    access_token: str


class AuthResponse(BaseModel):
    message: str
    user: UserResponse
    token: str


# Author Schemas
class AuthorBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
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


class AuthorResponse(AuthorBase):
    id: UUID
    created_at: datetime
    book_count: int = 0
    
    class Config:
        from_attributes = True


class AuthorListResponse(BaseModel):
    authors: List[AuthorResponse]
    total: int
    page: int
    total_pages: int


# Publisher Schemas
class PublisherBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
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


class PublisherResponse(PublisherBase):
    id: UUID
    created_at: datetime
    book_count: int = 0
    
    class Config:
        from_attributes = True


class PublisherListResponse(BaseModel):
    publishers: List[PublisherResponse]
    total: int
    page: int
    total_pages: int


# Tag Schemas
class TagBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    name_th: Optional[str] = Field(None, max_length=100)
    category: str = Field(default="genre", pattern="^(genre|theme|demographic|content_warning)$")


class TagCreate(TagBase):
    pass


class TagResponse(TagBase):
    id: UUID
    
    class Config:
        from_attributes = True


class TagWithCount(TagResponse):
    book_count: int = 0


# Book Schemas
class BookBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=500)
    title_th: Optional[str] = Field(None, max_length=500)
    original_title: Optional[str] = Field(None, max_length=500)
    description: Optional[str] = None
    description_th: Optional[str] = None
    cover_image_url: Optional[str] = None
    type: str = Field(default="manga", pattern="^(manga|novel|light_novel|manhwa|manhua)$")
    status: str = Field(default="ongoing", pattern="^(ongoing|completed|hiatus|cancelled)$")
    publication_year: Optional[int] = Field(None, ge=1900, le=2100)
    total_chapters: Optional[int] = Field(None, ge=0)
    total_volumes: Optional[int] = Field(None, ge=0)
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
    total_chapters: Optional[int] = Field(None, ge=0)
    total_volumes: Optional[int] = Field(None, ge=0)
    author_id: Optional[UUID] = None
    publisher_id: Optional[UUID] = None
    tags: Optional[List[UUID]] = None


class BookResponse(BookBase):
    id: UUID
    average_rating: float
    total_ratings: int
    total_reviews: int
    view_count: int
    created_at: datetime
    author_name: Optional[str] = None
    author_name_th: Optional[str] = None
    publisher_name: Optional[str] = None
    publisher_name_th: Optional[str] = None
    tags: List[TagResponse] = []
    
    class Config:
        from_attributes = True


class BookListResponse(BaseModel):
    books: List[BookResponse]
    total: int
    page: int
    total_pages: int


class BookAutocomplete(BaseModel):
    id: UUID
    title: str
    title_th: Optional[str] = None
    cover_image_url: Optional[str] = None
    type: str


# Review Schemas
class ReviewBase(BaseModel):
    book_id: UUID
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    is_spoiler: bool = False


class ReviewCreate(ReviewBase):
    pass


class ReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[str] = None
    is_spoiler: Optional[bool] = None


class ReviewResponse(BaseModel):
    id: UUID
    user_id: UUID
    book_id: UUID
    rating: Optional[int]
    title: Optional[str]
    content: Optional[str]
    is_spoiler: bool
    is_approved: bool
    helpful_count: int
    created_at: datetime
    username: Optional[str] = None
    display_name: Optional[str] = None
    user_avatar: Optional[str] = None
    book_title: Optional[str] = None
    book_title_th: Optional[str] = None
    
    class Config:
        from_attributes = True


class ReviewListResponse(BaseModel):
    reviews: List[ReviewResponse]
    total: int
    page: int
    total_pages: int


# Favorite Schemas
class FavoriteBase(BaseModel):
    book_id: UUID
    list_name: str = Field(default="favorites", pattern="^(favorites|reading|completed|plan_to_read|dropped)$")


class FavoriteCreate(FavoriteBase):
    pass


class FavoriteListUpdate(BaseModel):
    old_list_name: str = Field(..., pattern="^(favorites|reading|completed|plan_to_read|dropped)$")
    new_list_name: str = Field(..., pattern="^(favorites|reading|completed|plan_to_read|dropped)$")


class FavoriteResponse(BaseModel):
    id: UUID
    book_id: UUID
    list_name: str
    created_at: datetime
    title: Optional[str] = None
    title_th: Optional[str] = None
    cover_image_url: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    average_rating: Optional[float] = None
    author_name: Optional[str] = None
    author_name_th: Optional[str] = None
    
    class Config:
        from_attributes = True


class FavoriteListResponse(BaseModel):
    favorites: List[FavoriteResponse]
    total: int
    page: int
    total_pages: int


class FavoriteCheckResponse(BaseModel):
    is_favorite: bool
    lists: List[str]


class ListCount(BaseModel):
    list_name: str
    count: int


# Interaction Schemas
class InteractionCreate(BaseModel):
    book_id: UUID
    interaction_type: str = Field(..., pattern="^(view|click|read_more|share)$")
    weight: float = Field(default=1.0, ge=0, le=5)


# Search History Schemas
class SearchHistoryResponse(BaseModel):
    id: UUID
    search_query: str
    filters: Optional[dict] = None
    results_count: int
    created_at: datetime
    
    class Config:
        from_attributes = True


class PopularSearchResponse(BaseModel):
    search_query: str
    search_count: int


# Recommendation Schemas
class RecommendationResponse(BookResponse):
    recommendation_score: Optional[float] = None


# Generic Response Schemas
class MessageResponse(BaseModel):
    message: str


class HealthResponse(BaseModel):
    status: str
    timestamp: datetime
