from django.db import migrations


MODULES = (
    "dashboard", "employees", "departments", "clients", "projects",
    "tasks", "attendance", "leave", "finance", "documents", "users",
    "roles", "audit_log", "notifications", "settings",
)
ACTIONS = ("view", "create", "edit", "delete", "approve", "export", "manage")

HR_PERMISSIONS = {
    "dashboard": (["view"], "all"),
    "employees": (["view", "create", "edit", "export", "manage"], "all"),
    "departments": (["view", "edit"], "all"),
    "clients": (["view"], "all"),
    "projects": (["view"], "all"),
    "tasks": (["view", "create", "edit", "manage"], "all"),
    "attendance": (["view", "create", "edit", "export", "manage"], "all"),
    "leave": (["view", "edit", "approve", "export", "manage"], "all"),
    "documents": (["view", "create", "edit", "manage"], "all"),
    "users": (["view", "create", "edit", "manage"], "all"),
    "audit_log": (["view"], "all"),
    "notifications": (["view", "edit"], "own"),
    "settings": (["view", "edit"], "own"),
}

EMPLOYEE_PERMISSIONS = {
    "dashboard": (["view"], "own"),
    "employees": (["view"], "own"),
    "departments": (["view"], "department"),
    "projects": (["view"], "assigned"),
    "tasks": (["view", "edit"], "assigned"),
    "attendance": (["view", "create"], "own"),
    "leave": (["view", "create"], "own"),
    "documents": (["view"], "assigned"),
    "notifications": (["view", "edit"], "own"),
    "settings": (["view", "edit"], "own"),
}


def seed_roles_and_permissions(apps, schema_editor):
    Role = apps.get_model("core", "Role")
    User = apps.get_model("core", "User")
    RolePermission = apps.get_model("core", "RolePermission")

    super_admin, _ = Role.objects.get_or_create(
        name="Super Admin", defaults={"description": "Full system access"}
    )
    hr, _ = Role.objects.get_or_create(
        name="HR", defaults={"description": "Employee and HR operations access"}
    )
    employee, _ = Role.objects.get_or_create(
        name="Employee", defaults={"description": "Personal and assigned work access"}
    )
    Role.objects.filter(id__in=[super_admin.id, hr.id, employee.id]).update(is_active=True)

    for old_role in Role.objects.exclude(id__in=[super_admin.id, hr.id, employee.id]):
        target = hr if old_role.name.casefold() in {"hr", "hr manager", "human resources"} else employee
        User.objects.filter(role_id=old_role.id).update(role_id=target.id)
        old_role.is_active = False
        old_role.save(update_fields=["is_active"])

    matrices = {
        super_admin.id: {module: (list(ACTIONS), "all") for module in MODULES},
        hr.id: HR_PERMISSIONS,
        employee.id: EMPLOYEE_PERMISSIONS,
    }
    for role_id, matrix in matrices.items():
        for module in MODULES:
            actions, scope = matrix.get(module, ([], "none"))
            defaults = {f"can_{action}": action in actions for action in ACTIONS}
            defaults["scope"] = scope
            RolePermission.objects.update_or_create(
                role_id=role_id,
                module=module,
                defaults=defaults,
            )


def remove_seeded_permissions(apps, schema_editor):
    RolePermission = apps.get_model("core", "RolePermission")
    RolePermission.objects.all().delete()


class Migration(migrations.Migration):
    dependencies = [("core", "0003_rolepermission")]

    operations = [
        migrations.RunPython(seed_roles_and_permissions, remove_seeded_permissions),
    ]
