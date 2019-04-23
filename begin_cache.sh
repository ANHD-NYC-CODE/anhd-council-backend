ssh -t anhd@45.55.44.160 "cd /var/www/anhd-council-backend && sudo docker exec -it docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d redis --force-recreate --build --remove-orphans && sudo docker exec -it app python pre_cache.py"
# redis redis-cli FLUSHALL &&
