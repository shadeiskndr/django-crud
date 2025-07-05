from rest_framework.permissions import BasePermission, SAFE_METHODS
from users.models import CustomUser

class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission to only allow admins to edit objects.
    Read-only access is allowed for any request (authenticated or not).
    """

    def has_permission(self, request, view):
        # Allow all GET, HEAD, or OPTIONS requests.
        if request.method in SAFE_METHODS:
            return True

        # Write permissions are only allowed to authenticated admin users.
        return bool(
            request.user and
            request.user.is_authenticated and
            request.user.role == CustomUser.Role.ADMIN
        )
