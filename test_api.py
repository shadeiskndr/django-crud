import requests
import json
from datetime import date

# Base URL for your API
BASE_URL = "http://localhost:8000/api"

# Mock movie data
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
        "adult": False,
        "video": False,
        "original_language": "en",
        "status": "Released",
        "tagline": "Fear can hold you prisoner. Hope can set you free.",
        "homepage": "",
        "poster_path": "/q6y0Go1tsGEsmtFryDOJo3dEmqu.jpg",
        "backdrop_path": "/iNh3BivHyg5sQRPP1KOkzguEX0H.jpg",
        "imdb_id": "tt0111161",
        "genres": [{"id": 18, "name": "Drama"}, {"id": 80, "name": "Crime"}],
        "genres_names": "Drama, Crime",
        "origin_country": ["US"],
        "spoken_languages": [{"english_name": "English", "iso_639_1": "en", "name": "English"}],
        "spoken_languages_names": "English",
        "production_companies": [{"id": 97, "name": "Castle Rock Entertainment"}],
        "production_companies_names": "Castle Rock Entertainment",
        "production_countries": [{"iso_3166_1": "US", "name": "United States of America"}],
        "production_countries_names": "United States of America"
    },
    {
        "title": "The Godfather",
        "original_title": "The Godfather",
        "overview": "The aging patriarch of an organized crime dynasty transfers control of his clandestine empire to his reluctant son.",
        "release_date": "1972-03-24",
        "runtime": 175,
        "vote_average": 9.2,
        "vote_count": 1735967,
        "popularity": 75.2,
        "budget": 6000000,
        "revenue": 245066411,
        "adult": False,
        "video": False,
        "original_language": "en",
        "status": "Released",
        "tagline": "An offer you can't refuse.",
        "homepage": "",
        "poster_path": "/3bhkrj58Vtu7enYsRolD1fZdja1.jpg",
        "backdrop_path": "/tmU7GeKVybMWFButWEGl2M4GeiP.jpg",
        "imdb_id": "tt0068646",
        "genres": [{"id": 18, "name": "Drama"}, {"id": 80, "name": "Crime"}],
        "genres_names": "Drama, Crime",
        "origin_country": ["US"],
        "spoken_languages": [{"english_name": "English", "iso_639_1": "en", "name": "English"}],
        "spoken_languages_names": "English",
        "production_companies": [{"id": 4, "name": "Paramount Pictures"}],
        "production_companies_names": "Paramount Pictures",
        "production_countries": [{"iso_3166_1": "US", "name": "United States of America"}],
        "production_countries_names": "United States of America"
    },
    {
        "title": "Pulp Fiction",
        "original_title": "Pulp Fiction",
        "overview": "The lives of two mob hitmen, a boxer, a gangster and his wife intertwine in four tales of violence and redemption.",
        "release_date": "1994-10-14",
        "runtime": 154,
        "vote_average": 8.9,
        "vote_count": 673394,
        "popularity": 65.8,
        "budget": 8000000,
        "revenue": 214179088,
        "adult": False,
        "video": False,
        "original_language": "en",
        "status": "Released",
        "tagline": "Just because you are a character doesn't mean you have character.",
        "homepage": "",
        "poster_path": "/d5iIlFn5s0ImszYzBPb8JPIfbXD.jpg",
        "backdrop_path": "/suaEOtk1N1sgg2MTM7oZd2cfVp3.jpg",
        "imdb_id": "tt0110912",
        "genres": [{"id": 53, "name": "Thriller"}, {"id": 80, "name": "Crime"}],
        "genres_names": "Thriller, Crime",
        "origin_country": ["US"],
        "spoken_languages": [{"english_name": "English", "iso_639_1": "en", "name": "English"}],
        "spoken_languages_names": "English",
        "production_companies": [{"id": 14, "name": "Miramax"}],
        "production_companies_names": "Miramax",
        "production_countries": [{"iso_3166_1": "US", "name": "United States of America"}],
        "production_countries_names": "United States of America"
    },
    {
        "title": "Spirited Away",
        "original_title": "千と千尋の神隠し",
        "overview": "A ten-year-old girl who, while moving to a new neighborhood, enters the world of Kami (spirits of Japanese Shinto folklore).",
        "release_date": "2001-07-20",
        "runtime": 125,
        "vote_average": 8.6,
        "vote_count": 14503,
        "popularity": 95.2,
        "budget": 19000000,
        "revenue": 365000000,
        "adult": False,
        "video": False,
        "original_language": "ja",
        "status": "Released",
        "tagline": "The tunnel led Chihiro to a mysterious town...",
        "homepage": "",
        "poster_path": "/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg",
        "backdrop_path": "/Ab8mkHmkYADjU7wQiOkia9BzGvS.jpg",
        "imdb_id": "tt0245429",
        "genres": [{"id": 16, "name": "Animation"}, {"id": 10751, "name": "Family"}],
        "genres_names": "Animation, Family",
        "origin_country": ["JP"],
        "spoken_languages": [{"english_name": "Japanese", "iso_639_1": "ja", "name": "日本語"}],
        "spoken_languages_names": "Japanese",
        "production_companies": [{"id": 10342, "name": "Studio Ghibli"}],
        "production_companies_names": "Studio Ghibli",
        "production_countries": [{"iso_3166_1": "JP", "name": "Japan"}],
        "production_countries_names": "Japan"
    },
    {
        "title": "Inception",
        "original_title": "Inception",
        "overview": "A thief who steals corporate secrets through dream-sharing technology is given the inverse task of planting an idea into the mind of a C.E.O.",
        "release_date": "2010-07-16",
        "runtime": 148,
        "vote_average": 8.8,
        "vote_count": 2223756,
        "popularity": 88.4,
        "budget": 160000000,
        "revenue": 836836967,
        "adult": False,
        "video": False,
        "original_language": "en",
        "status": "Released",
        "tagline": "Your mind is the scene of the crime.",
        "homepage": "",
        "poster_path": "/9gk7adHYeDvHkCSEqAvQNLV5Uge.jpg",
        "backdrop_path": "/s3TBrRGB1iav7gFOCNx3H31MoES.jpg",
        "imdb_id": "tt1375666",
        "genres": [{"id": 28, "name": "Action"}, {"id": 878, "name": "Science Fiction"}],
        "genres_names": "Action, Science Fiction",
        "origin_country": ["US"],
        "spoken_languages": [{"english_name": "English", "iso_639_1": "en", "name": "English"}],
        "spoken_languages_names": "English",
        "production_companies": [{"id": 9996, "name": "Syncopy"}, {"id": 174, "name": "Warner Bros. Pictures"}],
        "production_companies_names": "Syncopy, Warner Bros. Pictures",
        "production_countries": [{"iso_3166_1": "US", "name": "United States of America"}],
        "production_countries_names": "United States of America"
    }
]

def test_create_movies():
    """Test creating movies"""
    print("🎬 Creating movies...")
    created_movies = []
    
    for movie_data in MOCK_MOVIES:
        response = requests.post(f"{BASE_URL}/movies/", json=movie_data)
        if response.status_code == 201:
            movie = response.json()
            created_movies.append(movie)
            print(f"✅ Created: {movie['title']} (ID: {movie['id']})")
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
        if len(created_movies) > 1:
            test_delete_movie(created_movies[-1]['id'])
        
        print("\n" + "=" * 50)
        print("🎉 All tests completed!")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure your server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ An error occurred: {str(e)}")

if __name__ == "__main__":
    main()

