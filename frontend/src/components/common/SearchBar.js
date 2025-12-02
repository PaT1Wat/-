import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useTranslation } from 'react-i18next';
import { useAutocomplete } from '../../hooks/useBooks';
import './SearchBar.css';

const SearchBar = ({ onSearch, initialQuery = '' }) => {
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const [query, setQuery] = useState(initialQuery);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const { suggestions } = useAutocomplete(query);
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (suggestionsRef.current && !suggestionsRef.current.contains(event.target) &&
          inputRef.current && !inputRef.current.contains(event.target)) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = (e) => {
    e.preventDefault();
    if (query.trim()) {
      setShowSuggestions(false);
      if (onSearch) {
        onSearch(query);
      } else {
        navigate(`/search?q=${encodeURIComponent(query)}`);
      }
    }
  };

  const handleSuggestionClick = (book) => {
    setShowSuggestions(false);
    navigate(`/book/${book.id}`);
  };

  return (
    <div className="search-bar-container">
      <form onSubmit={handleSubmit} className="search-form">
        <div className="search-input-wrapper">
          <span className="search-icon">🔍</span>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={(e) => {
              setQuery(e.target.value);
              setShowSuggestions(true);
            }}
            onFocus={() => setShowSuggestions(true)}
            placeholder={t('search.placeholder')}
            className="search-input"
          />
          {query && (
            <button
              type="button"
              className="clear-btn"
              onClick={() => {
                setQuery('');
                inputRef.current?.focus();
              }}
            >
              ✕
            </button>
          )}
        </div>
        <button type="submit" className="search-btn">
          {t('nav.search')}
        </button>
      </form>

      {showSuggestions && suggestions.length > 0 && (
        <div ref={suggestionsRef} className="suggestions-dropdown">
          {suggestions.map((book) => (
            <div
              key={book.id}
              className="suggestion-item"
              onClick={() => handleSuggestionClick(book)}
            >
              <div className="suggestion-cover">
                {book.cover_image_url ? (
                  <img src={book.cover_image_url} alt="" />
                ) : (
                  <span>📖</span>
                )}
              </div>
              <div className="suggestion-info">
                <span className="suggestion-title">
                  {i18n.language === 'th' && book.title_th ? book.title_th : book.title}
                </span>
                <span className="suggestion-type">{t(`type.${book.type}`)}</span>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default SearchBar;
