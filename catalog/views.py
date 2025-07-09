from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Count, Avg, Q
from .models import UserMovieCatalog, UserMovieCollection, UserMovieCollectionItem
from .serializers import (
    UserMovieCatalogSerializer, 
    CatalogActionSerializer,
    UserMovieCollectionSerializer,
    UserMovieCollectionCreateSerializer,
    AddToCollectionSerializer
)
from .permissions import IsOwnerOrReadOnly, IsOwnerOrPublicReadOnly
from .docs import CATALOG_ENTRIES_SCHEMA, MOVIE_COLLECTIONS_SCHEMA
from rest_framework.pagination import PageNumberPagination

class CatalogPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100

@CATALOG_ENTRIES_SCHEMA
class UserMovieCatalogViewSet(viewsets.ModelViewSet):
    serializer_class = UserMovieCatalogSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]
    pagination_class = CatalogPagination
    
    def get_queryset(self):
        if not hasattr(self, 'request') or not self.request.user.is_authenticated:
            return UserMovieCatalog.objects.none()            
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
        """Add a movie to want-to-watch"""
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

@MOVIE_COLLECTIONS_SCHEMA
class UserMovieCollectionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsOwnerOrPublicReadOnly]
    pagination_class = CatalogPagination
    
    def get_queryset(self):
        if not hasattr(self, 'request') or not self.request.user.is_authenticated:
            return UserMovieCollection.objects.none()
        if self.action == 'my_collections':  # This should match the action name
            # Show only user's own collections
            return UserMovieCollection.objects.filter(
                user=self.request.user
            ).select_related('user').prefetch_related('movies').annotate(
                movie_count=Count('movies')
            ).order_by('-updated_at')
        elif self.action == 'list':
            # For list view, show user's own collections + public collections from others
            return UserMovieCollection.objects.filter(
                Q(user=self.request.user) | Q(is_public=True)
            ).select_related('user').prefetch_related('movies').annotate(
                movie_count=Count('movies')
            ).order_by('-updated_at')
        else:
            # For detail views, show all collections (permissions will be checked)
            return UserMovieCollection.objects.select_related('user').prefetch_related('movies')
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return UserMovieCollectionCreateSerializer
        return UserMovieCollectionSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_collections(self, request):
        """Get only the current user's collections"""
        queryset = UserMovieCollection.objects.filter(user=request.user).annotate(
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
        """Add a movie to this collection"""
        movie_collection = self.get_object()
        serializer = AddToCollectionSerializer(data=request.data)
        
        if serializer.is_valid():
            movie_id = serializer.validated_data['movie_id']
            
            # Check if movie is already in the collection
            if UserMovieCollectionItem.objects.filter(movie_collection=movie_collection, movie_id=movie_id).exists():
                return Response(
                    {'error': 'Movie is already in this collection'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Add movie to collection
            UserMovieCollectionItem.objects.create(
                movie_collection=movie_collection,
                movie_id=movie_id,
                order=movie_collection.usermoviecollectionitem_set.count()
            )
            
            # Update the collection's updated_at timestamp
            movie_collection.save(update_fields=['updated_at'])
            
            return Response({'message': 'Movie added to collection'}, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['delete'])
    def remove_movie(self, request, pk=None):
        """Remove a movie from this collection"""
        movie_collection = self.get_object()
        movie_id = request.data.get('movie_id')
        
        if not movie_id:
            return Response(
                {'error': 'movie_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        deleted_count, _ = UserMovieCollectionItem.objects.filter(
            movie_collection=movie_collection,
            movie_id=movie_id
        ).delete()
        
        if deleted_count > 0:
            # Update the collection's updated_at timestamp
            movie_collection.save(update_fields=['updated_at'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response(
                {'error': 'Movie not found in this collection'}, 
                status=status.HTTP_404_NOT_FOUND
            )

