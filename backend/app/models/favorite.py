from typing import Any, Dict, List, Optional
from uuid import UUID

from app.config.database import database


class Favorite:
    @staticmethod
    async def add(user_id: UUID, book_id: UUID, list_name: str = "favorites") -> Optional[Dict[str, Any]]:
        query = """
            INSERT INTO favorites (user_id, book_id, list_name)
            VALUES (:user_id, :book_id, :list_name)
            ON CONFLICT (user_id, book_id, list_name) DO NOTHING
            RETURNING *
        """
        result = await database.fetch_one(
            query=query, 
            values={"user_id": str(user_id), "book_id": str(book_id), "list_name": list_name}
        )
        return dict(result) if result else None

    @staticmethod
    async def remove(
        user_id: UUID, 
        book_id: UUID, 
        list_name: Optional[str] = None
    ) -> Optional[Dict[str, Any]]:
        if list_name:
            query = """
                DELETE FROM favorites 
                WHERE user_id = :user_id AND book_id = :book_id AND list_name = :list_name
                RETURNING *
            """
            result = await database.fetch_one(
                query=query, 
                values={"user_id": str(user_id), "book_id": str(book_id), "list_name": list_name}
            )
        else:
            query = """
                DELETE FROM favorites 
                WHERE user_id = :user_id AND book_id = :book_id
                RETURNING *
            """
            result = await database.fetch_one(
                query=query, 
                values={"user_id": str(user_id), "book_id": str(book_id)}
            )
        return dict(result) if result else None

    @staticmethod
    async def get_by_user_id(
        user_id: UUID, 
        list_name: Optional[str] = None, 
        page: int = 1, 
        limit: int = 20
    ) -> Dict[str, Any]:
        offset = (page - 1) * limit
        
        if list_name:
            where_clause = "WHERE f.user_id = :user_id AND f.list_name = :list_name"
            count_where = "WHERE user_id = :user_id AND list_name = :list_name"
            values = {"user_id": str(user_id), "list_name": list_name, "limit": limit, "offset": offset}
            count_values = {"user_id": str(user_id), "list_name": list_name}
        else:
            where_clause = "WHERE f.user_id = :user_id"
            count_where = "WHERE user_id = :user_id"
            values = {"user_id": str(user_id), "limit": limit, "offset": offset}
            count_values = {"user_id": str(user_id)}

        query = f"""
            SELECT f.*, 
                   b.title, b.title_th, b.cover_image_url, b.type, b.status,
                   b.average_rating, b.author_id,
                   a.name as author_name, a.name_th as author_name_th
            FROM favorites f
            JOIN books b ON f.book_id = b.id
            LEFT JOIN authors a ON b.author_id = a.id
            {where_clause}
            ORDER BY f.created_at DESC
            LIMIT :limit OFFSET :offset
        """
        count_query = f"SELECT COUNT(*) as count FROM favorites {count_where}"
        
        results = await database.fetch_all(query=query, values=values)
        count_result = await database.fetch_one(query=count_query, values=count_values)
        
        total = count_result["count"] if count_result else 0
        return {
            "favorites": [dict(r) for r in results],
            "total": total,
            "page": page,
            "totalPages": (total + limit - 1) // limit if total > 0 else 0,
        }

    @staticmethod
    async def check_favorite(user_id: UUID, book_id: UUID) -> List[Dict[str, Any]]:
        query = """
            SELECT list_name FROM favorites 
            WHERE user_id = :user_id AND book_id = :book_id
        """
        results = await database.fetch_all(
            query=query, 
            values={"user_id": str(user_id), "book_id": str(book_id)}
        )
        return [dict(r) for r in results]

    @staticmethod
    async def update_list(
        user_id: UUID, 
        book_id: UUID, 
        old_list_name: str, 
        new_list_name: str
    ) -> Optional[Dict[str, Any]]:
        query = """
            UPDATE favorites 
            SET list_name = :new_list_name
            WHERE user_id = :user_id AND book_id = :book_id AND list_name = :old_list_name
            RETURNING *
        """
        result = await database.fetch_one(
            query=query, 
            values={
                "user_id": str(user_id), 
                "book_id": str(book_id), 
                "old_list_name": old_list_name, 
                "new_list_name": new_list_name
            }
        )
        return dict(result) if result else None

    @staticmethod
    async def get_list_counts(user_id: UUID) -> List[Dict[str, Any]]:
        query = """
            SELECT list_name, COUNT(*) as count
            FROM favorites
            WHERE user_id = :user_id
            GROUP BY list_name
        """
        results = await database.fetch_all(query=query, values={"user_id": str(user_id)})
        return [dict(r) for r in results]
