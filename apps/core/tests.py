from datetime import timedelta
from decimal import Decimal
from urllib.parse import parse_qs, urlparse

from django.test import TestCase, override_settings
from django.urls import reverse
from django.utils import timezone
from rest_framework.test import APITestCase

from .models import Account, Department, Employee, LoginActivity, Role, RolePermission, Task, User


class HealthCheckTests(TestCase):
    def test_health_check(self):
        response = self.client.get(reverse("health-check"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")


class AuthenticationTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        role, _ = Role.objects.get_or_create(name="Employee")
        cls.user = User.objects.create_user(
            email="employee@zigmaa.test",
            password="StrongPass123!",
            full_name="Test Employee",
            phone="9999999999",
            role=role,
        )

    def test_email_login_returns_access_token_and_refresh_cookie(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.user.email, "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["email"], self.user.email)
        self.assertIn("zigmaa_refresh", response.cookies)
        self.assertTrue(response.cookies["zigmaa_refresh"]["httponly"])
        activity = LoginActivity.objects.get(email=self.user.email, status="success")
        self.assertEqual(activity.user, self.user)
        self.assertEqual(activity.login_type, "password")
        self.user.refresh_from_db()
        self.assertIsNotNone(self.user.last_login)

    def test_invalid_password_is_rejected(self):
        response = self.client.post(
            reverse("login"),
            {"email": self.user.email, "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        activity = LoginActivity.objects.get(email=self.user.email, status="failed")
        self.assertIsNone(activity.user)
        self.assertNotIn("wrong-password", activity.failure_reason)

    def test_legacy_auth_login_endpoint_remains_available(self):
        response = self.client.post(
            reverse("auth-login"),
            {"email": self.user.email, "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)

    def test_access_token_can_load_current_user(self):
        login_response = self.client.post(
            reverse("auth-login"),
            {"email": self.user.email, "password": "StrongPass123!"},
            format="json",
        )
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {login_response.data['access']}")

        response = self.client.get(reverse("auth-me"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["role"], "Employee")

    def test_refresh_cookie_returns_new_access_token(self):
        self.client.post(
            reverse("auth-login"),
            {"email": self.user.email, "password": "StrongPass123!"},
            format="json",
        )

        response = self.client.post(reverse("auth-refresh"), format="json")

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    @override_settings(GOOGLE_OAUTH_CLIENT_ID="")
    def test_google_login_requires_configuration(self):
        response = self.client.post(
            reverse("auth-google"),
            {"credential": "not-a-real-token"},
            format="json",
        )

        self.assertEqual(response.status_code, 503)

    def test_password_reset_link_changes_password_and_is_single_use(self):
        forgot_response = self.client.post(
            reverse("auth-password-forgot"),
            {"email": self.user.email},
            format="json",
        )
        self.assertEqual(forgot_response.status_code, 200)
        self.assertIn("reset_link", forgot_response.data)

        query = parse_qs(urlparse(forgot_response.data["reset_link"]).query)
        reset_payload = {
            "uid": query["uid"][0],
            "token": query["token"][0],
            "new_password": "NewStrongPass456!",
            "confirm_password": "NewStrongPass456!",
        }
        reset_response = self.client.post(
            reverse("auth-password-reset"),
            reset_payload,
            format="json",
        )
        self.assertEqual(reset_response.status_code, 200)

        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password("NewStrongPass456!"))

        reused_response = self.client.post(
            reverse("auth-password-reset"),
            reset_payload,
            format="json",
        )
        self.assertEqual(reused_response.status_code, 400)

    def test_unknown_email_does_not_reveal_account_status(self):
        response = self.client.post(
            reverse("auth-password-forgot"),
            {"email": "missing@zigmaa.test"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("reset_link", response.data)


class SuperAdminDashboardTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        admin_role, _ = Role.objects.get_or_create(name="Super Admin")
        employee_role, _ = Role.objects.get_or_create(name="Employee")
        cls.admin_user = User.objects.create_user(
            email="admin@zigmaa.test", password="StrongPass123!",
            full_name="Test Admin", phone="9999999998", role=admin_role,
            is_staff=True, is_superuser=True,
        )
        cls.employee_user = User.objects.create_user(
            email="dashboard.employee@zigmaa.test", password="StrongPass123!",
            full_name="Dashboard Employee", phone="9999999997", role=employee_role,
        )
        department = Department.objects.create(name="Engineering")
        cls.employee = Employee.objects.create(
            user=cls.employee_user, department=department, employee_code="ZG-001",
            designation="Developer", date_of_joining=timezone.localdate(),
            salary=Decimal("50000.00"),
        )
        today = timezone.localdate()
        Task.objects.create(
            assigned_to=cls.employee, assigned_by=cls.admin_user,
            title="Today dashboard task", priority="high", status="in_progress",
            start_date=today, due_date=today,
        )
        Task.objects.create(
            assigned_to=cls.employee, assigned_by=cls.admin_user,
            title="Completed dashboard task", priority="medium", status="Completed",
            start_date=today - timedelta(days=2), due_date=today - timedelta(days=1),
            completed_at=today,
        )
        Account.objects.create(
            account_type="Revenue", title="Today payment", amount=Decimal("12500.00"),
            date=today, status="Completed", created_by=cls.admin_user,
        )

    def test_super_admin_can_load_dashboard_summary(self):
        self.client.force_authenticate(self.admin_user)
        response = self.client.get(reverse("super-admin-dashboard"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["metrics"]["today_tasks"], 1)
        self.assertEqual(response.data["metrics"]["completed_tasks"], 1)
        self.assertEqual(response.data["metrics"]["today_revenue"], "12500.00")
        self.assertEqual(response.data["metrics"]["total_employees"], 1)
        self.assertEqual(len(response.data["recent_tasks"]), 2)

    def test_employee_cannot_load_super_admin_dashboard(self):
        self.client.force_authenticate(self.employee_user)
        response = self.client.get(reverse("super-admin-dashboard"))

        self.assertEqual(response.status_code, 403)


class RolePermissionAPITests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.admin_role, _ = Role.objects.get_or_create(
            name="Super Admin", defaults={"description": "Full system access"}
        )
        cls.hr_role, _ = Role.objects.get_or_create(
            name="HR", defaults={"description": "HR operations"}
        )
        cls.employee_role, _ = Role.objects.get_or_create(
            name="Employee", defaults={"description": "Employee access"}
        )
        cls.admin = User.objects.create_user(
            email="rbac.admin@zigmaa.test", password="StrongPass123!",
            full_name="RBAC Admin", phone="9999999996", role=cls.admin_role,
            is_staff=True, is_superuser=True,
        )
        cls.employee_user = User.objects.create_user(
            email="rbac.employee@zigmaa.test", password="StrongPass123!",
            full_name="RBAC Employee", phone="9999999995", role=cls.employee_role,
        )
        RolePermission.objects.update_or_create(
            role=cls.employee_role,
            module="employees",
            defaults={"can_view": True, "scope": "own"},
        )

    def test_current_permissions_include_actions_and_data_scope(self):
        self.client.force_authenticate(self.employee_user)

        response = self.client.get(reverse("auth-permissions"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["role"], "Employee")
        self.assertEqual(response.data["permissions"]["employees"]["actions"], ["view"])
        self.assertEqual(response.data["permissions"]["employees"]["scope"], "own")

    def test_employee_cannot_manage_roles(self):
        self.client.force_authenticate(self.employee_user)

        response = self.client.get(reverse("role-list"))

        self.assertEqual(response.status_code, 403)

    def test_super_admin_can_list_only_three_system_roles(self):
        self.client.force_authenticate(self.admin)

        response = self.client.get(reverse("role-list"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            {role["name"] for role in response.data["roles"]},
            {"Super Admin", "HR", "Employee"},
        )

    def test_super_admin_can_update_hr_permission_matrix(self):
        self.client.force_authenticate(self.admin)
        response = self.client.put(
            reverse("role-permissions", kwargs={"role_id": self.hr_role.id}),
            {
                "permissions": {
                    "employees": {"actions": ["view", "edit"], "scope": "all"},
                    "leave": {"actions": ["view", "approve"], "scope": "all"},
                }
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        employee_access = RolePermission.objects.get(
            role=self.hr_role, module="employees"
        )
        self.assertTrue(employee_access.can_view)
        self.assertTrue(employee_access.can_edit)
        self.assertFalse(employee_access.can_delete)
        self.assertEqual(employee_access.scope, "all")

    def test_super_admin_permissions_cannot_be_reduced(self):
        self.client.force_authenticate(self.admin)

        response = self.client.put(
            reverse("role-permissions", kwargs={"role_id": self.admin_role.id}),
            {"permissions": {}},
            format="json",
        )

        self.assertEqual(response.status_code, 400)
