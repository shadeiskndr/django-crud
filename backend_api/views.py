from django.db.models import Q, Count, Avg, Max, Min
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination

from .models import Movie, Genre
from .serializers import (
    MovieSerializer,
    MovieListSerializer,
    MovieCreateUpdateSerializer,
)


# ───────────────────  Pagination  ───────────────────
class MoviePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


# ───────────────────  List / Create  ───────────────────
class MovieListCreateAPIView(APIView):
    """
    GET – list movies with search / filter / ordering
    POST – create a movie (see serializer for payload)
    """

    def get(self, request):
        search = request.query_params.get("search", "")
        genre = request.query_params.get("genre", "")
        year = request.query_params.get("year", "")
        min_rating = request.query_params.get("min_rating", "")
        ordering = request.query_params.get("ordering", "-created_at")

        queryset = Movie.objects.all()

        # Search
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search)
                | Q(original_title__icontains=search)
                | Q(overview__icontains=search)
            )

        # Filter by genre name (related)
        if genre:
            queryset = queryset.filter(genres__name__icontains=genre)

        # Release year
        if year and year.isdigit():
            queryset = queryset.filter(release_date__year=int(year))

        # Min rating
        if min_rating:
            try:
                queryset = queryset.filter(vote_average__gte=float(min_rating))
            except ValueError:
                pass

        # Ordering
        valid_orderings = [
            "title",
            "-title",
            "release_date",
            "-release_date",
            "vote_average",
            "-vote_average",
            "popularity",
            "-popularity",
            "created_at",
            "-created_at",
        ]
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)

        # Pagination
        paginator = MoviePagination()
        page = paginator.paginate_queryset(queryset, request)
        serializer = MovieListSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)

    def post(self, request):
        serializer = MovieCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            movie = serializer.save()
            return Response(MovieSerializer(movie).data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# ───────────────────  Detail / Update / Delete  ───────────────────
class MovieDetailAPIView(APIView):
    """
    CRUD actions on a single movie
    """

    def get_object(self, pk):
        return get_object_or_404(Movie, pk=pk)

    def get(self, request, pk):
        serializer = MovieSerializer(self.get_object(pk))
        return Response(serializer.data)

    def put(self, request, pk):
        movie = self.get_object(pk)
        serializer = MovieCreateUpdateSerializer(movie, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(MovieSerializer(movie).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk):
        movie = self.get_object(pk)
        serializer = MovieCreateUpdateSerializer(
            movie, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(MovieSerializer(movie).data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        self.get_object(pk).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


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
