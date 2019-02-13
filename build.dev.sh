# sh build.dev.sh
docker-compose -f docker-compose.yml -f docker-compose.dev.yml up --force-recreate --build --remove-orphans
echo "Dev build complete!"
