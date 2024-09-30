from rest_framework import permissions

class IsSuperUser(permissions.BasePermission):
    """
    Custom permission to only allow superusers to update or delete an object.
    """
    def has_permission(self, request, view):
        # Allow read (GET, HEAD, OPTIONS) for any request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Only allow superusers to perform write operations (POST, PUT, DELETE)
        return request.user.is_superuser
