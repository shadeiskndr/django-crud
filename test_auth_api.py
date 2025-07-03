import requests
import json
import uuid

# Base URL for your authentication API endpoints
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

def test_successful_registration():
    """Test creating a new user with valid data."""
    print("👤 Testing successful user registration...")
    
    user_data = generate_unique_user_data()
    
    response = requests.post(f"{BASE_URL}/register/", json=user_data)
    
    if response.status_code == 201:
        data = response.json()
        print(f"✅ Successfully created user: {data['user']['email']}")
        
        # Verify the response structure
        assert "user" in data
        assert "message" in data
        assert "password" not in data["user"] # IMPORTANT: Ensure password is not returned
        
        return data['user'] # Return created user data for the next test
    else:
        print(f"❌ Failed to create user. Status: {response.status_code}")
        print(f"   Error: {response.text}")
        return None

def test_duplicate_email_registration(existing_user_data):
    """Test trying to register with an email that already exists."""
    print("\n duplication Test: Testing registration with a duplicate email...")
    
    if not existing_user_data:
        print("   ⏩ Skipping test: No existing user data provided.")
        return

    # Create a new user payload but use the SAME email
    duplicate_data = {
        "username": "another_user",
        "email": existing_user_data['email'], # Use the existing email
        "password": "another-password"
    }
    
    response = requests.post(f"{BASE_URL}/register/", json=duplicate_data)
    
    if response.status_code == 400:
        errors = response.json()
        print("✅ Correctly failed with status 400 (Bad Request).")
        
        # Check if the error message is for the 'email' field
        if 'email' in errors:
            print(f"   Validation error received for email: {errors['email'][0]}")
        else:
            print(f"   Received a 400 error, but not for the email field: {errors}")
            
    else:
        print(f"❌ Test failed. Expected status 400, but got {response.status_code}")

def test_missing_password_registration():
    """Test trying to register without providing a password."""
    print("\n⚠️ Testing registration with a missing password...")
    
    user_data = generate_unique_user_data()
    del user_data['password'] # Remove the password from the payload
    
    response = requests.post(f"{BASE_URL}/register/", json=user_data)
    
    if response.status_code == 400:
        errors = response.json()
        print("✅ Correctly failed with status 400 (Bad Request).")
        
        # Check if the error message is for the 'password' field
        if 'password' in errors:
            print(f"   Validation error received for password: {errors['password'][0]}")
    else:
        print(f"❌ Test failed. Expected status 400, but got {response.status_code}")

def main():
    """Run all authentication tests."""
    print("🚀 Starting Authentication API Tests...")
    print("=" * 50)
    
    try:
        # 1. Test the happy path
        created_user = test_successful_registration()
        
        # 2. Test duplicate email failure (only if first test passed)
        test_duplicate_email_registration(created_user)
        
        # 3. Test missing required field failure
        test_missing_password_registration()
        
        print("\n" + "=" * 50)
        print("🎉 All authentication tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure your server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
