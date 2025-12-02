'use client';

import { useI18n } from '@/contexts/I18nContext';
import { useAuth } from '@/contexts/AuthContext';
import SearchBar from '@/components/common/SearchBar';
import BookGrid from '@/components/books/BookGrid';
import { usePopularBooks, useRecentBooks } from '@/hooks/useBooks';

export default function Home() {
  const { t } = useI18n();
  const { isAuthenticated } = useAuth();
  const { books: popularBooks, loading: popularLoading } = usePopularBooks(8);
  const { books: recentBooks, loading: recentLoading } = useRecentBooks(8);

  return (
    <div className="min-h-screen">
      {/* Hero Section */}
      <section className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white py-16 px-4 relative overflow-hidden">
        <div className="max-w-4xl mx-auto text-center relative z-10">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 drop-shadow-lg">
            {t('home.welcome')}
          </h1>
          <p className="text-xl opacity-90 mb-8">
            {t('home.subtitle')}
          </p>
          <SearchBar />
        </div>
        
        {/* Decorative emojis */}
        <div className="absolute inset-0 opacity-10 pointer-events-none">
          <span className="absolute text-8xl top-[10%] left-[5%] animate-bounce" style={{ animationDuration: '6s' }}>📚</span>
          <span className="absolute text-8xl top-[60%] right-[10%] animate-bounce" style={{ animationDuration: '8s' }}>📖</span>
          <span className="absolute text-8xl bottom-[10%] left-[15%] animate-bounce" style={{ animationDuration: '7s' }}>🎌</span>
        </div>
      </section>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
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
          <div className="mt-8 p-6 bg-gradient-to-br from-gray-50 to-gray-100 rounded-2xl">
            <BookGrid
              title={t('home.recommendations')}
              books={popularBooks.slice(0, 4)}
              loading={popularLoading}
              viewAllLink="/recommendations"
            />
          </div>
        )}
      </div>
    </div>
  );
}
