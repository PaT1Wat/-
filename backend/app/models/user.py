from typing import Any, Dict, List, Optional
from uuid import UUID

from app.config.database import database


class User:
    @staticmethod
    async def create(user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        query = """
            INSERT INTO users (firebase_uid, email, username, display_name, avatar_url, role, preferred_language)
            VALUES (:firebase_uid, :email, :username, :display_name, :avatar_url, :role, :preferred_language)
            RETURNING *
        """
        values = {
            "firebase_uid": user_data.get("firebase_uid"),
            "email": user_data.get("email"),
            "username": user_data.get("username"),
            "display_name": user_data.get("display_name") or user_data.get("username"),
            "avatar_url": user_data.get("avatar_url"),
            "role": user_data.get("role", "user"),
            "preferred_language": user_data.get("preferred_language", "th"),
        }
        result = await database.fetch_one(query=query, values=values)
        return dict(result) if result else None

    @staticmethod
    async def find_by_id(user_id: UUID) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE id = :id"
        result = await database.fetch_one(query=query, values={"id": str(user_id)})
        return dict(result) if result else None

    @staticmethod
    async def find_by_firebase_uid(firebase_uid: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE firebase_uid = :firebase_uid"
        result = await database.fetch_one(query=query, values={"firebase_uid": firebase_uid})
        return dict(result) if result else None

    @staticmethod
    async def find_by_email(email: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE email = :email"
        result = await database.fetch_one(query=query, values={"email": email})
        return dict(result) if result else None

    @staticmethod
    async def find_by_username(username: str) -> Optional[Dict[str, Any]]:
        query = "SELECT * FROM users WHERE username = :username"
        result = await database.fetch_one(query=query, values={"username": username})
        return dict(result) if result else None

    @staticmethod
    async def update(user_id: UUID, user_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        query = """
            UPDATE users 
            SET display_name = COALESCE(:display_name, display_name),
                avatar_url = COALESCE(:avatar_url, avatar_url),
                preferred_language = COALESCE(:preferred_language, preferred_language)
            WHERE id = :id
            RETURNING *
        """
        values = {
            "id": str(user_id),
            "display_name": user_data.get("display_name"),
            "avatar_url": user_data.get("avatar_url"),
            "preferred_language": user_data.get("preferred_language"),
        }
        result = await database.fetch_one(query=query, values=values)
        return dict(result) if result else None

    @staticmethod
    async def update_role(user_id: UUID, role: str) -> Optional[Dict[str, Any]]:
        query = "UPDATE users SET role = :role WHERE id = :id RETURNING *"
        result = await database.fetch_one(query=query, values={"id": str(user_id), "role": role})
        return dict(result) if result else None

    @staticmethod
    async def delete(user_id: UUID) -> Optional[Dict[str, Any]]:
        query = "DELETE FROM users WHERE id = :id RETURNING *"
        result = await database.fetch_one(query=query, values={"id": str(user_id)})
        return dict(result) if result else None

    @staticmethod
    async def get_all(page: int = 1, limit: int = 20) -> Dict[str, Any]:
        offset = (page - 1) * limit
        query = """
            SELECT id, email, username, display_name, avatar_url, role, created_at
            FROM users 
            ORDER BY created_at DESC 
            LIMIT :limit OFFSET :offset
        """
        count_query = "SELECT COUNT(*) as count FROM users"
        
        results = await database.fetch_all(query=query, values={"limit": limit, "offset": offset})
        count_result = await database.fetch_one(query=count_query)
        
        total = count_result["count"] if count_result else 0
        return {
            "users": [dict(r) for r in results],
            "total": total,
            "page": page,
            "totalPages": (total + limit - 1) // limit if total > 0 else 0,
        }
