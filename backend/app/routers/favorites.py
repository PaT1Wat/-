from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func, and_, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config.database import get_db
from app.middleware.auth import get_current_user
from app.models import Favorite, Book, Author, User
from app.schemas import (
    FavoriteCreate, FavoriteListUpdate, FavoriteResponse, 
    FavoriteListResponse, FavoriteCheckResponse, ListCount, MessageResponse
)


router = APIRouter(prefix="/favorites", tags=["Favorites"])


@router.get("", response_model=FavoriteListResponse)
async def get_favorites(
    list_name: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user's favorites."""
    offset = (page - 1) * limit
    
    stmt = (
        select(Favorite)
        .options(selectinload(Favorite.book).selectinload(Book.author))
        .where(Favorite.user_id == current_user.id)
    )
    
    if list_name:
        stmt = stmt.where(Favorite.list_name == list_name)
    
    stmt = stmt.order_by(Favorite.created_at.desc()).offset(offset).limit(limit)
    
    result = await db.execute(stmt)
    favorites = result.scalars().all()
    
    # Get total count
    count_stmt = select(func.count(Favorite.id)).where(Favorite.user_id == current_user.id)
    if list_name:
        count_stmt = count_stmt.where(Favorite.list_name == list_name)
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()
    
    return FavoriteListResponse(
        favorites=[
            FavoriteResponse(
                id=fav.id,
                book_id=fav.book_id,
                list_name=fav.list_name,
                created_at=fav.created_at,
                title=fav.book.title if fav.book else None,
                title_th=fav.book.title_th if fav.book else None,
                cover_image_url=fav.book.cover_image_url if fav.book else None,
                type=fav.book.type if fav.book else None,
                status=fav.book.status if fav.book else None,
                average_rating=float(fav.book.average_rating) if fav.book else None,
                author_name=fav.book.author.name if fav.book and fav.book.author else None,
                author_name_th=fav.book.author.name_th if fav.book and fav.book.author else None
            )
            for fav in favorites
        ],
        total=total,
        page=page,
        total_pages=(total + limit - 1) // limit if total > 0 else 0
    )


@router.get("/counts", response_model=List[ListCount])
async def get_list_counts(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get favorite list counts."""
    result = await db.execute(
        select(Favorite.list_name, func.count(Favorite.id).label("count"))
        .where(Favorite.user_id == current_user.id)
        .group_by(Favorite.list_name)
    )
    rows = result.all()
    
    return [ListCount(list_name=row[0], count=row[1]) for row in rows]


@router.get("/check/{book_id}", response_model=FavoriteCheckResponse)
async def check_favorite(
    book_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Check if a book is in favorites."""
    result = await db.execute(
        select(Favorite.list_name)
        .where(and_(Favorite.user_id == current_user.id, Favorite.book_id == book_id))
    )
    lists = [row[0] for row in result.all()]
    
    return FavoriteCheckResponse(
        is_favorite=len(lists) > 0,
        lists=lists
    )


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def add_favorite(
    favorite_data: FavoriteCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add a book to favorites."""
    # Check if already exists
    existing = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.user_id == current_user.id,
                Favorite.book_id == favorite_data.book_id,
                Favorite.list_name == favorite_data.list_name
            )
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Book already in this list"
        )
    
    favorite = Favorite(
        user_id=current_user.id,
        book_id=favorite_data.book_id,
        list_name=favorite_data.list_name
    )
    db.add(favorite)
    await db.commit()
    await db.refresh(favorite)
    
    return {
        "message": "Book added to favorites",
        "favorite": FavoriteResponse(
            id=favorite.id,
            book_id=favorite.book_id,
            list_name=favorite.list_name,
            created_at=favorite.created_at
        )
    }


@router.delete("/{book_id}", response_model=MessageResponse)
async def remove_favorite(
    book_id: UUID,
    list_name: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a book from favorites."""
    conditions = [Favorite.user_id == current_user.id, Favorite.book_id == book_id]
    if list_name:
        conditions.append(Favorite.list_name == list_name)
    
    result = await db.execute(select(Favorite).where(and_(*conditions)))
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    await db.delete(favorite)
    await db.commit()
    
    return MessageResponse(message="Book removed from favorites")


@router.put("/{book_id}/list", response_model=dict)
async def update_favorite_list(
    book_id: UUID,
    list_data: FavoriteListUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Move a book to a different list."""
    result = await db.execute(
        select(Favorite).where(
            and_(
                Favorite.user_id == current_user.id,
                Favorite.book_id == book_id,
                Favorite.list_name == list_data.old_list_name
            )
        )
    )
    favorite = result.scalar_one_or_none()
    
    if not favorite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Favorite not found"
        )
    
    favorite.list_name = list_data.new_list_name
    await db.commit()
    await db.refresh(favorite)
    
    return {
        "message": "List updated successfully",
        "favorite": FavoriteResponse(
            id=favorite.id,
            book_id=favorite.book_id,
            list_name=favorite.list_name,
            created_at=favorite.created_at
        )
    }
