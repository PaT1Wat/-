# Supabase Integration Guide

This document explains how to set up and configure Supabase as the database, authentication, and storage backend for this project.

## Overview

[Supabase](https://supabase.com/) is an open-source Firebase alternative that provides:
- **PostgreSQL Database**: Fully managed PostgreSQL with real-time subscriptions
- **Authentication**: Built-in auth with social providers (Google, GitHub, etc.)
- **Storage**: S3-compatible object storage for files
- **Row Level Security (RLS)**: Fine-grained access control at the database level

## Quick Start

### 1. Create a Supabase Project

1. Go to [Supabase Dashboard](https://app.supabase.com/)
2. Create a new project
3. Wait for the database to be provisioned

### 2. Configure Environment Variables

Copy the example environment file and fill in your Supabase credentials:

```bash
cp .env.example .env
```

Required variables:
```bash
# Supabase Configuration
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
SUPABASE_JWT_SECRET=your-jwt-secret-here

# Database connection string (for migrations)
DATABASE_URL=postgresql://postgres:[YOUR-PASSWORD]@db.[YOUR-PROJECT].supabase.co:5432/postgres
```

Find these values in your Supabase Dashboard:
- **Project URL & Keys**: Project Settings > API
- **JWT Secret**: Project Settings > API > JWT Secret
- **Database URL**: Project Settings > Database > Connection string (URI format)

### 3. Run Database Migrations

#### Option A: Using the local migration script

```bash
# Set up DATABASE_URL in your environment
export DATABASE_URL="postgresql://postgres:password@db.your-project.supabase.co:5432/postgres?sslmode=require"

# Run migrations
./run_migrations_local.sh
```

#### Option B: Using Supabase CLI (recommended for development)

```bash
# Install Supabase CLI
npm install -g supabase

# Link to your project
supabase link --project-ref your-project-ref

# Push migrations
supabase db push
```

#### Option C: Using the SQL Editor

1. Go to Supabase Dashboard > SQL Editor
2. Copy and paste the content from `migrations/*.sql`
3. Execute each migration in order

## Security Best Practices

### API Keys

| Key | Usage | Security Level |
|-----|-------|----------------|
| `SUPABASE_ANON_KEY` | Client-side, respects RLS | Safe to expose |
| `SUPABASE_SERVICE_ROLE_KEY` | Server-side only, bypasses RLS | **NEVER expose** |
| `SUPABASE_JWT_SECRET` | JWT verification on server | **Keep secret** |

### Row Level Security (RLS)

⚠️ **Always enable RLS on tables containing user data!**

RLS ensures that users can only access their own data, even if they bypass your application code. Example policies are included in `migrations/0001_create_samples.sql`.

Basic RLS commands:
```sql
-- Enable RLS on a table
ALTER TABLE your_table ENABLE ROW LEVEL SECURITY;

-- Create a policy for authenticated users
CREATE POLICY "Users can view their own data"
  ON your_table
  FOR SELECT
  USING (auth.uid() = user_id);
```

### Key Rotation

If you've accidentally exposed any keys:

1. Go to Project Settings > API
2. Click "Generate new key" for the compromised key
3. Update your environment variables immediately
4. Redeploy your application

## File Structure

```
supabase/
├── README.md                    # This file
└── MIGRATION_CHECKLIST.md       # Pre-migration checklist

backend/
└── schema.sql                   # Main database schema

# Root scripts
├── run_migrations_local.sh      # Local migration runner
└── run_schema_supabase.sh       # Schema deployment script
```

## GitHub Actions (CI/CD)

The workflow at `.github/workflows/deploy_migrations.yml` automatically runs migrations when you push to `main`.

### Required GitHub Secrets

Set these in your repository settings (Settings > Secrets and variables > Actions):

| Secret | Description |
|--------|-------------|
| `SUPABASE_DATABASE_URL` | PostgreSQL connection string with `sslmode=require` |
| `SUPABASE_SERVICE_ROLE_KEY` | Service role key for admin operations |

## Troubleshooting

### Common Issues

1. **Connection refused**: Ensure your IP is allowed in Supabase Network settings
2. **Permission denied**: Check RLS policies or use service role key for admin tasks
3. **SSL required**: Add `?sslmode=require` to your connection string

### Getting Help

- [Supabase Documentation](https://supabase.com/docs)
- [Supabase GitHub Discussions](https://github.com/supabase/supabase/discussions)
- [Project Issues](https://github.com/your-repo/issues)

## Migration Notes

This project previously used SQLAlchemy with direct PostgreSQL connections. The existing code continues to work with Supabase's PostgreSQL database. See `MIGRATION_CHECKLIST.md` for guidance on migrating existing SQL files.
