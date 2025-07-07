from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsOwnerOrReadOnly(BasePermission):
    """
    Custom permission to only allow owners of a catalog entry to edit it.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions for any authenticated user
        if request.method in SAFE_METHODS:
            return request.user.is_authenticated
        
        # Write permissions only to the owner
        return obj.user == request.user


class IsOwnerOrPublicReadOnly(BasePermission):
    """
    Permission for movie lists - owners can do anything, 
    others can only read public lists.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated
    
    def has_object_permission(self, request, view, obj):
        # Owner can do anything
        if obj.user == request.user:
            return True
        
        # Others can only read public lists
        if request.method in SAFE_METHODS and obj.is_public:
            return True
        
        return False
