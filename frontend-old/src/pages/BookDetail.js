import React, { useState, useEffect, useCallback } from 'react';
import { useParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { useBook, useRecommendations } from '../hooks/useBooks';
import { favoritesAPI, reviewsAPI, recommendationsAPI } from '../services/api';
import BookGrid from '../components/books/BookGrid';
import './BookDetail.css';

const BookDetail = () => {
  const { id } = useParams();
  const { t, i18n } = useTranslation();
  const { isAuthenticated } = useAuth();
  const { book, loading, error } = useBook(id);
  const { recommendations, loading: recsLoading } = useRecommendations(id, 6);
  
  const [favoriteStatus, setFavoriteStatus] = useState({ isFavorite: false, lists: [] });
  const [reviews, setReviews] = useState([]);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [reviewData, setReviewData] = useState({ rating: 5, title: '', content: '', is_spoiler: false });

  const checkFavoriteStatus = useCallback(async () => {
    try {
      const response = await favoritesAPI.check(id);
      setFavoriteStatus(response.data);
    } catch (err) {
      console.error('Error checking favorite:', err);
    }
  }, [id]);

  const recordInteraction = useCallback(async () => {
    try {
      await recommendationsAPI.recordInteraction(id, 'view', 1.0);
    } catch (err) {
      console.error('Error recording interaction:', err);
    }
  }, [id]);

  const fetchReviews = useCallback(async () => {
    try {
      const response = await reviewsAPI.getByBook(id, { limit: 5 });
      setReviews(response.data.reviews);
    } catch (err) {
      console.error('Error fetching reviews:', err);
    }
  }, [id]);

  useEffect(() => {
    if (id && isAuthenticated) {
      checkFavoriteStatus();
      recordInteraction();
    }
    fetchReviews();
  }, [id, isAuthenticated, checkFavoriteStatus, recordInteraction, fetchReviews]);

  const handleFavoriteToggle = async (listName = 'favorites') => {
    if (!isAuthenticated) return;
    
    try {
      if (favoriteStatus.lists.includes(listName)) {
        await favoritesAPI.remove(id, listName);
      } else {
        await favoritesAPI.add(id, listName);
      }
      checkFavoriteStatus();
    } catch (err) {
      console.error('Error toggling favorite:', err);
    }
  };

  const handleReviewSubmit = async (e) => {
    e.preventDefault();
    try {
      await reviewsAPI.create({
        book_id: id,
        ...reviewData
      });
      setShowReviewForm(false);
      setReviewData({ rating: 5, title: '', content: '', is_spoiler: false });
      fetchReviews();
    } catch (err) {
      alert(err.response?.data?.error || 'Error submitting review');
    }
  };

  if (loading) {
    return <div className="loading">{t('common.loading')}</div>;
  }

  if (error || !book) {
    return <div className="error">{t('common.error')}</div>;
  }

  const title = i18n.language === 'th' && book.title_th ? book.title_th : book.title;
  const description = i18n.language === 'th' && book.description_th ? book.description_th : book.description;
  const authorName = i18n.language === 'th' && book.author_name_th ? book.author_name_th : book.author_name;

  return (
    <div className="book-detail-page">
      <div className="book-detail-header">
        <div className="book-cover-large">
          {book.cover_image_url ? (
            <img src={book.cover_image_url} alt={title} />
          ) : (
            <div className="cover-placeholder">📖</div>
          )}
        </div>
        
        <div className="book-info-main">
          <span className={`book-type type-${book.type}`}>{t(`type.${book.type}`)}</span>
          <h1 className="book-title">{title}</h1>
          {book.original_title && book.original_title !== title && (
            <p className="original-title">{book.original_title}</p>
          )}
          
          {authorName && (
            <p className="book-author">
              <strong>{t('book.author')}:</strong> {authorName}
            </p>
          )}
          
          {book.publisher_name && (
            <p className="book-publisher">
              <strong>{t('book.publisher')}:</strong> {book.publisher_name}
            </p>
          )}

          <div className="book-stats">
            <div className="stat">
              <span className="stat-value">⭐ {Number(book.average_rating).toFixed(1)}</span>
              <span className="stat-label">{t('book.rating')}</span>
            </div>
            <div className="stat">
              <span className="stat-value">{book.total_reviews || 0}</span>
              <span className="stat-label">{t('book.reviews')}</span>
            </div>
            {book.total_chapters && (
              <div className="stat">
                <span className="stat-value">{book.total_chapters}</span>
                <span className="stat-label">{t('book.chapters')}</span>
              </div>
            )}
            {book.publication_year && (
              <div className="stat">
                <span className="stat-value">{book.publication_year}</span>
                <span className="stat-label">{t('book.year')}</span>
              </div>
            )}
          </div>

          <span className={`book-status status-${book.status}`}>
            {t(`status.${book.status}`)}
          </span>

          {book.tags && book.tags.length > 0 && (
            <div className="book-tags">
              {book.tags.map((tag) => (
                <span key={tag.id} className="tag">
                  {i18n.language === 'th' && tag.name_th ? tag.name_th : tag.name}
                </span>
              ))}
            </div>
          )}

          {isAuthenticated && (
            <div className="book-actions">
              <button
                className={`favorite-btn ${favoriteStatus.isFavorite ? 'active' : ''}`}
                onClick={() => handleFavoriteToggle('favorites')}
              >
                {favoriteStatus.isFavorite ? '❤️' : '🤍'} {t('book.addFavorite')}
              </button>
              <select
                className="list-select"
                value={favoriteStatus.lists[0] || ''}
                onChange={(e) => handleFavoriteToggle(e.target.value)}
              >
                <option value="">Add to list...</option>
                <option value="reading">{t('favorites.reading')}</option>
                <option value="completed">{t('favorites.completed')}</option>
                <option value="plan_to_read">{t('favorites.planToRead')}</option>
              </select>
            </div>
          )}
        </div>
      </div>

      {description && (
        <section className="book-description">
          <h2>Description</h2>
          <p>{description}</p>
        </section>
      )}

      <section className="book-reviews">
        <div className="reviews-header">
          <h2>{t('book.reviews')}</h2>
          {isAuthenticated && (
            <button
              className="write-review-btn"
              onClick={() => setShowReviewForm(!showReviewForm)}
            >
              {t('book.writeReview')}
            </button>
          )}
        </div>

        {showReviewForm && (
          <form className="review-form" onSubmit={handleReviewSubmit}>
            <div className="rating-input">
              {[1, 2, 3, 4, 5].map((star) => (
                <button
                  key={star}
                  type="button"
                  className={`star-btn ${reviewData.rating >= star ? 'active' : ''}`}
                  onClick={() => setReviewData(prev => ({ ...prev, rating: star }))}
                >
                  ⭐
                </button>
              ))}
            </div>
            <input
              type="text"
              placeholder={t('review.title')}
              value={reviewData.title}
              onChange={(e) => setReviewData(prev => ({ ...prev, title: e.target.value }))}
            />
            <textarea
              placeholder={t('review.content')}
              value={reviewData.content}
              onChange={(e) => setReviewData(prev => ({ ...prev, content: e.target.value }))}
              rows={4}
            />
            <label className="spoiler-label">
              <input
                type="checkbox"
                checked={reviewData.is_spoiler}
                onChange={(e) => setReviewData(prev => ({ ...prev, is_spoiler: e.target.checked }))}
              />
              {t('review.spoiler')}
            </label>
            <button type="submit" className="submit-btn">{t('review.submit')}</button>
          </form>
        )}

        <div className="reviews-list">
          {reviews.map((review) => (
            <div key={review.id} className="review-card">
              <div className="review-header">
                <span className="reviewer-name">{review.display_name || review.username}</span>
                <span className="review-rating">
                  {'⭐'.repeat(review.rating)}
                </span>
              </div>
              {review.title && <h4 className="review-title">{review.title}</h4>}
              {review.is_spoiler && <span className="spoiler-warning">⚠️ Spoiler</span>}
              <p className="review-content">{review.content}</p>
              <div className="review-footer">
                <span className="review-date">
                  {new Date(review.created_at).toLocaleDateString()}
                </span>
                <button className="helpful-btn">
                  👍 {review.helpful_count || 0}
                </button>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="similar-books">
        <BookGrid
          title={t('book.similar')}
          books={recommendations}
          loading={recsLoading}
        />
      </section>
    </div>
  );
};

export default BookDetail;
