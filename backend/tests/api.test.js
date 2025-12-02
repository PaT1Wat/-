const request = require('supertest');

// Mock Firebase Admin
jest.mock('firebase-admin', () => ({
  apps: [],
  initializeApp: jest.fn(),
  credential: {
    cert: jest.fn()
  },
  auth: () => ({
    verifyIdToken: jest.fn().mockRejectedValue(new Error('Mock error'))
  })
}));

// Mock database
jest.mock('../src/config/database', () => ({
  query: jest.fn(),
  pool: {
    on: jest.fn()
  }
}));

const app = require('../src/app');

describe('Health Check', () => {
  it('should return healthy status', async () => {
    const res = await request(app).get('/health');
    expect(res.statusCode).toEqual(200);
    expect(res.body).toHaveProperty('status', 'healthy');
    expect(res.body).toHaveProperty('timestamp');
  });
});

describe('API Routes', () => {
  it('should return 404 for unknown routes', async () => {
    const res = await request(app).get('/api/unknown');
    expect(res.statusCode).toEqual(404);
    expect(res.body).toHaveProperty('error', 'Route not found');
  });
});

describe('Books API', () => {
  const db = require('../src/config/database');
  
  beforeEach(() => {
    db.query.mockReset();
  });

  it('should get popular books', async () => {
    db.query.mockResolvedValueOnce({
      rows: [
        { id: '1', title: 'Test Manga', average_rating: 4.5 }
      ]
    });

    const res = await request(app).get('/api/books/popular');
    expect(res.statusCode).toEqual(200);
    expect(Array.isArray(res.body)).toBe(true);
  });

  it('should search books', async () => {
    db.query.mockResolvedValueOnce({
      rows: []
    });
    db.query.mockResolvedValueOnce({
      rows: [{ count: '0' }]
    });

    const res = await request(app).get('/api/books/search?query=test');
    expect(res.statusCode).toEqual(200);
    expect(res.body).toHaveProperty('books');
    expect(res.body).toHaveProperty('total');
  });

  it('should get autocomplete suggestions', async () => {
    db.query.mockResolvedValueOnce({
      rows: [
        { id: '1', title: 'Test', title_th: 'ทดสอบ' }
      ]
    });

    const res = await request(app).get('/api/books/autocomplete?query=test');
    expect(res.statusCode).toEqual(200);
    expect(Array.isArray(res.body)).toBe(true);
  });

  it('should return empty for short autocomplete query', async () => {
    const res = await request(app).get('/api/books/autocomplete?query=t');
    expect(res.statusCode).toEqual(200);
    expect(res.body).toEqual([]);
  });
});

describe('Tags API', () => {
  const db = require('../src/config/database');
  
  beforeEach(() => {
    db.query.mockReset();
  });

  it('should get all tags', async () => {
    db.query.mockResolvedValueOnce({
      rows: [
        { id: '1', name: 'Action', name_th: 'แอคชั่น', category: 'genre' },
        { id: '2', name: 'Romance', name_th: 'โรแมนซ์', category: 'genre' }
      ]
    });

    const res = await request(app).get('/api/books/tags');
    expect(res.statusCode).toEqual(200);
    expect(Array.isArray(res.body)).toBe(true);
  });

  it('should get popular tags', async () => {
    db.query.mockResolvedValueOnce({
      rows: [
        { id: '1', name: 'Action', book_count: 100 }
      ]
    });

    const res = await request(app).get('/api/books/tags/popular');
    expect(res.statusCode).toEqual(200);
    expect(Array.isArray(res.body)).toBe(true);
  });
});

describe('Authors API', () => {
  const db = require('../src/config/database');
  
  beforeEach(() => {
    db.query.mockReset();
  });

  it('should get all authors', async () => {
    db.query.mockResolvedValueOnce({
      rows: [{ id: '1', name: 'Test Author', book_count: 5 }]
    });
    db.query.mockResolvedValueOnce({
      rows: [{ count: '1' }]
    });

    const res = await request(app).get('/api/authors');
    expect(res.statusCode).toEqual(200);
    expect(res.body).toHaveProperty('authors');
  });

  it('should search authors', async () => {
    db.query.mockResolvedValueOnce({
      rows: [{ id: '1', name: 'Test' }]
    });

    const res = await request(app).get('/api/authors/search?query=test');
    expect(res.statusCode).toEqual(200);
    expect(Array.isArray(res.body)).toBe(true);
  });
});

describe('Publishers API', () => {
  const db = require('../src/config/database');
  
  beforeEach(() => {
    db.query.mockReset();
  });

  it('should get all publishers', async () => {
    db.query.mockResolvedValueOnce({
      rows: [{ id: '1', name: 'Test Publisher', book_count: 10 }]
    });
    db.query.mockResolvedValueOnce({
      rows: [{ count: '1' }]
    });

    const res = await request(app).get('/api/publishers');
    expect(res.statusCode).toEqual(200);
    expect(res.body).toHaveProperty('publishers');
  });
});

describe('Recommendations API', () => {
  const db = require('../src/config/database');
  
  beforeEach(() => {
    db.query.mockReset();
  });

  it('should get popular books for cold start', async () => {
    db.query.mockResolvedValueOnce({
      rows: [
        { id: '1', title: 'Popular Manga', average_rating: 4.8 }
      ]
    });

    const res = await request(app).get('/api/recommendations/popular');
    expect(res.statusCode).toEqual(200);
    expect(Array.isArray(res.body)).toBe(true);
  });

  it('should get popular searches', async () => {
    db.query.mockResolvedValueOnce({
      rows: [
        { search_query: 'one piece', search_count: 100 }
      ]
    });

    const res = await request(app).get('/api/recommendations/searches/popular');
    expect(res.statusCode).toEqual(200);
    expect(Array.isArray(res.body)).toBe(true);
  });
});
