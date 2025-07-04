from rest_framework.permissions import BasePermission
from .models import CustomUser

class IsAdmin(BasePermission):
    """Allows access only to admin users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == CustomUser.Role.ADMIN)

class IsModerator(BasePermission):
    """Allows access only to moderator users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == CustomUser.Role.MODERATOR)

class IsCritic(BasePermission):
    """Allows access only to critic users."""
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == CustomUser.Role.CRITIC)
