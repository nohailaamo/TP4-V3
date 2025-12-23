"""
Pydantic schemas for API request and response validation.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum


class BiometricTypeEnum(str, Enum):
    """Biometric types."""
    FACE = "face"
    VOICE = "voice"
    FINGERPRINT = "fingerprint"


class UserRoleEnum(str, Enum):
    """User roles."""
    ADMIN = "admin"
    DEVOPS = "devops"
    SECURITY_OFFICER = "security_officer"


class ActionStatusEnum(str, Enum):
    """Action status."""
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"


# User schemas
class UserCreate(BaseModel):
    """Schema for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)
    full_name: Optional[str] = None
    role: UserRoleEnum = UserRoleEnum.DEVOPS
    consent_given: bool = Field(..., description="GDPR consent required")


class UserResponse(BaseModel):
    """Schema for user response."""
    id: int
    username: str
    email: str
    full_name: Optional[str]
    role: str
    is_active: bool
    is_verified: bool
    consent_given: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """Schema for user login."""
    username: str
    password: str


class Token(BaseModel):
    """Schema for JWT token response."""
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """Schema for token data."""
    username: Optional[str] = None
    user_id: Optional[int] = None
    role: Optional[str] = None


# Biometric schemas
class BiometricEnrollRequest(BaseModel):
    """Schema for biometric enrollment request."""
    biometric_type: BiometricTypeEnum
    consent_confirmed: bool = Field(..., description="User must confirm consent")


class BiometricEnrollResponse(BaseModel):
    """Schema for biometric enrollment response."""
    success: bool
    message: str
    quality_score: Optional[float] = None


class BiometricAuthRequest(BaseModel):
    """Schema for biometric authentication request."""
    biometric_type: BiometricTypeEnum


class BiometricAuthResponse(BaseModel):
    """Schema for biometric authentication response."""
    success: bool
    authenticated: bool
    similarity_score: Optional[float] = None
    message: str


# CI/CD Action schemas
class CICDActionRequest(BaseModel):
    """Schema for CI/CD action approval request."""
    action_type: str = Field(..., description="deploy, rollback, or pipeline_modify")
    description: str
    pipeline_id: Optional[str] = None
    environment: Optional[str] = None


class CICDActionResponse(BaseModel):
    """Schema for CI/CD action response."""
    action_id: str
    status: ActionStatusEnum
    message: str
    expires_at: datetime


class ActionApprovalRequest(BaseModel):
    """Schema for action approval request."""
    action_id: str
    biometric_type: BiometricTypeEnum


class ActionApprovalResponse(BaseModel):
    """Schema for action approval response."""
    success: bool
    action_id: str
    status: ActionStatusEnum
    approved: bool
    message: str
    similarity_score: Optional[float] = None


# Audit schemas
class AuditLogResponse(BaseModel):
    """Schema for audit log response."""
    id: int
    user_id: Optional[int]
    action: str
    action_type: str
    status: str
    biometric_type: Optional[str]
    similarity_score: Optional[float]
    pipeline_id: Optional[str]
    timestamp: datetime
    details: Optional[str]
    
    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Schema for audit log list response."""
    total: int
    logs: List[AuditLogResponse]


# Metrics schemas
class BiometricMetrics(BaseModel):
    """Schema for biometric system metrics."""
    FAR: float = Field(..., description="False Acceptance Rate")
    FRR: float = Field(..., description="False Rejection Rate")
    EER: float = Field(..., description="Equal Error Rate")


# Generic response schemas
class MessageResponse(BaseModel):
    """Schema for generic message response."""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Schema for error response."""
    detail: str
    error_code: Optional[str] = None
