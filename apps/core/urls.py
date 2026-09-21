from django.urls import path

from .auth_views import (
    CurrentUserView,
    ForgotPasswordView,
    GoogleLoginView,
    LoginView,
    LogoutView,
    ResetPasswordView,
    RefreshTokenView,
)
from .dashboard_views import SuperAdminDashboardView
from .rbac_views import CurrentPermissionsView, RoleListView, RolePermissionsView
from .views import health_check

urlpatterns = [
    path("health/", health_check, name="health-check"),
    path("login/", LoginView.as_view(), name="login"),
    path("auth/login/", LoginView.as_view(), name="auth-login"),
    path("auth/google/", GoogleLoginView.as_view(), name="auth-google"),
    path("auth/password/forgot/", ForgotPasswordView.as_view(), name="auth-password-forgot"),
    path("auth/password/reset/", ResetPasswordView.as_view(), name="auth-password-reset"),
    path("auth/refresh/", RefreshTokenView.as_view(), name="auth-refresh"),
    path("auth/logout/", LogoutView.as_view(), name="auth-logout"),
    path("auth/me/", CurrentUserView.as_view(), name="auth-me"),
    path("auth/permissions/", CurrentPermissionsView.as_view(), name="auth-permissions"),
    path("roles/", RoleListView.as_view(), name="role-list"),
    path("roles/<int:role_id>/permissions/", RolePermissionsView.as_view(), name="role-permissions"),
    path("dashboard/super-admin/", SuperAdminDashboardView.as_view(), name="super-admin-dashboard"),
]
