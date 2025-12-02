'use client';

import { useState, useEffect, useCallback, Suspense } from 'react';
import { useSearchParams, useRouter } from 'next/navigation';
import { useI18n } from '@/contexts/I18nContext';
import SearchBar from '@/components/common/SearchBar';
import BookGrid from '@/components/books/BookGrid';
import { useBooks, useTags } from '@/hooks/useBooks';

function SearchContent() {
  const { t } = useI18n();
  const router = useRouter();
  const searchParams = useSearchParams();
  const { tags } = useTags();
  
  const [filters, setFilters] = useState({
    query: searchParams.get('q') || '',
    type: searchParams.get('type') || '',
    status: searchParams.get('status') || '',
    tags: searchParams.get('tags')?.split(',').filter(Boolean) || [],
    min_rating: searchParams.get('min_rating') || '',
    sort_by: searchParams.get('sort_by') || 'average_rating',
    sort_order: searchParams.get('sort_order') || 'DESC',
    page: parseInt(searchParams.get('page') || '1')
  });

  const { books, loading, pagination, fetchBooks } = useBooks(filters);

  const updateUrlParams = useCallback((currentFilters: typeof filters) => {
    const params = new URLSearchParams();
    if (currentFilters.query) params.set('q', currentFilters.query);
    if (currentFilters.type) params.set('type', currentFilters.type);
    if (currentFilters.status) params.set('status', currentFilters.status);
    if (currentFilters.tags.length) params.set('tags', currentFilters.tags.join(','));
    if (currentFilters.min_rating) params.set('min_rating', currentFilters.min_rating);
    if (currentFilters.sort_by !== 'average_rating') params.set('sort_by', currentFilters.sort_by);
    if (currentFilters.page > 1) params.set('page', String(currentFilters.page));
    router.push(`/search?${params.toString()}`);
  }, [router]);

  useEffect(() => {
    fetchBooks(filters);
    updateUrlParams(filters);
  }, [filters, fetchBooks, updateUrlParams]);

  const handleSearch = (query: string) => {
    setFilters(prev => ({ ...prev, query, page: 1 }));
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
  };

  const handleTagToggle = (tagName: string) => {
    setFilters(prev => ({
      ...prev,
      tags: prev.tags.includes(tagName)
        ? prev.tags.filter(t => t !== tagName)
        : [...prev.tags, tagName],
      page: 1
    }));
  };

  const handlePageChange = (page: number) => {
    setFilters(prev => ({ ...prev, page }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-4">{t('search.results')}</h1>
          <SearchBar onSearch={handleSearch} initialQuery={filters.query} />
        </div>

        <div className="flex gap-8 flex-col lg:flex-row">
          {/* Filters Sidebar */}
          <aside className="lg:w-64 flex-shrink-0">
            <div className="bg-white rounded-xl p-6 shadow-sm sticky top-24">
              <h2 className="text-lg font-semibold mb-4">{t('search.filters')}</h2>

              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">{t('search.type')}</label>
                  <select
                    value={filters.type}
                    onChange={(e) => handleFilterChange('type', e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 outline-none"
                  >
                    <option value="">All</option>
                    <option value="manga">{t('type.manga')}</option>
                    <option value="novel">{t('type.novel')}</option>
                    <option value="light_novel">{t('type.light_novel')}</option>
                    <option value="manhwa">{t('type.manhwa')}</option>
                    <option value="manhua">{t('type.manhua')}</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">{t('search.status')}</label>
                  <select
                    value={filters.status}
                    onChange={(e) => handleFilterChange('status', e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 outline-none"
                  >
                    <option value="">All</option>
                    <option value="ongoing">{t('status.ongoing')}</option>
                    <option value="completed">{t('status.completed')}</option>
                    <option value="hiatus">{t('status.hiatus')}</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">{t('search.rating')}</label>
                  <select
                    value={filters.min_rating}
                    onChange={(e) => handleFilterChange('min_rating', e.target.value)}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 outline-none"
                  >
                    <option value="">All</option>
                    <option value="4">4+ ⭐</option>
                    <option value="3">3+ ⭐</option>
                    <option value="2">2+ ⭐</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">{t('search.tags')}</label>
                  <div className="flex flex-wrap gap-2 max-h-48 overflow-y-auto">
                    {tags.slice(0, 20).map((tag) => (
                      <button
                        key={tag.id}
                        className={`px-3 py-1 rounded-full text-sm transition-colors ${
                          filters.tags.includes(tag.name)
                            ? 'bg-indigo-600 text-white'
                            : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                        }`}
                        onClick={() => handleTagToggle(tag.name)}
                      >
                        {tag.name_th || tag.name}
                      </button>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </aside>

          {/* Results */}
          <main className="flex-1">
            <div className="flex items-center justify-between mb-4">
              <span className="text-gray-600">{pagination.total} results</span>
              <select
                value={filters.sort_by}
                onChange={(e) => handleFilterChange('sort_by', e.target.value)}
                className="border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-indigo-200 focus:border-indigo-400 outline-none"
              >
                <option value="average_rating">Rating</option>
                <option value="created_at">Newest</option>
                <option value="view_count">Popular</option>
                <option value="title">Title</option>
              </select>
            </div>

            <BookGrid books={books} loading={loading} />

            {pagination.totalPages > 1 && (
              <div className="flex items-center justify-center gap-4 mt-8">
                <button
                  disabled={pagination.page <= 1}
                  onClick={() => handlePageChange(pagination.page - 1)}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  ←
                </button>
                <span className="text-gray-600">
                  {pagination.page} / {pagination.totalPages}
                </span>
                <button
                  disabled={pagination.page >= pagination.totalPages}
                  onClick={() => handlePageChange(pagination.page + 1)}
                  className="px-4 py-2 bg-white border border-gray-300 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50"
                >
                  →
                </button>
              </div>
            )}
          </main>
        </div>
      </div>
    </div>
  );
}

export default function SearchPage() {
  return (
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center">Loading...</div>}>
      <SearchContent />
    </Suspense>
  );
}
