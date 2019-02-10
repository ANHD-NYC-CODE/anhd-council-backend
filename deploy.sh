cd /var/www/anhd-council-backend
git pull origin master

docker-compose build app
docker-compose build celery_default
docker-compose build celery_update
docker-compose build celerybeat

docker-compose restart app
docker-compose restart celery_default
docker-compose restart celery_update
docker-compose restart celerybeat
docker container restart nginx_server
