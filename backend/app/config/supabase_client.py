"""
Supabase client module for database and storage operations.

This module provides a Supabase client instance configured from environment variables.
The client can be used for:
- Database operations (select, insert, update, delete)
- Storage operations (file upload, download)
- Real-time subscriptions

SECURITY NOTES:
- SUPABASE_ANON_KEY: Safe to use on client-side, limited by Row Level Security (RLS).
- SUPABASE_SERVICE_ROLE_KEY: Server-side only! Bypasses RLS.
  NEVER expose the service role key to client bundles or frontend code.

For server-side operations that need to bypass RLS (admin tasks, background jobs),
use get_supabase_admin_client(). For regular user-facing operations that should
respect RLS policies, use get_supabase_client().
"""

import os
from typing import Optional
from functools import lru_cache

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def _get_env_var(name: str, required: bool = True) -> Optional[str]:
    """Get environment variable with optional requirement check."""
    value = os.getenv(name)
    if required and not value:
        raise ValueError(
            f"Missing required environment variable: {name}. "
            f"Please set it in your .env file or environment."
        )
    return value


@lru_cache(maxsize=1)
def get_supabase_client():
    """
    Get the Supabase client using the anon key.
    
    This client respects Row Level Security (RLS) policies and is safe
    to use for user-facing operations where RLS should be enforced.
    
    Returns:
        Client: Supabase client instance
        
    Raises:
        ImportError: If supabase package is not installed
        ValueError: If required environment variables are missing
    """
    try:
        from supabase import create_client, Client
    except ImportError:
        raise ImportError(
            "The 'supabase' package is required. "
            "Install it with: pip install supabase"
        )
    
    url = _get_env_var("SUPABASE_URL")
    anon_key = _get_env_var("SUPABASE_ANON_KEY")
    
    client: Client = create_client(url, anon_key)
    return client


@lru_cache(maxsize=1)
def get_supabase_admin_client():
    """
    Get the Supabase client using the service role key.
    
    WARNING: This client bypasses Row Level Security (RLS) policies.
    Use only for server-side admin operations, background jobs, or
    operations that explicitly need to bypass RLS.
    
    NEVER expose this client or the service role key to client-side code!
    
    Returns:
        Client: Supabase admin client instance
        
    Raises:
        ImportError: If supabase package is not installed
        ValueError: If required environment variables are missing
    """
    try:
        from supabase import create_client, Client
    except ImportError:
        raise ImportError(
            "The 'supabase' package is required. "
            "Install it with: pip install supabase"
        )
    
    url = _get_env_var("SUPABASE_URL")
    service_role_key = _get_env_var("SUPABASE_SERVICE_ROLE_KEY")
    
    client: Client = create_client(url, service_role_key)
    return client


# Example usage functions for common operations
# TODO: These are placeholder examples - update table names and columns
# to match your actual Supabase schema.
#
# Note: The supabase-py client uses synchronous HTTP calls under the hood.
# These functions are kept synchronous for simplicity. For async FastAPI
# endpoints, consider running these in a thread pool executor or using
# the async httpx client directly.

def fetch_items_example(table_name: str = "items", limit: int = 10):
    """
    Example function demonstrating how to fetch rows from a Supabase table.
    
    This is a sample implementation. Replace 'items' with your actual table name.
    
    Args:
        table_name: Name of the table to query
        limit: Maximum number of rows to return
        
    Returns:
        list: List of rows from the table
    """
    client = get_supabase_client()
    
    response = client.table(table_name).select("*").limit(limit).execute()
    
    return response.data


def insert_item_example(table_name: str, data: dict):
    """
    Example function demonstrating how to insert a row into a Supabase table.
    
    Args:
        table_name: Name of the table to insert into
        data: Dictionary of column names and values
        
    Returns:
        dict: The inserted row data
    """
    client = get_supabase_client()
    
    response = client.table(table_name).insert(data).execute()
    
    return response.data


def upload_file_example(bucket_name: str, file_path: str, file_data: bytes):
    """
    Example function demonstrating how to upload a file to Supabase Storage.
    
    Args:
        bucket_name: Name of the storage bucket
        file_path: Path where the file will be stored in the bucket
        file_data: The file content as bytes
        
    Returns:
        dict: Upload response from Supabase
    """
    client = get_supabase_client()
    
    response = client.storage.from_(bucket_name).upload(file_path, file_data)
    
    return response
