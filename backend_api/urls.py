from django.urls import path
from .views import (
    MovieListCreateAPIView,
    MovieDetailAPIView,
    MovieStatsAPIView,
    GenreListAPIView,
    ProductionCompanyListAPIView,
    SpokenLanguageListAPIView,
    OriginCountryListAPIView,
    ProductionCountryListAPIView,
    VideoListAPIView,
)

app_name = "backend_api"

urlpatterns = [
    # Movie CRUD and Stats
    path("movies/", MovieListCreateAPIView.as_view(), name="movie-list-create"),
    path("movies/<int:pk>/", MovieDetailAPIView.as_view(), name="movie-detail"),
    path("movies/stats/", MovieStatsAPIView.as_view(), name="movie-stats"),

    # Lookup Endpoints for Frontend Forms
    path("genres/", GenreListAPIView.as_view(), name="genre-list"),
    path("companies/", ProductionCompanyListAPIView.as_view(), name="company-list"),
    path("languages/", SpokenLanguageListAPIView.as_view(), name="language-list"),
    path("countriesISO/", OriginCountryListAPIView.as_view(), name="country-list-iso"),
    path("countries/", ProductionCountryListAPIView.as_view(), name="country-list"),
    path("videos/", VideoListAPIView.as_view(), name="video-list"),
]
