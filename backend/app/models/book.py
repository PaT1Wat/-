import json
from typing import Any, Dict, List, Optional
from uuid import UUID

from app.config.database import database


class Book:
    @staticmethod
    async def create(book_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        query = """
            INSERT INTO books (
                title, title_th, original_title, description, description_th,
                cover_image_url, type, status, publication_year, total_chapters,
                total_volumes, author_id, publisher_id
            )
            VALUES (
                :title, :title_th, :original_title, :description, :description_th,
                :cover_image_url, :type, :status, :publication_year, :total_chapters,
                :total_volumes, :author_id, :publisher_id
            )
            RETURNING *
        """
        values = {
            "title": book_data.get("title"),
            "title_th": book_data.get("title_th"),
            "original_title": book_data.get("original_title"),
            "description": book_data.get("description"),
            "description_th": book_data.get("description_th"),
            "cover_image_url": book_data.get("cover_image_url"),
            "type": book_data.get("type", "manga"),
            "status": book_data.get("status", "ongoing"),
            "publication_year": book_data.get("publication_year"),
            "total_chapters": book_data.get("total_chapters"),
            "total_volumes": book_data.get("total_volumes"),
            "author_id": str(book_data["author_id"]) if book_data.get("author_id") else None,
            "publisher_id": str(book_data["publisher_id"]) if book_data.get("publisher_id") else None,
        }
        result = await database.fetch_one(query=query, values=values)
        return dict(result) if result else None

    @staticmethod
    async def find_by_id(book_id: UUID) -> Optional[Dict[str, Any]]:
        query = """
            SELECT b.*, 
                   a.name as author_name, a.name_th as author_name_th,
                   p.name as publisher_name, p.name_th as publisher_name_th,
                   COALESCE(
                     (SELECT json_agg(json_build_object('id', t.id, 'name', t.name, 'name_th', t.name_th, 'category', t.category))
                      FROM book_tags bt JOIN tags t ON bt.tag_id = t.id WHERE bt.book_id = b.id),
                     '[]'
                   ) as tags
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            LEFT JOIN publishers p ON b.publisher_id = p.id
            WHERE b.id = :id
        """
        result = await database.fetch_one(query=query, values={"id": str(book_id)})
        if result:
            result_dict = dict(result)
            # Parse tags JSON if it's a string
            if isinstance(result_dict.get("tags"), str):
                result_dict["tags"] = json.loads(result_dict["tags"])
            return result_dict
        return None

    @staticmethod
    async def update(book_id: UUID, book_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        allowed_fields = [
            "title", "title_th", "original_title", "description", "description_th",
            "cover_image_url", "type", "status", "publication_year", "total_chapters",
            "total_volumes", "author_id", "publisher_id"
        ]
        
        fields = []
        values = {"id": str(book_id)}
        
        for field in allowed_fields:
            if field in book_data and book_data[field] is not None:
                fields.append(f"{field} = :{field}")
                value = book_data[field]
                if field in ["author_id", "publisher_id"] and value:
                    value = str(value)
                values[field] = value
        
        if not fields:
            return await Book.find_by_id(book_id)
        
        query = f"UPDATE books SET {', '.join(fields)} WHERE id = :id RETURNING *"
        result = await database.fetch_one(query=query, values=values)
        return dict(result) if result else None

    @staticmethod
    async def delete(book_id: UUID) -> Optional[Dict[str, Any]]:
        query = "DELETE FROM books WHERE id = :id RETURNING *"
        result = await database.fetch_one(query=query, values={"id": str(book_id)})
        return dict(result) if result else None

    @staticmethod
    async def search(search_params: Dict[str, Any]) -> Dict[str, Any]:
        search_query = search_params.get("query")
        book_type = search_params.get("type")
        status = search_params.get("status")
        tags = search_params.get("tags")
        author_id = search_params.get("author_id")
        publisher_id = search_params.get("publisher_id")
        min_rating = search_params.get("min_rating")
        year_from = search_params.get("year_from")
        year_to = search_params.get("year_to")
        sort_by = search_params.get("sort_by", "average_rating")
        sort_order = search_params.get("sort_order", "DESC")
        page = search_params.get("page", 1)
        limit = search_params.get("limit", 20)

        conditions = []
        values = {}
        
        if search_query:
            conditions.append("""(
                b.title ILIKE :search_query OR 
                b.title_th ILIKE :search_query OR 
                b.original_title ILIKE :search_query OR
                b.description ILIKE :search_query OR
                b.description_th ILIKE :search_query
            )""")
            values["search_query"] = f"%{search_query}%"
        
        if book_type:
            conditions.append("b.type = :type")
            values["type"] = book_type
        
        if status:
            conditions.append("b.status = :status")
            values["status"] = status
        
        if author_id:
            conditions.append("b.author_id = :author_id")
            values["author_id"] = str(author_id)
        
        if publisher_id:
            conditions.append("b.publisher_id = :publisher_id")
            values["publisher_id"] = str(publisher_id)
        
        if min_rating:
            conditions.append("b.average_rating >= :min_rating")
            values["min_rating"] = min_rating
        
        if year_from:
            conditions.append("b.publication_year >= :year_from")
            values["year_from"] = year_from
        
        if year_to:
            conditions.append("b.publication_year <= :year_to")
            values["year_to"] = year_to
        
        if tags:
            conditions.append("""
                b.id IN (
                    SELECT bt.book_id FROM book_tags bt 
                    JOIN tags t ON bt.tag_id = t.id 
                    WHERE t.name = ANY(:tags)
                )
            """)
            values["tags"] = tags

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        offset = (page - 1) * limit

        valid_sort_fields = ["average_rating", "created_at", "title", "publication_year", "view_count", "total_reviews"]
        sort_field = sort_by if sort_by in valid_sort_fields else "average_rating"
        sort_dir = "ASC" if sort_order.upper() == "ASC" else "DESC"

        query = f"""
            SELECT b.*, 
                   a.name as author_name, a.name_th as author_name_th,
                   p.name as publisher_name, p.name_th as publisher_name_th,
                   COALESCE(
                     (SELECT json_agg(json_build_object('id', t.id, 'name', t.name, 'name_th', t.name_th))
                      FROM book_tags bt JOIN tags t ON bt.tag_id = t.id WHERE bt.book_id = b.id),
                     '[]'
                   ) as tags
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            LEFT JOIN publishers p ON b.publisher_id = p.id
            {where_clause}
            ORDER BY b.{sort_field} {sort_dir}
            LIMIT :limit OFFSET :offset
        """
        values["limit"] = limit
        values["offset"] = offset

        count_query = f"SELECT COUNT(*) as count FROM books b {where_clause}"
        
        results = await database.fetch_all(query=query, values=values)
        
        # Count query without limit/offset
        count_values = {k: v for k, v in values.items() if k not in ["limit", "offset"]}
        count_result = await database.fetch_one(query=count_query, values=count_values)
        
        total = count_result["count"] if count_result else 0
        
        books = []
        for r in results:
            book = dict(r)
            if isinstance(book.get("tags"), str):
                book["tags"] = json.loads(book["tags"])
            books.append(book)
        
        return {
            "books": books,
            "total": total,
            "page": page,
            "totalPages": (total + limit - 1) // limit if total > 0 else 0,
        }

    @staticmethod
    async def autocomplete(search_query: str, limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            SELECT id, title, title_th, cover_image_url, type
            FROM books
            WHERE title ILIKE :search_query OR title_th ILIKE :search_query OR original_title ILIKE :search_query
            ORDER BY view_count DESC, average_rating DESC
            LIMIT :limit
        """
        results = await database.fetch_all(
            query=query, 
            values={"search_query": f"%{search_query}%", "limit": limit}
        )
        return [dict(r) for r in results]

    @staticmethod
    async def add_tags(book_id: UUID, tag_ids: List[UUID]) -> None:
        for tag_id in tag_ids:
            query = """
                INSERT INTO book_tags (book_id, tag_id)
                VALUES (:book_id, :tag_id)
                ON CONFLICT DO NOTHING
            """
            await database.execute(query=query, values={"book_id": str(book_id), "tag_id": str(tag_id)})

    @staticmethod
    async def remove_tags(book_id: UUID, tag_ids: List[UUID]) -> None:
        for tag_id in tag_ids:
            query = "DELETE FROM book_tags WHERE book_id = :book_id AND tag_id = :tag_id"
            await database.execute(query=query, values={"book_id": str(book_id), "tag_id": str(tag_id)})

    @staticmethod
    async def increment_view_count(book_id: UUID) -> None:
        query = "UPDATE books SET view_count = view_count + 1 WHERE id = :id"
        await database.execute(query=query, values={"id": str(book_id)})

    @staticmethod
    async def get_popular(limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            SELECT b.*, a.name as author_name, a.name_th as author_name_th
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            ORDER BY b.average_rating DESC, b.total_reviews DESC
            LIMIT :limit
        """
        results = await database.fetch_all(query=query, values={"limit": limit})
        return [dict(r) for r in results]

    @staticmethod
    async def get_recent(limit: int = 10) -> List[Dict[str, Any]]:
        query = """
            SELECT b.*, a.name as author_name, a.name_th as author_name_th
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            ORDER BY b.created_at DESC
            LIMIT :limit
        """
        results = await database.fetch_all(query=query, values={"limit": limit})
        return [dict(r) for r in results]

    @staticmethod
    async def get_by_type(book_type: str, limit: int = 20, page: int = 1) -> List[Dict[str, Any]]:
        offset = (page - 1) * limit
        query = """
            SELECT b.*, a.name as author_name, a.name_th as author_name_th
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            WHERE b.type = :type
            ORDER BY b.average_rating DESC
            LIMIT :limit OFFSET :offset
        """
        results = await database.fetch_all(
            query=query, 
            values={"type": book_type, "limit": limit, "offset": offset}
        )
        return [dict(r) for r in results]
