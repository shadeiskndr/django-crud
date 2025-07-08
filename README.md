# Movielogd - Movie Database CRUD API

A comprehensive Django REST API project for managing a movie database with user authentication, personal catalogs, custom movie lists, and full CRUD operations with advanced search and analytics.

## Project Overview

Movielogd is a **movie database CRUD API** with **personal movie tracking and curation features** built with Django and Django REST Framework. The API provides comprehensive movie management capabilities with user authentication, role-based access control, personal movie catalogs, custom movie lists, advanced search, filtering, and statistical features using a **fully normalized PostgreSQL schema**.

## Architecture & Stack

- **Backend**: Django 5.2.3 with Django REST Framework
- **Database**: PostgreSQL 15 (Alpine) with normalized relational schema
- **Authentication**: JWT-based with role-based access control
- **Containerization**: Docker with Docker Compose
- **Python Version**: 3.13.5
- **Data Pipeline**: SQLite ETL for bulk data import

## Key Features

### 1. User Management & Authentication
- **JWT-based authentication** with custom token claims (username, email, role)
- **Email-based login** instead of username for better UX
- **Role-based access control** with four user roles:
  - `USER` - Basic users with catalog features
  - `CRITIC` - Enhanced review capabilities
  - `MODERATOR` - Content moderation permissions
  - `ADMIN` - Full system access and user management
- **User registration** with automatic default role assignment
- **Admin user management** for role updates and user listing

### 2. Personal Movie Catalogs
- **Movie tracking system** with three status types:
  - `BOOKMARKED` - Movies saved for later
  - `WATCHED` - Movies already seen with viewing history
  - `WANT_TO_WATCH` - Personal watchlist/queue
- **Rich personal data**:
  - Personal ratings (0-10 scale)
  - Personal notes and reviews
  - Timestamps for when movies were added/watched
- **Personal statistics and analytics**
- **Quick action endpoints** for common operations (bookmark, mark watched, etc.)

### 3. Custom Movie Lists
- **User-created themed lists** (e.g., "Best Sci-Fi", "Date Night Movies")
- **Privacy controls**: Public lists for sharing, private lists for personal use
- **Ordered list management** with custom sequencing
- **List sharing and discovery** of public lists from other users
- **Comprehensive list statistics** (movie counts, creation dates)

### 4. Movie Reviews & Community Features
- **Full review system** with detailed movie reviews and ratings
- **Review workflow**: Draft → Published → Moderated (Hidden/Featured)
- **Community voting**: Helpful/Not Helpful voting on reviews
- **Review reporting**: Community-driven content moderation
- **Role-based moderation**:
  - `CRITIC` - Enhanced review features and priority
  - `MODERATOR` - Feature reviews, hide inappropriate content, resolve reports
  - `ADMIN` - Full moderation capabilities
- **Advanced features**:
  - Featured reviews showcase
  - Moderation queue for pending content
  - Review search, filtering, and pagination
  - Comprehensive vote and report tracking

### 5. Normalized Database Schema
- **Relational design** with proper foreign keys and many-to-many relationships
- **Lookup tables**: Genres, Languages, Countries, Production Companies, Videos
- **Through tables**: Efficient many-to-many relationships (MovieGenre, MovieVideo, etc.)
- **User isolation**: Personal catalogs and lists are properly scoped to users
- **Optimized queries** with database indexes and Django ORM relationships
- **Data integrity** with foreign key constraints and validation

### 6. Movie Management
- **Public read access** for movie browsing (no authentication required)
- **Admin-only write access** for movie data management
- Rich movie data model with 30+ scalar fields plus related entities:
  - Basic info (title, overview, release date)
  - Ratings (vote_average, vote_count, popularity)
  - Media paths (poster_path, backdrop_path)
  - Production details (companies, countries, languages)
  - Collection and external ID information
  - Related videos, genres, and metadata

## API Endpoints

### Authentication Endpoints
- `POST /api/auth/register/` - User registration
- `POST /api/auth/login/` - JWT token login with role claims
- `POST /api/auth/login/refresh/` - JWT token refresh
- `GET /api/auth/users/` - List all users (admin-only)
- `PATCH /api/auth/users/{id}/role/` - Update user role (admin-only)

### Movie CRUD Operations
- `GET /api/movies/` - List movies with pagination, search, and filtering (public)
- `POST /api/movies/` - Create a new movie with relational data (admin-only)
- `GET /api/movies/{id}/` - Retrieve a specific movie with full relations (public)
- `PUT /api/movies/{id}/` - Update a movie (admin-only)
- `PATCH /api/movies/{id}/` - Partially update a movie (admin-only)
- `DELETE /api/movies/{id}/` - Delete a movie (admin-only)

