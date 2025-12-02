from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class InteractionCreate(BaseModel):
    book_id: UUID
    interaction_type: str = Field(..., pattern="^(view|click|read_more|share)$")
    weight: Optional[float] = Field(1.0, ge=0, le=5)


class RecommendationResponse(BaseModel):
    id: UUID
    title: str
    title_th: Optional[str] = None
    cover_image_url: Optional[str] = None
    type: Optional[str] = None
    average_rating: Optional[float] = None
    author_name: Optional[str] = None
    author_name_th: Optional[str] = None
    recommendation_score: Optional[float] = None

    class Config:
        from_attributes = True


class SimilarityScore(BaseModel):
    bookId: UUID
    similarity: float


class PredictedRating(BaseModel):
    bookId: UUID
    predictedRating: float


class SearchHistoryItem(BaseModel):
    id: UUID
    search_query: str
    filters: Optional[Dict[str, Any]] = None
    results_count: Optional[int] = 0
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PopularSearchItem(BaseModel):
    search_query: str
    search_count: int
