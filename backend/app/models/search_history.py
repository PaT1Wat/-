import json
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.config.database import database


class SearchHistory:
    @staticmethod
    async def add(
        user_id: UUID, 
        search_query: str, 
        filters: Optional[Dict[str, Any]] = None, 
        results_count: int = 0
    ) -> Optional[Dict[str, Any]]:
        query = """
            INSERT INTO search_history (user_id, search_query, filters, results_count)
            VALUES (:user_id, :search_query, :filters, :results_count)
            RETURNING *
        """
        result = await database.fetch_one(
            query=query, 
            values={
                "user_id": str(user_id), 
                "search_query": search_query, 
                "filters": json.dumps(filters) if filters else None, 
                "results_count": results_count
            }
        )
        return dict(result) if result else None

    @staticmethod
    async def get_by_user_id(user_id: UUID, limit: int = 20) -> List[Dict[str, Any]]:
        query = """
            SELECT * FROM search_history
            WHERE user_id = :user_id
            ORDER BY created_at DESC
            LIMIT :limit
        """
        results = await database.fetch_all(
            query=query, 
            values={"user_id": str(user_id), "limit": limit}
        )
        return [dict(r) for r in results]

    @staticmethod
    async def clear_history(user_id: UUID) -> None:
        query = "DELETE FROM search_history WHERE user_id = :user_id"
        await database.execute(query=query, values={"user_id": str(user_id)})

    @staticmethod
    async def get_popular_searches(limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            SELECT search_query, COUNT(*) as search_count
            FROM search_history
            WHERE created_at > NOW() - INTERVAL '30 days'
            GROUP BY search_query
            ORDER BY search_count DESC
            LIMIT :limit
        """
        results = await database.fetch_all(query=query, values={"limit": limit})
        return [dict(r) for r in results]

    @staticmethod
    async def get_suggestions_from_history(
        user_id: UUID, 
        partial_query: str, 
        limit: int = 5
    ) -> List[str]:
        query = """
            SELECT DISTINCT search_query
            FROM search_history
            WHERE user_id = :user_id AND search_query ILIKE :partial_query
            ORDER BY created_at DESC
            LIMIT :limit
        """
        results = await database.fetch_all(
            query=query, 
            values={
                "user_id": str(user_id), 
                "partial_query": f"{partial_query}%", 
                "limit": limit
            }
        )
        return [r["search_query"] for r in results]