### Movie Analytics & Lookup
- `GET /api/movies/stats/` - Get database statistics and analytics
- `GET /api/genres/` - List all genres
- `GET /api/companies/` - List production companies with search
- `GET /api/languages/` - List spoken languages
- `GET /api/countries/` - List production countries
- `GET /api/videos/` - List video metadata

### Personal Catalog Management
- `GET /api/catalog/entries/` - User's personal movie catalog
- `POST /api/catalog/entries/` - Add movie to personal catalog
- `GET /api/catalog/entries/bookmarked/` - User's bookmarked movies
- `GET /api/catalog/entries/watched/` - User's watched movies
- `GET /api/catalog/entries/want_to_watch/` - User's watchlist
- `POST /api/catalog/entries/bookmark/` - Quick bookmark action
- `POST /api/catalog/entries/mark_watched/` - Mark as watched with rating
- `POST /api/catalog/entries/add_to_watchlist/` - Add to watchlist
- `DELETE /api/catalog/entries/remove/` - Remove from catalog
- `GET /api/catalog/entries/stats/` - Personal viewing statistics

### Custom Movie Lists
- `GET /api/catalog/lists/` - Browse public lists + user's own lists
- `POST /api/catalog/lists/` - Create new movie list
- `GET /api/catalog/lists/{id}/` - View specific list details
- `PUT /api/catalog/lists/{id}/` - Update list (owner only)
- `DELETE /api/catalog/lists/{id}/` - Delete list (owner only)
- `GET /api/catalog/lists/my_lists/` - User's private lists view
- `POST /api/catalog/lists/{id}/add_movie/` - Add movie to list
- `DELETE /api/catalog/lists/{id}/remove_movie/` - Remove movie from list

### Movie Reviews & Community
- `GET /api/reviews/reviews/` - List published reviews (public)
- `POST /api/reviews/reviews/` - Create new review (authenticated)
- `GET /api/reviews/reviews/{id}/` - View specific review (public)
- `PATCH /api/reviews/reviews/{id}/` - Update review (author only)
- `DELETE /api/reviews/reviews/{id}/` - Delete review (author only)
- `GET /api/reviews/reviews/my_reviews/` - User's own reviews
- `POST /api/reviews/reviews/{id}/publish/` - Publish draft review
- `GET /api/reviews/reviews/featured/` - Featured reviews showcase (public)

### Review Voting & Engagement
- `POST /api/reviews/votes/` - Vote helpful/not helpful on review
- `GET /api/reviews/votes/` - User's voting history
- `POST /api/reviews/reports/` - Report inappropriate review
- `GET /api/reviews/reports/` - User's submitted reports

### Content Moderation (Moderators/Admins)
- `GET /api/reviews/moderation/pending/` - Pending moderation queue
- `POST /api/reviews/moderation/{id}/feature/` - Feature/unfeature review
- `POST /api/reviews/moderation/{id}/hide/` - Hide inappropriate review
- `POST /api/reviews/moderation/{id}/restore/` - Restore hidden review
- `GET /api/reviews/reports/pending/` - Pending reports queue
- `POST /api/reviews/reports/{id}/resolve/` - Resolve report

## Advanced Features

### Search & Filtering
- **Search**: By title, original title, or overview
- **Genre filtering**: Filter by genre names (uses relational lookup)
- **Year filtering**: Filter by release year
- **Rating filtering**: Minimum rating threshold
- **Sorting**: Multiple ordering options (date, rating, popularity, title)
- **Review filtering**: By movie, status, rating, and user
- **Review search**: Full-text search in review content

### Pagination
- 20 items per page (default)
- Configurable page size up to 100 items
- Standard pagination with page numbers

### Statistics & Analytics
- **Movie database stats**: Total count, ratings, runtime averages
- **Personal catalog stats**: Viewing history, personal ratings
- **Review analytics**: Helpful votes, featured count, moderation stats
- **Top 10 genres** with counts (from relational data)
- **User activity tracking** with timestamps

### Security & Permissions
- **Role-based access control** with custom permission classes
- **User isolation**: Personal data scoped to authenticated users
- **Privacy controls**: Public vs. private movie lists
- **Review moderation**: Community reporting and moderator controls
- **Content safety**: Automated duplicate prevention and validation
- **Admin controls**: User management and role assignment
- **JWT token security** with custom claims for role verification

