from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.middleware.auth import get_current_user, require_admin
from app.models import Publisher, Book, User
from app.schemas import (
    PublisherCreate, PublisherUpdate, PublisherResponse, PublisherListResponse,
    BookResponse, MessageResponse
)


router = APIRouter(prefix="/publishers", tags=["Publishers"])


@router.get("", response_model=PublisherListResponse)
async def get_publishers(
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get all publishers with pagination."""
    offset = (page - 1) * limit
    
    # Get publishers with book count
    result = await db.execute(
        select(Publisher, func.count(Book.id).label("book_count"))
        .outerjoin(Book)
        .group_by(Publisher.id)
        .order_by(Publisher.name.asc())
        .offset(offset)
        .limit(limit)
    )
    rows = result.all()
    
    # Get total count
    count_result = await db.execute(select(func.count(Publisher.id)))
    total = count_result.scalar_one()
    
    publishers = [
        PublisherResponse(
            id=publisher.id,
            name=publisher.name,
            name_th=publisher.name_th,
            description=publisher.description,
            description_th=publisher.description_th,
            website_url=publisher.website_url,
            logo_url=publisher.logo_url,
            created_at=publisher.created_at,
            book_count=count
        )
        for publisher, count in rows
    ]
    
    return PublisherListResponse(
        publishers=publishers,
        total=total,
        page=page,
        total_pages=(total + limit - 1) // limit if total > 0 else 0
    )


@router.get("/search", response_model=List[PublisherResponse])
async def search_publishers(
    query: str = "",
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Search publishers by name."""
    if not query:
        return []
    
    search_pattern = f"%{query}%"
    result = await db.execute(
        select(Publisher, func.count(Book.id).label("book_count"))
        .outerjoin(Book)
        .where(
            Publisher.name.ilike(search_pattern) | 
            Publisher.name_th.ilike(search_pattern)
        )
        .group_by(Publisher.id)
        .order_by(Publisher.name.asc())
        .limit(limit)
    )
    rows = result.all()
    
    return [
        PublisherResponse(
            id=publisher.id,
            name=publisher.name,
            name_th=publisher.name_th,
            description=publisher.description,
            description_th=publisher.description_th,
            website_url=publisher.website_url,
            logo_url=publisher.logo_url,
            created_at=publisher.created_at,
            book_count=count
        )
        for publisher, count in rows
    ]


@router.get("/{publisher_id}", response_model=PublisherResponse)
async def get_publisher_by_id(
    publisher_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """Get a publisher by ID."""
    result = await db.execute(
        select(Publisher, func.count(Book.id).label("book_count"))
        .outerjoin(Book)
        .where(Publisher.id == publisher_id)
        .group_by(Publisher.id)
    )
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publisher not found"
        )
    
    publisher, count = row
    return PublisherResponse(
        id=publisher.id,
        name=publisher.name,
        name_th=publisher.name_th,
        description=publisher.description,
        description_th=publisher.description_th,
        website_url=publisher.website_url,
        logo_url=publisher.logo_url,
        created_at=publisher.created_at,
        book_count=count
    )


@router.get("/{publisher_id}/books", response_model=dict)
async def get_publisher_books(
    publisher_id: UUID,
    page: int = 1,
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get books by a publisher."""
    # Check if publisher exists
    result = await db.execute(
        select(Publisher, func.count(Book.id).label("book_count"))
        .outerjoin(Book)
        .where(Publisher.id == publisher_id)
        .group_by(Publisher.id)
    )
    row = result.one_or_none()
    
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publisher not found"
        )
    
    publisher, count = row
    
    # Get books
    offset = (page - 1) * limit
    books_result = await db.execute(
        select(Book)
        .where(Book.publisher_id == publisher_id)
        .order_by(Book.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    books = books_result.scalars().all()
    
    return {
        "publisher": PublisherResponse(
            id=publisher.id,
            name=publisher.name,
            name_th=publisher.name_th,
            description=publisher.description,
            description_th=publisher.description_th,
            website_url=publisher.website_url,
            logo_url=publisher.logo_url,
            created_at=publisher.created_at,
            book_count=count
        ),
        "books": [BookResponse.model_validate(book) for book in books]
    }


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_publisher(
    publisher_data: PublisherCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new publisher (Admin only)."""
    publisher = Publisher(
        name=publisher_data.name,
        name_th=publisher_data.name_th,
        description=publisher_data.description,
        description_th=publisher_data.description_th,
        website_url=publisher_data.website_url,
        logo_url=publisher_data.logo_url
    )
    db.add(publisher)
    await db.commit()
    await db.refresh(publisher)
    
    return {
        "message": "Publisher created successfully",
        "publisher": PublisherResponse(
            id=publisher.id,
            name=publisher.name,
            name_th=publisher.name_th,
            description=publisher.description,
            description_th=publisher.description_th,
            website_url=publisher.website_url,
            logo_url=publisher.logo_url,
            created_at=publisher.created_at,
            book_count=0
        )
    }


@router.put("/{publisher_id}", response_model=dict)
async def update_publisher(
    publisher_id: UUID,
    publisher_data: PublisherUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a publisher (Admin only)."""
    result = await db.execute(select(Publisher).where(Publisher.id == publisher_id))
    publisher = result.scalar_one_or_none()
    
    if not publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publisher not found"
        )
    
    update_data = publisher_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(publisher, field, value)
    
    await db.commit()
    await db.refresh(publisher)
    
    # Get book count
    count_result = await db.execute(
        select(func.count(Book.id)).where(Book.publisher_id == publisher_id)
    )
    book_count = count_result.scalar_one()
    
    return {
        "message": "Publisher updated successfully",
        "publisher": PublisherResponse(
            id=publisher.id,
            name=publisher.name,
            name_th=publisher.name_th,
            description=publisher.description,
            description_th=publisher.description_th,
            website_url=publisher.website_url,
            logo_url=publisher.logo_url,
            created_at=publisher.created_at,
            book_count=book_count
        )
    }


@router.delete("/{publisher_id}", response_model=MessageResponse)
async def delete_publisher(
    publisher_id: UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a publisher (Admin only)."""
    result = await db.execute(select(Publisher).where(Publisher.id == publisher_id))
    publisher = result.scalar_one_or_none()
    
    if not publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publisher not found"
        )
    
    await db.delete(publisher)
    await db.commit()
    
    return MessageResponse(message="Publisher deleted successfully")
