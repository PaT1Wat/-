const express = require('express');
const router = express.Router();
const { body } = require('express-validator');
const authorController = require('../controllers/authorController');
const { verifyFirebaseToken, requireAdmin } = require('../middleware/auth');
const { handleValidationErrors } = require('../middleware/errorHandler');

// Public routes
router.get('/', authorController.getAuthors);
router.get('/search', authorController.searchAuthors);
router.get('/:id', authorController.getAuthorById);
router.get('/:id/books', authorController.getAuthorBooks);

// Admin routes
router.post(
  '/',
  verifyFirebaseToken,
  requireAdmin,
  [
    body('name').notEmpty().isLength({ max: 255 }).trim(),
    body('name_th').optional().isLength({ max: 255 }).trim(),
    body('biography').optional(),
    body('biography_th').optional(),
    handleValidationErrors
  ],
  authorController.createAuthor
);

router.put(
  '/:id',
  verifyFirebaseToken,
  requireAdmin,
  [
    body('name').optional().isLength({ max: 255 }).trim(),
    body('name_th').optional().isLength({ max: 255 }).trim(),
    handleValidationErrors
  ],
  authorController.updateAuthor
);

router.delete('/:id', verifyFirebaseToken, requireAdmin, authorController.deleteAuthor);

module.exports = router;
