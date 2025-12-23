"""
Configuration module for the biometric CI/CD authentication system.
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "Biometric CI/CD Authentication"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Security
    secret_key: str = "your-secret-key-change-this-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Database
    database_url: str = "sqlite+aiosqlite:///./biometric_cicd.db"
    
    # Biometric settings
    face_recognition_tolerance: float = 0.6
    voice_mfcc_n_mfcc: int = 13
    similarity_threshold: float = 0.85
    
    # Encryption
    encryption_key: str = "your-encryption-key-change-this-in-production"
    
    # GDPR Compliance
    data_retention_days: int = 365
    require_consent: bool = True
    
    # Logging
    log_level: str = "INFO"
    log_file: str = "app.log"
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
