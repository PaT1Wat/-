const Book = require('../models/Book');
const Tag = require('../models/Tag');
const SearchHistory = require('../models/SearchHistory');
const UserInteraction = require('../models/UserInteraction');
const recommendationService = require('../services/recommendationService');

// Get all books with pagination and filtering
const getBooks = async (req, res, next) => {
  try {
    const result = await Book.search(req.query);
    res.json(result);
  } catch (error) {
    next(error);
  }
};

// Get single book by ID
const getBookById = async (req, res, next) => {
  try {
    const { id } = req.params;
    const book = await Book.findById(id);
    
    if (!book) {
      return res.status(404).json({ error: 'Book not found' });
    }

    // Increment view count
    await Book.incrementViewCount(id);

    // Record user interaction if authenticated
    if (req.user) {
      await UserInteraction.record(req.user.id, id, 'view', 1.0);
    }

    res.json(book);
  } catch (error) {
    next(error);
  }
};

// Create new book (Admin)
const createBook = async (req, res, next) => {
  try {
    const bookData = req.body;
    const book = await Book.create(bookData);

    // Add tags if provided
    if (bookData.tags && bookData.tags.length > 0) {
      await Book.addTags(book.id, bookData.tags);
    }

    const createdBook = await Book.findById(book.id);
    res.status(201).json({
      message: 'Book created successfully',
      book: createdBook
    });
  } catch (error) {
    next(error);
  }
};

// Update book (Admin)
const updateBook = async (req, res, next) => {
  try {
    const { id } = req.params;
    const bookData = req.body;

    const existingBook = await Book.findById(id);
    if (!existingBook) {
      return res.status(404).json({ error: 'Book not found' });
    }

    const book = await Book.update(id, bookData);

    // Update tags if provided
    if (bookData.tags !== undefined) {
      // Get current tags
      const currentTags = existingBook.tags.map(t => t.id);
      const newTags = bookData.tags;
      
      // Remove old tags
      if (currentTags.length > 0) {
        await Book.removeTags(id, currentTags);
      }
      
      // Add new tags
      if (newTags.length > 0) {
        await Book.addTags(id, newTags);
      }
    }

    const updatedBook = await Book.findById(id);
    res.json({
      message: 'Book updated successfully',
      book: updatedBook
    });
  } catch (error) {
    next(error);
  }
};

// Delete book (Admin)
const deleteBook = async (req, res, next) => {
  try {
    const { id } = req.params;
    const book = await Book.delete(id);
    
    if (!book) {
      return res.status(404).json({ error: 'Book not found' });
    }

    res.json({ message: 'Book deleted successfully' });
  } catch (error) {
    next(error);
  }
};

// Search books with full-text search
const searchBooks = async (req, res, next) => {
  try {
    const { query, type, status, tags, author_id, publisher_id, 
            min_rating, year_from, year_to, sort_by, sort_order, page, limit } = req.query;

    // Parse tags if it's a string
    const parsedTags = tags ? (typeof tags === 'string' ? tags.split(',') : tags) : undefined;

    const result = await Book.search({
      query,
      type,
      status,
      tags: parsedTags,
      author_id,
      publisher_id,
      min_rating: min_rating ? parseFloat(min_rating) : undefined,
      year_from: year_from ? parseInt(year_from) : undefined,
      year_to: year_to ? parseInt(year_to) : undefined,
      sort_by,
      sort_order,
      page: page ? parseInt(page) : 1,
      limit: limit ? parseInt(limit) : 20
    });

    // Save search history if user is authenticated
    if (req.user && query) {
      await SearchHistory.add(req.user.id, query, req.query, result.total);
    }

    res.json(result);
  } catch (error) {
    next(error);
  }
};

// Autocomplete search
const autocomplete = async (req, res, next) => {
  try {
    const { query } = req.query;
    
    if (!query || query.length < 2) {
      return res.json([]);
    }

    const results = await Book.autocomplete(query);
    res.json(results);
  } catch (error) {
    next(error);
  }
};

// Get popular books
const getPopularBooks = async (req, res, next) => {
  try {
    const { limit = 10 } = req.query;
    const books = await Book.getPopular(parseInt(limit));
    res.json(books);
  } catch (error) {
    next(error);
  }
};

// Get recent books
const getRecentBooks = async (req, res, next) => {
  try {
    const { limit = 10 } = req.query;
    const books = await Book.getRecent(parseInt(limit));
    res.json(books);
  } catch (error) {
    next(error);
  }
};

// Get books by type
const getBooksByType = async (req, res, next) => {
  try {
    const { type } = req.params;
    const { limit = 20, page = 1 } = req.query;
    const books = await Book.getByType(type, parseInt(limit), parseInt(page));
    res.json(books);
  } catch (error) {
    next(error);
  }
};

// Get recommendations for a book
const getBookRecommendations = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { limit = 10 } = req.query;

    // Check if book exists
    const book = await Book.findById(id);
    if (!book) {
      return res.status(404).json({ error: 'Book not found' });
    }

    // Get similar books based on tags
    const similar = await recommendationService.getSimilarBooksByTags(id, parseInt(limit));
    
    // If user is authenticated, get hybrid recommendations
    let recommendations = similar;
    if (req.user) {
      recommendations = await recommendationService.getHybridRecommendations(
        req.user.id, 
        id, 
        parseInt(limit)
      );
      
      // Fallback to similar books if no recommendations
      if (recommendations.length === 0) {
        recommendations = similar;
      }
    }

    res.json(recommendations);
  } catch (error) {
    next(error);
  }
};

// Get all tags
const getTags = async (req, res, next) => {
  try {
    const { category } = req.query;
    const tags = category ? await Tag.getByCategory(category) : await Tag.getAll();
    res.json(tags);
  } catch (error) {
    next(error);
  }
};

// Create tag (Admin)
const createTag = async (req, res, next) => {
  try {
    const tag = await Tag.create(req.body);
    res.status(201).json({
      message: 'Tag created successfully',
      tag
    });
  } catch (error) {
    next(error);
  }
};

// Get popular tags
const getPopularTags = async (req, res, next) => {
  try {
    const { limit = 20 } = req.query;
    const tags = await Tag.getPopular(parseInt(limit));
    res.json(tags);
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getBooks,
  getBookById,
  createBook,
  updateBook,
  deleteBook,
  searchBooks,
  autocomplete,
  getPopularBooks,
  getRecentBooks,
  getBooksByType,
  getBookRecommendations,
  getTags,
  createTag,
  getPopularTags
};
