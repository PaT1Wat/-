from typing import Any, Dict, List, Optional
from uuid import UUID

from app.config.database import database


class UserInteraction:
    @staticmethod
    async def record(
        user_id: UUID, 
        book_id: UUID, 
        interaction_type: str, 
        weight: float = 1.0
    ) -> Optional[Dict[str, Any]]:
        query = """
            INSERT INTO user_interactions (user_id, book_id, interaction_type, interaction_weight)
            VALUES (:user_id, :book_id, :interaction_type, :weight)
            RETURNING *
        """
        result = await database.fetch_one(
            query=query, 
            values={
                "user_id": str(user_id), 
                "book_id": str(book_id), 
                "interaction_type": interaction_type, 
                "weight": weight
            }
        )
        return dict(result) if result else None

    @staticmethod
    async def get_by_user_id(user_id: UUID, limit: int = 100) -> List[Dict[str, Any]]:
        query = """
            SELECT ui.*, b.title, b.title_th, b.type
            FROM user_interactions ui
            JOIN books b ON ui.book_id = b.id
            WHERE ui.user_id = :user_id
            ORDER BY ui.created_at DESC
            LIMIT :limit
        """
        results = await database.fetch_all(
            query=query, 
            values={"user_id": str(user_id), "limit": limit}
        )
        return [dict(r) for r in results]

    @staticmethod
    async def get_interaction_matrix() -> List[Dict[str, Any]]:
        query = """
            SELECT 
                user_id,
                book_id,
                SUM(interaction_weight) as total_weight
            FROM user_interactions
            GROUP BY user_id, book_id
        """
        results = await database.fetch_all(query=query)
        return [dict(r) for r in results]

    @staticmethod
    async def get_user_preferences(user_id: UUID) -> List[Dict[str, Any]]:
        query = """
            SELECT 
                t.id as tag_id,
                t.name as tag_name,
                t.category,
                SUM(ui.interaction_weight) as preference_score
            FROM user_interactions ui
            JOIN book_tags bt ON ui.book_id = bt.book_id
            JOIN tags t ON bt.tag_id = t.id
            WHERE ui.user_id = :user_id
            GROUP BY t.id, t.name, t.category
            ORDER BY preference_score DESC
        """
        results = await database.fetch_all(query=query, values={"user_id": str(user_id)})
        return [dict(r) for r in results]

    @staticmethod
    async def get_similar_users(user_id: UUID, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            WITH user_books AS (
                SELECT DISTINCT book_id FROM user_interactions WHERE user_id = :user_id
            )
            SELECT 
                ui.user_id,
                COUNT(DISTINCT ui.book_id) as common_books
            FROM user_interactions ui
            JOIN user_books ub ON ui.book_id = ub.book_id
            WHERE ui.user_id != :user_id
            GROUP BY ui.user_id
            ORDER BY common_books DESC
            LIMIT :limit
        """
        results = await database.fetch_all(
            query=query, 
            values={"user_id": str(user_id), "limit": limit}
        )
        return [dict(r) for r in results]
