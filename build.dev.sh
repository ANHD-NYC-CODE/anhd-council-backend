# sh build.dev.sh

# these commands build/rebuild the dev docker environment LOCALLY
# be careful when running and make sure your data/ and logs/ folders are empty! and make sure the sample pg_vol is not present.
# otherwise build size will be too large
docker build -f Dockerfile --tag app_image .
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d --force-recreate --build --remove-orphans
docker exec -it app python manage.py migrate
docker image prune -f

echo "Dev build complete! View logs with 'docker-compose logs -f app' or attach to the app for debugging with 'docker attach app'"
