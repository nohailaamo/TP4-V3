"""
Biometric API endpoints for enrollment and authentication.
"""
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.database import User, BiometricType
from app.models.schemas import (
    BiometricEnrollResponse,
    BiometricAuthResponse,
    BiometricTypeEnum
)
from app.services.biometric import biometric_service
from app.api.dependencies import get_current_active_user, validate_biometric_file


router = APIRouter(prefix="/api/biometric", tags=["Biometric"])


@router.post("/enroll", response_model=BiometricEnrollResponse)
async def enroll_biometric(
    biometric_type: BiometricTypeEnum = Form(...),
    consent_confirmed: bool = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Enroll biometric data for the current user.
    
    - **biometric_type**: Type of biometric (face, voice, fingerprint)
    - **consent_confirmed**: User must confirm consent for biometric processing
    - **file**: Biometric data file (image for face, audio for voice)
    
    Returns enrollment status and quality score.
    """
    # Verify consent
    if not consent_confirmed:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Consent must be confirmed for biometric enrollment"
        )
    
    if not current_user.consent_given:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User consent not given in profile. Please update consent settings."
        )
    
    # Validate file
    biometric_data = await validate_biometric_file(file)
    
    # Convert enum to BiometricType
    bio_type = BiometricType[biometric_type.value.upper()]
    
    # Enroll biometric
    result = await biometric_service.enroll_biometric(
        db=db,
        user_id=current_user.id,
        biometric_type=bio_type,
        biometric_data=biometric_data
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return BiometricEnrollResponse(**result)


@router.post("/authenticate", response_model=BiometricAuthResponse)
async def authenticate_biometric(
    biometric_type: BiometricTypeEnum = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Authenticate user using biometric data.
    
    - **biometric_type**: Type of biometric (face, voice, fingerprint)
    - **file**: Biometric data file to verify
    
    Returns authentication result with similarity score.
    """
    # Validate file
    biometric_data = await validate_biometric_file(file)
    
    # Convert enum to BiometricType
    bio_type = BiometricType[biometric_type.value.upper()]
    
    # Authenticate
    result = await biometric_service.authenticate_biometric(
        db=db,
        user_id=current_user.id,
        biometric_type=bio_type,
        biometric_data=biometric_data
    )
    
    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["message"]
        )
    
    return BiometricAuthResponse(**result)
