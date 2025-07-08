import requests
import json
import uuid
import os
import django

# --- Setup Django Environment to access models ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movielogd.settings')
django.setup()
from users.models import CustomUser
from movies.models import Genre, Movie
# --- End Django Setup ---

# Base URLs
API_BASE_URL = "http://localhost:8000/api"
AUTH_BASE_URL = "http://localhost:8000/api/auth"
CATALOG_BASE_URL = "http://localhost:8000/api/catalog"

# --- Helper Functions ---

def generate_unique_user_data():
    """Generates user data with a unique email."""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "username": f"catalog_test_user_{unique_id}",
        "email": f"catalog_test_{unique_id}@example.com",
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
    """Creates necessary test data (movies, genres) for catalog tests."""
    print("🔧 Setting up test data...")
    
    # Create genres
    Genre.objects.update_or_create(tmdb_id=28, defaults={'name': 'Action'})
    Genre.objects.update_or_create(tmdb_id=12, defaults={'name': 'Adventure'})
    Genre.objects.update_or_create(tmdb_id=18, defaults={'name': 'Drama'})
    
    # Create test movies if they don't exist
    test_movies = [
        {
            'title': 'Test Movie 1',
            'original_title': 'Test Movie 1',
            'overview': 'A test movie for catalog testing',
            'release_date': '2024-01-01',
            'vote_average': 8.5,
            'runtime': 120
        },
        {
            'title': 'Test Movie 2', 
            'original_title': 'Test Movie 2',
            'overview': 'Another test movie for catalog testing',
            'release_date': '2024-02-01',
            'vote_average': 7.8,
            'runtime': 105
        },
        {
            'title': 'Test Movie 3',
            'original_title': 'Test Movie 3', 
            'overview': 'Third test movie for list testing',
            'release_date': '2024-03-01',
            'vote_average': 9.2,
            'runtime': 140
        }
    ]
    
    created_movies = []
    for movie_data in test_movies:
        movie, created = Movie.objects.get_or_create(
            title=movie_data['title'],
            defaults=movie_data
        )
        created_movies.append(movie)
        if created:
            # Add some genres to the movie
            movie.genres.add(28, 18)  # Action and Drama
    
    print(f"   ✅ Created/verified {len(created_movies)} test movies")
    return [movie.id for movie in created_movies]

# --- Test Functions ---

