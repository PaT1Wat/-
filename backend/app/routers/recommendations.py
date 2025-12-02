from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, text, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config.database import get_db
from app.middleware.auth import get_current_user, require_admin
from app.models import Book, User, UserInteraction, SearchHistory
from app.schemas import (
    BookResponse, InteractionCreate, SearchHistoryResponse,
    PopularSearchResponse, MessageResponse
)
from app.services import recommendation_service


router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


def book_to_response(book: Book) -> BookResponse:
    """Convert Book model to BookResponse schema."""
    return BookResponse(
        id=book.id,
        title=book.title,
        title_th=book.title_th,
        original_title=book.original_title,
        description=book.description,
        description_th=book.description_th,
        cover_image_url=book.cover_image_url,
        type=book.type,
        status=book.status,
        publication_year=book.publication_year,
        total_chapters=book.total_chapters,
        total_volumes=book.total_volumes,
        author_id=book.author_id,
        publisher_id=book.publisher_id,
        average_rating=float(book.average_rating),
        total_ratings=book.total_ratings,
        total_reviews=book.total_reviews,
        view_count=book.view_count,
        created_at=book.created_at,
        author_name=book.author.name if book.author else None,
        author_name_th=book.author.name_th if book.author else None,
        publisher_name=book.publisher.name if book.publisher else None,
        publisher_name_th=book.publisher.name_th if book.publisher else None,
        tags=[]
    )


@router.get("/popular", response_model=List[BookResponse])
async def get_popular_books(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get popular books (for cold start)."""
    books = await recommendation_service.get_popular_books(db, limit)
    return [book_to_response(book) for book in books]


@router.get("/searches/popular", response_model=List[PopularSearchResponse])
async def get_popular_searches(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get popular searches."""
    result = await db.execute(
        text("""
            SELECT search_query, COUNT(*) as search_count
            FROM search_history
            WHERE created_at > NOW() - INTERVAL '30 days'
            GROUP BY search_query
            ORDER BY search_count DESC
            LIMIT :limit
        """),
        {"limit": limit}
    )
    rows = result.fetchall()
    
    return [
        PopularSearchResponse(search_query=row[0], search_count=row[1])
        for row in rows
    ]


@router.get("/personalized", response_model=List[BookResponse])
async def get_personalized_recommendations(
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get personalized recommendations based on user preferences."""
    books = await recommendation_service.get_personalized_recommendations(
        db, current_user.id, limit
    )
    return [book_to_response(book) for book in books]


@router.get("/hybrid", response_model=List[BookResponse])
async def get_hybrid_recommendations(
    book_id: Optional[UUID] = None,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get hybrid recommendations combining multiple algorithms."""
    recommendations = await recommendation_service.get_hybrid_recommendations(
        db, current_user.id, book_id, limit
    )
    return [
        book_to_response(rec["book"])
        for rec in recommendations
        if rec["book"]
    ]


@router.get("/content-based", response_model=List[dict])
async def get_content_based_recommendations(
    book_id: UUID,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get content-based recommendations using TF-IDF."""
    recommendations = await recommendation_service.get_content_based_recommendations(
        db, book_id, limit
    )
    return [
        {"book_id": str(book_id), "similarity": similarity}
        for book_id, similarity in recommendations
    ]


@router.get("/collaborative/knn", response_model=List[dict])
async def get_knn_recommendations(
    limit: int = 10,
    k: int = 5,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get KNN-based collaborative filtering recommendations."""
    recommendations = await recommendation_service.get_knn_recommendations(
        db, current_user.id, k, limit
    )
    return [
        {"book_id": str(book_id), "predicted_rating": rating}
        for book_id, rating in recommendations
    ]


@router.get("/collaborative/svd", response_model=List[dict])
async def get_svd_recommendations(
    limit: int = 10,
    factors: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get SVD-based recommendations."""
    recommendations = await recommendation_service.get_svd_recommendations(
        db, current_user.id, factors, limit
    )
    return [
        {"book_id": str(book_id), "predicted_rating": rating}
        for book_id, rating in recommendations
    ]


@router.post("/interaction", response_model=MessageResponse)
async def record_interaction(
    interaction_data: InteractionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Record user interaction with a book."""
    interaction = UserInteraction(
        user_id=current_user.id,
        book_id=interaction_data.book_id,
        interaction_type=interaction_data.interaction_type,
        interaction_weight=interaction_data.weight
    )
    db.add(interaction)
    await db.commit()
    
    return MessageResponse(message="Interaction recorded")


@router.get("/history", response_model=List[SearchHistoryResponse])
async def get_search_history(
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's search history."""
    result = await db.execute(
        select(SearchHistory)
        .where(SearchHistory.user_id == current_user.id)
        .order_by(SearchHistory.created_at.desc())
        .limit(limit)
    )
    history = result.scalars().all()
    
    return [SearchHistoryResponse.model_validate(h) for h in history]


@router.delete("/history", response_model=MessageResponse)
async def clear_search_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Clear user's search history."""
    await db.execute(
        delete(SearchHistory).where(SearchHistory.user_id == current_user.id)
    )
    await db.commit()
    
    return MessageResponse(message="Search history cleared")


@router.get("/suggestions", response_model=List[str])
async def get_search_suggestions(
    query: str = "",
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get search suggestions from history."""
    if not query or len(query) < 2:
        return []
    
    result = await db.execute(
        select(SearchHistory.search_query)
        .where(
            SearchHistory.user_id == current_user.id,
            SearchHistory.search_query.ilike(f"{query}%")
        )
        .distinct()
        .order_by(SearchHistory.created_at.desc())
        .limit(5)
    )
    
    return [row[0] for row in result.all()]


@router.post("/initialize", response_model=MessageResponse)
async def initialize_recommendations(
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Initialize recommendation service (Admin only)."""
    await recommendation_service.initialize_tfidf(db)
    return MessageResponse(message="Recommendation service initialized")
