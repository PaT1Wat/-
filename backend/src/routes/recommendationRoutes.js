const express = require('express');
const router = express.Router();
const { body } = require('express-validator');
const recommendationController = require('../controllers/recommendationController');
const { verifyFirebaseToken, requireAdmin } = require('../middleware/auth');
const { handleValidationErrors } = require('../middleware/errorHandler');

// Public routes
router.get('/popular', recommendationController.getPopularBooks);
router.get('/searches/popular', recommendationController.getPopularSearches);

// Authenticated routes
router.get('/personalized', verifyFirebaseToken, recommendationController.getPersonalizedRecommendations);
router.get('/hybrid', verifyFirebaseToken, recommendationController.getHybridRecommendations);
router.get('/content-based', verifyFirebaseToken, recommendationController.getContentBasedRecommendations);
router.get('/collaborative/knn', verifyFirebaseToken, recommendationController.getKNNRecommendations);
router.get('/collaborative/svd', verifyFirebaseToken, recommendationController.getSVDRecommendations);

router.post(
  '/interaction',
  verifyFirebaseToken,
  [
    body('book_id').isUUID(),
    body('interaction_type').isIn(['view', 'click', 'read_more', 'share']),
    body('weight').optional().isFloat({ min: 0, max: 5 }),
    handleValidationErrors
  ],
  recommendationController.recordInteraction
);

router.get('/history', verifyFirebaseToken, recommendationController.getSearchHistory);
router.delete('/history', verifyFirebaseToken, recommendationController.clearSearchHistory);
router.get('/suggestions', verifyFirebaseToken, recommendationController.getSearchSuggestions);

// Admin routes
router.post('/initialize', verifyFirebaseToken, requireAdmin, recommendationController.initializeRecommendations);

module.exports = router;
