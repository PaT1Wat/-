from typing import Any, Dict, List, Optional
from uuid import UUID

from app.config.database import database


class Publisher:
    @staticmethod
    async def create(publisher_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        query = """
            INSERT INTO publishers (name, name_th, description, description_th, website_url, logo_url)
            VALUES (:name, :name_th, :description, :description_th, :website_url, :logo_url)
            RETURNING *
        """
        values = {
            "name": publisher_data.get("name"),
            "name_th": publisher_data.get("name_th"),
            "description": publisher_data.get("description"),
            "description_th": publisher_data.get("description_th"),
            "website_url": publisher_data.get("website_url"),
            "logo_url": publisher_data.get("logo_url"),
        }
        result = await database.fetch_one(query=query, values=values)
        return dict(result) if result else None

    @staticmethod
    async def find_by_id(publisher_id: UUID) -> Optional[Dict[str, Any]]:
        query = """
            SELECT p.*, 
                   (SELECT COUNT(*) FROM books WHERE publisher_id = p.id) as book_count
            FROM publishers p
            WHERE p.id = :id
        """
        result = await database.fetch_one(query=query, values={"id": str(publisher_id)})
        return dict(result) if result else None

    @staticmethod
    async def update(publisher_id: UUID, publisher_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        query = """
            UPDATE publishers 
            SET name = COALESCE(:name, name),
                name_th = COALESCE(:name_th, name_th),
                description = COALESCE(:description, description),
                description_th = COALESCE(:description_th, description_th),
                website_url = COALESCE(:website_url, website_url),
                logo_url = COALESCE(:logo_url, logo_url)
            WHERE id = :id
            RETURNING *
        """
        values = {
            "id": str(publisher_id),
            "name": publisher_data.get("name"),
            "name_th": publisher_data.get("name_th"),
            "description": publisher_data.get("description"),
            "description_th": publisher_data.get("description_th"),
            "website_url": publisher_data.get("website_url"),
            "logo_url": publisher_data.get("logo_url"),
        }
        result = await database.fetch_one(query=query, values=values)
        return dict(result) if result else None

    @staticmethod
    async def delete(publisher_id: UUID) -> Optional[Dict[str, Any]]:
        query = "DELETE FROM publishers WHERE id = :id RETURNING *"
        result = await database.fetch_one(query=query, values={"id": str(publisher_id)})
        return dict(result) if result else None

    @staticmethod
    async def get_all(page: int = 1, limit: int = 20) -> Dict[str, Any]:
        offset = (page - 1) * limit
        query = """
            SELECT p.*, 
                   (SELECT COUNT(*) FROM books WHERE publisher_id = p.id) as book_count
            FROM publishers p
            ORDER BY p.name ASC
            LIMIT :limit OFFSET :offset
        """
        count_query = "SELECT COUNT(*) as count FROM publishers"
        
        results = await database.fetch_all(query=query, values={"limit": limit, "offset": offset})
        count_result = await database.fetch_one(query=count_query)
        
        total = count_result["count"] if count_result else 0
        return {
            "publishers": [dict(r) for r in results],
            "total": total,
            "page": page,
            "totalPages": (total + limit - 1) // limit if total > 0 else 0,
        }

    @staticmethod
    async def search(search_query: str, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            SELECT p.*, 
                   (SELECT COUNT(*) FROM books WHERE publisher_id = p.id) as book_count
            FROM publishers p
            WHERE p.name ILIKE :search_query OR p.name_th ILIKE :search_query
            ORDER BY p.name ASC
            LIMIT :limit
        """
        results = await database.fetch_all(
            query=query, 
            values={"search_query": f"%{search_query}%", "limit": limit}
        )
        return [dict(r) for r in results]

    @staticmethod
    async def get_books(publisher_id: UUID, page: int = 1, limit: int = 20) -> List[Dict[str, Any]]:
        offset = (page - 1) * limit
        query = """
            SELECT b.*
            FROM books b
            WHERE b.publisher_id = :publisher_id
            ORDER BY b.created_at DESC
            LIMIT :limit OFFSET :offset
        """
        results = await database.fetch_all(
            query=query, 
            values={"publisher_id": str(publisher_id), "limit": limit, "offset": offset}
        )
        return [dict(r) for r in results]
