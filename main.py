"""
Main FastAPI application.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from config.settings import settings
from app.core.database import init_db, close_db
from app.api import auth, biometric, cicd, audit


# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(settings.log_file),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup
    logger.info("Starting up application...")
    await init_db()
    logger.info("Database initialized")
    
    yield
    
    # Shutdown
    logger.info("Shutting down application...")
    await close_db()
    logger.info("Database connections closed")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## Biometric CI/CD Authentication System
    
    Secure your CI/CD pipeline critical actions with biometric authentication.
    
    ### Features
    - **Multi-modal biometric authentication** (Face, Voice)
    - **Role-based access control** (Admin, DevOps, Security Officer)
    - **Encrypted biometric storage** with AES encryption
    - **Comprehensive audit logging** for compliance
    - **GDPR compliant** with consent management and right to be forgotten
    - **CI/CD integration** for GitLab and Jenkins
    
    ### Security
    - Biometric descriptors are encrypted using AES-256
    - User identifiers are pseudonymized with SHA-256
    - JWT tokens for API authentication
    - Role-based authorization for sensitive operations
    
    ### Compliance
    - GDPR Article 9 - Processing of special categories of personal data
    - Audit trails for all biometric operations
    - Data retention policies
    - User consent management
    """,
    lifespan=lifespan,
    debug=settings.debug
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(biometric.router)
app.include_router(cicd.router)
app.include_router(audit.router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Biometric CI/CD Authentication API",
        "version": settings.app_version,
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "version": settings.app_version
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug
    )
