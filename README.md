# Manga/Novel Recommendation System

A full-stack web application for discovering, reviewing, and getting personalized recommendations for manga, novels, light novels, manhwa, and manhua.

## Features

### User Features
- 🔐 **Authentication** - Login with Google via Firebase
- 🔍 **Search** - Full-text search with filters (type, status, tags, rating, year)
- 📖 **Browse** - View book details, ratings, and reviews
- 💾 **Favorites** - Save books to custom lists (Favorites, Reading, Completed, Plan to Read, Dropped)
- ✍️ **Reviews** - Write and rate books, mark reviews as helpful
- 🤖 **Recommendations** - Get personalized suggestions based on your preferences

### Admin Features
- 📚 Manage Books (CRUD operations)
- 👤 Manage Authors
- 🏢 Manage Publishers
- ✅ Moderate Reviews (approve/reject)

### Technical Features
- 🌍 **Thai Language Support** - Full i18n support for Thai and English
- 📱 **Responsive Design** - Works on desktop, tablet, and mobile
- ⚡ **AI Recommendations** using:
  - TF-IDF + Cosine Similarity for content-based filtering
  - KNN + SVD for collaborative filtering
  - Hybrid approach combining both methods

## Tech Stack

### Backend
- **Runtime**: Node.js with Express
- **Database**: PostgreSQL
- **Authentication**: Firebase Admin SDK + JWT
- **AI/ML**: Natural.js for NLP (TF-IDF)

### Frontend
- **Framework**: React 18
- **Routing**: React Router v6
- **Internationalization**: i18next
- **Authentication**: Firebase Auth
- **HTTP Client**: Axios

## Getting Started

### Prerequisites
- Node.js 18+
- PostgreSQL 13+
- Firebase Project

### Backend Setup

```bash
cd backend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env
# Edit .env with your configuration

# Setup database (run schema.sql in PostgreSQL)
psql -d your_database -f src/config/schema.sql

# Start development server
npm run dev
```

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Copy environment variables
cp .env.example .env
# Edit .env with your Firebase config

# Start development server
npm start
```

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register new user
- `POST /api/auth/login/firebase` - Login with Firebase token
- `GET /api/auth/profile` - Get current user profile
- `PUT /api/auth/profile` - Update profile

### Books
- `GET /api/books` - List books with pagination
- `GET /api/books/search` - Search books with filters
- `GET /api/books/autocomplete` - Autocomplete search
- `GET /api/books/:id` - Get book details
- `GET /api/books/:id/recommendations` - Get similar books
- `POST /api/books` - Create book (admin)
- `PUT /api/books/:id` - Update book (admin)
- `DELETE /api/books/:id` - Delete book (admin)

### Reviews
- `GET /api/reviews/book/:bookId` - Get reviews for a book
- `POST /api/reviews` - Create review
- `PUT /api/reviews/:id` - Update review
- `DELETE /api/reviews/:id` - Delete review

### Favorites
- `GET /api/favorites` - Get user's favorites
- `POST /api/favorites` - Add to favorites
- `DELETE /api/favorites/:bookId` - Remove from favorites

### Recommendations
- `GET /api/recommendations/personalized` - Get personalized recommendations
- `GET /api/recommendations/popular` - Get popular books
- `POST /api/recommendations/interaction` - Record user interaction

## Database Schema

The system uses the following main tables:
- **users** - User accounts
- **books** - Manga/novels
- **authors** - Book authors
- **publishers** - Publishers
- **tags** - Genres and themes
- **reviews** - User reviews and ratings
- **favorites** - User's saved books
- **search_history** - Search history for recommendations
- **user_interactions** - User behavior tracking

## AI Recommendation Algorithm

### Content-Based Filtering (TF-IDF + Cosine Similarity)
- Analyzes book descriptions, titles, and tags
- Finds similar books based on text content
- Works well for new users with limited history

### Collaborative Filtering (KNN + SVD)
- **KNN**: Finds users with similar preferences
- **SVD**: Matrix factorization for latent features
- Predicts ratings based on similar users' behavior

### Hybrid Approach
Combines both methods with configurable weights:
- Content-based: 30%
- KNN: 40%
- SVD: 30%

## License

ISC