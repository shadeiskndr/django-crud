from django.urls import path
from .views import (
    MovieListCreateAPIView,
    MovieDetailAPIView,
    MovieStatsAPIView
)

app_name = 'backend_api'

urlpatterns = [
    # Movie CRUD endpoints
    path('movies/', MovieListCreateAPIView.as_view(), name='movie-list-create'),
    path('movies/<int:pk>/', MovieDetailAPIView.as_view(), name='movie-detail'),
    
    # Additional endpoints
    path('movies/stats/', MovieStatsAPIView.as_view(), name='movie-stats'),
]
