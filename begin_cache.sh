ssh -t anhd@45.55.44.160 "cd /var/www/anhd-council-backend && sudo docker exec -it redis redis-cli FLUSHALL && app python pre_cache.py"
