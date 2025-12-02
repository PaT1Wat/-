from typing import Any, Dict, List, Optional
from uuid import UUID

from app.config.database import database


class Tag:
    @staticmethod
    async def create(tag_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        query = """
            INSERT INTO tags (name, name_th, category)
            VALUES (:name, :name_th, :category)
            RETURNING *
        """
        values = {
            "name": tag_data.get("name"),
            "name_th": tag_data.get("name_th"),
            "category": tag_data.get("category", "genre"),
        }
        result = await database.fetch_one(query=query, values=values)
        return dict(result) if result else None

    @staticmethod
    async def find_by_id(tag_id: UUID) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM tags WHERE id = :id"
        result = await database.fetch_one(query=query, values={"id": str(tag_id)})
        return dict(result) if result else None

    @staticmethod
    async def find_by_name(name: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM tags WHERE name = :name OR name_th = :name"
        result = await database.fetch_one(query=query, values={"name": name})
        return dict(result) if result else None

    @staticmethod
    async def update(tag_id: UUID, tag_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        query = """
            UPDATE tags 
            SET name = COALESCE(:name, name),
                name_th = COALESCE(:name_th, name_th),
                category = COALESCE(:category, category)
            WHERE id = :id
            RETURNING *
        """
        values = {
            "id": str(tag_id),
            "name": tag_data.get("name"),
            "name_th": tag_data.get("name_th"),
            "category": tag_data.get("category"),
        }
        result = await database.fetch_one(query=query, values=values)
        return dict(result) if result else None

    @staticmethod
    async def delete(tag_id: UUID) -> Optional[Dict[str, Any]]:
        query = "DELETE FROM tags WHERE id = :id RETURNING *"
        result = await database.fetch_one(query=query, values={"id": str(tag_id)})
        return dict(result) if result else None

    @staticmethod
    async def get_all(category: Optional[str] = None) -> List[Dict[str, Any]]:
        if category:
            query = "SELECT * FROM tags WHERE category = :category ORDER BY category, name"
            results = await database.fetch_all(query=query, values={"category": category})
        else:
            query = "SELECT * FROM tags ORDER BY category, name"
            results = await database.fetch_all(query=query)
        return [dict(r) for r in results]

    @staticmethod
    async def search(search_query: str, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM tags
            WHERE name ILIKE :search_query OR name_th ILIKE :search_query
            ORDER BY name
            LIMIT :limit
        """
        results = await database.fetch_all(
            query=query, 
            values={"search_query": f"%{search_query}%", "limit": limit}
        )
        return [dict(r) for r in results]

    @staticmethod
    async def get_popular(limit: int = 20) -> List[Dict[str, Any]]:
        query = """
            SELECT t.*, COUNT(bt.book_id) as book_count
            FROM tags t
            LEFT JOIN book_tags bt ON t.id = bt.tag_id
            GROUP BY t.id
            ORDER BY book_count DESC
            LIMIT :limit
        """
        results = await database.fetch_all(query=query, values={"limit": limit})
        return [dict(r) for r in results]

    @staticmethod
    async def get_by_category(category: str) -> List[Dict[str, Any]]:
        query = "SELECT * FROM tags WHERE category = :category ORDER BY name"
        results = await database.fetch_all(query=query, values={"category": category})
        return [dict(r) for r in results]