## Data Import Pipeline

### Bulk Data Loading
- **SQLite ETL**: Convert TMDB JSONL dumps to normalized SQLite
- **Automatic import**: Load SQLite data into PostgreSQL on startup
- **Streaming import**: Memory-efficient processing of large datasets
- **Real-time progress**: Live import status with row counts and progress bars

### Import Process
1. **ETL Phase**: `json_to_sqlite_filtered.py` converts JSONL → SQLite
2. **Startup Import**: Docker container automatically loads SQLite → PostgreSQL
3. **Normalization**: Flattens nested JSON into proper relational tables
4. **Validation**: Ensures data integrity during import

## API Data Formats

### User Registration/Login
```json
// Registration
{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "secure-password",
  "first_name": "John",
  "last_name": "Doe"
}

// Login Response
{
  "access": "jwt-token-with-role-claims",
  "refresh": "refresh-token"
}
```

### Personal Catalog Entry
```json
{
  "id": 1,
  "movie": {
    "id": 278,
    "title": "The Shawshank Redemption",
    "genres": [{"tmdb_id": 18, "name": "Drama"}]
  },
  "status": "watched",
  "personal_rating": 9.5,
  "notes": "Amazing cinematography!",
  "watched_at": "2024-01-15T20:30:00Z",
  "added_at": "2024-01-10T14:20:00Z"
}
```

### Custom Movie List
```json
{
  "id": 1,
  "name": "Best Sci-Fi Movies",
  "description": "My favorite science fiction films",
  "is_public": true,
  "owner": "johndoe@example.com",
  "movie_count": 15,
  "movies": [
    {
      "movie": {
        "id": 550,
        "title": "Fight Club",
        "genres": [{"name": "Drama"}]
      },
      "added_at": "2024-01-10T14:20:00Z",
      "order": 1
    }
  ],
  "created_at": "2024-01-01T10:00:00Z"
}
```

### Movie Review
```json
{
  "id": 1,
  "user": {
    "username": "movielover",
    "email": "user@example.com",
    "role": "CRITIC"
  },
  "movie": {
    "id": 278,
    "title": "The Shawshank Redemption",
    "genres": [{"name": "Drama"}]
  },
  "title": "A Masterpiece of Cinema",
  "content": "This film represents the pinnacle of storytelling...",
  "rating": 9.5,
  "status": "PUBLISHED",
  "is_featured": true,
  "helpful_count": 45,
  "not_helpful_count": 2,
  "reported_count": 0,
  "created_at": "2024-01-15T14:30:00Z",
  "published_at": "2024-01-15T15:00:00Z",
  "updated_at": "2024-01-16T10:20:00Z"
}
```

### Review Vote/Report
```json
// Vote
{
  "id": 1,
  "review_id": 123,
  "vote_type": "HELPFUL",
  "created_at": "2024-01-15T16:00:00Z"
}

// Report
{
  "id": 1,
  "review_id": 123,
  "reason": "INAPPROPRIATE",
  "description": "Contains offensive language",
  "resolved": false,
  "created_at": "2024-01-15T16:30:00Z"
}
```

### Movie Create/Update Format
```json
{
  "title": "The Shawshank Redemption",
  "overview": "Two imprisoned men bond...",
  "release_date": "1994-09-23",
  "vote_average": 9.3,
  "runtime": 142,
  
  // Relational data as simple ID arrays
  "genre_ids": [18, 80],
  "spoken_language_codes": ["en"],
  "production_company_ids": [97],
  "production_country_codes": ["US"],
  "video_ids": ["abc123"]
}
```

## Quick Start

### Prerequisites
- Docker
- Docker Compose
- Movie dataset in JSONL format (optional, for bulk import)

