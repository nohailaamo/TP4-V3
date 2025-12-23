#!/usr/bin/env python3
"""
Example script demonstrating the biometric CI/CD authentication workflow.

This script shows how to:
1. Register a user
2. Login and get JWT token
3. Enroll biometric data
4. Authenticate with biometric
5. Request a CI/CD action
6. Approve the action with biometric authentication
"""
import requests
import sys
from pathlib import Path


# API Configuration
API_BASE_URL = "http://localhost:8000"

# Test data
TEST_USER = {
    "username": "demo_admin",
    "email": "demo@example.com",
    "password": "DemoP@ssw0rd123",
    "full_name": "Demo Admin",
    "role": "admin",
    "consent_given": True
}


def print_step(step_num, description):
    """Print a step header."""
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print('='*60)


def register_user():
    """Register a new user."""
    print_step(1, "Register User")
    
    response = requests.post(
        f"{API_BASE_URL}/api/auth/register",
        json=TEST_USER
    )
    
    if response.status_code == 201:
        print("✅ User registered successfully!")
        print(f"User ID: {response.json()['id']}")
        return True
    elif response.status_code == 400 and "already registered" in response.json()["detail"]:
        print("ℹ️  User already exists, continuing...")
        return True
    else:
        print(f"❌ Registration failed: {response.json()}")
        return False


def login():
    """Login and get JWT token."""
    print_step(2, "Login and Get Token")
    
    response = requests.post(
        f"{API_BASE_URL}/api/auth/login",
        data={
            "username": TEST_USER["username"],
            "password": TEST_USER["password"]
        }
    )
    
    if response.status_code == 200:
        token = response.json()["access_token"]
        print("✅ Login successful!")
        print(f"Token: {token[:50]}...")
        return token
    else:
        print(f"❌ Login failed: {response.json()}")
        return None


def enroll_biometric(token, biometric_file):
    """Enroll biometric data."""
    print_step(3, "Enroll Biometric Data")
    
    if not Path(biometric_file).exists():
        print(f"⚠️  Biometric file not found: {biometric_file}")
        print("Please provide a valid face image or voice file.")
        return False
    
    file_type = "face" if biometric_file.endswith(('.jpg', '.jpeg', '.png')) else "voice"
    
    with open(biometric_file, 'rb') as f:
        response = requests.post(
            f"{API_BASE_URL}/api/biometric/enroll",
            headers={"Authorization": f"Bearer {token}"},
            data={
                "biometric_type": file_type,
                "consent_confirmed": "true"
            },
            files={"file": f}
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Biometric enrolled successfully!")
        print(f"Type: {file_type}")
        print(f"Quality Score: {result.get('quality_score', 'N/A')}")
        return True
    else:
        print(f"❌ Enrollment failed: {response.json()}")
        return False


def authenticate_biometric(token, biometric_file):
    """Authenticate with biometric data."""
    print_step(4, "Authenticate with Biometric")
    
    if not Path(biometric_file).exists():
        print(f"⚠️  Biometric file not found: {biometric_file}")
        return False
    
    file_type = "face" if biometric_file.endswith(('.jpg', '.jpeg', '.png')) else "voice"
    
    with open(biometric_file, 'rb') as f:
        response = requests.post(
            f"{API_BASE_URL}/api/biometric/authenticate",
            headers={"Authorization": f"Bearer {token}"},
            data={"biometric_type": file_type},
            files={"file": f}
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Authentication: {'SUCCESS' if result['authenticated'] else 'FAILED'}")
        print(f"Similarity Score: {result.get('similarity_score', 'N/A')}")
        return result['authenticated']
    else:
        print(f"❌ Authentication request failed: {response.json()}")
        return False


def request_cicd_action(token):
    """Request a CI/CD action."""
    print_step(5, "Request CI/CD Action")
    
    response = requests.post(
        f"{API_BASE_URL}/api/cicd/request-action",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "action_type": "deploy",
            "description": "Deploy to production environment",
            "pipeline_id": "demo-pipeline-12345",
            "environment": "production"
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        action_id = result["action_id"]
        print(f"✅ Action requested successfully!")
        print(f"Action ID: {action_id}")
        print(f"Status: {result['status']}")
        print(f"Expires at: {result['expires_at']}")
        return action_id
    else:
        print(f"❌ Action request failed: {response.json()}")
        return None


def approve_cicd_action(token, action_id, biometric_file):
    """Approve a CI/CD action with biometric authentication."""
    print_step(6, "Approve CI/CD Action with Biometric")
    
    if not Path(biometric_file).exists():
        print(f"⚠️  Biometric file not found: {biometric_file}")
        return False
    
    file_type = "face" if biometric_file.endswith(('.jpg', '.jpeg', '.png')) else "voice"
    
    with open(biometric_file, 'rb') as f:
        response = requests.post(
            f"{API_BASE_URL}/api/cicd/approve-action",
            headers={"Authorization": f"Bearer {token}"},
            data={
                "action_id": action_id,
                "biometric_type": file_type
            },
            files={"file": f}
        )
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Action {'APPROVED' if result['approved'] else 'DENIED'}!")
        print(f"Status: {result['status']}")
        print(f"Similarity Score: {result.get('similarity_score', 'N/A')}")
        print(f"Message: {result['message']}")
        return result['approved']
    else:
        print(f"❌ Approval failed: {response.json()}")
        return False


def main():
    """Main workflow."""
    print("\n" + "="*60)
    print("Biometric CI/CD Authentication Demo")
    print("="*60)
    
    # Check if biometric file is provided
    if len(sys.argv) < 2:
        print("\nUsage: python example_workflow.py <biometric_file>")
        print("\nExample:")
        print("  python example_workflow.py data/faces/1477812374602827.jpeg")
        print("  python example_workflow.py data/voices/1462-170142-0000.flac")
        sys.exit(1)
    
    biometric_file = sys.argv[1]
    
    # Step 1: Register
    if not register_user():
        sys.exit(1)
    
    # Step 2: Login
    token = login()
    if not token:
        sys.exit(1)
    
    # Step 3: Enroll biometric
    if not enroll_biometric(token, biometric_file):
        print("\n⚠️  Continuing despite enrollment issue (might already be enrolled)...")
    
    # Step 4: Authenticate biometric
    if not authenticate_biometric(token, biometric_file):
        print("\n❌ Biometric authentication failed. Cannot proceed.")
        sys.exit(1)
    
    # Step 5: Request CI/CD action
    action_id = request_cicd_action(token)
    if not action_id:
        sys.exit(1)
    
    # Step 6: Approve CI/CD action
    if not approve_cicd_action(token, action_id, biometric_file):
        print("\n❌ Action approval failed!")
        sys.exit(1)
    
    print("\n" + "="*60)
    print("✅ DEMO COMPLETED SUCCESSFULLY!")
    print("="*60)
    print("\nThe CI/CD pipeline is now authorized to proceed with deployment.")


if __name__ == "__main__":
    main()
