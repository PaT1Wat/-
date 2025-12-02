const recommendationService = require('../services/recommendationService');
const UserInteraction = require('../models/UserInteraction');
const SearchHistory = require('../models/SearchHistory');

// Get personalized recommendations
const getPersonalizedRecommendations = async (req, res, next) => {
  try {
    const { limit = 10 } = req.query;
    
    const recommendations = await recommendationService.getPersonalizedRecommendations(
      req.user.id,
      parseInt(limit)
    );

    res.json(recommendations);
  } catch (error) {
    next(error);
  }
};

// Get hybrid recommendations
const getHybridRecommendations = async (req, res, next) => {
  try {
    const { book_id, limit = 10 } = req.query;
    
    const recommendations = await recommendationService.getHybridRecommendations(
      req.user.id,
      book_id,
      parseInt(limit)
    );

    res.json(recommendations);
  } catch (error) {
    next(error);
  }
};

// Get content-based recommendations
const getContentBasedRecommendations = async (req, res, next) => {
  try {
    const { book_id, limit = 10 } = req.query;
    
    if (!book_id) {
      return res.status(400).json({ error: 'book_id is required' });
    }

    const similarities = await recommendationService.getContentBasedRecommendations(
      book_id,
      parseInt(limit)
    );

    res.json(similarities);
  } catch (error) {
    next(error);
  }
};

// Get collaborative filtering recommendations (KNN)
const getKNNRecommendations = async (req, res, next) => {
  try {
    const { limit = 10, k = 5 } = req.query;
    
    const recommendations = await recommendationService.getKNNRecommendations(
      req.user.id,
      parseInt(k),
      parseInt(limit)
    );

    res.json(recommendations);
  } catch (error) {
    next(error);
  }
};

// Get SVD-based recommendations
const getSVDRecommendations = async (req, res, next) => {
  try {
    const { limit = 10, factors = 10 } = req.query;
    
    const recommendations = await recommendationService.getSVDRecommendations(
      req.user.id,
      parseInt(factors),
      parseInt(limit)
    );

    res.json(recommendations);
  } catch (error) {
    next(error);
  }
};

// Get popular books (cold start)
const getPopularBooks = async (req, res, next) => {
  try {
    const { limit = 10 } = req.query;
    const books = await recommendationService.getPopularBooks(parseInt(limit));
    res.json(books);
  } catch (error) {
    next(error);
  }
};

// Record user interaction
const recordInteraction = async (req, res, next) => {
  try {
    const { book_id, interaction_type, weight = 1.0 } = req.body;
    
    const validTypes = ['view', 'click', 'read_more', 'share'];
    if (!validTypes.includes(interaction_type)) {
      return res.status(400).json({ error: 'Invalid interaction type' });
    }

    await UserInteraction.record(req.user.id, book_id, interaction_type, weight);
    res.json({ message: 'Interaction recorded' });
  } catch (error) {
    next(error);
  }
};

// Get user's search history
const getSearchHistory = async (req, res, next) => {
  try {
    const { limit = 20 } = req.query;
    const history = await SearchHistory.getByUserId(req.user.id, parseInt(limit));
    res.json(history);
  } catch (error) {
    next(error);
  }
};

// Clear search history
const clearSearchHistory = async (req, res, next) => {
  try {
    await SearchHistory.clearHistory(req.user.id);
    res.json({ message: 'Search history cleared' });
  } catch (error) {
    next(error);
  }
};

// Get popular searches
const getPopularSearches = async (req, res, next) => {
  try {
    const { limit = 10 } = req.query;
    const searches = await SearchHistory.getPopularSearches(parseInt(limit));
    res.json(searches);
  } catch (error) {
    next(error);
  }
};

// Get search suggestions
const getSearchSuggestions = async (req, res, next) => {
  try {
    const { query } = req.query;
    
    if (!query || query.length < 2) {
      return res.json([]);
    }

    const suggestions = await SearchHistory.getSuggestionsFromHistory(
      req.user.id,
      query
    );
    res.json(suggestions);
  } catch (error) {
    next(error);
  }
};

// Initialize recommendation service (Admin)
const initializeRecommendations = async (req, res, next) => {
  try {
    await recommendationService.initializeTfIdf();
    res.json({ message: 'Recommendation service initialized' });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getPersonalizedRecommendations,
  getHybridRecommendations,
  getContentBasedRecommendations,
  getKNNRecommendations,
  getSVDRecommendations,
  getPopularBooks,
  recordInteraction,
  getSearchHistory,
  clearSearchHistory,
  getPopularSearches,
  getSearchSuggestions,
  initializeRecommendations
};
