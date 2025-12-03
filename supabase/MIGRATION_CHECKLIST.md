# Supabase Migration Checklist

This checklist helps you identify and resolve compatibility issues when migrating existing SQL schemas and migrations to Supabase.

## Pre-Migration Checks

### 1. Unsupported PostgreSQL Features

Supabase runs managed PostgreSQL with some restrictions. Check your SQL files for:

#### ❌ Statements That Will Fail

| Statement | Issue | Solution |
|-----------|-------|----------|
| `CREATE DATABASE` | Supabase provides one database | Remove; use provided database |
| `CREATE ROLE` / `CREATE USER` | Managed by Supabase | Use Supabase Auth instead |
| `ALTER ROLE` / `ALTER USER` | Managed by Supabase | Remove these statements |
| `GRANT SUPERUSER` | No superuser access | Remove; use RLS policies |
| `DROP DATABASE` | Not permitted | Remove from migrations |
| `CREATE TABLESPACE` | Managed storage | Remove; use default tablespace |

#### ⚠️ Extension Availability

Some extensions may not be available. Check the [Supabase Extensions List](https://supabase.com/docs/guides/database/extensions).

**Available extensions** (commonly used):
- `uuid-ossp` ✅
- `pg_trgm` ✅
- `pgcrypto` ✅
- `postgis` ✅
- `pgjwt` ✅

**To enable an extension in Supabase:**
```sql
CREATE EXTENSION IF NOT EXISTS "extension_name";
```

### 2. Schema Compatibility

Run this command to scan your schema for potential issues:

```bash
# Check for CREATE DATABASE statements
grep -n "CREATE DATABASE" backend/schema.sql migrations/*.sql 2>/dev/null

# Check for CREATE ROLE/USER statements
grep -n -E "CREATE (ROLE|USER)" backend/schema.sql migrations/*.sql 2>/dev/null

# Check for SUPERUSER references
grep -n "SUPERUSER" backend/schema.sql migrations/*.sql 2>/dev/null

# Check for GRANT statements that might need adjustment
grep -n "^GRANT" backend/schema.sql migrations/*.sql 2>/dev/null
```

### 3. Connection String Format

Ensure your connection string follows this format:

```
postgresql://postgres:[PASSWORD]@db.[PROJECT_REF].supabase.co:5432/postgres?sslmode=require
```

**Required parameters:**
- `sslmode=require` - Supabase requires SSL connections
- Port `5432` (default) or `6543` (for connection pooling via Supavisor)

## Migration Execution Checklist

Before running migrations, verify:

- [ ] All `CREATE DATABASE` statements removed
- [ ] All `CREATE ROLE/USER` statements removed
- [ ] All `SUPERUSER` grants removed
- [ ] All required extensions are available in Supabase
- [ ] Connection string includes `sslmode=require`
- [ ] RLS is enabled on tables with user data
- [ ] RLS policies are defined for each table

## Row Level Security (RLS) Setup

### Enable RLS on All User-Data Tables

```sql
-- Enable RLS
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE reviews ENABLE ROW LEVEL SECURITY;
ALTER TABLE favorites ENABLE ROW LEVEL SECURITY;
ALTER TABLE search_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_interactions ENABLE ROW LEVEL SECURITY;
```

### Common RLS Patterns

#### Pattern 1: Users can only access their own data
```sql
CREATE POLICY "Users can read own data"
  ON table_name
  FOR SELECT
  USING (auth.uid() = user_id);

CREATE POLICY "Users can insert own data"
  ON table_name
  FOR INSERT
  WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own data"
  ON table_name
  FOR UPDATE
  USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own data"
  ON table_name
  FOR DELETE
  USING (auth.uid() = user_id);
```

#### Pattern 2: Public read, authenticated write
```sql
CREATE POLICY "Anyone can read"
  ON table_name
  FOR SELECT
  USING (true);

CREATE POLICY "Authenticated users can insert"
  ON table_name
  FOR INSERT
  WITH CHECK (auth.role() = 'authenticated');
```

#### Pattern 3: Admin-only access
```sql
CREATE POLICY "Admin full access"
  ON table_name
  USING (
    auth.uid() IN (
      SELECT id FROM users WHERE role = 'admin'
    )
  );
```

## Post-Migration Verification

After running migrations, verify:

- [ ] All tables created successfully
- [ ] Indexes created correctly
- [ ] Foreign key constraints active
- [ ] Triggers functioning
- [ ] RLS policies enforced
- [ ] Test queries return expected results

### Verification Queries

```sql
-- List all tables
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';

-- Check RLS status
SELECT tablename, rowsecurity 
FROM pg_tables 
WHERE schemaname = 'public';

-- List all policies
SELECT * FROM pg_policies WHERE schemaname = 'public';
```

## Common Migration Fixes

### Fix 1: Replace `uuid_generate_v4()` with `gen_random_uuid()`

If `uuid-ossp` is not available, use the built-in PostgreSQL function:

```sql
-- Before
id UUID PRIMARY KEY DEFAULT uuid_generate_v4()

-- After (PostgreSQL 13+)
id UUID PRIMARY KEY DEFAULT gen_random_uuid()
```

### Fix 2: Add SSL Mode to Connection

```python
# Python SQLAlchemy
DATABASE_URL = "postgresql+asyncpg://postgres:pass@db.xxx.supabase.co:5432/postgres?ssl=require"
```

```javascript
// Node.js
const connectionString = "postgresql://postgres:pass@db.xxx.supabase.co:5432/postgres?sslmode=require";
```

### Fix 3: Handle Missing Extensions

```sql
-- Check if extension exists before using
DO $$
BEGIN
  IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'pg_trgm') THEN
    CREATE INDEX IF NOT EXISTS idx_search ON books USING gin (title gin_trgm_ops);
  END IF;
END $$;
```

## Resources

- [Supabase Database Documentation](https://supabase.com/docs/guides/database)
- [PostgreSQL to Supabase Migration Guide](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)
