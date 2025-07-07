from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserMovieCatalogViewSet, MovieListViewSet

app_name = "catalog"

router = DefaultRouter()
router.register(r'entries', UserMovieCatalogViewSet, basename='catalog-entries')
router.register(r'lists', MovieListViewSet, basename='movie-lists')

urlpatterns = [
    path('', include(router.urls)),
]
