import os
from typing import Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt

from app.config.firebase import verify_firebase_token
from app.models.user import User
from app.schemas.user import TokenData

security = HTTPBearer(auto_error=False)


def get_jwt_secret() -> str:
    """Get and validate JWT secret."""
    secret = os.getenv("JWT_SECRET", "")
    if not secret or len(secret) < 32:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="JWT_SECRET must be set and at least 32 characters long",
        )
    return secret


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> dict:
    """Verify token and return current user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No token provided",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    # Try Firebase token first
    try:
        decoded_token = verify_firebase_token(token)
        user = await User.find_by_firebase_uid(decoded_token["uid"])
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user
    except Exception:
        pass
    
    # Try JWT token as fallback
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])
        user_id = payload.get("userId")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
            )
        user = await User.find_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
            )
        return user
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_optional_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
) -> Optional[dict]:
    """Optional authentication - doesn't fail if no token."""
    if not credentials:
        return None
    
    token = credentials.credentials
    
    # Try Firebase token first
    try:
        decoded_token = verify_firebase_token(token)
        user = await User.find_by_firebase_uid(decoded_token["uid"])
        return user
    except Exception:
        pass
    
    # Try JWT token as fallback
    try:
        payload = jwt.decode(token, get_jwt_secret(), algorithms=["HS256"])
        user_id = payload.get("userId")
        if user_id:
            user = await User.find_by_id(user_id)
            return user
    except JWTError:
        pass
    
    return None


async def require_admin(current_user: dict = Depends(get_current_user)) -> dict:
    """Require admin role."""
    if current_user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return current_user


async def require_moderator(current_user: dict = Depends(get_current_user)) -> dict:
    """Require moderator or admin role."""
    if current_user.get("role") not in ["admin", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Moderator access required",
        )
    return current_user


def create_access_token(user: dict) -> str:
    """Create JWT access token."""
    expires_in = os.getenv("JWT_EXPIRES_IN", "7d")
    # Parse expires_in (e.g., "7d" -> 7 days)
    import datetime
    if expires_in.endswith("d"):
        delta = datetime.timedelta(days=int(expires_in[:-1]))
    elif expires_in.endswith("h"):
        delta = datetime.timedelta(hours=int(expires_in[:-1]))
    else:
        delta = datetime.timedelta(days=7)
    
    expire = datetime.datetime.utcnow() + delta
    
    to_encode = {
        "userId": str(user["id"]),
        "email": user["email"],
        "role": user.get("role", "user"),
        "exp": expire,
    }
    
    return jwt.encode(to_encode, get_jwt_secret(), algorithm="HS256")
