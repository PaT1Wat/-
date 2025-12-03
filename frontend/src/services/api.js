import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:3001/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json'
  }
});

// Request interceptor to add auth token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
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
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

// Auth API
export const authAPI = {
  register: (data) => api.post('/auth/register', data),
  loginWithFirebase: (firebaseToken) => api.post('/auth/login/firebase', { firebase_token: firebaseToken }),
  loginWithSupabase: (accessToken) => api.post('/auth/login/supabase', { access_token: accessToken }),
  getProfile: () => api.get('/auth/profile'),
  updateProfile: (data) => api.put('/auth/profile', data)
};

// Books API
export const booksAPI = {
  getBooks: (params) => api.get('/books', { params }),
  getBook: (id) => api.get(`/books/${id}`),
  search: (params) => api.get('/books/search', { params }),
  autocomplete: (query) => api.get('/books/autocomplete', { params: { query } }),
  getPopular: (limit) => api.get('/books/popular', { params: { limit } }),
  getRecent: (limit) => api.get('/books/recent', { params: { limit } }),
  getByType: (type, params) => api.get(`/books/type/${type}`, { params }),
  getRecommendations: (id, limit) => api.get(`/books/${id}/recommendations`, { params: { limit } }),
  getTags: (category) => api.get('/books/tags', { params: { category } }),
  getPopularTags: (limit) => api.get('/books/tags/popular', { params: { limit } }),
  // Admin
  createBook: (data) => api.post('/books', data),
  updateBook: (id, data) => api.put(`/books/${id}`, data),
  deleteBook: (id) => api.delete(`/books/${id}`),
  createTag: (data) => api.post('/books/tags', data)
};

// Authors API
export const authorsAPI = {
  getAll: (params) => api.get('/authors', { params }),
  getById: (id) => api.get(`/authors/${id}`),
  search: (query) => api.get('/authors/search', { params: { query } }),
  getBooks: (id, params) => api.get(`/authors/${id}/books`, { params }),
  create: (data) => api.post('/authors', data),
  update: (id, data) => api.put(`/authors/${id}`, data),
  delete: (id) => api.delete(`/authors/${id}`)
};

// Publishers API
export const publishersAPI = {
  getAll: (params) => api.get('/publishers', { params }),
  getById: (id) => api.get(`/publishers/${id}`),
  search: (query) => api.get('/publishers/search', { params: { query } }),
  getBooks: (id, params) => api.get(`/publishers/${id}/books`, { params }),
  create: (data) => api.post('/publishers', data),
  update: (id, data) => api.put(`/publishers/${id}`, data),
  delete: (id) => api.delete(`/publishers/${id}`)
};

// Reviews API
export const reviewsAPI = {
  getByBook: (bookId, params) => api.get(`/reviews/book/${bookId}`, { params }),
  getUserReviews: (params) => api.get('/reviews/user', { params }),
  create: (data) => api.post('/reviews', data),
  update: (id, data) => api.put(`/reviews/${id}`, data),
  delete: (id) => api.delete(`/reviews/${id}`),
  markHelpful: (id) => api.post(`/reviews/${id}/helpful`),
  // Moderator
  getPending: (params) => api.get('/reviews/pending', { params }),
  approve: (id) => api.put(`/reviews/${id}/approve`),
  reject: (id) => api.delete(`/reviews/${id}/reject`)
};

// Favorites API
export const favoritesAPI = {
  getAll: (params) => api.get('/favorites', { params }),
  getCounts: () => api.get('/favorites/counts'),
  check: (bookId) => api.get(`/favorites/check/${bookId}`),
  add: (bookId, listName) => api.post('/favorites', { book_id: bookId, list_name: listName }),
  remove: (bookId, listName) => api.delete(`/favorites/${bookId}`, { params: { list_name: listName } }),
  updateList: (bookId, oldListName, newListName) => api.put(`/favorites/${bookId}/list`, { old_list_name: oldListName, new_list_name: newListName })
};

// Recommendations API
export const recommendationsAPI = {
  getPersonalized: (limit) => api.get('/recommendations/personalized', { params: { limit } }),
  getHybrid: (bookId, limit) => api.get('/recommendations/hybrid', { params: { book_id: bookId, limit } }),
  getPopular: (limit) => api.get('/recommendations/popular', { params: { limit } }),
  getPopularSearches: (limit) => api.get('/recommendations/searches/popular', { params: { limit } }),
  recordInteraction: (bookId, type, weight) => api.post('/recommendations/interaction', { book_id: bookId, interaction_type: type, weight }),
  getSearchHistory: (limit) => api.get('/recommendations/history', { params: { limit } }),
  clearSearchHistory: () => api.delete('/recommendations/history'),
  getSearchSuggestions: (query) => api.get('/recommendations/suggestions', { params: { query } })
};

export default api;
