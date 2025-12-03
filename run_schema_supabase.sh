#!/bin/bash
# run_schema_supabase.sh
#
# Run a single schema.sql file against the Supabase PostgreSQL database.
# This is useful when you have a complete schema in one file.
#
# Usage:
#   export DATABASE_URL="postgresql://user:pass@host:5432/database?sslmode=require"
#   ./run_schema_supabase.sh [path/to/schema.sql]
#
# If no file is specified, it defaults to ./backend/schema.sql
#
# Requirements:
#   - Either psql installed locally, OR Docker installed
#   - DATABASE_URL environment variable set

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
    echo "Find your connection string in Supabase Dashboard:"
    echo "  Project Settings > Database > Connection string > URI"
    exit 1
fi

# Determine schema file path
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCHEMA_FILE="${1:-${SCRIPT_DIR}/backend/schema.sql}"

if [ ! -f "$SCHEMA_FILE" ]; then
    echo -e "${RED}Error: Schema file not found: ${SCHEMA_FILE}${NC}"
    echo ""
    echo "Usage: ./run_schema_supabase.sh [path/to/schema.sql]"
    echo "Default: ./backend/schema.sql"
    exit 1
fi

echo -e "${GREEN}Schema file: ${SCHEMA_FILE}${NC}"
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
        
        # Get absolute path for Docker volume
        local abs_path=$(cd "$(dirname "$sql_file")" && pwd)/$(basename "$sql_file")
        local dirname=$(dirname "$abs_path")
        local filename=$(basename "$abs_path")
        
        docker run --rm \
            -v "${dirname}:/schema:ro" \
            postgres:15-alpine \
            psql "$DATABASE_URL" -f "/schema/${filename}"
        return $?
    fi
    
    echo -e "${RED}Error: Neither psql nor Docker is available.${NC}"
    echo "Please install either:"
    echo "  - PostgreSQL client (psql)"
    echo "  - Docker"
    return 1
}

# Confirmation prompt
echo -e "${YELLOW}⚠️  Warning: This will run the schema SQL against your database.${NC}"
echo "This may create tables, modify data, or cause other changes."
echo ""
read -p "Do you want to continue? (y/N) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo ""
echo -e "${GREEN}Running schema...${NC}"
echo ""

if run_psql "$SCHEMA_FILE"; then
    echo ""
    echo -e "${GREEN}========================================${NC}"
    echo -e "${GREEN}Schema applied successfully!${NC}"
    echo -e "${GREEN}========================================${NC}"
else
    echo ""
    echo -e "${RED}========================================${NC}"
    echo -e "${RED}Failed to apply schema!${NC}"
    echo -e "${RED}========================================${NC}"
    exit 1
fi
