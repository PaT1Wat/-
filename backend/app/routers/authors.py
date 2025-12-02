from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config.database import get_db
from app.middleware.auth import get_current_user, require_admin
from app.models import Author, Book, User
from app.schemas import (
    AuthorCreate, AuthorUpdate, AuthorResponse, AuthorListResponse,
    BookResponse, MessageResponse
)


router = APIRouter(prefix="/authors", tags=["Authors"])


@router.get("", response_model=AuthorListResponse)
async def get_authors(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get all authors with pagination."""
    offset = (page - 1) * limit
    
    # Get authors with book count
    result = await db.execute(
        select(Author, func.count(Book.id).label("book_count"))
        .outerjoin(Book)
        .group_by(Author.id)
        .order_by(Author.name.asc())
        .offset(offset)
        .limit(limit)
    )
    rows = result.all()
    
    # Get total count
    count_result = await db.execute(select(func.count(Author.id)))
    total = count_result.scalar_one()
    
    authors = [
        AuthorResponse(
            id=author.id,
            name=author.name,
            name_th=author.name_th,
            biography=author.biography,
            biography_th=author.biography_th,
            avatar_url=author.avatar_url,
            created_at=author.created_at,
            book_count=count
        )
        for author, count in rows
    ]
    
    return AuthorListResponse(
        authors=authors,
        total=total,
        page=page,
        total_pages=(total + limit - 1) // limit if total > 0 else 0
    )


@router.get("/search", response_model=List[AuthorResponse])
async def search_authors(
    query: str = "",
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Search authors by name."""
    if not query:
        return []
    
    search_pattern = f"%{query}%"
    result = await db.execute(
        select(Author, func.count(Book.id).label("book_count"))
        .outerjoin(Book)
        .where(
            Author.name.ilike(search_pattern) | 
            Author.name_th.ilike(search_pattern)
        )
        .group_by(Author.id)
        .order_by(Author.name.asc())
        .limit(limit)
    )
    rows = result.all()
    
    return [
        AuthorResponse(
            id=author.id,
            name=author.name,
            name_th=author.name_th,
            biography=author.biography,
            biography_th=author.biography_th,
            avatar_url=author.avatar_url,
            created_at=author.created_at,
            book_count=count
        )
        for author, count in rows
    ]


@router.get("/{author_id}", response_model=AuthorResponse)
async def get_author_by_id(
    author_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get an author by ID."""
    result = await db.execute(
        select(Author, func.count(Book.id).label("book_count"))
        .outerjoin(Book)
        .where(Author.id == author_id)
        .group_by(Author.id)
    )
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    
    author, count = row
    return AuthorResponse(
        id=author.id,
        name=author.name,
        name_th=author.name_th,
        biography=author.biography,
        biography_th=author.biography_th,
        avatar_url=author.avatar_url,
        created_at=author.created_at,
        book_count=count
    )


@router.get("/{author_id}/books", response_model=dict)
async def get_author_books(
    author_id: UUID,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get books by an author."""
    # Check if author exists
    result = await db.execute(
        select(Author, func.count(Book.id).label("book_count"))
        .outerjoin(Book)
        .where(Author.id == author_id)
        .group_by(Author.id)
    )
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    
    author, count = row
    
    # Get books
    offset = (page - 1) * limit
    books_result = await db.execute(
        select(Book)
        .where(Book.author_id == author_id)
        .order_by(Book.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    books = books_result.scalars().all()
    
    return {
        "author": AuthorResponse(
            id=author.id,
            name=author.name,
            name_th=author.name_th,
            biography=author.biography,
            biography_th=author.biography_th,
            avatar_url=author.avatar_url,
            created_at=author.created_at,
            book_count=count
        ),
        "books": [BookResponse.model_validate(book) for book in books]
    }


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_author(
    author_data: AuthorCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new author (Admin only)."""
    author = Author(
        name=author_data.name,
        name_th=author_data.name_th,
        biography=author_data.biography,
        biography_th=author_data.biography_th,
        avatar_url=author_data.avatar_url
    )
    db.add(author)
    await db.commit()
    await db.refresh(author)
    
    return {
        "message": "Author created successfully",
        "author": AuthorResponse(
            id=author.id,
            name=author.name,
            name_th=author.name_th,
            biography=author.biography,
            biography_th=author.biography_th,
            avatar_url=author.avatar_url,
            created_at=author.created_at,
            book_count=0
        )
    }


@router.put("/{author_id}", response_model=dict)
async def update_author(
    author_id: UUID,
    author_data: AuthorUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update an author (Admin only)."""
    result = await db.execute(select(Author).where(Author.id == author_id))
    author = result.scalar_one_or_none()
    
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    
    update_data = author_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(author, field, value)
    
    await db.commit()
    await db.refresh(author)
    
    # Get book count
    count_result = await db.execute(
        select(func.count(Book.id)).where(Book.author_id == author_id)
    )
    book_count = count_result.scalar_one()
    
    return {
        "message": "Author updated successfully",
        "author": AuthorResponse(
            id=author.id,
            name=author.name,
            name_th=author.name_th,
            biography=author.biography,
            biography_th=author.biography_th,
            avatar_url=author.avatar_url,
            created_at=author.created_at,
            book_count=book_count
        )
    }


@router.delete("/{author_id}", response_model=MessageResponse)
async def delete_author(
    author_id: UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete an author (Admin only)."""
    result = await db.execute(select(Author).where(Author.id == author_id))
    author = result.scalar_one_or_none()
    
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found"
        )
    
    await db.delete(author)
    await db.commit()
    
    return MessageResponse(message="Author deleted successfully")
