import React from 'react';
import { useTranslation } from 'react-i18next';
import { useAuth } from '../contexts/AuthContext';
import SearchBar from '../components/common/SearchBar';
import BookGrid from '../components/books/BookGrid';
import { usePopularBooks, useRecentBooks } from '../hooks/useBooks';
import './Home.css';

const Home = () => {
  const { t } = useTranslation();
  const { isAuthenticated } = useAuth();
  const { books: popularBooks, loading: popularLoading } = usePopularBooks(8);
  const { books: recentBooks, loading: recentLoading } = useRecentBooks(8);

  return (
    <div className="home-page">
      <section className="hero-section">
        <div className="hero-content">
          <h1 className="hero-title">{t('home.welcome')}</h1>
          <p className="hero-subtitle">{t('home.subtitle')}</p>
          <SearchBar />
        </div>
        <div className="hero-decoration">
          <span className="decoration-emoji">📚</span>
          <span className="decoration-emoji">📖</span>
          <span className="decoration-emoji">🎌</span>
        </div>
      </section>

      <main className="home-content">
        <BookGrid
          title={t('home.popular')}
          books={popularBooks}
          loading={popularLoading}
          viewAllLink="/search?sort_by=average_rating"
        />

        <BookGrid
          title={t('home.recent')}
          books={recentBooks}
          loading={recentLoading}
          viewAllLink="/search?sort_by=created_at"
        />

        {isAuthenticated && (
          <div className="recommendations-section">
            <BookGrid
              title={t('home.recommendations')}
              books={popularBooks.slice(0, 4)}
              loading={popularLoading}
              viewAllLink="/recommendations"
            />
          </div>
        )}
      </main>
    </div>
  );
};

export default Home;
