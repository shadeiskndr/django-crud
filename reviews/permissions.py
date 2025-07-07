from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models import CustomUser


class IsAuthorOrReadOnly(BasePermission):
    """Review authors can edit their own reviews, others can only read"""
    
    def has_permission(self, request, view):
        # Allow all GET requests (public read access)
        if request.method in SAFE_METHODS:
            return True
        
        # For write operations, user must be authenticated
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        # Read permissions for anyone
        if request.method in SAFE_METHODS:
            return True
        
        # Write permissions only to the review author
        return obj.user == request.user


class CanModerateReviews(BasePermission):
    """Only moderators and admins can moderate reviews"""
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [CustomUser.Role.MODERATOR, CustomUser.Role.ADMIN]
        )


class CanPublishReviews(BasePermission):
    """Users can publish their own reviews, critics have enhanced features"""
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [
                CustomUser.Role.USER, 
                CustomUser.Role.CRITIC, 
                CustomUser.Role.MODERATOR, 
                CustomUser.Role.ADMIN
            ]
        )
    
    def has_object_permission(self, request, view, obj):
        # Authors can always edit their reviews
        if obj.user == request.user:
            return True
        
        # Moderators and admins can moderate any review
        if request.user.role in [CustomUser.Role.MODERATOR, CustomUser.Role.ADMIN]:
            return True
        
        return False


class CanFeatureReviews(BasePermission):
    """Only moderators and admins can feature reviews"""
    
    def has_permission(self, request, view):
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [CustomUser.Role.MODERATOR, CustomUser.Role.ADMIN]
        )


class IsOwnerOrModerator(BasePermission):
    """Owner can manage their own content, moderators can manage any content"""
    
    def has_object_permission(self, request, view, obj):
        # Owner can manage their own content
        if obj.user == request.user:
            return True
        
        # Moderators and admins can manage any content
        return bool(
            request.user and 
            request.user.is_authenticated and 
            request.user.role in [CustomUser.Role.MODERATOR, CustomUser.Role.ADMIN]
        )