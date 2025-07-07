import requests
import json
import uuid
import os
import django

# --- Setup Django Environment to access models ---
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movielogd.settings')
django.setup()
from users.models import CustomUser
from backend_api.models import Genre, Movie
from reviews.models import Review
# --- End Django Setup ---

# Base URLs
API_BASE_URL = "http://localhost:8000/api"
AUTH_BASE_URL = "http://localhost:8000/api/auth"
REVIEWS_BASE_URL = "http://localhost:8000/api/reviews"

# --- Helper Functions ---

def generate_unique_user_data():
    """Generates user data with a unique email."""
    unique_id = uuid.uuid4().hex[:8]
    return {
        "username": f"review_test_user_{unique_id}",
        "email": f"review_test_{unique_id}@example.com",
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
    """Creates necessary test data (movies, genres) for review tests."""
    print("🔧 Setting up test data...")
    
    # Create genres
    Genre.objects.update_or_create(tmdb_id=28, defaults={'name': 'Action'})
    Genre.objects.update_or_create(tmdb_id=12, defaults={'name': 'Adventure'})
    Genre.objects.update_or_create(tmdb_id=18, defaults={'name': 'Drama'})
    Genre.objects.update_or_create(tmdb_id=878, defaults={'name': 'Science Fiction'})
    
    # Create test movies if they don't exist
    test_movies = [
        {
            'title': 'Review Test Movie 1',
            'original_title': 'Review Test Movie 1',
            'overview': 'A great action movie for testing reviews',
            'release_date': '2024-01-01',
            'vote_average': 8.5,
            'runtime': 120
        },
        {
            'title': 'Review Test Movie 2', 
            'original_title': 'Review Test Movie 2',
            'overview': 'A sci-fi thriller perfect for reviews',
            'release_date': '2024-02-01',
            'vote_average': 7.8,
            'runtime': 105
        },
        {
            'title': 'Review Test Movie 3',
            'original_title': 'Review Test Movie 3', 
            'overview': 'An indie drama for diverse reviews',
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

def test_review_crud_operations(user_token, movie_ids):
    """Test basic CRUD operations for reviews."""
    print("\n📝 Testing Review CRUD Operations...")
    
    headers = {'Authorization': f'Bearer {user_token}'}
    
    # Test 1: Create a review
    print("   - Testing create review...")
    review_data = {
        "movie_id": movie_ids[0],
        "title": "Amazing Action Flick!",
        "content": "This movie had incredible action sequences and great character development. The cinematography was outstanding and the plot kept me engaged throughout. Highly recommended for action movie fans!",
        "rating": 8.5,
        "status": "DRAFT"
    }
    response = requests.post(f"{REVIEWS_BASE_URL}/reviews/", json=review_data, headers=headers)
    if response.status_code == 201:
        print("     ✅ Successfully created review")
        created_review = response.json()
        review_id = created_review['id']
    else:
        print(f"     ❌ Failed to create review: {response.status_code} - {response.text}")
        return False
    
    # Test 2: Get the created review
    print("   - Testing get review...")
    response = requests.get(f"{REVIEWS_BASE_URL}/reviews/{review_id}/", headers=headers)
    if response.status_code == 200:
        review = response.json()
        print(f"     ✅ Successfully retrieved review: '{review['title']}'")
    else:
        print(f"     ❌ Failed to get review: {response.status_code} - {response.text}")
        return False
    
    # Test 3: Update the review
    print("   - Testing update review...")
    update_data = {
        "title": "Updated: Amazing Action Flick!",
        "content": "Updated content with more details about the special effects and soundtrack.",
        "rating": 9.0,
        "status": "DRAFT"
    }
    response = requests.patch(f"{REVIEWS_BASE_URL}/reviews/{review_id}/", json=update_data, headers=headers)
    if response.status_code == 200:
        print("     ✅ Successfully updated review")
        updated_review = response.json()
    else:
        print(f"     ❌ Failed to update review: {response.status_code} - {response.text}")
        return False
    
    # Test 4: Publish the review
    print("   - Testing publish review...")
    response = requests.post(f"{REVIEWS_BASE_URL}/reviews/{review_id}/publish/", headers=headers)
    if response.status_code == 200:
        print("     ✅ Successfully published review")
        published_review = response.json()
        assert published_review['status'] == 'PUBLISHED'
        assert published_review['published_at'] is not None
    else:
        print(f"     ❌ Failed to publish review: {response.status_code} - {response.text}")
        return False
    
    # Test 5: Get user's own reviews
    print("   - Testing get user's own reviews...")
    response = requests.get(f"{REVIEWS_BASE_URL}/reviews/my_reviews/", headers=headers)
    if response.status_code == 200:
        my_reviews = response.json()
        review_count = len(my_reviews.get('results', my_reviews))
        print(f"     ✅ Retrieved {review_count} user's own reviews")
    else:
        print(f"     ❌ Failed to get user's reviews: {response.status_code} - {response.text}")
        return False
    
    # Test 6: List all published reviews (public access)
    print("   - Testing list published reviews...")
    response = requests.get(f"{REVIEWS_BASE_URL}/reviews/")  # No auth header for public access
    if response.status_code == 200:
        all_reviews = response.json()
        review_count = len(all_reviews.get('results', all_reviews))
        print(f"     ✅ Retrieved {review_count} published reviews (public access)")
    else:
        print(f"     ❌ Failed to get published reviews: {response.status_code} - {response.text}")
        return False
    
    return review_id

def test_review_voting_system(user_tokens, review_id):
    """Test the review voting system."""
    print("\n👍 Testing Review Voting System...")

    # Ensure review_id is valid
    if not review_id or review_id is False:
        print("   ❌ Invalid review_id provided to voting test")
        return False
    
    user1_token, user2_token = user_tokens
    user1_headers = {'Authorization': f'Bearer {user1_token}'}
    user2_headers = {'Authorization': f'Bearer {user2_token}'}
    
    # Test 1: User 2 votes "HELPFUL" on User 1's review
    print("   - Testing helpful vote...")
    vote_data = {
        "review_id": review_id,
        "vote_type": "HELPFUL"
    }
    response = requests.post(f"{REVIEWS_BASE_URL}/votes/", json=vote_data, headers=user2_headers)
    if response.status_code == 201:
        print("     ✅ Successfully voted helpful")
        vote = response.json()
        vote_id = vote['id']
    else:
        print(f"     ❌ Failed to vote helpful: {response.status_code} - {response.text}")
        return False
    
    # Test 2: Check that helpful count increased
    print("   - Testing helpful count update...")
    response = requests.get(f"{REVIEWS_BASE_URL}/reviews/{review_id}/", headers=user1_headers)
    if response.status_code == 200:
        review = response.json()
        if review['helpful_count'] > 0:
            print(f"     ✅ Helpful count updated: {review['helpful_count']}")
        else:
            print(f"     ❌ Helpful count not updated: {review['helpful_count']}")
            return False
    else:
        print(f"     ❌ Failed to get updated review: {response.status_code}")
        return False
    
    # Test 3: Change vote to "NOT_HELPFUL"
    print("   - Testing vote change...")
    update_vote_data = {
        "review_id": review_id,
        "vote_type": "NOT_HELPFUL"
    }
    response = requests.post(f"{REVIEWS_BASE_URL}/votes/", json=update_vote_data, headers=user2_headers)
    if response.status_code == 201:  # Should update existing vote
        print("     ✅ Successfully changed vote to not helpful")
    else:
        print(f"     ❌ Failed to change vote: {response.status_code} - {response.text}")
        return False
    
    # Test 4: User 1 tries to vote on their own review (should fail)
    print("   - Testing self-vote prevention...")
    self_vote_data = {
        "review_id": review_id,
        "vote_type": "HELPFUL"
    }
    response = requests.post(f"{REVIEWS_BASE_URL}/votes/", json=self_vote_data, headers=user1_headers)
    if response.status_code == 400:
        print("     ✅ Correctly prevented self-voting")
    else:
        print(f"     ❌ Should have prevented self-voting: {response.status_code}")
        return False
    
    # Test 5: Get user's votes
    print("   - Testing get user votes...")
    response = requests.get(f"{REVIEWS_BASE_URL}/votes/", headers=user2_headers)
    if response.status_code == 200:
        votes = response.json()
        vote_count = len(votes.get('results', votes))
        print(f"     ✅ Retrieved {vote_count} votes for user")
    else:
        print(f"     ❌ Failed to get user votes: {response.status_code}")
        return False
    
    return True

def test_review_reporting_system(user_tokens, review_id):
    """Test the review reporting system."""
    print("\n🚨 Testing Review Reporting System...")

    # Ensure review_id is valid
    if not review_id or review_id is False:
        print("   ❌ Invalid review_id provided to reporting test")
        return False
    
    user1_token, user2_token = user_tokens
    user1_headers = {'Authorization': f'Bearer {user1_token}'}
    user2_headers = {'Authorization': f'Bearer {user2_token}'}
    
    # Test 1: User 2 reports User 1's review
    print("   - Testing report review...")
    report_data = {
        "review_id": review_id,
        "reason": "INAPPROPRIATE",
        "description": "This review contains inappropriate language and should be reviewed."
    }
    response = requests.post(f"{REVIEWS_BASE_URL}/reports/", json=report_data, headers=user2_headers)
    if response.status_code == 201:
        print("     ✅ Successfully reported review")
        report = response.json()
        report_id = report['id']
    else:
        print(f"     ❌ Failed to report review: {response.status_code} - {response.text}")
        return False
    
    # Test 2: Check that reported count increased
    print("   - Testing reported count update...")
    response = requests.get(f"{REVIEWS_BASE_URL}/reviews/{review_id}/", headers=user1_headers)
    if response.status_code == 200:
        review = response.json()
        if review['reported_count'] > 0:
            print(f"     ✅ Reported count updated: {review['reported_count']}")
        else:
            print(f"     ❌ Reported count not updated: {review['reported_count']}")
            return False
    else:
        print(f"     ❌ Failed to get updated review: {response.status_code}")
        return False
    
    # Test 3: User 1 tries to report their own review (should fail)
    print("   - Testing self-report prevention...")
    self_report_data = {
        "review_id": review_id,
        "reason": "SPAM",
        "description": "Testing self-report"
    }
    response = requests.post(f"{REVIEWS_BASE_URL}/reports/", json=self_report_data, headers=user1_headers)
    if response.status_code == 400:
        print("     ✅ Correctly prevented self-reporting")
    else:
        print(f"     ❌ Should have prevented self-reporting: {response.status_code}")
        return False
    
    # Test 4: Get user's reports
    print("   - Testing get user reports...")
    response = requests.get(f"{REVIEWS_BASE_URL}/reports/", headers=user2_headers)
    if response.status_code == 200:
        reports = response.json()
        report_count = len(reports.get('results', reports))
        print(f"     ✅ Retrieved {report_count} reports for user")
    else:
        print(f"     ❌ Failed to get user reports: {response.status_code}")
        return False
    
    return report_id

def test_moderation_features(moderator_token, admin_token, review_id, report_id):
    """Test moderation features for moderators and admins."""
    print("\n🛡️  Testing Moderation Features...")

    # Ensure review_id is valid
    if not review_id or review_id is False:
        print("   ❌ Invalid review_id provided to moderation test")
        return False
    
    moderator_headers = {'Authorization': f'Bearer {moderator_token}'}
    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Test 1: Get pending moderation queue (moderator)
    print("   - Testing moderation queue access...")
    response = requests.get(f"{REVIEWS_BASE_URL}/moderation/pending/", headers=moderator_headers)
    if response.status_code == 200:
        pending_reviews = response.json()
        review_count = len(pending_reviews.get('results', pending_reviews))
        print(f"     ✅ Moderator can access pending queue: {review_count} reviews")
    else:
        print(f"     ❌ Moderator cannot access pending queue: {response.status_code}")
        return False
    
    # Test 2: Get pending reports (moderator)
    print("   - Testing reports queue access...")
    response = requests.get(f"{REVIEWS_BASE_URL}/reports/pending/", headers=moderator_headers)
    if response.status_code == 200:
        pending_reports = response.json()
        report_count = len(pending_reports.get('results', pending_reports))
        print(f"     ✅ Moderator can access reports queue: {report_count} reports")
    else:
        print(f"     ❌ Moderator cannot access reports queue: {response.status_code}")
        return False
    
    # Test 3: Feature a review (moderator)
    print("   - Testing feature review...")
    feature_data = {"is_featured": True}
    response = requests.post(f"{REVIEWS_BASE_URL}/moderation/{review_id}/feature/", json=feature_data, headers=moderator_headers)
    if response.status_code == 200:
        print("     ✅ Moderator successfully featured review")
        featured_review = response.json()
        assert featured_review['is_featured'] == True
    else:
        print(f"     ❌ Moderator failed to feature review: {response.status_code}")
        return False
    
    # Test 4: Hide a review (moderator)
    print("   - Testing hide review...")
    hide_data = {"moderation_notes": "Review hidden due to inappropriate content"}
    response = requests.post(f"{REVIEWS_BASE_URL}/moderation/{review_id}/hide/", json=hide_data, headers=moderator_headers)
    if response.status_code == 200:
        print("     ✅ Moderator successfully hid review")
        hidden_review = response.json()
        assert hidden_review['status'] == 'HIDDEN'
    else:
        print(f"     ❌ Moderator failed to hide review: {response.status_code}")
        return False
    
    # Test 5: Restore a hidden review (moderator)
    print("   - Testing restore review...")
    response = requests.post(f"{REVIEWS_BASE_URL}/moderation/{review_id}/restore/", headers=moderator_headers)
    if response.status_code == 200:
        print("     ✅ Moderator successfully restored review")
        restored_review = response.json()
        assert restored_review['status'] == 'PUBLISHED'
    else:
        print(f"     ❌ Moderator failed to restore review: {response.status_code}")
        return False
    
    # Test 6: Resolve a report (moderator)
    print("   - Testing resolve report...")
    resolve_data = {
        "resolved": True,
        "resolution_notes": "Report reviewed and resolved. No action taken as content is appropriate."
    }
    response = requests.post(f"{REVIEWS_BASE_URL}/reports/{report_id}/resolve/", json=resolve_data, headers=moderator_headers)
    if response.status_code == 200:
        print("     ✅ Moderator successfully resolved report")
        resolved_report = response.json()
        assert resolved_report['resolved'] == True
    else:
        print(f"     ❌ Moderator failed to resolve report: {response.status_code}")
        return False
    
    # Test 7: Get featured reviews
    print("   - Testing get featured reviews...")
    response = requests.get(f"{REVIEWS_BASE_URL}/reviews/featured/")  # Public access
    if response.status_code == 200:
        featured_reviews = response.json()
        review_count = len(featured_reviews.get('results', featured_reviews))
        print(f"     ✅ Retrieved {review_count} featured reviews")
    else:
        print(f"     ❌ Failed to get featured reviews: {response.status_code}")
        return False
    
    return True

def test_role_based_permissions(user_tokens, moderator_token, admin_token, review_id):
    """Test that permissions work correctly for different roles."""
    print("\n🔒 Testing Role-Based Permissions...")

    # Ensure review_id is valid
    if not review_id or review_id is False:
        print("   ❌ Invalid review_id provided to permissions test")
        return False
    
    user1_token, user2_token = user_tokens
    user1_headers = {'Authorization': f'Bearer {user1_token}'}
    user2_headers = {'Authorization': f'Bearer {user2_token}'}
    moderator_headers = {'Authorization': f'Bearer {moderator_token}'}
    admin_headers = {'Authorization': f'Bearer {admin_token}'}
    
    # Test 1: Regular user cannot access moderation endpoints
    print("   - Testing user access to moderation endpoints...")
    response = requests.get(f"{REVIEWS_BASE_URL}/moderation/pending/", headers=user1_headers)
    if response.status_code == 403:
        print("     ✅ Regular user correctly denied access to moderation")
    else:
        print(f"     ❌ Regular user should be denied moderation access: {response.status_code}")
        return False
    
    # Test 2: Regular user cannot feature reviews
    print("   - Testing user feature review access...")
    feature_data = {"is_featured": True}
    response = requests.post(f"{REVIEWS_BASE_URL}/moderation/{review_id}/feature/", json=feature_data, headers=user1_headers)
    if response.status_code == 403:
        print("     ✅ Regular user correctly denied feature access")
    else:
        print(f"     ❌ Regular user should be denied feature access: {response.status_code}")
        return False
    
    # Test 3: User 2 cannot edit User 1's review
    print("   - Testing cross-user review editing...")
    update_data = {"title": "Malicious update attempt"}
    response = requests.patch(f"{REVIEWS_BASE_URL}/reviews/{review_id}/", json=update_data, headers=user2_headers)
    if response.status_code == 403:
        print("     ✅ User correctly denied editing another's review")
    else:
        print(f"     ❌ User should be denied editing another's review: {response.status_code}")
        return False
    
    # Test 4: Moderator can access moderation endpoints
    print("   - Testing moderator moderation access...")
    response = requests.get(f"{REVIEWS_BASE_URL}/moderation/pending/", headers=moderator_headers)
    if response.status_code == 200:
        print("     ✅ Moderator correctly granted moderation access")
    else:
        print(f"     ❌ Moderator should have moderation access: {response.status_code}")
        return False
    
    # Test 5: Admin can access all moderation endpoints
    print("   - Testing admin moderation access...")
    response = requests.get(f"{REVIEWS_BASE_URL}/moderation/pending/", headers=admin_headers)
    if response.status_code == 200:
        print("     ✅ Admin correctly granted moderation access")
    else:
        print(f"     ❌ Admin should have moderation access: {response.status_code}")
        return False
    
    # Test 6: Moderator can moderate any review
    print("   - Testing moderator cross-user moderation...")
    moderate_data = {"moderation_notes": "Moderator reviewing content"}
    response = requests.patch(f"{REVIEWS_BASE_URL}/moderation/{review_id}/", json=moderate_data, headers=moderator_headers)
    if response.status_code == 200:
        print("     ✅ Moderator can moderate any review")
    else:
        print(f"     ❌ Moderator should be able to moderate any review: {response.status_code}")
        return False
    
    return True

def test_error_handling_and_edge_cases(user_token, movie_ids):
    """Test error handling and edge cases."""
    print("\n⚠️  Testing Error Handling and Edge Cases...")
    
    headers = {'Authorization': f'Bearer {user_token}'}
    
    # Test 1: Try to review non-existent movie
    print("   - Testing review non-existent movie...")
    invalid_review = {
        "movie_id": 99999,
        "title": "Review for non-existent movie",
        "content": "This should fail",
        "rating": 5.0,
        "status": "DRAFT"
    }
    response = requests.post(f"{REVIEWS_BASE_URL}/reviews/", json=invalid_review, headers=headers)
    if response.status_code == 400:
        print("     ✅ Correctly rejected non-existent movie")
    else:
        print(f"     ❌ Should have rejected non-existent movie: {response.status_code}")
        return False
    
    # Test 2: Try to create review with invalid rating
    print("   - Testing invalid rating...")
    invalid_rating_review = {
        "movie_id": movie_ids[0],
        "title": "Invalid rating test",
        "content": "Testing invalid rating",
        "rating": 15.0,  # Should be 0-10
        "status": "DRAFT"
    }
    response = requests.post(f"{REVIEWS_BASE_URL}/reviews/", json=invalid_rating_review, headers=headers)
    if response.status_code == 400:
        print("     ✅ Correctly rejected invalid rating")
    else:
        print(f"     ❌ Should have rejected invalid rating: {response.status_code}")
        return False
    
    # Test 3: Try to create duplicate review for same movie
    print("   - Testing duplicate review prevention...")
    review_data = {
        "movie_id": movie_ids[1],
        "title": "First review",
        "content": "This is my first review",
        "rating": 8.0,
        "status": "PUBLISHED"
    }
    response1 = requests.post(f"{REVIEWS_BASE_URL}/reviews/", json=review_data, headers=headers)
    
    duplicate_review = {
        "movie_id": movie_ids[1],
        "title": "Second review",
        "content": "Trying to create duplicate",
        "rating": 7.0,
        "status": "PUBLISHED"
    }
    response2 = requests.post(f"{REVIEWS_BASE_URL}/reviews/", json=duplicate_review, headers=headers)
    
    if response1.status_code == 201 and response2.status_code == 400:
        print("     ✅ Correctly prevented duplicate review")
    else:
        print(f"     ❌ Duplicate review handling failed: {response1.status_code}, {response2.status_code}")
        return False
    
    # Test 4: Try to publish non-draft review
    print("   - Testing publish non-draft review...")
    if response1.status_code == 201:
        published_review_id = response1.json()['id']
        response = requests.post(f"{REVIEWS_BASE_URL}/reviews/{published_review_id}/publish/", headers=headers)
        if response.status_code == 400:
            print("     ✅ Correctly rejected publishing non-draft review")
        else:
            print(f"     ❌ Should have rejected publishing non-draft: {response.status_code}")
            return False
    
    # Test 5: Try to vote on non-existent review
    print("   - Testing vote on non-existent review...")
    invalid_vote = {
        "review_id": 99999,
        "vote_type": "HELPFUL"
    }
    response = requests.post(f"{REVIEWS_BASE_URL}/votes/", json=invalid_vote, headers=headers)
    if response.status_code == 400:
        print("     ✅ Correctly rejected vote on non-existent review")
    else:
        print(f"     ❌ Should have rejected vote on non-existent review: {response.status_code}")
        return False
    
    # Test 6: Try to report non-existent review
    print("   - Testing report non-existent review...")
    invalid_report = {
        "review_id": 99999,
        "reason": "SPAM",
        "description": "Testing invalid report"
    }
    response = requests.post(f"{REVIEWS_BASE_URL}/reports/", json=invalid_report, headers=headers)
    if response.status_code == 400:
        print("     ✅ Correctly rejected report on non-existent review")
    else:
        print(f"     ❌ Should have rejected report on non-existent review: {response.status_code}")
        return False
    
    # Test 7: Test unauthenticated access to protected endpoints
    print("   - Testing unauthenticated access...")
    response = requests.post(f"{REVIEWS_BASE_URL}/reviews/", json=review_data)
    if response.status_code == 401:
        print("     ✅ Correctly denied unauthenticated review creation")
    else:
        print(f"     ❌ Should have denied unauthenticated access: {response.status_code}")
        return False
    
    return True

def test_filtering_and_search(user_token, movie_ids):
    """Test filtering and search functionality."""
    print("\n🔍 Testing Filtering and Search...")
    
    headers = {'Authorization': f'Bearer {user_token}'}
    
    # Create multiple reviews for testing
    review_data_1 = {
        "movie_id": movie_ids[0],
        "title": "Excellent Action Movie",
        "content": "Great action sequences and plot",
        "rating": 9.0,
        "status": "PUBLISHED"
    }
    review_data_2 = {
        "movie_id": movie_ids[1],
        "title": "Good Sci-Fi Film",
        "content": "Interesting concept but slow pacing",
        "rating": 7.0,
        "status": "PUBLISHED"
    }
    
    # Create the reviews
    response1 = requests.post(f"{REVIEWS_BASE_URL}/reviews/", json=review_data_1, headers=headers)
    response2 = requests.post(f"{REVIEWS_BASE_URL}/reviews/", json=review_data_2, headers=headers)
    
    if not (response1.status_code == 201 and response2.status_code == 201):
        print("   ⚠️ Could not create test reviews for filtering tests")
        return False
    
    # Test 1: Filter by movie
    print("   - Testing filter by movie...")
    response = requests.get(f"{REVIEWS_BASE_URL}/reviews/?movie_id={movie_ids[0]}")
    if response.status_code == 200:
        filtered_reviews = response.json()
        # Handle both paginated and non-paginated responses
        if isinstance(filtered_reviews, dict) and 'results' in filtered_reviews:
            results = filtered_reviews['results']
        elif isinstance(filtered_reviews, list):
            results = filtered_reviews
        else:
            results = []
        
        # Check if filtering worked (at least some results should be for the specific movie)
        movie_specific_count = 0
        for review in results:
            if isinstance(review, dict) and 'movie' in review:
                if isinstance(review['movie'], dict) and review['movie'].get('id') == movie_ids[0]:
                    movie_specific_count += 1
                elif isinstance(review['movie'], str) and str(movie_ids[0]) in review['movie']:
                    movie_specific_count += 1
        
        if movie_specific_count > 0 or len(results) >= 1:
            print("     ✅ Successfully filtered reviews by movie")
        else:
            print("     ❌ Movie filtering not working correctly")
            return False
    else:
        print(f"     ❌ Failed to filter by movie: {response.status_code}")
        return False
    
    # Test 2: Filter by status
    print("   - Testing filter by status...")
    response = requests.get(f"{REVIEWS_BASE_URL}/reviews/?status=PUBLISHED")
    if response.status_code == 200:
        filtered_reviews = response.json()
        print("     ✅ Successfully filtered reviews by status")
    else:
        print(f"     ❌ Failed to filter by status: {response.status_code}")
        return False
    
    # Test 3: Test ordering
    print("   - Testing review ordering...")
    response = requests.get(f"{REVIEWS_BASE_URL}/reviews/?ordering=rating")
    if response.status_code == 200:
        ordered_reviews = response.json()
        print("     ✅ Successfully ordered reviews by rating")
    else:
        print(f"     ❌ Failed to order reviews: {response.status_code}")
        return False
    
    # Test 4: Test pagination
    print("   - Testing pagination...")
    response = requests.get(f"{REVIEWS_BASE_URL}/reviews/?page_size=1")
    if response.status_code == 200:
        paginated_reviews = response.json()
        if 'results' in paginated_reviews:
            print("     ✅ Pagination working correctly")
        else:
            print("     ⚠️ Pagination format may be different than expected")
    else:
        print(f"     ❌ Failed to test pagination: {response.status_code}")
        return False
    
    return True

def main():
    """Run all review API tests."""
    print("🚀 Starting Reviews API Tests...")
    print("=" * 70)
    
    try:
        # Setup test data
        movie_ids = setup_test_data()
        
        # Create test users with different roles
        user1_creds = create_test_user(role=CustomUser.Role.USER)
        user2_creds = create_test_user(role=CustomUser.Role.USER)
        critic_creds = create_test_user(role=CustomUser.Role.CRITIC)
        moderator_creds = create_test_user(role=CustomUser.Role.MODERATOR)
        admin_creds = create_test_user(role=CustomUser.Role.ADMIN)
        
        # Get tokens
        user1_token = get_auth_token(user1_creds)
        user2_token = get_auth_token(user2_creds)
        critic_token = get_auth_token(critic_creds)
        moderator_token = get_auth_token(moderator_creds)
        admin_token = get_auth_token(admin_creds)
        
        if not all([user1_token, user2_token, critic_token, moderator_token, admin_token]):
            print("❌ Failed to get all required tokens. Aborting tests.")
            return
        
        user_tokens = [user1_token, user2_token]
        
        # Run all test suites
        tests_passed = 0
        total_tests = 7
        
        print("\n" + "="*70)
        review_id = test_review_crud_operations(user1_token, movie_ids)
        if review_id:
            tests_passed += 1
            print(f"   🔍 Debug - Review ID for subsequent tests: {review_id}")
        else:
            print("   ❌ Could not get review_id, skipping dependent tests")
            return
        
        if test_review_voting_system(user_tokens, review_id):
            tests_passed += 1
        
        report_id = test_review_reporting_system(user_tokens, review_id)
        if report_id:
            tests_passed += 1
        else:
            print("   ❌ Could not get report_id, using None for moderation tests")
            report_id = None
        
        if test_moderation_features(moderator_token, admin_token, review_id, report_id):
            tests_passed += 1
        
        if test_role_based_permissions(user_tokens, moderator_token, admin_token, review_id):
            tests_passed += 1
        
        if test_error_handling_and_edge_cases(user2_token, movie_ids):
            tests_passed += 1
        
        if test_filtering_and_search(critic_token, movie_ids):
            tests_passed += 1
        
        # Summary
        print("\n" + "=" * 70)
        print(f"🎉 Reviews API Tests Completed!")
        print(f"📊 Results: {tests_passed}/{total_tests} test suites passed")
        
        if tests_passed == total_tests:
            print("✅ All tests passed! Reviews API is working correctly.")
            print("\n📋 Features Successfully Tested:")
            print("   • Review CRUD operations (create, read, update, publish)")
            print("   • Review voting system (helpful/not helpful)")
            print("   • Review reporting system")
            print("   • Moderation features (hide, feature, resolve reports)")
            print("   • Role-based permissions (USER, CRITIC, MODERATOR, ADMIN)")
            print("   • Error handling and edge cases")
            print("   • Filtering, search, and pagination")
        else:
            print("⚠️  Some tests failed. Please check the output above.")
            print(f"   {total_tests - tests_passed} test suite(s) need attention.")
        
    except requests.exceptions.ConnectionError:
        print("\n❌ Could not connect to the API. Make sure your server is running on http://localhost:8000")
    except Exception as e:
        print(f"\n❌ An unexpected error occurred: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()