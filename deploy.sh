cd /var/www/anhd-council-backend
git pull origin master

# Need to restart celery workers
docker-compose restart celery_default
docker-compose restart celery_update
docker-compose restart celerybeat
