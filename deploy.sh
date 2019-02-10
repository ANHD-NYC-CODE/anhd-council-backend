cd /var/www/anhd-council-backend
git pull origin master

docker-compose exec app pipenv install
docker-compose exec celery_default pipenv install
docker-compose exec celery_default pipenv install
docker-compose exec celerybeat pipenv install

docker-compose restart app
docker-compose restart nginx_server

# gracefully shutdown and restart workers after tasks completed

docker-compose exec docker-compose exec celery_update celery control pool_restart


# docker-compose exec celery_default pkill 'celery'
# docker-compose exec celery_update pkill 'celery'
