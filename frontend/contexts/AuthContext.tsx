'use client';

import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { onAuthStateChanged, signInWithPopup, signOut, User as FirebaseUser, Auth } from 'firebase/auth';
import { auth, googleProvider } from '@/lib/firebase';
import { authAPI } from '@/lib/api';
import type { User } from '@/lib/types';

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  loginWithGoogle: () => Promise<void>;
  logout: () => Promise<void>;
  updateUser: (userData: User) => void;
  isAuthenticated: boolean;
  isAdmin: boolean;
  isModerator: boolean;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthProviderProps {
  children: ReactNode;
}

export const AuthProvider = ({ children }: AuthProviderProps) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let unsubscribe: (() => void) | undefined;
    let isMounted = true;
    
    const initializeAuth = async () => {
      // Only run in browser
      if (typeof window === 'undefined') {
        return;
      }

      // Check for stored user
      const storedUser = localStorage.getItem('user');
      const storedToken = localStorage.getItem('token');
      
      if (storedUser && storedToken) {
        try {
          if (isMounted) {
            setUser(JSON.parse(storedUser));
          }
        } catch (e) {
          console.error('Error parsing stored user:', e);
        }
      }

      // Only set up Firebase auth listener if auth is initialized
      if (!auth) {
        if (isMounted) {
          setLoading(false);
        }
        return;
      }

      // auth is now guaranteed to be Auth type after the null check above
      const validAuth: Auth = auth;
      unsubscribe = onAuthStateChanged(validAuth, async (firebaseUser: FirebaseUser | null) => {
        if (firebaseUser) {
          try {
            const token = await firebaseUser.getIdToken();
            const response = await authAPI.loginWithFirebase(token);
            const userData = response.data.user;
            
            localStorage.setItem('token', response.data.token);
            localStorage.setItem('user', JSON.stringify(userData));
            if (isMounted) {
              setUser(userData);
            }
          } catch (err) {
            console.error('Auth error:', err);
            if (isMounted) {
              setError(err instanceof Error ? err.message : 'Authentication error');
            }
          }
        }
        if (isMounted) {
          setLoading(false);
        }
      });
    };

    initializeAuth();

    return () => {
      isMounted = false;
      if (unsubscribe) {
        unsubscribe();
      }
    };
  }, []);

  const loginWithGoogle = async () => {
    if (!auth || !googleProvider) {
      setError('Firebase not initialized');
      throw new Error('Firebase not initialized');
    }
    try {
      setError(null);
      await signInWithPopup(auth, googleProvider);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Login failed');
      throw err;
    }
  };

  const logout = async () => {
    if (!auth) {
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setUser(null);
      return;
    }
    try {
      await signOut(auth);
      localStorage.removeItem('token');
      localStorage.removeItem('user');
      setUser(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Logout failed');
      throw err;
    }
  };

  const updateUser = (userData: User) => {
    setUser(userData);
    if (typeof window !== 'undefined') {
      localStorage.setItem('user', JSON.stringify(userData));
    }
  };

  const value: AuthContextType = {
    user,
    loading,
    error,
    loginWithGoogle,
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
