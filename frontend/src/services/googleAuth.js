/**
 * Google Identity Services (GSI) for Client-Only Authentication
 * 
 * This module provides client-only Google Sign-In without requiring a backend
 * database or Supabase. It uses Google Identity Services to authenticate users
 * and stores user information in localStorage for demo/testing purposes.
 * 
 * For production use, the ID token should be verified on the server.
 * 
 * Setup:
 * 1. Get a Google Client ID from Google Cloud Console
 * 2. Add REACT_APP_GOOGLE_CLIENT_ID to your .env file
 * 3. Add authorized JavaScript origins in Google Cloud Console
 */

/**
 * Initialize Google Identity Services
 * @returns {Promise<boolean>} True if initialization was successful
 */
export const initializeGoogleAuth = () => {
  return new Promise((resolve) => {
    // Check if google script is already loaded
    if (window.google?.accounts?.id) {
      resolve(true);
      return;
    }

    // Load Google Identity Services script
    const script = document.createElement('script');
    script.src = 'https://accounts.google.com/gsi/client';
    script.async = true;
    script.defer = true;
    script.onload = () => resolve(true);
    script.onerror = () => {
      console.error('Failed to load Google Identity Services');
      resolve(false);
    };
    document.head.appendChild(script);
  });
};

/**
 * Sign in with Google using One Tap or Button
 * @param {Object} options Configuration options
 * @param {string} options.clientId Google Client ID
 * @param {Function} options.onSuccess Callback for successful login
 * @param {Function} options.onError Callback for login error
 * @returns {Object} Google Sign-In instance
 */
export const signInWithGoogle = async ({ clientId, onSuccess, onError }) => {
  if (!clientId) {
    const error = new Error('Google Client ID is not configured. Please set REACT_APP_GOOGLE_CLIENT_ID in your .env file');
    if (onError) onError(error);
    throw error;
  }

  await initializeGoogleAuth();

  if (!window.google?.accounts?.id) {
    const error = new Error('Google Identity Services failed to load');
    if (onError) onError(error);
    throw error;
  }

  // Initialize Google Sign-In
  window.google.accounts.id.initialize({
    client_id: clientId,
    callback: (response) => {
      try {
        // Decode JWT token (basic decode without verification - for demo only)
        const payload = parseJwt(response.credential);
        
        // Create user object from Google profile
        const user = {
          id: payload.sub,
          email: payload.email,
          name: payload.name,
          picture: payload.picture,
          email_verified: payload.email_verified,
          provider: 'google',
          auth_mode: 'client-only'
        };

        if (onSuccess) onSuccess(user, response.credential);
      } catch (error) {
        console.error('Error processing Google Sign-In:', error);
        if (onError) onError(error);
      }
    },
    cancel_on_tap_outside: false,
  });

  return {
    renderButton: (element, options = {}) => {
      const defaultOptions = {
        theme: 'outline',
        size: 'large',
        text: 'signin_with',
        shape: 'rectangular',
        logo_alignment: 'left',
        width: element?.offsetWidth || 300
      };
      
      window.google.accounts.id.renderButton(
        element,
        { ...defaultOptions, ...options }
      );
    },
    prompt: () => {
      window.google.accounts.id.prompt();
    }
  };
};

/**
 * Sign out (client-only)
 * Clears local storage and Google session
 */
export const signOutGoogle = () => {
  // Clear localStorage
  localStorage.removeItem('google_user');
  localStorage.removeItem('google_token');
  
  // Revoke Google token if available
  if (window.google?.accounts?.id) {
    window.google.accounts.id.disableAutoSelect();
  }
};

/**
 * Get stored Google user from localStorage
 * @returns {Object|null} User object or null
 */
export const getStoredGoogleUser = () => {
  try {
    const userStr = localStorage.getItem('google_user');
    if (!userStr) return null;
    
    const user = JSON.parse(userStr);
    
    // Validate user object structure
    if (!user || typeof user !== 'object') {
      console.warn('Invalid user data in localStorage');
      localStorage.removeItem('google_user');
      return null;
    }
    
    // Validate required fields
    if (!user.id || !user.email) {
      console.warn('User data missing required fields');
      localStorage.removeItem('google_user');
      return null;
    }
    
    return user;
  } catch (error) {
    console.error('Error reading stored user:', error);
    localStorage.removeItem('google_user');
    return null;
  }
};

/**
 * Store Google user in localStorage
 * @param {Object} user User object
 * @param {string} token ID token
 */
export const storeGoogleUser = (user, token) => {
  try {
    localStorage.setItem('google_user', JSON.stringify(user));
    localStorage.setItem('google_token', token);
  } catch (error) {
    console.error('Error storing user:', error);
  }
};

/**
 * Parse JWT token (basic decode without verification)
 * WARNING: This is for demo purposes only. In production, verify tokens on the server.
 * @param {string} token JWT token
 * @returns {Object} Decoded token payload
 */
const parseJwt = (token) => {
  try {
    // Validate token format (must have 3 parts)
    const parts = token.split('.');
    if (parts.length !== 3) {
      throw new Error('Invalid token format: expected 3 parts');
    }

    const base64Url = parts[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    
    const payload = JSON.parse(jsonPayload);
    
    // Validate required fields
    if (!payload.sub || !payload.email) {
      throw new Error('Invalid token payload: missing required fields');
    }
    
    return payload;
  } catch (error) {
    throw new Error(`Invalid token format: ${error.message}`);
  }
};

/**
 * Check if Google Client ID is configured
 * @returns {boolean}
 */
export const isGoogleAuthConfigured = () => {
  return !!(process.env.REACT_APP_GOOGLE_CLIENT_ID && 
            process.env.REACT_APP_GOOGLE_CLIENT_ID !== 'your-google-client-id-here');
};

/**
 * Get Google Client ID from environment
 * @returns {string|null}
 */
export const getGoogleClientId = () => {
  return process.env.REACT_APP_GOOGLE_CLIENT_ID || null;
};
