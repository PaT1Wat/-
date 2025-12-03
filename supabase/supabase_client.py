"""
Supabase Python Client Example

This module demonstrates how to configure and use the Supabase Python client
for database operations, authentication, and storage.

Requirements:
    pip install supabase python-dotenv

Usage:
    from supabase.supabase_client import get_client, fetch_books, create_review
    
    # Get the client
    client = get_client()
    
    # Use helper functions
    books = fetch_books(limit=10)
    review = create_review(user_id, book_id, rating=5, content="Great book!")

Security Notes:
    - SUPABASE_ANON_KEY: Safe for client-side, respects RLS
    - SUPABASE_SERVICE_ROLE_KEY: Server-side only, bypasses RLS
    - Never expose the service role key to frontend code!
"""

import os
from typing import Optional, List, Dict, Any
from functools import lru_cache

# Optional: Load from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


def _get_env(name: str, required: bool = True) -> Optional[str]:
    """Get environment variable with optional requirement check."""
    value = os.getenv(name)
    if required and not value:
        raise ValueError(
            f"Missing required environment variable: {name}. "
            "Set it in your .env file or environment."
        )
    return value


@lru_cache(maxsize=1)
def get_client():
    """
    Get Supabase client using the anon key.
    
    This client respects Row Level Security (RLS) policies and is safe
    for user-facing operations.
    
    Returns:
        Supabase client instance
        
    Example:
        client = get_client()
        response = client.table("books").select("*").limit(10).execute()
        books = response.data
    """
    try:
        from supabase import create_client, Client
    except ImportError:
        raise ImportError(
            "The 'supabase' package is required. "
            "Install it with: pip install supabase"
        )
    
    url = _get_env("SUPABASE_URL")
    anon_key = _get_env("SUPABASE_ANON_KEY")
    
    return create_client(url, anon_key)


@lru_cache(maxsize=1)
def get_admin_client():
    """
    Get Supabase client using the service role key.
    
    WARNING: This client bypasses Row Level Security!
    Use only for server-side admin operations.
    
    Returns:
        Supabase admin client instance
    """
    try:
        from supabase import create_client, Client
    except ImportError:
        raise ImportError(
            "The 'supabase' package is required. "
            "Install it with: pip install supabase"
        )
    
    url = _get_env("SUPABASE_URL")
    service_role_key = _get_env("SUPABASE_SERVICE_ROLE_KEY")
    
    return create_client(url, service_role_key)


# ============================================================================
# Example CRUD Operations
# ============================================================================
# These functions demonstrate common patterns. Adapt table names and columns
# to match your actual schema.