def test_catalog_entries_crud(user_token, movie_ids):
    """Test basic CRUD operations for catalog entries."""
    print("\n📚 Testing Catalog Entries CRUD Operations...")
    
    headers = {'Authorization': f'Bearer {user_token}'}
    
    # Test 1: Bookmark a movie
    print("   - Testing bookmark movie...")
    bookmark_data = {
        "movie_id": movie_ids[0],
        "notes": "Looks interesting, want to watch this weekend"
    }
    response = requests.post(f"{CATALOG_BASE_URL}/entries/bookmark/", json=bookmark_data, headers=headers)
    if response.status_code == 201:
        print("     ✅ Successfully bookmarked movie")
        bookmark_entry = response.json()
    else:
        print(f"     ❌ Failed to bookmark movie: {response.status_code} - {response.text}")
        return False
    
    # Test 2: Mark a movie as watched
    print("   - Testing mark movie as watched...")
    watched_data = {
        "movie_id": movie_ids[1],
        "personal_rating": 8.5,
        "notes": "Great movie! Loved the cinematography"
    }
    response = requests.post(f"{CATALOG_BASE_URL}/entries/mark_watched/", json=watched_data, headers=headers)
    if response.status_code == 201:
        print("     ✅ Successfully marked movie as watched")
        watched_entry = response.json()
    else:
        print(f"     ❌ Failed to mark movie as watched: {response.status_code} - {response.text}")
        return False
    
    # Test 3: Add to watchlist
    print("   - Testing add to watchlist...")
    watchlist_data = {
        "movie_id": movie_ids[2],
        "notes": "Recommended by a friend"
    }
    response = requests.post(f"{CATALOG_BASE_URL}/entries/add_to_watchlist/", json=watchlist_data, headers=headers)
    if response.status_code == 201:
        print("     ✅ Successfully added to watchlist")
    else:
        print(f"     ❌ Failed to add to watchlist: {response.status_code} - {response.text}")
        return False
    
    # Test 4: Get all catalog entries
    print("   - Testing get all catalog entries...")
    response = requests.get(f"{CATALOG_BASE_URL}/entries/", headers=headers)
    if response.status_code == 200:
        entries = response.json()
        print(f"     ✅ Retrieved {len(entries.get('results', entries))} catalog entries")
    else:
        print(f"     ❌ Failed to get catalog entries: {response.status_code} - {response.text}")
        return False
    
    # Test 5: Get bookmarked movies
    print("   - Testing get bookmarked movies...")
    response = requests.get(f"{CATALOG_BASE_URL}/entries/bookmarked/", headers=headers)
    if response.status_code == 200:
        bookmarked = response.json()
        print(f"     ✅ Retrieved bookmarked movies: {len(bookmarked.get('results', bookmarked))} items")
    else:
        print(f"     ❌ Failed to get bookmarked movies: {response.status_code} - {response.text}")
        return False
    
    # Test 6: Get watched movies
    print("   - Testing get watched movies...")
    response = requests.get(f"{CATALOG_BASE_URL}/entries/watched/", headers=headers)
    if response.status_code == 200:
        watched = response.json()
        print(f"     ✅ Retrieved watched movies: {len(watched.get('results', watched))} items")
    else:
        print(f"     ❌ Failed to get watched movies: {response.status_code} - {response.text}")
        return False
    
    # Test 7: Get catalog statistics
    print("   - Testing get catalog statistics...")
    response = requests.get(f"{CATALOG_BASE_URL}/entries/stats/", headers=headers)
    if response.status_code == 200:
        stats = response.json()
        print(f"     ✅ Retrieved catalog stats: {stats}")
    else:
        print(f"     ❌ Failed to get catalog stats: {response.status_code} - {response.text}")
        return False
    
    # Test 8: Remove a movie from catalog
    print("   - Testing remove movie from catalog...")
    remove_data = {"movie_id": movie_ids[0]}
    response = requests.delete(f"{CATALOG_BASE_URL}/entries/remove/", json=remove_data, headers=headers)
    if response.status_code == 204:
        print("     ✅ Successfully removed movie from catalog")
    else:
        print(f"     ❌ Failed to remove movie from catalog: {response.status_code} - {response.text}")
        return False
    
    return True

def test_movie_lists_crud(user_token, movie_ids):
    """Test CRUD operations for movie lists."""
    print("\n🎬 Testing Movie Lists CRUD Operations...")
    
    headers = {'Authorization': f'Bearer {user_token}'}
    
    # Test 1: Create a movie list
    print("   - Testing create movie list...")
    list_data = {
        "name": "My Favorite Action Movies",
        "description": "A collection of the best action movies I've seen",
        "is_public": True
    }
    response = requests.post(f"{CATALOG_BASE_URL}/lists/", json=list_data, headers=headers)
    if response.status_code == 201:
        print("     ✅ Successfully created movie list")
        movie_list = response.json()
        list_id = movie_list['id']
    else:
        print(f"     ❌ Failed to create movie list: {response.status_code} - {response.text}")
        return False
    
    # Test 2: Add movies to the list
    print("   - Testing add movies to list...")
    for i, movie_id in enumerate(movie_ids[:2]):  # Add first 2 movies
        add_data = {"movie_id": movie_id}
        response = requests.post(f"{CATALOG_BASE_URL}/lists/{list_id}/add_movie/", json=add_data, headers=headers)
        if response.status_code == 201:
            print(f"     ✅ Successfully added movie {i+1} to list")
        else:
            print(f"     ❌ Failed to add movie {i+1} to list: {response.status_code} - {response.text}")
    
    # Test 3: Get the list with movies
    print("   - Testing get list with movies...")
    response = requests.get(f"{CATALOG_BASE_URL}/lists/{list_id}/", headers=headers)
    if response.status_code == 200:
        list_detail = response.json()
        print(f"     ✅ Retrieved list with {list_detail.get('movie_count', 0)} movies")
    else:
        print(f"     ❌ Failed to get list detail: {response.status_code} - {response.text}")
        return False
    
    # Test 4: Get all lists
    print("   - Testing get all accessible lists...")
    response = requests.get(f"{CATALOG_BASE_URL}/lists/", headers=headers)
    if response.status_code == 200:
        all_lists = response.json()
        print(f"     ✅ Retrieved {len(all_lists.get('results', all_lists))} accessible lists")
    else:
        print(f"     ❌ Failed to get all lists: {response.status_code} - {response.text}")
        return False
    
    # Test 5: Get only user's lists
    print("   - Testing get user's own lists...")
    response = requests.get(f"{CATALOG_BASE_URL}/lists/my_lists/", headers=headers)
    if response.status_code == 200:
        my_lists = response.json()
        print(f"     ✅ Retrieved {len(my_lists.get('results', my_lists))} user's own lists")
    else:
        print(f"     ❌ Failed to get user's lists: {response.status_code} - {response.text}")
        return False
    
    # Test 6: Remove a movie from the list
    print("   - Testing remove movie from list...")
    remove_data = {"movie_id": movie_ids[0]}
    response = requests.delete(f"{CATALOG_BASE_URL}/lists/{list_id}/remove_movie/", json=remove_data, headers=headers)
    if response.status_code == 204:
        print("     ✅ Successfully removed movie from list")
    else:
        print(f"     ❌ Failed to remove movie from list: {response.status_code} - {response.text}")
        return False
    
    # Test 7: Update the list
    print("   - Testing update movie list...")
    update_data = {
        "name": "My Updated Action Movies List",
        "description": "Updated description for my action movies",
        "is_public": False
    }
    response = requests.patch(f"{CATALOG_BASE_URL}/lists/{list_id}/", json=update_data, headers=headers)
    if response.status_code == 200:
        print("     ✅ Successfully updated movie list")
    else:
        print(f"     ❌ Failed to update movie list: {response.status_code} - {response.text}")
        return False
    
    return list_id

