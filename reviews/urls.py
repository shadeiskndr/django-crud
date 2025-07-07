from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ReviewViewSet,
    ReviewModerationViewSet,
    ReviewVoteViewSet,
    ReviewReportViewSet
)

app_name = "reviews"

router = DefaultRouter()
router.register(r'reviews', ReviewViewSet, basename='review')
router.register(r'moderation', ReviewModerationViewSet, basename='review-moderation')
router.register(r'votes', ReviewVoteViewSet, basename='review-vote')
router.register(r'reports', ReviewReportViewSet, basename='review-report')

urlpatterns = [
    path('', include(router.urls)),
]