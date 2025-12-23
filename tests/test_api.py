"""
Basic tests for the biometric CI/CD authentication system.
"""
import pytest
from httpx import AsyncClient
from fastapi import status

from main import app


@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint returns correct response."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "message" in data
    assert "version" in data


@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/health")
    
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_register_user():
    """Test user registration."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser",
                "email": "test@example.com",
                "password": "SecureP@ss123",
                "full_name": "Test User",
                "role": "devops",
                "consent_given": True
            }
        )
    
    assert response.status_code in [status.HTTP_201_CREATED, status.HTTP_400_BAD_REQUEST]
    # 400 is acceptable if user already exists


@pytest.mark.asyncio
async def test_register_without_consent():
    """Test user registration fails without consent."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "testuser2",
                "email": "test2@example.com",
                "password": "SecureP@ss123",
                "consent_given": False
            }
        )
    
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "consent" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_login_invalid_credentials():
    """Test login with invalid credentials."""
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post(
            "/api/auth/login",
            data={
                "username": "nonexistent",
                "password": "wrongpassword"
            }
        )
    
    assert response.status_code == status.HTTP_401_UNAUTHORIZED


# Note: Additional tests would require setting up test fixtures
# with actual biometric data and database mocking.
# This is a basic test structure to demonstrate the testing approach.
