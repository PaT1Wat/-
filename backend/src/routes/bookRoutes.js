const express = require('express');
const router = express.Router();
const { body, query } = require('express-validator');
const bookController = require('../controllers/bookController');
const { verifyFirebaseToken, optionalAuth, requireAdmin } = require('../middleware/auth');
const { handleValidationErrors } = require('../middleware/errorHandler');

// Public routes
router.get('/', optionalAuth, bookController.getBooks);
router.get('/search', optionalAuth, bookController.searchBooks);
router.get('/autocomplete', bookController.autocomplete);
router.get('/popular', bookController.getPopularBooks);
router.get('/recent', bookController.getRecentBooks);
router.get('/type/:type', bookController.getBooksByType);
router.get('/tags', bookController.getTags);
router.get('/tags/popular', bookController.getPopularTags);
router.get('/:id', optionalAuth, bookController.getBookById);
router.get('/:id/recommendations', optionalAuth, bookController.getBookRecommendations);

// Admin routes
router.post(
  '/',
  verifyFirebaseToken,
  requireAdmin,
  [
    body('title').notEmpty().isLength({ max: 500 }).trim(),
    body('title_th').optional().isLength({ max: 500 }).trim(),
    body('description').optional(),
    body('type').optional().isIn(['manga', 'novel', 'light_novel', 'manhwa', 'manhua']),
    body('status').optional().isIn(['ongoing', 'completed', 'hiatus', 'cancelled']),
    body('publication_year').optional().isInt({ min: 1900, max: 2100 }),
    body('tags').optional().isArray(),
    handleValidationErrors
  ],
  bookController.createBook
);

router.put(
  '/:id',
  verifyFirebaseToken,
  requireAdmin,
  [
    body('title').optional().isLength({ max: 500 }).trim(),
    body('title_th').optional().isLength({ max: 500 }).trim(),
    body('type').optional().isIn(['manga', 'novel', 'light_novel', 'manhwa', 'manhua']),
    body('status').optional().isIn(['ongoing', 'completed', 'hiatus', 'cancelled']),
    body('tags').optional().isArray(),
    handleValidationErrors
  ],
  bookController.updateBook
);

router.delete('/:id', verifyFirebaseToken, requireAdmin, bookController.deleteBook);

// Admin: Create tag
router.post(
  '/tags',
  verifyFirebaseToken,
  requireAdmin,
  [
    body('name').notEmpty().isLength({ max: 100 }).trim(),
    body('name_th').optional().isLength({ max: 100 }).trim(),
    body('category').optional().isIn(['genre', 'theme', 'demographic', 'content_warning']),
    handleValidationErrors
  ],
  bookController.createTag
);

module.exports = router;
