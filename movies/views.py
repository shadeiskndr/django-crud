from django.db.models import Q, Count, Avg, Max, Min
from django.shortcuts import get_object_or_404
from rest_framework import status, filters, viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from rest_framework.generics import ListAPIView

from .models import (
    Movie,
    Genre,
    ProductionCompany,
    SpokenLanguage,
    OriginCountry,
    ProductionCountry,
    Video
)
from .serializers import (
    MovieSerializer,
    MovieListSerializer,
    MovieCreateUpdateSerializer,
    GenreSerializer,
    ProductionCompanySerializer,
    SpokenLanguageSerializer,
    OriginCountrySerializer,
    ProductionCountrySerializer,
    VideoSerializer,
)

from .permissions import IsAdminOrReadOnly

# ───────────────────  Pagination  ───────────────────
class MoviePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


# ───────────────────  MovieViewSet  ───────────────────
class MovieViewSet(viewsets.ModelViewSet):
    """
    A unified ViewSet for viewing and editing movies.
    - GET (list, retrieve): Open to all users.
    - POST, PUT, PATCH, DELETE: Restricted to Admin users.
    """
    queryset = Movie.objects.all().order_by("-created_at")
    pagination_class = MoviePagination
    permission_classes = [IsAdminOrReadOnly] # <-- Apply our new permission class

    def get_serializer_class(self):
        """Return appropriate serializer class based on the action."""
        if self.action == 'list':
            return MovieListSerializer
        if self.action in ['create', 'update', 'partial_update']:
            return MovieCreateUpdateSerializer
        # For 'retrieve' action
        return MovieSerializer

    def list(self, request, *args, **kwargs):
        """
        Custom list action to include search and filter functionality.
        """
        search = request.query_params.get("search", "")
        genre = request.query_params.get("genre", "")
        year = request.query_params.get("year", "")
        min_rating = request.query_params.get("min_rating", "")
        ordering = request.query_params.get("ordering", "-created_at")

        queryset = self.get_queryset()

        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) |
                Q(original_title__icontains=search) |
                Q(overview__icontains=search)
            )
        if genre:
            queryset = queryset.filter(genres__name__icontains=genre)
        if year and year.isdigit():
            queryset = queryset.filter(release_date__year=int(year))
        if min_rating:
            try:
                queryset = queryset.filter(vote_average__gte=float(min_rating))
            except ValueError:
                pass

        valid_orderings = [
            "title", "-title", "release_date", "-release_date",
            "vote_average", "-vote_average", "popularity", "-popularity",
            "created_at", "-created_at",
        ]
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


# ───────────────────  Statistics  ───────────────────
class MovieStatsAPIView(APIView):
    """
    Aggregated statistics over the movie catalogue.
    """

    def get(self, request):
        stats = Movie.objects.aggregate(
            total_movies=Count("id"),
            avg_rating=Avg("vote_average"),
            highest_rating=Max("vote_average"),
            lowest_rating=Min("vote_average"),
            avg_runtime=Avg("runtime"),
            latest_release=Max("release_date"),
            earliest_release=Min("release_date"),
        )

        # Top 10 genres
        top_genres_qs = (
            Genre.objects.annotate(count=Count("movies"))
            .order_by("-count")[:10]
        )
        stats["top_genres"] = [
            {"genre": g.name, "count": g.count} for g in top_genres_qs
        ]

        return Response(stats)
    
# ───────────────────  Lookup / Reference Endpoints  ───────────────────

class GenreListAPIView(ListAPIView):
    """
    GET – list all genres.
    """
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    pagination_class = MoviePagination  # Use None for disabling pagination


class ProductionCompanyListAPIView(ListAPIView):
    """
    GET – list all production companies.
    Supports search by name, e.g., /api/companies/?search=Warner
    """
    queryset = ProductionCompany.objects.all()
    serializer_class = ProductionCompanySerializer
    # Add search capability for the 'name' field
    filter_backends = [filters.SearchFilter]
    search_fields = ['name']
    pagination_class = MoviePagination # Use None for disabling pagination


class SpokenLanguageListAPIView(ListAPIView):
    """
    GET – list all spoken languages.
    """
    queryset = SpokenLanguage.objects.all()
    serializer_class = SpokenLanguageSerializer
    pagination_class = MoviePagination # Use None for disabling pagination

class OriginCountryListAPIView(ListAPIView):
    """
    GET – list all origin countries ISO.
    """
    queryset = OriginCountry.objects.all()
    serializer_class = OriginCountrySerializer
    pagination_class = MoviePagination # Use None for disabling pagination


class ProductionCountryListAPIView(ListAPIView):
    """
    GET – list all production countries.
    """
    queryset = ProductionCountry.objects.all()
    serializer_class = ProductionCountrySerializer
    pagination_class = MoviePagination # Use None for disabling pagination


class VideoListAPIView(ListAPIView):
    """
    GET – list all videos.
    """
    queryset = Video.objects.all()
    serializer_class = VideoSerializer
    pagination_class = MoviePagination # Use None for disabling pagination

