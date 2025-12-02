from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth import get_current_user
from app.models.favorite import Favorite
from app.schemas.favorite import (
    FavoriteCheckResponse,
    FavoriteCreate,
    FavoriteListResponse,
    FavoriteUpdateList,
    ListCountResponse,
)

router = APIRouter()


@router.get("", response_model=FavoriteListResponse)
async def get_favorites(
    list_name: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(get_current_user),
):
    """Get user's favorites."""
    return await Favorite.get_by_user_id(current_user["id"], list_name, page, limit)


@router.get("/counts")
async def get_list_counts(current_user: dict = Depends(get_current_user)):
    """Get list counts."""
    counts = await Favorite.get_list_counts(current_user["id"])
    return counts


@router.get("/check/{book_id}", response_model=FavoriteCheckResponse)
async def check_favorite(
    book_id: UUID,
    current_user: dict = Depends(get_current_user),
):
    """Check if book is in favorites."""
    lists = await Favorite.check_favorite(current_user["id"], book_id)
    return {
        "isFavorite": len(lists) > 0,
        "lists": [l["list_name"] for l in lists],
    }


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    favorite_data: FavoriteCreate,
    current_user: dict = Depends(get_current_user),
):
    """Add to favorites."""
    favorite = await Favorite.add(
        current_user["id"], 
        favorite_data.book_id, 
        favorite_data.list_name or "favorites"
    )
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book already in this list",
        )
    
    return {
        "message": "Book added to favorites",
        "favorite": favorite,
    }


@router.delete("/{book_id}")
async def remove_favorite(
    book_id: UUID,
    list_name: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    """Remove from favorites."""
    favorite = await Favorite.remove(current_user["id"], book_id, list_name)
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found",
        )
    
    return {"message": "Book removed from favorites"}


@router.put("/{book_id}/list")
async def update_favorite_list(
    book_id: UUID,
    list_data: FavoriteUpdateList,
    current_user: dict = Depends(get_current_user),
):
    """Move book to different list."""
    favorite = await Favorite.update_list(
        current_user["id"],
        book_id,
        list_data.old_list_name,
        list_data.new_list_name,
    )
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found",
        )
    
    return {
        "message": "List updated successfully",
        "favorite": favorite,
    }
