const express = require('express');
const router = express.Router();
const { body } = require('express-validator');
const favoriteController = require('../controllers/favoriteController');
const { verifyFirebaseToken } = require('../middleware/auth');
const { handleValidationErrors } = require('../middleware/errorHandler');

// All routes require authentication
router.use(verifyFirebaseToken);

router.get('/', favoriteController.getFavorites);
router.get('/counts', favoriteController.getListCounts);
router.get('/check/:bookId', favoriteController.checkFavorite);

router.post(
  '/',
  [
    body('book_id').isUUID(),
    body('list_name').optional().isIn(['favorites', 'reading', 'completed', 'plan_to_read', 'dropped']),
    handleValidationErrors
  ],
  favoriteController.addFavorite
);

router.delete('/:bookId', favoriteController.removeFavorite);

router.put(
  '/:bookId/list',
  [
    body('old_list_name').isIn(['favorites', 'reading', 'completed', 'plan_to_read', 'dropped']),
    body('new_list_name').isIn(['favorites', 'reading', 'completed', 'plan_to_read', 'dropped']),
    handleValidationErrors
  ],
  favoriteController.updateFavoriteList
);

module.exports = router;
