"""
API dependencies for authentication and authorization.
"""
from fastapi import Depends, HTTPException, status, UploadFile, File
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional

from app.core.database import get_db
from app.models.database import User, UserRole
from app.services.auth import auth_service
from app.models.schemas import TokenData


# OAuth2 scheme
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        token: JWT access token
        db: Database session
        
    Returns:
        User object
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Decode token
    payload = auth_service.decode_token(token)
    if payload is None:
        raise credentials_exception
    
    username: str = payload.get("sub")
    if username is None:
        raise credentials_exception
    
    # Get user from database
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    
    if user is None:
        raise credentials_exception
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get the current active user.
    
    Args:
        current_user: Current user from token
        
    Returns:
        Active user object
        
    Raises:
        HTTPException: If user is not active or verified
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user"
        )
    
    if not current_user.consent_given:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User consent not given. Biometric operations require consent."
        )
    
    return current_user


def require_role(required_role: UserRole):
    """
    Dependency factory for role-based access control.
    
    Args:
        required_role: Required user role
        
    Returns:
        Dependency function
    """
    async def role_checker(current_user: User = Depends(get_current_active_user)) -> User:
        if current_user.role != required_role and current_user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation requires {required_role.value} role"
            )
        return current_user
    
    return role_checker


async def require_admin(current_user: User = Depends(get_current_active_user)) -> User:
    """
    Require admin role.
    
    Args:
        current_user: Current user
        
    Returns:
        User with admin role
        
    Raises:
        HTTPException: If user is not admin
    """
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    return current_user


async def validate_biometric_file(
    file: UploadFile = File(...)
) -> bytes:
    """
    Validate and read biometric file upload.
    
    Args:
        file: Uploaded file
        
    Returns:
        File contents as bytes
        
    Raises:
        HTTPException: If file is invalid
    """
    # Check file size (max 10MB)
    max_size = 10 * 1024 * 1024
    
    content = await file.read()
    
    if len(content) > max_size:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File too large. Maximum size is 10MB"
        )
    
    if len(content) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file"
        )
    
    # Validate file type based on content
    # Check for common image formats (JPEG, PNG)
    is_image = (
        content.startswith(b'\xff\xd8\xff') or  # JPEG
        content.startswith(b'\x89PNG') or  # PNG
        content.startswith(b'GIF')  # GIF
    )
    
    # Check for common audio formats
    is_audio = (
        content.startswith(b'RIFF') or  # WAV
        content.startswith(b'fLaC') or  # FLAC
        content.startswith(b'ID3') or content[4:8] == b'ftyp'  # MP3, MP4
    )
    
    if not (is_image or is_audio):
        # Allow it anyway - some formats may not have clear signatures
        pass
    
    return content
