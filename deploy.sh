# docker-compose exec app pipenv install
# docker-compose exec celery_default pipenv install
# docker-compose exec celery_default pipenv install
# docker-compose exec celerybeat pipenv install
#
# docker-compose exec app python manage.py migrate
# docker-compose restart nginx

# gracefully shutdown and restart workers after tasks completed (propogates to all workers)

# docker-compose exec celery_default celery control shutdown
#

docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --force-recreate --build --remove-orphans
docker exec -it app python manage.py migrate
echo "Deploy complete!"

# docker-compose exec celery_default pkill 'celery'
# docker-compose exec celery_update pkill 'celery'
