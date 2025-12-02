const jwt = require('jsonwebtoken');
const User = require('../models/User');
const { admin } = require('../config/firebase');

// Validate JWT_SECRET exists and has sufficient length
const getJwtSecret = () => {
  const secret = process.env.JWT_SECRET;
  if (!secret || secret.length < 32) {
    throw new Error('JWT_SECRET must be set and at least 32 characters long');
  }
  return secret;
};

// Register new user
const register = async (req, res, next) => {
  try {
    const { firebase_uid, email, username, display_name, avatar_url, preferred_language } = req.body;

    // Check if user already exists
    const existingUser = await User.findByEmail(email);
    if (existingUser) {
      return res.status(409).json({ error: 'User with this email already exists' });
    }

    const existingUsername = await User.findByUsername(username);
    if (existingUsername) {
      return res.status(409).json({ error: 'Username already taken' });
    }

    const user = await User.create({
      firebase_uid,
      email,
      username,
      display_name: display_name || username,
      avatar_url,
      preferred_language
    });

    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id, email: user.email, role: user.role },
      getJwtSecret(),
      { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
    );

    res.status(201).json({
      message: 'User registered successfully',
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        display_name: user.display_name,
        avatar_url: user.avatar_url,
        role: user.role
      },
      token
    });
  } catch (error) {
    next(error);
  }
};

// Login with Firebase token
const loginWithFirebase = async (req, res, next) => {
  try {
    const { firebase_token } = req.body;

    // Verify Firebase token
    const decodedToken = await admin.auth().verifyIdToken(firebase_token);
    
    // Find or create user
    let user = await User.findByFirebaseUid(decodedToken.uid);
    
    if (!user) {
      // Create new user from Firebase data
      user = await User.create({
        firebase_uid: decodedToken.uid,
        email: decodedToken.email,
        username: decodedToken.email.split('@')[0] + '_' + Date.now(),
        display_name: decodedToken.name || decodedToken.email.split('@')[0],
        avatar_url: decodedToken.picture
      });
    }

    // Generate JWT token
    const token = jwt.sign(
      { userId: user.id, email: user.email, role: user.role },
      getJwtSecret(),
      { expiresIn: process.env.JWT_EXPIRES_IN || '7d' }
    );

    res.json({
      message: 'Login successful',
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        display_name: user.display_name,
        avatar_url: user.avatar_url,
        role: user.role
      },
      token
    });
  } catch (error) {
    next(error);
  }
};

// Get current user profile
const getProfile = async (req, res, next) => {
  try {
    const user = await User.findById(req.user.id);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({
      id: user.id,
      email: user.email,
      username: user.username,
      display_name: user.display_name,
      avatar_url: user.avatar_url,
      role: user.role,
      preferred_language: user.preferred_language,
      created_at: user.created_at
    });
  } catch (error) {
    next(error);
  }
};

// Update user profile
const updateProfile = async (req, res, next) => {
  try {
    const { display_name, avatar_url, preferred_language } = req.body;
    
    const user = await User.update(req.user.id, {
      display_name,
      avatar_url,
      preferred_language
    });

    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({
      message: 'Profile updated successfully',
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        display_name: user.display_name,
        avatar_url: user.avatar_url,
        role: user.role,
        preferred_language: user.preferred_language
      }
    });
  } catch (error) {
    next(error);
  }
};

// Admin: Get all users
const getAllUsers = async (req, res, next) => {
  try {
    const { page = 1, limit = 20 } = req.query;
    const result = await User.getAll(parseInt(page), parseInt(limit));
    res.json(result);
  } catch (error) {
    next(error);
  }
};

// Admin: Update user role
const updateUserRole = async (req, res, next) => {
  try {
    const { id } = req.params;
    const { role } = req.body;

    if (!['user', 'admin', 'moderator'].includes(role)) {
      return res.status(400).json({ error: 'Invalid role' });
    }

    const user = await User.updateRole(id, role);
    if (!user) {
      return res.status(404).json({ error: 'User not found' });
    }

    res.json({
      message: 'User role updated successfully',
      user: {
        id: user.id,
        email: user.email,
        username: user.username,
        role: user.role
      }
    });
  } catch (error) {
    next(error);
  }
};

module.exports = {
  register,
  loginWithFirebase,
  getProfile,
  updateProfile,
  getAllUsers,
  updateUserRole
};
