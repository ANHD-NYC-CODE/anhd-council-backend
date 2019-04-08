# sh build.dev.sh
# docker build -f Dockerfile --tag app_image .
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --force-recreate --build --remove-orphans
docker exec -it app python manage.py migrate
docker image prune -f

echo "Dev build complete!"