def test_permissions_and_access_control(movie_ids):
    """Test that permissions work correctly."""
    print("\n🔒 Testing Permissions and Access Control...")
    
    # Create two different users
    user1_creds = create_test_user(role=CustomUser.Role.USER)
    user2_creds = create_test_user(role=CustomUser.Role.USER)
    
    user1_token = get_auth_token(user1_creds)
    user2_token = get_auth_token(user2_creds)
    
    if not (user1_token and user2_token):
        print("   ❌ Failed to get tokens for permission testing")
        return False
    
    user1_headers = {'Authorization': f'Bearer {user1_token}'}
    user2_headers = {'Authorization': f'Bearer {user2_token}'}
    
    # Test 1: User 1 creates a catalog entry
    print("   - Testing user isolation for catalog entries...")
    bookmark_data = {"movie_id": movie_ids[0], "notes": "User 1's bookmark"}
    response = requests.post(f"{CATALOG_BASE_URL}/entries/bookmark/", json=bookmark_data, headers=user1_headers)
    if response.status_code == 201:
        print("     ✅ User 1 successfully created catalog entry")
    else:
        print(f"     ❌ User 1 failed to create catalog entry: {response.text}")
        return False
    
    # Test 2: User 2 should not see User 1's catalog entries
    response = requests.get(f"{CATALOG_BASE_URL}/entries/", headers=user2_headers)
    if response.status_code == 200:
        entries = response.json()
        entry_count = len(entries.get('results', entries))
        if entry_count == 0:
            print("     ✅ User 2 correctly sees no catalog entries (user isolation working)")
        else:
            print(f"     ❌ User 2 can see {entry_count} entries (should be 0)")
            return False
    else:
        print(f"     ❌ Failed to get User 2's catalog entries: {response.status_code}")
        return False
    
    # Test 3: User 1 creates a public movie list
    print("   - Testing public vs private movie lists...")
    public_list_data = {
        "name": "User 1's Public List",
        "description": "This should be visible to other users",
        "is_public": True
    }
    response = requests.post(f"{CATALOG_BASE_URL}/lists/", json=public_list_data, headers=user1_headers)
    if response.status_code == 201:
        public_list = response.json()
        public_list_id = public_list['id']
        print("     ✅ User 1 successfully created public list")
    else:
        print(f"     ❌ User 1 failed to create public list: {response.text}")
        return False
    
    # Test 4: User 1 creates a private movie list
    private_list_data = {
        "name": "User 1's Private List",
        "description": "This should NOT be visible to other users",
        "is_public": False
    }
    response = requests.post(f"{CATALOG_BASE_URL}/lists/", json=private_list_data, headers=user1_headers)
    if response.status_code == 201:
        private_list = response.json()
        private_list_id = private_list['id']
        print("     ✅ User 1 successfully created private list")
    else:
        print(f"     ❌ User 1 failed to create private list: {response.text}")
        return False
    
    # Test 5: User 2 should see User 1's public list but not private list
    response = requests.get(f"{CATALOG_BASE_URL}/lists/", headers=user2_headers)
    if response.status_code == 200:
        all_lists = response.json()
        list_results = all_lists.get('results', all_lists)
        
        # Check if User 2 can see the public list
        public_list_visible = any(lst['id'] == public_list_id for lst in list_results)
        private_list_visible = any(lst['id'] == private_list_id for lst in list_results)
        
        if public_list_visible and not private_list_visible:
            print("     ✅ User 2 can see public list but not private list (permissions working)")
        elif not public_list_visible:
            print("     ❌ User 2 cannot see public list (should be visible)")
            return False
        elif private_list_visible:
            print("     ❌ User 2 can see private list (should be hidden)")
            return False
    else:
        print(f"     ❌ Failed to get lists for User 2: {response.status_code}")
        return False
    
    # Test 6: User 2 should not be able to modify User 1's lists
    print("   - Testing list modification permissions...")
    unauthorized_update = {
        "name": "Hacked List Name",
        "description": "User 2 trying to modify User 1's list"
    }
    response = requests.patch(f"{CATALOG_BASE_URL}/lists/{public_list_id}/", json=unauthorized_update, headers=user2_headers)
    if response.status_code == 403:
        print("     ✅ User 2 correctly denied permission to modify User 1's list")
    else:
        print(f"     ❌ User 2 was able to modify User 1's list (should be denied): {response.status_code}")
        return False
    
    # Test 7: Test unauthenticated access
    print("   - Testing unauthenticated access...")
    response = requests.get(f"{CATALOG_BASE_URL}/entries/")
    if response.status_code == 401:
        print("     ✅ Unauthenticated request correctly denied (401)")
    else:
        print(f"     ❌ Unauthenticated request not properly denied: {response.status_code}")
        return False
    
    return True

