from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Avg, Q
from .models import UserMovieCatalog, MovieList, MovieListItem
from .serializers import (
    UserMovieCatalogSerializer, 
    CatalogActionSerializer,
    MovieListSerializer,
    MovieListCreateSerializer,
    AddToListSerializer
)
from .permissions import IsOwnerOrReadOnly, IsOwnerOrPublicReadOnly
from rest_framework.pagination import PageNumberPagination

class CatalogPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

class UserMovieCatalogViewSet(viewsets.ModelViewSet):
    serializer_class = UserMovieCatalogSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = CatalogPagination
    
    def get_queryset(self):
        return UserMovieCatalog.objects.filter(
            user=self.request.user
        ).select_related('movie').order_by('-added_at')
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def bookmarked(self, request):
        """Get user's bookmarked movies"""
        queryset = self.get_queryset().filter(status=UserMovieCatalog.Status.BOOKMARKED)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def watched(self, request):
        """Get user's watched movies"""
        queryset = self.get_queryset().filter(status=UserMovieCatalog.Status.WATCHED)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def want_to_watch(self, request):
        """Get user's want-to-watch movies"""
        queryset = self.get_queryset().filter(status=UserMovieCatalog.Status.WANT_TO_WATCH)
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'])
    def bookmark(self, request):
        """Quick bookmark a movie"""
        serializer = CatalogActionSerializer(data=request.data)
        if serializer.is_valid():
            movie_id = serializer.validated_data['movie_id']
            notes = serializer.validated_data.get('notes', '')
            
            catalog_entry, created = UserMovieCatalog.objects.update_or_create(
                user=request.user,
                movie_id=movie_id,
                status=UserMovieCatalog.Status.BOOKMARKED,
                defaults={'notes': notes}
            )
            
            response_serializer = UserMovieCatalogSerializer(catalog_entry)
            return Response(
                response_serializer.data, 
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def mark_watched(self, request):
        """Mark a movie as watched"""
        serializer = CatalogActionSerializer(data=request.data)
        if serializer.is_valid():
            movie_id = serializer.validated_data['movie_id']
            notes = serializer.validated_data.get('notes', '')
            personal_rating = serializer.validated_data.get('personal_rating')
            
            catalog_entry, created = UserMovieCatalog.objects.update_or_create(
                user=request.user,
                movie_id=movie_id,
                status=UserMovieCatalog.Status.WATCHED,
                defaults={
                    'notes': notes,
                    'personal_rating': personal_rating,
                    'watched_at': timezone.now()
                }
            )
            
            response_serializer = UserMovieCatalogSerializer(catalog_entry)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'])
    def add_to_watchlist(self, request):
        """Add a movie to want-to-watch list"""
        serializer = CatalogActionSerializer(data=request.data)
        if serializer.is_valid():
            movie_id = serializer.validated_data['movie_id']
            notes = serializer.validated_data.get('notes', '')
            
            catalog_entry, created = UserMovieCatalog.objects.update_or_create(
                user=request.user,
                movie_id=movie_id,
                status=UserMovieCatalog.Status.WANT_TO_WATCH,
                defaults={'notes': notes}
            )
            
            response_serializer = UserMovieCatalogSerializer(catalog_entry)
            return Response(
                response_serializer.data,
                status=status.HTTP_201_CREATED if created else status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['delete'])
    def remove(self, request):
        """Remove a movie from catalog"""
        movie_id = request.data.get('movie_id')
        if not movie_id:
            return Response(
                {'error': 'movie_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count, _ = UserMovieCatalog.objects.filter(
            user=request.user,
            movie_id=movie_id
        ).delete()
        
        if deleted_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'error': 'Movie not found in catalog'}, 
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user's catalog statistics"""
        queryset = self.get_queryset()
        
        stats = {
            'total_movies': queryset.count(),
            'bookmarked': queryset.filter(status=UserMovieCatalog.Status.BOOKMARKED).count(),
            'watched': queryset.filter(status=UserMovieCatalog.Status.WATCHED).count(),
            'want_to_watch': queryset.filter(status=UserMovieCatalog.Status.WANT_TO_WATCH).count(),
        }
        
        # Calculate rating statistics for watched movies
        watched_with_ratings = queryset.filter(
            status=UserMovieCatalog.Status.WATCHED,
            personal_rating__isnull=False
        )
        
        if watched_with_ratings.exists():
            rating_stats = watched_with_ratings.aggregate(
                avg_personal_rating=Avg('personal_rating'),
                total_rated=Count('personal_rating')
            )
            stats.update(rating_stats)
        else:
            stats.update({
                'avg_personal_rating': None,
                'total_rated': 0
            })
        
        return Response(stats)


class MovieListViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrPublicReadOnly]
    pagination_class = CatalogPagination
    
    def get_queryset(self):
        if self.action == 'list':
            # Show user's own lists + public lists from others
            return MovieList.objects.filter(
                Q(user=self.request.user) | Q(is_public=True)
            ).select_related('user').prefetch_related('movies').annotate(
                movie_count=Count('movies')
            ).order_by('-updated_at')
        else:
            # For detail views, show all lists (permissions will be checked)
            return MovieList.objects.select_related('user').prefetch_related('movies')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return MovieListCreateSerializer
        return MovieListSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_lists(self, request):
        """Get only the current user's lists"""
        queryset = MovieList.objects.filter(user=request.user).annotate(
            movie_count=Count('movies')
        ).order_by('-updated_at')
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_movie(self, request, pk=None):
        """Add a movie to this list"""
        movie_list = self.get_object()
        serializer = AddToListSerializer(data=request.data)
        
        if serializer.is_valid():
            movie_id = serializer.validated_data['movie_id']
            
            # Check if movie is already in the list
            if MovieListItem.objects.filter(movie_list=movie_list, movie_id=movie_id).exists():
                return Response(
                    {'error': 'Movie is already in this list'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add movie to list
            MovieListItem.objects.create(
                movie_list=movie_list,
                movie_id=movie_id,
                order=movie_list.movielistitem_set.count()
            )
            
            # Update the list's updated_at timestamp
            movie_list.save(update_fields=['updated_at'])
            
            return Response({'message': 'Movie added to list'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def remove_movie(self, request, pk=None):
        """Remove a movie from this list"""
        movie_list = self.get_object()
        movie_id = request.data.get('movie_id')
        
        if not movie_id:
            return Response(
                {'error': 'movie_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count, _ = MovieListItem.objects.filter(
            movie_list=movie_list,
            movie_id=movie_id
        ).delete()
        
        if deleted_count > 0:
            # Update the list's updated_at timestamp
            movie_list.save(update_fields=['updated_at'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'error': 'Movie not found in this list'}, 
                status=status.HTTP_404_NOT_FOUND
            )

