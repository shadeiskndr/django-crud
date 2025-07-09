from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserMovieCatalogViewSet, UserMovieCollectionViewSet

app_name = "catalog"

router = DefaultRouter()
router.register(r'entries', UserMovieCatalogViewSet, basename='catalog-entries')
router.register(r'collections', UserMovieCollectionViewSet, basename='movie-collections')

urlpatterns = [
    path('', include(router.urls)),
]
