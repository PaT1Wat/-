const { admin } = require('../config/firebase');
const User = require('../models/User');
const jwt = require('jsonwebtoken');

// Verify Firebase token
const verifyFirebaseToken = async (req, res, next) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    return res.status(401).json({ error: 'No token provided' });
  }

  const token = authHeader.split('Bearer ')[1];

  try {
    // Try Firebase token first
    const decodedToken = await admin.auth().verifyIdToken(token);
    const user = await User.findByFirebaseUid(decodedToken.uid);
    
    if (!user) {
      return res.status(401).json({ error: 'User not found' });
    }
    
    req.user = user;
    req.firebaseUser = decodedToken;
    next();
  } catch (firebaseError) {
    // Try JWT token as fallback
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      const user = await User.findById(decoded.userId);
      
      if (!user) {
        return res.status(401).json({ error: 'User not found' });
      }
      
      req.user = user;
      next();
    } catch (jwtError) {
      return res.status(401).json({ error: 'Invalid token' });
    }
  }
};

// Optional authentication - doesn't fail if no token
const optionalAuth = async (req, res, next) => {
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    req.user = null;
    return next();
  }

  const token = authHeader.split('Bearer ')[1];

  try {
    const decodedToken = await admin.auth().verifyIdToken(token);
    const user = await User.findByFirebaseUid(decodedToken.uid);
    req.user = user;
    req.firebaseUser = decodedToken;
  } catch (firebaseError) {
    try {
      const decoded = jwt.verify(token, process.env.JWT_SECRET);
      const user = await User.findById(decoded.userId);
      req.user = user;
    } catch (jwtError) {
      req.user = null;
    }
  }
  
  next();
};

// Admin role check
const requireAdmin = (req, res, next) => {
  if (!req.user || req.user.role !== 'admin') {
    return res.status(403).json({ error: 'Admin access required' });
  }
  next();
};

// Moderator or Admin role check
const requireModerator = (req, res, next) => {
  if (!req.user || (req.user.role !== 'admin' && req.user.role !== 'moderator')) {
    return res.status(403).json({ error: 'Moderator access required' });
  }
  next();
};

module.exports = {
  verifyFirebaseToken,
  optionalAuth,
  requireAdmin,
  requireModerator
};
