import React, { createContext, useContext, useState, useEffect } from 'react';
import { supabase, signInWithGoogle as supabaseSignInWithGoogle, signOut as supabaseSignOut } from '../services/supabase';
import { authAPI } from '../services/api';
import { 
  isGoogleAuthConfigured, 
  getStoredGoogleUser, 
  storeGoogleUser,
  signOutGoogle 
} from '../services/googleAuth';

const AuthContext = createContext(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [authMode, setAuthMode] = useState('supabase'); // 'supabase' or 'client-only'

  useEffect(() => {
    // Determine auth mode based on configuration
    const isClientOnlyMode = isGoogleAuthConfigured();
    const mode = isClientOnlyMode ? 'client-only' : 'supabase';
    setAuthMode(mode);

    // Check for stored user (client-only mode)
    if (mode === 'client-only') {
      const googleUser = getStoredGoogleUser();
      if (googleUser) {
        setUser(googleUser);
      }
      setLoading(false);
      return; // Skip Supabase initialization in client-only mode
    }

    // Supabase mode: Check for stored user
    const storedUser = localStorage.getItem('user');
    const storedToken = localStorage.getItem('token');
    
    if (storedUser && storedToken) {
      setUser(JSON.parse(storedUser));
    }

    // Listen for Supabase auth state changes
    const { data: { subscription } } = supabase.auth.onAuthStateChange(async (event, session) => {
      if (session?.access_token) {
        try {
          const response = await authAPI.loginWithSupabase(session.access_token);
          const userData = response.data.user;
          
          localStorage.setItem('token', response.data.token);
          localStorage.setItem('user', JSON.stringify(userData));
          setUser(userData);
        } catch (err) {
          console.error('Auth error:', err);
          setError(err.message);
        }
      }
      setLoading(false);
    });

    // Check initial session
    supabase.auth.getSession().then(({ data: { session } }) => {
      if (!session) {
        setLoading(false);
      }
    });

    return () => subscription.unsubscribe();
  }, []);

  const loginWithGoogle = async () => {
    try {
      setError(null);
      // Use Supabase OAuth flow (will be handled in Login.js for client-only mode)
      await supabaseSignInWithGoogle();
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const loginWithGoogleClientOnly = (userData, token) => {
    // Client-only mode: Store user data directly
    storeGoogleUser(userData, token);
    setUser(userData);
  };

  const logout = async () => {
    try {
      if (authMode === 'client-only') {
        signOutGoogle();
        setUser(null);
      } else {
        await supabaseSignOut();
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        setUser(null);
      }
    } catch (err) {
      setError(err.message);
      throw err;
    }
  };

  const updateUser = (userData) => {
    setUser(userData);
    localStorage.setItem('user', JSON.stringify(userData));
  };

  const value = {
    user,
    loading,
    error,
    authMode,
    loginWithGoogle,
    loginWithGoogleClientOnly,
    logout,
    updateUser,
    isAuthenticated: !!user,
    isAdmin: user?.role === 'admin',
    isModerator: user?.role === 'admin' || user?.role === 'moderator'
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};

export default AuthContext;
