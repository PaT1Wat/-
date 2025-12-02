const express = require('express');
const router = express.Router();
const { body } = require('express-validator');
const publisherController = require('../controllers/publisherController');
const { verifyFirebaseToken, requireAdmin } = require('../middleware/auth');
const { handleValidationErrors } = require('../middleware/errorHandler');

// Public routes
router.get('/', publisherController.getPublishers);
router.get('/search', publisherController.searchPublishers);
router.get('/:id', publisherController.getPublisherById);
router.get('/:id/books', publisherController.getPublisherBooks);

// Admin routes
router.post(
  '/',
  verifyFirebaseToken,
  requireAdmin,
  [
    body('name').notEmpty().isLength({ max: 255 }).trim(),
    body('name_th').optional().isLength({ max: 255 }).trim(),
    body('description').optional(),
    body('website_url').optional().isURL(),
    handleValidationErrors
  ],
  publisherController.createPublisher
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
  publisherController.updatePublisher
);

router.delete('/:id', verifyFirebaseToken, requireAdmin, publisherController.deletePublisher);

module.exports = router;
