from urllib.parse import quote

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.db import transaction
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from google.auth.exceptions import GoogleAuthError
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework.views import APIView
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.token_blacklist.models import BlacklistedToken, OutstandingToken
from rest_framework_simplejwt.tokens import RefreshToken

from .models import LoginActivity, Role, User
from .serializers import (
    ForgotPasswordSerializer,
    GoogleLoginSerializer,
    LoginSerializer,
    ResetPasswordSerializer,
    UserSerializer,
)


def set_refresh_cookie(response, refresh_token):
    response.set_cookie(
        key=settings.JWT_AUTH_COOKIE_NAME,
        value=str(refresh_token),
        max_age=int(refresh_token.lifetime.total_seconds()),
        httponly=True,
        secure=settings.JWT_AUTH_COOKIE_SECURE,
        samesite=settings.JWT_AUTH_COOKIE_SAMESITE,
        path="/api/v1/auth/",
    )


def authentication_response(user):
    refresh = RefreshToken.for_user(user)
    response = Response(
        {
            "access": str(refresh.access_token),
            "user": UserSerializer(user).data,
        }
    )
    set_refresh_cookie(response, refresh)
    return response


def create_login_activity(request, email, status_value, user=None, failure_reason=""):
    LoginActivity.objects.create(
        user=user,
        email=str(email or "").strip().lower()[:254],
        login_type="password",
        status=status_value,
        ip_address=request.META.get("REMOTE_ADDR") or None,
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:1000],
        failure_reason=failure_reason[:255],
    )


class LoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    @transaction.atomic
    def post(self, request):
        serializer = LoginSerializer(data=request.data, context={"request": request})
        if not serializer.is_valid():
            email = request.data.get("email", "") if hasattr(request.data, "get") else ""
            create_login_activity(
                request,
                email,
                "failed",
                failure_reason="Invalid credentials or login payload.",
            )
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        user = serializer.validated_data["user"]
        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        create_login_activity(request, user.email, "success", user=user)
        return authentication_response(user)


class GoogleLoginView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "google_login"

    @transaction.atomic
    def post(self, request):
        serializer = GoogleLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        client_id = settings.GOOGLE_OAUTH_CLIENT_ID
        if not client_id:
            return Response(
                {"detail": "Google authentication is not configured."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            payload = id_token.verify_oauth2_token(
                serializer.validated_data["credential"],
                google_requests.Request(),
                client_id,
            )
        except (ValueError, GoogleAuthError):
            return Response(
                {"detail": "Invalid Google credential."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = str(payload.get("email", "")).strip().lower()
        google_sub = str(payload.get("sub", "")).strip()
        if not email or not google_sub or payload.get("email_verified") is not True:
            return Response(
                {"detail": "Google account email could not be verified."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(google_sub=google_sub).first()
        if user is None:
            existing_user = User.objects.filter(email__iexact=email).first()
            if existing_user is not None:
                return Response(
                    {
                        "detail": (
                            "An account with this email already exists. "
                            "Sign in with your password before linking Google."
                        )
                    },
                    status=status.HTTP_409_CONFLICT,
                )

            employee_role, _ = Role.objects.get_or_create(
                name="Employee",
                defaults={"description": "Employee access"},
            )
            user = User.objects.create_user(
                email=email,
                full_name=str(payload.get("name") or email.split("@", 1)[0]),
                phone="",
                profile_image=str(payload.get("picture") or ""),
                google_sub=google_sub,
                role=employee_role,
            )

        if not user.is_active:
            return Response(
                {"detail": "This account is inactive."},
                status=status.HTTP_403_FORBIDDEN,
            )

        user.last_login = timezone.now()
        user.save(update_fields=["last_login"])
        return authentication_response(user)


class ForgotPasswordView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset"

    def post(self, request):
        serializer = ForgotPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = User.objects.filter(
            email__iexact=serializer.validated_data["email"],
            is_active=True,
        ).first()
        response_data = {
            "detail": "If the account exists, a password reset link has been generated."
        }

        if user is not None:
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            reset_link = (
                f"{settings.FRONTEND_URL}/?view=reset-password"
                f"&uid={quote(uid)}&token={quote(token)}"
            )
            if settings.PASSWORD_RESET_EXPOSE_LINK:
                response_data["reset_link"] = reset_link

        return Response(response_data)


class ResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "password_reset_confirm"

    @transaction.atomic
    def post(self, request):
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        outstanding_tokens = OutstandingToken.objects.filter(user=user)
        for outstanding_token in outstanding_tokens:
            BlacklistedToken.objects.get_or_create(token=outstanding_token)

        return Response({"detail": "Your password has been reset successfully."})


class RefreshTokenView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        raw_refresh_token = request.COOKIES.get(settings.JWT_AUTH_COOKIE_NAME)
        if not raw_refresh_token:
            return Response(
                {"detail": "Refresh token is missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(raw_refresh_token)
        except TokenError:
            return Response(
                {"detail": "Refresh token is invalid or expired."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if not User.objects.filter(id=refresh.get("user_id"), is_active=True).exists():
            return Response(
                {"detail": "User account is unavailable."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        return Response({"access": str(refresh.access_token)})


class LogoutView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]


    def post(self, request):
        raw_refresh_token = request.COOKIES.get(settings.JWT_AUTH_COOKIE_NAME)
        if raw_refresh_token:
            try:
                RefreshToken(raw_refresh_token).blacklist()
            except TokenError:
                pass

        response = Response(status=status.HTTP_204_NO_CONTENT)
        response.delete_cookie(
            settings.JWT_AUTH_COOKIE_NAME,
            path="/api/v1/auth/",
            samesite=settings.JWT_AUTH_COOKIE_SAMESITE,
        )
        return response


class CurrentUserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)
