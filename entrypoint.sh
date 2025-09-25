#!/usr/bin/env sh
set -e

# Apply migrations (SQLite)
python manage.py migrate --noinput

# Collect static files into STATIC_ROOT (staticfiles/)
python manage.py collectstatic --noinput

# Start Django development server for homolog environment
exec python manage.py runserver 0.0.0.0:8000
