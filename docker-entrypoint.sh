#!/bin/sh

# Collect static files
echo "Collect static files"
python3.6 manage.py collectstatic --noinput

# Apply database migrations
echo "Apply database migrations"
python3.6 manage.py migrate

# Start server
echo "Starting server"
/usr/local/bin/gunicorn app.wsgi:application -w 2 -b :8000 --reload
