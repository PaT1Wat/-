const express = require('express');
const router = express.Router();
const { body } = require('express-validator');
const authController = require('../controllers/authController');
const { verifyFirebaseToken, requireAdmin } = require('../middleware/auth');
const { handleValidationErrors } = require('../middleware/errorHandler');

// Register new user
router.post(
  '/register',
  [
    body('email').isEmail().normalizeEmail(),
    body('username').isLength({ min: 3, max: 50 }).trim(),
    body('display_name').optional().isLength({ max: 255 }).trim(),
    handleValidationErrors
  ],
  authController.register
);

// Login with Firebase token
router.post(
  '/login/firebase',
  [
    body('firebase_token').notEmpty(),
    handleValidationErrors
  ],
  authController.loginWithFirebase
);

// Get current user profile
router.get('/profile', verifyFirebaseToken, authController.getProfile);

// Update user profile
router.put(
  '/profile',
  verifyFirebaseToken,
  [
    body('display_name').optional().isLength({ max: 255 }).trim(),
    body('preferred_language').optional().isIn(['th', 'en', 'ja']),
    handleValidationErrors
  ],
  authController.updateProfile
);

// Admin: Get all users
router.get('/users', verifyFirebaseToken, requireAdmin, authController.getAllUsers);

// Admin: Update user role
router.put(
  '/users/:id/role',
  verifyFirebaseToken,
  requireAdmin,
  [
    body('role').isIn(['user', 'admin', 'moderator']),
    handleValidationErrors
  ],
  authController.updateUserRole
);

module.exports = router;
