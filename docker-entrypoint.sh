#!/bin/sh


# Apply database migrations
echo "Apply database migrations"
python manage.py migrate

# Collect static files
echo "Collect static files"
python manage.py collectstatic --noinput

# Start server
echo "Starting server"
/usr/local/bin/gunicorn app.wsgi:application -k gevent --log-level=DEBUG --workers=8 --threads=2 -b :8000 --max-requests 20 --max-requests-jitter 2 --timeout 300 --reload --graceful-timeout 30
