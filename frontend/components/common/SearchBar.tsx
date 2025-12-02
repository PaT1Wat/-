'use client';

import { useState, useRef, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Image from 'next/image';
import { useI18n } from '@/contexts/I18nContext';
import { useAutocomplete } from '@/hooks/useBooks';

interface SearchBarProps {
  onSearch?: (query: string) => void;
  initialQuery?: string;
}

export default function SearchBar({ onSearch, initialQuery = '' }: SearchBarProps) {
  const { t, language } = useI18n();
  const router = useRouter();
  const [query, setQuery] = useState(initialQuery);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const { suggestions } = useAutocomplete(query);
  const inputRef = useRef<HTMLInputElement>(null);
  const suggestionsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        suggestionsRef.current && 
        !suggestionsRef.current.contains(event.target as Node) &&
        inputRef.current && 
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowSuggestions(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (query.trim()) {
      setShowSuggestions(false);
      if (onSearch) {
        onSearch(query);
      } else {
        router.push(`/search?q=${encodeURIComponent(query)}`);
      }
    }
  };

  const handleSuggestionClick = (bookId: string) => {
    setShowSuggestions(false);
    router.push(`/book/${bookId}`);
  };

  return (
    <div className="relative w-full max-w-2xl mx-auto">
      <form onSubmit={handleSubmit} className="flex gap-2">
        <div className="flex-1 relative">
          <span className="absolute left-4 top-1/2 -translate-y-1/2 text-lg">🔍</span>
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
            className="w-full pl-12 pr-10 py-3 rounded-xl border-2 border-gray-200 focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100 outline-none transition-all text-gray-800"
          />
          {query && (
            <button
              type="button"
              onClick={() => {
                setQuery('');
                inputRef.current?.focus();
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
            >
              ✕
            </button>
          )}
        </div>
        <button 
          type="submit" 
          className="bg-indigo-600 text-white px-6 py-3 rounded-xl font-medium hover:bg-indigo-700 transition-colors"
        >
          {t('nav.search')}
        </button>
      </form>

      {showSuggestions && suggestions.length > 0 && (
        <div 
          ref={suggestionsRef} 
          className="absolute top-full left-0 right-0 mt-2 bg-white rounded-xl shadow-xl border border-gray-100 overflow-hidden z-50"
        >
          {suggestions.map((book) => (
            <div
              key={book.id}
              onClick={() => handleSuggestionClick(book.id)}
              className="flex items-center gap-3 p-3 hover:bg-gray-50 cursor-pointer transition-colors"
            >
              <div className="w-10 h-14 relative flex-shrink-0 bg-gray-100 rounded overflow-hidden">
                {book.cover_image_url ? (
                  <Image
                    src={book.cover_image_url}
                    alt=""
                    fill
                    className="object-cover"
                    sizes="40px"
                  />
                ) : (
                  <span className="flex items-center justify-center h-full text-xl">📖</span>
                )}
              </div>
              <div className="flex-1 min-w-0">
                <p className="font-medium text-gray-800 truncate">
                  {language === 'th' && book.title_th ? book.title_th : book.title}
                </p>
                <p className="text-xs text-gray-500">
                  {book.type && t(`type.${book.type}` as keyof typeof t)}
                </p>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
