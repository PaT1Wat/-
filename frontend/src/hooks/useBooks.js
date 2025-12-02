import { useState, useEffect, useCallback } from 'react';
import { booksAPI, recommendationsAPI } from '../services/api';

export const useBooks = (initialParams = {}) => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState({
    page: 1,
    totalPages: 1,
    total: 0
  });

  const fetchBooks = useCallback(async (params = {}) => {
    setLoading(true);
    setError(null);
    try {
      const response = await booksAPI.search({ ...initialParams, ...params });
      setBooks(response.data.books);
      setPagination({
        page: response.data.page,
        totalPages: response.data.totalPages,
        total: response.data.total
      });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [initialParams]);

  useEffect(() => {
    fetchBooks();
  }, [fetchBooks]);

  return { books, loading, error, pagination, fetchBooks, setBooks };
};

export const useBook = (id) => {
  const [book, setBook] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!id) return;

    const fetchBook = async () => {
      setLoading(true);
      setError(null);
      try {
        const response = await booksAPI.getBook(id);
        setBook(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchBook();
  }, [id]);

  return { book, loading, error, setBook };
};

export const usePopularBooks = (limit = 10) => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchPopular = async () => {
      setLoading(true);
      try {
        const response = await booksAPI.getPopular(limit);
        setBooks(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchPopular();
  }, [limit]);

  return { books, loading, error };
};

export const useRecentBooks = (limit = 10) => {
  const [books, setBooks] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchRecent = async () => {
      setLoading(true);
      try {
        const response = await booksAPI.getRecent(limit);
        setBooks(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchRecent();
  }, [limit]);

  return { books, loading, error };
};

export const useRecommendations = (bookId = null, limit = 10) => {
  const [recommendations, setRecommendations] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

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
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchRecommendations();
  }, [bookId, limit]);

  return { recommendations, loading, error };
};

export const useTags = () => {
  const [tags, setTags] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchTags = async () => {
      setLoading(true);
      try {
        const response = await booksAPI.getTags();
        setTags(response.data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchTags();
  }, []);

  return { tags, loading, error };
};

export const useAutocomplete = (query, delay = 300) => {
  const [suggestions, setSuggestions] = useState([]);
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
