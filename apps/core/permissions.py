from rest_framework.permissions import BasePermission


class IsSuperAdmin(BasePermission):
    message = "Super Admin access is required."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False
        if user.is_superuser:
            return True
        return bool(user.role_id and user.role.name.casefold() == "super admin")