def fetch_books(
    limit: int = 10,
    offset: int = 0,
    book_type: Optional[str] = None,
    status: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Fetch books from the database with optional filters.
    
    Args:
        limit: Maximum number of books to return
        offset: Number of books to skip (for pagination)
        book_type: Filter by type (manga, novel, etc.)
        status: Filter by status (ongoing, completed, etc.)
        
    Returns:
        List of book dictionaries
        
    Example:
        # Get first 10 manga
        manga = fetch_books(limit=10, book_type="manga")
        
        # Get completed novels
        novels = fetch_books(book_type="novel", status="completed")
    """
    client = get_client()
    
    query = client.table("books").select(
        "*",
        "authors(id, name)",
        "publishers(id, name)"
    )
    
    if book_type:
        query = query.eq("type", book_type)
    
    if status:
        query = query.eq("status", status)
    
    response = query.order("created_at", desc=True).range(offset, offset + limit - 1).execute()
    
    return response.data


def get_book_by_id(book_id: str) -> Optional[Dict[str, Any]]:
    """
    Get a single book by its ID.
    
    Args:
        book_id: UUID of the book
        
    Returns:
        Book dictionary or None if not found
    """
    client = get_client()
    
    response = client.table("books").select(
        "*",
        "authors(id, name, biography)",
        "publishers(id, name)",
        "book_tags(tags(id, name))"
    ).eq("id", book_id).single().execute()
    
    return response.data


def create_review(
    user_id: str,
    book_id: str,
    rating: int,
    content: str,
    title: Optional[str] = None,
    is_spoiler: bool = False
) -> Dict[str, Any]:
    """
    Create a new review for a book.
    
    Args:
        user_id: UUID of the user creating the review
        book_id: UUID of the book being reviewed
        rating: Rating from 1-5
        content: Review text content
        title: Optional review title
        is_spoiler: Whether the review contains spoilers
        
    Returns:
        The created review data
        
    Raises:
        Exception: If the review already exists (user can only review once per book)
    """
    client = get_client()
    
    review_data = {
        "user_id": user_id,
        "book_id": book_id,
        "rating": rating,
        "content": content,
        "title": title,
        "is_spoiler": is_spoiler
    }
    
    response = client.table("reviews").insert(review_data).execute()
    
    return response.data[0] if response.data else None


def update_review(
    review_id: str,
    user_id: str,
    updates: Dict[str, Any]
) -> Optional[Dict[str, Any]]:
    """
    Update an existing review.
    
    Note: RLS ensures users can only update their own reviews.
    
    Args:
        review_id: UUID of the review
        user_id: UUID of the user (for RLS verification)
        updates: Dictionary of fields to update
        
    Returns:
        Updated review data or None
    """
    client = get_client()
    
    # Only allow updating certain fields
    allowed_fields = {"rating", "content", "title", "is_spoiler"}
    safe_updates = {k: v for k, v in updates.items() if k in allowed_fields}
    
    response = client.table("reviews")\
        .update(safe_updates)\
        .eq("id", review_id)\
        .eq("user_id", user_id)\
        .execute()
    
    return response.data[0] if response.data else None


def delete_review(review_id: str, user_id: str) -> bool:
    """
    Delete a review.
    
    Note: RLS ensures users can only delete their own reviews.
    
    Args:
        review_id: UUID of the review
        user_id: UUID of the user (for RLS verification)
        
    Returns:
        True if deleted, False otherwise
    """
    client = get_client()
    
    response = client.table("reviews")\
        .delete()\
        .eq("id", review_id)\
        .eq("user_id", user_id)\
        .execute()
    
    return len(response.data) > 0


def add_to_favorites(
    user_id: str,
    book_id: str,
    list_name: str = "favorites"
) -> Dict[str, Any]:
    """
    Add a book to user's favorites list.
    
    Args:
        user_id: UUID of the user
        book_id: UUID of the book
        list_name: List type (favorites, reading, completed, plan_to_read, dropped)
        
    Returns:
        The created favorite entry
    """
    client = get_client()
    
    response = client.table("favorites").insert({
        "user_id": user_id,
        "book_id": book_id,
        "list_name": list_name
    }).execute()
    
    return response.data[0] if response.data else None


def get_user_favorites(
    user_id: str,
    list_name: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Get user's favorite books.
    
    Args:
        user_id: UUID of the user
        list_name: Optional filter by list type
        
    Returns:
        List of favorites with book details
    """
    client = get_client()
    
    query = client.table("favorites").select(
        "*",
        "books(id, title, cover_image_url, type, status, average_rating)"
    ).eq("user_id", user_id)
    
    if list_name:
        query = query.eq("list_name", list_name)
    
    response = query.order("created_at", desc=True).execute()
    
    return response.data


# ============================================================================
# File Storage Example
# ============================================================================

def upload_cover_image(
    book_id: str,
    file_data: bytes,
    file_name: str,
    content_type: str = "image/jpeg"
) -> str:
    """
    Upload a book cover image to Supabase Storage.
    
    Args:
        book_id: UUID of the book (used in the file path)
        file_data: Image file content as bytes
        file_name: Original filename
        content_type: MIME type of the file
        
    Returns:
        Public URL of the uploaded image
    """
    client = get_admin_client()  # Using admin client for storage operations
    
    # Create a unique file path
    file_extension = file_name.split(".")[-1] if "." in file_name else "jpg"
    storage_path = f"book-covers/{book_id}.{file_extension}"
    
    # Upload to the 'covers' bucket
    response = client.storage.from_("covers").upload(
        storage_path,
        file_data,
        {"content-type": content_type}
    )
    
    # Get public URL
    public_url = client.storage.from_("covers").get_public_url(storage_path)
    
    return public_url


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Test the client
    try:
        client = get_client()
        print("✓ Supabase client initialized successfully")
        
        # Test a simple query
        # response = client.table("books").select("count", count="exact").execute()
        # print(f"✓ Found {response.count} books in database")
        
    except Exception as e:
        print(f"✗ Error: {e}")
