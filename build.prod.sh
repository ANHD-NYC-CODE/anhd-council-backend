docker build -f Dockerfile --tag app_image .
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build --remove-orphans
docker exec app python manage.py migrate --noinput
docker exec app python manage.py collectstatic --noinput
docker image prune -f
echo "Production build complete!"
