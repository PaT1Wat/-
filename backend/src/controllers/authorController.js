const Author = require('../models/Author');

// Get all authors
const getAuthors = async (req, res, next) => {
  try {
    const { page = 1, limit = 20 } = req.query;
    const result = await Author.getAll(parseInt(page), parseInt(limit));
    res.json(result);
  } catch (error) {
    next(error);
  }
};

// Get author by ID
const getAuthorById = async (req, res, next) => {
  try {
    const { id } = req.params;
    const author = await Author.findById(id);
    
    if (!author) {
      return res.status(404).json({ error: 'Author not found' });
    }

    res.json(author);
  } catch (error) {
    next(error);
  }
};

// Create author (Admin)
const createAuthor = async (req, res, next) => {
  try {
    const author = await Author.create(req.body);
    res.status(201).json({
      message: 'Author created successfully',
      author
    });
  } catch (error) {
    next(error);
  }
};

// Update author (Admin)
const updateAuthor = async (req, res, next) => {
  try {
    const { id } = req.params;
    const author = await Author.update(id, req.body);
    
    if (!author) {
      return res.status(404).json({ error: 'Author not found' });
    }

    res.json({
      message: 'Author updated successfully',
      author
    });
  } catch (error) {
    next(error);
  }
};

// Delete author (Admin)
const deleteAuthor = async (req, res, next) => {
  try {
    const { id } = req.params;
    const author = await Author.delete(id);
    
    if (!author) {
      return res.status(404).json({ error: 'Author not found' });
    }

    res.json({ message: 'Author deleted successfully' });
  } catch (error) {
    next(error);
  }
};

// Search authors
const searchAuthors = async (req, res, next) => {
  try {
    const { query, limit = 10 } = req.query;
    
    if (!query) {
      return res.json([]);
    }

    const authors = await Author.search(query, parseInt(limit));
    res.json(authors);
  } catch (error) {
    next(error);
  }
};

// Get author's books
const getAuthorBooks = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { page = 1, limit = 20 } = req.query;
    
    const author = await Author.findById(id);
    if (!author) {
      return res.status(404).json({ error: 'Author not found' });
    }

    const books = await Author.getBooks(id, parseInt(page), parseInt(limit));
    res.json({
      author,
      books
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getAuthors,
  getAuthorById,
  createAuthor,
  updateAuthor,
  deleteAuthor,
  searchAuthors,
  getAuthorBooks
};
