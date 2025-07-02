# Movielogd - Movie Database CRUD API

A Django REST API project for managing a comprehensive movie database with full CRUD operations, search, filtering, and analytics.

## Project Overview

Movielogd is a **movie database CRUD API** built with Django and Django REST Framework, designed to store and manage detailed movie information similar to TMDB (The Movie Database). The API provides comprehensive movie management capabilities with advanced search, filtering, and statistical features using a **fully normalized PostgreSQL schema**.

## Architecture & Stack

- **Backend**: Django 5.2.3 with Django REST Framework
- **Database**: PostgreSQL 15 (Alpine) with normalized relational schema
- **Containerization**: Docker with Docker Compose
- **Python Version**: 3.13.5
- **Data Pipeline**: SQLite ETL for bulk data import

## Key Features

### 1. Normalized Database Schema
- **Relational design** with proper foreign keys and many-to-many relationships
- **Lookup tables**: Genres, Languages, Countries, Production Companies, Videos
- **Through tables**: Efficient many-to-many relationships (MovieGenre, MovieVideo, etc.)
- **Optimized queries** with database indexes and Django ORM relationships
- **Data integrity** with foreign key constraints and validation

### 2. Movie Management
- Full CRUD operations for movies with relational data
- Rich movie data model with 30+ scalar fields plus related entities:
  - Basic info (title, overview, release date)
  - Ratings (vote_average, vote_count, popularity)
  - Media paths (poster_path, backdrop_path)
  - Production details (companies, countries, languages)
  - Collection and external ID information
  - Related videos, genres, and metadata

### 3. API Endpoints

#### Movie CRUD Operations
- `GET /api/movies/` - List movies with pagination, search, and filtering
- `POST /api/movies/` - Create a new movie with relational data
- `GET /api/movies/{id}/` - Retrieve a specific movie with full relations
- `PUT /api/movies/{id}/` - Update a movie (full update)
- `PATCH /api/movies/{id}/` - Partially update a movie
- `DELETE /api/movies/{id}/` - Delete a movie

#### Analytics
- `GET /api/movies/stats/` - Get database statistics and analytics

### 4. Advanced Features

#### Search & Filtering
- **Search**: By title, original title, or overview
- **Genre filtering**: Filter by genre names (uses relational lookup)
- **Year filtering**: Filter by release year
- **Rating filtering**: Minimum rating threshold
- **Sorting**: Multiple ordering options (date, rating, popularity, title)

#### Pagination
- 20 items per page (default)
- Configurable page size up to 100 items
- Standard pagination with page numbers

#### Statistics & Analytics
- Total movie count
- Average, highest, and lowest ratings
- Average runtime
- Latest and earliest release dates
- Top 10 genres with counts (from relational data)

### 5. Data Import Pipeline

#### Bulk Data Loading
- **SQLite ETL**: Convert TMDB JSONL dumps to normalized SQLite
- **Automatic import**: Load SQLite data into PostgreSQL on startup
- **Streaming import**: Memory-efficient processing of large datasets
- **Real-time progress**: Live import status with row counts and progress bars

#### Import Process
1. **ETL Phase**: `json_to_sqlite_filtered.py` converts JSONL → SQLite
2. **Startup Import**: Docker container automatically loads SQLite → PostgreSQL
3. **Normalization**: Flattens nested JSON into proper relational tables
4. **Validation**: Ensures data integrity during import

### 6. API Data Format

#### Create/Update Format (Input)
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

#### Response Format (Output)
```json
{
  "id": 1,
  "title": "The Shawshank Redemption",
  "overview": "Two imprisoned men bond...",
  
  // Nested relational data
  "genres": [
    {"tmdb_id": 18, "name": "Drama"},
    {"tmdb_id": 80, "name": "Crime"}
  ],
  "production_companies": [
    {"tmdb_id": 97, "name": "Castle Rock Entertainment"}
  ]
}
```

### 7. Database Schema Highlights

#### Core Tables
- **movies**: Main movie data (scalar fields only)
- **backend_api_genre**: Genre lookup table
- **backend_api_spokenlanguage**: Language lookup table
- **backend_api_productioncountry**: Country lookup table
- **backend_api_productioncompany**: Production company lookup table
- **backend_api_video**: Video/trailer lookup table

#### Relationship Tables
- **backend_api_moviegenre**: Movie ↔ Genre relationships
- **backend_api_moviespokenlanguage**: Movie ↔ Language relationships
- **backend_api_movieproductioncountry**: Movie ↔ Country relationships
- **backend_api_movieproductioncompany**: Movie ↔ Company relationships
- **backend_api_movievideo**: Movie ↔ Video relationships

#### Database Optimization
- Indexes on key fields (title, release_date, vote_average, popularity)
- Foreign key constraints for data integrity
- Efficient querying with Django select_related/prefetch_related
- Bulk operations for large data imports

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

2. **Prepare movie data (optional)**
   ```bash
   # Convert JSONL to SQLite (if you have movie data)
   python json_to_sqlite_filtered.py movies.jsonl seed/movies.db
   ```

3. **Start the application**
   ```bash
   docker compose up --build
   ```

The application will:
- Wait for PostgreSQL to be ready
- Generate and apply database migrations
- Import movie data from `seed/movies.db` (if present)
- Start the Django development server

### Import Process Logs
```
→ importing lookup tables
Genre                     4,878/4,878    100.0%
SpokenLanguage            137/137        100.0%
ProductionCompany         15,240/15,240  100.0%

→ importing movies
Movie                     100,000/100,000  100.0%

→ linking many-to-many relations
movie_genres              480,000/480,000  100.0%
movie_production_companies 150,000/150,000  100.0%

Import finished.
```

## Data Pipeline

### 1. ETL Process
```bash
# Convert TMDB JSONL dump to normalized SQLite
python json_to_sqlite_filtered.py movies.jsonl movies.db
```

### 2. Automatic Import
The Docker container automatically imports SQLite data on startup:
```bash
python manage.py import_movies_from_sqlite seed/movies.db
```

### 3. Data Flow
```
JSONL → SQLite (normalized) → PostgreSQL (Django ORM)
```

## Development

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
- Browse movie data with relational lookups
- Manage genres, languages, and production companies
- View through-table relationships inline

## Performance Notes

- **Bulk imports**: Use `bulk_create()` for efficient large-scale inserts
- **Query optimization**: Leverage `select_related()` and `prefetch_related()`
- **Indexing**: Database indexes on frequently queried fields
- **Memory efficiency**: Streaming import process for large datasets
- **Batch processing**: 1,000-row batches for optimal throughput

## API Testing

Use the included `test_api.py` script to test all endpoints:

```bash
python test_api.py
```

The test script demonstrates:
- Creating movies with relational data
- Search and filtering capabilities
- CRUD operations
- Statistics endpoints

---

**Note**: This project uses a fully normalized PostgreSQL schema for optimal query performance and data integrity, with an efficient ETL pipeline for bulk data import from TMDB-style datasets.