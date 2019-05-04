docker build -f Dockerfile --tag app_image .
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build --remove-orphans
docker exec -it app python manage.py migrate
docker image prune -f
echo "Production build complete!"
