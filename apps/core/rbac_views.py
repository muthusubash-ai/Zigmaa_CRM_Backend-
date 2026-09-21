from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Role, RolePermission
from .permissions import IsSuperAdmin
from .rbac import ACTIONS, MODULES, ROLE_SUPER_ADMIN, SYSTEM_ROLES, permission_payload_for
from .rbac_serializers import PermissionMatrixSerializer
from .serializers import UserSerializer


def role_payload(role):
    stored = {
        permission.module: {
            "actions": permission.allowed_actions,
            "scope": permission.scope,
        }
        for permission in role.permissions.all()
    }
    return {
        "id": role.id,
        "name": role.name,
        "description": role.description or "",
        "is_active": role.is_active,
        "user_count": role.users.count(),
        "is_editable": role.name != ROLE_SUPER_ADMIN,
        "permissions": {
            module: stored.get(module, {"actions": [], "scope": "none"})
            for module in MODULES
        },
    }


class CurrentPermissionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(
            {
                "user": UserSerializer(request.user).data,
                "role": request.user.role.name,
                "permissions": permission_payload_for(request.user),
            }
        )


class RoleListView(APIView):
    permission_classes = [IsSuperAdmin]

    def get(self, request):
        roles = (
            Role.objects.filter(name__in=SYSTEM_ROLES, is_active=True)
            .prefetch_related("permissions")
            .order_by("id")
        )
        return Response({"roles": [role_payload(role) for role in roles]})


class RolePermissionsView(APIView):
    permission_classes = [IsSuperAdmin]

    def get_role(self, role_id):
        return get_object_or_404(
            Role.objects.prefetch_related("permissions"),
            id=role_id,
            name__in=SYSTEM_ROLES,
            is_active=True,
        )

    def get(self, request, role_id):
        return Response(role_payload(self.get_role(role_id)))

    @transaction.atomic
    def put(self, request, role_id):
        role = self.get_role(role_id)
        if role.name == ROLE_SUPER_ADMIN:
            return Response(
                {"detail": "Super Admin permissions are fixed to full access."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = PermissionMatrixSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        matrix = serializer.validated_data["permissions"]

        for module in MODULES:
            rule = matrix.get(module, {"actions": [], "scope": "none"})
            actions = set(rule["actions"])
            defaults = {f"can_{action}": action in actions for action in ACTIONS}
            defaults["scope"] = rule["scope"]
            RolePermission.objects.update_or_create(
                role=role,
                module=module,
                defaults=defaults,
            )

        role = Role.objects.prefetch_related("permissions").get(id=role.id)
        return Response(role_payload(role))
