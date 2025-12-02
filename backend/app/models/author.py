from typing import Any, Dict, List, Optional
from uuid import UUID

from app.config.database import database


class Author:
    @staticmethod
    async def create(author_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        query = """
            INSERT INTO authors (name, name_th, biography, biography_th, avatar_url)
            VALUES (:name, :name_th, :biography, :biography_th, :avatar_url)
            RETURNING *
        """
        values = {
            "name": author_data.get("name"),
            "name_th": author_data.get("name_th"),
            "biography": author_data.get("biography"),
            "biography_th": author_data.get("biography_th"),
            "avatar_url": author_data.get("avatar_url"),
        }
        result = await database.fetch_one(query=query, values=values)
        return dict(result) if result else None

    @staticmethod
    async def find_by_id(author_id: UUID) -> Optional[Dict[str, Any]]:
        query = """
            SELECT a.*, 
                   (SELECT COUNT(*) FROM books WHERE author_id = a.id) as book_count
            FROM authors a
            WHERE a.id = :id
        """
        result = await database.fetch_one(query=query, values={"id": str(author_id)})
        return dict(result) if result else None

    @staticmethod
    async def update(author_id: UUID, author_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        query = """
            UPDATE authors 
            SET name = COALESCE(:name, name),
                name_th = COALESCE(:name_th, name_th),
                biography = COALESCE(:biography, biography),
                biography_th = COALESCE(:biography_th, biography_th),
                avatar_url = COALESCE(:avatar_url, avatar_url)
            WHERE id = :id
            RETURNING *
        """
        values = {
            "id": str(author_id),
            "name": author_data.get("name"),
            "name_th": author_data.get("name_th"),
            "biography": author_data.get("biography"),
            "biography_th": author_data.get("biography_th"),
            "avatar_url": author_data.get("avatar_url"),
        }
        result = await database.fetch_one(query=query, values=values)
        return dict(result) if result else None

    @staticmethod
    async def delete(author_id: UUID) -> Optional[Dict[str, Any]]:
        query = "DELETE FROM authors WHERE id = :id RETURNING *"
        result = await database.fetch_one(query=query, values={"id": str(author_id)})
        return dict(result) if result else None

    @staticmethod
    async def get_all(page: int = 1, limit: int = 20) -> Dict[str, Any]:
        offset = (page - 1) * limit
        query = """
            SELECT a.*, 
                   (SELECT COUNT(*) FROM books WHERE author_id = a.id) as book_count
            FROM authors a
            ORDER BY a.name ASC
            LIMIT :limit OFFSET :offset
        """
        count_query = "SELECT COUNT(*) as count FROM authors"
        
        results = await database.fetch_all(query=query, values={"limit": limit, "offset": offset})
        count_result = await database.fetch_one(query=count_query)
        
        total = count_result["count"] if count_result else 0
        return {
            "authors": [dict(r) for r in results],
            "total": total,
            "page": page,
            "totalPages": (total + limit - 1) // limit if total > 0 else 0,
        }

    @staticmethod
    async def search(search_query: str, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            SELECT a.*, 
                   (SELECT COUNT(*) FROM books WHERE author_id = a.id) as book_count
            FROM authors a
            WHERE a.name ILIKE :search_query OR a.name_th ILIKE :search_query
            ORDER BY a.name ASC
            LIMIT :limit
        """
        results = await database.fetch_all(
            query=query, 
            values={"search_query": f"%{search_query}%", "limit": limit}
        )
        return [dict(r) for r in results]

    @staticmethod
    async def get_books(author_id: UUID, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        offset = (page - 1) * limit
        query = """
            SELECT b.*
            FROM books b
            WHERE b.author_id = :author_id
            ORDER BY b.created_at DESC
            LIMIT :limit OFFSET :offset
        """
        results = await database.fetch_all(
            query=query, 
            values={"author_id": str(author_id), "limit": limit, "offset": offset}
        )
        return [dict(r) for r in results]
