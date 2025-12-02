from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth import get_current_user, require_admin
from app.models.user_interaction import UserInteraction
from app.models.search_history import SearchHistory
from app.services.recommendation_service import recommendation_service
from app.schemas.recommendation import (
    InteractionCreate,
    PopularSearchItem,
    SearchHistoryItem,
)

router = APIRouter()


@router.get("/popular")
async def get_popular_books(limit: int = 10):
    """Get popular books (cold start)."""
    books = await recommendation_service.get_popular_books(limit)
    return books


@router.get("/searches/popular")
async def get_popular_searches(limit: int = 10):
    """Get popular searches."""
    searches = await SearchHistory.get_popular_searches(limit)
    return searches


@router.get("/personalized")
async def get_personalized_recommendations(
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
):
    """Get personalized recommendations."""
    recommendations = await recommendation_service.get_personalized_recommendations(
        current_user["id"],
        limit,
    )
    return recommendations


@router.get("/hybrid")
async def get_hybrid_recommendations(
    book_id: Optional[UUID] = None,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
):
    """Get hybrid recommendations."""
    recommendations = await recommendation_service.get_hybrid_recommendations(
        current_user["id"],
        book_id,
        limit,
    )
    return recommendations


@router.get("/content-based")
async def get_content_based_recommendations(
    book_id: Optional[UUID] = None,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
):
    """Get content-based recommendations."""
    if not book_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="book_id is required",
        )
    
    similarities = await recommendation_service.get_content_based_recommendations(
        book_id,
        limit,
    )
    return similarities


@router.get("/collaborative/knn")
async def get_knn_recommendations(
    limit: int = 10,
    k: int = 5,
    current_user: dict = Depends(get_current_user),
):
    """Get collaborative filtering recommendations (KNN)."""
    recommendations = await recommendation_service.get_knn_recommendations(
        current_user["id"],
        k,
        limit,
    )
    return recommendations


@router.get("/collaborative/svd")
async def get_svd_recommendations(
    limit: int = 10,
    factors: int = 10,
    current_user: dict = Depends(get_current_user),
):
    """Get SVD-based recommendations."""
    recommendations = await recommendation_service.get_svd_recommendations(
        current_user["id"],
        factors,
        limit,
    )
    return recommendations


@router.post("/interaction")
async def record_interaction(
    interaction_data: InteractionCreate,
    current_user: dict = Depends(get_current_user),
):
    """Record user interaction."""
    valid_types = ["view", "click", "read_more", "share"]
    if interaction_data.interaction_type not in valid_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid interaction type",
        )
    
    await UserInteraction.record(
        current_user["id"],
        interaction_data.book_id,
        interaction_data.interaction_type,
        interaction_data.weight or 1.0,
    )
    return {"message": "Interaction recorded"}


@router.get("/history")
async def get_search_history(
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
):
    """Get user's search history."""
    history = await SearchHistory.get_by_user_id(current_user["id"], limit)
    return history


@router.delete("/history")
async def clear_search_history(current_user: dict = Depends(get_current_user)):
    """Clear search history."""
    await SearchHistory.clear_history(current_user["id"])
    return {"message": "Search history cleared"}


@router.get("/suggestions")
async def get_search_suggestions(
    query: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """Get search suggestions."""
    if not query or len(query) < 2:
        return []
    
    suggestions = await SearchHistory.get_suggestions_from_history(
        current_user["id"],
        query,
    )
    return suggestions


@router.post("/initialize")
async def initialize_recommendations(current_user: dict = Depends(require_admin)):
    """Initialize recommendation service (Admin)."""
    await recommendation_service.initialize_tfidf()
    return {"message": "Recommendation service initialized"}
