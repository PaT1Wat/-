import React, { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import SearchBar from '../components/common/SearchBar';
import BookGrid from '../components/books/BookGrid';
import { useBooks, useTags } from '../hooks/useBooks';
import './Search.css';

const Search = () => {
  const { t } = useTranslation();
  const [searchParams, setSearchParams] = useSearchParams();
  const { tags } = useTags();
  
  const [filters, setFilters] = useState({
    query: searchParams.get('q') || '',
    type: searchParams.get('type') || '',
    status: searchParams.get('status') || '',
    tags: searchParams.get('tags')?.split(',').filter(Boolean) || [],
    min_rating: searchParams.get('min_rating') || '',
    sort_by: searchParams.get('sort_by') || 'average_rating',
    sort_order: searchParams.get('sort_order') || 'DESC',
    page: parseInt(searchParams.get('page')) || 1
  });

  const { books, loading, pagination, fetchBooks } = useBooks(filters);

  const updateUrlParams = useCallback((currentFilters) => {
    const params = new URLSearchParams();
    if (currentFilters.query) params.set('q', currentFilters.query);
    if (currentFilters.type) params.set('type', currentFilters.type);
    if (currentFilters.status) params.set('status', currentFilters.status);
    if (currentFilters.tags.length) params.set('tags', currentFilters.tags.join(','));
    if (currentFilters.min_rating) params.set('min_rating', currentFilters.min_rating);
    if (currentFilters.sort_by !== 'average_rating') params.set('sort_by', currentFilters.sort_by);
    if (currentFilters.page > 1) params.set('page', currentFilters.page);
    setSearchParams(params);
  }, [setSearchParams]);

  useEffect(() => {
    fetchBooks(filters);
    updateUrlParams(filters);
  }, [filters, fetchBooks, updateUrlParams]);

  const handleSearch = (query) => {
    setFilters(prev => ({ ...prev, query, page: 1 }));
  };

  const handleFilterChange = (key, value) => {
    setFilters(prev => ({ ...prev, [key]: value, page: 1 }));
  };

  const handleTagToggle = (tagName) => {
    setFilters(prev => ({
      ...prev,
      tags: prev.tags.includes(tagName)
        ? prev.tags.filter(t => t !== tagName)
        : [...prev.tags, tagName],
      page: 1
    }));
  };

  const handlePageChange = (page) => {
    setFilters(prev => ({ ...prev, page }));
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <div className="search-page">
      <div className="search-header">
        <h1>{t('search.results')}</h1>
        <SearchBar onSearch={handleSearch} initialQuery={filters.query} />
      </div>

      <div className="search-content">
        <aside className="filters-sidebar">
          <h2>{t('search.filters')}</h2>

          <div className="filter-group">
            <label>{t('search.type')}</label>
            <select
              value={filters.type}
              onChange={(e) => handleFilterChange('type', e.target.value)}
            >
              <option value="">All</option>
              <option value="manga">{t('type.manga')}</option>
              <option value="novel">{t('type.novel')}</option>
              <option value="light_novel">{t('type.light_novel')}</option>
              <option value="manhwa">{t('type.manhwa')}</option>
              <option value="manhua">{t('type.manhua')}</option>
            </select>
          </div>

          <div className="filter-group">
            <label>{t('search.status')}</label>
            <select
              value={filters.status}
              onChange={(e) => handleFilterChange('status', e.target.value)}
            >
              <option value="">All</option>
              <option value="ongoing">{t('status.ongoing')}</option>
              <option value="completed">{t('status.completed')}</option>
              <option value="hiatus">{t('status.hiatus')}</option>
            </select>
          </div>

          <div className="filter-group">
            <label>{t('search.rating')}</label>
            <select
              value={filters.min_rating}
              onChange={(e) => handleFilterChange('min_rating', e.target.value)}
            >
              <option value="">All</option>
              <option value="4">4+ ⭐</option>
              <option value="3">3+ ⭐</option>
              <option value="2">2+ ⭐</option>
            </select>
          </div>

          <div className="filter-group">
            <label>{t('search.tags')}</label>
            <div className="tags-list">
              {tags.slice(0, 20).map((tag) => (
                <button
                  key={tag.id}
                  className={`tag-btn ${filters.tags.includes(tag.name) ? 'active' : ''}`}
                  onClick={() => handleTagToggle(tag.name)}
                >
                  {tag.name_th || tag.name}
                </button>
              ))}
            </div>
          </div>
        </aside>

        <main className="search-results">
          <div className="results-header">
            <span>{pagination.total} results</span>
            <select
              value={filters.sort_by}
              onChange={(e) => handleFilterChange('sort_by', e.target.value)}
              className="sort-select"
            >
              <option value="average_rating">Rating</option>
              <option value="created_at">Newest</option>
              <option value="view_count">Popular</option>
              <option value="title">Title</option>
            </select>
          </div>

          <BookGrid books={books} loading={loading} />

          {pagination.totalPages > 1 && (
            <div className="pagination">
              <button
                disabled={pagination.page <= 1}
                onClick={() => handlePageChange(pagination.page - 1)}
              >
                ←
              </button>
              <span>
                {pagination.page} / {pagination.totalPages}
              </span>
              <button
                disabled={pagination.page >= pagination.totalPages}
                onClick={() => handlePageChange(pagination.page + 1)}
              >
                →
              </button>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default Search;
