#!/bin/bash
# run_migrations_local.sh
#
# Run SQL migrations against a PostgreSQL database locally.
# This script uses Docker to run psql if it's not installed natively.
#
# Usage:
#   export DATABASE_URL="postgresql://user:pass@host:5432/database?sslmode=require"
#   ./run_migrations_local.sh
#
# Or specify DATABASE_URL directly:
#   DATABASE_URL="postgresql://..." ./run_migrations_local.sh
#
# Requirements:
#   - Either psql installed locally, OR Docker installed
#   - DATABASE_URL environment variable set
#   - Migration files in the migrations/ directory

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check for DATABASE_URL
if [ -z "$DATABASE_URL" ]; then
    echo -e "${RED}Error: DATABASE_URL environment variable is not set.${NC}"
    echo ""
    echo "Set it with:"
    echo "  export DATABASE_URL=\"postgresql://postgres:password@db.your-project.supabase.co:5432/postgres?sslmode=require\""
    echo ""
    echo "Or pass it directly:"
    echo "  DATABASE_URL=\"postgresql://...\" ./run_migrations_local.sh"
    exit 1
fi

# Find migrations directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
MIGRATIONS_DIR="${SCRIPT_DIR}/migrations"

if [ ! -d "$MIGRATIONS_DIR" ]; then
    echo -e "${RED}Error: Migrations directory not found at ${MIGRATIONS_DIR}${NC}"
    exit 1
fi

# Find all .sql files, sorted alphabetically
SQL_FILES=$(find "$MIGRATIONS_DIR" -name "*.sql" -type f | sort)

if [ -z "$SQL_FILES" ]; then
    echo -e "${YELLOW}No SQL files found in ${MIGRATIONS_DIR}${NC}"
    exit 0
fi

echo -e "${GREEN}Found migration files:${NC}"
for file in $SQL_FILES; do
    echo "  - $(basename "$file")"
done
echo ""

# Function to run psql
run_psql() {
    local sql_file="$1"
    
    # Try native psql first
    if command -v psql &> /dev/null; then
        echo -e "${GREEN}Using native psql...${NC}"
        psql "$DATABASE_URL" -f "$sql_file"
        return $?
    fi
    
    # Fall back to Docker
    if command -v docker &> /dev/null; then
        echo -e "${YELLOW}psql not found, using Docker...${NC}"
        
        # Extract just the filename for mounting
        local filename=$(basename "$sql_file")
        local dirname=$(dirname "$sql_file")
        
        # Note: DATABASE_URL already contains credentials, so no PGPASSWORD needed
        docker run --rm \
            -v "${dirname}:/migrations:ro" \
            postgres:15-alpine \
            psql "$DATABASE_URL" -f "/migrations/${filename}"
        return $?
    fi
    
    echo -e "${RED}Error: Neither psql nor Docker is available.${NC}"
    echo "Please install either:"
    echo "  - PostgreSQL client (psql)"
    echo "  - Docker"
    return 1
}

# Run each migration
echo -e "${GREEN}Running migrations...${NC}"
echo ""

for sql_file in $SQL_FILES; do
    filename=$(basename "$sql_file")
    echo -e "${YELLOW}>>> Running: ${filename}${NC}"
    
    if run_psql "$sql_file"; then
        echo -e "${GREEN}✓ Successfully ran: ${filename}${NC}"
    else
        echo -e "${RED}✗ Failed to run: ${filename}${NC}"
        exit 1
    fi
    
    echo ""
done

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}All migrations completed successfully!${NC}"
echo -e "${GREEN}========================================${NC}"
