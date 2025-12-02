'use client';

import { useState, useEffect, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { useI18n } from '@/contexts/I18nContext';
import { useAuth } from '@/contexts/AuthContext';
import { favoritesAPI } from '@/lib/api';
import BookGrid from '@/components/books/BookGrid';
import type { Favorite, Book } from '@/lib/types';

interface ListCount {
  list_name: string;
  count: string;
}

export default function FavoritesPage() {
  const { t } = useI18n();
  const { isAuthenticated } = useAuth();
  const router = useRouter();
  const [activeList, setActiveList] = useState('favorites');
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [loading, setLoading] = useState(false);
  const [counts, setCounts] = useState<ListCount[]>([]);

  const lists = [
    { key: 'favorites', label: t('favorites.favorites') },
    { key: 'reading', label: t('favorites.reading') },
    { key: 'completed', label: t('favorites.completed') },
    { key: 'plan_to_read', label: t('favorites.planToRead') },
    { key: 'dropped', label: t('favorites.dropped') }
  ];

  const fetchCounts = useCallback(async () => {
    try {
      const response = await favoritesAPI.getCounts();
      setCounts(response.data);
    } catch (err) {
      console.error('Error fetching counts:', err);
    }
  }, []);

  const fetchFavorites = useCallback(async () => {
    setLoading(true);
    try {
      const response = await favoritesAPI.getAll({ list_name: activeList });
      setFavorites(response.data.favorites);
    } catch (err) {
      console.error('Error fetching favorites:', err);
    } finally {
      setLoading(false);
    }
  }, [activeList]);

  useEffect(() => {
    if (!isAuthenticated) {
      router.push('/login');
      return;
    }
    fetchCounts();
  }, [isAuthenticated, router, fetchCounts]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchFavorites();
    }
  }, [isAuthenticated, fetchFavorites]);

  const getCount = (listKey: string): number => {
    const item = counts.find(c => c.list_name === listKey);
    return item ? parseInt(item.count) : 0;
  };

  // Convert favorites to books format for BookGrid
  const books: Book[] = favorites.map(f => ({
    id: f.book_id,
    title: f.title || '',
    title_th: f.title_th,
    cover_image_url: f.cover_image_url,
    type: f.type as Book['type'],
    status: f.status as Book['status'],
    average_rating: f.average_rating,
    author_name: f.author_name,
    author_name_th: f.author_name_th
  }));

  if (!isAuthenticated) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold mb-8">{t('favorites.title')}</h1>

        <div className="flex flex-wrap gap-2 mb-8">
          {lists.map((list) => (
            <button
              key={list.key}
              className={`px-4 py-2 rounded-lg font-medium transition-colors flex items-center gap-2 ${
                activeList === list.key
                  ? 'bg-indigo-600 text-white'
                  : 'bg-white text-gray-700 hover:bg-gray-100 border border-gray-200'
              }`}
              onClick={() => setActiveList(list.key)}
            >
              {list.label}
              <span className={`px-2 py-0.5 rounded-full text-xs ${
                activeList === list.key
                  ? 'bg-white/20 text-white'
                  : 'bg-gray-100 text-gray-600'
              }`}>
                {getCount(list.key)}
              </span>
            </button>
          ))}
        </div>

        <BookGrid
          books={books}
          loading={loading}
          emptyMessage={t('favorites.empty')}
        />
      </div>
    </div>
  );
}
