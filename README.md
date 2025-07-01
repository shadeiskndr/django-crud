# Movielogd - Movie Database CRUD API

A Django REST API project for managing a comprehensive movie database with full CRUD operations, search, filtering, and analytics.

## Project Overview

Movielogd is a **movie database CRUD API** built with Django and Django REST Framework, designed to store and manage detailed movie information similar to TMDB (The Movie Database). The API provides comprehensive movie management capabilities with advanced search, filtering, and statistical features.

## Architecture & Stack

- **Backend**: Django 5.2.3 with Django REST Framework
- **Database**: PostgreSQL 15 (Alpine)
- **Containerization**: Docker with Docker Compose
- **Python Version**: 3.13.5

## Key Features

### 1. Movie Management
- Full CRUD operations for movies
- Rich movie data model with 30+ fields including:
  - Basic info (title, overview, release date)
  - Ratings (vote_average, vote_count, popularity)
  - Media paths (poster_path, backdrop_path)
  - Production details (companies, countries, languages)
  - Collection and external ID information
  - JSON fields for complex data (genres, videos, etc.)

### 2. API Endpoints

#### Movie CRUD Operations
- `GET /api/movies/` - List movies with pagination, search, and filtering
- `POST /api/movies/` - Create a new movie
- `GET /api/movies/{id}/` - Retrieve a specific movie
- `PUT /api/movies/{id}/` - Update a movie (full update)
- `PATCH /api/movies/{id}/` - Partially update a movie
- `DELETE /api/movies/{id}/` - Delete a movie

#### Analytics
- `GET /api/movies/stats/` - Get database statistics and analytics

### 3. Advanced Features

#### Search & Filtering
- **Search**: By title, original title, or overview
- **Genre filtering**: Filter by genre names
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
- Top 10 genres with counts

### 4. Data Model Highlights

The Movie model includes comprehensive fields for storing detailed movie information:

- **Basic Information**: title, original_title, overview, tagline
- **Release Information**: release_date, status, original_language
- **Ratings & Popularity**: vote_average, vote_count, popularity
- **Financial Data**: budget, revenue
- **Media Assets**: poster_path, backdrop_path, homepage
- **Production Details**: production_companies, production_countries, spoken_languages
- **Collection Data**: Flattened collection information
- **External IDs**: IMDB, Twitter, Facebook, Wikidata, Instagram
- **Technical Details**: runtime, adult content flag, video flag
- **JSON Fields**: Complex data structures for genres, videos, etc.

#### Database Optimization
- Indexes on key fields (title, release_date, vote_average, popularity)
- Validation for ratings (0-10 scale) and runtime
- Efficient querying with Django Q objects

## Quick Start

### Prerequisites
- Docker
- Docker Compose

### Running the Application

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd django-crud
   ```

2. **Start the application**
   ```bash
   docker compose up --build
   ```

