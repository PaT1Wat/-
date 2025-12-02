from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.middleware.auth import get_current_user, get_optional_user, require_admin
from app.models.book import Book
from app.models.tag import Tag
from app.models.search_history import SearchHistory
from app.models.user_interaction import UserInteraction
from app.services.recommendation_service import recommendation_service
from app.schemas.book import (
    BookCreate,
    BookListResponse,
    BookResponse,
    BookUpdate,
    BookAutocompleteResponse,
    TagCreate,
    TagResponse,
    TagWithCount,
)

router = APIRouter()


@router.get("", response_model=BookListResponse)
async def get_books(
    query: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[str] = None,
    author_id: Optional[UUID] = None,
    publisher_id: Optional[UUID] = None,
    min_rating: Optional[float] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    sort_by: str = "average_rating",
    sort_order: str = "DESC",
    page: int = 1,
    limit: int = 20,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Get all books with pagination and filtering."""
    parsed_tags = tags.split(",") if tags else None
    
    result = await Book.search({
        "query": query,
        "type": type,
        "status": status,
        "tags": parsed_tags,
        "author_id": author_id,
        "publisher_id": publisher_id,
        "min_rating": min_rating,
        "year_from": year_from,
        "year_to": year_to,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "page": page,
        "limit": limit,
    })
    return result


@router.get("/search", response_model=BookListResponse)
async def search_books(
    query: Optional[str] = None,
    type: Optional[str] = None,
    status: Optional[str] = None,
    tags: Optional[str] = None,
    author_id: Optional[UUID] = None,
    publisher_id: Optional[UUID] = None,
    min_rating: Optional[float] = None,
    year_from: Optional[int] = None,
    year_to: Optional[int] = None,
    sort_by: str = "average_rating",
    sort_order: str = "DESC",
    page: int = 1,
    limit: int = 20,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Search books with full-text search."""
    parsed_tags = tags.split(",") if tags else None
    
    result = await Book.search({
        "query": query,
        "type": type,
        "status": status,
        "tags": parsed_tags,
        "author_id": author_id,
        "publisher_id": publisher_id,
        "min_rating": min_rating,
        "year_from": year_from,
        "year_to": year_to,
        "sort_by": sort_by,
        "sort_order": sort_order,
        "page": page,
        "limit": limit,
    })
    
    # Save search history if user is authenticated
    if current_user and query:
        await SearchHistory.add(
            current_user["id"],
            query,
            {"type": type, "status": status, "tags": parsed_tags},
            result["total"],
        )
    
    return result


@router.get("/autocomplete", response_model=List[BookAutocompleteResponse])
async def autocomplete(query: Optional[str] = None):
    """Autocomplete search."""
    if not query or len(query) < 2:
        return []
    
    results = await Book.autocomplete(query)
    return results


@router.get("/popular")
async def get_popular_books(limit: int = 10):
    """Get popular books."""
    books = await Book.get_popular(limit)
    return books


@router.get("/recent")
async def get_recent_books(limit: int = 10):
    """Get recent books."""
    books = await Book.get_recent(limit)
    return books


@router.get("/type/{book_type}")
async def get_books_by_type(
    book_type: str,
    limit: int = 20,
    page: int = 1,
):
    """Get books by type."""
    books = await Book.get_by_type(book_type, limit, page)
    return books


@router.get("/tags", response_model=List[TagResponse])
async def get_tags(category: Optional[str] = None):
    """Get all tags."""
    tags = await Tag.get_all(category) if category else await Tag.get_all()
    return tags


@router.get("/tags/popular", response_model=List[TagWithCount])
async def get_popular_tags(limit: int = 20):
    """Get popular tags."""
    tags = await Tag.get_popular(limit)
    return tags


@router.get("/{book_id}", response_model=BookResponse)
async def get_book_by_id(
    book_id: UUID,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Get single book by ID."""
    book = await Book.find_by_id(book_id)
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    
    # Increment view count
    await Book.increment_view_count(book_id)
    
    # Record user interaction if authenticated
    if current_user:
        await UserInteraction.record(current_user["id"], book_id, "view", 1.0)
    
    return book


@router.get("/{book_id}/recommendations")
async def get_book_recommendations(
    book_id: UUID,
    limit: int = 10,
    current_user: Optional[dict] = Depends(get_optional_user),
):
    """Get recommendations for a book."""
    # Check if book exists
    book = await Book.find_by_id(book_id)
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    
    # Get similar books based on tags
    similar = await recommendation_service.get_similar_books_by_tags(book_id, limit)
    
    # If user is authenticated, get hybrid recommendations
    recommendations = similar
    if current_user:
        hybrid_recs = await recommendation_service.get_hybrid_recommendations(
            current_user["id"],
            book_id,
            limit,
        )
        if hybrid_recs:
            recommendations = hybrid_recs
    
    return recommendations


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    current_user: dict = Depends(require_admin),
):
    """Create new book (Admin)."""
    book = await Book.create(book_data.model_dump())
    
    # Add tags if provided
    if book_data.tags and len(book_data.tags) > 0:
        await Book.add_tags(book["id"], book_data.tags)
    
    created_book = await Book.find_by_id(book["id"])
    return {
        "message": "Book created successfully",
        "book": created_book,
    }


@router.put("/{book_id}", response_model=dict)
async def update_book(
    book_id: UUID,
    book_data: BookUpdate,
    current_user: dict = Depends(require_admin),
):
    """Update book (Admin)."""
    existing_book = await Book.find_by_id(book_id)
    if not existing_book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    
    await Book.update(book_id, book_data.model_dump(exclude_unset=True))
    
    # Update tags if provided
    if book_data.tags is not None:
        # Get current tags
        current_tags = [t["id"] for t in (existing_book.get("tags") or [])]
        
        # Remove old tags
        if current_tags:
            await Book.remove_tags(book_id, current_tags)
        
        # Add new tags
        if book_data.tags:
            await Book.add_tags(book_id, book_data.tags)
    
    updated_book = await Book.find_by_id(book_id)
    return {
        "message": "Book updated successfully",
        "book": updated_book,
    }


@router.delete("/{book_id}")
async def delete_book(
    book_id: UUID,
    current_user: dict = Depends(require_admin),
):
    """Delete book (Admin)."""
    book = await Book.delete(book_id)
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found",
        )
    
    return {"message": "Book deleted successfully"}


@router.post("/tags", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    current_user: dict = Depends(require_admin),
):
    """Create tag (Admin)."""
    tag = await Tag.create(tag_data.model_dump())
    return {
        "message": "Tag created successfully",
        "tag": tag,
    }
