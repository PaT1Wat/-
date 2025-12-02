from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.middleware.auth import require_admin
from app.models.author import Author
from app.schemas.author import (
    AuthorCreate,
    AuthorListResponse,
    AuthorResponse,
    AuthorUpdate,
)

router = APIRouter()


@router.get("", response_model=AuthorListResponse)
async def get_authors(page: int = 1, limit: int = 20):
    """Get all authors."""
    return await Author.get_all(page, limit)


@router.get("/search")
async def search_authors(query: Optional[str] = None, limit: int = 10):
    """Search authors."""
    if not query:
        return []
    
    authors = await Author.search(query, limit)
    return authors


@router.get("/{author_id}", response_model=AuthorResponse)
async def get_author_by_id(author_id: UUID):
    """Get author by ID."""
    author = await Author.find_by_id(author_id)
    
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found",
        )
    
    return author


@router.get("/{author_id}/books")
async def get_author_books(
    author_id: UUID,
    page: int = 1,
    limit: int = 20,
):
    """Get author's books."""
    author = await Author.find_by_id(author_id)
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found",
        )
    
    books = await Author.get_books(author_id, page, limit)
    return {
        "author": author,
        "books": books,
    }


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_author(
    author_data: AuthorCreate,
    current_user: dict = Depends(require_admin),
):
    """Create author (Admin)."""
    author = await Author.create(author_data.model_dump())
    return {
        "message": "Author created successfully",
        "author": author,
    }


@router.put("/{author_id}", response_model=dict)
async def update_author(
    author_id: UUID,
    author_data: AuthorUpdate,
    current_user: dict = Depends(require_admin),
):
    """Update author (Admin)."""
    author = await Author.update(author_id, author_data.model_dump(exclude_unset=True))
    
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found",
        )
    
    return {
        "message": "Author updated successfully",
        "author": author,
    }


@router.delete("/{author_id}")
async def delete_author(
    author_id: UUID,
    current_user: dict = Depends(require_admin),
):
    """Delete author (Admin)."""
    author = await Author.delete(author_id)
    
    if not author:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Author not found",
        )
    
    return {"message": "Author deleted successfully"}
