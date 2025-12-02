import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import BookCard from './BookCard';
import './BookGrid.css';

const BookGrid = ({ title, books, loading, viewAllLink, emptyMessage }) => {
  const { t } = useTranslation();

  if (loading) {
    return (
      <div className="book-grid-section">
        {title && <h2 className="section-title">{title}</h2>}
        <div className="book-grid">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="book-card-skeleton">
              <div className="skeleton-cover"></div>
              <div className="skeleton-info">
                <div className="skeleton-title"></div>
                <div className="skeleton-author"></div>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  if (!books || books.length === 0) {
    return (
      <div className="book-grid-section">
        {title && <h2 className="section-title">{title}</h2>}
        <p className="empty-message">{emptyMessage || t('search.noResults')}</p>
      </div>
    );
  }

  return (
    <div className="book-grid-section">
      <div className="section-header">
        {title && <h2 className="section-title">{title}</h2>}
        {viewAllLink && (
          <Link to={viewAllLink} className="view-all-link">
            {t('common.viewAll')} →
          </Link>
        )}
      </div>
      <div className="book-grid">
        {books.map((book) => (
          <BookCard key={book.id} book={book} />
        ))}
      </div>
    </div>
  );
};

export default BookGrid;
