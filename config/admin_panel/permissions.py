from rest_framework import permissions

class IsAdminUserRole(permissions.BasePermission):
    """
    Allows access only to superusers, staff, or users with role='admin'.
    """
    def has_permission(self, request, view):
        return bool(
            request.user and request.user.is_authenticated and (
                request.user.is_staff or
                request.user.is_superuser or
                getattr(request.user, 'role', '') == 'admin'
            )
        )