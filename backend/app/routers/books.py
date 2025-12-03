from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, func, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.config.database import get_db
from app.middleware.auth import get_optional_user, get_current_user, require_admin
from app.models import Book, Author, Publisher, Tag, BookTag, User, UserInteraction, SearchHistory
from app.schemas import (
    BookCreate, BookUpdate, BookResponse, BookListResponse, BookAutocomplete,
    TagCreate, TagResponse, TagWithCount, MessageResponse
)
from app.services import recommendation_service

# TODO: Supabase Migration
# To migrate database operations to Supabase, import the Supabase client:
# from app.config.supabase_client import get_supabase_client, get_supabase_admin_client
#
# Example Supabase query (replace SQLAlchemy queries):
#   client = get_supabase_client()
#   response = client.table("books").select("*, authors(*), tags(*)").execute()
#   books = response.data
#
# Note: Use get_supabase_admin_client() only for server-side operations
# that need to bypass Row Level Security (RLS).


router = APIRouter(prefix="/books", tags=["Books"])


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
        tags=[TagResponse.model_validate(tag) for tag in book.tags] if book.tags else []
    )


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
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all books with pagination and filtering."""
    offset = (page - 1) * limit
    
    # Build query
    stmt = select(Book).options(
        selectinload(Book.author),
        selectinload(Book.publisher),
        selectinload(Book.tags)
    )
    
    conditions = []
    
    # Full-text search
    if query:
        search_pattern = f"%{query}%"
        conditions.append(
            or_(
                Book.title.ilike(search_pattern),
                Book.title_th.ilike(search_pattern),
                Book.original_title.ilike(search_pattern),
                Book.description.ilike(search_pattern),
                Book.description_th.ilike(search_pattern)
            )
        )
    
    if type:
        conditions.append(Book.type == type)
    
    if status:
        conditions.append(Book.status == status)
    
    if author_id:
        conditions.append(Book.author_id == author_id)
    
    if publisher_id:
        conditions.append(Book.publisher_id == publisher_id)
    
    if min_rating:
        conditions.append(Book.average_rating >= min_rating)
    
    if year_from:
        conditions.append(Book.publication_year >= year_from)
    
    if year_to:
        conditions.append(Book.publication_year <= year_to)
    
    if conditions:
        stmt = stmt.where(and_(*conditions))
    
    # Tag filtering
    if tags:
        tag_list = tags.split(",")
        stmt = stmt.where(
            Book.id.in_(
                select(BookTag.book_id)
                .join(Tag)
                .where(Tag.name.in_(tag_list))
            )
        )
    
    # Sorting
    valid_sort_fields = {
        "average_rating": Book.average_rating,
        "created_at": Book.created_at,
        "title": Book.title,
        "publication_year": Book.publication_year,
        "view_count": Book.view_count,
        "total_reviews": Book.total_reviews
    }
    sort_field = valid_sort_fields.get(sort_by, Book.average_rating)
    
    if sort_order.upper() == "ASC":
        stmt = stmt.order_by(sort_field.asc())
    else:
        stmt = stmt.order_by(sort_field.desc())
    
    stmt = stmt.offset(offset).limit(limit)
    
    result = await db.execute(stmt)
    books = result.scalars().unique().all()
    
    # Count total
    count_stmt = select(func.count(Book.id))
    if conditions:
        count_stmt = count_stmt.where(and_(*conditions))
    count_result = await db.execute(count_stmt)
    total = count_result.scalar_one()
    
    # Save search history if user is authenticated
    if current_user and query:
        search_history = SearchHistory(
            user_id=current_user.id,
            search_query=query,
            filters={"type": type, "status": status, "tags": tags},
            results_count=total
        )
        db.add(search_history)
        await db.commit()
    
    return BookListResponse(
        books=[book_to_response(book) for book in books],
        total=total,
        page=page,
        total_pages=(total + limit - 1) // limit if total > 0 else 0
    )


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
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """Search books with full-text search."""
    return await get_books(
        query=query, type=type, status=status, tags=tags,
        author_id=author_id, publisher_id=publisher_id,
        min_rating=min_rating, year_from=year_from, year_to=year_to,
        sort_by=sort_by, sort_order=sort_order, page=page, limit=limit,
        current_user=current_user, db=db
    )


@router.get("/autocomplete", response_model=List[BookAutocomplete])
async def autocomplete(
    query: str = "",
    db: AsyncSession = Depends(get_db)
):
    """Autocomplete search."""
    if len(query) < 2:
        return []
    
    search_pattern = f"%{query}%"
    result = await db.execute(
        select(Book)
        .where(
            or_(
                Book.title.ilike(search_pattern),
                Book.title_th.ilike(search_pattern),
                Book.original_title.ilike(search_pattern)
            )
        )
        .order_by(Book.view_count.desc(), Book.average_rating.desc())
        .limit(10)
    )
    books = result.scalars().all()
    
    return [
        BookAutocomplete(
            id=book.id,
            title=book.title,
            title_th=book.title_th,
            cover_image_url=book.cover_image_url,
            type=book.type
        )
        for book in books
    ]


@router.get("/popular", response_model=List[BookResponse])
async def get_popular_books(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get popular books."""
    result = await db.execute(
        select(Book)
        .options(selectinload(Book.author), selectinload(Book.tags))
        .order_by(Book.average_rating.desc(), Book.total_reviews.desc())
        .limit(limit)
    )
    books = result.scalars().all()
    return [book_to_response(book) for book in books]


