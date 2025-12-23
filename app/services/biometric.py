"""
Biometric service for enrollment and authentication operations.
"""
from typing import Optional, Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import numpy as np
from datetime import datetime

from app.models.database import BiometricData, BiometricType, User, AuditLog, ActionStatus
from app.services.face_recognition import face_recognition_service
from app.services.voice_recognition import voice_recognition_service
from app.utils.encryption import encryption_service


class BiometricService:
    """Service for biometric operations."""
    
    async def enroll_biometric(
        self,
        db: AsyncSession,
        user_id: int,
        biometric_type: BiometricType,
        biometric_data: bytes
    ) -> Dict:
        """
        Enroll biometric data for a user.
        
        Args:
            db: Database session
            user_id: User ID
            biometric_type: Type of biometric (face, voice, fingerprint)
            biometric_data: Raw biometric data (image or audio bytes)
            
        Returns:
            Dictionary with enrollment result
        """
        try:
            # Extract features based on biometric type
            if biometric_type == BiometricType.FACE:
                features = face_recognition_service.extract_face_encoding(biometric_data)
                quality = face_recognition_service.calculate_quality_score(biometric_data)
            elif biometric_type == BiometricType.VOICE:
                features = voice_recognition_service.extract_voice_features(biometric_data)
                quality = voice_recognition_service.calculate_quality_score(biometric_data)
            else:
                return {
                    "success": False,
                    "message": f"Biometric type {biometric_type} not yet implemented"
                }
            
            if features is None:
                return {
                    "success": False,
                    "message": f"Failed to extract {biometric_type.value} features"
                }
            
            # Encrypt the features
            encrypted_features = encryption_service.encrypt_descriptor(features)
            
            # Check if user already has this biometric type enrolled
            result = await db.execute(
                select(BiometricData).where(
                    BiometricData.user_id == user_id,
                    BiometricData.biometric_type == biometric_type,
                    BiometricData.is_active == True
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                # Update existing enrollment
                existing.encrypted_descriptor = encrypted_features
                existing.enrollment_date = datetime.utcnow()
                existing.quality_score = quality
            else:
                # Create new enrollment
                biometric_entry = BiometricData(
                    user_id=user_id,
                    biometric_type=biometric_type,
                    encrypted_descriptor=encrypted_features,
                    quality_score=quality
                )
                db.add(biometric_entry)
            
            # Log enrollment
            audit_log = AuditLog(
                user_id=user_id,
                action=f"Biometric enrollment: {biometric_type.value}",
                action_type="enrollment",
                status=ActionStatus.APPROVED,
                biometric_type=biometric_type,
                timestamp=datetime.utcnow()
            )
            db.add(audit_log)
            
            await db.commit()
            
            return {
                "success": True,
                "message": f"{biometric_type.value.capitalize()} enrolled successfully",
                "quality_score": quality
            }
            
        except Exception as e:
            await db.rollback()
            return {
                "success": False,
                "message": f"Enrollment error: {str(e)}"
            }
    
    async def authenticate_biometric(
        self,
        db: AsyncSession,
        user_id: int,
        biometric_type: BiometricType,
        biometric_data: bytes
    ) -> Dict:
        """
        Authenticate a user using biometric data.
        
        Args:
            db: Database session
            user_id: User ID
            biometric_type: Type of biometric
            biometric_data: Raw biometric data
            
        Returns:
            Dictionary with authentication result
        """
        try:
            # Extract features from provided biometric data
            if biometric_type == BiometricType.FACE:
                new_features = face_recognition_service.extract_face_encoding(biometric_data)
            elif biometric_type == BiometricType.VOICE:
                new_features = voice_recognition_service.extract_voice_features(biometric_data)
            else:
                return {
                    "success": False,
                    "authenticated": False,
                    "message": f"Biometric type {biometric_type} not yet implemented"
                }
            
            if new_features is None:
                # Log failed attempt
                audit_log = AuditLog(
                    user_id=user_id,
                    action=f"Biometric authentication: {biometric_type.value}",
                    action_type="authentication",
                    status=ActionStatus.DENIED,
                    biometric_type=biometric_type,
                    details="Failed to extract features",
                    timestamp=datetime.utcnow()
                )
                db.add(audit_log)
                await db.commit()
                
                return {
                    "success": False,
                    "authenticated": False,
                    "message": f"Failed to extract {biometric_type.value} features"
                }
            
            # Retrieve enrolled biometric data
            result = await db.execute(
                select(BiometricData).where(
                    BiometricData.user_id == user_id,
                    BiometricData.biometric_type == biometric_type,
                    BiometricData.is_active == True
                )
            )
            enrolled_biometric = result.scalar_one_or_none()
            
            if not enrolled_biometric:
                audit_log = AuditLog(
                    user_id=user_id,
                    action=f"Biometric authentication: {biometric_type.value}",
                    action_type="authentication",
                    status=ActionStatus.DENIED,
                    biometric_type=biometric_type,
                    details="No enrolled biometric data found",
                    timestamp=datetime.utcnow()
                )
                db.add(audit_log)
                await db.commit()
                
                return {
                    "success": False,
                    "authenticated": False,
                    "message": f"No enrolled {biometric_type.value} data found"
                }
            
            # Decrypt enrolled features
            enrolled_features = encryption_service.decrypt_descriptor(
                enrolled_biometric.encrypted_descriptor,
                shape=new_features.shape,
                dtype=new_features.dtype
            )
            
            # Compare features
            if biometric_type == BiometricType.FACE:
                is_match, similarity = face_recognition_service.compare_faces(
                    enrolled_features, new_features
                )
            elif biometric_type == BiometricType.VOICE:
                is_match, similarity = voice_recognition_service.compare_voices(
                    enrolled_features, new_features
                )
            else:
                is_match, similarity = False, 0.0
            
            # Update last used timestamp
            enrolled_biometric.last_used = datetime.utcnow()
            
            # Log authentication attempt
            audit_log = AuditLog(
                user_id=user_id,
                action=f"Biometric authentication: {biometric_type.value}",
                action_type="authentication",
                status=ActionStatus.APPROVED if is_match else ActionStatus.DENIED,
                biometric_type=biometric_type,
                similarity_score=similarity,
                timestamp=datetime.utcnow()
            )
            db.add(audit_log)
            
            await db.commit()
            
            return {
                "success": True,
                "authenticated": is_match,
                "similarity_score": similarity,
                "message": "Authentication successful" if is_match else "Authentication failed"
            }
            
        except Exception as e:
            await db.rollback()
            return {
                "success": False,
                "authenticated": False,
                "message": f"Authentication error: {str(e)}"
            }


# Global instance
biometric_service = BiometricService()
