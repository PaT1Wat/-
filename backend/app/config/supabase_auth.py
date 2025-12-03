"""
Supabase authentication module for verifying JWT tokens.

This module provides functions to verify Supabase Auth JWT tokens
using the Supabase API or JWT verification.

SECURITY NOTES:
- Supabase tokens are JWTs that can be verified using the JWT secret
- The JWT secret is available in your Supabase project settings
- Use the anon key for client-side operations
- Use the service role key only for server-side admin operations
"""

import logging
from typing import Optional
import httpx
from jose import jwt, JWTError
from functools import lru_cache

from app.config.settings import settings


logger = logging.getLogger(__name__)


def verify_supabase_token(token: str) -> Optional[dict]:
    """
    Verify a Supabase Auth JWT token.
    
    This function verifies the token using the Supabase JWT secret.
    The token contains user information including:
    - sub: User ID (UUID)
    - email: User's email address
    - role: User's role (e.g., 'authenticated')
    - user_metadata: Additional user metadata
    
    Args:
        token: The JWT token from Supabase Auth
        
    Returns:
        dict: Decoded token payload if valid, None otherwise
    """
    if not settings.supabase_jwt_secret:
        logger.warning("SUPABASE_JWT_SECRET not configured, skipping Supabase token verification")
        return None
    
    try:
        # Supabase uses HS256 algorithm for JWT signing
        decoded = jwt.decode(
            token,
            settings.supabase_jwt_secret,
            algorithms=["HS256"],
            audience="authenticated"  # Supabase default audience for authenticated users
        )
        return decoded
    except JWTError as e:
        logger.debug(f"Supabase token verification failed: {e}")
        return None


async def verify_supabase_token_with_api(token: str) -> Optional[dict]:
    """
    Verify a Supabase Auth token by calling the Supabase Auth API.
    
    This is an alternative method that verifies the token by calling
    the Supabase API endpoint. It's more reliable but requires a network call.
    
    Args:
        token: The JWT token from Supabase Auth
        
    Returns:
        dict: User data if token is valid, None otherwise
    """
    if not settings.supabase_url or not settings.supabase_anon_key:
        logger.warning("Supabase URL or anon key not configured")
        return None
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{settings.supabase_url}/auth/v1/user",
                headers={
                    "Authorization": f"Bearer {token}",
                    "apikey": settings.supabase_anon_key
                }
            )
            
            if response.status_code == 200:
                user_data = response.json()
                # Return in a format compatible with our existing code
                return {
                    "uid": user_data.get("id"),
                    "email": user_data.get("email"),
                    "email_verified": user_data.get("email_confirmed_at") is not None,
                    "name": user_data.get("user_metadata", {}).get("full_name"),
                    "picture": user_data.get("user_metadata", {}).get("avatar_url"),
                    "user_metadata": user_data.get("user_metadata", {}),
                    "app_metadata": user_data.get("app_metadata", {})
                }
            else:
                logger.debug(f"Supabase API verification failed: {response.status_code}")
                return None
                
    except Exception as e:
        logger.error(f"Error verifying Supabase token with API: {e}")
        return None


@lru_cache(maxsize=1)
def is_supabase_auth_configured() -> bool:
    """
    Check if Supabase Auth is properly configured.
    
    Returns:
        bool: True if Supabase Auth is configured, False otherwise
    """
    return bool(
        settings.supabase_url and 
        settings.supabase_anon_key and 
        settings.supabase_jwt_secret
    )


def get_user_id_from_token(decoded_token: dict) -> Optional[str]:
    """
    Extract the user ID from a decoded Supabase token.
    
    Args:
        decoded_token: The decoded JWT payload
        
    Returns:
        str: The user ID (UUID) or None if not found
    """
    # For JWT tokens decoded locally, user ID is in 'sub'
    # For API-verified tokens, it might be in 'uid'
    return decoded_token.get("sub") or decoded_token.get("uid")


def get_email_from_token(decoded_token: dict) -> Optional[str]:
    """
    Extract the email from a decoded Supabase token.
    
    Args:
        decoded_token: The decoded JWT payload
        
    Returns:
        str: The user email or None if not found
    """
    return decoded_token.get("email")
