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

def test_role_update_functionality():
    """Test the new role update endpoint."""
    print("\n🔄 Testing Role Update Functionality...")
    
    # Create an admin user and a regular user
    admin_creds = create_test_user(role=CustomUser.Role.ADMIN)
    user_creds = create_test_user(role=CustomUser.Role.USER)
    
    # Get tokens
    admin_token = test_login_and_token_claims(admin_creds)
    user_token = test_login_and_token_claims(user_creds)
    
    if not (admin_token and user_token):
        print("   ❌ Could not get required tokens. Skipping role update tests.")
        return
    
    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    user_headers = {'Authorization': f'Bearer {user_token}'}
    
    # First, get the user ID by listing users
    print("   - Getting user list to find user ID...")
    users_response = requests.get(f"{BASE_URL}/users/", headers=admin_headers)
    if users_response.status_code != 200:
        print(f"   ❌ Could not get users list: {users_response.status_code}")
        return
    
    users_data = users_response.json()
    results = users_data.get('results', users_data) if isinstance(users_data, dict) else users_data
    
    # Find the regular user in the list
    target_user = None
    for user in results:
        if user['email'] == user_creds['email']:
            target_user = user
            break
    
    if not target_user:
        print("   ❌ Could not find target user in users list.")
        return
    
    user_id = target_user['id']
    print(f"   ✅ Found target user ID: {user_id}")
    
    # --- Test Case 1: Regular user trying to update roles (should fail) ---
    print("   - Testing role update by regular user (should fail)...")
    role_update_payload = {"role": "ADMIN"}
    response = requests.patch(f"{BASE_URL}/users/{user_id}/role/", 
                            json=role_update_payload, headers=user_headers)
    if response.status_code == 403:
        print("     ✅ Correctly denied regular user role update (403 Forbidden)")
    else:
        print(f"     ❌ FAILED! Expected 403, got {response.status_code}")
    
    # --- Test Case 2: Admin updating user role (should succeed) ---
    print("   - Testing role update by admin (USER → CRITIC)...")
    role_update_payload = {"role": "CRITIC"}
    response = requests.patch(f"{BASE_URL}/users/{user_id}/role/", 
                            json=role_update_payload, headers=admin_headers)
    if response.status_code == 200:
        data = response.json()
        print("     ✅ Successfully updated user role")
        print(f"     ✅ New role: {data['user']['role']}")
        assert data['user']['role'] == 'CRITIC'
    else:
        print(f"     ❌ FAILED! Expected 200, got {response.status_code}, Error: {response.text}")
        return
    
    # --- Test Case 3: Admin updating user role to ADMIN ---
    print("   - Testing role update by admin (CRITIC → ADMIN)...")
    role_update_payload = {"role": "ADMIN"}
    response = requests.patch(f"{BASE_URL}/users/{user_id}/role/", 
                            json=role_update_payload, headers=admin_headers)
    if response.status_code == 200:
        data = response.json()
        print("     ✅ Successfully updated user role to ADMIN")
        print(f"     ✅ New role: {data['user']['role']}")
        assert data['user']['role'] == 'ADMIN'
    else:
        print(f"     ❌ FAILED! Expected 200, got {response.status_code}, Error: {response.text}")
        return
    
    # --- Test Case 4: Test invalid role ---
    print("   - Testing invalid role update...")
    role_update_payload = {"role": "INVALID_ROLE"}
    response = requests.patch(f"{BASE_URL}/users/{user_id}/role/", 
                            json=role_update_payload, headers=admin_headers)
    if response.status_code == 400:
        print("     ✅ Correctly rejected invalid role (400 Bad Request)")
    else:
        print(f"     ❌ FAILED! Expected 400, got {response.status_code}")
    
    # --- Test Case 5: Verify the updated user can now access admin endpoints ---
    print("   - Testing that updated user now has admin privileges...")
    # Login as the updated user to get fresh token with new role
    updated_user_token = test_login_and_token_claims(user_creds)
    if updated_user_token:
        updated_headers = {'Authorization': f'Bearer {updated_user_token}'}
        admin_test_response = requests.get(f"{BASE_URL}/users/", headers=updated_headers)
        if admin_test_response.status_code == 200:
            print("     ✅ Updated user can now access admin endpoints")
        else:
            print(f"     ❌ Updated user still cannot access admin endpoints: {admin_test_response.status_code}")
    
    print("   ✅ Role update functionality tests completed!")

def test_role_update_edge_cases():
    """Test edge cases for role updates."""
    print("\n🧪 Testing Role Update Edge Cases...")
    
    # Create admin user
    admin_creds = create_test_user(role=CustomUser.Role.ADMIN)
    admin_token = test_login_and_token_claims(admin_creds)
    
    if not admin_token:
        print("   ❌ Could not get admin token. Skipping edge case tests.")
        return
    
    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    
    # --- Test Case 1: Update non-existent user ---
    print("   - Testing update of non-existent user...")
    response = requests.patch(f"{BASE_URL}/users/99999/role/", 
                            json={"role": "ADMIN"}, headers=admin_headers)
    if response.status_code == 404:
        print("     ✅ Correctly returned 404 for non-existent user")
    else:
        print(f"     ❌ Expected 404, got {response.status_code}")
    
    # --- Test Case 2: Missing role in payload ---
    print("   - Testing update with missing role...")
    # Get a valid user ID first
    users_response = requests.get(f"{BASE_URL}/users/", headers=admin_headers)
    if users_response.status_code == 200:
        users_data = users_response.json()
        results = users_data.get('results', users_data) if isinstance(users_data, dict) else users_data
        if results:
            user_id = results[0]['id']
            response = requests.patch(f"{BASE_URL}/users/{user_id}/role/", 
                                    json={}, headers=admin_headers)  # Empty payload
            if response.status_code == 400:
                print("     ✅ Correctly rejected empty role payload")
            else:
                print(f"     ❌ Expected 400, got {response.status_code}")
    
    # --- Test Case 3: Test all valid roles ---
    print("   - Testing all valid role assignments...")
    valid_roles = ['USER', 'CRITIC', 'MODERATOR', 'ADMIN']
    
    # Create a test user for role cycling
    test_user_creds = create_test_user(role=CustomUser.Role.USER)
    users_response = requests.get(f"{BASE_URL}/users/", headers=admin_headers)
    if users_response.status_code == 200:
        users_data = users_response.json()
        results = users_data.get('results', users_data) if isinstance(users_data, dict) else users_data
        
        target_user = None
        for user in results:
            if user['email'] == test_user_creds['email']:
                target_user = user
                break
        
        if target_user:
            user_id = target_user['id']
            for role in valid_roles:
                response = requests.patch(f"{BASE_URL}/users/{user_id}/role/", 
                                        json={"role": role}, headers=admin_headers)
                if response.status_code == 200:
                    print(f"     ✅ Successfully assigned role: {role}")
                else:
                    print(f"     ❌ Failed to assign role {role}: {response.status_code}")
    
    print("   ✅ Edge case tests completed!")

def main():
    """Run all authentication and authorization tests."""
    print("🚀 Starting Enhanced Auth API Tests (including Role Updates)...")
    print("=" * 70)
    
    try:
        user_credentials = test_successful_registration()
        if user_credentials:
            test_login_and_token_claims(user_credentials)
        test_protected_endpoint_access()
        test_role_update_functionality()
        test_role_update_edge_cases()
        
        print("\n" + "=" * 70)
        print("🎉 All authentication and authorization tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the API. Make sure your server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

