/**
 * Supabase JavaScript Client Example
 *
 * This module demonstrates how to configure and use the Supabase JavaScript client
 * for database operations, authentication, and storage.
 *
 * Requirements:
 *   npm install @supabase/supabase-js
 *
 * Usage (Node.js):
 *   import { getClient, fetchBooks, signInWithGoogle } from './supabase_client.js';
 *
 *   const client = getClient();
 *   const { data: books } = await fetchBooks({ limit: 10 });
 *
 * Usage (Browser/React):
 *   import { supabase, signInWithGoogle } from './supabase_client.js';
 *
 *   const handleLogin = async () => {
 *     const { error } = await signInWithGoogle();
 *     if (error) console.error(error);
 *   };
 *
 * Security Notes:
 *   - SUPABASE_ANON_KEY: Safe for client-side, respects RLS
 *   - SUPABASE_SERVICE_ROLE_KEY: Server-side only, bypasses RLS
 *   - NEVER expose the service role key in browser/frontend code!
 */

// For Node.js environments
// const { createClient } = require('@supabase/supabase-js');

// For ES modules / browser
import { createClient } from '@supabase/supabase-js';

// ============================================================================
// Configuration
// ============================================================================

// For browser (React/Vue/etc.), use environment variables with REACT_APP_ or VITE_ prefix
const SUPABASE_URL = process.env.SUPABASE_URL ||
    process.env.REACT_APP_SUPABASE_URL ||
    process.env.VITE_SUPABASE_URL;

const SUPABASE_ANON_KEY = process.env.SUPABASE_ANON_KEY ||
    process.env.REACT_APP_SUPABASE_ANON_KEY ||
    process.env.VITE_SUPABASE_ANON_KEY;

// Validate configuration
if (!SUPABASE_URL || !SUPABASE_ANON_KEY) {
    throw new Error(
        'Supabase configuration missing. Set SUPABASE_URL and SUPABASE_ANON_KEY ' +
        'in your environment variables.'
    );
}

// ============================================================================
// Client Initialization
// ============================================================================

/**
 * Supabase client instance.
 *
 * This client uses the anon key and respects Row Level Security (RLS).
 * Safe to use in browser/frontend code.
 */
export const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    auth: {
        persistSession: true,
        autoRefreshToken: true,
        detectSessionInUrl: true
    }
});

/**
 * Get Supabase client (alternative getter function).
 *
 * @returns {SupabaseClient} The Supabase client instance
 */
export function getClient() {
    return supabase;
}

// ============================================================================
// Authentication Functions
// ============================================================================

/**
 * Sign in with Google OAuth.
 *
 * This redirects the user to Google's OAuth page and back to your app.
 *
 * @param {string} redirectTo - URL to redirect to after sign-in
 * @returns {Promise<{data, error}>} Auth response
 *
 * @example
 * const { error } = await signInWithGoogle('https://myapp.com/dashboard');
 */
export async function signInWithGoogle(redirectTo) {
    const { data, error } = await supabase.auth.signInWithOAuth({
        provider: 'google',
        options: {
            redirectTo: redirectTo || window.location.origin
        }
    });
    return { data, error };
}

/**
 * Sign in with email and password.
 *
 * @param {string} email - User's email
 * @param {string} password - User's password
 * @returns {Promise<{data, error}>} Auth response
 *
 * @example
 * const { data, error } = await signInWithEmail('user@example.com', 'password123');
 */
export async function signInWithEmail(email, password) {
    const { data, error } = await supabase.auth.signInWithPassword({
        email,
        password
    });
    return { data, error };
}

/**
 * Sign up with email and password.
 *
 * @param {string} email - User's email
 * @param {string} password - User's password
 * @param {Object} metadata - Optional user metadata
 * @returns {Promise<{data, error}>} Auth response
 */
export async function signUpWithEmail(email, password, metadata = {}) {
    const { data, error } = await supabase.auth.signUp({
        email,
        password,
        options: {
            data: metadata
        }
    });
    return { data, error };
}

/**
 * Sign out the current user.
 *
 * @returns {Promise<{error}>} Sign out response
 */
export async function signOut() {
    const { error } = await supabase.auth.signOut();
    return { error };
}

/**
 * Get the current authenticated user.
 *
 * @returns {Promise<{data, error}>} User data or null
 */
export async function getCurrentUser() {
    const { data: { user }, error } = await supabase.auth.getUser();
    return { user, error };
}

/**
 * Listen for authentication state changes.
 *
 * @param {Function} callback - Function to call on auth state change
 * @returns {Function} Unsubscribe function
 *
 * @example
 * const unsubscribe = onAuthStateChange((event, session) => {
 *   if (event === 'SIGNED_IN') {
 *     console.log('User signed in:', session.user);
 *   }
 * });
 */
export function onAuthStateChange(callback) {
    const { data: { subscription } } = supabase.auth.onAuthStateChange(callback);
    return () => subscription.unsubscribe();
}

// ============================================================================
// Database Operations
// ============================================================================

/**
 * Fetch books from the database.
 *
 * @param {Object} options - Query options
 * @param {number} options.limit - Maximum number of books (default: 10)
 * @param {number} options.offset - Number of books to skip (default: 0)
 * @param {string} options.type - Filter by book type
 * @param {string} options.status - Filter by status
 * @returns {Promise<{data, error}>} Books data
 *
 * @example
 * const { data: books, error } = await fetchBooks({
 *   limit: 20,
 *   type: 'manga',
 *   status: 'ongoing'
 * });
 */
export async function fetchBooks({ limit = 10, offset = 0, type, status } = {}) {
    let query = supabase
        .from('books')
        .select(`
            *,
            authors (id, name),
            publishers (id, name)
        `)
        .order('created_at', { ascending: false })
        .range(offset, offset + limit - 1);

    if (type) {
        query = query.eq('type', type);
    }

    if (status) {
        query = query.eq('status', status);
    }

    const { data, error } = await query;
    return { data, error };
}

