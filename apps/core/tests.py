from urllib.parse import parse_qs, urlparse

from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APITestCase

from .models import Role, User


class HealthCheckTests(TestCase):
    def test_health_check(self):
        response = self.client.get(reverse("health-check"))

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "ok")


class AuthenticationTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        role = Role.objects.create(name="Employee")
        cls.user = User.objects.create_user(
            email="employee@zigmaa.test",
            password="StrongPass123!",
            full_name="Test Employee",
            phone="9999999999",
            role=role,
        )

    def test_email_login_returns_access_token_and_refresh_cookie(self):
        response = self.client.post(
            reverse("auth-login"),
            {"email": self.user.email, "password": "StrongPass123!"},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)
        self.assertEqual(response.data["user"]["email"], self.user.email)
        self.assertIn("zigmaa_refresh", response.cookies)
        self.assertTrue(response.cookies["zigmaa_refresh"]["httponly"])

    def test_invalid_password_is_rejected(self):
        response = self.client.post(
            reverse("auth-login"),
            {"email": self.user.email, "password": "wrong-password"},
            format="json",
        )

        self.assertEqual(response.status_code, 400)

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
