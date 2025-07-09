import requests
import json
import uuid
import os
import django

# --- Setup Django Environment to access models ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movielogd.settings')
django.setup()
from users.models import CustomUser
from movies.models import Genre # <-- Import Genre model
# --- End Django Setup ---

# Base URLs
API_BASE_URL = "http://localhost:8000/api"
AUTH_BASE_URL = "http://localhost:8000/api/auth"

# Mock movie data for creation
MOCK_MOVIE_PAYLOAD = {
    "title": "The Test Movie",
    "original_title": "The Test Movie",
    "overview": "A movie created by an automated test.",
    "release_date": "2024-01-01",
    "runtime": 120,
    "vote_average": 7.5,
    "genre_ids": [28, 12], # Action, Adventure
}

# --- Helper Functions ---

def generate_unique_user_data():
    """Generates user data with a unique email."""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "username": f"api_test_user_{unique_id}",
        "email": f"api_test_{unique_id}@example.com",
        "password": "strong-password-123",
    }

def create_test_user(role=CustomUser.Role.USER):
    """Creates a user directly in the DB with a specific role."""
    user_data = generate_unique_user_data()
    CustomUser.objects.create_user(
        username=user_data['username'],
        email=user_data['email'],
        password=user_data['password'],
        role=role
    )
    return user_data

def get_auth_token(user_credentials):
    """Logs in a user and returns the access token."""
    response = requests.post(f"{AUTH_BASE_URL}/login/", json=user_credentials)
    if response.status_code == 200:
        return response.json()['access']
    print(f"   ⚠️ Could not log in user {user_credentials['email']}. Response: {response.text}")
    return None

def setup_test_data():
    """Creates necessary related objects (like Genres) for tests to pass."""
    print("🔧 Setting up test data (Genres)...")
    # The MOCK_MOVIE_PAYLOAD requires genres with IDs 28 and 12.
    # Use update_or_create to avoid errors on re-runs.
    Genre.objects.update_or_create(tmdb_id=28, defaults={'name': 'Action'})
    Genre.objects.update_or_create(tmdb_id=12, defaults={'name': 'Adventure'})
    print("   ✅ Genres created.")

# --- Test Functions ---

def test_read_operations():
    """Tests that read operations (list, retrieve) are public."""
    print("\n📖 Testing Read Operations (Public Access)...")
    
    # Test LIST
    list_response = requests.get(f"{API_BASE_URL}/movies/")
    if list_response.status_code == 200:
        print("   ✅ LIST: Public access to /movies/ is allowed (200 OK).")
    else:
        print(f"   ❌ LIST: FAILED! Expected 200, got {list_response.status_code}.")

    # Create a movie with an admin account to test RETRIEVE
    admin_creds = create_test_user(role=CustomUser.Role.ADMIN)
    admin_token = get_auth_token(admin_creds)
    if not admin_token:
        print("   ❌ CRITICAL: Could not get admin token. Skipping retrieve test.")
        return
        
    headers = {'Authorization': f'Bearer {admin_token}'}
    create_response = requests.post(f"{API_BASE_URL}/movies/", headers=headers, json=MOCK_MOVIE_PAYLOAD)
    
    if create_response.status_code != 201:
        print(f"   ❌ CRITICAL: Could not create a movie for testing retrieve. Error: {create_response.text}")
        return
    
    movie_id = create_response.json()['id']
    
    # Test RETRIEVE (no auth headers)
    retrieve_response = requests.get(f"{API_BASE_URL}/movies/{movie_id}/")
    if retrieve_response.status_code == 200:
        print(f"   ✅ RETRIEVE: Public access to /movies/{movie_id}/ is allowed (200 OK).")
    else:
        print(f"   ❌ RETRIEVE: FAILED! Expected 200, got {retrieve_response.status_code}.")