@router.get("/recent", response_model=List[BookResponse])
async def get_recent_books(
    limit: int = 10,
    db: AsyncSession = Depends(get_db)
):
    """Get recently added books."""
    result = await db.execute(
        select(Book)
        .options(selectinload(Book.author), selectinload(Book.tags))
        .order_by(Book.created_at.desc())
        .limit(limit)
    )
    books = result.scalars().all()
    return [book_to_response(book) for book in books]


@router.get("/type/{book_type}", response_model=List[BookResponse])
async def get_books_by_type(
    book_type: str,
    limit: int = 20,
    page: int = 1,
    db: AsyncSession = Depends(get_db)
):
    """Get books by type."""
    offset = (page - 1) * limit
    result = await db.execute(
        select(Book)
        .options(selectinload(Book.author), selectinload(Book.tags))
        .where(Book.type == book_type)
        .order_by(Book.average_rating.desc())
        .offset(offset)
        .limit(limit)
    )
    books = result.scalars().all()
    return [book_to_response(book) for book in books]


@router.get("/tags", response_model=List[TagResponse])
async def get_tags(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get all tags."""
    stmt = select(Tag)
    if category:
        stmt = stmt.where(Tag.category == category)
    stmt = stmt.order_by(Tag.category, Tag.name)
    
    result = await db.execute(stmt)
    tags = result.scalars().all()
    return [TagResponse.model_validate(tag) for tag in tags]


@router.get("/tags/popular", response_model=List[TagWithCount])
async def get_popular_tags(
    limit: int = 20,
    db: AsyncSession = Depends(get_db)
):
    """Get popular tags."""
    result = await db.execute(
        select(Tag, func.count(BookTag.book_id).label("book_count"))
        .outerjoin(BookTag)
        .group_by(Tag.id)
        .order_by(func.count(BookTag.book_id).desc())
        .limit(limit)
    )
    rows = result.all()
    
    return [
        TagWithCount(
            id=tag.id,
            name=tag.name,
            name_th=tag.name_th,
            category=tag.category,
            book_count=count
        )
        for tag, count in rows
    ]


@router.get("/{book_id}", response_model=BookResponse)
async def get_book_by_id(
    book_id: UUID,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a single book by ID."""
    result = await db.execute(
        select(Book)
        .options(
            selectinload(Book.author),
            selectinload(Book.publisher),
            selectinload(Book.tags)
        )
        .where(Book.id == book_id)
    )
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Increment view count
    book.view_count += 1
    await db.commit()
    
    # Record user interaction if authenticated
    if current_user:
        interaction = UserInteraction(
            user_id=current_user.id,
            book_id=book_id,
            interaction_type="view",
            interaction_weight=1.0
        )
        db.add(interaction)
        await db.commit()
    
    return book_to_response(book)


@router.get("/{book_id}/recommendations", response_model=List[BookResponse])
async def get_book_recommendations(
    book_id: UUID,
    limit: int = 10,
    current_user: Optional[User] = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """Get recommendations for a book."""
    # Check if book exists
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Get similar books based on tags
    similar_books = await recommendation_service.get_similar_books_by_tags(db, book_id, limit)
    
    # If user is authenticated, get hybrid recommendations
    if current_user:
        hybrid_recs = await recommendation_service.get_hybrid_recommendations(
            db, current_user.id, book_id, limit
        )
        if hybrid_recs:
            return [
                book_to_response(rec["book"])
                for rec in hybrid_recs
                if rec["book"]
            ]
    
    return [book_to_response(book) for book in similar_books]


@router.post("", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_book(
    book_data: BookCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new book (Admin only)."""
    book = Book(
        title=book_data.title,
        title_th=book_data.title_th,
        original_title=book_data.original_title,
        description=book_data.description,
        description_th=book_data.description_th,
        cover_image_url=book_data.cover_image_url,
        type=book_data.type,
        status=book_data.status,
        publication_year=book_data.publication_year,
        total_chapters=book_data.total_chapters,
        total_volumes=book_data.total_volumes,
        author_id=book_data.author_id,
        publisher_id=book_data.publisher_id
    )
    db.add(book)
    await db.flush()
    
    # Add tags
    if book_data.tags:
        for tag_id in book_data.tags:
            book_tag = BookTag(book_id=book.id, tag_id=tag_id)
            db.add(book_tag)
    
    await db.commit()
    await db.refresh(book)
    
    # Reload with relationships
    result = await db.execute(
        select(Book)
        .options(selectinload(Book.author), selectinload(Book.publisher), selectinload(Book.tags))
        .where(Book.id == book.id)
    )
    book = result.scalar_one()
    
    return {
        "message": "Book created successfully",
        "book": book_to_response(book)
    }


@router.put("/{book_id}", response_model=dict)
async def update_book(
    book_id: UUID,
    book_data: BookUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update a book (Admin only)."""
    result = await db.execute(
        select(Book)
        .options(selectinload(Book.tags))
        .where(Book.id == book_id)
    )
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    # Update fields
    update_data = book_data.model_dump(exclude_unset=True, exclude={"tags"})
    for field, value in update_data.items():
        setattr(book, field, value)
    
    # Update tags if provided
    if book_data.tags is not None:
        # Remove existing tags using ORM approach
        from sqlalchemy import delete as sql_delete
        await db.execute(
            sql_delete(BookTag).where(BookTag.book_id == book_id)
        )
        
        # Add new tags
        for tag_id in book_data.tags:
            book_tag = BookTag(book_id=book_id, tag_id=tag_id)
            db.add(book_tag)
    
    await db.commit()
    
    # Reload with relationships
    result = await db.execute(
        select(Book)
        .options(selectinload(Book.author), selectinload(Book.publisher), selectinload(Book.tags))
        .where(Book.id == book_id)
    )
    book = result.scalar_one()
    
    return {
        "message": "Book updated successfully",
        "book": book_to_response(book)
    }


@router.delete("/{book_id}", response_model=MessageResponse)
async def delete_book(
    book_id: UUID,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Delete a book (Admin only)."""
    result = await db.execute(select(Book).where(Book.id == book_id))
    book = result.scalar_one_or_none()
    
    if not book:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Book not found"
        )
    
    await db.delete(book)
    await db.commit()
    
    return MessageResponse(message="Book deleted successfully")


@router.post("/tags", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Create a new tag (Admin only)."""
    tag = Tag(
        name=tag_data.name,
        name_th=tag_data.name_th,
        category=tag_data.category
    )
    db.add(tag)
    await db.commit()
    await db.refresh(tag)
    
    return {
        "message": "Tag created successfully",
        "tag": TagResponse.model_validate(tag)
    }
