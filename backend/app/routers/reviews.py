from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth import get_current_user, require_moderator
from app.models.review import Review
from app.schemas.review import (
    ReviewCreate,
    ReviewListResponse,
    ReviewResponse,
    ReviewUpdate,
)

router = APIRouter()


@router.get("/book/{book_id}", response_model=ReviewListResponse)
async def get_book_reviews(
    book_id: UUID,
    page: int = 1,
    limit: int = 10,
    sort_by: str = "created_at",
):
    """Get reviews for a book."""
    return await Review.get_by_book_id(book_id, page, limit, sort_by)


@router.get("/user", response_model=ReviewListResponse)
async def get_current_user_reviews(
    page: int = 1,
    limit: int = 10,
    current_user: dict = Depends(get_current_user),
):
    """Get current user's reviews."""
    return await Review.get_by_user_id(current_user["id"], page, limit)


@router.get("/user/{user_id}", response_model=ReviewListResponse)
async def get_user_reviews(
    user_id: UUID,
    page: int = 1,
    limit: int = 10,
):
    """Get user's reviews."""
    return await Review.get_by_user_id(user_id, page, limit)


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: dict = Depends(get_current_user),
):
    """Create review."""
    # Check if user already reviewed this book
    existing_review = await Review.find_by_user_and_book(
        current_user["id"], 
        review_data.book_id
    )
    if existing_review:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already reviewed this book",
        )
    
    review = await Review.create({
        "user_id": current_user["id"],
        "book_id": review_data.book_id,
        "rating": review_data.rating,
        "title": review_data.title,
        "content": review_data.content,
        "is_spoiler": review_data.is_spoiler,
    })
    
    created_review = await Review.find_by_id(review["id"])
    return {
        "message": "Review created successfully",
        "review": created_review,
    }


@router.put("/{review_id}", response_model=dict)
async def update_review(
    review_id: UUID,
    review_data: ReviewUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update review."""
    review = await Review.update(
        review_id, 
        current_user["id"], 
        review_data.model_dump(exclude_unset=True)
    )
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or not authorized",
        )
    
    updated_review = await Review.find_by_id(review_id)
    return {
        "message": "Review updated successfully",
        "review": updated_review,
    }


@router.delete("/{review_id}")
async def delete_review(
    review_id: UUID,
    current_user: dict = Depends(get_current_user),
):
    """Delete review."""
    # Admin can delete any review, users can only delete their own
    if current_user.get("role") == "admin":
        review = await Review.delete(review_id)
    else:
        review = await Review.delete(review_id, current_user["id"])
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found or not authorized",
        )
    
    return {"message": "Review deleted successfully"}


@router.post("/{review_id}/helpful")
async def mark_helpful(
    review_id: UUID,
    current_user: dict = Depends(get_current_user),
):
    """Mark review as helpful."""
    review = await Review.increment_helpful(review_id)
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )
    
    return {
        "message": "Review marked as helpful",
        "helpful_count": review["helpful_count"],
    }


@router.get("/pending", response_model=ReviewListResponse)
async def get_pending_reviews(
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(require_moderator),
):
    """Moderator: Get pending reviews."""
    return await Review.get_pending_reviews(page, limit)


@router.put("/{review_id}/approve")
async def approve_review(
    review_id: UUID,
    current_user: dict = Depends(require_moderator),
):
    """Moderator: Approve review."""
    review = await Review.approve(review_id)
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )
    
    return {
        "message": "Review approved successfully",
        "review": review,
    }


@router.delete("/{review_id}/reject")
async def reject_review(
    review_id: UUID,
    current_user: dict = Depends(require_moderator),
):
    """Moderator: Reject review."""
    review = await Review.reject(review_id)
    
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found",
        )
    
    return {"message": "Review rejected successfully"}
