from rest_framework import permissions


class IsAdminOrAuthorOrReadOnly(permissions.IsAuthenticatedOrReadOnly):
    """Разрешение для авторов, администраторов или только для чтения."""

    def has_object_permission(self, request, view, obj):
        """Проверка прав доступа к объекту."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_superuser
            or obj.author == request.user
        )