### Running the Application

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django-crud
   ```

2. **Prepare environment file**
   ```bash
   # Create .env file with database credentials
   cp .env.example .env
   ```

3. **Prepare movie data (optional)**
   ```bash
   # Convert JSONL to SQLite (if you have movie data)
   python json_to_sqlite_filtered.py movies.jsonl seed/movies.db
   ```

4. **Start the application**
   ```bash
   docker compose up --build
   ```

The application will:
- Wait for PostgreSQL to be ready
- Generate and apply database migrations
- Import movie data from `seed/movies.db` (if present)
- Start the Django development server

### First Steps

1. **Register a user**
   ```bash
   curl -X POST http://localhost:8000/api/auth/register/ \
     -H "Content-Type: application/json" \
     -d '{"username":"johndoe","email":"john@example.com","password":"secure123"}'
   ```

2. **Login and get token**
   ```bash
   curl -X POST http://localhost:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"email":"john@example.com","password":"secure123"}'
   ```

3. **Browse movies (no auth required)**
   ```bash
   curl http://localhost:8000/api/movies/
   ```

4. **Add movie to personal catalog**
   ```bash
   curl -X POST http://localhost:8000/api/catalog/entries/bookmark/ \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"movie_id":278,"notes":"Must watch this classic!"}'
   ```

5. **Create a movie review**
   ```bash
   curl -X POST http://localhost:8000/api/reviews/reviews/ \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"movie_id":278,"title":"Amazing Film","content":"Detailed review...","rating":9.5,"status":"PUBLISHED"}'
   ```

6. **Browse public reviews**
   ```bash
   curl http://localhost:8000/api/reviews/reviews/
   ```

## Database Schema Highlights

### Core Tables
- **users_customuser**: User accounts with roles
- **movies_movie**: Main movie data (scalar fields only)
- **catalog_usermoviewcatalog**: Personal movie tracking
- **catalog_movielist**: Custom user-created movie lists
- **catalog_movielistitem**: Movies in custom lists (with ordering)
- **reviews_review**: Movie reviews with ratings and content
- **reviews_reviewvote**: Community voting on review helpfulness
- **reviews_reviewreport**: Community reporting of inappropriate content

### Lookup Tables
- **movies_genre**: Genre lookup table
- **movies_spokenlanguage**: Language lookup table
- **movies_productioncountry**: Country lookup table
- **movies_productioncompany**: Production company lookup table
- **movies_video**: Video/trailer lookup table

### Relationship Tables
- **movies_moviegenre**: Movie ↔ Genre relationships
- **movies_moviespokenlanguage**: Movie ↔ Language relationships
- **movies_movieproductioncountry**: Movie ↔ Country relationships
- **movies_movieproductioncompany**: Movie ↔ Company relationships
- **movies_movievideo**: Movie ↔ Video relationships

## Development

### Testing

The project includes comprehensive test suites:

```bash
# Test core movie API functionality
python test_api.py

# Test authentication and user management
python test_auth_api.py

# Test catalog and list functionality
python test_catalog_api.py
```

### Database Migrations
```bash
# Generate migrations after model changes
python manage.py makemigrations

# Apply migrations
python manage.py migrate
```

### Manual Data Import
```bash
# Import from SQLite file
python manage.py import_movies_from_sqlite path/to/movies.db

# Force re-import (overwrites existing data)
python manage.py import_movies_from_sqlite path/to/movies.db --force
```

### Admin Interface
Access Django admin at `http://localhost:8000/admin/` to:
- Manage users and roles
- Browse movie data with relational lookups
- View personal catalogs and custom lists
- Moderate reviews and resolve reports
- Manage genres, languages, and production companies

## Performance Notes

- **User isolation**: All catalog queries automatically scoped to authenticated user
- **Database optimization**: Strategic indexes on common query patterns
- **Bulk imports**: Use `bulk_create()` for efficient large-scale inserts
- **Query optimization**: Leverage `select_related()` and `prefetch_related()`
- **Memory efficiency**: Streaming import process for large datasets
- **Batch processing**: 1,000-row batches for optimal throughput
- **Review caching**: Helpful counts and featured status optimized for performance

## Use Cases

### For Movie Enthusiasts
- Track personal viewing history with ratings and notes
- Create themed movie lists (e.g., "Best Horror Films", "Date Night Movies")
- Discover new movies through public lists from other users
- Maintain a personal watchlist and bookmark system
- Write detailed movie reviews and share opinions
- Vote on community reviews to highlight quality content

### For Content Creators
- Curate and share movie recommendations through public lists
- Build following through high-quality movie curation
- Track personal viewing patterns and preferences
- Establish credibility through featured reviews and critic status
- Build reputation through community engagement and helpful reviews

### For Film Critics
- Enhanced review capabilities with critic role privileges
- Priority placement and featuring of quality reviews
- Professional review workflow with draft/publish system
- Community recognition through helpful vote tracking

### For Developers
- Role-based API access for different user types
- Comprehensive movie database with full TMDB-style data
- Ready-to-use authentication and user management
- Extensible catalog system for additional features
- Complete review and moderation system with community features
- Scalable voting and reporting infrastructure

---

**Note**: This project provides a complete movie database platform with user management, personal tracking, community reviews, and social features, built on a fully normalized PostgreSQL schema with efficient ETL pipeline for bulk data import from TMDB-style datasets.