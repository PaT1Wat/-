from typing import Any, Dict, List, Optional
from uuid import UUID

from app.config.database import database


class Review:
    @staticmethod
    async def create(review_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        query = """
            INSERT INTO reviews (user_id, book_id, rating, title, content, is_spoiler)
            VALUES (:user_id, :book_id, :rating, :title, :content, :is_spoiler)
            RETURNING *
        """
        values = {
            "user_id": str(review_data.get("user_id")),
            "book_id": str(review_data.get("book_id")),
            "rating": review_data.get("rating"),
            "title": review_data.get("title"),
            "content": review_data.get("content"),
            "is_spoiler": review_data.get("is_spoiler", False),
        }
        result = await database.fetch_one(query=query, values=values)
        return dict(result) if result else None

    @staticmethod
    async def find_by_id(review_id: UUID) -> Optional[Dict[str, Any]]:
        query = """
            SELECT r.*, 
                   u.username, u.display_name, u.avatar_url as user_avatar,
                   b.title as book_title, b.title_th as book_title_th
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            JOIN books b ON r.book_id = b.id
            WHERE r.id = :id
        """
        result = await database.fetch_one(query=query, values={"id": str(review_id)})
        return dict(result) if result else None

    @staticmethod
    async def update(review_id: UUID, user_id: UUID, review_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        query = """
            UPDATE reviews 
            SET rating = COALESCE(:rating, rating),
                title = COALESCE(:title, title),
                content = COALESCE(:content, content),
                is_spoiler = COALESCE(:is_spoiler, is_spoiler)
            WHERE id = :id AND user_id = :user_id
            RETURNING *
        """
        values = {
            "id": str(review_id),
            "user_id": str(user_id),
            "rating": review_data.get("rating"),
            "title": review_data.get("title"),
            "content": review_data.get("content"),
            "is_spoiler": review_data.get("is_spoiler"),
        }
        result = await database.fetch_one(query=query, values=values)
        return dict(result) if result else None

    @staticmethod
    async def delete(review_id: UUID, user_id: Optional[UUID] = None) -> Optional[Dict[str, Any]]:
        if user_id:
            query = "DELETE FROM reviews WHERE id = :id AND user_id = :user_id RETURNING *"
            result = await database.fetch_one(
                query=query, 
                values={"id": str(review_id), "user_id": str(user_id)}
            )
        else:
            query = "DELETE FROM reviews WHERE id = :id RETURNING *"
            result = await database.fetch_one(query=query, values={"id": str(review_id)})
        return dict(result) if result else None

    @staticmethod
    async def get_by_book_id(
        book_id: UUID, 
        page: int = 1, 
        limit: int = 10, 
        sort_by: str = "created_at"
    ) -> Dict[str, Any]:
        offset = (page - 1) * limit
        valid_sort_fields = ["created_at", "rating", "helpful_count"]
        sort_field = sort_by if sort_by in valid_sort_fields else "created_at"
        
        query = f"""
            SELECT r.*, 
                   u.username, u.display_name, u.avatar_url as user_avatar
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            WHERE r.book_id = :book_id AND r.is_approved = true
            ORDER BY r.{sort_field} DESC
            LIMIT :limit OFFSET :offset
        """
        count_query = "SELECT COUNT(*) as count FROM reviews WHERE book_id = :book_id AND is_approved = true"
        
        results = await database.fetch_all(
            query=query, 
            values={"book_id": str(book_id), "limit": limit, "offset": offset}
        )
        count_result = await database.fetch_one(query=count_query, values={"book_id": str(book_id)})
        
        total = count_result["count"] if count_result else 0
        return {
            "reviews": [dict(r) for r in results],
            "total": total,
            "page": page,
            "totalPages": (total + limit - 1) // limit if total > 0 else 0,
        }

    @staticmethod
    async def get_by_user_id(user_id: UUID, page: int = 1, limit: int = 10) -> Dict[str, Any]:
        offset = (page - 1) * limit
        query = """
            SELECT r.*, 
                   b.title as book_title, b.title_th as book_title_th, b.cover_image_url
            FROM reviews r
            JOIN books b ON r.book_id = b.id
            WHERE r.user_id = :user_id
            ORDER BY r.created_at DESC
            LIMIT :limit OFFSET :offset
        """
        count_query = "SELECT COUNT(*) as count FROM reviews WHERE user_id = :user_id"
        
        results = await database.fetch_all(
            query=query, 
            values={"user_id": str(user_id), "limit": limit, "offset": offset}
        )
        count_result = await database.fetch_one(query=count_query, values={"user_id": str(user_id)})
        
        total = count_result["count"] if count_result else 0
        return {
            "reviews": [dict(r) for r in results],
            "total": total,
            "page": page,
            "totalPages": (total + limit - 1) // limit if total > 0 else 0,
        }

    @staticmethod
    async def find_by_user_and_book(user_id: UUID, book_id: UUID) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM reviews WHERE user_id = :user_id AND book_id = :book_id"
        result = await database.fetch_one(
            query=query, 
            values={"user_id": str(user_id), "book_id": str(book_id)}
        )
        return dict(result) if result else None

    @staticmethod
    async def increment_helpful(review_id: UUID) -> Optional[Dict[str, Any]]:
        query = "UPDATE reviews SET helpful_count = helpful_count + 1 WHERE id = :id RETURNING *"
        result = await database.fetch_one(query=query, values={"id": str(review_id)})
        return dict(result) if result else None

    @staticmethod
    async def get_pending_reviews(page: int = 1, limit: int = 20) -> Dict[str, Any]:
        offset = (page - 1) * limit
        query = """
            SELECT r.*, 
                   u.username, u.display_name,
                   b.title as book_title
            FROM reviews r
            JOIN users u ON r.user_id = u.id
            JOIN books b ON r.book_id = b.id
            WHERE r.is_approved = false
            ORDER BY r.created_at DESC
            LIMIT :limit OFFSET :offset
        """
        count_query = "SELECT COUNT(*) as count FROM reviews WHERE is_approved = false"
        
        results = await database.fetch_all(query=query, values={"limit": limit, "offset": offset})
        count_result = await database.fetch_one(query=count_query)
        
        total = count_result["count"] if count_result else 0
        return {
            "reviews": [dict(r) for r in results],
            "total": total,
            "page": page,
            "totalPages": (total + limit - 1) // limit if total > 0 else 0,
        }

    @staticmethod
    async def approve(review_id: UUID) -> Optional[Dict[str, Any]]:
        query = "UPDATE reviews SET is_approved = true WHERE id = :id RETURNING *"
        result = await database.fetch_one(query=query, values={"id": str(review_id)})
        return dict(result) if result else None

    @staticmethod
    async def reject(review_id: UUID) -> Optional[Dict[str, Any]]:
        query = "DELETE FROM reviews WHERE id = :id RETURNING *"
        result = await database.fetch_one(query=query, values={"id": str(review_id)})
        return dict(result) if result else None
