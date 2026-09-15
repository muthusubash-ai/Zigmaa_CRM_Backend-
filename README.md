# Zigmaa CRM Backend

Django REST Framework API with PostgreSQL.

## Setup

Requires Python 3.11 or newer and PostgreSQL.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
Copy-Item .env.example .env
```

Load the values in `.env` into your environment, create the database using the
instructions in `database/README.md`, and run:

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

The health endpoint is `http://localhost:8000/api/v1/health/`.

## Authentication endpoints

- `POST /api/v1/auth/login/` - email/password login
- `POST /api/v1/auth/google/` - Google ID-token login
- `POST /api/v1/auth/password/forgot/` - generate a single-use reset link
- `POST /api/v1/auth/password/reset/` - validate the token and set a new password
- `POST /api/v1/auth/refresh/` - refresh the access token from the HttpOnly cookie
- `POST /api/v1/auth/logout/` - revoke the refresh token and clear its cookie
- `GET /api/v1/auth/me/` - return the authenticated user

Set `GOOGLE_OAUTH_CLIENT_ID` in `.env` before enabling Google login. In
production, set `DJANGO_DEBUG=False`, `JWT_AUTH_COOKIE_SECURE=True`, and
`PASSWORD_RESET_EXPOSE_LINK=False`. Production delivery should send the reset
link through the configured email provider instead of returning it in the API.

- `config/` contains project settings and root URLs.
- `apps/` contains modular Django applications.
- `database/` contains PostgreSQL setup documentation; migrations will live in each app.
