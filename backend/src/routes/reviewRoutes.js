const express = require('express');
const router = express.Router();
const { body } = require('express-validator');
const reviewController = require('../controllers/reviewController');
const { verifyFirebaseToken, requireModerator } = require('../middleware/auth');
const { handleValidationErrors } = require('../middleware/errorHandler');

// Public routes
router.get('/book/:bookId', reviewController.getBookReviews);

// Authenticated routes
router.get('/user', verifyFirebaseToken, reviewController.getUserReviews);
router.get('/user/:userId', reviewController.getUserReviews);

router.post(
  '/',
  verifyFirebaseToken,
  [
    body('book_id').isUUID(),
    body('rating').isInt({ min: 1, max: 5 }),
    body('title').optional().isLength({ max: 255 }).trim(),
    body('content').optional(),
    body('is_spoiler').optional().isBoolean(),
    handleValidationErrors
  ],
  reviewController.createReview
);

router.put(
  '/:id',
  verifyFirebaseToken,
  [
    body('rating').optional().isInt({ min: 1, max: 5 }),
    body('title').optional().isLength({ max: 255 }).trim(),
    body('content').optional(),
    body('is_spoiler').optional().isBoolean(),
    handleValidationErrors
  ],
  reviewController.updateReview
);

router.delete('/:id', verifyFirebaseToken, reviewController.deleteReview);
router.post('/:id/helpful', verifyFirebaseToken, reviewController.markHelpful);

// Moderator routes
router.get('/pending', verifyFirebaseToken, requireModerator, reviewController.getPendingReviews);
router.put('/:id/approve', verifyFirebaseToken, requireModerator, reviewController.approveReview);
router.delete('/:id/reject', verifyFirebaseToken, requireModerator, reviewController.rejectReview);

module.exports = router;
