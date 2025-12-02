const Review = require('../models/Review');

// Get reviews for a book
const getBookReviews = async (req, res, next) => {
  try {
    const { bookId } = req.params;
    const { page = 1, limit = 10, sort_by = 'created_at' } = req.query;
    
    const result = await Review.getByBookId(bookId, parseInt(page), parseInt(limit), sort_by);
    res.json(result);
  } catch (error) {
    next(error);
  }
};

// Get user's reviews
const getUserReviews = async (req, res, next) => {
  try {
    const userId = req.params.userId || req.user.id;
    const { page = 1, limit = 10 } = req.query;
    
    const result = await Review.getByUserId(userId, parseInt(page), parseInt(limit));
    res.json(result);
  } catch (error) {
    next(error);
  }
};

// Create review
const createReview = async (req, res, next) => {
  try {
    const { book_id, rating, title, content, is_spoiler } = req.body;

    // Check if user already reviewed this book
    const existingReview = await Review.findByUserAndBook(req.user.id, book_id);
    if (existingReview) {
      return res.status(409).json({ error: 'You have already reviewed this book' });
    }

    const review = await Review.create({
      user_id: req.user.id,
      book_id,
      rating,
      title,
      content,
      is_spoiler
    });

    const createdReview = await Review.findById(review.id);
    res.status(201).json({
      message: 'Review created successfully',
      review: createdReview
    });
  } catch (error) {
    next(error);
  }
};

// Update review
const updateReview = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { rating, title, content, is_spoiler } = req.body;

    const review = await Review.update(id, req.user.id, {
      rating,
      title,
      content,
      is_spoiler
    });

    if (!review) {
      return res.status(404).json({ error: 'Review not found or not authorized' });
    }

    const updatedReview = await Review.findById(id);
    res.json({
      message: 'Review updated successfully',
      review: updatedReview
    });
  } catch (error) {
    next(error);
  }
};

// Delete review
const deleteReview = async (req, res, next) => {
  try {
    const { id } = req.params;
    
    // Admin can delete any review, users can only delete their own
    const review = req.user.role === 'admin' 
      ? await Review.delete(id)
      : await Review.delete(id, req.user.id);

    if (!review) {
      return res.status(404).json({ error: 'Review not found or not authorized' });
    }

    res.json({ message: 'Review deleted successfully' });
  } catch (error) {
    next(error);
  }
};

// Mark review as helpful
const markHelpful = async (req, res, next) => {
  try {
    const { id } = req.params;
    const review = await Review.incrementHelpful(id);

    if (!review) {
      return res.status(404).json({ error: 'Review not found' });
    }

    res.json({
      message: 'Review marked as helpful',
      helpful_count: review.helpful_count
    });
  } catch (error) {
    next(error);
  }
};

// Moderator: Get pending reviews
const getPendingReviews = async (req, res, next) => {
  try {
    const { page = 1, limit = 20 } = req.query;
    const result = await Review.getPendingReviews(parseInt(page), parseInt(limit));
    res.json(result);
  } catch (error) {
    next(error);
  }
};

// Moderator: Approve review
const approveReview = async (req, res, next) => {
  try {
    const { id } = req.params;
    const review = await Review.approve(id);

    if (!review) {
      return res.status(404).json({ error: 'Review not found' });
    }

    res.json({
      message: 'Review approved successfully',
      review
    });
  } catch (error) {
    next(error);
  }
};

// Moderator: Reject review
const rejectReview = async (req, res, next) => {
  try {
    const { id } = req.params;
    const review = await Review.reject(id);

    if (!review) {
      return res.status(404).json({ error: 'Review not found' });
    }

    res.json({ message: 'Review rejected successfully' });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  getBookReviews,
  getUserReviews,
  createReview,
  updateReview,
  deleteReview,
  markHelpful,
  getPendingReviews,
  approveReview,
  rejectReview
};