def test_error_handling(user_token):
    """Test error handling for invalid requests."""
    print("\n⚠️  Testing Error Handling...")
    
    headers = {'Authorization': f'Bearer {user_token}'}
    
    # Test 1: Try to bookmark non-existent movie
    print("   - Testing bookmark non-existent movie...")
    invalid_bookmark = {"movie_id": 99999, "notes": "This movie doesn't exist"}
    response = requests.post(f"{CATALOG_BASE_URL}/entries/bookmark/", json=invalid_bookmark, headers=headers)
    if response.status_code == 400:
        print("     ✅ Correctly rejected non-existent movie ID")
    else:
        print(f"     ❌ Should have rejected non-existent movie: {response.status_code}")
        return False
    
    # Test 2: Try to bookmark without movie_id
    print("   - Testing bookmark without movie_id...")
    invalid_data = {"notes": "Missing movie_id"}
    response = requests.post(f"{CATALOG_BASE_URL}/entries/bookmark/", json=invalid_data, headers=headers)
    if response.status_code == 400:
        print("     ✅ Correctly rejected request without movie_id")
    else:
        print(f"     ❌ Should have rejected request without movie_id: {response.status_code}")
        return False
    
    # Test 3: Try to add invalid rating
    print("   - Testing invalid personal rating...")
    invalid_rating = {
        "movie_id": 1,  # Assuming movie with ID 1 exists
        "personal_rating": 15.0  # Invalid rating (should be 0-10)
    }
    response = requests.post(f"{CATALOG_BASE_URL}/entries/mark_watched/", json=invalid_rating, headers=headers)
    if response.status_code == 400:
        print("     ✅ Correctly rejected invalid rating")
    else:
        print(f"     ❌ Should have rejected invalid rating: {response.status_code}")
        return False
    
    # Test 4: Try to create list with duplicate name
    print("   - Testing duplicate list name...")
    unique_id = uuid.uuid4().hex[:8]  # Add this line
    list_data = {
        "name": f"Test List {unique_id}",  # Make name unique
        "description": "First list", 
        "is_public": False
    }
    response1 = requests.post(f"{CATALOG_BASE_URL}/lists/", json=list_data, headers=headers)
    response2 = requests.post(f"{CATALOG_BASE_URL}/lists/", json=list_data, headers=headers)  # Same name
    
    if response1.status_code == 201 and response2.status_code == 400:
        print("     ✅ Correctly rejected duplicate list name")
    else:
        print(f"     ❌ Duplicate list handling failed: {response1.status_code}, {response2.status_code}")
        return False
    
    return True

