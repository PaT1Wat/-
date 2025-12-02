from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth import require_admin
from app.models.publisher import Publisher
from app.schemas.publisher import (
    PublisherCreate,
    PublisherListResponse,
    PublisherResponse,
    PublisherUpdate,
)

router = APIRouter()


@router.get("", response_model=PublisherListResponse)
async def get_publishers(page: int = 1, limit: int = 20):
    """Get all publishers."""
    return await Publisher.get_all(page, limit)


@router.get("/search")
async def search_publishers(query: Optional[str] = None, limit: int = 10):
    """Search publishers."""
    if not query:
        return []
    
    publishers = await Publisher.search(query, limit)
    return publishers


@router.get("/{publisher_id}", response_model=PublisherResponse)
async def get_publisher_by_id(publisher_id: UUID):
    """Get publisher by ID."""
    publisher = await Publisher.find_by_id(publisher_id)
    
    if not publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publisher not found",
        )
    
    return publisher


@router.get("/{publisher_id}/books")
async def get_publisher_books(
    publisher_id: UUID,
    page: int = 1,
    limit: int = 20,
):
    """Get publisher's books."""
    publisher = await Publisher.find_by_id(publisher_id)
    if not publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publisher not found",
        )
    
    books = await Publisher.get_books(publisher_id, page, limit)
    return {
        "publisher": publisher,
        "books": books,
    }


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_publisher(
    publisher_data: PublisherCreate,
    current_user: dict = Depends(require_admin),
):
    """Create publisher (Admin)."""
    publisher = await Publisher.create(publisher_data.model_dump())
    return {
        "message": "Publisher created successfully",
        "publisher": publisher,
    }


@router.put("/{publisher_id}", response_model=dict)
async def update_publisher(
    publisher_id: UUID,
    publisher_data: PublisherUpdate,
    current_user: dict = Depends(require_admin),
):
    """Update publisher (Admin)."""
    publisher = await Publisher.update(publisher_id, publisher_data.model_dump(exclude_unset=True))
    
    if not publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publisher not found",
        )
    
    return {
        "message": "Publisher updated successfully",
        "publisher": publisher,
    }


@router.delete("/{publisher_id}")
async def delete_publisher(
    publisher_id: UUID,
    current_user: dict = Depends(require_admin),
):
    """Delete publisher (Admin)."""
    publisher = await Publisher.delete(publisher_id)
    
    if not publisher:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Publisher not found",
        )
    
    return {"message": "Publisher deleted successfully"}
