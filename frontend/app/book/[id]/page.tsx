'use client';

import { useState, useEffect, use } from 'react';
import Image from 'next/image';
import { useI18n } from '@/contexts/I18nContext';
import { useAuth } from '@/contexts/AuthContext';
import { useBook, useRecommendations } from '@/hooks/useBooks';
import { favoritesAPI, reviewsAPI, recommendationsAPI } from '@/lib/api';
import BookGrid from '@/components/books/BookGrid';
import type { Review } from '@/lib/types';

interface BookDetailPageProps {
  params: Promise<{ id: string }>;
}

export default function BookDetailPage({ params }: BookDetailPageProps) {
  const { id } = use(params);
  const { t, language } = useI18n();
  const { isAuthenticated } = useAuth();
  const { book, loading, error } = useBook(id);
  const { recommendations, loading: recsLoading } = useRecommendations(id, 6);
  
  const [favoriteStatus, setFavoriteStatus] = useState({ isFavorite: false, lists: [] as string[] });
  const [reviews, setReviews] = useState<Review[]>([]);
  const [showReviewForm, setShowReviewForm] = useState(false);
  const [reviewData, setReviewData] = useState({ rating: 5, title: '', content: '', is_spoiler: false });

  // Fetch favorite status when authenticated
  useEffect(() => {
    if (!id || !isAuthenticated) return;
    
    const checkStatus = async () => {
      try {
        const response = await favoritesAPI.check(id);
        setFavoriteStatus(response.data);
      } catch (error) {
        console.error('Error checking favorite:', error);
      }
    };
    
    checkStatus();
  }, [id, isAuthenticated]);

  // Record view interaction when authenticated
  useEffect(() => {
    if (!id || !isAuthenticated) return;
    
    const recordView = async () => {
      try {
        await recommendationsAPI.recordInteraction(id, 'view', 1.0);
      } catch (error) {
        console.error('Error recording interaction:', error);
      }
    };
    
    recordView();
  }, [id, isAuthenticated]);

  // Fetch reviews
  useEffect(() => {
    if (!id) return;
    
    const loadReviews = async () => {
      try {
        const response = await reviewsAPI.getByBook(id, { limit: 5 });
        setReviews(response.data.reviews);
      } catch (error) {
        console.error('Error fetching reviews:', error);
      }
    };
    
    loadReviews();
  }, [id]);

  const refreshFavoriteStatus = async () => {
    try {
      const response = await favoritesAPI.check(id);
      setFavoriteStatus(response.data);
    } catch (error) {
      console.error('Error checking favorite:', error);
    }
  };

  const refreshReviews = async () => {
    try {
      const response = await reviewsAPI.getByBook(id, { limit: 5 });
      setReviews(response.data.reviews);
    } catch (error) {
      console.error('Error fetching reviews:', error);
    }
  };

  const handleFavoriteToggle = async (listName = 'favorites') => {
    if (!isAuthenticated) return;
    
    try {
      if (favoriteStatus.lists.includes(listName)) {
        await favoritesAPI.remove(id, listName);
      } else {
        await favoritesAPI.add(id, listName);
      }
      refreshFavoriteStatus();
    } catch (error) {
      console.error('Error toggling favorite:', error);
    }
  };

  const handleReviewSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await reviewsAPI.create({
        book_id: id,
        ...reviewData
      });
      setShowReviewForm(false);
      setReviewData({ rating: 5, title: '', content: '', is_spoiler: false });
      refreshReviews();
    } catch (error) {
      console.error('Error submitting review:', error);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">{t('common.loading')}</div>
      </div>
    );
  }

  if (error || !book) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-red-600">{t('common.error')}</div>
      </div>
    );
  }

  const title = language === 'th' && book.title_th ? book.title_th : book.title;
  const description = language === 'th' && book.description_th ? book.description_th : book.description;
  const authorName = language === 'th' && book.author_name_th ? book.author_name_th : book.author_name;

  const typeColors: Record<string, string> = {
    manga: 'bg-pink-600',
    novel: 'bg-purple-600',
    light_novel: 'bg-violet-700',
    manhwa: 'bg-blue-700',
    manhua: 'bg-blue-500'
  };

  const statusColors: Record<string, string> = {
    ongoing: 'bg-blue-100 text-blue-700',
    completed: 'bg-green-100 text-green-700',
    hiatus: 'bg-orange-100 text-orange-700',
    cancelled: 'bg-red-100 text-red-700'
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="bg-white rounded-2xl shadow-sm p-6 mb-8">
          <div className="flex flex-col md:flex-row gap-8">
            {/* Cover */}
            <div className="w-full md:w-72 flex-shrink-0">
              <div className="aspect-[2/3] relative rounded-xl overflow-hidden bg-gray-100">
                {book.cover_image_url ? (
                  <Image
                    src={book.cover_image_url}
                    alt={title}
                    fill
                    className="object-cover"
                    sizes="(max-width: 768px) 100vw, 300px"
                    priority
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center text-8xl">📖</div>
                )}
              </div>
            </div>

            {/* Info */}
            <div className="flex-1">
              {book.type && (
                <span className={`inline-block ${typeColors[book.type] || 'bg-gray-600'} text-white px-3 py-1 rounded-full text-sm font-semibold uppercase mb-3`}>
                  {t(`type.${book.type}` as keyof typeof t)}
                </span>
              )}
              
              <h1 className="text-3xl font-bold text-gray-900 mb-2">{title}</h1>
              
              {book.original_title && book.original_title !== title && (
                <p className="text-gray-500 text-lg mb-4">{book.original_title}</p>
              )}

              {authorName && (
                <p className="text-gray-700 mb-2">
                  <strong>{t('book.author')}:</strong> {authorName}
                </p>
              )}
              
              {book.publisher_name && (
                <p className="text-gray-700 mb-4">
                  <strong>{t('book.publisher')}:</strong> {book.publisher_name}
                </p>
              )}

              {/* Stats */}
              <div className="flex flex-wrap gap-6 mb-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-amber-500">⭐ {Number(book.average_rating || 0).toFixed(1)}</div>
                  <div className="text-sm text-gray-500">{t('book.rating')}</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-gray-800">{book.total_reviews || 0}</div>
                  <div className="text-sm text-gray-500">{t('book.reviews')}</div>
                </div>
                {book.total_chapters && (
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-800">{book.total_chapters}</div>
                    <div className="text-sm text-gray-500">{t('book.chapters')}</div>
                  </div>
                )}
                {book.publication_year && (
                  <div className="text-center">
                    <div className="text-2xl font-bold text-gray-800">{book.publication_year}</div>
                    <div className="text-sm text-gray-500">{t('book.year')}</div>
                  </div>
                )}
              </div>

              {book.status && (
                <span className={`inline-block ${statusColors[book.status] || 'bg-gray-100 text-gray-700'} px-3 py-1 rounded-full text-sm font-medium mb-4`}>
                  {t(`status.${book.status}` as keyof typeof t)}
                </span>
              )}

              {/* Tags */}
              {book.tags && book.tags.length > 0 && (
                <div className="flex flex-wrap gap-2 mb-6">
                  {book.tags.map((tag) => (
                    <span key={tag.id} className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm">
                      {language === 'th' && tag.name_th ? tag.name_th : tag.name}
                    </span>
                  ))}
                </div>
              )}

              {/* Actions */}
              {isAuthenticated && (
                <div className="flex flex-wrap gap-3">
                  <button
                    className={`px-6 py-2 rounded-lg font-medium transition-colors ${
                      favoriteStatus.isFavorite
                        ? 'bg-red-100 text-red-600 hover:bg-red-200'
                        : 'bg-indigo-600 text-white hover:bg-indigo-700'
                    }`}
                    onClick={() => handleFavoriteToggle('favorites')}
                  >
                    {favoriteStatus.isFavorite ? '❤️' : '🤍'} {t('book.addFavorite')}
                  </button>
                  <select
                    className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 outline-none"
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
        </div>

        {/* Description */}
        {description && (
          <section className="bg-white rounded-2xl shadow-sm p-6 mb-8">
            <h2 className="text-xl font-bold mb-4">Description</h2>
            <p className="text-gray-700 whitespace-pre-line">{description}</p>
          </section>
        )}

        {/* Reviews */}
        <section className="bg-white rounded-2xl shadow-sm p-6 mb-8">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-xl font-bold">{t('book.reviews')}</h2>
            {isAuthenticated && (
              <button
                className="bg-indigo-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors"
                onClick={() => setShowReviewForm(!showReviewForm)}
              >
                {t('book.writeReview')}
              </button>
            )}
          </div>

          {showReviewForm && (
            <form className="bg-gray-50 rounded-xl p-6 mb-6" onSubmit={handleReviewSubmit}>
              <div className="flex gap-1 mb-4">
                {[1, 2, 3, 4, 5].map((star) => (
                  <button
                    key={star}
                    type="button"
                    className={`text-3xl transition-colors ${reviewData.rating >= star ? 'text-amber-400' : 'text-gray-300'}`}
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
                className="w-full border border-gray-300 rounded-lg px-4 py-2 mb-4 focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 outline-none"
              />
              <textarea
                placeholder={t('review.content')}
                value={reviewData.content}
                onChange={(e) => setReviewData(prev => ({ ...prev, content: e.target.value }))}
                rows={4}
                className="w-full border border-gray-300 rounded-lg px-4 py-2 mb-4 focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 outline-none resize-none"
              />
              <label className="flex items-center gap-2 mb-4">
                <input
                  type="checkbox"
                  checked={reviewData.is_spoiler}
                  onChange={(e) => setReviewData(prev => ({ ...prev, is_spoiler: e.target.checked }))}
                  className="w-4 h-4 text-indigo-600 rounded focus:ring-indigo-500"
                />
                <span className="text-gray-700">{t('review.spoiler')}</span>
              </label>
              <button type="submit" className="bg-indigo-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-indigo-700 transition-colors">
                {t('review.submit')}
              </button>
            </form>
          )}

          <div className="space-y-4">
            {reviews.map((review) => (
              <div key={review.id} className="border-b border-gray-100 pb-4 last:border-0">
                <div className="flex items-center justify-between mb-2">
                  <span className="font-medium text-gray-900">{review.display_name || review.username}</span>
                  <span className="text-amber-400">{'⭐'.repeat(review.rating)}</span>
                </div>
                {review.title && <h4 className="font-semibold text-gray-800 mb-1">{review.title}</h4>}
                {review.is_spoiler && (
                  <span className="inline-block bg-red-100 text-red-600 px-2 py-0.5 rounded text-xs font-medium mb-2">⚠️ Spoiler</span>
                )}
                <p className="text-gray-700">{review.content}</p>
                <div className="flex items-center gap-4 mt-2 text-sm text-gray-500">
                  <span>{review.created_at ? new Date(review.created_at).toLocaleDateString() : ''}</span>
                  <button className="hover:text-indigo-600 transition-colors">
                    👍 {review.helpful_count || 0}
                  </button>
                </div>
              </div>
            ))}
          </div>
        </section>

        {/* Similar Books */}
        <section className="bg-white rounded-2xl shadow-sm p-6">
          <BookGrid
            title={t('book.similar')}
            books={recommendations}
            loading={recsLoading}
          />
        </section>
      </div>
    </div>
  );
}
