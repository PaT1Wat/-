const Favorite = require('../models/Favorite');

// Get user's favorites
const getFavorites = async (req, res, next) => {
  try {
    const { list_name, page = 1, limit = 20 } = req.query;
    const result = await Favorite.getByUserId(
      req.user.id, 
      list_name, 
      parseInt(page), 
      parseInt(limit)
    );
    res.json(result);
  } catch (error) {
    next(error);
  }
};

// Add to favorites
const addFavorite = async (req, res, next) => {
  try {
    const { book_id, list_name = 'favorites' } = req.body;
    
    const favorite = await Favorite.add(req.user.id, book_id, list_name);
    
    if (!favorite) {
      return res.status(409).json({ error: 'Book already in this list' });
    }

    res.status(201).json({
      message: 'Book added to favorites',
      favorite
    });
  } catch (error) {
    next(error);
  }
};

// Remove from favorites
const removeFavorite = async (req, res, next) => {
  try {
    const { bookId } = req.params;
    const { list_name } = req.query;
    
    const favorite = await Favorite.remove(req.user.id, bookId, list_name);
    
    if (!favorite) {
      return res.status(404).json({ error: 'Favorite not found' });
    }

    res.json({ message: 'Book removed from favorites' });
  } catch (error) {
    next(error);
  }
};

// Check if book is in favorites
const checkFavorite = async (req, res, next) => {
  try {
    const { bookId } = req.params;
    const lists = await Favorite.checkFavorite(req.user.id, bookId);
    
    res.json({
      isFavorite: lists.length > 0,
      lists: lists.map(l => l.list_name)
    });
  } catch (error) {
    next(error);
  }
};

// Move book to different list
const updateFavoriteList = async (req, res, next) => {
  try {
    const { bookId } = req.params;
    const { old_list_name, new_list_name } = req.body;
    
    const favorite = await Favorite.updateList(
      req.user.id, 
      bookId, 
      old_list_name, 
      new_list_name
    );
    
    if (!favorite) {
      return res.status(404).json({ error: 'Favorite not found' });
    }

    res.json({
      message: 'List updated successfully',
      favorite
    });
  } catch (error) {
    next(error);
  }
};

// Get list counts
const getListCounts = async (req, res, next) => {
  try {
    const counts = await Favorite.getListCounts(req.user.id);
    res.json(counts);
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getFavorites,
  addFavorite,
  removeFavorite,
  checkFavorite,
  updateFavoriteList,
  getListCounts
};
