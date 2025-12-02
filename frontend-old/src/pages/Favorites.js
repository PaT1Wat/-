import React, { useState, useEffect, useCallback } from 'react';
import { Navigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import { favoritesAPI } from '../services/api';
import BookGrid from '../components/books/BookGrid';
import './Favorites.css';

const Favorites = () => {
  const { t } = useTranslation();
  const { isAuthenticated } = useAuth();
  const [activeList, setActiveList] = useState('favorites');
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [counts, setCounts] = useState([]);

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
      setBooks(response.data.favorites);
    } catch (err) {
      console.error('Error fetching favorites:', err);
    } finally {
      setLoading(false);
    }
  }, [activeList]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchCounts();
    }
  }, [isAuthenticated, fetchCounts]);

  useEffect(() => {
    if (isAuthenticated) {
      fetchFavorites();
    }
  }, [isAuthenticated, fetchFavorites]);

  const getCount = (listKey) => {
    const item = counts.find(c => c.list_name === listKey);
    return item ? parseInt(item.count) : 0;
  };

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return (
    <div className="favorites-page">
      <h1>{t('favorites.title')}</h1>

      <div className="list-tabs">
        {lists.map((list) => (
          <button
            key={list.key}
            className={`tab-btn ${activeList === list.key ? 'active' : ''}`}
            onClick={() => setActiveList(list.key)}
          >
            {list.label}
            <span className="count">{getCount(list.key)}</span>
          </button>
        ))}
      </div>

      <BookGrid
        books={books.map(f => ({
          id: f.book_id,
          title: f.title,
          title_th: f.title_th,
          cover_image_url: f.cover_image_url,
          type: f.type,
          status: f.status,
          average_rating: f.average_rating,
          author_name: f.author_name,
          author_name_th: f.author_name_th
        }))}
        loading={loading}
        emptyMessage={t('favorites.empty')}
      />
    </div>
  );
};

export default Favorites;