def test_write_operations():
    """Tests that write operations (POST, PUT, PATCH, DELETE) are restricted."""
    print("\n✍️  Testing Write Operations (Admin-Only Access)...")

    # Setup users and tokens
    admin_creds = create_test_user(role=CustomUser.Role.ADMIN)
    user_creds = create_test_user(role=CustomUser.Role.USER)
    admin_token = get_auth_token(admin_creds)
    user_token = get_auth_token(user_creds)
    
    if not (admin_token and user_token):
        print("   ❌ CRITICAL: Could not get auth tokens. Aborting write tests.")
        return

    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    user_headers = {'Authorization': f'Bearer {user_token}'}

    # --- Test CREATE (POST) ---
    print("   - Testing CREATE (POST /movies/)...")
    # No Auth
    r_no_auth = requests.post(f"{API_BASE_URL}/movies/", json=MOCK_MOVIE_PAYLOAD)
    print(f"     - No Auth: {'✅ Correctly denied (401)' if r_no_auth.status_code == 401 else f'❌ FAILED (Expected 401, got {r_no_auth.status_code})'}")
    # User Auth
    r_user_auth = requests.post(f"{API_BASE_URL}/movies/", headers=user_headers, json=MOCK_MOVIE_PAYLOAD)
    print(f"     - User Role: {'✅ Correctly denied (403)' if r_user_auth.status_code == 403 else f'❌ FAILED (Expected 403, got {r_user_auth.status_code})'}")
    # Admin Auth
    r_admin_auth = requests.post(f"{API_BASE_URL}/movies/", headers=admin_headers, json=MOCK_MOVIE_PAYLOAD)
    print(f"     - Admin Role: {'✅ Correctly allowed (201)' if r_admin_auth.status_code == 201 else f'❌ FAILED (Expected 201, got {r_admin_auth.status_code})'}")
    
    if r_admin_auth.status_code != 201:
        print(f"   ❌ CRITICAL: Could not create movie as admin. Aborting further write tests. Error: {r_admin_auth.text}")
        return
    
    movie_id = r_admin_auth.json()['id']
    update_payload = {"tagline": "This was updated by a test."}

    # --- Test UPDATE (PATCH) ---
    print(f"   - Testing UPDATE (PATCH /movies/{movie_id}/)...")
    # No Auth
    r_no_auth = requests.patch(f"{API_BASE_URL}/movies/{movie_id}/", json=update_payload)
    print(f"     - No Auth: {'✅ Correctly denied (401)' if r_no_auth.status_code == 401 else f'❌ FAILED (Expected 401, got {r_no_auth.status_code})'}")
    # User Auth
    r_user_auth = requests.patch(f"{API_BASE_URL}/movies/{movie_id}/", headers=user_headers, json=update_payload)
    print(f"     - User Role: {'✅ Correctly denied (403)' if r_user_auth.status_code == 403 else f'❌ FAILED (Expected 403, got {r_user_auth.status_code})'}")
    # Admin Auth
    r_admin_auth = requests.patch(f"{API_BASE_URL}/movies/{movie_id}/", headers=admin_headers, json=update_payload)
    print(f"     - Admin Role: {'✅ Correctly allowed (200)' if r_admin_auth.status_code == 200 else f'❌ FAILED (Expected 200, got {r_admin_auth.status_code})'}")

    # --- Test DELETE ---
    print(f"   - Testing DELETE (/movies/{movie_id}/)...")
    # User Auth (try to delete first)
    r_user_auth = requests.delete(f"{API_BASE_URL}/movies/{movie_id}/", headers=user_headers)
    print(f"     - User Role: {'✅ Correctly denied (403)' if r_user_auth.status_code == 403 else f'❌ FAILED (Expected 403, got {r_user_auth.status_code})'}")
    # Admin Auth
    r_admin_auth = requests.delete(f"{API_BASE_URL}/movies/{movie_id}/", headers=admin_headers)
    print(f"     - Admin Role: {'✅ Correctly allowed (204)' if r_admin_auth.status_code == 204 else f'❌ FAILED (Expected 204, got {r_admin_auth.status_code})'}")
    
    # Verify deletion
    r_verify = requests.get(f"{API_BASE_URL}/movies/{movie_id}/")
    print(f"     - Verify Deletion: {'✅ Movie is gone (404)' if r_verify.status_code == 404 else f'❌ FAILED (Expected 404, got {r_verify.status_code})'}")

def main():
    """Run all API tests."""
    print("🚀 Starting API Security Tests...")
    print("=" * 50)
    
    try:
        setup_test_data()
        test_read_operations()
        test_write_operations()
        
        print("\n" + "=" * 50)
        print("🎉 All API security tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the API. Make sure your server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")

if __name__ == "__main__":
    main()
