-- Sample Migration: Create sample tables with Row Level Security (RLS)
-- 
-- This migration demonstrates Supabase-compatible table creation with:
-- - UUID primary keys using uuid_generate_v4()
-- - Timestamps with timezone
-- - Row Level Security (RLS) policies for authenticated users
--
-- NOTE: This is a sample migration. For your actual schema, see backend/schema.sql
-- and adapt it following the patterns shown here.

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- ============================================================================
-- Sample Users Table
-- ============================================================================
-- This table stores user information synced from Supabase Auth.
-- The 'id' column should match auth.uid() for RLS policies to work.

CREATE TABLE IF NOT EXISTS sample_users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    username VARCHAR(100) UNIQUE NOT NULL,
    display_name VARCHAR(255),
    avatar_url TEXT,
    role VARCHAR(20) DEFAULT 'user' CHECK (role IN ('user', 'admin', 'moderator')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Enable Row Level Security
ALTER TABLE sample_users ENABLE ROW LEVEL SECURITY;

-- RLS Policies for sample_users
-- Policy: Anyone can view user profiles (public read)
CREATE POLICY "sample_users_select_public"
    ON sample_users
    FOR SELECT
    USING (true);

-- Policy: Users can update their own profile
CREATE POLICY "sample_users_update_own"
    ON sample_users
    FOR UPDATE
    USING (auth.uid() = id)
    WITH CHECK (auth.uid() = id);

-- Policy: Only authenticated users can insert (for registration)
CREATE POLICY "sample_users_insert_authenticated"
    ON sample_users
    FOR INSERT
    WITH CHECK (auth.uid() = id);

-- ============================================================================
-- Sample Items Table
-- ============================================================================
-- Demonstrates a table with foreign key to users and appropriate RLS.

CREATE TABLE IF NOT EXISTS sample_items (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES sample_users(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    is_public BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Enable Row Level Security
ALTER TABLE sample_items ENABLE ROW LEVEL SECURITY;

-- RLS Policies for sample_items
-- Policy: Anyone can view public items
CREATE POLICY "sample_items_select_public"
    ON sample_items
    FOR SELECT
    USING (is_public = true);

-- Policy: Users can view their own items (public or private)
CREATE POLICY "sample_items_select_own"
    ON sample_items
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can insert their own items
CREATE POLICY "sample_items_insert_own"
    ON sample_items
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own items
CREATE POLICY "sample_items_update_own"
    ON sample_items
    FOR UPDATE
    USING (auth.uid() = user_id)
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own items
CREATE POLICY "sample_items_delete_own"
    ON sample_items
    FOR DELETE
    USING (auth.uid() = user_id);

-- ============================================================================
-- Indexes for Performance
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_sample_users_email ON sample_users(email);
CREATE INDEX IF NOT EXISTS idx_sample_users_username ON sample_users(username);
CREATE INDEX IF NOT EXISTS idx_sample_items_user_id ON sample_items(user_id);
CREATE INDEX IF NOT EXISTS idx_sample_items_created_at ON sample_items(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sample_items_title ON sample_items USING gin (title gin_trgm_ops);

-- ============================================================================
-- Trigger for updated_at
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to sample_users
DROP TRIGGER IF EXISTS update_sample_users_updated_at ON sample_users;
CREATE TRIGGER update_sample_users_updated_at
    BEFORE UPDATE ON sample_users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Apply trigger to sample_items
DROP TRIGGER IF EXISTS update_sample_items_updated_at ON sample_items;
CREATE TRIGGER update_sample_items_updated_at
    BEFORE UPDATE ON sample_items
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- Sample Data (Optional - comment out for production)
-- ============================================================================
-- Uncomment the following to insert sample data for testing:
--
-- INSERT INTO sample_users (id, email, username, display_name, role)
-- VALUES 
--     ('00000000-0000-0000-0000-000000000001', 'admin@example.com', 'admin', 'Administrator', 'admin'),
--     ('00000000-0000-0000-0000-000000000002', 'user@example.com', 'testuser', 'Test User', 'user');
--
-- INSERT INTO sample_items (user_id, title, description, is_public)
-- VALUES 
--     ('00000000-0000-0000-0000-000000000002', 'My First Item', 'This is a public item', true),
--     ('00000000-0000-0000-0000-000000000002', 'Private Notes', 'This is private', false);
