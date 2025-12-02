import os
from databases import Database
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/manga_recommendation")

# Convert postgresql:// to postgresql+asyncpg:// if needed for async support
if DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

database = Database(DATABASE_URL)


async def get_database():
    """Dependency to get database connection."""
    return database
