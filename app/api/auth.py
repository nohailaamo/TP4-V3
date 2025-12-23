"""
Authentication API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from datetime import datetime

from app.core.database import get_db
from app.models.database import User
from app.models.schemas import UserCreate, UserResponse, Token, MessageResponse
from app.services.auth import auth_service
from app.utils.encryption import pseudonymize_identifier
from app.api.dependencies import get_current_user, require_admin


router = APIRouter(prefix="/api/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register a new user.
    
    Requires GDPR consent to be given.
    """
    # Check if username already exists
    result = await db.execute(
        select(User).where(User.username == user_data.username)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    result = await db.execute(
        select(User).where(User.email == user_data.email)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Verify consent
    if not user_data.consent_given:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User consent is required for registration (GDPR compliance)"
        )
    
    # Create user
    hashed_password = auth_service.get_password_hash(user_data.password)
    pseudonym = pseudonymize_identifier(user_data.username)
    
    new_user = User(
        username=user_data.username,
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        role=user_data.role,
        pseudonym=pseudonym,
        consent_given=user_data.consent_given,
        consent_date=datetime.utcnow() if user_data.consent_given else None,
        is_verified=True  # Auto-verify for demo purposes
    )
    
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    
    return new_user


@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Login with username and password to get JWT token.
    """
    # Get user
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()
    
    if not user or not auth_service.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    # Create access token
    access_token = auth_service.create_access_token(
        data={
            "sub": user.username,
            "user_id": user.id,
            "role": user.role.value
        }
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current user information.
    """
    return current_user


@router.delete("/user/{user_id}", response_model=MessageResponse)
async def delete_user_data(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(require_admin)
):
    """
    Delete user data (GDPR right to be forgotten).
    
    Admin only. Deletes user and all associated biometric data.
    """
    # Get user
    result = await db.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Delete user (cascade will handle biometric data)
    await db.delete(user)
    await db.commit()
    
    return {
        "message": f"User {user.username} and all associated data deleted successfully",
        "success": True
    }
