from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.shortcuts import get_object_or_404
from django.db.models import Q
from .models import Movie
from .serializers import MovieSerializer, MovieListSerializer, MovieCreateUpdateSerializer

class MoviePagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class MovieListCreateAPIView(APIView):
    """
    GET: List all movies with pagination and search
    POST: Create a new movie
    """
    
    def get(self, request):
        # Get query parameters
        search = request.query_params.get('search', '')
        genre = request.query_params.get('genre', '')
        year = request.query_params.get('year', '')
        min_rating = request.query_params.get('min_rating', '')
        ordering = request.query_params.get('ordering', '-created_at')
        
        # Start with all movies
        queryset = Movie.objects.all()
        
        # Apply filters
        if search:
            queryset = queryset.filter(
                Q(title__icontains=search) | 
                Q(original_title__icontains=search) |
                Q(overview__icontains=search)
            )
        
        if genre:
            queryset = queryset.filter(genres_names__icontains=genre)
            
        if year:
            try:
                queryset = queryset.filter(release_date__year=int(year))
            except ValueError:
                pass
                
        if min_rating:
            try:
                queryset = queryset.filter(vote_average__gte=float(min_rating))
            except ValueError:
                pass
        
        # Apply ordering
        valid_orderings = [
            'title', '-title', 'release_date', '-release_date',
            'vote_average', '-vote_average', 'popularity', '-popularity',
            'created_at', '-created_at'
        ]
        if ordering in valid_orderings:
            queryset = queryset.order_by(ordering)
        
        # Paginate results
        paginator = MoviePagination()
        paginated_queryset = paginator.paginate_queryset(queryset, request)
        
        # Serialize data
        serializer = MovieListSerializer(paginated_queryset, many=True)
        
        return paginator.get_paginated_response(serializer.data)
    
    def post(self, request):
        serializer = MovieCreateUpdateSerializer(data=request.data)
        if serializer.is_valid():
            movie = serializer.save()
            response_serializer = MovieSerializer(movie)
            return Response(
                response_serializer.data, 
                status=status.HTTP_201_CREATED
            )
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )

class MovieDetailAPIView(APIView):
    """
    GET: Retrieve a specific movie
    PUT: Update a specific movie (full update)
    PATCH: Partially update a specific movie
    DELETE: Delete a specific movie
    """
    
    def get_object(self, pk):
        return get_object_or_404(Movie, pk=pk)
    
    def get(self, request, pk):
        movie = self.get_object(pk)
        serializer = MovieSerializer(movie)
        return Response(serializer.data)
    
    def put(self, request, pk):
        movie = self.get_object(pk)
        serializer = MovieCreateUpdateSerializer(movie, data=request.data)
        if serializer.is_valid():
            updated_movie = serializer.save()
            response_serializer = MovieSerializer(updated_movie)
            return Response(response_serializer.data)
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def patch(self, request, pk):
        movie = self.get_object(pk)
        serializer = MovieCreateUpdateSerializer(
            movie, 
            data=request.data, 
            partial=True
        )
        if serializer.is_valid():
            updated_movie = serializer.save()
            response_serializer = MovieSerializer(updated_movie)
            return Response(response_serializer.data)
        return Response(
            serializer.errors, 
            status=status.HTTP_400_BAD_REQUEST
        )
    
    def delete(self, request, pk):
        movie = self.get_object(pk)
        movie.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

class MovieStatsAPIView(APIView):
    """
    GET: Get statistics about movies in the database
    """
    
    def get(self, request):
        from django.db.models import Count, Avg, Max, Min
        
        stats = Movie.objects.aggregate(
            total_movies=Count('id'),
            avg_rating=Avg('vote_average'),
            highest_rating=Max('vote_average'),
            lowest_rating=Min('vote_average'),
            avg_runtime=Avg('runtime'),
            latest_release=Max('release_date'),
            earliest_release=Min('release_date')
        )
        
        # Get top genres
        movies_with_genres = Movie.objects.exclude(genres_names='')
        genre_counts = {}
        for movie in movies_with_genres:
            if movie.genres_names:
                genres = [g.strip() for g in movie.genres_names.split(',')]
                for genre in genres:
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        top_genres = sorted(genre_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        
        stats['top_genres'] = [{'genre': genre, 'count': count} for genre, count in top_genres]
        
        return Response(stats)
