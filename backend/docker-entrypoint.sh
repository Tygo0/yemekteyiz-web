#!/bin/sh
set -e

echo "Running database migrations..."
export FLASK_APP=wsgi.py
flask db upgrade

if [ -n "$ADMIN_USERNAME" ] && [ -n "$ADMIN_PASSWORD" ]; then
  echo "Ensuring admin account exists..."
  python3 seed.py
fi

echo "Starting gunicorn..."
exec gunicorn --bind 0.0.0.0:5000 --workers "${GUNICORN_WORKERS:-2}" wsgi:app
