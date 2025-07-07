from django.db.models import Q, Count, Avg
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.pagination import PageNumberPagination
from .models import Review, ReviewVote, ReviewReport
from .serializers import (
    ReviewSerializer,
    ReviewCreateUpdateSerializer,
    ReviewListSerializer,
    ReviewVoteSerializer,
    ReviewReportSerializer,
    ModerationSerializer,
    ReportResolutionSerializer
)
from .permissions import (
    IsAuthorOrReadOnly,
    CanModerateReviews,
    CanPublishReviews,
    CanFeatureReviews,
    IsOwnerOrModerator
)
from users.models import CustomUser


class ReviewPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = "page_size"
    max_page_size = 100


class ReviewViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing movie reviews.
    - Public read access for published reviews
    - Authenticated users can create reviews
    - Authors can edit their own reviews
    """
    permission_classes = [IsAuthorOrReadOnly]
    pagination_class = ReviewPagination

    def get_permissions(self):
        """
        Instantiate and return the list of permissions for this view.
        """
        if self.action in ['list', 'retrieve', 'featured']:
            # Public read access for list and retrieve
            permission_classes = []
        elif self.action in ['create']:
            # Authenticated users can create
            permission_classes = [IsAuthenticated]
        else:
            # Other actions need authentication and ownership
            permission_classes = [IsAuthenticated, IsAuthorOrReadOnly]
        
        return [permission() for permission in permission_classes]
    
    def get_queryset(self):
        queryset = Review.objects.select_related('user', 'movie').exclude(status=Review.Status.DELETED)
        
        # Filter by movie
        movie_id = self.request.query_params.get('movie_id')
        if movie_id:
            queryset = queryset.filter(movie_id=movie_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # For list view, only show published reviews unless it's user's own
        if self.action == 'list':
            if self.request.user.is_authenticated:
                queryset = queryset.filter(
                    Q(status=Review.Status.PUBLISHED) | Q(user=self.request.user)
                )
            else:
                queryset = queryset.filter(status=Review.Status.PUBLISHED)
        
        # Ordering
        ordering = self.request.query_params.get('ordering', '-published_at')
        if ordering == 'helpful':
            queryset = queryset.order_by('-helpful_count', '-published_at')
        elif ordering == 'rating':
            queryset = queryset.order_by('-rating', '-published_at')
        else:
            queryset = queryset.order_by('-published_at', '-created_at')
        
        return queryset
    
    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ReviewCreateUpdateSerializer
        elif self.action == 'list':
            return ReviewListSerializer
        return ReviewSerializer
    
    def create(self, request, *args, **kwargs):
        """Override create to return full review data after creation"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Perform the creation
        review = self.perform_create(serializer)
        
        # Return the full review data using the detailed serializer
        response_serializer = ReviewSerializer(review, context={'request': request})
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    def perform_create(self, serializer):
        return serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'])
    def my_reviews(self, request):
        """Get current user's reviews (all statuses)"""
        reviews = self.get_queryset().filter(user=request.user)
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish a draft review"""
        review = self.get_object()
        
        if review.user != request.user:
            return Response(
                {'error': 'You can only publish your own reviews.'}, 
                status=status.HTTP_403_FORBIDDEN
            )
        
        if review.status != Review.Status.DRAFT:
            return Response(
                {'error': 'Only draft reviews can be published.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        review.status = Review.Status.PUBLISHED
        review.published_at = timezone.now()
        review.save()
        
        serializer = ReviewSerializer(review, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def featured(self, request):
        """Get featured reviews"""
        reviews = self.get_queryset().filter(
            status=Review.Status.PUBLISHED,
            is_featured=True
        )
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)


class ReviewModerationViewSet(viewsets.ModelViewSet):
    """ViewSet for review moderation (moderators/admins only)"""
    serializer_class = ModerationSerializer
    permission_classes = [IsAuthenticated, CanModerateReviews]
    pagination_class = ReviewPagination
    
    def get_queryset(self):
        return Review.objects.select_related('user', 'movie').exclude(status=Review.Status.DELETED)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get reviews pending moderation"""
        reviews = self.get_queryset().filter(
            Q(reported_count__gt=0) | Q(status=Review.Status.PUBLISHED)
        ).order_by('-reported_count', '-created_at')
        
        page = self.paginate_queryset(reviews)
        if page is not None:
            serializer = ReviewSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewSerializer(reviews, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanFeatureReviews])
    def feature(self, request, pk=None):
        """Feature/unfeature a review"""
        review = self.get_object()
        is_featured = request.data.get('is_featured', True)
        
        review.is_featured = is_featured
        review.moderated_by = request.user
        review.save()
        
        serializer = ReviewSerializer(review, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def hide(self, request, pk=None):
        """Hide a review"""
        review = self.get_object()
        moderation_notes = request.data.get('moderation_notes', '')
        
        review.status = Review.Status.HIDDEN
        review.moderated_by = request.user
        review.moderation_notes = moderation_notes
        review.save()
        
        serializer = ReviewSerializer(review, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        """Restore a hidden review"""
        review = self.get_object()
        
        if review.status == Review.Status.HIDDEN:
            review.status = Review.Status.PUBLISHED
            review.moderated_by = request.user
            review.save()
        
        serializer = ReviewSerializer(review, context={'request': request})
        return Response(serializer.data)


class ReviewVoteViewSet(viewsets.ModelViewSet):
    """ViewSet for voting on reviews"""
    serializer_class = ReviewVoteSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrModerator]
    pagination_class = ReviewPagination
    
    def get_queryset(self):
        return ReviewVote.objects.select_related('user', 'review').filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class ReviewReportViewSet(viewsets.ModelViewSet):
    """ViewSet for reporting reviews"""
    serializer_class = ReviewReportSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = ReviewPagination
    
    def get_queryset(self):
        if self.request.user.role in [CustomUser.Role.MODERATOR, CustomUser.Role.ADMIN]:
            # Moderators can see all reports
            return ReviewReport.objects.select_related('user', 'review', 'resolved_by')
        else:
            # Users can only see their own reports
            return ReviewReport.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action in ['resolve'] and self.request.user.role in [CustomUser.Role.MODERATOR, CustomUser.Role.ADMIN]:
            return ReportResolutionSerializer
        return ReviewReportSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated, CanModerateReviews])
    def pending(self, request):
        """Get unresolved reports (moderators only)"""
        reports = ReviewReport.objects.filter(resolved=False).select_related('user', 'review')
        page = self.paginate_queryset(reports)
        if page is not None:
            serializer = ReviewReportSerializer(page, many=True, context={'request': request})
            return self.get_paginated_response(serializer.data)
        
        serializer = ReviewReportSerializer(reports, many=True, context={'request': request})
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated, CanModerateReviews])
    def resolve(self, request, pk=None):
        """Resolve a report (moderators only)"""
        report = self.get_object()
        resolution_notes = request.data.get('resolution_notes', '')
        
        report.resolved = True
        report.resolved_by = request.user
        report.resolved_at = timezone.now()
        report.resolution_notes = resolution_notes
        report.save()
        
        serializer = ReviewReportSerializer(report, context={'request': request})
        return Response(serializer.data)