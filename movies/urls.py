from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    MovieViewSet,
    MovieStatsAPIView,
    GenreListAPIView,
    ProductionCompanyListAPIView,
    SpokenLanguageListAPIView,
    OriginCountryListAPIView,
    ProductionCountryListAPIView,
    VideoListAPIView,
)

app_name = "backend_api"

router = DefaultRouter()
router.register(r'movies', MovieViewSet, basename='movie')

urlpatterns = [
    # Router-generated movie URLs (list, create, retrieve, update, delete)
    path("", include(router.urls)),

    # Other specific endpoints
    path("movies/stats/", MovieStatsAPIView.as_view(), name="movie-stats"),
    path("genres/", GenreListAPIView.as_view(), name="genre-list"),
    path("companies/", ProductionCompanyListAPIView.as_view(), name="company-list"),
    path("languages/", SpokenLanguageListAPIView.as_view(), name="language-list"),
    path("countriesISO/", OriginCountryListAPIView.as_view(), name="country-list-iso"),
    path("countries/", ProductionCountryListAPIView.as_view(), name="country-list"),
    path("videos/", VideoListAPIView.as_view(), name="video-list"),
]
