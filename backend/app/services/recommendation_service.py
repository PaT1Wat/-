from typing import List, Dict, Optional, Tuple
from uuid import UUID
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse.linalg import svds
from scipy.linalg import LinAlgError
from sqlalchemy import select, func, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Book, User, Review, UserInteraction, Tag, BookTag


logger = logging.getLogger(__name__)


class RecommendationService:
    def __init__(self):
        self.tfidf_vectorizer = TfidfVectorizer(stop_words='english', max_features=5000)
        self.book_vectors = None
        self.book_ids: List[UUID] = []
        self.initialized = False
    
    async def initialize_tfidf(self, db: AsyncSession) -> None:
        """Initialize TF-IDF vectors for all books."""
        result = await db.execute(
            select(Book).options(selectinload(Book.tags))
        )
        books = result.scalars().all()
        
        if not books:
            return
        
        documents = []
        self.book_ids = []
        
        for book in books:
            # Combine all text features for TF-IDF
            tags_text = " ".join([tag.name for tag in book.tags]) if book.tags else ""
            document = " ".join(filter(None, [
                book.title or "",
                book.title_th or "",
                book.description or "",
                book.description_th or "",
                book.type or "",
                tags_text
            ])).lower()
            
            documents.append(document)
            self.book_ids.append(book.id)
        
        if documents:
            self.book_vectors = self.tfidf_vectorizer.fit_transform(documents)
            self.initialized = True
            logger.info(f"TF-IDF initialized with {len(books)} books")
    
    async def get_content_based_recommendations(
        self, 
        db: AsyncSession, 
        book_id: UUID, 
        limit: int = 10
    ) -> List[Tuple[UUID, float]]:
        """Get content-based recommendations using TF-IDF + Cosine Similarity."""
        if not self.initialized:
            await self.initialize_tfidf(db)
        
        if not self.initialized or book_id not in self.book_ids:
            return []
        
        book_index = self.book_ids.index(book_id)
        book_vector = self.book_vectors[book_index]
        
        # Calculate cosine similarity with all other books
        similarities = cosine_similarity(book_vector, self.book_vectors).flatten()
        
        # Get top similar books (excluding the book itself)
        similar_indices = similarities.argsort()[::-1][1:limit + 1]
        
        return [
            (self.book_ids[idx], float(similarities[idx]))
            for idx in similar_indices
            if similarities[idx] > 0
        ]
    
    async def build_user_item_matrix(
        self, 
        db: AsyncSession
    ) -> Tuple[np.ndarray, List[UUID], List[UUID]]:
        """Build user-item interaction matrix for collaborative filtering."""
        # Get all reviews
        reviews_result = await db.execute(select(Review))
        reviews = reviews_result.scalars().all()
        
        # Get all interactions
        interactions_result = await db.execute(select(UserInteraction))
        interactions = interactions_result.scalars().all()
        
        # Collect unique users and books
        user_ids = list(set([r.user_id for r in reviews] + [i.user_id for i in interactions]))
        book_ids = list(set([r.book_id for r in reviews] + [i.book_id for i in interactions]))
        
        if not user_ids or not book_ids:
            return np.array([]), [], []
        
        user_index = {uid: idx for idx, uid in enumerate(user_ids)}
        book_index = {bid: idx for idx, bid in enumerate(book_ids)}
        
        # Build matrix
        matrix = np.zeros((len(user_ids), len(book_ids)))
        
        # Add reviews (with rating as score)
        for review in reviews:
            if review.rating:
                u_idx = user_index[review.user_id]
                b_idx = book_index[review.book_id]
                matrix[u_idx, b_idx] = review.rating
        
        # Add interactions (weighted)
        for interaction in interactions:
            u_idx = user_index[interaction.user_id]
            b_idx = book_index[interaction.book_id]
            if matrix[u_idx, b_idx] == 0:
                matrix[u_idx, b_idx] = 3 + float(interaction.interaction_weight)
            else:
                matrix[u_idx, b_idx] += float(interaction.interaction_weight)
        
        return matrix, user_ids, book_ids
    
    async def get_knn_recommendations(
        self, 
        db: AsyncSession, 
        user_id: UUID, 
        k: int = 5, 
        limit: int = 10
    ) -> List[Tuple[UUID, float]]:
        """Get KNN-based collaborative filtering recommendations."""
        matrix, user_ids, book_ids = await self.build_user_item_matrix(db)
        
        if len(matrix) == 0 or user_id not in user_ids:
            return []
        
        user_index = user_ids.index(user_id)
        target_ratings = matrix[user_index]
        
        # Calculate similarities with other users (Pearson correlation)
        similarities = []
        for idx, other_ratings in enumerate(matrix):
            if idx == user_index:
                continue
            
            # Find common items
            common_mask = (target_ratings > 0) & (other_ratings > 0)
            if common_mask.sum() < 2:
                continue
            
            target_common = target_ratings[common_mask]
            other_common = other_ratings[common_mask]
            
            # Calculate Pearson correlation
            if np.std(target_common) > 0 and np.std(other_common) > 0:
                correlation = np.corrcoef(target_common, other_common)[0, 1]
                if correlation > 0:
                    similarities.append((idx, correlation))
        
        if not similarities:
            return []
        
        # Get top K neighbors
        similarities.sort(key=lambda x: x[1], reverse=True)
        neighbors = similarities[:k]
        
        # Predict ratings for unseen books
        predictions = {}
        rated_books = set(np.where(target_ratings > 0)[0])
        
        for neighbor_idx, similarity in neighbors:
            for book_idx, rating in enumerate(matrix[neighbor_idx]):
                if rating > 0 and book_idx not in rated_books:
                    if book_idx not in predictions:
                        predictions[book_idx] = {"weighted_sum": 0, "similarity_sum": 0}
                    predictions[book_idx]["weighted_sum"] += rating * similarity
                    predictions[book_idx]["similarity_sum"] += similarity
        
        # Calculate final predictions
        recommendations = []
        for book_idx, pred in predictions.items():
            if pred["similarity_sum"] > 0:
                predicted_rating = pred["weighted_sum"] / pred["similarity_sum"]
                recommendations.append((book_ids[book_idx], predicted_rating))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:limit]
    
    async def get_svd_recommendations(
        self, 
        db: AsyncSession, 
        user_id: UUID, 
        factors: int = 10, 
        limit: int = 10
    ) -> List[Tuple[UUID, float]]:
        """Get SVD-based matrix factorization recommendations."""
        matrix, user_ids, book_ids = await self.build_user_item_matrix(db)
        
        if len(matrix) == 0 or user_id not in user_ids:
            return []
        
        if matrix.shape[0] < 2 or matrix.shape[1] < 2:
            return []
        
        user_index = user_ids.index(user_id)
        
        # Adjust factors based on matrix size
        k = min(factors, min(matrix.shape) - 1)
        if k < 1:
            return []
        
        # SVD decomposition
        try:
            U, sigma, Vt = svds(matrix.astype(float), k=k)
            sigma_diag = np.diag(sigma)
            predicted_ratings = np.dot(np.dot(U, sigma_diag), Vt)
        except (LinAlgError, ValueError) as e:
            logger.warning(f"SVD decomposition failed: {e}")
            return []
        
        # Get predictions for target user
        user_predictions = predicted_ratings[user_index]
        rated_mask = matrix[user_index] > 0
        
        # Filter out already rated books
        recommendations = []
        for idx, (book_id, prediction) in enumerate(zip(book_ids, user_predictions)):
            if not rated_mask[idx]:
                recommendations.append((book_id, float(prediction)))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:limit]
    
    async def get_hybrid_recommendations(
        self, 
        db: AsyncSession, 
        user_id: UUID, 
        book_id: Optional[UUID] = None, 
        limit: int = 10
    ) -> List[Dict]:
        """Get hybrid recommendations combining content-based and collaborative filtering."""
        weights = {
            "content_based": 0.3,
            "knn": 0.4,
            "svd": 0.3
        }
        
        recommendations: Dict[UUID, float] = {}
        
        # Get content-based recommendations if book is provided
        if book_id:
            content_recs = await self.get_content_based_recommendations(db, book_id, limit * 2)
            for rec_book_id, similarity in content_recs:
                recommendations[rec_book_id] = recommendations.get(rec_book_id, 0) + similarity * weights["content_based"]
        
        # Get KNN-based recommendations
        knn_recs = await self.get_knn_recommendations(db, user_id, 5, limit * 2)
        for rec_book_id, predicted_rating in knn_recs:
            recommendations[rec_book_id] = recommendations.get(rec_book_id, 0) + (predicted_rating / 5) * weights["knn"]
        
        # Get SVD-based recommendations
        svd_recs = await self.get_svd_recommendations(db, user_id, 10, limit * 2)
        for rec_book_id, predicted_rating in svd_recs:
            recommendations[rec_book_id] = recommendations.get(rec_book_id, 0) + (predicted_rating / 5) * weights["svd"]
        
        # Sort and get top recommendations
        sorted_recs = sorted(recommendations.items(), key=lambda x: x[1], reverse=True)[:limit]
        
        if not sorted_recs:
            return []
        
        # Fetch book details
        book_ids_to_fetch = [rec[0] for rec in sorted_recs]
        result = await db.execute(
            select(Book)
            .options(selectinload(Book.author), selectinload(Book.tags))
            .where(Book.id.in_(book_ids_to_fetch))
        )
        books = {book.id: book for book in result.scalars().all()}
        
        return [
            {
                "book": books.get(book_id),
                "recommendation_score": score
            }
            for book_id, score in sorted_recs
            if book_id in books
        ]
    
    async def get_personalized_recommendations(
        self, 
        db: AsyncSession, 
        user_id: UUID, 
        limit: int = 10
    ) -> List[Book]:
        """Get personalized recommendations based on user preferences."""
        # Get user's preferred tags based on interactions
        preferences_query = text("""
            SELECT t.id, COUNT(*) as preference_score
            FROM user_interactions ui
            JOIN book_tags bt ON ui.book_id = bt.book_id
            JOIN tags t ON bt.tag_id = t.id
            WHERE ui.user_id = :user_id
            GROUP BY t.id
            ORDER BY preference_score DESC
            LIMIT 5
        """)
        
        result = await db.execute(preferences_query, {"user_id": str(user_id)})
        preferences = result.fetchall()
        
        if not preferences:
            return await self.get_popular_books(db, limit)
        
        preferred_tag_ids = [row[0] for row in preferences]
        
        # Get books matching preferences that user hasn't interacted with
        query = text("""
            SELECT DISTINCT b.id
            FROM books b
            JOIN book_tags bt ON b.id = bt.book_id
            WHERE bt.tag_id = ANY(:tag_ids)
              AND b.id NOT IN (
                SELECT book_id FROM user_interactions WHERE user_id = :user_id
                UNION
                SELECT book_id FROM reviews WHERE user_id = :user_id
                UNION
                SELECT book_id FROM favorites WHERE user_id = :user_id
              )
            ORDER BY b.average_rating DESC
            LIMIT :limit
        """)
        
        result = await db.execute(
            query, 
            {"tag_ids": preferred_tag_ids, "user_id": str(user_id), "limit": limit}
        )
        book_ids = [row[0] for row in result.fetchall()]
        
        if not book_ids:
            return await self.get_popular_books(db, limit)
        
        # Fetch full book details
        books_result = await db.execute(
            select(Book)
            .options(selectinload(Book.author), selectinload(Book.tags))
            .where(Book.id.in_(book_ids))
        )
        
        return list(books_result.scalars().all())
    
    async def get_popular_books(self, db: AsyncSession, limit: int = 10) -> List[Book]:
        """Get popular books for cold start."""
        result = await db.execute(
            select(Book)
            .options(selectinload(Book.author), selectinload(Book.tags))
            .order_by(Book.average_rating.desc(), Book.total_reviews.desc(), Book.view_count.desc())
            .limit(limit)
        )
        return list(result.scalars().all())
    
    async def get_similar_books_by_tags(
        self, 
        db: AsyncSession, 
        book_id: UUID, 
        limit: int = 10
    ) -> List[Book]:
        """Get similar books based on shared tags."""
        query = text("""
            WITH book_tags_list AS (
                SELECT tag_id FROM book_tags WHERE book_id = :book_id
            )
            SELECT b.id, COUNT(bt.tag_id) as common_tags
            FROM books b
            JOIN book_tags bt ON b.id = bt.book_id
            WHERE bt.tag_id IN (SELECT tag_id FROM book_tags_list)
              AND b.id != :book_id
            GROUP BY b.id
            ORDER BY common_tags DESC, b.average_rating DESC
            LIMIT :limit
        """)
        
        result = await db.execute(query, {"book_id": str(book_id), "limit": limit})
        book_ids = [row[0] for row in result.fetchall()]
        
        if not book_ids:
            return []
        
        # Fetch full book details
        books_result = await db.execute(
            select(Book)
            .options(selectinload(Book.author), selectinload(Book.tags))
            .where(Book.id.in_(book_ids))
        )
        
        return list(books_result.scalars().all())


# Singleton instance
recommendation_service = RecommendationService()
