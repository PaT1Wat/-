import logging
import math
import os
from typing import Any, Dict, List, Optional, Set
from uuid import UUID

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from app.config.database import database

# Configure logging
logger = logging.getLogger(__name__)


class RecommendationService:
    def __init__(self):
        self.book_vectors: Dict[str, int] = {}
        self.user_item_matrix: Dict[str, Dict[str, float]] = {}
        self.initialized = False
        self.tfidf_vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.books: List[Dict[str, Any]] = []
        self.user_ids: List[str] = []
        self.book_ids: List[str] = []
        
        # ML hyperparameters - can be overridden via environment variables
        self.learning_rate = float(os.getenv("ML_LEARNING_RATE", "0.01"))
        self.regularization = float(os.getenv("ML_REGULARIZATION", "0.02"))
        self.iterations = int(os.getenv("ML_ITERATIONS", "100"))
        self.random_seed = int(os.getenv("ML_RANDOM_SEED", "42")) if os.getenv("ML_RANDOM_SEED") else None

    async def initialize_tfidf(self) -> None:
        """Initialize TF-IDF vectors for all books."""
        try:
            query = """
                SELECT b.id, b.title, b.title_th, b.description, b.description_th, b.type,
                       COALESCE(
                         (SELECT string_agg(t.name, ' ') FROM book_tags bt JOIN tags t ON bt.tag_id = t.id WHERE bt.book_id = b.id),
                         ''
                       ) as tags
                FROM books b
            """
            result = await database.fetch_all(query=query)
            self.books = [dict(r) for r in result]
            
            if not self.books:
                logger.warning("No books found for TF-IDF initialization")
                return

            # Prepare documents for TF-IDF
            documents = []
            for i, book in enumerate(self.books):
                document = " ".join([
                    str(book.get("title") or ""),
                    str(book.get("title_th") or ""),
                    str(book.get("description") or ""),
                    str(book.get("description_th") or ""),
                    str(book.get("type") or ""),
                    str(book.get("tags") or ""),
                ]).lower()
                documents.append(document)
                self.book_vectors[str(book["id"])] = i

            # Create TF-IDF matrix
            self.tfidf_vectorizer = TfidfVectorizer(
                max_features=5000,
                stop_words="english",
                ngram_range=(1, 2),
            )
            self.tfidf_matrix = self.tfidf_vectorizer.fit_transform(documents)
            self.initialized = True
            
            logger.info(f"TF-IDF initialized with {len(self.books)} books")
        except Exception as e:
            logger.error(f"Error initializing TF-IDF: {e}")

    async def get_content_based_recommendations(
        self, 
        book_id: UUID, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Content-based filtering using TF-IDF + Cosine Similarity."""
        if not self.initialized:
            await self.initialize_tfidf()

        book_id_str = str(book_id)
        if book_id_str not in self.book_vectors:
            return []

        book_index = self.book_vectors[book_id_str]
        
        # Calculate cosine similarity
        if self.tfidf_matrix is None:
            return []
            
        book_vector = self.tfidf_matrix[book_index]
        similarities = cosine_similarity(book_vector, self.tfidf_matrix).flatten()
        
        # Get top similar books (excluding the book itself)
        similar_indices = similarities.argsort()[::-1][1:limit + 1]
        
        result = []
        for idx in similar_indices:
            if similarities[idx] > 0:
                result.append({
                    "bookId": self.books[idx]["id"],
                    "similarity": float(similarities[idx]),
                })
        
        return result

    async def build_user_item_matrix(self) -> None:
        """Build user-item interaction matrix for collaborative filtering."""
        query = """
            SELECT 
                user_id,
                book_id,
                COALESCE(
                    (SELECT rating FROM reviews WHERE user_id = ui.user_id AND book_id = ui.book_id),
                    3
                ) + SUM(interaction_weight) as score
            FROM user_interactions ui
            GROUP BY user_id, book_id
            UNION
            SELECT user_id, book_id, rating as score
            FROM reviews
        """
        result = await database.fetch_all(query=query)
        
        self.user_item_matrix.clear()
        user_ids_set: Set[str] = set()
        book_ids_set: Set[str] = set()
        
        for row in result:
            user_id = str(row["user_id"])
            book_id = str(row["book_id"])
            user_ids_set.add(user_id)
            book_ids_set.add(book_id)
            
            if user_id not in self.user_item_matrix:
                self.user_item_matrix[user_id] = {}
            self.user_item_matrix[user_id][book_id] = float(row["score"])
        
        self.user_ids = list(user_ids_set)
        self.book_ids = list(book_ids_set)

    async def get_knn_recommendations(
        self, 
        user_id: UUID, 
        k: int = 5, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """KNN-based collaborative filtering."""
        await self.build_user_item_matrix()
        
        user_id_str = str(user_id)
        if user_id_str not in self.user_item_matrix:
            return []

        target_user_ratings = self.user_item_matrix[user_id_str]
        similarities = []

        # Find K nearest neighbors
        for other_user_id in self.user_ids:
            if other_user_id == user_id_str:
                continue
            
            other_user_ratings = self.user_item_matrix.get(other_user_id, {})
            if not other_user_ratings:
                continue

            # Calculate similarity based on common items
            common_books = []
            for book_id, rating in target_user_ratings.items():
                if book_id in other_user_ratings:
                    common_books.append({
                        "target_rating": rating,
                        "other_rating": other_user_ratings[book_id],
                    })

            if len(common_books) < 2:
                continue

            # Pearson correlation
            n = len(common_books)
            sum_target = sum(item["target_rating"] for item in common_books)
            sum_other = sum(item["other_rating"] for item in common_books)
            sum_target_sq = sum(item["target_rating"] ** 2 for item in common_books)
            sum_other_sq = sum(item["other_rating"] ** 2 for item in common_books)
            sum_product = sum(item["target_rating"] * item["other_rating"] for item in common_books)

            numerator = n * sum_product - sum_target * sum_other
            denominator = math.sqrt(
                (n * sum_target_sq - sum_target ** 2) * 
                (n * sum_other_sq - sum_other ** 2)
            )

            if denominator > 0:
                similarity = numerator / denominator
                if similarity > 0:
                    similarities.append({"userId": other_user_id, "similarity": similarity})

        # Get top K neighbors
        similarities.sort(key=lambda x: x["similarity"], reverse=True)
        neighbors = similarities[:k]

        if not neighbors:
            return []

        # Predict ratings for unseen books
        predictions: Dict[str, Dict[str, float]] = {}
        target_books = set(target_user_ratings.keys())

        for neighbor in neighbors:
            neighbor_ratings = self.user_item_matrix.get(neighbor["userId"], {})
            for book_id, rating in neighbor_ratings.items():
                if book_id not in target_books:
                    if book_id not in predictions:
                        predictions[book_id] = {"weighted_sum": 0, "similarity_sum": 0}
                    predictions[book_id]["weighted_sum"] += rating * neighbor["similarity"]
                    predictions[book_id]["similarity_sum"] += neighbor["similarity"]

        # Calculate final predictions
        recommendations = []
        for book_id, pred in predictions.items():
            if pred["similarity_sum"] > 0:
                recommendations.append({
                    "bookId": book_id,
                    "predictedRating": pred["weighted_sum"] / pred["similarity_sum"],
                })

        # Sort by predicted rating
        recommendations.sort(key=lambda x: x["predictedRating"], reverse=True)
        return recommendations[:limit]

    async def get_svd_recommendations(
        self, 
        user_id: UUID, 
        factors: int = 10, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Simple SVD-inspired matrix factorization."""
        await self.build_user_item_matrix()
        
        user_id_str = str(user_id)
        if user_id_str not in self.user_item_matrix or len(self.user_ids) < 2:
            return []

        # Build rating matrix
        user_index = {uid: i for i, uid in enumerate(self.user_ids)}
        book_index = {bid: i for i, bid in enumerate(self.book_ids)}

        num_users = len(self.user_ids)
        num_books = len(self.book_ids)

        # Initialize matrix with zeros
        matrix = np.zeros((num_users, num_books))

        # Fill in known ratings
        for uid, ratings in self.user_item_matrix.items():
            u_idx = user_index.get(uid)
            if u_idx is None:
                continue
            for bid, rating in ratings.items():
                b_idx = book_index.get(bid)
                if b_idx is not None:
                    matrix[u_idx, b_idx] = rating

        # Simple gradient descent for matrix factorization
        # Use configurable hyperparameters from instance
        learning_rate = self.learning_rate
        regularization = self.regularization
        iterations = self.iterations

        # Initialize factor matrices with small random values
        if self.random_seed is not None:
            np.random.seed(self.random_seed)
        user_factors = np.random.rand(num_users, factors) * 0.1
        book_factors = np.random.rand(num_books, factors) * 0.1

        # Training
        for _ in range(iterations):
            for u in range(num_users):
                for b in range(num_books):
                    if matrix[u, b] > 0:
                        prediction = np.dot(user_factors[u], book_factors[b])
                        error = matrix[u, b] - prediction
                        
                        user_factors[u] += learning_rate * (
                            error * book_factors[b] - regularization * user_factors[u]
                        )
                        book_factors[b] += learning_rate * (
                            error * user_factors[u] - regularization * book_factors[b]
                        )

        # Generate predictions for target user
        target_user_idx = user_index.get(user_id_str)
        if target_user_idx is None:
            return []
            
        target_user_ratings = self.user_item_matrix.get(user_id_str, {})
        recommendations = []

        for bid, b_idx in book_index.items():
            if bid not in target_user_ratings:
                prediction = float(np.dot(user_factors[target_user_idx], book_factors[b_idx]))
                recommendations.append({"bookId": bid, "predictedRating": prediction})

        recommendations.sort(key=lambda x: x["predictedRating"], reverse=True)
        return recommendations[:limit]

    async def get_hybrid_recommendations(
        self, 
        user_id: UUID, 
        book_id: Optional[UUID] = None, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Hybrid recommendation combining content-based and collaborative filtering."""
        recommendations: Dict[str, Dict[str, Any]] = {}
        weights = {
            "content_based": 0.3,
            "knn": 0.4,
            "svd": 0.3,
        }

        try:
            # Get content-based recommendations if book is provided
            if book_id:
                content_recs = await self.get_content_based_recommendations(book_id, limit * 2)
                for rec in content_recs:
                    bid = str(rec["bookId"])
                    if bid not in recommendations:
                        recommendations[bid] = {"bookId": bid, "score": 0}
                    recommendations[bid]["score"] += rec["similarity"] * weights["content_based"]

            # Get KNN-based recommendations
            knn_recs = await self.get_knn_recommendations(user_id, 5, limit * 2)
            for rec in knn_recs:
                bid = str(rec["bookId"])
                if bid not in recommendations:
                    recommendations[bid] = {"bookId": bid, "score": 0}
                recommendations[bid]["score"] += (rec["predictedRating"] / 5) * weights["knn"]

            # Get SVD-based recommendations
            svd_recs = await self.get_svd_recommendations(user_id, 10, limit * 2)
            for rec in svd_recs:
                bid = str(rec["bookId"])
                if bid not in recommendations:
                    recommendations[bid] = {"bookId": bid, "score": 0}
                recommendations[bid]["score"] += (rec["predictedRating"] / 5) * weights["svd"]

        except Exception as e:
            logger.error(f"Error in hybrid recommendations: {e}")

        # Sort by combined score
        sorted_recs = sorted(
            recommendations.values(), 
            key=lambda x: x["score"], 
            reverse=True
        )[:limit]

        # Fetch book details
        if sorted_recs:
            book_ids = [r["bookId"] for r in sorted_recs]
            query = """
                SELECT b.*, a.name as author_name, a.name_th as author_name_th
                FROM books b
                LEFT JOIN authors a ON b.author_id = a.id
                WHERE b.id = ANY(:book_ids)
            """
            result = await database.fetch_all(query=query, values={"book_ids": book_ids})
            
            book_map = {str(r["id"]): dict(r) for r in result}
            return [
                {**book_map.get(rec["bookId"], {}), "recommendationScore": rec["score"]}
                for rec in sorted_recs
                if rec["bookId"] in book_map
            ]

        return []

    async def get_personalized_recommendations(
        self, 
        user_id: UUID, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get personalized recommendations based on user behavior."""
        preferences_query = """
            SELECT 
                t.id, t.name, t.category,
                SUM(ui.interaction_weight) as preference_score
            FROM user_interactions ui
            JOIN book_tags bt ON ui.book_id = bt.book_id
            JOIN tags t ON bt.tag_id = t.id
            WHERE ui.user_id = :user_id
            GROUP BY t.id, t.name, t.category
            ORDER BY preference_score DESC
            LIMIT 5
        """
        pref_result = await database.fetch_all(
            query=preferences_query, 
            values={"user_id": str(user_id)}
        )
        
        if not pref_result:
            # Return popular books for new users
            return await self.get_popular_books(limit)

        preferred_tags = [str(r["id"]) for r in pref_result]
        
        # Get books user hasn't interacted with but match preferences
        query = """
            SELECT DISTINCT b.*, a.name as author_name, a.name_th as author_name_th,
                   COUNT(bt.tag_id) as matching_tags
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            JOIN book_tags bt ON b.id = bt.book_id
            WHERE bt.tag_id = ANY(:preferred_tags)
              AND b.id NOT IN (
                SELECT book_id FROM user_interactions WHERE user_id = :user_id
                UNION
                SELECT book_id FROM reviews WHERE user_id = :user_id
                UNION
                SELECT book_id FROM favorites WHERE user_id = :user_id
              )
            GROUP BY b.id, a.name, a.name_th
            ORDER BY matching_tags DESC, b.average_rating DESC
            LIMIT :limit
        """
        
        result = await database.fetch_all(
            query=query, 
            values={"preferred_tags": preferred_tags, "user_id": str(user_id), "limit": limit}
        )
        return [dict(r) for r in result]

    async def get_popular_books(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get popular books for cold start."""
        query = """
            SELECT b.*, a.name as author_name, a.name_th as author_name_th
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            ORDER BY b.average_rating DESC, b.total_reviews DESC, b.view_count DESC
            LIMIT :limit
        """
        result = await database.fetch_all(query=query, values={"limit": limit})
        return [dict(r) for r in result]

    async def get_similar_books_by_tags(
        self, 
        book_id: UUID, 
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Get similar books based on tags."""
        query = """
            WITH book_tags_list AS (
                SELECT tag_id FROM book_tags WHERE book_id = :book_id
            )
            SELECT b.*, a.name as author_name, a.name_th as author_name_th,
                   COUNT(bt.tag_id) as common_tags
            FROM books b
            LEFT JOIN authors a ON b.author_id = a.id
            JOIN book_tags bt ON b.id = bt.book_id
            WHERE bt.tag_id IN (SELECT tag_id FROM book_tags_list)
              AND b.id != :book_id
            GROUP BY b.id, a.name, a.name_th
            ORDER BY common_tags DESC, b.average_rating DESC
            LIMIT :limit
        """
        result = await database.fetch_all(
            query=query, 
            values={"book_id": str(book_id), "limit": limit}
        )
        return [dict(r) for r in result]


# Export singleton instance
recommendation_service = RecommendationService()
