import requests
import json
import uuid
import os
import django
import jwt

# --- Setup Django Environment to access models ---
# This block is still needed for a standalone script to use the ORM,
# even when running inside the container.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movielogd.settings')
django.setup()
from users.models import CustomUser
# --- End Django Setup ---

# Base URL for your API endpoints
# 'localhost' works here because the script is running inside the 'web'
# container, so it's making a network request to itself.
BASE_URL = "http://localhost:8000/api/auth"

def generate_unique_user_data():
    """Generates user data with a unique email to avoid collisions on re-runs."""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "username": f"testuser_{unique_id}",
        "email": f"test_{unique_id}@example.com",
        "password": "strong-password-123",
        "first_name": "Test",
        "last_name": "User"
    }

def create_test_user(role=CustomUser.Role.USER):
    """Helper function to create a user directly in the DB with a specific role."""
    user_data = generate_unique_user_data()
    user = CustomUser.objects.create_user(
        username=user_data['username'],
        email=user_data['email'],
        password=user_data['password'],
        role=role # Set the role directly
    )
    print(f"   🔧 Created '{role}' user in DB: {user.email}")
    # Return the original credentials for logging in
    return user_data

def test_successful_registration():
    """Test creating a new user and verify they get the default 'USER' role."""
    print("👤 Testing successful user registration...")
    
    user_data = generate_unique_user_data()
    response = requests.post(f"{BASE_URL}/register/", json=user_data)
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Successfully created user: {data['user']['email']}")
        
        assert "user" in data
        assert "role" in data["user"]
        assert data["user"]["role"] == CustomUser.Role.USER
        print(f"   ✅ Role assigned correctly: {data['user']['role']}")
        
        return user_data
    else:
        print(f"❌ Failed to create user. Status: {response.status_code}, Error: {response.text}")
        return None

def test_login_and_token_claims(user_credentials):
    """Test logging in and verify the token contains the 'role' claim."""
    print("\n🔑 Testing user login and token claims...")
    
    if not user_credentials:
        print("   ⏩ Skipping login test: No user credentials provided.")
        return None

    login_payload = {
        "email": user_credentials['email'],
        "password": user_credentials['password']
    }
    
    response = requests.post(f"{BASE_URL}/login/", json=login_payload)
    
    if response.status_code == 200:
        tokens = response.json()
        print("   ✅ Successfully logged in and received tokens.")
        access_token = tokens['access']
        decoded_token = jwt.decode(access_token, options={"verify_signature": False})
        
        assert "role" in decoded_token
        print(f"   ✅ Token contains role claim: '{decoded_token['role']}'")
        return access_token
    else:
        print(f"   ❌ Login failed! Expected 200, got {response.status_code}, Error: {response.text}")
        return None

def test_protected_endpoint_access():
    """Test the admin-only /users/ endpoint with different roles."""
    print("\n🛡️  Testing RBAC on protected endpoint (/users/)...")
    
    # --- Test Case 1: No Authentication ---
    print("   - Testing with no authentication...")
    no_auth_response = requests.get(f"{BASE_URL}/users/")
    if no_auth_response.status_code == 401:
        print("     ✅ Correctly failed with 401 Unauthorized.")
    else:
        print(f"     ❌ FAILED! Expected 401, got {no_auth_response.status_code}")

    # --- Test Case 2: Authenticated as standard 'USER' ---
    print("   - Testing with standard 'USER' role...")
    user_creds = create_test_user(role=CustomUser.Role.USER)
    user_token = test_login_and_token_claims(user_creds)
    if user_token:
        headers = {'Authorization': f'Bearer {user_token}'}
        user_response = requests.get(f"{BASE_URL}/users/", headers=headers)
        if user_response.status_code == 403:
            print("     ✅ Correctly failed with 403 Forbidden.")
        else:
            print(f"     ❌ FAILED! Expected 403, got {user_response.status_code}")

    # --- Test Case 3: Authenticated as 'ADMIN' ---
    print("   - Testing with 'ADMIN' role...")
    admin_creds = create_test_user(role=CustomUser.Role.ADMIN)
    admin_token = test_login_and_token_claims(admin_creds)
    if admin_token:
        headers = {'Authorization': f'Bearer {admin_token}'}
        admin_response = requests.get(f"{BASE_URL}/users/", headers=headers)
        if admin_response.status_code == 200:
            print("     ✅ Correctly succeeded with 200 OK.")
        else:
            print(f"     ❌ FAILED! Expected 200, got {admin_response.status_code}")

def main():
    """Run all authentication and authorization tests."""
    print("🚀 Starting Auth API Tests (including RBAC)...")
    print("=" * 60)
    
    try:
        user_credentials = test_successful_registration()
        if user_credentials:
            test_login_and_token_claims(user_credentials)
        test_protected_endpoint_access()
        
        print("\n" + "=" * 60)
        print("🎉 All authentication and authorization tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the API. Make sure your server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
