from rest_framework.permissions import BasePermission

from .rbac import ROLE_SUPER_ADMIN


class IsSuperAdmin(BasePermission):
    message = "Super Admin access is required."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False
        if user.is_superuser:
            return True
        return bool(user.role_id and user.role.is_active and user.role.name == ROLE_SUPER_ADMIN)


class HasModulePermission(BasePermission):
    message = "You do not have permission to perform this action."
    method_actions = {
        "GET": "view",
        "HEAD": "view",
        "OPTIONS": "view",
        "POST": "create",
        "PUT": "edit",
        "PATCH": "edit",
        "DELETE": "delete",
    }

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated or not user.is_active:
            return False
        if user.is_superuser or (user.role_id and user.role.name == ROLE_SUPER_ADMIN):
            request.permission_scope = "all"
            return True
        if not user.role_id or not user.role.is_active:
            return False

        module = getattr(view, "permission_module", None)
        action = getattr(view, "permission_action", None)
        if action is None:
            action = getattr(view, "permission_action_map", {}).get(
                request.method, self.method_actions.get(request.method)
            )
        if not module or not action:
            return False

        permission = user.role.permissions.filter(module=module).first()
        if permission is None or permission.scope == "none":
            return False
        request.permission_scope = permission.scope
        return bool(getattr(permission, f"can_{action}", False))
