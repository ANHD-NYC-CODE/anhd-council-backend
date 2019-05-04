docker build -f Dockerfile --tag app_image .
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build --force-recreate --remove-orphans
docker exec -it app python manage.py migrate
# sudo docker exec -it redis redis-cli FLUSHALL
docker image prune -f
echo "Production build complete!"

# echo "starting pre-cache"
# docker exec -it app python pre_cache.py