def test_edge_cases(user_token, movie_ids):
    """Test edge cases and boundary conditions."""
    print("\n🔍 Testing Edge Cases...")
    
    headers = {'Authorization': f'Bearer {user_token}'}
    
    # Test 1: Bookmark same movie multiple times (should update, not create duplicate)
    print("   - Testing duplicate bookmark handling...")
    bookmark_data = {"movie_id": movie_ids[0], "notes": "First bookmark"}
    response1 = requests.post(f"{CATALOG_BASE_URL}/entries/bookmark/", json=bookmark_data, headers=headers)
    
    bookmark_data_updated = {"movie_id": movie_ids[0], "notes": "Updated bookmark"}
    response2 = requests.post(f"{CATALOG_BASE_URL}/entries/bookmark/", json=bookmark_data_updated, headers=headers)
    
    if response1.status_code == 201 and response2.status_code == 200:
        print("     ✅ Correctly handled duplicate bookmark (update instead of create)")
    else:
        print(f"     ❌ Duplicate bookmark handling failed: {response1.status_code}, {response2.status_code}")
        return False
    
    # Test 2: Change movie status (bookmark -> watched)
    print("   - Testing status change (bookmark to watched)...")
    watched_data = {
        "movie_id": movie_ids[0],
        "personal_rating": 8.0,
        "notes": "Changed from bookmark to watched"
    }
    response = requests.post(f"{CATALOG_BASE_URL}/entries/mark_watched/", json=watched_data, headers=headers)
    if response.status_code in [200, 201]:
        print("     ✅ Successfully changed movie status")
    else:
        print(f"     ❌ Failed to change movie status: {response.status_code}")
        return False
    
    # Test 3: Add same movie to list multiple times
    print("   - Testing duplicate movie in list...")
    list_data = {"name": "Edge Case List", "description": "Testing duplicates", "is_public": False}
    list_response = requests.post(f"{CATALOG_BASE_URL}/lists/", json=list_data, headers=headers)
    
    if list_response.status_code == 201:
        list_id = list_response.json()['id']
        
        # Add movie twice
        add_data = {"movie_id": movie_ids[0]}
        response1 = requests.post(f"{CATALOG_BASE_URL}/lists/{list_id}/add_movie/", json=add_data, headers=headers)
        response2 = requests.post(f"{CATALOG_BASE_URL}/lists/{list_id}/add_movie/", json=add_data, headers=headers)
        
        if response1.status_code == 201 and response2.status_code == 400:
            print("     ✅ Correctly prevented duplicate movie in list")
        else:
            print(f"     ❌ Duplicate movie in list handling failed: {response1.status_code}, {response2.status_code}")
            return False
    else:
        print(f"     ❌ Failed to create test list: {list_response.status_code}")
        return False
    
    # Test 4: Remove non-existent movie from catalog
    print("   - Testing remove non-existent movie from catalog...")
    remove_data = {"movie_id": 99999}
    response = requests.delete(f"{CATALOG_BASE_URL}/entries/remove/", json=remove_data, headers=headers)
    if response.status_code == 404:
        print("     ✅ Correctly handled removal of non-existent movie")
    else:
        print(f"     ❌ Should have returned 404 for non-existent movie: {response.status_code}")
        return False
    
    return True

def main():
    """Run all catalog API tests."""
    print("🚀 Starting Catalog API Tests...")
    print("=" * 60)
    
    try:
        # Setup test data
        movie_ids = setup_test_data()
        
        # Create test user and get token
        user_creds = create_test_user(role=CustomUser.Role.USER)
        user_token = get_auth_token(user_creds)
        
        if not user_token:
            print("❌ Failed to get user token. Aborting tests.")
            return
        
        # Run all test suites
        tests_passed = 0
        total_tests = 5
        
        if test_catalog_entries_crud(user_token, movie_ids):
            tests_passed += 1
        
        if test_movie_lists_crud(user_token, movie_ids):
            tests_passed += 1
        
        if test_permissions_and_access_control(movie_ids):
            tests_passed += 1
        
        if test_error_handling(user_token):
            tests_passed += 1
        
        if test_edge_cases(user_token, movie_ids):
            tests_passed += 1
        
        # Summary
        print("\n" + "=" * 60)
        print(f"🎉 Catalog API Tests Completed!")
        print(f"📊 Results: {tests_passed}/{total_tests} test suites passed")
        
        if tests_passed == total_tests:
            print("✅ All tests passed! Catalog API is working correctly.")
        else:
            print("⚠️  Some tests failed. Please check the output above.")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the API. Make sure your server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

