const Publisher = require('../models/Publisher');

// Get all publishers
const getPublishers = async (req, res, next) => {
  try {
    const { page = 1, limit = 20 } = req.query;
    const result = await Publisher.getAll(parseInt(page), parseInt(limit));
    res.json(result);
  } catch (error) {
    next(error);
  }
};

// Get publisher by ID
const getPublisherById = async (req, res, next) => {
  try {
    const { id } = req.params;
    const publisher = await Publisher.findById(id);
    
    if (!publisher) {
      return res.status(404).json({ error: 'Publisher not found' });
    }

    res.json(publisher);
  } catch (error) {
    next(error);
  }
};

// Create publisher (Admin)
const createPublisher = async (req, res, next) => {
  try {
    const publisher = await Publisher.create(req.body);
    res.status(201).json({
      message: 'Publisher created successfully',
      publisher
    });
  } catch (error) {
    next(error);
  }
};

// Update publisher (Admin)
const updatePublisher = async (req, res, next) => {
  try {
    const { id } = req.params;
    const publisher = await Publisher.update(id, req.body);
    
    if (!publisher) {
      return res.status(404).json({ error: 'Publisher not found' });
    }

    res.json({
      message: 'Publisher updated successfully',
      publisher
    });
  } catch (error) {
    next(error);
  }
};

// Delete publisher (Admin)
const deletePublisher = async (req, res, next) => {
  try {
    const { id } = req.params;
    const publisher = await Publisher.delete(id);
    
    if (!publisher) {
      return res.status(404).json({ error: 'Publisher not found' });
    }

    res.json({ message: 'Publisher deleted successfully' });
  } catch (error) {
    next(error);
  }
};

// Search publishers
const searchPublishers = async (req, res, next) => {
  try {
    const { query, limit = 10 } = req.query;
    
    if (!query) {
      return res.json([]);
    }

    const publishers = await Publisher.search(query, parseInt(limit));
    res.json(publishers);
  } catch (error) {
    next(error);
  }
};

// Get publisher's books
const getPublisherBooks = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { page = 1, limit = 20 } = req.query;
    
    const publisher = await Publisher.findById(id);
    if (!publisher) {
      return res.status(404).json({ error: 'Publisher not found' });
    }

    const books = await Publisher.getBooks(id, parseInt(page), parseInt(limit));
    res.json({
      publisher,
      books
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getPublishers,
  getPublisherById,
  createPublisher,
  updatePublisher,
  deletePublisher,
  searchPublishers,
  getPublisherBooks
};
