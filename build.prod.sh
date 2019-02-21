# may need to run as sudo
# sudo sh build.prod.sh
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --force-recreate --build --remove-orphans
docker exec -it app python manage.py migrate
docker image prune -f
echo "Production build complete!"
