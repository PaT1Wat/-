import React from 'react';
import { Link } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import './BookCard.css';

const BookCard = ({ book, showRating = true }) => {
  const { t, i18n } = useTranslation();
  const title = i18n.language === 'th' && book.title_th ? book.title_th : book.title;
  const authorName = i18n.language === 'th' && book.author_name_th ? book.author_name_th : book.author_name;

  return (
    <Link to={`/book/${book.id}`} className="book-card">
      <div className="book-cover">
        {book.cover_image_url ? (
          <img src={book.cover_image_url} alt={title} />
        ) : (
          <div className="book-cover-placeholder">
            <span className="placeholder-icon">📖</span>
          </div>
        )}
        <span className={`book-type type-${book.type}`}>
          {t(`type.${book.type}`)}
        </span>
      </div>
      
      <div className="book-info">
        <h3 className="book-title" title={title}>{title}</h3>
        {authorName && (
          <p className="book-author">{authorName}</p>
        )}
        {showRating && book.average_rating > 0 && (
          <div className="book-rating">
            <span className="rating-star">⭐</span>
            <span className="rating-value">{Number(book.average_rating).toFixed(1)}</span>
            <span className="rating-count">({book.total_reviews || 0})</span>
          </div>
        )}
        <span className={`book-status status-${book.status}`}>
          {t(`status.${book.status}`)}
        </span>
      </div>
    </Link>
  );
};

export default BookCard;
