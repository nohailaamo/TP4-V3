"""
Database models for the biometric CI/CD authentication system.
"""
from datetime import datetime
from typing import Optional
from enum import Enum as PyEnum

from sqlalchemy import String, Integer, DateTime, Boolean, LargeBinary, Text, Enum
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base class for all database models."""
    pass


class UserRole(PyEnum):
    """User roles for access control."""
    ADMIN = "admin"
    DEVOPS = "devops"
    SECURITY_OFFICER = "security_officer"


class BiometricType(PyEnum):
    """Types of biometric data."""
    FACE = "face"
    VOICE = "voice"
    FINGERPRINT = "fingerprint"


class ActionStatus(PyEnum):
    """Status of CI/CD actions."""
    APPROVED = "approved"
    DENIED = "denied"
    PENDING = "pending"


class User(Base):
    """User model for authentication and authorization."""
    __tablename__ = "users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    full_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.DEVOPS)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_given: Mapped[bool] = mapped_column(Boolean, default=False)
    consent_date: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Pseudonymized identifier (SHA-256 hash)
    pseudonym: Mapped[Optional[str]] = mapped_column(String(64), unique=True, nullable=True)


class BiometricData(Base):
    """Biometric data storage with encryption."""
    __tablename__ = "biometric_data"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(Integer, index=True)
    biometric_type: Mapped[BiometricType] = mapped_column(Enum(BiometricType))
    
    # Encrypted biometric descriptor
    encrypted_descriptor: Mapped[bytes] = mapped_column(LargeBinary)
    
    # Metadata
    enrollment_date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    last_used: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Quality metrics
    quality_score: Mapped[Optional[float]] = mapped_column(nullable=True)


class AuditLog(Base):
    """Audit log for tracking all authentication attempts and actions."""
    __tablename__ = "audit_logs"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, index=True)
    pseudonym: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    
    action: Mapped[str] = mapped_column(String(255))
    action_type: Mapped[str] = mapped_column(String(50))  # enrollment, authentication, approval
    status: Mapped[ActionStatus] = mapped_column(Enum(ActionStatus))
    
    # Biometric details
    biometric_type: Mapped[Optional[BiometricType]] = mapped_column(Enum(BiometricType), nullable=True)
    similarity_score: Mapped[Optional[float]] = mapped_column(nullable=True)
    
    # CI/CD specific
    pipeline_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    pipeline_action: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    
    # Metadata
    ip_address: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, index=True)
    
    # Additional details
    details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)


class CICDAction(Base):
    """CI/CD actions pending biometric approval."""
    __tablename__ = "cicd_actions"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    action_id: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    
    # Action details
    action_type: Mapped[str] = mapped_column(String(100))  # deploy, rollback, pipeline_modify
    description: Mapped[str] = mapped_column(Text)
    requester_id: Mapped[int] = mapped_column(Integer)
    
    # Approval details
    status: Mapped[ActionStatus] = mapped_column(Enum(ActionStatus), default=ActionStatus.PENDING)
    approver_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    approval_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    
    # Timestamps
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    expires_at: Mapped[datetime] = mapped_column(DateTime)
    
    # Metadata
    pipeline_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    environment: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
