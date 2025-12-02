from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from app.config.firebase import verify_firebase_token
from app.middleware.auth import (
    create_access_token,
    get_current_user,
    require_admin,
)
from app.models.user import User
from app.schemas.user import (
    AuthResponse,
    FirebaseLoginRequest,
    ProfileResponse,
    RegisterRequest,
    UserResponse,
    UserRoleUpdate,
    UserUpdate,
)

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(user_data: RegisterRequest):
    """Register a new user."""
    # Check if user already exists
    existing_user = await User.find_by_email(user_data.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )
    
    existing_username = await User.find_by_username(user_data.username)
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already taken",
        )
    
    user = await User.create({
        "firebase_uid": user_data.firebase_uid,
        "email": user_data.email,
        "username": user_data.username,
        "display_name": user_data.display_name or user_data.username,
        "avatar_url": user_data.avatar_url,
        "preferred_language": user_data.preferred_language,
    })
    
    token = create_access_token(user)
    
    return {
        "message": "User registered successfully",
        "user": user,
        "token": token,
    }


@router.post("/login/firebase", response_model=AuthResponse)
async def login_with_firebase(login_data: FirebaseLoginRequest):
    """Login with Firebase token."""
    try:
        decoded_token = verify_firebase_token(login_data.firebase_token)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid Firebase token",
        )
    
    # Find or create user
    user = await User.find_by_firebase_uid(decoded_token["uid"])
    
    if not user:
        # Create new user from Firebase data
        email = decoded_token.get("email", "")
        username = email.split("@")[0] + "_" + str(int(__import__("time").time()))
        
        user = await User.create({
            "firebase_uid": decoded_token["uid"],
            "email": email,
            "username": username,
            "display_name": decoded_token.get("name") or email.split("@")[0],
            "avatar_url": decoded_token.get("picture"),
        })
    
    token = create_access_token(user)
    
    return {
        "message": "Login successful",
        "user": user,
        "token": token,
    }


@router.get("/profile", response_model=ProfileResponse)
async def get_profile(current_user: dict = Depends(get_current_user)):
    """Get current user profile."""
    user = await User.find_by_id(current_user["id"])
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.put("/profile", response_model=dict)
async def update_profile(
    user_data: UserUpdate,
    current_user: dict = Depends(get_current_user),
):
    """Update user profile."""
    user = await User.update(current_user["id"], {
        "display_name": user_data.display_name,
        "avatar_url": user_data.avatar_url,
        "preferred_language": user_data.preferred_language,
    })
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return {
        "message": "Profile updated successfully",
        "user": user,
    }


@router.get("/users")
async def get_all_users(
    page: int = 1,
    limit: int = 20,
    current_user: dict = Depends(require_admin),
):
    """Admin: Get all users."""
    return await User.get_all(page, limit)


@router.put("/users/{user_id}/role")
async def update_user_role(
    user_id: UUID,
    role_data: UserRoleUpdate,
    current_user: dict = Depends(require_admin),
):
    """Admin: Update user role."""
    if role_data.role not in ["user", "admin", "moderator"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid role",
        )
    
    user = await User.update_role(user_id, role_data.role)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    
    return {
        "message": "User role updated successfully",
        "user": {
            "id": user["id"],
            "email": user["email"],
            "username": user["username"],
            "role": user["role"],
        },
    }
