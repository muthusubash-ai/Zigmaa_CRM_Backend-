from rest_framework import serializers

from .rbac import ACTIONS, MODULES, SCOPES


class PermissionMatrixSerializer(serializers.Serializer):
    permissions = serializers.DictField()

    def validate_permissions(self, matrix):
        normalized = {}
        invalid_modules = set(matrix) - set(MODULES)
        if invalid_modules:
            raise serializers.ValidationError(
                f"Unknown modules: {', '.join(sorted(invalid_modules))}."
            )

        for module, rule in matrix.items():
            if not isinstance(rule, dict):
                raise serializers.ValidationError(f"{module} must be an object.")
            actions = rule.get("actions", [])
            scope = rule.get("scope", "none")
            if not isinstance(actions, list):
                raise serializers.ValidationError(f"{module}.actions must be a list.")
            invalid_actions = set(actions) - set(ACTIONS)
            if invalid_actions:
                raise serializers.ValidationError(
                    f"Unknown actions for {module}: {', '.join(sorted(invalid_actions))}."
                )
            if scope not in SCOPES:
                raise serializers.ValidationError(f"Unknown scope for {module}: {scope}.")
            if actions and scope == "none":
                raise serializers.ValidationError(
                    f"{module} needs a data scope when actions are enabled."
                )
            normalized[module] = {
                "actions": list(dict.fromkeys(actions)),
                "scope": scope,
            }
        return normalized
