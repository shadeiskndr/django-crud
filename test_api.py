import requests
import json
from datetime import date

# Base URL for your API
BASE_URL = "http://localhost:8000/api"

# Updated mock movie data - using simple ID arrays instead of nested objects
MOCK_MOVIES = [
    {
        "title": "The Shawshank Redemption",
        "original_title": "The Shawshank Redemption",
        "overview": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
        "release_date": "1994-09-23",
        "runtime": 142,
        "vote_average": 9.3,
        "vote_count": 2343110,
        "popularity": 80.5,
        "budget": 25000000,
        "revenue": 16000000,
        "video": False,
        "original_language": "en",
        "status": "Released",
        "tagline": "Fear can hold you prisoner. Hope can set you free.",
        "homepage": "",
        "poster_path": "/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
        "backdrop_path": "/iNh3BivHyg5sQRPP1KOkzguEX0H.jpg",
        "imdb_id": "tt0111161",
        
        # NEW FORMAT: Simple arrays instead of nested objects
        "genre_ids": [18, 80],  # Drama, Crime
        "spoken_language_codes": ["en"],
        "origin_country_codes": ["US"],
        "production_company_ids": [97],  # Castle Rock Entertainment
        "production_country_codes": ["US"],
        # "video_ids": [],  # Optional - can omit if no videos
        
        # Collection info (flattened)
        "collection_id": None,
        "collection_name": "",
        "collection_poster_path": "",
        "collection_backdrop_path": "",
        
        # External IDs (flattened)
        "external_imdb_id": "tt0111161",
        "external_twitter_id": "",
        "external_facebook_id": "",
        "external_wikidata_id": "",
        "external_instagram_id": "",
    },
    # ... other movies would follow the same pattern
]

def test_create_movies():
    """Test creating movies with the new relational format"""
    print("🎬 Creating movies...")
    created_movies = []
    
    for movie_data in MOCK_MOVIES:
        response = requests.post(f"{BASE_URL}/movies/", json=movie_data)
        if response.status_code == 201:
            movie = response.json()
            created_movies.append(movie)
            print(f"✅ Created: {movie['title']} (ID: {movie['id']})")
            
            # Show the nested relations in the response
            if movie.get('genres'):
                genres = [g['name'] for g in movie['genres']]
                print(f"   Genres: {', '.join(genres)}")
                
        else:
            print(f"❌ Failed to create {movie_data['title']}: {response.status_code}")
            print(f"   Error: {response.text}")
    
    return created_movies

def test_list_movies():
    """Test listing movies"""
    print("\n📋 Listing all movies...")
    response = requests.get(f"{BASE_URL}/movies/")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['count']} movies")
        for movie in data['results']:
            print(f"   - {movie['title']} ({movie['release_date']}) - Rating: {movie['vote_average']}")
    else:
        print(f"❌ Failed to list movies: {response.status_code}")

def test_search_movies():
    """Test searching movies"""
    print("\n🔍 Testing search functionality...")
    
    # Search by title
    response = requests.get(f"{BASE_URL}/movies/?search=godfather")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Search 'godfather': {data['count']} results")
        for movie in data['results']:
            print(f"   - {movie['title']}")
    
    # Filter by genre
    response = requests.get(f"{BASE_URL}/movies/?genre=Crime")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Genre 'Crime': {data['count']} results")
        for movie in data['results']:
            print(f"   - {movie['title']}")
    
    # Filter by year
    response = requests.get(f"{BASE_URL}/movies/?year=1994")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Year '1994': {data['count']} results")
        for movie in data['results']:
            print(f"   - {movie['title']}")
    
    # Filter by minimum rating
    response = requests.get(f"{BASE_URL}/movies/?min_rating=9.0")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Min rating 9.0: {data['count']} results")
        for movie in data['results']:
            print(f"   - {movie['title']} ({movie['vote_average']})")

def test_get_movie_detail(movie_id):
    """Test getting movie details"""
    print(f"\n🎭 Getting details for movie ID {movie_id}...")
    response = requests.get(f"{BASE_URL}/movies/{movie_id}/")
    if response.status_code == 200:
        movie = response.json()
        print(f"✅ Retrieved: {movie['title']}")
        print(f"   Overview: {movie['overview'][:100]}...")
        print(f"   Runtime: {movie['runtime']} minutes")
        print(f"   Rating: {movie['vote_average']}/10")
        return movie
    else:
        print(f"❌ Failed to get movie {movie_id}: {response.status_code}")
        return None

def test_update_movie(movie_id):
    """Test updating a movie"""
    print(f"\n✏️ Updating movie ID {movie_id}...")
    
    # Partial update (PATCH)
    update_data = {
        "tagline": "Updated tagline for testing!",
        "popularity": 99.9
    }
    
    response = requests.patch(f"{BASE_URL}/movies/{movie_id}/", json=update_data)
    if response.status_code == 200:
        movie = response.json()
        print(f"✅ Updated: {movie['title']}")
        print(f"   New tagline: {movie['tagline']}")
        print(f"   New popularity: {movie['popularity']}")
    else:
        print(f"❌ Failed to update movie {movie_id}: {response.status_code}")
        print(f"   Error: {response.text}")

def test_movie_stats():
    """Test getting movie statistics"""
    print("\n📊 Getting movie statistics...")
    response = requests.get(f"{BASE_URL}/movies/stats/")
    if response.status_code == 200:
        stats = response.json()
        print("✅ Statistics:")
        print(f"   Total movies: {stats['total_movies']}")
        print(f"   Average rating: {stats['avg_rating']:.2f}")
        print(f"   Highest rating: {stats['highest_rating']}")
        print(f"   Average runtime: {stats['avg_runtime']:.1f} minutes")
        print(f"   Top genres:")
        for genre_info in stats['top_genres'][:5]:
            print(f"     - {genre_info['genre']}: {genre_info['count']} movies")
    else:
        print(f"❌ Failed to get stats: {response.status_code}")

def test_delete_movie(movie_id):
    """Test deleting a movie"""
    print(f"\n🗑️ Deleting movie ID {movie_id}...")
    response = requests.delete(f"{BASE_URL}/movies/{movie_id}/")
    if response.status_code == 204:
        print(f"✅ Successfully deleted movie {movie_id}")
    else:
        print(f"❌ Failed to delete movie {movie_id}: {response.status_code}")

def main():
    """Run all tests"""
    print("🚀 Starting API Tests...")
    print("=" * 50)
    
    try:
        # Test creating movies
        created_movies = test_create_movies()
        
        if not created_movies:
            print("❌ No movies were created. Stopping tests.")
            return
        
        # Test listing movies
        test_list_movies()
        
        # Test search functionality
        test_search_movies()
        
        # Test getting movie details
        first_movie = test_get_movie_detail(created_movies[0]['id'])
        
        # Test updating a movie
        test_update_movie(created_movies[0]['id'])
        
        # Test movie statistics
        test_movie_stats()
        
        # Test deleting a movie (delete the last one)
        if len(created_movies) > 0:
            test_delete_movie(created_movies[-1]['id'])
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure your server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()

