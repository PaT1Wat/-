from datetime import datetime
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.config.database import get_db
from app.config.firebase import verify_firebase_token
from app.config.supabase_auth import verify_supabase_token, get_user_id_from_token, get_email_from_token
from app.middleware.auth import create_access_token, get_current_user, require_admin
from app.models import User
from app.schemas import (
    UserCreate, UserUpdate, UserRoleUpdate, UserResponse, 
    UserListResponse, FirebaseLoginRequest, SupabaseLoginRequest, AuthResponse, MessageResponse
)


router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """Register a new user."""
    # Check if email exists
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    
    # Check if username exists
    result = await db.execute(select(User).where(User.username == user_data.username))
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken"
        )
    
    # Create user
    user = User(
        firebase_uid=user_data.firebase_uid,
        email=user_data.email,
        username=user_data.username,
        display_name=user_data.display_name or user_data.username,
        avatar_url=user_data.avatar_url,
        preferred_language=user_data.preferred_language or "th"
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    
    # Generate JWT token
    token = create_access_token({"user_id": str(user.id), "email": user.email, "role": user.role})
    
    return AuthResponse(
        message="User registered successfully",
        user=UserResponse.model_validate(user),
        token=token
    )


@router.post("/login/firebase", response_model=AuthResponse)
async def login_with_firebase(
    login_data: FirebaseLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with Firebase token."""
    # Verify Firebase token
    decoded_token = verify_firebase_token(login_data.firebase_token)
    if not decoded_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token"
        )
    
    # Find or create user
    result = await db.execute(select(User).where(User.firebase_uid == decoded_token["uid"]))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user from Firebase data
        email = decoded_token.get("email", "")
        username = email.split("@")[0] + "_" + str(int(datetime.utcnow().timestamp()))
        
        user = User(
            firebase_uid=decoded_token["uid"],
            email=email,
            username=username,
            display_name=decoded_token.get("name") or email.split("@")[0],
            avatar_url=decoded_token.get("picture")
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    # Generate JWT token
    token = create_access_token({"user_id": str(user.id), "email": user.email, "role": user.role})
    
    return AuthResponse(
        message="Login successful",
        user=UserResponse.model_validate(user),
        token=token
    )


@router.post("/login/supabase", response_model=AuthResponse)
async def login_with_supabase(
    login_data: SupabaseLoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """Login with Supabase Auth token."""
    # Verify Supabase token
    decoded_token = verify_supabase_token(login_data.access_token)
    if not decoded_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Supabase token"
        )
    
    user_id = get_user_id_from_token(decoded_token)
    email = get_email_from_token(decoded_token)
    
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token: missing user ID"
        )
    
    # Find or create user
    result = await db.execute(select(User).where(User.firebase_uid == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create new user from Supabase data
        if not email:
            email = f"{user_id}@supabase.user"
        username = email.split("@")[0] + "_" + str(int(datetime.utcnow().timestamp()))
        
        # Get user metadata from token if available
        user_metadata = decoded_token.get("user_metadata", {})
        
        user = User(
            # Note: firebase_uid field is reused to store Supabase user IDs for backward compatibility
            firebase_uid=user_id,
            email=email,
            username=username,
            display_name=user_metadata.get("full_name") or user_metadata.get("name") or email.split("@")[0],
            avatar_url=user_metadata.get("avatar_url") or user_metadata.get("picture")
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
    
    # Generate JWT token
    token = create_access_token({"user_id": str(user.id), "email": user.email, "role": user.role})
    
    return AuthResponse(
        message="Login successful",
        user=UserResponse.model_validate(user),
        token=token
    )


@router.get("/profile", response_model=UserResponse)
async def get_profile(
    current_user: User = Depends(get_current_user)
):
    """Get current user profile."""
    return UserResponse.model_validate(current_user)


@router.put("/profile", response_model=dict)
async def update_profile(
    profile_data: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update user profile."""
    if profile_data.display_name is not None:
        current_user.display_name = profile_data.display_name
    if profile_data.avatar_url is not None:
        current_user.avatar_url = profile_data.avatar_url
    if profile_data.preferred_language is not None:
        current_user.preferred_language = profile_data.preferred_language
    
    await db.commit()
    await db.refresh(current_user)
    
    return {
        "message": "Profile updated successfully",
        "user": UserResponse.model_validate(current_user)
    }


@router.get("/users", response_model=UserListResponse)
async def get_all_users(
    page: int = 1,
    limit: int = 20,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Get all users (Admin only)."""
    offset = (page - 1) * limit
    
    # Get users
    result = await db.execute(
        select(User)
        .order_by(User.created_at.desc())
        .offset(offset)
        .limit(limit)
    )
    users = result.scalars().all()
    
    # Get total count
    count_result = await db.execute(select(func.count(User.id)))
    total = count_result.scalar_one()
    
    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
        page=page,
        total_pages=(total + limit - 1) // limit
    )


@router.put("/users/{user_id}/role", response_model=dict)
async def update_user_role(
    user_id: UUID,
    role_data: UserRoleUpdate,
    admin: User = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """Update user role (Admin only)."""
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    user.role = role_data.role
    await db.commit()
    await db.refresh(user)
    
    return {
        "message": "User role updated successfully",
        "user": UserResponse.model_validate(user)
    }
