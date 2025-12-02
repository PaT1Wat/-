import axios from 'axios';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      if (typeof window !== 'undefined') {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data: { email: string; username: string; password?: string }) => 
    api.post('/auth/register', data),
  loginWithFirebase: (firebaseToken: string) => 
    api.post('/auth/login/firebase', { firebase_token: firebaseToken }),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (data: { display_name?: string; avatar_url?: string }) => 
    api.put('/auth/profile', data)
};

// Books API
export const booksAPI = {
  getBooks: (params?: Record<string, unknown>) => api.get('/books', { params }),
  getBook: (id: string) => api.get(`/books/${id}`),
  search: (params?: Record<string, unknown>) => api.get('/books/search', { params }),
  autocomplete: (query: string) => api.get('/books/autocomplete', { params: { query } }),
  getPopular: (limit?: number) => api.get('/books/popular', { params: { limit } }),
  getRecent: (limit?: number) => api.get('/books/recent', { params: { limit } }),
  getByType: (type: string, params?: Record<string, unknown>) => 
    api.get(`/books/type/${type}`, { params }),
  getRecommendations: (id: string, limit?: number) => 
    api.get(`/books/${id}/recommendations`, { params: { limit } }),
  getTags: (category?: string) => api.get('/books/tags', { params: { category } }),
  getPopularTags: (limit?: number) => api.get('/books/tags/popular', { params: { limit } }),
  // Admin
  createBook: (data: Record<string, unknown>) => api.post('/books', data),
  updateBook: (id: string, data: Record<string, unknown>) => api.put(`/books/${id}`, data),
  deleteBook: (id: string) => api.delete(`/books/${id}`),
  createTag: (data: Record<string, unknown>) => api.post('/books/tags', data)
};

// Authors API
export const authorsAPI = {
  getAll: (params?: Record<string, unknown>) => api.get('/authors', { params }),
  getById: (id: string) => api.get(`/authors/${id}`),
  search: (query: string) => api.get('/authors/search', { params: { query } }),
  getBooks: (id: string, params?: Record<string, unknown>) => 
    api.get(`/authors/${id}/books`, { params }),
  create: (data: Record<string, unknown>) => api.post('/authors', data),
  update: (id: string, data: Record<string, unknown>) => api.put(`/authors/${id}`, data),
  delete: (id: string) => api.delete(`/authors/${id}`)
};

// Publishers API
export const publishersAPI = {
  getAll: (params?: Record<string, unknown>) => api.get('/publishers', { params }),
  getById: (id: string) => api.get(`/publishers/${id}`),
  search: (query: string) => api.get('/publishers/search', { params: { query } }),
  getBooks: (id: string, params?: Record<string, unknown>) => 
    api.get(`/publishers/${id}/books`, { params }),
  create: (data: Record<string, unknown>) => api.post('/publishers', data),
  update: (id: string, data: Record<string, unknown>) => api.put(`/publishers/${id}`, data),
  delete: (id: string) => api.delete(`/publishers/${id}`)
};

// Reviews API
export const reviewsAPI = {
  getByBook: (bookId: string, params?: Record<string, unknown>) => 
    api.get(`/reviews/book/${bookId}`, { params }),
  getUserReviews: (params?: Record<string, unknown>) => api.get('/reviews/user', { params }),
  create: (data: Record<string, unknown>) => api.post('/reviews', data),
  update: (id: string, data: Record<string, unknown>) => api.put(`/reviews/${id}`, data),
  delete: (id: string) => api.delete(`/reviews/${id}`),
  markHelpful: (id: string) => api.post(`/reviews/${id}/helpful`),
  // Moderator
  getPending: (params?: Record<string, unknown>) => api.get('/reviews/pending', { params }),
  approve: (id: string) => api.put(`/reviews/${id}/approve`),
  reject: (id: string) => api.delete(`/reviews/${id}/reject`)
};

// Favorites API
export const favoritesAPI = {
  getAll: (params?: Record<string, unknown>) => api.get('/favorites', { params }),
  getCounts: () => api.get('/favorites/counts'),
  check: (bookId: string) => api.get(`/favorites/check/${bookId}`),
  add: (bookId: string, listName: string) => 
    api.post('/favorites', { book_id: bookId, list_name: listName }),
  remove: (bookId: string, listName: string) => 
    api.delete(`/favorites/${bookId}`, { params: { list_name: listName } }),
  updateList: (bookId: string, oldListName: string, newListName: string) => 
    api.put(`/favorites/${bookId}/list`, { old_list_name: oldListName, new_list_name: newListName })
};

// Recommendations API
export const recommendationsAPI = {
  getPersonalized: (limit?: number) => 
    api.get('/recommendations/personalized', { params: { limit } }),
  getHybrid: (bookId: string, limit?: number) => 
    api.get('/recommendations/hybrid', { params: { book_id: bookId, limit } }),
  getPopular: (limit?: number) => api.get('/recommendations/popular', { params: { limit } }),
  getPopularSearches: (limit?: number) => 
    api.get('/recommendations/searches/popular', { params: { limit } }),
  recordInteraction: (bookId: string, type: string, weight: number) => 
    api.post('/recommendations/interaction', { book_id: bookId, interaction_type: type, weight }),
  getSearchHistory: (limit?: number) => 
    api.get('/recommendations/history', { params: { limit } }),
  clearSearchHistory: () => api.delete('/recommendations/history'),
  getSearchSuggestions: (query: string) => 
    api.get('/recommendations/suggestions', { params: { query } })
};

export default api;
