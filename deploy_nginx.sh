#!/usr/bin/env sh
# nginx.conf is COPY'd into the image at build time (nginx/Dockerfile), not bind-mounted.
set -e
cd "$(dirname "$0")"
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d --build nginx
docker exec nginx_server nginx -t
docker exec nginx_server nginx -s reload
