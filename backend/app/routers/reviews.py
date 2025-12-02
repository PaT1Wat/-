from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config.database import get_db
from app.middleware.auth import get_current_user, require_moderator
from app.models import Review, Book, User
from app.schemas import (
    ReviewCreate, ReviewUpdate, ReviewResponse, ReviewListResponse, MessageResponse
)


router = APIRouter(prefix="/reviews", tags=["Reviews"])


def review_to_response(review: Review) -> ReviewResponse:
    """Convert Review model to ReviewResponse schema."""
    return ReviewResponse(
        id=review.id,
        user_id=review.user_id,
        book_id=review.book_id,
        rating=review.rating,
        title=review.title,
        content=review.content,
        is_spoiler=review.is_spoiler,
        is_approved=review.is_approved,
        helpful_count=review.helpful_count,
        created_at=review.created_at,
        username=review.user.username if review.user else None,
        display_name=review.user.display_name if review.user else None,
        user_avatar=review.user.avatar_url if review.user else None,
        book_title=review.book.title if review.book else None,
        book_title_th=review.book.title_th if review.book else None
    )


@router.get("/book/{book_id}", response_model=ReviewListResponse)
async def get_book_reviews(
    book_id: UUID,
    page: int = 1,
    limit: int = 10,
    sort_by: str = "created_at",
    db: AsyncSession = Depends(get_db)
):
    """Get reviews for a book."""
    offset = (page - 1) * limit
    
    # Validate sort field
    valid_sort_fields = {
        "created_at": Review.created_at,
        "rating": Review.rating,
        "helpful_count": Review.helpful_count
    }
    sort_field = valid_sort_fields.get(sort_by, Review.created_at)
    
    result = await db.execute(
        select(Review)
        .options(selectinload(Review.user), selectinload(Review.book))
        .where(and_(Review.book_id == book_id, Review.is_approved == True))
        .order_by(sort_field.desc())
        .offset(offset)
        .limit(limit)
    )
    reviews = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Review.id))
        .where(and_(Review.book_id == book_id, Review.is_approved == True))
    )
    total = count_result.scalar_one()
    
    return ReviewListResponse(
        reviews=[review_to_response(review) for review in reviews],
        total=total,
        page=page,
        total_pages=(total + limit - 1) // limit if total > 0 else 0
    )


@router.get("/user", response_model=ReviewListResponse)
async def get_current_user_reviews(
    page: int = 1,
    limit: int = 10,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get reviews by the current user."""
    return await get_user_reviews(current_user.id, page, limit, db)


@router.get("/user/{user_id}", response_model=ReviewListResponse)
async def get_user_reviews(
    user_id: UUID,
    page: int = 1,
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get reviews by a user."""
    offset = (page - 1) * limit
    
    result = await db.execute(
        select(Review)
        .options(selectinload(Review.user), selectinload(Review.book))
        .where(Review.user_id == user_id)
        .order_by(Review.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    reviews = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Review.id)).where(Review.user_id == user_id)
    )
    total = count_result.scalar_one()
    
    return ReviewListResponse(
        reviews=[review_to_response(review) for review in reviews],
        total=total,
        page=page,
        total_pages=(total + limit - 1) // limit if total > 0 else 0
    )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new review."""
    # Check if user already reviewed this book
    existing = await db.execute(
        select(Review).where(
            and_(Review.user_id == current_user.id, Review.book_id == review_data.book_id)
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already reviewed this book"
        )
    
    review = Review(
        user_id=current_user.id,
        book_id=review_data.book_id,
        rating=review_data.rating,
        title=review_data.title,
        content=review_data.content,
        is_spoiler=review_data.is_spoiler
    )
    db.add(review)
    await db.commit()
    
    # Reload with relationships
    result = await db.execute(
        select(Review)
        .options(selectinload(Review.user), selectinload(Review.book))
        .where(Review.id == review.id)
    )
    review = result.scalar_one()
    
    return {
        "message": "Review created successfully",
        "review": review_to_response(review)
    }


@router.put("/{review_id}", response_model=dict)
async def update_review(
    review_id: UUID,
    review_data: ReviewUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update a review."""
    result = await db.execute(
        select(Review).where(
            and_(Review.id == review_id, Review.user_id == current_user.id)
        )
    )
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or not authorized"
        )
    
    update_data = review_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(review, field, value)
    
    await db.commit()
    
    # Reload with relationships
    result = await db.execute(
        select(Review)
        .options(selectinload(Review.user), selectinload(Review.book))
        .where(Review.id == review_id)
    )
    review = result.scalar_one()
    
    return {
        "message": "Review updated successfully",
        "review": review_to_response(review)
    }


@router.delete("/{review_id}", response_model=MessageResponse)
async def delete_review(
    review_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a review."""
    # Admin can delete any review
    if current_user.role == "admin":
        result = await db.execute(select(Review).where(Review.id == review_id))
    else:
        result = await db.execute(
            select(Review).where(
                and_(Review.id == review_id, Review.user_id == current_user.id)
            )
        )
    
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or not authorized"
        )
    
    await db.delete(review)
    await db.commit()
    
    return MessageResponse(message="Review deleted successfully")


@router.post("/{review_id}/helpful", response_model=dict)
async def mark_helpful(
    review_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark a review as helpful."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    review.helpful_count += 1
    await db.commit()
    
    return {
        "message": "Review marked as helpful",
        "helpful_count": review.helpful_count
    }


@router.get("/pending", response_model=ReviewListResponse)
async def get_pending_reviews(
    page: int = 1,
    limit: int = 20,
    moderator: User = Depends(require_moderator),
    db: AsyncSession = Depends(get_db)
):
    """Get pending reviews (Moderator only)."""
    offset = (page - 1) * limit
    
    result = await db.execute(
        select(Review)
        .options(selectinload(Review.user), selectinload(Review.book))
        .where(Review.is_approved == False)
        .order_by(Review.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    reviews = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(
        select(func.count(Review.id)).where(Review.is_approved == False)
    )
    total = count_result.scalar_one()
    
    return ReviewListResponse(
        reviews=[review_to_response(review) for review in reviews],
        total=total,
        page=page,
        total_pages=(total + limit - 1) // limit if total > 0 else 0
    )


@router.put("/{review_id}/approve", response_model=dict)
async def approve_review(
    review_id: UUID,
    moderator: User = Depends(require_moderator),
    db: AsyncSession = Depends(get_db)
):
    """Approve a review (Moderator only)."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    review.is_approved = True
    await db.commit()
    
    # Reload with relationships
    result = await db.execute(
        select(Review)
        .options(selectinload(Review.user), selectinload(Review.book))
        .where(Review.id == review_id)
    )
    review = result.scalar_one()
    
    return {
        "message": "Review approved successfully",
        "review": review_to_response(review)
    }


@router.delete("/{review_id}/reject", response_model=MessageResponse)
async def reject_review(
    review_id: UUID,
    moderator: User = Depends(require_moderator),
    db: AsyncSession = Depends(get_db)
):
    """Reject a review (Moderator only)."""
    result = await db.execute(select(Review).where(Review.id == review_id))
    review = result.scalar_one_or_none()
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    await db.delete(review)
    await db.commit()
    
    return MessageResponse(message="Review rejected successfully")