/**
 * Get a single book by ID.
 *
 * @param {string} bookId - UUID of the book
 * @returns {Promise<{data, error}>} Book data
 */
export async function getBookById(bookId) {
    const { data, error } = await supabase
        .from('books')
        .select(`
            *,
            authors (id, name, biography),
            publishers (id, name),
            book_tags (
                tags (id, name)
            )
        `)
        .eq('id', bookId)
        .single();

    return { data, error };
}

/**
 * Create a review for a book.
 *
 * @param {Object} review - Review data
 * @param {string} review.bookId - UUID of the book
 * @param {number} review.rating - Rating from 1-5
 * @param {string} review.content - Review content
 * @param {string} review.title - Optional review title
 * @param {boolean} review.isSpoiler - Whether review contains spoilers
 * @returns {Promise<{data, error}>} Created review
 */
export async function createReview({ bookId, rating, content, title = null, isSpoiler = false }) {
    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
        return { data: null, error: { message: 'User must be authenticated to create reviews' } };
    }

    const { data, error } = await supabase
        .from('reviews')
        .insert({
            user_id: user.id,
            book_id: bookId,
            rating,
            content,
            title,
            is_spoiler: isSpoiler
        })
        .select()
        .single();

    return { data, error };
}

/**
 * Get reviews for a book.
 *
 * @param {string} bookId - UUID of the book
 * @param {Object} options - Query options
 * @returns {Promise<{data, error}>} Reviews data
 */
export async function getBookReviews(bookId, { limit = 10, offset = 0 } = {}) {
    const { data, error } = await supabase
        .from('reviews')
        .select(`
            *,
            users (id, username, display_name, avatar_url)
        `)
        .eq('book_id', bookId)
        .eq('is_approved', true)
        .order('created_at', { ascending: false })
        .range(offset, offset + limit - 1);

    return { data, error };
}

/**
 * Add a book to favorites.
 *
 * @param {string} bookId - UUID of the book
 * @param {string} listName - List type (favorites, reading, completed, plan_to_read, dropped)
 * @returns {Promise<{data, error}>} Created favorite
 */
export async function addToFavorites(bookId, listName = 'favorites') {
    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
        return { data: null, error: { message: 'User must be authenticated' } };
    }

    const { data, error } = await supabase
        .from('favorites')
        .insert({
            user_id: user.id,
            book_id: bookId,
            list_name: listName
        })
        .select()
        .single();

    return { data, error };
}

/**
 * Get user's favorites.
 *
 * @param {string} listName - Optional filter by list type
 * @returns {Promise<{data, error}>} Favorites with book details
 */
export async function getFavorites(listName = null) {
    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
        return { data: null, error: { message: 'User must be authenticated' } };
    }

    let query = supabase
        .from('favorites')
        .select(`
            *,
            books (id, title, cover_image_url, type, status, average_rating)
        `)
        .eq('user_id', user.id)
        .order('created_at', { ascending: false });

    if (listName) {
        query = query.eq('list_name', listName);
    }

    const { data, error } = await query;
    return { data, error };
}

/**
 * Remove a book from favorites.
 *
 * @param {string} bookId - UUID of the book
 * @param {string} listName - Optional list name filter
 * @returns {Promise<{error}>} Delete result
 */
export async function removeFromFavorites(bookId, listName = null) {
    const { data: { user } } = await supabase.auth.getUser();

    if (!user) {
        return { error: { message: 'User must be authenticated' } };
    }

    let query = supabase
        .from('favorites')
        .delete()
        .eq('user_id', user.id)
        .eq('book_id', bookId);

    if (listName) {
        query = query.eq('list_name', listName);
    }

    const { error } = await query;
    return { error };
}

// ============================================================================
// Storage Functions
// ============================================================================

/**
 * Upload a file to Supabase Storage.
 *
 * @param {string} bucket - Storage bucket name
 * @param {string} path - File path in the bucket
 * @param {File|Blob} file - File to upload
 * @returns {Promise<{data, error}>} Upload result
 */
export async function uploadFile(bucket, path, file) {
    const { data, error } = await supabase.storage
        .from(bucket)
        .upload(path, file, {
            cacheControl: '3600',
            upsert: false
        });

    return { data, error };
}

/**
 * Get public URL for a file.
 *
 * @param {string} bucket - Storage bucket name
 * @param {string} path - File path in the bucket
 * @returns {string} Public URL
 */
export function getPublicUrl(bucket, path) {
    const { data } = supabase.storage.from(bucket).getPublicUrl(path);
    return data.publicUrl;
}

// ============================================================================
// Real-time Subscriptions
// ============================================================================

/**
 * Subscribe to real-time changes on a table.
 *
 * @param {string} table - Table name to subscribe to
 * @param {Function} callback - Function to call on changes
 * @param {Object} options - Subscription options
 * @returns {Object} Subscription channel (call .unsubscribe() to stop)
 *
 * @example
 * const channel = subscribeToTable('reviews', (payload) => {
 *   console.log('Review changed:', payload);
 * }, { filter: 'book_id=eq.some-uuid' });
 *
 * // Later, to unsubscribe:
 * channel.unsubscribe();
 */
export function subscribeToTable(table, callback, { filter, event = '*' } = {}) {
    let channel = supabase
        .channel(`public:${table}`)
        .on(
            'postgres_changes',
            {
                event,
                schema: 'public',
                table,
                filter
            },
            callback
        )
        .subscribe();

    return channel;
}

// ============================================================================
// Export default client for convenience
// ============================================================================

export default supabase;
