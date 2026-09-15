# PostgreSQL setup

Django migrations are the source of truth for the database schema. Do not keep
a separate hand-written schema that can drift away from the application models.

Create the initial local database and user in PostgreSQL:

```sql
CREATE DATABASE zigmaa_crm;
CREATE USER zigmaa_user WITH PASSWORD 'replace-with-a-secure-password';
ALTER DATABASE zigmaa_crm OWNER TO zigmaa_user;
```

Copy `backend/.env.example` to `backend/.env`, enter the matching credentials,
and then run `python manage.py migrate` from the backend folder.

