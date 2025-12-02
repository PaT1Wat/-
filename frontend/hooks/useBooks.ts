'use client';

import { useState, useEffect, useCallback } from 'react';
import { booksAPI, recommendationsAPI } from '@/lib/api';
import type { Book, Tag, Pagination } from '@/lib/types';

interface BooksState {
  books: Book[];
  loading: boolean;
  error: string | null;
  pagination: Pagination;
}

export const useBooks = (initialParams: Record<string, unknown> = {}) => {
  const [state, setState] = useState<BooksState>({
    books: [],
    loading: false,
    error: null,
    pagination: { page: 1, totalPages: 1, total: 0 }
  });

  const fetchBooks = useCallback(async (params: Record<string, unknown> = {}) => {
    setState(prev => ({ ...prev, loading: true, error: null }));
    try {
      const response = await booksAPI.search({ ...initialParams, ...params });
      setState({
        books: response.data.books,
        loading: false,
        error: null,
        pagination: {
          page: response.data.page,
          totalPages: response.data.totalPages,
          total: response.data.total
        }
      });
    } catch (err) {
      setState(prev => ({
        ...prev,
        loading: false,
        error: err instanceof Error ? err.message : 'Failed to fetch books'
      }));
    }
  }, [initialParams]);

  useEffect(() => {
    fetchBooks();
  }, [fetchBooks]);

  return { ...state, fetchBooks, setBooks: (books: Book[]) => setState(prev => ({ ...prev, books })) };
};

export const useBook = (id: string) => {
  const [book, setBook] = useState<Book | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;

    const fetchBook = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await booksAPI.getBook(id);
        setBook(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch book');
      } finally {
        setLoading(false);
      }
    };

    fetchBook();
  }, [id]);

  return { book, loading, error, setBook };
};

export const usePopularBooks = (limit = 10) => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchPopular = async () => {
      setLoading(true);
      try {
        const response = await booksAPI.getPopular(limit);
        setBooks(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch popular books');
      } finally {
        setLoading(false);
      }
    };

    fetchPopular();
  }, [limit]);

  return { books, loading, error };
};

export const useRecentBooks = (limit = 10) => {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecent = async () => {
      setLoading(true);
      try {
        const response = await booksAPI.getRecent(limit);
        setBooks(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch recent books');
      } finally {
        setLoading(false);
      }
    };

    fetchRecent();
  }, [limit]);

  return { books, loading, error };
};

export const useRecommendations = (bookId: string | null = null, limit = 10) => {
  const [recommendations, setRecommendations] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchRecommendations = async () => {
      setLoading(true);
      try {
        let response;
        if (bookId) {
          response = await booksAPI.getRecommendations(bookId, limit);
        } else {
          response = await recommendationsAPI.getPopular(limit);
        }
        setRecommendations(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch recommendations');
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [bookId, limit]);

  return { recommendations, loading, error };
};

export const useTags = () => {
  const [tags, setTags] = useState<Tag[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchTags = async () => {
      setLoading(true);
      try {
        const response = await booksAPI.getTags();
        setTags(response.data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to fetch tags');
      } finally {
        setLoading(false);
      }
    };

    fetchTags();
  }, []);

  return { tags, loading, error };
};

export const useAutocomplete = (query: string, delay = 300) => {
  const [suggestions, setSuggestions] = useState<Book[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query || query.length < 2) {
      setSuggestions([]);
      return;
    }

    const timeoutId = setTimeout(async () => {
      setLoading(true);
      try {
        const response = await booksAPI.autocomplete(query);
        setSuggestions(response.data);
      } catch (err) {
        console.error('Autocomplete error:', err);
      } finally {
        setLoading(false);
      }
    }, delay);

    return () => clearTimeout(timeoutId);
  }, [query, delay]);

  return { suggestions, loading };
};
