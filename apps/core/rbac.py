ROLE_SUPER_ADMIN = "Super Admin"
ROLE_HR = "HR"
ROLE_EMPLOYEE = "Employee"

SYSTEM_ROLES = (ROLE_SUPER_ADMIN, ROLE_HR, ROLE_EMPLOYEE)

MODULES = (
    "dashboard", "employees", "departments", "clients", "projects",
    "tasks", "attendance", "leave", "finance", "documents", "users",
    "roles", "audit_log", "notifications", "settings",
)
ACTIONS = ("view", "create", "edit", "delete", "approve", "export", "manage")
SCOPES = ("none", "own", "assigned", "department", "all")
ALL_ACTIONS = list(ACTIONS)

DEFAULT_ROLE_PERMISSIONS = {
    ROLE_SUPER_ADMIN: {
        module: {"actions": ALL_ACTIONS, "scope": "all"} for module in MODULES
    },
    ROLE_HR: {
        "dashboard": {"actions": ["view"], "scope": "all"},
        "employees": {"actions": ["view", "create", "edit", "export", "manage"], "scope": "all"},
        "departments": {"actions": ["view", "edit"], "scope": "all"},
        "clients": {"actions": ["view"], "scope": "all"},
        "projects": {"actions": ["view"], "scope": "all"},
        "tasks": {"actions": ["view", "create", "edit", "manage"], "scope": "all"},
        "attendance": {"actions": ["view", "create", "edit", "export", "manage"], "scope": "all"},
        "leave": {"actions": ["view", "edit", "approve", "export", "manage"], "scope": "all"},
        "documents": {"actions": ["view", "create", "edit", "manage"], "scope": "all"},
        "users": {"actions": ["view", "create", "edit", "manage"], "scope": "all"},
        "audit_log": {"actions": ["view"], "scope": "all"},
        "notifications": {"actions": ["view", "edit"], "scope": "own"},
        "settings": {"actions": ["view", "edit"], "scope": "own"},
    },
    ROLE_EMPLOYEE: {
        "dashboard": {"actions": ["view"], "scope": "own"},
        "employees": {"actions": ["view"], "scope": "own"},
        "departments": {"actions": ["view"], "scope": "department"},
        "projects": {"actions": ["view"], "scope": "assigned"},
        "tasks": {"actions": ["view", "edit"], "scope": "assigned"},
        "attendance": {"actions": ["view", "create"], "scope": "own"},
        "leave": {"actions": ["view", "create"], "scope": "own"},
        "documents": {"actions": ["view"], "scope": "assigned"},
        "notifications": {"actions": ["view", "edit"], "scope": "own"},
        "settings": {"actions": ["view", "edit"], "scope": "own"},
    },
}


def permission_payload_for(user):
    if not user or not user.is_authenticated or not user.role_id:
        return {}
    if user.is_superuser or user.role.name == ROLE_SUPER_ADMIN:
        return {module: {"actions": list(ACTIONS), "scope": "all"} for module in MODULES}
    return {
        permission.module: {
            "actions": permission.allowed_actions,
            "scope": permission.scope,
        }
        for permission in user.role.permissions.all()
        if permission.allowed_actions and permission.scope != "none"
    }
