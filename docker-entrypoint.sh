#!/bin/sh


# Apply database migrations
echo "Apply database migrations"
python3.6 manage.py migrate

# Collect static files
echo "Collect static files"
python3.6 manage.py collectstatic --noinput

# Start server
echo "Starting server"
/usr/local/bin/gunicorn app.wsgi:application --workers=12 --threads=2 --max-requests=1000 -t 420 -b :8000 --reload --graceful-timeout 30
